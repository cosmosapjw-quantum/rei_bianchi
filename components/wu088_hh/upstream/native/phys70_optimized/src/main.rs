use std::{fs,io::Write,process::ExitCode,time::Instant};
use rayon::prelude::*;
use sha2::{Digest,Sha256};
use serde_json::{json,Value};
use wu088_hh_phys70_optimized::{*,kernel::Backend};
use num_complex::Complex64;

fn digest(bytes:&[u8])->String {format!("{:x}",Sha256::digest(bytes))}
fn execute(request:&Request,seed:&[(Complex64,Complex64)],request_sha:&str,seed_sha:&str,source_sha:&str)->Result<Value,Box<dyn std::error::Error>> {
    request.validate()?;
    let n=request.physics_request.lmax+1;
    let started=Instant::now();
    let (complete,times,states,attempts,accepted,rejected,reuses,counters,more,message)=match request.engine {
        Engine::LegacyGmres=>{
            let result=wu088_hh_phys69_vigilode::solve(&request.physics_request,seed)?;
            let complete=result.observed.success&&result.observed.t==[0.0,T-B]&&result.observed.y.len()==2;
            (complete,result.observed.t,result.observed.y,result.attempts,result.accepted_steps,result.rejected_steps,result.state_reuses,serde_json::to_value(result.observed.counters)?,json!({"driver":result.driver,"structured_shifted_solves":0,"uniform_numerical_certificate":false}),result.observed.message)
        },
        Engine::BlockScalar|Engine::BlockSimd=>{
            let backend=if request.engine==Engine::BlockScalar {Backend::Scalar} else {Backend::Simd};
            let r=integrate::solve_structured(&request.physics_request,seed,backend)?;
            let more=json!({"driver":"PHYS70_ORIGINAL_HH_STRUCTURED_RAW_U","structured_shifted_solves":r.shifted_solves,"max_shifted_backward_residual_observed":r.max_shifted_residual,"min_shifted_denominator_observed":r.min_shifted_denominator,"retained_workspace_bytes":r.workspace_bytes,"uniform_numerical_certificate":false});
            (r.complete,vec![0.0,r.t],vec![r.y0,r.y],r.attempts,r.accepted_steps,r.rejected_steps,r.state_reuses,json!({"kernel":r.kernel_counts,"jvp_calls":r.shifted_solves,"jvp_role":"full shifted residual checks using frozen coefficients","assembled_jacobians":0,"direct_factorizations":0,"structured_shifted_solves":r.shifted_solves}),more,r.message)
        }
    };
    let elapsed=started.elapsed().as_secs_f64();
    let complete=complete&&times==[0.0,T-B]&&states.len()==2&&states.iter().all(|y|y.len()==2*(4*n+1)&&y.iter().all(|x|x.is_finite()));
    let endpoint=if complete {let y=&states[1];let d2=get(y,4*n)/D2_SCALE;let d1a=get(y,2*n+TARGET_B)/Q_SCALE;let d1b=get(y,3*n+TARGET_A)/Q_SCALE;
        Some(json!({"d2":{"real":d2.re,"imag":d2.im},"d1_q21_20":{"real":d1a.re,"imag":d1a.im},"d1_q20_21":{"real":d1b.re,"imag":d1b.im},"normalization_drift_max_abs_F_B_minus_1":(0..n).map(|j|(get(y,j)-1.0).norm()).fold(0.0_f64,f64::max)}))} else {None};
    Ok(json!({"schema":"PHYS70_OPTIMIZED_RESULT_V1","status":if complete {"COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE"} else {"PARTIAL_INTEGRATION"},"complete":complete,"request":request,"request_sha256":request_sha,"seed_sha256":seed_sha,"source_sha256":source_sha,"upstream_commit":UPSTREAM_COMMIT,"engine":request.engine,"B":B,"T":T,"k":K,"eta_C":"-10/7","m":0,"target":[21,20],"clock":"tau=65-r;0..38","q_scale":"2^80","d2_scale":"2^160","endpoint":endpoint,"observed_times_tau":times,"observed_states_scaled":states,"attempts":attempts,"accepted_steps":accepted,"rejected_steps":rejected,"state_reuses":reuses,"counters":counters,"implementation":more,"message":message,"integration_elapsed_seconds":elapsed,"build_features":{"sse2":cfg!(target_feature="sse2"),"avx":cfg!(target_feature="avx"),"avx2":cfg!(target_feature="avx2"),"fma":cfg!(target_feature="fma"),"wide":"1.7.1","rayon":"1.12.0"},"dense_interpolation_used":false,"HH_R10":"OFF","scientific_scope":"finite-L original external second Born; binary64 diagnostic, no original source-driven xi or global integration enclosure"}))
}
fn main_run()->Result<bool,Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args==["--help"] {
        println!("wu088-hh-phys70-optimized run REQUEST_JSON SEED_TEXT FROZEN_NPZ\nwu088-hh-phys70-optimized micro SAVED_PHYS69_RESULT FROZEN_NPZ\nwu088-hh-phys70-optimized batch REQUEST_LIST_JSON SEED_TEXT FROZEN_NPZ THREADS\nOriginal B27,T65,k7/10,m0,target21/20. New performance probes do not rerun interval certificates. HH_R10=OFF.");return Ok(true);
    }
    let value=match args.first().map(String::as_str) {
        Some("run") if args.len()==4=>{
            let bytes=fs::read(&args[1])?;let request:Request=serde_json::from_slice(&bytes)?;request.validate()?;
            let source_sha=digest(&fs::read(&args[3])?);if source_sha!=FROZEN_SOURCE_SHA256{return Err("original source hash mismatch".into());}
            let seed_bytes=fs::read(&args[2])?;let seed=parse_seed(std::str::from_utf8(&seed_bytes)?,request.physics_request.lmax)?;
            execute(&request,&seed,&digest(&bytes),&digest(&seed_bytes),&source_sha)?
        },
        Some("micro") if args.len()==3=>{
            let source_sha=digest(&fs::read(&args[2])?);if source_sha!=FROZEN_SOURCE_SHA256{return Err("original source hash mismatch".into());}
            let bytes=fs::read(&args[1])?;let old:Value=serde_json::from_slice(&bytes)?;
            if old["schema"]!="PHYS69_VIGILODE_RESULT_V1"||old["complete"]!=true||old["source_sha256"]!=FROZEN_SOURCE_SHA256||old["upstream_commit"]!=UPSTREAM_COMMIT||old["HH_R10"]!="OFF" {return Err("immutable source result identity".into());}
            let req:PhysicsRequest=serde_json::from_value(old["request"].clone())?;req.validate()?;
            let states:Vec<Vec<f64>>=serde_json::from_value(old["observed_states_scaled"].clone())?;
            if states.len()!=2||old["observed_times_tau"]!=json!([0.0,38.0]){return Err("saved endpoint incomplete".into());}
            let mut result=benchmark::microbench(&states[1],req.lmax,req.angular_nodes)?;
            result["saved_input_sha256"]=json!(digest(&bytes));result["source_sha256"]=json!(source_sha);result
        },
        Some("batch") if args.len()==5=>{
            let bytes=fs::read(&args[1])?;let requests:Vec<Request>=serde_json::from_slice(&bytes)?;
            let threads:usize=args[4].parse()?;if requests.is_empty()||requests.len()>16||!(1..=8).contains(&threads){return Err("batch needs 1..16 independent requests and 1..8 threads".into());}
            let source_sha=digest(&fs::read(&args[3])?);if source_sha!=FROZEN_SOURCE_SHA256{return Err("original source hash mismatch".into());}
            let seed_bytes=fs::read(&args[2])?;let seed_sha=digest(&seed_bytes);let seed_text=std::str::from_utf8(&seed_bytes)?;
            let mut seeds=Vec::new();for r in &requests{r.validate()?;seeds.push(parse_seed(seed_text,r.physics_request.lmax)?);}
            let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build()?;let start=Instant::now();
            let results:Vec<Result<Value,String>>=pool.install(||requests.par_iter().zip(&seeds).map(|(r,seed)|{
                let request_sha=digest(&serde_json::to_vec(r).unwrap());execute(r,seed,&request_sha,&seed_sha,&source_sha).map_err(|e|e.to_string())
            }).collect());
            let success=results.iter().all(|r|r.as_ref().is_ok_and(|v|v["complete"]==true));
            let results:Vec<Value>=results.into_iter().map(|r|r.unwrap_or_else(|e|json!({"complete":false,"status":"ERROR","error":e}))).collect();
            json!({"schema":"PHYS70_INDEPENDENT_BATCH_V1","complete":success,"threads":threads,"requests":requests.len(),"request_list_sha256":digest(&bytes),"per_request_digest":"serde_json canonical serialization of parsed request","results":results,"wall_seconds":start.elapsed().as_secs_f64(),"ordered_results":true,"parallel_radial_carry":false,"HH_R10":"OFF"})
        },_=>return Err("usage: see --help".into())
    };
    let success=value.get("complete").map_or(value["status"]=="PASS_BOUNDED_NEW_PERFORMANCE_EXPERIMENT",|v|v==true);
    let mut stdout=std::io::stdout().lock();serde_json::to_writer_pretty(&mut stdout,&value)?;stdout.write_all(b"\n")?;Ok(success)
}
fn main()->ExitCode {match main_run(){Ok(true)=>ExitCode::SUCCESS,Ok(false)=>ExitCode::FAILURE,Err(e)=>{eprintln!("{}",json!({"status":"ERROR","error":e.to_string(),"HH_R10":"OFF"}));ExitCode::FAILURE}}}
