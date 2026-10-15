//! Fresh, bounded diagnostic REI physics from zbar20 for a selected gas IC.
//! Uses exact actual native source and adaptive chemistry/photons; no resume,
//! production output, or mismatch with PR127's local GL4 proper-time clock.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::axbi_rates::AxbiProvider;
use rei_microphysics::igm_thermal::IgmPhotoInput;
use std::{env,fs,io::{self,Write},path::PathBuf,time::Instant};

fn run()->Result<(),String> {
    let args=env::args().skip(1).collect::<Vec<_>>();
    if args.len()!=8 || args[0]!="--config" || args[2]!="--output"
        || args[4]!="--case" || args[6]!="--steps" {
        return Err("usage: --config CFG --output CSV --case ID --steps N".into());
    }
    let n=args[7].parse::<usize>().map_err(|_|"invalid step count")?;
    if n==0||n>8192{return Err("bounded 1..8192 accepted steps only".into());}
    let txt=fs::read_to_string(&args[1]).map_err(|e|e.to_string())?;
    let c=DriverConfig::read(&txt).map_err(|e|format!("{e:?}"))?;
    let (driver,mut state)=Driver::new(c).map_err(|e|format!("{e:?}"))?;
    let label=&args[5];
    if label.contains(',')||label.contains('\n') {return Err("invalid case".into());}
    let mut out=io::BufWriter::new(fs::File::create(PathBuf::from(&args[3]))
        .map_err(|e|e.to_string())?);
    writeln!(out,"case_id,accepted,zbar,a,time_s,q_ref,xHII,xHeII,xHeIII,xe_per_H,Tgas_K,H_s_inv,photon_number_per_H,photon_energy_eV_per_H,source_n_per_H,absorbed_n_per_H,energy_ledger_eV_per_H,number_ledger_per_H,last_error,attempts,rejects,rhs_evaluations,photo_free_dxHII_dt_per_s,photo_free_dT_dt_K_per_s,J0_eV_per_H,J1_eV_per_H,J2_eV_per_H")
        .map_err(|e|e.to_string())?;
    let t0=Instant::now();
    for i in 0..=n {
        let z=1./state.a-1.;
        let point=driver.background.point_at_scale(state.a)
            .map_err(|e|format!("{e:?}"))?;
        let nh=driver.n_h0_cm3/state.a.powi(3);
        let nhe=driver.n_he0_cm3/state.a.powi(3);
        let gas=state.gas.eos(nh,nhe).map_err(|e|format!("{e:?}"))?;
        let provider=AxbiProvider.point(&state.gas,nh,nhe,point.h_per_s,
            2.7255/state.a,IgmPhotoInput::default())
            .map_err(|e|format!("{e:?}"))?;
        let (num,u)=driver.photon_inventory(&state);
        let angular=driver.moments(&state).map_err(|e|format!("{e:?}"))?;
        let (rn,ru)=driver.residuals(&state).map_err(|e|format!("{e:?}"))?;
        let x=state.gas.fractions;
        let xe=x[0]+nhe/nh*(x[1]+2.*x[2]);
        writeln!(out,"{label},{i},{z:.17e},{a:.17e},{ts:.17e},{q:.17e},{xh:.17e},{y:.17e},{zz:.17e},{xe:.17e},{t:.17e},{h:.17e},{n:.17e},{u:.17e},{sn:.17e},{ab:.17e},{ru:.17e},{rn:.17e},{er:.17e},{at},{rej},{rhs},{dx:.17e},{dt:.17e},{j0:.17e},{j1:.17e},{j2:.17e}",
            a=state.a,ts=point.time_s,q=driver.config.q_ref,
            xh=x[0],y=x[1],zz=x[2],t=gas.temperature_k,
            h=point.h_per_s,n=num,sn=state.ledgers.source_n,ab=state.ledgers.absorbed_n,
            er=state.last_error,at=state.attempts,rej=state.rejects,
            rhs=state.rhs_evaluations,
            dx=provider.rhs.fraction_dt[0],dt=provider.rhs.temperature_dt_k_s,
            j0=angular[0],j1=angular[1],j2=angular[2])
            .map_err(|e|e.to_string())?;
        // A production controller must NOT count a stationary terminal
        // state as a further accepted science step. Stop at the real
        // zbar endpoint even if a higher diagnostic step cap was requested.
        if i==n || state.a>=1.0/(1.0+driver.config.end_zbar) {break;}
        let mut ok=false;
        for _ in 0..64 {
            if driver.adaptive_step(&mut state)
                .map_err(|e|format!("step index={i} status={e:?}"))? {
                ok=true;break;
            }
        }
        if !ok{return Err(format!("no accepted step within 64 attempts at {i}"));}
        driver.validate(&state,1e-8).map_err(|e|format!("{e:?}"))?;
    }
    out.flush().map_err(|e|e.to_string())?;
    eprintln!("RESULT case={label} accepted={} total_attempts={} rejected={} rhs={} seconds={:.6} zbar={:.12} SHA_BINDING_NATIVE_PR127",state.accepted,state.attempts,state.rejects,state.rhs_evaluations,t0.elapsed().as_secs_f64(),1./state.a-1.);
    Ok(())
}

fn main() {
    if let Err(e)=run(){eprintln!("FAIL {e}");std::process::exit(1);}
}
