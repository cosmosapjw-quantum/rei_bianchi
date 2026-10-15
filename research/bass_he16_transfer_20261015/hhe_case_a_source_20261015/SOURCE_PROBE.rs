use rei_microphysics::{igm_rates::igm_rates,igm_state::IgmGasState,igm_thermal::{igm_point_rhs,IgmPhotoInput},axbi_driver::{Driver,DriverConfig}};
fn main(){
 let (driver,init)=Driver::new(DriverConfig::baseline()).unwrap();
 let p=driver.background.point_at_scale(init.a).unwrap();let nh=driver.n_h0_cm3/init.a.powi(3);
 let nhe=driver.n_he0_cm3/init.a.powi(3);
 for eta in [0.,1e-5,1e-4]{
  let gas=IgmGasState::from_temperature([1.-eta,eta/2.,1.-eta],nh,nhe,8.098143045064857).unwrap();
  let t=gas.eos(nh,nhe).unwrap().temperature_k;
  let rates=igm_rates(t).unwrap();
  let rhs=igm_point_rhs(&gas,nh,nhe,0.,2.7255/init.a,IgmPhotoInput::default()).unwrap();
  println!("eta={} nh={} nhe={} T={} ne={}",eta,nh,nhe,t,gas.eos(nh,nhe).unwrap().electron_density_cm3);
  println!("ci={:?} rr={:?} dr={} wmicro={} CMB={} ft={:?}",rates.ci_cm3_s,rates.rr_cm3_s,rates.dr_cm3_s,rhs.thermal_micro_erg_cm3_s,rhs.cmb_to_gas_erg_cm3_s,rhs.fraction_dt);
  println!("rr events={:?} CI events={:?} DR={} RR thermal={:?} escape={} bind={} photo={:?}",rhs.rr_events_cm3_s,rhs.ci_events_cm3_s,rhs.dr_events_cm3_s,rhs.rr_thermal_sink_erg_cm3_s,rhs.escape_erg_cm3_s,rhs.binding_micro_erg_cm3_s,rhs.photo_events_cm3_s);
  println!("event+energy identity {}", rhs.thermal_micro_erg_cm3_s+rhs.binding_micro_erg_cm3_s+rhs.escape_erg_cm3_s-rhs.cmb_to_gas_erg_cm3_s);
 }
}