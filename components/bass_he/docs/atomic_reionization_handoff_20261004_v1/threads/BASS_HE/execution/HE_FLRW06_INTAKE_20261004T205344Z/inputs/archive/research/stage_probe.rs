// Bounded diagnostic of the existing published stage. No production mutation.
use std::io::{self, Read};
mod coupled_primary;
use coupled_primary::{PrimaryPacket, PrimaryState, PrimaryStage, primary_stage_step, try_primary_stage_step};
fn arr(v:&[f64])->String {format!("[{}]",v.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(","))}
fn mat(v:&[[f64;3]])->String {format!("[{}]",v.iter().map(|x|arr(x)).collect::<Vec<_>>().join(","))}
fn same(a:&PrimaryState,b:&PrimaryState)->bool {
 a.fractions==b.fractions && a.w_ev_per_h==b.w_ev_per_h && a.escape_ev_per_h==b.escape_ev_per_h && a.packets.len()==b.packets.len() && a.packets.iter().zip(&b.packets).all(|(x,y)| x.energy_ev==y.energy_ev && x.per_h==y.per_h)
}
fn stage_probe()->Result<(),String> {
 let mut text=String::new();io::stdin().read_to_string(&mut text).map_err(|e|e.to_string())?;
 let mut it=text.split_whitespace();
 let mut number=||it.next().ok_or("EOF".to_owned())?.parse::<f64>().map_err(|e|e.to_string());
 let nh=number()?;let fhe=number()?;let hubble=number()?;let dt=number()?;let temp=number()?;
 let f=[number()?,number()?,number()?];let count=number()? as usize;
 if count>256{return Err("node bound".to_owned());}
 let mut packets=Vec::new();for _ in 0..count {packets.push(PrimaryPacket{energy_ev:number()?,per_h:number()?});}
 if it.next().is_some(){return Err("extra input".to_owned());}
 let gas=HHeModel::controlled_fixture();
 let w=1.5*gas.kb_erg_k*temp*(1.0+fhe+f[0]+fhe*(f[1]+2.0*f[2]))/gas.ev_erg;
 let old=PrimaryState{fractions:f,w_ev_per_h:w,escape_ev_per_h:0.0,packets};
 let stage=PrimaryStage{n_h_cm3:nh,f_he:fhe,h_mean_per_s:hubble};
 let controls=StepControl{max_iterations:80,residual_tolerance:1e-14};
 for case in 0..4 {
  let mut input=old.clone();
  if case==1{input.packets.reverse();}
  if case==2{input.packets=input.packets.iter().flat_map(|p|[PrimaryPacket{energy_ev:p.energy_ev,per_h:p.per_h*0.5},PrimaryPacket{energy_ev:p.energy_ev,per_h:p.per_h*0.5}]).collect();}
  let use_dt=if case==3 {0.0} else {dt};
  let r=primary_stage_step(&stage,&input,use_dt,controls).map_err(|e|format!("case {case}: {e}"))?;
  let energies:Vec<_>=r.state.packets.iter().map(|p|p.energy_ev).collect();
  let out:Vec<_>=r.state.packets.iter().map(|p|p.per_h).collect();
  let prior:Vec<_>=input.packets.iter().map(|p|p.per_h).collect();
  println!("{{\"case\":{},\"dt\":{:.17e},\"initial_w\":{:.17e},\"fractions\":{},\"w\":{:.17e},\"escape\":{:.17e},\"energies\":{},\"old_photons\":{},\"photons\":{},\"photo_events\":{},\"ci\":{},\"rr\":{},\"dr\":{},\"work\":{:.17e},\"residual\":{:.17e},\"iterations\":{}}}",case,use_dt,w,arr(&r.state.fractions),r.state.w_ev_per_h,r.state.escape_ev_per_h,arr(&energies),arr(&prior),arr(&out),mat(&r.events.photo_per_h),arr(&r.events.collision_per_h),arr(&r.events.recombination_per_h),arr(&r.events.dr_per_h),r.events.thermal_work_ev_per_h,r.residual,r.iterations);
 }
 let mut state=old.clone();state.packets[0].per_h=-1.0;let before=state.clone();
 let result=try_primary_stage_step(&stage,&mut state,dt,controls);
 match result {Err(e)=>println!("{{\"case\":4,\"error\":\"{}\",\"unchanged\":{}}}",e.code(),same(&state,&before)),Ok(_)=>return Err("negative input accepted".to_owned())}
 Ok(())
}
fn main(){if let Err(e)=stage_probe(){eprintln!("{e}");std::process::exit(2);}}
