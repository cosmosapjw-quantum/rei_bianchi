//! Backward-compatible source-off line protocol. Opt-in batch and backend.
//! RHS/STEP/STEP_TIGHT replies retain their original numeric layout.
use rei_iso_couple_reference::{
    HHeModel,
    deuterium_atomic::DAtomicProvider,
    full_network::{self, FullState, NetworkConfig, NetworkError},
    gas_reference_rhs::{GasRates, GasBatchStats, GasRateWorkspace, gas_rates_batch_into},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::MixtureState,
    rate_table::{IgmRateBackend, IgmRateTable},
};
use std::{io::{self, BufRead, Write}, sync::Arc};

const MAX_BATCH: usize = 65_536;
fn base_config() -> Result<NetworkConfig, NetworkError> {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_D_H_DELTA_CHI")
            .map_err(|_| NetworkError::SourceMismatch)?,
        "MD14_Z002_FESC_BB50K_13P6_100_V1",
    );
    c.use_photo = false;
    Ok(c)
}
fn number(words: &mut std::str::SplitWhitespace<'_>) -> Result<f64, NetworkError> {
    let value = words.next().ok_or(NetworkError::InvalidInput)?
        .parse::<f64>().map_err(|_| NetworkError::InvalidInput)?;
    if !value.is_finite() { return Err(NetworkError::InvalidInput); }
    Ok(value)
}
fn parse_mask(words: &mut std::str::SplitWhitespace<'_>) -> Result<u8, NetworkError> {
    let value = number(words)?;
    if !(0.0..=7.0).contains(&value) || value.fract() != 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    Ok(value as u8)
}
fn parse_state(words: &mut std::str::SplitWhitespace<'_>) -> Result<FullState, NetworkError> {
    let mut n = [0.0;13];
    for value in &mut n { *value = number(words)?; }
    let thermal = number(words)?;
    Ok(FullState {
        gas: MixtureState { nuclei: IsotopeNumberState::new(n)
            .map_err(|_|NetworkError::NegativePopulation)?, thermal_j_m3: thermal },
        photon_bins: Vec::new(), escaped_j_m3: 0.0, cmb_reservoir_j_m3: 0.0, elapsed_s: 0.0,
    })
}
fn configured(mut c: NetworkConfig, mask: u8, tcmb: f64, tight: bool) -> NetworkConfig {
    c.cmb_temperature_k = tcmb;
    c.use_collisions = mask & 1 != 0;
    c.use_cx = mask & 2 != 0;
    c.use_cmb = mask & 4 != 0;
    if tight { c.cx_controls.atol_normalized = 1e-15; c.cx_controls.rtol = 1e-11; }
    c
}
enum Reply {
    Single { row: [f64;28], len: usize },
    Batch { rows: Vec<GasRates>, stats: GasBatchStats },
}
fn execute(line: &str, base: NetworkConfig, backend: &IgmRateBackend,
    workspace: &mut GasRateWorkspace<'_>, workers: usize) -> Result<Reply, NetworkError> {
    let mut words = line.split_whitespace();
    let command = words.next().ok_or(NetworkError::InvalidInput)?;
    if command == "RHS_BATCH" {
        let count = words.next().ok_or(NetworkError::InvalidInput)?.parse::<usize>()
            .map_err(|_|NetworkError::InvalidInput)?;
        if count == 0 || count > MAX_BATCH { return Err(NetworkError::InvalidInput); }
        let mask = parse_mask(&mut words)?;
        let c = configured(base, mask, number(&mut words)?, false);
        let mut states = Vec::with_capacity(count);
        for _ in 0..count { states.push(parse_state(&mut words)?); }
        if words.next().is_some() { return Err(NetworkError::InvalidInput); }
        let mut rows = vec![GasRates::default();count];
        let stats = gas_rates_batch_into(&states,&c,mask,backend,&mut rows,workers)?;
        return Ok(Reply::Batch{rows,stats});
    }
    let tight = command == "STEP_TIGHT";
    let step = command == "STEP" || tight;
    if command != "RHS" && !step { return Err(NetworkError::InvalidInput); }
    let mask = parse_mask(&mut words)?;
    let tcmb = number(&mut words)?;
    let dt = if step {number(&mut words)?} else {0.0};
    let s = parse_state(&mut words)?;
    if words.next().is_some() { return Err(NetworkError::InvalidInput); }
    let c = configured(base,mask,tcmb,tight);
    let mut row = [0.0;28];
    if step {
        // The table flag affects RHS only; the original STEP owner stays Direct.
        let out = full_network::step(&s,&c,dt)?;
        for sp in S::ALL { row[sp as usize] = out.state.gas.nuclei.density_m3(sp); }
        row[13..16].copy_from_slice(&[out.state.gas.thermal_j_m3,
            out.state.escaped_j_m3,out.state.cmb_reservoir_j_m3]);
        row[16..20].copy_from_slice(&out.budget.ci_events_m3);
        row[20..24].copy_from_slice(&out.budget.rr_events_m3);
        row[24..27].copy_from_slice(&[out.budget.dr_hei_m3,out.budget.cx_signed_m3,
            out.budget.freefree_integrated_j_m3]);
        Ok(Reply::Single{row,len:27})
    } else {
        let rates = workspace.evaluate(&s,&c,mask)?;
        row[..27].copy_from_slice(&rates.vector()); row[27] = rates.chemical;
        Ok(Reply::Single{row,len:28})
    }
}
fn write_row(out: &mut impl Write, row: &[f64]) -> io::Result<()> {
    write!(out,"OK")?;
    for x in row { write!(out," {x:.17e}")?; }
    writeln!(out)
}
fn options() -> Result<(IgmRateBackend,usize),String> {
    let mut args=std::env::args().skip(1);
    let mut selection="direct".to_string(); let mut workers=1;
    while let Some(arg)=args.next() { match arg.as_str() {
        "--rates" => selection=args.next().ok_or("--rates requires direct or table")?,
        "--workers" => workers=args.next().ok_or("--workers requires 1..4")?
            .parse::<usize>().map_err(|_|"invalid worker count")?,
        "--help" => {
            println!("gas_rhs_server [--rates direct|table] [--workers 1..4]\nRHS mask Tcmb n[13] U\nRHS_BATCH count mask Tcmb (n[13] U)*count\nMETA | QUIT\nSTEP/STEP_TIGHT retain Direct backend and original protocol.");
            std::process::exit(0);
        },
        _=>return Err(format!("unknown argument: {arg}")),
    }}
    if !(1..=4).contains(&workers) { return Err("workers must be 1..4".into()); }
    let backend=match selection.as_str() {
        "direct"=>IgmRateBackend::Direct,
        "table"=>IgmRateBackend::Table(Arc::new(IgmRateTable::build_default()
            .map_err(|e|format!("table build: {e:?}"))?)),
        _=>return Err("rates must be direct or table".into()),
    };
    Ok((backend,workers))
}
fn main() -> io::Result<()> {
    let (backend,workers)=options().unwrap_or_else(|e|{eprintln!("{e}");std::process::exit(64)});
    let base=base_config().map_err(|e|io::Error::other(format!("{e:?}")))?;
    let mut workspace=GasRateWorkspace::new(&backend);
    let mut out=io::BufWriter::new(io::stdout().lock());
    let mut input=io::stdin().lock(); let mut line=String::new();
    loop {
        line.clear(); if input.read_line(&mut line)?==0 {break;}
        let request=line.trim_end_matches(['\r','\n']);
        if request=="QUIT" {break;}
        if request=="META" {
            writeln!(out,"{{\"schema\":\"REI_GAS_RHS_PROTOCOL_V2\",\"rhs_evaluator\":\"{}\",\"step_evaluator\":\"IGM_GRACKLE_DIRECT_F64_V1\",\"photo_owner\":\"OFF\",\"workers\":{},\"cache\":\"ONE_ENTRY_EXACT_EOS_T_BITS\",\"max_batch\":{}}}",backend.evaluator_id(),workers,MAX_BATCH)?;
        } else { match execute(request,base,&backend,&mut workspace,workers) {
            Ok(Reply::Single{row,len})=>write_row(&mut out,&row[..len])?,
            Ok(Reply::Batch{rows,stats})=>{
                writeln!(out,"BATCH_OK {} 28",rows.len())?;
                for rates in rows {
                    let mut row=[0.0;28];row[..27].copy_from_slice(&rates.vector());row[27]=rates.chemical;
                    write_row(&mut out,&row)?;
                }
                writeln!(out,"BATCH_END {} {} {}",stats.evaluations,stats.preparations,stats.exact_temperature_hits)?;
            },
            Err(e)=>writeln!(out,"ERR {e:?}")?,
        }}
        out.flush()?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn payload() -> String {
        let n=[0.0,180.0,20.0,0.0045,0.0005,0.0,0.0,0.0,0.0,0.0,12.0,3.0,1.0];
        let nuclei=IsotopeNumberState::new(n).unwrap();
        let u=1.5*rei_iso_couple_reference::mixture_eos::KB_J_K*
            nuclei.thermal_particle_density_all_thermal_m3().unwrap()*1e4;
        n.into_iter().chain([u]).map(|v|format!("{v:.17e}")).collect::<Vec<_>>().join(" ")
    }
    #[test]
    fn original_rhs_layout_and_batch_reply_agree_exactly() {
        let backend=IgmRateBackend::Direct;let mut ws=GasRateWorkspace::new(&backend);
        let base=base_config().unwrap();let p=payload();
        let Reply::Single{row,len}=execute(&format!("RHS 7 29 {p}"),base,&backend,&mut ws,1).unwrap() else {panic!()};
        assert_eq!(len,28);
        let Reply::Batch{rows,stats}=execute(&format!("RHS_BATCH 2 7 29 {p} {p}"),base,&backend,&mut ws,1).unwrap() else {panic!()};
        assert_eq!(stats.preparations,1);assert_eq!(stats.exact_temperature_hits,1);
        for r in rows {assert_eq!(row[..27].iter().map(|x|x.to_bits()).collect::<Vec<_>>(),r.vector().map(f64::to_bits));assert_eq!(row[27].to_bits(),r.chemical.to_bits());}
    }
    #[test]
    fn malformed_batch_is_rejected_before_output() {
        let backend=IgmRateBackend::Direct;let mut ws=GasRateWorkspace::new(&backend);let base=base_config().unwrap();
        for request in ["RHS_BATCH 0 7 29","RHS_BATCH 65537 7 29","RHS_BATCH 1 7 NaN","RHS_BATCH 1 7 29","RHS 8 29","UNKNOWN"] {
            assert!(execute(request,base,&backend,&mut ws,1).is_err(),"{request}");
        }
    }
}
