//! Opt-in V10 native source clock study on an isolated PR150 source copy.
use rei_microphysics::axbi_driver::{Driver,DriverConfig,BassResearchNumerics};
use rei_microphysics::{igm_rates::igm_rates,HHeModel};
use std::{env,time::Instant};

fn run()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<String>=env::args().collect();
    if args.len()!=3 {return Err("usage: native_v10 MODE 8|16|32|64|128|512|1024".into())}
    let mode=&args[1]; let n:usize=args[2].parse()?;
    if ![8,16,32,64,128,512,1024,2048].contains(&n) {return Err("V10_RUN_DOMAIN".into())}
    let (numerics,no_radiation,half_opacity,rrmp,tight)=match mode.as_str() {
        "legacy_be" => (BassResearchNumerics::Legacy,false,false,false,false),
        "legacy_tight" => (BassResearchNumerics::Legacy,false,false,false,true),
        "no_radiation_be" => (BassResearchNumerics::Legacy,true,false,false,false),
        "no_radiation_rrmp" => (BassResearchNumerics::Legacy,true,false,true,false),
        "split_be" => (BassResearchNumerics::SplitBe,false,false,false,false),
        "uniform_birth" => (BassResearchNumerics::UniformBirth,false,false,false,false),
        "full_exp" => (BassResearchNumerics::FullExponentialFrozen,false,false,false,false),
        "full_exp_half" => (BassResearchNumerics::FullExponentialFrozen,false,true,false,false),
        "full_exp_half_rrmp" => (BassResearchNumerics::FullExponentialFrozen,false,true,true,false),
        "best_tight" => (BassResearchNumerics::FullExponentialFrozen,false,true,true,true),
        _ => return Err("V10_RUN_DOMAIN".into()),
    };
    let mut config=DriverConfig::baseline();
    config.transport_cells=64;
    config.energy_subdivisions=16;
    config.n_mu=8;
    config.transport_threads=1;
    config.max_steps=8192;
    config.max_attempts=8192;
    config.max_rhs=2000000;
    config.max_wall_s=300.0;
    let (mut driver,mut state)=Driver::v10_seed(config)?;
    driver.v10_set_control(numerics,no_radiation,half_opacity,rrmp,tight);
    let t0=Instant::now();
    let dln=1e-5/(n as f64);
    let r=driver.n_he0_cm3/driver.n_h0_cm3;
    let ne_initial_per_h=0.075+r*(0.12+2.0*0.03);
    let c=HHeModel::controlled_fixture();
    println!("step,a,T_K,HII,HeII,HeIII,ne_cm3,photon_n_per_h,photon_u_ev_per_h,thermal_ev_per_h,source_n,absorbed_n,photo_HI,photo_HeI,photo_HeII,rr_HII,rr_HeII,rr_HeIII,dr_HeII,escape_ev_per_h,photon_work_ev_per_h,thermal_work_ev_per_h,cmb_ev_per_h,number_residual,energy_residual,rhs_evaluations,max_newton_residual,proper_dt_s,H_per_s,nh_cm3,nhe_cm3,chemical_ev_per_h,photo_binding_ev_per_h,photoheating_ev_per_h,ci_HI,ci_HeI,ci_HeII,electron_event_residual_per_h,recomb_exposure_max,step_delta_number_residual,step_delta_energy_residual,source_u,boundary_u,boundary_n,initial_energy_ev_per_h,rr_cooling_HII_ev,rr_cooling_HeII_ev,rr_cooling_HeIII_ev,dr_cooling_HeII_ev,ci_cooling_HI_ev,ci_cooling_HeI_ev,ci_cooling_HeII_ev,ce_cooling_HI_ev,ce_cooling_HeI_ev,ce_cooling_HeII_ev,freefree_cooling_ev,photo_heat_direct_ev,photo_binding_direct_ev");
    for j in 0..n {
        let old_a=state.a;
        let (nr_old,er_old)=driver.residuals(&state)?;
        driver.fixed_step(&mut state,dln)?;
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
        print!("{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            j+1,state.a,eos.temperature_k,x[0],x[1],x[2],eos.electron_density_cm3,pn,pu,
            rei_microphysics::igm_state::w_erg_per_h_to_ev(state.gas.w_erg_per_h)?,
            l.source_n,l.absorbed_n,l.photo_events[0],l.photo_events[1],l.photo_events[2],
            l.rr_events[0],l.rr_events[1],l.rr_events[2],l.dr_events,l.escaped_u,
            l.photon_work,l.thermal_work,l.cmb_input,nr,er,state.rhs_evaluations,state.max_newton_residual,
            dt,h,nh,nhe,binding,photo_binding,photoheating,l.ci_events[0],l.ci_events[1],l.ci_events[2],electron_res,stiffness,nr-nr_old,er-er_old);
        println!(",{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            l.source_u,l.boundary_u,l.boundary_n,driver.v10_initial_energy(),
            l.v10_rr_cooling_ev[0],l.v10_rr_cooling_ev[1],l.v10_rr_cooling_ev[2],l.v10_dr_cooling_ev,
            l.v10_ci_cooling_ev[0],l.v10_ci_cooling_ev[1],l.v10_ci_cooling_ev[2],
            l.v10_ce_cooling_ev[0],l.v10_ce_cooling_ev[1],l.v10_ce_cooling_ev[2],
            l.v10_freefree_cooling_ev,l.v10_photo_heat_ev,l.v10_photo_binding_ev);
    }
    eprintln!("V10_COMPLETED mode={} steps={} x_end=1e-5 wall_s={:.9} accepted={} attempts={} rhs={} ",mode,n,t0.elapsed().as_secs_f64(),state.accepted,state.attempts,state.rhs_evaluations);
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("V10_ERROR {e:?}");std::process::exit(2)}}
