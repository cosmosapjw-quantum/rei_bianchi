//! Research probe only, exact PR378 native owner with initial-energy rebasing.
use rei_microphysics::{axbi_covariant_driver::{Driver,DriverConfig,DriverState},general_history::{GeneralHistory,HistoryPoint},igm_state::{IgmGasState,w_ev_per_h_to_erg,w_erg_per_h_to_ev},igm_thermal::{igm_point_rhs,IgmPhotoInput},ForwardError};
use std::{fs,io::{BufWriter,Write}};
const H0:f64=2.1842852410855023e-18;
fn map<T>(x:Result<T,ForwardError>)->Result<T,String>{x.map_err(|e|format!("{e:?}"))}
fn gas(q:[f64;4])->Result<IgmGasState,String>{map(IgmGasState::new([q[0],q[1],q[2]],map(w_ev_per_h_to_erg(q[3]))?))}
fn q(s:&DriverState)->Result<[f64;4],String>{Ok([s.gas.fractions[0],s.gas.fractions[1],s.gas.fractions[2],map(w_erg_per_h_to_ev(s.gas.w_erg_per_h))?])}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();if args.len()!=4{return Err("config history point.csv step.csv".into())}
 let txt=fs::read_to_string(&args[1])?;let mut v=Vec::new();
 for line in txt.lines().skip(1){let a=line.split(',').map(str::parse::<f64>).collect::<Result<Vec<_>,_>>()?;if a.len()!=16{return Err("history columns".into())}v.push(a)}
 let points:Vec<_>=v.iter().map(|r|HistoryPoint{a:r[0],h:r[1],f:std::array::from_fn(|i|std::array::from_fn(|j|r[2+3*i+j]))}).collect();
 let mut cfg=map(DriverConfig::read(&fs::read_to_string(&args[0])?))?;
 cfg.end_zbar=1./points.last().ok_or("no history")?.a-1.+1e-10;
 let (mut d,s)=map(Driver::new_general(cfg, map(GeneralHistory::new(points.clone(),4,8))?))?;
 let base=q(&s)?;let scale=[base[0],1e-4,1e-4,base[3]];
 for i in 0..4{if (base[i]-v[0][11+i]).abs()>1e-14{return Err(format!("initial gas mismatch {i} {} {}",base[i],v[0][11+i]).into())}}
 let mut p=BufWriter::new(fs::File::create(&args[2])?);let mut o=BufWriter::new(fs::File::create(&args[3])?);
 writeln!(p,"snapshot,col,eps,x,y,z,w,fx,fy,fz,fw,charge_res,energy_res")?;
 writeln!(o,"grid,col,eps,du,x0,y0,z0,w0,x1,y1,z1,w1,photon_n,photon_u,energy_res,number_res,metric,rhs")?;
 let eps=[0.02,0.01,0.005,0.0025];
 for i in [0,v.len()/2,v.len()-1]{
  let r=&v[i];let b=[r[11],r[12],r[13],r[14]];let nh=d.n_h0_cm3/r[0].powi(3);let nhe=d.n_he0_cm3/r[0].powi(3);
  let mut eval=|col:i32,e:f64|->Result<(),Box<dyn std::error::Error>>{
   let mut x=b;if col>=0{x[col as usize]+=e*scale[col as usize];}
   let f=map(igm_point_rhs(&gas(x)?,nh,nhe,H0*r[1],2.7255/r[0],IgmPhotoInput::default()))?;
   let f0=f.fraction_dt;let w=map(w_erg_per_h_to_ev(f.w_dt_erg_per_h_s.abs()))?*f.w_dt_erg_per_h_s.signum();
   let ch=f.species_chemical_cm3_s;
   let charge=ch[1]+ch[3]+2.*ch[4]-ch[5];
   let energy=f.thermal_micro_erg_cm3_s+f.binding_micro_erg_cm3_s+f.escape_erg_cm3_s-f.photo_input_erg_cm3_s-f.cmb_to_gas_erg_cm3_s;
   writeln!(p,"{i},{col},{e:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",x[0],x[1],x[2],x[3],f0[0]/(H0*r[1]),f0[1]/(H0*r[1]),f0[2]/(H0*r[1]),w/(H0*r[1]),charge,energy)?;Ok(())
  };
  eval(-1,0.)?;
  for j in 0..4{for e in eps{eval(j,e)?;if j==0||j==3||b[j as usize]>e*scale[j as usize]{eval(j,-e)?;}else{eval(j,2.*e)?;}}}
 }
 p.flush()?;
 for (grid,to) in [(0,points[1].a),(1,(points[0].a*points[1].a).sqrt())]{
  let du=(to/s.a).ln();
  let mut eval=|col:i32,e:f64|->Result<(),Box<dyn std::error::Error>>{
   let mut x=base;if col>=0{x[col as usize]+=e*scale[col as usize];}
   let mut init=s.clone();init.gas=gas(x)?;
   map(d.c4a_rebase_initial(&init))?;
   let init_before=q(&init)?;
   let mut rhs=0;let next=map(d.external_trial(&init,to,&mut rhs))?;
   let a=q(&next)?;let (pn,pu)=d.photon_inventory(&next);let (nr,ur)=map(d.residuals(&next))?;
   assert_eq!(next.accepted,1);assert_eq!(q(&init)?,init_before);assert!(next.last_error<d.config.local_target);
   writeln!(o,"{grid},{col},{e:.17e},{du:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{pn:.17e},{pu:.17e},{ur:.17e},{nr:.17e},{:.17e},{rhs}",x[0],x[1],x[2],x[3],a[0],a[1],a[2],a[3],next.last_error)?;
   Ok(())
  };
  eval(-1,0.)?;for j in 0..4{for e in eps{eval(j,e)?;if j==0||j==3{eval(j,-e)?;}else{eval(j,2.*e)?;}}}o.flush()?;
  eprintln!("native grid {grid} du={du:.17e} complete");
 }
 Ok(())
}

