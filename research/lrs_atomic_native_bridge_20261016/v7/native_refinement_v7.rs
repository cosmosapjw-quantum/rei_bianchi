//! Source-on FLRW finite-interval refinement using the exact PR150 driver API.
//! `baseline` calls owner fixed_step; `midpoint` calls V7 experimental split.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::{igm_rates::igm_rates,HHeModel};
use std::{env,time::Instant};

fn run()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<String>=env::args().collect();
    if args.len()!=3 {return Err("usage: native_refinement_v7 baseline|midpoint 16|32|64|128".into())}
    let mode=&args[1]; let n:usize=args[2].parse()?;
    if ![16,32,64,128].contains(&n) || !["baseline","midpoint"].contains(&mode.as_str()) {return Err("V7_RUN_DOMAIN".into())}
    let mut config=DriverConfig::baseline();
    config.transport_cells=64;
    config.energy_subdivisions=16;
    config.n_mu=8;
    config.transport_threads=2;
    config.max_steps=256;
    config.max_attempts=512;
    config.max_rhs=200000;
    config.max_wall_s=3600.0;
    let (driver,mut state)=Driver::v7_seed(config)?;
    let t0=Instant::now();
    let dln=1e-5/(n as f64);
    let r=driver.n_he0_cm3/driver.n_h0_cm3;
    let ne_initial_per_h=0.075+r*(0.12+2.0*0.03);
    let c=HHeModel::controlled_fixture();
    println!("step,a,T_K,HII,HeII,HeIII,ne_cm3,photon_n_per_h,photon_u_ev_per_h,thermal_ev_per_h,source_n,absorbed_n,photo_HI,photo_HeI,photo_HeII,rr_HII,rr_HeII,rr_HeIII,dr_HeII,escape_ev_per_h,photon_work_ev_per_h,thermal_work_ev_per_h,cmb_ev_per_h,number_residual,energy_residual,rhs_evaluations,max_newton_residual,proper_dt_s,H_per_s,nh_cm3,nhe_cm3,chemical_ev_per_h,photo_binding_ev_per_h,photoheating_ev_per_h,ci_HI,ci_HeI,ci_HeII,electron_event_residual_per_h,recomb_exposure_max,step_delta_number_residual,step_delta_energy_residual");
    for j in 0..n {
        let old_a=state.a;
        let (nr_old,er_old)=driver.residuals(&state)?;
        if mode=="baseline" {driver.fixed_step(&mut state,dln)?;} else {driver.fixed_step_v7(&mut state,dln)?;}
        let nh=driver.n_h0_cm3/state.a.powi(3); let nhe=driver.n_he0_cm3/state.a.powi(3);
        let eos=state.gas.eos(nh,nhe)?;
        let (pn,pu)=driver.photon_inventory(&state);
        let (nr,er)=driver.residuals(&state)?;
        let l=&state.ledgers; let x=state.gas.fractions;
        let dt=driver.geometry_increment(old_a,state.a)?.proper_time_s;
        let h=driver.geometry_point(state.a)?.h_per_s;
        let binding=c.threshold_ev[0]*x[0]+r*(c.threshold_ev[1]*x[1]+(c.threshold_ev[1]+c.threshold_ev[2])*x[2]);
        let photo_binding=c.threshold_ev[0]*l.photo_events[0]+c.threshold_ev[1]*l.photo_events[1]+c.threshold_ev[2]*l.photo_events[2];
        let photoheating=l.source_u-pu-l.photon_work-l.boundary_u-photo_binding;
        let ne_per_h=x[0]+r*(x[1]+2.0*x[2]);
        let event_balance=l.photo_events.iter().sum::<f64>()+l.ci_events.iter().sum::<f64>()-l.rr_events.iter().sum::<f64>()-l.dr_events;
        let electron_res=ne_per_h-ne_initial_per_h-event_balance;
        let rates=igm_rates(eos.temperature_k)?;
        let stiffness=(0..3).map(|i|dt*eos.electron_density_cm3*(rates.rr_cm3_s[i]+if i==1 {rates.dr_cm3_s} else {0.0})).fold(0.0_f64,f64::max);
        println!("{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            j+1,state.a,eos.temperature_k,x[0],x[1],x[2],eos.electron_density_cm3,pn,pu,
            rei_microphysics::igm_state::w_erg_per_h_to_ev(state.gas.w_erg_per_h)?,
            l.source_n,l.absorbed_n,l.photo_events[0],l.photo_events[1],l.photo_events[2],
            l.rr_events[0],l.rr_events[1],l.rr_events[2],l.dr_events,l.escaped_u,
            l.photon_work,l.thermal_work,l.cmb_input,nr,er,state.rhs_evaluations,state.max_newton_residual,
            dt,h,nh,nhe,binding,photo_binding,photoheating,l.ci_events[0],l.ci_events[1],l.ci_events[2],electron_res,stiffness,nr-nr_old,er-er_old);
    }
    eprintln!("V7_COMPLETED mode={} steps={} x_end=1e-5 wall_s={:.9} accepted={} attempts={} rhs={} ",mode,n,t0.elapsed().as_secs_f64(),state.accepted,state.attempts,state.rhs_evaluations);
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("V7_ERROR {e:?}");std::process::exit(2)}}
