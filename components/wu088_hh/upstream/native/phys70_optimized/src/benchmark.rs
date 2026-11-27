//! Bounded NEW performance experiments on immutable saved PHYS69 states.
//! No special-function initialization or accepted certificate is recomputed.
use std::{hint::black_box,sync::Arc,time::Instant};
use rayon::prelude::*;
use rodas5p_core::{CoreError,CoreResult,InitialGuess,LinearMethod,LinearSolverConfig,WorkCounters};
use rodas5p_integrators::Rodas5pMfFastWorkspace;
use serde_json::{json,Value};
use wu088_hh_phys69_vigilode::HhModel;
use crate::{kernel::{HhKernel,Backend},block::FrozenJacobian,integrate::StructuredWorkspace};

pub fn linear_config()->LinearSolverConfig { LinearSolverConfig { method:LinearMethod::Gmres,rtol:1e-12,atol:1e-14,restart:40,maxiter:200,x0_strategy:InitialGuess::Zero,..Default::default() } }
fn relative_inf(a:&[f64],b:&[f64])->f64 {
    let mut e=0.0_f64; let mut m=0.0_f64;
    for (&a,&b) in a.iter().zip(b) {e=e.max((a-b).abs());m=m.max(a.abs().max(b.abs()));}
    if m==0.0 {e} else {e/m}
}
fn timed<F:FnMut(usize)->CoreResult<()>>(loops:usize,mut f:F)->CoreResult<f64> {
    let t=Instant::now(); for i in 0..loops { f(i)?; } Ok(t.elapsed().as_secs_f64())
}

pub fn microbench(y:&[f64],lmax:usize,nodes:usize)->CoreResult<Value> {
    let n=2*(4*(lmax+1)+1);
    if y.len()!=n {return Err(CoreError::Dimension("saved benchmark state shape".into()));}
    let legacy=Arc::new(HhModel::new(lmax,nodes)?);
    let mut scalar=HhKernel::new(lmax,nodes,Backend::Scalar)?;
    let mut simd=HhKernel::new(lmax,nodes,Backend::Simd)?;
    let mut old=vec![0.0;n]; let mut a=old.clone(); let mut b=old.clone();
    let v:Vec<f64>=(0..n).map(|i|((i*7%31) as f64-15.0)/30.0).collect();
    let mut jac=FrozenJacobian::new(lmax+1); simd.freeze(38.0,y,&mut jac)?;
    legacy.jvp(38.0,y,&v,&mut old)?; jac.apply(&v,&mut a)?;
    let jvp_error=relative_inf(&old,&a);
    if jvp_error>2e-13 {return Err(CoreError::InvalidInput(format!("frozen JVP changed: {jvp_error:e}")));}
    legacy.rhs(37.375,y,&mut old)?;scalar.rhs(37.375,y,&mut a)?;simd.rhs(37.375,y,&mut b)?;
    let rhs_bitwise=old.iter().zip(&a).zip(&b).all(|((&x,&a),&b)|x.to_bits()==a.to_bits() && x.to_bits()==b.to_bits());
    if !rhs_bitwise {return Err(CoreError::InvalidInput("ordered scalar/SIMD RHS lost bit parity".into()));}
    let mut samples=Vec::new();
    // Alternate ordering to avoid assigning all early/late samples to one implementation.
    for sample in 0..7 {
        let order=if sample%2==0 {[0,1,2]} else {[2,1,0]};
        let mut seconds=[0.0;3];
        for engine in order {
            seconds[engine]=timed(1000,|i| {
                let tau=37.0+(i%7) as f64*0.125;
                match engine {0=>legacy.rhs(tau,black_box(y),&mut old)?,1=>scalar.rhs(tau,black_box(y),&mut a)?,_=>simd.rhs(tau,black_box(y),&mut b)?};
                black_box(if engine==0 {&old} else if engine==1 {&a} else {&b});Ok(())
            })?;
        }
        let old_jvp=timed(5000,|_|{legacy.jvp(38.0,black_box(y),black_box(&v),&mut old)?;black_box(&old);Ok(())})?;
        let frozen_jvp=timed(5000,|_|{jac.apply(black_box(&v),&mut a)?;black_box(&a);Ok(())})?;
        samples.push(json!({"sample":sample,"rhs_calls_per_engine":1000,"legacy_rhs_seconds":seconds[0],"scalar_rhs_seconds":seconds[1],"simd_rhs_seconds":seconds[2],"jvp_calls_per_engine":5000,"legacy_jvp_seconds":old_jvp,"frozen_jvp_seconds":frozen_jvp}));
    }
    let problem=legacy.ode()?;let mut baseline=Rodas5pMfFastWorkspace::new(&problem,&linear_config())?;
    baseline.set_gmres_into(true);baseline.set_ls_workspace(true);
    let mut block=StructuredWorkspace::new(n)?;let mut work=WorkCounters::default();
    // One common original state at r=27.625, positive step stays inside collar.
    let t=37.375;let h=0.001;
    let err_old=baseline.attempt(&problem,t,y,h,true,None,3e-13,3e-11,&mut work)?;
    let err_new=block.attempt(&mut simd,t,y,h,true,3e-13,3e-11)?;
    let step_error=relative_inf(baseline.y_new(),block.y_new());
    let stage_errors:Vec<f64>=(0..8).map(|i|relative_inf(baseline.stage(i),block.stage(i))).collect();
    let scaled_stage_defect=(0..8).flat_map(|i|baseline.stage(i).iter().zip(block.stage(i)).zip(y)
        .map(|((&old,&new),&base)|(old-new).abs()/(3e-13+3e-11*base.abs()))).fold(0.0_f64,f64::max);
    // A relative error divided by the tiny cancelling embedded stage is not a
    // meaningful acceptance metric. Bind absolute differences to the ORIGINAL
    // state error weights instead; retain the raw relative numbers as telemetry.
    if step_error>2e-12 || scaled_stage_defect>0.005 {return Err(CoreError::InvalidInput("upstream raw-U stage parity".into()));}
    let mut step_samples=Vec::new();
    for sample in 0..5 {
        let order=if sample%2==0 {[0,1]} else {[1,0]};let mut seconds=[0.0;2];
        for engine in order {
            seconds[engine]=timed(12,|_|{
                if engine==0 {black_box(baseline.attempt(&problem,t,black_box(y),h,true,None,3e-13,3e-11,&mut work)?);}
                else {black_box(block.attempt(&mut simd,t,black_box(y),h,true,3e-13,3e-11)?);}
                Ok(())
            })?;
        }
        step_samples.push(json!({"sample":sample,"new_probe_attempts_per_engine":12,"legacy_seconds":seconds[0],"structured_simd_seconds":seconds[1]}));
    }
    // Independent frozen-state callback jobs, not dependent radial panels.
    let mut parallel=Vec::new();let mut expected:Option<Vec<Vec<f64>>>=None;
    for threads in [1,2,4] {
        let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().map_err(|e|CoreError::InvalidInput(e.to_string()))?;
        let mut jobs:Vec<_>=(0..8).map(|_|Ok((HhKernel::new(lmax,nodes,Backend::Simd)?,vec![0.0;n]))).collect::<CoreResult<_>>()?;
        let mut elapsed=Vec::new();
        for _ in 0..5 {
            let started=Instant::now();
            pool.install(||jobs.par_iter_mut().enumerate().try_for_each(|(job,(kernel,out))|->CoreResult<()>{
                for i in 0..500 {kernel.rhs(37.0+(i%7) as f64*0.1+job as f64*0.001,black_box(y),out)?;black_box(&*out);}
                Ok(())
            }))?;
            elapsed.push(started.elapsed().as_secs_f64());
        }
        let endpoints:Vec<Vec<f64>>=jobs.iter().map(|(_,out)|out.clone()).collect();
        let bitwise=expected.as_ref().is_none_or(|old|old.iter().flatten().zip(endpoints.iter().flatten()).all(|(a,b)|a.to_bits()==b.to_bits()));
        if !bitwise {return Err(CoreError::InvalidInput("Rayon independent job parity".into()));}
        if expected.is_none(){expected=Some(endpoints);}
        parallel.push(json!({"threads":threads,"jobs":8,"rhs_calls_per_job":500,"seconds":elapsed,"bitwise_equal":bitwise,"pool_setup_in_timer":false,"workspace_setup_in_timer":false}));
    }
    Ok(json!({"schema":"PHYS70_MICROBENCH_V1","status":"PASS_BOUNDED_NEW_PERFORMANCE_EXPERIMENT","lmax":lmax,"angular_nodes":nodes,"dimension":n,"input":"immutable PHYS69 final state; callback/step probes are not trajectories","legacy_rhs_scalar_simd_bitwise":rhs_bitwise,"frozen_jvp_relative_inf":jvp_error,"callback_samples":samples,"step_samples":step_samples,"common_step":{"tau":t,"h":h,"endpoint_relative_inf":step_error,"stage_relative_inf":stage_errors,"stage_difference_over_original_state_tolerance_max":scaled_stage_defect,"stage_tolerance_fraction_gate":0.005,"legacy_error_norm":err_old,"structured_error_norm":err_new},"memory":{"scope":"retained vector capacities; not total RSS or total allocator traffic","legacy_driver_report":baseline.krylov_workspace_bytes(),"structured_driver_and_frozen_bytes":block.workspace_bytes(),"structured_kernel_table_and_rows_bytes":simd.workspace_bytes()},"parallel_frozen_jobs":parallel,"old_scientific_integrations":0,"HH_R10":"OFF"}))
}
