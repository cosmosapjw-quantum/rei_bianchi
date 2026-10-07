use rei_microphysics::{
    igm_config::{parse_config, HistoryConfig},
    igm_photo::packet_opacity,
    igm_state::IgmGasState,
    HHeModel,
};
use short_hhe_control::{
    err, material,
    radiation::{self, Grid},
    v2, Fallible,
};
use std::{fs, io::Write};
fn config() -> Fallible<HistoryConfig> {
    parse_config(
        &fs::read_to_string("../../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg").map_err(err)?,
    )
    .map_err(err)
}
fn initial(cfg: &HistoryConfig) -> Fallible<[f64; 4]> {
    let p = cfg.background.at_ln_a(cfg.start).map_err(err)?;
    Ok(material::values(
        &IgmGasState::from_temperature(cfg.fractions, p.n_h_cm3, p.n_he_cm3, cfg.temperature_k)
            .map_err(err)?,
    ))
}
fn fields(o: v2::Owners) -> [f64; 13] {
    [
        o.n, o.u, o.qn, o.qe, o.red, o.outn, o.oute, o.an[0], o.an[1], o.an[2], o.be[0], o.be[1],
        o.be[2],
    ]
}
fn frozen(cfg: &HistoryConfig) -> Fallible<bool> {
    let s1 = radiation::time_at(cfg, 1, 1);
    let p = cfg.background.at_ln_a(s1).map_err(err)?;
    let y = initial(cfg)?;
    let mut file = fs::File::create("results/frozen_A.csv").map_err(err)?;
    writeln!(file,"base,order,nodes,Nactive,Eactive,emitted_N,emitted_E,redshift_E,out_N,out_E,abs_HI,abs_HeI,abs_HeII,B_HI,B_HeI,B_HeII").map_err(err)?;
    let mut compare = fs::File::create("results/quadrature_A.csv").map_err(err)?;
    writeln!(compare, "base,component,relative_difference,passed").map_err(err)?;
    let mut selected = false;
    for base in [128, 256, 512] {
        let mut results = Vec::new();
        for order in [2, 4] {
            let grid = Grid::new(cfg, base, order)?;
            println!(
                "A base={base} order={order} nodes={} intervals={}",
                grid.nodes.len(),
                grid.intervals
            );
            let a = radiation::transaction(
                cfg,
                &grid,
                p,
                y,
                cfg.start,
                s1,
                &vec![0.; grid.nodes.len()],
            )?;
            let o = a.owners;
            let nres = o.n + o.an.iter().sum::<f64>() + o.outn - o.qn;
            let eres = o.u + o.be.iter().sum::<f64>() + o.red + o.oute - o.qe;
            if nres.abs() > 1e-10 * o.qn.max(1e-10) || eres.abs() > 1e-10 * o.qe.max(1e-20) {
                return Err(format!(
                    "frozen pure-radiation budget N={nres:e},E={eres:e}"
                ));
            }
            let d = material::photo_delta(o.an, o.be, p.n_he_cm3 / p.n_h_cm3);
            let f = p.n_he_cm3 / p.n_h_cm3;
            let binding = d[0] * v2::EPS * v2::CHI[0]
                + f * (v2::CHI[1] * d[1] + (v2::CHI[1] + v2::CHI[2]) * d[2]) * v2::EPS;
            let id = (binding + d[3] - o.be.iter().sum::<f64>()).abs() / o.be.iter().sum::<f64>();
            if id > 2e-12 {
                return Err("shared invariant energy owner identity".into());
            }
            write!(file, "{base},{order},{}", grid.nodes.len()).map_err(err)?;
            for v in fields(o) {
                write!(file, ",{v:.17e}").map_err(err)?;
            }
            writeln!(file).map_err(err)?;
            file.flush().map_err(err)?;
            results.push(fields(o));
        }
        let mut pass = true;
        for i in 0..13 {
            let a = results[0][i];
            let b = results[1][i];
            let rel = if b == 0.0 {
                if a == 0.0 {
                    0.0
                } else {
                    f64::INFINITY
                }
            } else {
                (a - b).abs() / b.abs()
            };
            pass &= rel <= 1e-6;
            writeln!(compare, "{base},{i},{rel:.17e},{}", rel <= 1e-6).map_err(err)?;
        }
        compare.flush().map_err(err)?;
        println!("A quadrature base={base} pass={pass}");
        if base == 512 {
            selected = pass;
        }
    }
    // Independent Python oracle consumes exact binary64 kernel inputs/outputs.
    let mut f = fs::File::create("results/kernel_samples.csv").map_err(err)?;
    writeln!(f, "f,q,r0,r1,r2,h,e,n,u,qn,qe,red,a0,a1,a2,b0,b1,b2").map_err(err)?;
    let c = HHeModel::controlled_fixture();
    let gas = material::gas(y)?;
    for e in [14., 25., 55., 80.] {
        let rates = packet_opacity(&gas, e, p.n_h_cm3, p.n_he_cm3)
            .map_err(err)?
            .map(|v| v / p.hubble_per_s);
        for old in [0., 1e-5] {
            let q = cfg.source.photons_per_h_per_s
                / ((1. / cfg.source.energy_min_ev - 1. / cfg.source.energy_max_ev)
                    * e
                    * p.hubble_per_s);
            let h = cfg.max_dln_a;
            let o = v2::kernel(old, q, rates, h, e).map_err(err)?;
            let vals = [
                old, q, rates[0], rates[1], rates[2], h, e, o.n, o.u, o.qn, o.qe, o.red, o.an[0],
                o.an[1], o.an[2], o.be[0], o.be[1], o.be[2],
            ];
            for (i, x) in vals.iter().enumerate() {
                if i > 0 {
                    write!(f, ",").map_err(err)?;
                }
                write!(f, "{x:.17e}").map_err(err)?;
            }
            writeln!(f).map_err(err)?;
        }
    }

    for i in 0..3 {
        let cutoff = rei_microphysics::verner_cutoff_ev(radiation::SPECIES[i]);
        let eta = cutoff.ln() + cfg.start + 1.4905626121828326e-5;
        let stop = eta - cutoff.ln();
        let (e, _) = short_hhe_control::event_anchor::start_energy(eta, cfg.start, stop)?;
        let h = stop - cfg.start;
        let mut rates = [0.; 3];
        rates[i] = 0.7;
        let old = 0.02;
        let q = 0.4;
        let o = v2::kernel(old, q, rates, h, e).map_err(err)?;
        let vals = [
            old, q, rates[0], rates[1], rates[2], h, e, o.n, o.u, o.qn, o.qe, o.red, o.an[0],
            o.an[1], o.an[2], o.be[0], o.be[1], o.be[2],
        ];
        for (j, x) in vals.iter().enumerate() {
            if j > 0 {
                write!(f, ",").map_err(err)?;
            }
            write!(f, "{x:.17e}").map_err(err)?;
        }
        writeln!(f).map_err(err)?;
    }
    assert_eq!(c.ev_erg, v2::EPS);
    assert_eq!(c.threshold_ev, v2::CHI);
    Ok(selected)
}
fn run() -> Fallible<()> {
    let cfg = config()?;
    if !frozen(&cfg)? {
        return Err("A 512 quadrature gate failed; B not authorized by conditional gate".into());
    }
    println!("FROZEN_A_PASS");
    for order in [2, 4] {
        let grid = Grid::new(&cfg, 512, order)?;
        for phases in [true, false] {
            for m in [1, 2, 4, 8] {
                short_hhe_control::output::history(&cfg, &grid, m, phases)?;
            }
        }
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("PARTIAL: {e}");
        std::process::exit(2)
    }
}
