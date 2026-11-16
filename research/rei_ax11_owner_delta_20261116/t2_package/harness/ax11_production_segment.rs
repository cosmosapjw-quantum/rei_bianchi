//! Finite T2 ZERO/PLUS segment using the source-verified original Driver API.
//! The external launcher verifies source/binary/config/checkpoint hashes before
//! every execution. No full-state trace, per-comparison component log or retry.
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use rei_microphysics::ForwardError;
use std::{env, fs, io::{BufWriter, Write}, path::{Path, PathBuf}, time::Instant};

type R<T> = Result<T, ForwardError>;
const MAX_ACCEPTED: usize = 4_000_000;
const MAX_TRIALS: usize = 12_500_000;
const MAX_RHS: usize = 100_000_000;
const MAX_CASE_WALL_S: f64 = 39000.0;
const MAX_SEGMENT_ACCEPTED: usize = 250_000;
const OUTPUT_MIB: usize = 2048;
fn fail(code: &'static str) -> ForwardError { ForwardError::InvalidInput(code) }
fn io(_: std::io::Error) -> ForwardError { fail("AX11_T2_IO") }

struct Args {
    config: PathBuf, checkpoint: Option<PathBuf>, out: PathBuf,
    case: String, accepted: usize, fresh_wall_s: f64,
}
impl Args {
    fn parse() -> R<Self> {
        let v:Vec<String>=env::args().collect();
        if !(6..=7).contains(&v.len()) {return Err(fail("AX11_T2_USAGE"));}
        let accepted=v[5].parse::<usize>().map_err(|_|fail("AX11_T2_ACCEPTED_CAP"))?;
        let wall=if v.len()==7 {v[6].parse::<f64>().map_err(|_|fail("AX11_T2_WALL_CAP"))?}else{MAX_CASE_WALL_S};
        if !(1..=MAX_SEGMENT_ACCEPTED).contains(&accepted) || !wall.is_finite() || wall<=0.0 || wall>MAX_CASE_WALL_S
            || !["ZERO","PLUS"].contains(&v[4].as_str()) {return Err(fail("AX11_T2_ARGUMENT_DOMAIN"));}
        Ok(Self {config:v[1].clone().into(),checkpoint:if v[2]=="IC"{None}else{Some(v[2].clone().into())},
            out:v[3].clone().into(),case:v[4].clone(),accepted,fresh_wall_s:wall})
    }
}

#[derive(Clone,Copy)]
struct Counts { accepted:usize,trials:usize,comparisons:usize,rejects:usize,consecutive:usize,rhs:usize }
impl Counts {
    fn of(s:&DriverState)->Self {Self {accepted:s.accepted,trials:s.attempts,comparisons:s.comparisons,rejects:s.rejects,consecutive:s.consecutive_rejects,rhs:s.rhs_evaluations}}
    fn json(self)->String {format!("{{\"accepted\":{},\"trials\":{},\"comparisons\":{},\"rejects\":{},\"consecutive_rejects\":{},\"rhs_evaluations\":{}}}",self.accepted,self.trials,self.comparisons,self.rejects,self.consecutive,self.rhs)}
    fn deltas(self,old:Self)->String {format!("{{\"accepted\":{},\"trials\":{},\"comparisons\":{},\"rejects\":{},\"rhs_evaluations\":{}}}",self.accepted-old.accepted,self.trials-old.trials,self.comparisons-old.comparisons,self.rejects-old.rejects,self.rhs-old.rhs)}
}

fn config_text(c:&DriverConfig)->String {
    format!(concat!("q_ref={:.17e}\nsame_h={}\nend_zbar={:.17e}\nescape_fraction={:.17e}\n",
        "initial_temperature_k={:.17e}\nenergy_subdivisions={}\nn_mu={}\nbackground_panels={}\n",
        "local_target={:.17e}\ninitial_dln_a={:.17e}\nmax_steps={}\nmax_attempts={}\nmax_rhs={}\n",
        "max_wall_s={:.17e}\nspectra_every_accepted={}\noutput_budget_mib={}\n"),
        c.q_ref,c.same_h,c.end_zbar,c.escape_fraction,c.initial_temperature_k,c.energy_subdivisions,c.n_mu,c.background_panels,
        c.local_target,c.initial_dln_a,c.max_steps,c.max_attempts,c.max_rhs,c.max_wall_s,c.spectra_every_accepted,c.output_budget_mib)
}

fn open_table(p:&Path,header:&str)->R<BufWriter<fs::File>> {
    let mut w=BufWriter::new(fs::OpenOptions::new().create_new(true).write(true).open(p).map_err(io)?);
    writeln!(w,"{header}").map_err(io)?;Ok(w)
}
struct Tables {h:BufWriter<fs::File>,a:BufWriter<fs::File>,p:BufWriter<fs::File>,l:BufWriter<fs::File>,fb:BufWriter<fs::File>,rejects:BufWriter<fs::File>}
impl Tables {
    fn new(out:&Path)->R<Self> {Ok(Self {
        h:open_table(&out.join("history.csv"),"case_id,q_ref,Sigma,time_s,a,zbar,b,H_per_s,s_per_s,x_HII,x_HeII,x_HeIII,nH_proper_cm3,ne_proper_cm3,temperature_K,Gamma_HI_per_s,Gamma_HeI_per_s,Gamma_HeII_per_s,photon_n_per_H,photon_u_eV_per_H,J0_photon_u_eV_per_H,J1_photon_u_eV_per_H,J2_photon_u_eV_per_H,x_HI,x_HeI")?,
        a:open_table(&out.join("abundances.csv"),"run_id,time_s,zbar,Tgas_K,background_Tref_K,species_id,A,Z,charge,nproper,element_fraction,Ybaryon,electron_xe,normalization_registry")?,
        p:open_table(&out.join("spectra.csv"),"case_id,q_ref,Sigma,time_s,a,zbar,energy_low_eV,energy_high_eV,mu_center,solid_angle_weight_sr,photon_n_per_H,photon_u_eV_per_H")?,
        l:open_table(&out.join("ledgers.csv"),"case_id,time_s,ledger_name,residual,tolerance,status")?,
        fb:open_table(&out.join("feedback.csv"),"case_id,time_s,a,H_per_s,effective_radiation_DeltaP_J_m3,ionizing_DeltaP_J_m3,effective_radiation_signed_deltaepsilon_J_m3,extra_energy_J_m3,extra_energy_ratio,total_DeltaP_J_m3")?,
        rejects:open_table(&out.join("raw/rejections.csv"),"attempt,a,dln_a,error")?,
    })}
    fn batch(&mut self,d:&Driver,s:&DriverState,case:&str,out:&Path,spectrum:bool)->R<()> {
        d.output_batch(s,case,out,spectrum,&mut self.h,&mut self.a,&mut self.p,&mut self.l,&mut self.fb)
    }
    fn flush(&mut self)->R<()> {for w in [&mut self.h,&mut self.a,&mut self.p,&mut self.l,&mut self.fb,&mut self.rejects] {w.flush().map_err(io)?;}Ok(())}
}

fn atomic_text(p:&Path,text:&str)->R<()> {
    let tmp=p.with_extension("tmp");
    fs::write(&tmp,text).map_err(io)?;fs::rename(tmp,p).map_err(io)
}

// One constant-count, bounded-size receipt at existing checkpoint cadence. No
// every-step diagnostic allocation or I/O. The original recursive guard also
// sees these auxiliary files; its accounting is deliberately not weakened.
fn progress(out:&Path,d:&Driver,s:&DriverState,case:&str,status:&str,error:&str,checkpoint_saved:bool)->R<()> {
    let time=d.background.point_at_scale(s.a)?.time_s;
    let text=format!(concat!("{{\"schema\":\"AX11_T2_PROGRESS_V1\",\"case\":\"{}\",\"status\":\"{}\",\"error\":\"{}\",",
        "\"checkpoint_saved\":{},\"a\":{:.17e},\"proper_time_s\":{:.17e},\"counts\":{},\"cumulative_wall_s\":{:.17e},",
        "\"next_dln_a\":{:.17e},\"last_error\":{:.17e},\"max_newton_residual\":{:.17e},\"scientific_admission\":\"NOT_ISSUED\"}}\n"),
        case,status,error,checkpoint_saved,s.a,time,Counts::of(s).json(),s.wall_elapsed_s,s.next_dln_a,s.last_error,s.max_newton_residual);
    if text.len()>8192 {return Err(fail("AX11_T2_RECEIPT_SIZE"));}
    atomic_text(&out.join("progress.json"),&text)
}

// Same original cadence resource checks: recursive scientific byte enforcement
// remains inside every output batch and checkpoint save. The launcher owns the
// stricter aggregate two-case CPU/disk/segment policy.
fn resources(out:&Path)->R<()> {
    let mut bytes=0_u64;
    for e in fs::read_dir(out).map_err(io)? {let e=e.map_err(io)?;if e.path().is_file(){bytes=bytes.checked_add(e.metadata().map_err(io)?.len()).ok_or(fail("AXBI_OUTPUT_CAP"))?;}}
    if bytes>OUTPUT_MIB as u64*1024*1024 {return Err(fail("AXBI_OUTPUT_CAP"));}
    if let Ok(status)=fs::read_to_string("/proc/self/status") {
        if status.lines().find(|x|x.starts_with("VmHWM:")).and_then(|x|x.split_whitespace().nth(1)).and_then(|x|x.parse::<u64>().ok()).is_some_and(|x|x>2*1024*1024){return Err(fail("AXBI_RSS_CAP"));}
    }
    Ok(())
}

#[derive(Clone,Copy)]
enum Stop {Endpoint,SegmentAccepted,SegmentWall,CaseAccepted,CaseTrials,CaseRhs,CaseWall}
impl Stop {
    fn status(self)->&'static str {match self {
        Self::Endpoint=>"SCIENTIFIC_ENDPOINT_ZBAR4",Self::SegmentAccepted=>"SEGMENT_ACCEPTED_BOUNDARY",Self::SegmentWall=>"SEGMENT_WALL_BOUNDARY",
        Self::CaseAccepted=>"CASE_ACCEPTED_CAP",Self::CaseTrials=>"CASE_TRIAL_CAP",Self::CaseRhs=>"CASE_RHS_CAP",Self::CaseWall=>"CASE_WALL_CAP",
    }}
    fn exit(self)->i32 {match self {Self::Endpoint=>0,Self::SegmentAccepted|Self::SegmentWall=>10,_=>11}}
}

fn run(a:Args)->R<i32> {
    let process_started=Instant::now();
    let input_config=fs::read_to_string(&a.config).map_err(io)?;
    let mut cfg=DriverConfig::read(&input_config)?;
    let baseline=DriverConfig::baseline();
    let q=if a.case=="ZERO"{0.0_f64}else{0.01_f64};
    // The outer source/config pin is primary. This small executable scope guard
    // catches an accidental baseline, FESC/Tgas or dE/dmu run in this T2 wave.
    if cfg.q_ref.to_bits()!=q.to_bits() || cfg.same_h || cfg.end_zbar.to_bits()!=4.0_f64.to_bits()
        || cfg.local_target.to_bits()!=6.25e-7_f64.to_bits() || cfg.initial_dln_a.to_bits()!=1e-10_f64.to_bits()
        || cfg.escape_fraction.to_bits()!=baseline.escape_fraction.to_bits()
        || cfg.initial_temperature_k.to_bits()!=baseline.initial_temperature_k.to_bits()
        || cfg.energy_subdivisions!=baseline.energy_subdivisions || cfg.n_mu!=baseline.n_mu
        || cfg.background_panels!=baseline.background_panels || cfg.spectra_every_accepted!=60
    {return Err(fail("AX11_T2_PHYSICAL_CONFIG_MISMATCH"));}
    // Honor the launcher's allocated cumulative caps after preparation/preflight
    // debits. The constants are absolute ceilings, never replacement allocations.
    if cfg.max_steps==0 || cfg.max_steps>MAX_ACCEPTED || cfg.max_attempts==0 || cfg.max_attempts>MAX_TRIALS
        || cfg.max_rhs==0 || cfg.max_rhs>MAX_RHS || !cfg.max_wall_s.is_finite() || cfg.max_wall_s<=0.0 || cfg.max_wall_s>MAX_CASE_WALL_S
    {return Err(fail("AX11_T2_ALLOCATED_CAP_DOMAIN"));}
    // Native counters/clock stay cumulative. Only output allocation is fixed.
    cfg.output_budget_mib=OUTPUT_MIB;
    let effective=config_text(&cfg);
    let (driver,mut state)=Driver::new(cfg)?;
    if let Some(path)=&a.checkpoint {state=driver.read_checkpoint(path)?;}
    if state.accepted>driver.config.max_steps || state.attempts>driver.config.max_attempts || state.rhs_evaluations>driver.config.max_rhs
        || state.wall_elapsed_s>driver.config.max_wall_s {return Err(fail("AX11_T2_INPUT_EXCEEDS_CASE_CAP"));}
    let start=state.clone();
    let old=Counts::of(&state);
    let prior_wall=state.wall_elapsed_s;
    let target=state.accepted.checked_add(a.accepted).ok_or(fail("AX11_T2_COUNT_OVERFLOW"))?.min(driver.config.max_steps);
    let end=1.0/(1.0+driver.config.end_zbar);
    let start_time=driver.background.point_at_scale(state.a)?.time_s;
    fs::create_dir(&a.out).map_err(io)?;
    fs::create_dir(a.out.join("raw")).map_err(io)?;
    fs::create_dir(a.out.join("checkpoints")).map_err(io)?;
    fs::write(a.out.join("config.cfg"),input_config).map_err(io)?;
    fs::write(a.out.join("effective_resource_config.cfg"),&effective).map_err(io)?;
    fs::write(a.out.join("source_identity.start.txt"),compiled_identity()).map_err(io)?;
    fs::write(a.out.join("source_identity.txt"),compiled_identity()).map_err(io)?;
    fs::write(a.out.join("case_id.txt"),&a.case).map_err(io)?;
    if let Some(path)=&a.checkpoint {fs::copy(path,a.out.join("input_checkpoint.txt")).map_err(io)?;}
    fs::write(a.out.join("metadata.txt"),concat!(
        "scenario=PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1\nwave=AX11_T2_ZERO_PLUS\n",
        "clock=elapsed proper seconds since zbar20\nframe=non-tilted normal tetrad\n",
        "method=binary64 BE split step-doubling empirical\nlocal_target=6.25e-7\ninitial_dln_a=1e-10\n",
        "spectra_cadence=initial; every60 cumulative accepted; each30wallsecondcheckpoint; terminal; fullgrid noaveraging\n",
        "checkpoint_retention=all existing-cadence checkpoints retained\n",
        "diagnostics=no full-state trace or per-comparison component log\n",
        "timing_scopes=inclusive nested; do not sum\n",
        "preflight=external source/binary/config/checkpoint hash verification required\n",
        "scientific_admission=NOT_ISSUED\n")).map_err(io)?;
    let mut t=Tables::new(&a.out)?;
    t.batch(&driver,&state,&a.case,&a.out,true)?;t.flush()?;
    driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.start.txt"),&state)?;
    driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.txt"),&state)?;
    progress(&a.out,&driver,&state,&a.case,"STARTED","NONE",true)?;
    println!("AX11_T2_START case={} accepted={} trials={} rhs={} a={:.17e} prior_wall_s={:.6} requested_delta={}",a.case,state.accepted,state.attempts,state.rhs_evaluations,state.a,prior_wall,a.accepted);
    let setup_wall_s=process_started.elapsed().as_secs_f64();
    let started=Instant::now();
    let mut last_save=Instant::now();
    let mut last_spectrum_time=Some(start_time);
    let mut max_accepted_metric:Option<f64>=None;
    let outcome=(||->R<Stop>{
        loop {
            state.wall_elapsed_s=prior_wall+started.elapsed().as_secs_f64();
            if state.a==end {return Ok(Stop::Endpoint);}
            if state.accepted>=driver.config.max_steps {return Ok(Stop::CaseAccepted);}
            if state.attempts>=driver.config.max_attempts {return Ok(Stop::CaseTrials);}
            if state.rhs_evaluations>=driver.config.max_rhs {return Ok(Stop::CaseRhs);}
            if state.wall_elapsed_s>=driver.config.max_wall_s {return Ok(Stop::CaseWall);}
            if state.accepted>=target {return Ok(Stop::SegmentAccepted);}
            if started.elapsed().as_secs_f64()>=a.fresh_wall_s {return Ok(Stop::SegmentWall);}
            if state.consecutive_rejects>=30 || state.next_dln_a<1e-10 {return Err(fail("AXBI_REJECT_CAP"));}
            // Original rollback state only: one photon vector, never a history.
            let previous=state.clone();
            let accepted=match driver.adaptive_step(&mut state) {
                Ok(v)=>v,
                Err(e)=>{
                    writeln!(t.rejects,"{},{},{},{e:?}",state.attempts,state.a,state.next_dln_a).map_err(io)?;
                    t.rejects.flush().map_err(io)?;
                    if e.code()=="AXBI_TENTATIVE_CAP" || (e.code()=="AXBI_STEP_CAP" && state.attempts>=driver.config.max_attempts) {return Ok(Stop::CaseTrials);}
                    if state.rhs_evaluations>=driver.config.max_rhs {return Ok(Stop::CaseRhs);}
                    if state.consecutive_rejects>=30 || state.next_dln_a<1e-10 {return Err(e);}
                    false
                }
            };
            if !accepted {
                writeln!(t.rejects,"{},{},{},local_metric={}",state.attempts,state.a,state.next_dln_a,state.last_error).map_err(io)?;
                if state.consecutive_rejects>=30 || state.next_dln_a<1e-10 {return Err(fail("AXBI_REJECT_CAP"));}
                continue;
            }
            let terminal=state.a==end || state.accepted>=target || state.accepted>=driver.config.max_steps
                || state.attempts>=driver.config.max_attempts || state.rhs_evaluations>=driver.config.max_rhs
                || prior_wall+started.elapsed().as_secs_f64()>=driver.config.max_wall_s || started.elapsed().as_secs_f64()>=a.fresh_wall_s;
            let checkpoint_due=driver.spectrum_due(state.accepted,last_save.elapsed().as_secs_f64(),terminal);
            if let Err(e)=t.batch(&driver,&state,&a.case,&a.out,checkpoint_due) {
                let paid=Counts::of(&state);let wall=state.wall_elapsed_s;
                state=previous;
                state.attempts=paid.trials;state.comparisons=paid.comparisons;state.rhs_evaluations=paid.rhs;state.rejects=paid.rejects;state.wall_elapsed_s=wall;
                return Err(e);
            }
            max_accepted_metric=Some(max_accepted_metric.map_or(state.last_error,|x|x.max(state.last_error)));
            if checkpoint_due {
                last_spectrum_time=Some(driver.background.point_at_scale(state.a)?.time_s);
                t.flush()?;
                state.wall_elapsed_s=prior_wall+started.elapsed().as_secs_f64();
                driver.save_checkpoint_budget(&a.out,&a.out.join(format!("checkpoints/{:08}.txt",state.accepted)),&state)?;
                driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.txt"),&state)?;
                resources(&a.out)?;
                progress(&a.out,&driver,&state,&a.case,"RUNNING_CHECKPOINTED","NONE",true)?;
                last_save=Instant::now();
            }
        }
    })();
    let fresh_evolution_wall_s=started.elapsed().as_secs_f64();
    state.wall_elapsed_s=prior_wall+fresh_evolution_wall_s;
    let mut final_error:Option<ForwardError>=None;
    macro_rules! persist {($e:expr)=>{if let Err(e)=$e {if final_error.is_none(){final_error=Some(e);}}};}
    persist!(t.flush());
    persist!(driver.ensure_spectrum_snapshot(&state,&a.case,&a.out,&mut last_spectrum_time,&mut t.p));
    persist!(t.p.flush().map_err(io));
    let mut checkpoint_saved=false;
    match driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.txt"),&state) {
        Ok(())=>checkpoint_saved=true,Err(e)=>{if final_error.is_none(){final_error=Some(e);}}
    }
    persist!(driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.end.txt"),&state));
    persist!(fs::write(a.out.join("source_identity.end.txt"),compiled_identity()).map_err(io));
    #[cfg(ax11_profile)] {
        persist!(fs::write(a.out.join("raw/driver_timing.csv"),driver.profile_snapshot()).map_err(io));
        persist!(fs::write(a.out.join("raw/background_timing.csv"),driver.background.profile_snapshot()).map_err(io));
    }
    let status=match &outcome {Ok(s)=>s.status(),Err(_)=>"REAL_FAILURE_CHECKPOINTED"};
    let outcome_error=outcome.as_ref().err().map_or("NONE",ForwardError::code);
    let final_code=final_error.as_ref().map_or("NONE",ForwardError::code);
    let exit_code=if outcome.is_err() || final_error.is_some(){2}else{outcome.as_ref().unwrap().exit()};
    let end_time=driver.background.point_at_scale(state.a)?.time_s;
    let metric=max_accepted_metric.map_or_else(||"null".into(),|x|format!("{x:.17e}"));
    let counts=Counts::of(&state);
    let summary=format!(concat!("{{\n\"schema\":\"AX11_T2_SEGMENT_V1\",\n\"case\":\"{}\",\n\"status\":\"{}\",\n",
        "\"error\":\"{}\",\n\"finalization_error\":\"{}\",\n\"exit_code\":{},\n\"checkpoint_saved\":{},\n",
        "\"start_counts\":{},\n\"end_counts\":{},\n\"delta_counts\":{},\n",
        "\"a_start\":{:.17e},\n\"a_end\":{:.17e},\n\"proper_time_start_s\":{:.17e},\n\"proper_time_end_s\":{:.17e},\n",
        "\"proper_time_delta_s\":{:.17e},\n\"prior_wall_s\":{:.17e},\n\"fresh_evolution_wall_s\":{:.17e},\n\"cumulative_wall_s\":{:.17e},\n",
        "\"setup_wall_s\":{:.17e},\n\"process_wall_s_at_summary\":{:.17e},\n\"accepted_increment_requested\":{},\n\"segment_fresh_wall_cap_s\":{:.17e},\n",
        "\"case_caps\":{{\"accepted\":{},\"trials\":{},\"rhs\":{},\"wall_s\":{:.17e}}},\n\"output_budget_mib\":2048,\n",
        "\"next_dln_a\":{:.17e},\n\"last_error\":{:.17e},\n\"max_newton_residual\":{:.17e},\n\"maximum_accepted_local_metric_this_segment\":{},\n",
        "\"scientific_endpoint_reached\":{},\n\"scientific_admission\":\"NOT_ISSUED\",\n\"unknown_unfinished_process_cost\":false\n}}\n"),
        a.case,status,outcome_error,final_code,exit_code,checkpoint_saved,old.json(),counts.json(),counts.deltas(old),
        start.a,state.a,start_time,end_time,end_time-start_time,prior_wall,fresh_evolution_wall_s,state.wall_elapsed_s,
        setup_wall_s,process_started.elapsed().as_secs_f64(),a.accepted,a.fresh_wall_s,
        driver.config.max_steps,driver.config.max_attempts,driver.config.max_rhs,driver.config.max_wall_s,
        state.next_dln_a,state.last_error,state.max_newton_residual,metric,state.a==end);
    atomic_text(&a.out.join("segment_summary.json"),&summary)?;
    atomic_text(&a.out.join("RETURN.txt"),&format!("status={status}\nerror={outcome_error}\nfinalization_error={final_code}\nexit_code={exit_code}\ncheckpoint_saved={checkpoint_saved}\na={}\naccepted={}\nattempts={}\ncomparisons={}\nrejections={}\nconsecutive_rejects={}\nrhs_evaluations={}\nprior_wall_s={}\nfresh_wall_s={}\nwall_s={}\nnext_dln_a={}\nmax_newton_residual={}\nlast_error={}\nscientific_admission=NOT_ISSUED\n",state.a,state.accepted,state.attempts,state.comparisons,state.rejects,state.consecutive_rejects,state.rhs_evaluations,prior_wall,fresh_evolution_wall_s,state.wall_elapsed_s,state.next_dln_a,state.max_newton_residual,state.last_error))?;
    let receipt_error=if final_error.is_some(){final_code}else{outcome_error};
    progress(&a.out,&driver,&state,&a.case,status,receipt_error,checkpoint_saved)?;
    println!("AX11_T2_END case={} status={status} exit={exit_code} accepted_delta={} trials_delta={} rhs_delta={} a={:.17e} cumulative_wall_s={:.6}",a.case,state.accepted-start.accepted,state.attempts-start.attempts,state.rhs_evaluations-start.rhs_evaluations,state.a,state.wall_elapsed_s);
    Ok(exit_code)
}

fn main() {
    match Args::parse().and_then(run) {
        Ok(code)=>std::process::exit(code),
        Err(e)=>{
            eprintln!("AX11_T2_STOP {}",e.code());
            if e.code()=="AX11_T2_USAGE" {eprintln!("usage: ax11_production_segment CONFIG CHECKPOINT|IC NEW_OUT ZERO|PLUS ACCEPTED_DELTA [SEGMENT_FRESH_WALL_SECONDS]");}
            std::process::exit(2);
        }
    }
}
