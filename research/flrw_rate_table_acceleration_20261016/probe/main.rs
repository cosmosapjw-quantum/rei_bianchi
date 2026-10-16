#![allow(dead_code)]
#[derive(Debug,Clone)] pub enum ForwardError { InvalidInput(&'static str) }
#[path="../../../rust/rei_microphysics/src/igm_rates.rs"] mod igm_rates;
mod rate_table;
use rate_table::*;
use igm_rates::{igm_rates,IgmRates};
use std::time::Instant;
fn output(r:IgmRates)->[f64;16]{let a=igm_flat(r);std::array::from_fn(|i|if i<15{a[i]}else{r.dr_cooling_erg_cm3_s})}
fn neighbors(t:f64)->[f64;3]{[f64::from_bits(t.to_bits()-1),t,f64::from_bits(t.to_bits()+1)]}
fn main(){
 let nodes:usize=std::env::args().nth(1).unwrap_or("8193".into()).parse().unwrap();
 let start=Instant::now();let table=IgmRateTable::new(nodes).unwrap();let construction=start.elapsed().as_secs_f64();
 let mut ts=Vec::new();let logmax=1e6f64.ln();
 for i in 0..20001{ts.push((logmax*(i as f64+0.371)/20002.0).exp());}
 let mut seed=0x172942a3d8c56f01u64;
 for _ in 0..8192{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);let u=(seed>>11)as f64/(1u64<<53)as f64;ts.push((logmax*u).exp());}
 for i in 0..nodes{let t=if i==0{1.0}else if i+1==nodes{1e6}else{(logmax*i as f64/(nodes-1)as f64).exp()};ts.extend(neighbors(t).into_iter().filter(|&x|x>=1.0&&x<=1e6));}
 for i in 0..nodes-1{for q in [0.25,0.5,0.75]{ts.push((logmax*(i as f64+q)/(nodes-1)as f64).exp());}}
 for t in igm_branch_knots(){ts.extend(neighbors(t));}
 let mut max=[0.0f64;16];let mut worst=[0.0f64;16];let mut mask_errors=0;let mut zero_errors=0;
 let probe=Instant::now();
 for &t in &ts{let direct=igm_rates(t).unwrap();let got=table.rates(t).unwrap();let a=output(direct);let b=output(got);
   for j in 0..16{if a[j]==0.0{if b[j]!=0.0{zero_errors+=1;}}else if a[j].is_normal(){let err=((b[j]-a[j])/a[j]).abs();if err>max[j]{max[j]=err;worst[j]=t;}}}
   let da=direct.diagnostics;let db=got.diagnostics;
   if da.dr_low_branch!=db.dr_low_branch{mask_errors+=1;}
   for j in 0..3{if (da.ci_floor_cm3_s[j]!=0.0)!=(db.ci_floor_cm3_s[j]!=0.0){mask_errors+=1;}if (da.ce_cap_erg[j]!=0.0)!=(db.ce_cap_erg[j]!=0.0){mask_errors+=1;}}
 }
 let seconds=probe.elapsed().as_secs_f64();let mut invalid_errors=0;
 for t in [0.0,0.999999,1e6+1.0,f64::NAN,f64::INFINITY,-1.0]{if table.rates(t).is_ok(){invalid_errors+=1;}}
 let power=LogRateGrid::build(1.0,1e6,257,|t|Ok([2e-10*t.powf(-0.6353)]),|_,_|false,|_,_,_|false).unwrap();
 let mut power_error=0.0f64;for &t in ts.iter().take(1000){let expected=2e-10*t.powf(-0.6353);power_error=power_error.max((power.evaluate(t,|t|Ok([2e-10*t.powf(-0.6353)])).unwrap()[0]/expected-1.0).abs());}
 let curved=LogRateGrid::build(10.0,1000.0,257,|t|Ok([(-500.0/t).exp()]),|_,_|false,|_,_,_|false).unwrap();
 let mut curved_error=0.0f64;for i in 0..1001{let t=(10f64.ln()+(1000f64.ln()-10f64.ln())*(i as f64+0.4)/1002.0).exp();let expected=(-500.0/t).exp();curved_error=curved_error.max((curved.evaluate(t,|t|Ok([(-500.0/t).exp()])).unwrap()[0]/expected-1.0).abs());}
 let curved_bound=(50.0*((100f64.ln()/256.0).powi(2))/8.0).exp_m1();
 assert!(power_error<1e-12);assert!(curved_error<=curved_bound+1e-13);
 for j in 0..16{println!("CHANNEL,{nodes},{j},{:.17e},{:.17e}",max[j],worst[j]);}
 println!("SUMMARY {{\"nodes\":{nodes},\"queries\":{},\"construction_seconds\":{construction:.9},\"probe_seconds\":{seconds:.9},\"max_relative_error\":{:.17e},\"mask_errors\":{mask_errors},\"zero_errors\":{zero_errors},\"invalid_errors\":{invalid_errors},\"blocked_cells\":{},\"storage_bytes\":{},\"powerlaw_relative_error\":{power_error:.17e},\"curved_relative_error\":{curved_error:.17e},\"curved_analytic_bound\":{curved_bound:.17e},\"seed\":\"0x172942a3d8c56f01\",\"derivative_api\":false}}",ts.len(),max.iter().copied().fold(0.0,f64::max),table.grid().blocked_cells(),table.grid().storage_bytes());
}
