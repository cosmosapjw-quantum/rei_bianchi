//! Independent-history throughput using the pinned integrator's existing bounded pool.
use rodas5p_integrators::ParallelExecution;
use serde_json::{json, Value};
use std::{fs::{self,File},path::PathBuf,process::Command,time::Instant};
fn main()->Result<(),Box<dyn std::error::Error>> {
 let args=std::env::args().collect::<Vec<_>>();
 if args.len()!=5 {return Err("usage: lrs_batch CASE_BINARY FRESH_OUTPUT WORKERS CPU_LIST".into());}
 let binary=PathBuf::from(&args[1]);let out=PathBuf::from(&args[2]);let width=args[3].parse::<usize>()?;
 if !(1..=4).contains(&width){return Err("workers must be 1..4".into());}
 let cpus=args[4].split(',').map(str::parse::<usize>).collect::<Result<Vec<_>,_>>()?;
 if cpus.len()<width || cpus.iter().collect::<std::collections::BTreeSet<_>>().len()!=cpus.len(){return Err("distinct CPU per slot required".into());}
 fs::create_dir(&out)?;
 let jobs=["fixed","birth","disabled"];let slots=(0..width).map(|i|(i,cpus[i],jobs.iter().enumerate().filter(|(j,_)|j%width==i).map(|(_,m)|m.to_string()).collect::<Vec<_>>())).collect::<Vec<_>>();
 let pool=ParallelExecution::rayon(width).map_err(|e|format!("{e:?}"))?;let start=Instant::now();
 let results=pool.map_ordered(&slots, |(slot,cpu,modes)| {
  let mut children=Vec::<Value>::new();
  for mode in modes {
   let dir=out.join(mode);let child_start=Instant::now();
   let result=(||->Result<Value,std::io::Error>{
    fs::create_dir(&dir)?;
    let mut argv=vec!["-k".into(),"2s".into(),"30s".into(),"/usr/bin/time".into(),"-f".into(),"%M".into(),"-o".into(),dir.join("peak_rss_kb.txt").display().to_string(),"taskset".into(),"-c".into(),cpu.to_string(),binary.display().to_string(),dir.join("raw.json").display().to_string(),mode.clone(),"radau".into(),"16".into(),"--native-eval".into(),"cell-cache".into()];
    if !std::path::Path::new("/usr/bin/time").is_file() {argv.drain(3..8);}
    fs::write(dir.join("inputs.json"),serde_json::to_vec_pretty(&json!({"command":"timeout","argv":argv,"cpu":cpu,"per_case_cap_s":30}))?)?;
    let status=Command::new("timeout").args(&argv).stdout(File::create(dir.join("stdout.txt"))?).stderr(File::create(dir.join("stderr.txt"))?).status()?;
    Ok(json!({"mode":mode,"exit_code":status.code(),"success":status.success(),"wall_s":child_start.elapsed().as_secs_f64(),"peak_rss_kb":fs::read_to_string(dir.join("peak_rss_kb.txt")).ok().and_then(|s|s.trim().parse::<u64>().ok())}))
   })();
   let report=match result {Ok(x)=>x,Err(e)=>json!({"mode":mode,"success":false,"io_error":e.to_string(),"wall_s":child_start.elapsed().as_secs_f64()})};
   let success=report["success"]==true;children.push(report);if !success {break;}
  }
  Ok(json!({"slot":slot,"cpu":cpu,"children":children}))
 }).map_err(|e|format!("{e:?}"))?;
 let success=results.iter().flat_map(|r|r["children"].as_array().unwrap()).all(|r|r["success"]==true);
 let report=json!({"workers":width,"backend":pool.backend(),"jobs":3,"max_useful_width":3,"wall_s":start.elapsed().as_secs_f64(),"success":success,"slots":results});
 fs::write(out.join("batch.json"),serde_json::to_vec_pretty(&report)?)?;
 println!("{}",report);
 if !success{return Err("one or more child histories failed".into());}Ok(())
}
