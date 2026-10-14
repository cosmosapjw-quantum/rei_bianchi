//! Standalone research driver; includes exact production paired module unchanged.
use rei_microphysics::*;
pub use rei_microphysics::coupled_primary;
#[path = "../../../../rust/rei_microphysics/src/paired_runtime.rs"]
mod paired_runtime;
use paired_runtime::*;
use std::fmt::Write;
fn arr(a:&[f64])->String {format!("[{}]",a.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(","))}
fn state(s:&PairedState)->String {
 format!("{{\"time_s\":{:.17e},\"gas\":{},\"photons\":{},\"lower_guard_n\":{},\"lower_guard_u\":{},\"ledgers\":{}}}",s.time_s,arr(&[s.gas.fractions[0],s.gas.fractions[1],s.gas.fractions[2],s.gas.w_ev_per_h]),arr(&s.photons),arr(&s.lower_guard_n),arr(&s.lower_guard_u),arr(&[s.gas.escape_ev_per_h,s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h]))
}
fn main()->Result<(),Box<dyn std::error::Error>> {
 let c=PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16};
 let nodes=energy_nodes(&c)?;let initial=paired_initial(&c)?;let provider=AtomicProvider::reference();
 let sig=nodes.iter().map(|&e|Ok(arr(&[provider.cross_section(Absorber::HI,e)?,provider.cross_section(Absorber::HeI,e)?,provider.cross_section(Absorber::HeII,e)?]))).collect::<Result<Vec<_>,ForwardError>>()?;
 let mut out=String::new();
 write!(out,"{{\"energy_ev\":{},\"qhat\":[{}],\"sigma_cm2\":[{}],\"initial\":{},\"coefficient_samples\":[",arr(&nodes),(0..128).map(|d|arr(&qhat(&c,d))).collect::<Vec<_>>().join(","),sig.join(","),state(&initial))?;
 for (i,t) in [30000.,35000.,50000.,60000.,110000.].iter().enumerate(){let k=ft03_coefficients(*t)?;if i>0{out.push(',');}write!(out,"{{\"temperature_k\":{},\"alpha_rr\":{},\"beta_ci\":{},\"rr_kinetic\":{},\"alpha_dr\":{},\"dr_energy\":{}}}",t,arr(&k.alpha_rr_cm3_s),arr(&k.beta_ci_cm3_s),arr(&k.rr_kinetic_erg_cm3_s),arr(&k.alpha_dr_cm3_s),arr(&k.dr_energy_erg))?;}
 out.push_str("],\"discrete_runs\":[");let mut first=true;
 for (geometry,h) in [("FLRW",[1e-14;3]),("BI",[1.01e-14,0.99e-14,1e-14])]{
  for dt in [1.25e9,6.25e8,3.125e8]{let mut s=initial.clone();let steps=(1e10/dt) as usize;let(mut local,mut width,mut ledger)=(0.0_f64,0.0_f64,0.0_f64);
   for _ in 0..steps{let trial=paired_trial(&c,h,&s,dt)?;local=local.max(trial.local_bound);width=width.max(trial.public_width);ledger=ledger.max(trial.max_ledger);s=trial.state;}
   if !first{out.push(',');}first=false;
   let mut row=state(&s);row.pop();write!(row,",\"geometry\":\"{}\",\"h_per_s\":{},\"macro_dt_s\":{},\"accepted_steps\":{},\"max_local_bound\":{},\"max_public_width\":{},\"max_ledger\":{},\"actual_paired_trial\":true}}",geometry,arr(&h),dt,steps,local,width,ledger)?;out.push_str(&row);
  }
 }
 out.push_str("],\"small_dt_trials\":[");
 // Diagnostic calls are separate from the six trajectory calls.
 for (i,dt) in [1000000.,100000.,10000.,1000.].iter().enumerate(){let z=paired_trial(&c,[1e-14;3],&initial,*dt)?;if i>0{out.push(',');}write!(out,"{{\"dt_s\":{},\"state\":{}}}",dt,state(&z.state))?;}
 // Occupied lowest-node witness, preserving total photon count and exact boxes.
 let mut witness=initial.clone();witness.photons.fill(0.);witness.photon_boxes.fill(Interval::point(0.).expect("finite constant"));witness.photons[0]=0.05;witness.photon_boxes[0]=Interval::point(0.05).expect("finite constant");
 out.push_str("],\"lowest_node_witness\":[");
 for(i,dt)in[10000.,1000.].iter().enumerate(){let z=paired_trial(&c,[1e-14;3],&witness,*dt)?;if i>0{out.push(',');}write!(out,"{{\"dt_s\":{},\"initial_p0\":0.05,\"final_p0\":{},\"guard_n\":{},\"guard_u\":{}}}",dt,z.state.photons[0],z.state.lower_guard_n[0],z.state.lower_guard_u[0])?;}
 out.push_str("]}");println!("{}",out);Ok(())
}
