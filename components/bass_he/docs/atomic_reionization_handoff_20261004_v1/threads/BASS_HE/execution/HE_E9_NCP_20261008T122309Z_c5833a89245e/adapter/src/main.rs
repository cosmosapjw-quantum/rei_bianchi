use std::{fs::{self,OpenOptions},io::Write,path::Path};
use short_hhe_control::{coupled,material,radiation,output};
fn run()->Result<(),String>{
 let a:Vec<String>=std::env::args().collect();
 if a.len()!=3{return Err("config NEW_OUTPUT (OFF N384 first two steps only)".into())}
 let c=rei_microphysics::igm_config::parse_config(&fs::read_to_string(&a[1]).map_err(|e|e.to_string())?).map_err(|e|format!("{e:?}"))?;
 let out=Path::new(&a[2]);fs::create_dir(out).map_err(|e|e.to_string())?;
 let open=|name:&str|OpenOptions::new().write(true).create_new(true).open(out.join(name)).map_err(|e|e.to_string());
 let mut original=open("OWNER_ORIGINAL_OFF.csv")?;let mut side=open("OWNER_STATE_SIDECAR.csv")?;let mut trace=open("STEPS.csv")?;
 writeln!(original,"{}",output::HEADER).map_err(|e|e.to_string())?;
 writeln!(side,"step,s,x,y,z,w").map_err(|e|e.to_string())?;
 writeln!(trace,"step,iterations,scaled_nonlinear_residual,number_allowance_ratio,energy_allowance_ratio").map_err(|e|e.to_string())?;
 let grid=radiation::Grid::new(&c,512,4)?;if grid.nodes.len()>4096{return Err("ACTIVE_CAP".into())}
 let mut s=coupled::State::new(&c,&grid)?;let p=c.background.at_ln_a(c.start).map_err(|e|format!("{e:?}"))?;
 let initial=s.y[3]+material::binding(s.y,p.n_he_cm3/p.n_h_cm3);
 for k in 0..=2 {
  if k>0{s=coupled::advance(&c,&grid,&s,he_e9_owner_prefix::clock(&c,k)?,initial)?;}
  let before=s.clone();let row=output::row(&c,&grid,&s,initial)?;if s!=before{return Err("READOUT_MUTATED_STATE".into())}
  output::write_row(&mut original,&row)?;
  writeln!(side,"{k},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",s.s,s.y[0],s.y[1],s.y[2],s.y[3]).map_err(|e|e.to_string())?;
  writeln!(trace,"{k},{},{:.17e},{:.17e},{:.17e}",s.iterations,s.norm,s.n_ratio,s.e_ratio).map_err(|e|e.to_string())?;
  for f in [&mut original,&mut side,&mut trace]{f.flush().map_err(|e|e.to_string())?;f.sync_all().map_err(|e|e.to_string())?;}
  eprintln!("ACCEPTED mode=OFF N=384 step={k} nodes={} norm={} Nratio={} Eratio={}",grid.nodes.len(),s.norm,s.n_ratio,s.e_ratio);
 }
 let mut checkpoint=open("CHECKPOINT_NONRESUMABLE.txt")?;writeln!(checkpoint,"{:?}",s).map_err(|e|e.to_string())?;checkpoint.sync_all().map_err(|e|e.to_string())?;
 let mut ready=open("READY.json")?;writeln!(ready,"{{\"mode\":\"OFF\",\"N\":384,\"accepted_steps\":2,\"rows\":3,\"owner_adopted\":false,\"checkpoint_resumable\":false}}").map_err(|e|e.to_string())?;ready.sync_all().map_err(|e|e.to_string())?;
 Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("OWNER_PREFIX_FAIL {e}");std::process::exit(2)}}
