//! Frozen fixed-opacity point comparator. No chemistry integration.
use rei_microphysics::{GeometrySnapshot, HHeModel, AtomicProvider, Absorber};
use rei_microphysics::axbi_covariant_transport::{CovariantTransport,FIT_THRESHOLDS_EV};
use rei_microphysics::axbi_sources::{AxbiSource,AngularCell};
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_rates::{igm_rates,IgmRates};
use rei_microphysics::igm_thermal::{igm_point_rhs,IgmPhotoInput,IgmPointRhs};
use std::fmt::Write;
fn field<T:std::fmt::Debug>(s:&mut String,k:&str,v:T){if s.len()>1{s.push(',');}write!(s,"\"{}\":{:?}",k,v).unwrap();}
fn rhs_json(v:&IgmPointRhs)->String {let mut s=String::from("{");
field(&mut s,"fraction_dt",v.fraction_dt);
field(&mut s,"species_chemical_cm3_s",v.species_chemical_cm3_s);
field(&mut s,"w_dt_erg_per_h_s",v.w_dt_erg_per_h_s);
field(&mut s,"temperature_dt_k_s",v.temperature_dt_k_s);
field(&mut s,"photo_events_cm3_s",v.photo_events_cm3_s);
field(&mut s,"ci_events_cm3_s",v.ci_events_cm3_s);
field(&mut s,"rr_events_cm3_s",v.rr_events_cm3_s);
field(&mut s,"dr_events_cm3_s",v.dr_events_cm3_s);
field(&mut s,"ci_thermal_sink_erg_cm3_s",v.ci_thermal_sink_erg_cm3_s);
field(&mut s,"rr_thermal_sink_erg_cm3_s",v.rr_thermal_sink_erg_cm3_s);
field(&mut s,"dr_thermal_sink_erg_cm3_s",v.dr_thermal_sink_erg_cm3_s);
field(&mut s,"ce_thermal_sink_erg_cm3_s",v.ce_thermal_sink_erg_cm3_s);
field(&mut s,"freefree_thermal_sink_erg_cm3_s",v.freefree_thermal_sink_erg_cm3_s);
field(&mut s,"thermal_micro_erg_cm3_s",v.thermal_micro_erg_cm3_s);
field(&mut s,"binding_micro_erg_cm3_s",v.binding_micro_erg_cm3_s);
field(&mut s,"escape_erg_cm3_s",v.escape_erg_cm3_s);
field(&mut s,"cmb_to_gas_erg_cm3_s",v.cmb_to_gas_erg_cm3_s);
field(&mut s,"photo_input_erg_cm3_s",v.photo_input_erg_cm3_s);
field(&mut s,"expansion_work_erg_cm3_s",v.expansion_work_erg_cm3_s);
field(&mut s,"ci_floor_events_cm3_s",v.ci_floor_events_cm3_s);
field(&mut s,"ce_cap_cooling_erg_cm3_s",v.ce_cap_cooling_erg_cm3_s);
field(&mut s,"excluded_dr_cooling_erg_cm3_s",v.excluded_dr_cooling_erg_cm3_s);
s.push('}');s}
fn rates_json(v:&IgmRates)->String {let mut s=String::from("{");
field(&mut s,"ci_cm3_s",v.ci_cm3_s);
field(&mut s,"rr_cm3_s",v.rr_cm3_s);
field(&mut s,"dr_cm3_s",v.dr_cm3_s);
field(&mut s,"ce_erg",v.ce_erg);
field(&mut s,"rr_cooling_erg_cm3_s",v.rr_cooling_erg_cm3_s);
field(&mut s,"dr_cooling_erg_cm3_s",v.dr_cooling_erg_cm3_s);
field(&mut s,"dr_raw_cooling_erg_cm3_s",v.dr_raw_cooling_erg_cm3_s);
field(&mut s,"freefree_erg_cm3_s",v.freefree_erg_cm3_s);
field(&mut s,"ci_floor_cm3_s",v.diagnostics.ci_floor_cm3_s);
field(&mut s,"ce_cap_erg",v.diagnostics.ce_cap_erg);
field(&mut s,"dr_excluded_erg_cm3_s",v.diagnostics.dr_excluded_erg_cm3_s);
field(&mut s,"dr_low_branch",v.diagnostics.dr_low_branch);
s.push('}');s}

fn run(id:&str,q:&[f64],counts:&[f64],b:f64,dt:f64,t:f64,tcmb:f64,yhe:f64){
 let nh=0.01; let f=[0.31,0.23,0.17]; let mus=[0.0,0.37,-0.81];
 let reference=GeometrySnapshot::new([1.0;3],[0.0;3]).unwrap();
 let now=GeometrySnapshot::new([(-b).exp(),(-b).exp(),(2.0*b).exp()],[0.0;3]).unwrap();
 let mut source=AxbiSource::new(nh,0.1,2,4).unwrap();
 source.angular_cells=mus.iter().map(|&mu|AngularCell{mu,count_fraction:1.0/3.0}).collect();
 let tr=CovariantTransport::new(&source,reference,1,10.0,100.0).unwrap();
 let mut input=tr.empty_state();
 for i in 0..q.len(){tr.add_delta(&mut input,i,q[i],counts[i]).unwrap();}
 let gas=IgmGasState::from_temperature(f,nh,nh*yhe,t).unwrap();
 let eos=gas.eos(nh,nh*yhe).unwrap();
 let abs=[nh*(1.0-f[0]),nh*yhe*(1.0-(f[1]+f[2])),nh*yhe*f[1]];
 let prep=tr.prepare(&input,&now).unwrap();
 let result=prep.evaluate(abs,nh,dt).unwrap();
 let on=igm_point_rhs(&gas,nh,nh*yhe,0.0,tcmb,result.photo).unwrap();
 let off=igm_point_rhs(&gas,nh,nh*yhe,0.0,tcmb,IgmPhotoInput::default()).unwrap();
 let rates=igm_rates(eos.temperature_k).unwrap();
 let rays=tr.ray_geometry(&now).unwrap();
 let energies:Vec<f64>=q.iter().enumerate().map(|(i,v)|v*rays[i].scale).collect();
 let species=[Absorber::HI,Absorber::HeI,Absorber::HeII];
 let provider=AtomicProvider::reference();
 let sigma:Vec<[f64;3]>=energies.iter().map(|&e|std::array::from_fn(|i|provider.cross_section(species[i],e).unwrap())).collect();
 let active:Vec<[bool;3]>=energies.iter().map(|&e|std::array::from_fn(|i|e>=FIT_THRESHOLDS_EV[i])).collect();
 let mut s=String::from("{");
 field(&mut s,"id",id);field(&mut s,"q_ev",q);field(&mut s,"input_counts",counts);field(&mut s,"mu0",&mus[..q.len()]);
 field(&mut s,"a",1.0);field(&mut s,"b",b);field(&mut s,"dt_s",dt);field(&mut s,"nh",nh);field(&mut s,"yhe",yhe);field(&mut s,"h",0.0);
 field(&mut s,"requested_t",t);field(&mut s,"tcmb",tcmb);field(&mut s,"fractions",f);field(&mut s,"w",gas.w_erg_per_h);
 field(&mut s,"temperature",eos.temperature_k);field(&mut s,"ne",eos.electron_density_cm3);field(&mut s,"u",eos.u_erg_cm3);
 field(&mut s,"absorbers_cm3",abs);field(&mut s,"node_count",prep.node_count());field(&mut s,"transport_workers",tr.transport_threads());
 field(&mut s,"actual_energy_ev",energies);field(&mut s,"sigma_cm2",sigma);field(&mut s,"fit_active",active);
 field(&mut s,"input_number_cells",input.number);field(&mut s,"input_energy_ref_cells",input.energy_ref);
 field(&mut s,"survivors_cells",result.state.number);field(&mut s,"survivor_energy_ref_cells",result.state.energy_ref);
 field(&mut s,"gamma_s",result.photo.gamma_s);field(&mut s,"heat_erg_per_absorber_s",result.photo.heat_erg_per_absorber_s);
 field(&mut s,"absorbed_per_h",result.absorbed_per_h);field(&mut s,"binding_ev_per_h",result.binding_ev_per_h);field(&mut s,"heat_ev_per_h",result.heat_ev_per_h);
 let constants=HHeModel::controlled_fixture();field(&mut s,"kb_erg_k",constants.kb_erg_k);field(&mut s,"ev_erg",constants.ev_erg);field(&mut s,"c_cm_s",constants.c_cm_s);field(&mut s,"chi_ev",constants.threshold_ev);
 write!(s,",\"on\":{},\"off\":{},\"rates\":{}",rhs_json(&on),rhs_json(&off),rates_json(&rates)).unwrap();s.push('}');println!("{}",s);
}
fn main(){
 // Frozen case matrix: adjacent binary64 thresholds; exact equality at b=0.
 for (i,&e) in FIT_THRESHOLDS_EV.iter().enumerate(){
  for (name,q) in [("below",f64::from_bits(e.to_bits()-1)),("equal",e),("above",f64::from_bits(e.to_bits()+1))]{
   for dt in [0.0,1e9]{run(&format!("threshold{}_{}_dt{}",i,name,dt),&[q],&[0.013],0.0,dt,1e4,30.0,0.083);}
  }
 }
 for b in [0.0,0.1,-0.1]{for t in [100.0,1e4,1e5]{for dt in [0.0,1e9,1e16]{
  let tcmb=if t==100.0 {300.0}else{30.0};
  run(&format!("mixed_b{}_T{}_dt{}",b,t,dt),&[20.0,40.0,80.0],&[0.013,0.007,0.003],b,dt,t,tcmb,0.083);
 }}}
 for dt in [0.0,1e9]{run(&format!("no_helium_dt{}",dt),&[20.0,40.0,80.0],&[0.013,0.007,0.003],0.1,dt,1e4,30.0,0.0);}
 run("empty_photons",&[],&[],0.0,1e9,1e4,30.0,0.083);
}
