//! Portable read-only Rust C8/C9 intake validator for new stress-coupled
//! Einstein gamma/nu/massive background, source unique from old AX03.
//! No owner native driver edits, no H/He physics admission.
use std::{env,fs::File,io::{BufRead,BufReader},collections::BTreeMap};
fn bad(msg:&str)->!{eprintln!("REI_INITIAL_PI_TABLE_REJECT:{msg}");std::process::exit(3)}
fn parse(col:&[&str],heads:&[String],key:&str)->f64 {
 let i=heads.iter().position(|z|z==key).unwrap_or_else(||bad("FIELD_MISSING"));
 let val=col[i].parse::<f64>().unwrap_or_else(|_|bad("NOT_NUMBER"));
 if !val.is_finite(){bad("NONFINITE")}val
}
fn main(){
 let arg:Vec<_>=env::args().skip(1).collect();
 if arg.len()!=1{bad("CSV_REQUIRED")}
 let f=File::open(&arg[0]).unwrap_or_else(|_|bad("CANNOT_OPEN"));
 let mut lines=BufReader::new(f).lines();
 let h=lines.next().unwrap_or_else(||bad("EMPTY")).unwrap();
 let heads=h.split(',').map(str::to_owned).collect::<Vec<String>>();
 let mut cases=BTreeMap::<String,(usize,f64,f64,f64)>::new();
 let mut count=0_usize;let mut checksum=0.0;
 for line in lines {
  let line=line.unwrap_or_else(|_|bad("READ_ERROR"));
  let cols=line.split(',').collect::<Vec<_>>();
  if cols.len()!=heads.len(){bad("ROW_COLUMN_COUNT")}
  let readstr=|key:&str|->&str {
   let ix=heads.iter().position(|s|s==key).unwrap_or_else(||bad("UNKNOWN_FIELD"));
   cols[ix]
  };
  let study=readstr("study_mode");
  if !["stress_only_zero_shear","cancellation_no_thomson",
        "cancellation_real_HHe_Thomson"].contains(&study){
      bad("UNKNOWN_STRESS_STUDY_MODE")
  }
  if readstr("physics_family")!="REI_BASS_PR140_Einstein_massive_gamma_nu"{
      bad("NOT_SOURCE_LOCKED_EINSTEIN_FAMILY")
  }
  let key=format!("{}:{}",study,readstr("scenario_id"));
  let t=parse(&cols,&heads,"proper_elapsed_s");
  let a=parse(&cols,&heads,"a");
  let z=parse(&cols,&heads,"mean_redshift");
  let q=parse(&cols,&heads,"original_q_ref_compatibility");
  let sigma0=parse(&cols,&heads,"Sigma_ref_abs");
  let orient=parse(&cols,&heads,"orientation_ref");
  let H=parse(&cols,&heads,"H_per_s");
  let s=parse(&cols,&heads,"s_per_s");
  let b=parse(&cols,&heads,"b");
  let sh=parse(&cols,&heads,"signed_s_over_H");
  let Sigma=parse(&cols,&heads,"Sigma_abs");
  let perp=parse(&cols,&heads,"H_perp_per_s");
  let axial=parse(&cols,&heads,"H_parallel_per_s");
  let H0_rho=parse(&cols,&heads,"rhocrit0_Jm3");
  let d=parse(&cols,&heads,"dust_energy_norm");
  let mas=parse(&cols,&heads,"massive_energy_norm");
  let rad=parse(&cols,&heads,"rad_energy_norm");
  let ol=parse(&cols,&heads,"omega_lambda");
  let Pi_g=parse(&cols,&heads,"Pi_gamma_Pa");
  let Pi_n=parse(&cols,&heads,"Pi_nu_Pa");
  let Pi_m=parse(&cols,&heads,"Pi_massive_Pa");
  let Pi=parse(&cols,&heads,"Pi_total_Pa");
  let numg=parse(&cols,&heads,"gamma_number_mono");
  let numn=parse(&cols,&heads,"nu_number_mono");
  let electron=parse(&cols,&heads,"source_n_e_cm3");
  let row_no=parse(&cols,&heads,"row");
  let Hamilton_err=parse(&cols,&heads,"Hamiltonian_relative_error");
  if !H.is_finite()||H<=0.||a<=0.||t<0.||H0_rho<=0.||d<0.||mas<0.||rad<=0.||electron<0.{
   bad("POSITIVE_PHYSICAL_DOMAIN")
  }
  if (z-(1./a-1.)).abs()>3e-13*20_f64.max(z.abs()){bad("MEAN_REDSHIFT_CHART")}
  let expected0=3_f64.sqrt()*q.abs()/(1.+q*q).sqrt();
  if (sigma0-expected0).abs()>5e-13{bad("SIGNED_SHEAR_INITIAL_ADAPTER")}
  let sign=if q>0.{1.}else if q<0.{-1.}else{0.};
  if orient!=sign{bad("SIGN_ORIENTATION")}
  if (Sigma-3_f64.sqrt()*s.abs()/H).abs()>8e-13{bad("PUBLIC_SCALAR_SIGMA_CONTRACT")}
  if (sh-s/H).abs()>8e-13{bad("SIGNED_SOURCE_COMPONENT")}
  if ((2.*perp+axial)/(3.*H)-1.).abs()>5e-13{bad("DIRECTIONAL_HUBBLE_TRACE")}
  if ((perp-(H-s))/H).abs()>5e-13 || ((axial-(H+2.*s))/H).abs()>5e-13{bad("PHYSICAL_HUBBLE_AXES")}
  let h0sq=8.*std::f64::consts::PI*6.67430e-11*H0_rho/
          (3.*299792458.0*299792458.0);
  let hc=h0sq*(d+mas+rad+ol)+s*s;
  if (H*H/hc-1.).abs()>8e-13 || Hamilton_err>8e-13{bad("EINSTEIN_HAMILTONIAN_CONSTRAINT")}
  if (Pi-(Pi_g+Pi_n+Pi_m)).abs()>(1e-11*(Pi_g.abs()+Pi_n.abs()+Pi_m.abs()).max(1e-32)){
      bad("PI_TENSOR_AMPLITUDE_CLOSURE")
  }
  if (numg-1.).abs()>8e-11 || (numn-1.).abs()>8e-11{bad("PHOTON_NEUTRINO_NUMBER")}
  if study!="cancellation_real_HHe_Thomson" && electron!=0.{
    bad("GAMMA_ELECTRON_SOURCE_MIXED")
  }
  if study=="cancellation_real_HHe_Thomson" && electron<=0.{
    bad("SOURCE_HHE_ELECTRON_NOT_POSITIVE")
  }
  let ent=cases.entry(key.clone()).or_insert((0,-1.0,0.0,0.0));
  if row_no !=ent.0 as f64{bad("UNEXPECTED_CASE_ORDER")}
  if ent.0==0 {
    if t!=0. || b!=0. {bad("NO_INITIAL_ISOTROPIC_AXES_OR_CLOCK")}
    if study=="stress_only_zero_shear" && sigma0!=0.{bad("STRESS_ONLY_SIGMA0")}
  }else if !(t>ent.1){bad("NONMONOTONE_PROPER_CLOCK")}
  ent.1=t;ent.2=sh;ent.3=b;ent.0+=1;
  checksum+=sh +Sigma + t*1e-16+Pi*1e12;
  count+=1;
 }
 if count!=3864 || cases.len()!=24 || !cases.values().all(|x|x.0==161){
   bad("INCOMPLETE_BACKGROUND_SUPPLIER")
 }
 for (key,r) in &cases {
   if !key.starts_with("stress_only_zero_shear:") && r.2.abs()>3e-10{
     bad("SHEAR_CANCELLATION_NOT_MET")
   }
   if r.3.abs()<2e-5{bad("MISSING_METRIC_MEMORY")}
 }
 println!("{{\"schema\":\"rei.pi_stress_background_consumer.v1\",\"rows\":{},\"cases\":{},\"per_case\":161,\"Hamiltonian_and_Pi_source_checks\":\"PASS\",\"checksum\":{:.17e},\"native_REI_owner_modified\":false}}",
 count,cases.len(),checksum);
}
