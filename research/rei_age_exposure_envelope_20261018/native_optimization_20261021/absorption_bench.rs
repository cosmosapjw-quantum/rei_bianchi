// Actual native prepared-absorption kernel only: no gas IVP/RHS/history.
use rei_microphysics::{axbi_driver::{Driver,DriverConfig},axbi_covariant_transport::AbsorptionResult};
use std::{sync::Arc,time::Instant};
fn bits(rows:&[AbsorptionResult])->Vec<u64>{
 let mut v=vec![];
 for r in rows {
  for x in r.state.number.iter().chain(&r.state.energy_ref).chain(&r.state.support_lo).chain(&r.state.support_hi)
   .chain(&r.photo.gamma_s).chain(&r.photo.heat_erg_per_absorber_s).chain(&r.absorbed_per_h) {v.push(x.to_bits());}
  v.extend([r.binding_ev_per_h.to_bits(),r.heat_ev_per_h.to_bits()]);
 }v
}
fn main()->Result<(),Box<dyn std::error::Error>> {
 let prepare_start=Instant::now();
 let mut cfg=DriverConfig::baseline();cfg.q_ref=0.;cfg.n_mu=8;cfg.energy_subdivisions=8;cfg.transport_cells=16;cfg.transport_threads=1;cfg.inactive_hi_split=false;cfg.background_panels=256;
 let (d,s)=Driver::new(cfg)?;let g=d.geometry_point(s.a)?.geometry()?;
 let mut state=d.transport.empty_state();d.transport.inject(&mut state,&g,1./s.a-1.,1e10)?;
 let prepared=d.transport.prepare(&state,&g)?;let nodes=prepared.node_count();let cohorts=Arc::new(vec![prepared;32]);
 // Fixed positive gas fractions from the original initial physical setup.
 let nh=d.n_h0_cm3/s.a.powi(3);let nhe=d.n_he0_cm3/s.a.powi(3);let abs=[nh*(1.-0.01),nhe*(1.-0.01-0.001),nhe*0.01];let dt=1e10;
 let serial=||cohorts.iter().map(|p|p.evaluate(abs,nh,dt)).collect::<Result<Vec<_>,_>>();
 let oracle=bits(&serial()?);let prep_seconds=prepare_start.elapsed().as_secs_f64();
 for mode in [0,1,2,4] {
  let transport=d.transport.clone().with_threads(if mode==0 {1} else {mode})?;
  let evaluate=||if mode==0 {serial()} else {transport.rei_ordered_cohort_evaluate(Arc::clone(&cohorts),abs,nh,dt)};
  assert_eq!(bits(&evaluate()?),oracle);
  for repeat in 0..5 {
   let start=Instant::now();let mut last=vec![];
   for _ in 0..20 {last=std::hint::black_box(evaluate()?);}
   let seconds=start.elapsed().as_secs_f64();assert_eq!(bits(&last),oracle);
   println!("{{\"mode\":\"{}\",\"workers\":{},\"repeat\":{},\"iterations\":20,\"cohorts\":32,\"nodes_per_cohort\":{},\"wall_seconds\":{:.17e},\"all_scientific_fields_bitwise_equal\":true,\"fixture_prepare_seconds\":{:.17e},\"dt\":{:.17e},\"absorbers\":[{:.17e},{:.17e},{:.17e}],\"scope\":\"PREPARED_NATIVE_BE_KERNEL_ONLY_NO_RHS\"}}",if mode==0 {"original_serial"} else {"ordered_pool"},if mode==0 {1} else {mode},repeat,nodes,seconds,prep_seconds,dt,abs[0],abs[1],abs[2]);
  }
 }
 Ok(())
}
