//! Bounded prefix/restart probe of the original AXBI driver, never a full-history runner.
//! Install in examples/ax11_profile_window.rs of an isolated, hash-verified crate.
//! The deployment runner MUST verify source, config and checkpoint identities first.
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use rei_microphysics::ForwardError;
use std::{env, fs, io::{BufWriter, Seek, SeekFrom, Write}, path::{Path, PathBuf}, time::Instant};

type R<T> = Result<T, ForwardError>;
fn fail(code: &'static str) -> ForwardError { ForwardError::InvalidInput(code) }
fn io(_: std::io::Error) -> ForwardError { fail("AX11_WINDOW_IO") }
fn add(a: usize, b: usize) -> R<usize> { a.checked_add(b).ok_or(fail("AX11_WINDOW_COUNT_OVERFLOW")) }

struct Args {
    config: PathBuf, checkpoint: Option<PathBuf>, out: PathBuf,
    accepted: usize, attempts: usize, rhs: usize, wall: f64,
    stop_a: Option<f64>, case: Option<String>,
}
impl Args {
    fn parse() -> R<Self> {
        let v: Vec<String> = env::args().collect();
        if !(8..=10).contains(&v.len()) { return Err(fail("AX11_WINDOW_USAGE")); }
        let count = |i: usize| -> R<usize> { v[i].parse().map_err(|_| fail("AX11_WINDOW_COUNT")) };
        let number = |i: usize| -> R<f64> { v[i].parse().map_err(|_| fail("AX11_WINDOW_NUMBER")) };
        let a = Self {
            config: v[1].clone().into(),
            checkpoint: if v[2] == "IC" { None } else { Some(v[2].clone().into()) },
            out: v[3].clone().into(), accepted: count(4)?, attempts: count(5)?, rhs: count(6)?,
            wall: number(7)?,
            stop_a: if v.len() > 8 && v[8] != "NONE" { Some(number(8)?) } else { None },
            case: v.get(9).cloned(),
        };
        if a.accepted == 0 || a.attempts == 0 || a.rhs == 0 || !a.wall.is_finite() || a.wall <= 0.0
            || a.stop_a.is_some_and(|x| !x.is_finite() || x <= 0.0)
        { return Err(fail("AX11_WINDOW_CAP_DOMAIN")); }
        Ok(a)
    }
}

#[derive(Clone, Copy)]
struct Counts { accepted: usize, attempts: usize, comparisons: usize, rejects: usize, consecutive: usize, rhs: usize }
impl Counts {
    fn state(s: &DriverState) -> Self { Self { accepted:s.accepted, attempts:s.attempts, comparisons:s.comparisons, rejects:s.rejects, consecutive:s.consecutive_rejects, rhs:s.rhs_evaluations } }
    fn zero() -> Self { Self { accepted:0, attempts:0, comparisons:0, rejects:0, consecutive:0, rhs:0 } }
    fn json(self) -> String { format!("{{\"accepted\":{},\"attempts\":{},\"comparisons\":{},\"rejects\":{},\"consecutive_rejects\":{},\"rhs_evaluations\":{}}}",self.accepted,self.attempts,self.comparisons,self.rejects,self.consecutive,self.rhs) }
}

// Only resource counters/wall are parsed here. The original reader remains the
// authority for the complete checkpoint, physics state, clock and shape.
fn prior(path: Option<&Path>) -> R<(Counts, f64)> {
    let Some(path) = path else { return Ok((Counts::zero(), 0.0)); };
    let text = fs::read_to_string(path).map_err(io)?;
    let v: Vec<&str> = text.lines().collect();
    if v.len() != 6 || v[0] != "AXBI_CHECKPOINT_V2" { return Err(fail("AX11_WINDOW_CHECKPOINT_HEADER")); }
    let c = v[2].split_whitespace().map(|x| x.parse::<usize>().map_err(|_| fail("AX11_WINDOW_CHECKPOINT_COUNTER"))).collect::<R<Vec<_>>>()?;
    let f = v[1].split_whitespace().map(|x| x.parse::<f64>().map_err(|_| fail("AX11_WINDOW_CHECKPOINT_FLOAT"))).collect::<R<Vec<_>>>()?;
    if c.len()!=6 || f.len()!=11 || !f[10].is_finite() || f[10]<0.0 { return Err(fail("AX11_WINDOW_CHECKPOINT_SHAPE")); }
    Ok((Counts { accepted:c[0],attempts:c[1],rejects:c[2],consecutive:c[3],rhs:c[4],comparisons:c[5] }, f[10]))
}

fn effective_text(c: &DriverConfig) -> String {
    format!(concat!("q_ref={:.17e}\nsame_h={}\nend_zbar={:.17e}\nescape_fraction={:.17e}\n",
        "initial_temperature_k={:.17e}\nenergy_subdivisions={}\nn_mu={}\nbackground_panels={}\n",
        "local_target={:.17e}\ninitial_dln_a={:.17e}\nmax_steps={}\nmax_attempts={}\nmax_rhs={}\n",
        "max_wall_s={:.17e}\nspectra_every_accepted={}\noutput_budget_mib={}\n"),
        c.q_ref,c.same_h,c.end_zbar,c.escape_fraction,c.initial_temperature_k,c.energy_subdivisions,c.n_mu,
        c.background_panels,c.local_target,c.initial_dln_a,c.max_steps,c.max_attempts,c.max_rhs,c.max_wall_s,
        c.spectra_every_accepted,c.output_budget_mib)
}

fn open_table(path: &Path, header: &str) -> R<BufWriter<fs::File>> {
    let mut w = BufWriter::new(fs::OpenOptions::new().write(true).create_new(true).open(path).map_err(io)?);
    writeln!(w,"{header}").map_err(io)?; Ok(w)
}
struct Tables {
    h: BufWriter<fs::File>, a: BufWriter<fs::File>, p: BufWriter<fs::File>,
    l: BufWriter<fs::File>, fb: BufWriter<fs::File>, rejects: BufWriter<fs::File>,
}
impl Tables {
    fn new(out: &Path) -> R<Self> { Ok(Self {
        h:open_table(&out.join("history.csv"),"case_id,q_ref,Sigma,time_s,a,zbar,b,H_per_s,s_per_s,x_HII,x_HeII,x_HeIII,nH_proper_cm3,ne_proper_cm3,temperature_K,Gamma_HI_per_s,Gamma_HeI_per_s,Gamma_HeII_per_s,photon_n_per_H,photon_u_eV_per_H,J0_photon_u_eV_per_H,J1_photon_u_eV_per_H,J2_photon_u_eV_per_H,x_HI,x_HeI")?,
        a:open_table(&out.join("abundances.csv"),"run_id,time_s,zbar,Tgas_K,background_Tref_K,species_id,A,Z,charge,nproper,element_fraction,Ybaryon,electron_xe,normalization_registry")?,
        p:open_table(&out.join("spectra.csv"),"case_id,q_ref,Sigma,time_s,a,zbar,energy_low_eV,energy_high_eV,mu_center,solid_angle_weight_sr,photon_n_per_H,photon_u_eV_per_H")?,
        l:open_table(&out.join("ledgers.csv"),"case_id,time_s,ledger_name,residual,tolerance,status")?,
        fb:open_table(&out.join("feedback.csv"),"case_id,time_s,a,H_per_s,effective_radiation_DeltaP_J_m3,ionizing_DeltaP_J_m3,effective_radiation_signed_deltaepsilon_J_m3,extra_energy_J_m3,extra_energy_ratio,total_DeltaP_J_m3")?,
        rejects:open_table(&out.join("raw/rejections.csv"),"attempt,a,dln_a,error")?,
    }) }
    fn batch(&mut self, d:&Driver, s:&DriverState, case:&str, out:&Path, spectrum:bool) -> R<()> {
        d.output_batch(s,case,out,spectrum,&mut self.h,&mut self.a,&mut self.p,&mut self.l,&mut self.fb)
    }
    fn flush(&mut self) -> R<()> {
        for w in [&mut self.h,&mut self.a,&mut self.p,&mut self.l,&mut self.fb,&mut self.rejects] { w.flush().map_err(io)?; } Ok(())
    }
}

// Preallocate the maximum finite trace BEFORE any scientific output. Original
// directory-size guards therefore account for every future trace byte, including
// the terminal-spectrum/checkpoint reservation. Written record count is durable.
struct Trace { f:fs::File, n:u64, capacity:u64, photons:usize, record_bytes:u64 }
impl Trace {
    fn new(path:&Path, photons:usize, capacity:usize, output_limit:u64) -> R<Self> {
        let record_bytes=(photons as u64).checked_add(38).and_then(|x|x.checked_mul(8)).ok_or(fail("AX11_TRACE_SIZE"))?;
        let bytes=(capacity as u64).checked_mul(record_bytes).and_then(|x|x.checked_add(56)).ok_or(fail("AX11_TRACE_SIZE"))?;
        if bytes > output_limit / 2 { return Err(fail("AX11_TRACE_RESERVATION_CAP")); }
        let mut f=fs::OpenOptions::new().write(true).read(true).create_new(true).open(path).map_err(io)?;
        f.set_len(bytes).map_err(io)?;
        f.write_all(b"AX11TRC1").map_err(io)?;
        for x in [photons as u64,32,6,record_bytes,0,capacity as u64] { f.write_all(&x.to_le_bytes()).map_err(io)?; }
        f.flush().map_err(io)?;
        Ok(Self {f,n:0,capacity:capacity as u64,photons,record_bytes})
    }
    fn push(&mut self,s:&DriverState) -> R<()> {
        if self.n>=self.capacity || s.photons.len()!=self.photons { return Err(fail("AX11_TRACE_SHAPE")); }
        let l=&s.ledgers;
        let mut values=Vec::with_capacity(32+self.photons);
        values.extend_from_slice(&[s.a,s.gas.fractions[0],s.gas.fractions[1],s.gas.fractions[2],s.gas.w_erg_per_h,
            s.next_dln_a,s.max_newton_residual,s.last_error,l.source_n,l.source_u,l.absorbed_n,l.escaped_u,
            l.boundary_n,l.boundary_u,l.thermal_work,l.photon_work,l.cmb_input,l.dr_events,l.ce_cap_ev,l.excluded_dr_ev]);
        for x in [l.rr_events,l.ci_events,l.photo_events,l.ci_floor_events] { values.extend_from_slice(&x); }
        self.f.seek(SeekFrom::Start(56+self.n*self.record_bytes)).map_err(io)?;
        for x in values { self.f.write_all(&x.to_bits().to_le_bytes()).map_err(io)?; }
        for x in [s.accepted,s.attempts,s.comparisons,s.rejects,s.consecutive_rejects,s.rhs_evaluations] { self.f.write_all(&(x as u64).to_le_bytes()).map_err(io)?; }
        for &x in &s.photons { self.f.write_all(&x.to_bits().to_le_bytes()).map_err(io)?; }
        self.n+=1;
        self.f.seek(SeekFrom::Start(40)).map_err(io)?;
        self.f.write_all(&self.n.to_le_bytes()).map_err(io)?;
        self.f.flush().map_err(io)
    }
    fn finish(&mut self) -> R<()> { self.f.set_len(56+self.n*self.record_bytes).map_err(io)?; self.f.flush().map_err(io) }
}

#[cfg(ax11_profile)]
struct Components { w:BufWriter<fs::File> }
#[cfg(not(ax11_profile))]
struct Components;
impl Components {
    fn new(out:&Path) -> R<Self> {
        #[cfg(ax11_profile)] { Ok(Self {w:open_table(&out.join("raw/error_components.csv"),"a_start,to_proposed,dln_a_proposed,outcome,error_code,accepted_before,accepted_after,attempts_before,attempts_after,comparisons_before,comparisons_after,rejects_after,rhs_before,rhs_after,adaptive_wall_ns,components_available,HII,HeII,HeIII,thermal,photon_N_L1,photon_U_L1")?}) }
        #[cfg(not(ax11_profile))] { let _=out; Ok(Self) }
    }
    fn row(&mut self,d:&Driver,before:&DriverState,after:&DriverState,to:f64,outcome:&str,error:&str,nanos:u128) -> R<()> {
        #[cfg(ax11_profile)] {
            let c=d.last_error_components();
            write!(self.w,"{:.17e},{:.17e},{:.17e},{},{},{},{},{},{},{},{},{},{},{},{},{}",
                before.a,to,before.next_dln_a,outcome,error,before.accepted,after.accepted,before.attempts,after.attempts,
                before.comparisons,after.comparisons,after.rejects,before.rhs_evaluations,after.rhs_evaluations,nanos,c.is_some()).map_err(io)?;
            match c { Some(v)=>{for x in v {write!(self.w,",{x:.17e}").map_err(io)?;}},None=>write!(self.w,",NA,NA,NA,NA,NA,NA").map_err(io)? }
            writeln!(self.w).map_err(io)?; self.w.flush().map_err(io)?;
        }
        #[cfg(not(ax11_profile))] { let _=(d,before,after,to,outcome,error,nanos); }
        Ok(())
    }
}

// Optional future fixed-a mode. Never change end_zbar and never call a nearby
// floating-point a the requested fixed a. No scientific run below uses this mode.
// The public original API cannot reach every arbitrary binary64 endpoint.
fn clip_to_exact_a(s:&mut DriverState,target:f64,end:f64) -> R<bool> {
    if (s.a*s.next_dln_a.exp()).min(end)<=target { return Ok(false); }
    let h=(target/s.a).ln();
    if !h.is_finite() || h<1e-10 || h>s.next_dln_a { return Err(fail("AX11_FIXED_A_UNREPRESENTABLE")); }
    let bits=h.to_bits();
    for offset in 0..=256_u64 {
        for candidate in [bits.saturating_sub(offset),bits.saturating_add(offset)] {
            let t=f64::from_bits(candidate);
            if t>=1e-10 && t<=s.next_dln_a && (s.a*t.exp()).to_bits()==target.to_bits() {
                s.next_dln_a=t; return Ok(true);
            }
        }
    }
    Err(fail("AX11_FIXED_A_UNREPRESENTABLE"))
}

fn resource_check(out:&Path,total:u64) -> R<()> {
    fn bytes(p:&Path) -> R<u64> {
        let mut n=0_u64;
        for e in fs::read_dir(p).map_err(io)? {
            let e=e.map_err(io)?;
            n=n.checked_add(if e.file_type().map_err(io)?.is_dir(){bytes(&e.path())?}else{e.metadata().map_err(io)?.len()}).ok_or(fail("AX11_OUTPUT_SIZE"))?;
        }
        Ok(n)
    }
    if bytes(out)?>total { return Err(fail("AXBI_OUTPUT_CAP")); }
    if let Ok(status)=fs::read_to_string("/proc/self/status") {
        if status.lines().find(|x|x.starts_with("VmHWM:")).and_then(|x|x.split_whitespace().nth(1)).and_then(|x|x.parse::<u64>().ok()).is_some_and(|x|x>2*1024*1024) { return Err(fail("AXBI_RSS_CAP")); }
    }
    Ok(())
}

fn run(a:Args) -> R<()> {
    let process_started=Instant::now();
    let config_text=fs::read_to_string(&a.config).map_err(io)?;
    let mut cfg=DriverConfig::read(&config_text)?;
    let (old,prior_wall)=prior(a.checkpoint.as_deref())?;
    cfg.max_steps=add(add(old.accepted,a.accepted)?,1)?;
    cfg.max_attempts=add(old.attempts,a.attempts)?;
    cfg.max_rhs=add(old.rhs,a.rhs)?;
    cfg.max_wall_s=prior_wall+a.wall;
    if !cfg.max_wall_s.is_finite() { return Err(fail("AX11_WINDOW_WALL_OVERFLOW")); }
    let effective=effective_text(&cfg);
    let case=a.case.as_deref().unwrap_or(if cfg.q_ref==0.0{"ZERO"}else if cfg.q_ref==0.01{"PLUS"}else if cfg.q_ref== -0.01{"MINUS"}else{"AX11"});
    if case.is_empty() || case.contains([',','\n','\r']) { return Err(fail("AXBI_CASE_ID")); }
    let (driver,mut state)=Driver::new(cfg)?;
    if let Some(path)=&a.checkpoint { state=driver.read_checkpoint(path)?; }
    let start=state.clone();
    let actual_old=Counts::state(&state);
    if actual_old.json()!=old.json() || state.wall_elapsed_s.to_bits()!=prior_wall.to_bits() { return Err(fail("AX11_WINDOW_PRIOR_MISMATCH")); }
    let end=1.0/(1.0+driver.config.end_zbar);
    if a.stop_a.is_some_and(|x| x<=state.a || x>end) { return Err(fail("AX11_FIXED_A_DOMAIN")); }
    let start_time=driver.background.point_at_scale(state.a)?.time_s;
    // Atomic directory creation prevents accidental reuse or appended histories.
    fs::create_dir(&a.out).map_err(io)?;
    fs::create_dir(a.out.join("raw")).map_err(io)?;
    fs::create_dir(a.out.join("checkpoints")).map_err(io)?;
    fs::write(a.out.join("config.cfg"),config_text).map_err(io)?;
    fs::write(a.out.join("effective_resource_config.cfg"),effective).map_err(io)?;
    fs::write(a.out.join("source_identity.txt"),compiled_identity()).map_err(io)?;
    fs::write(a.out.join("case_id.txt"),case).map_err(io)?;
    if let Some(path)=&a.checkpoint {fs::copy(path,a.out.join("input_checkpoint.txt")).map_err(io)?;}
    fs::write(a.out.join("metadata.txt"),concat!(
        "clock=elapsed proper seconds since zbar20\nframe=non-tilted normal tetrad\n",
        "method=binary64 BE split step-doubling empirical\n",
        "spectra_cadence=initial; configured accepted-step interval(default60); each30wallsecondcheckpoint; terminal; fullgrid noaveraging\n",
        "scope=bounded accepted-state prefix or checkpoint continuation\n",
        "trace=all accepted states, binary64 bits, excludes wall; initial row included\n",
        "timing_scopes=inclusive; do not add nested scopes\n",
        "timing_overhead=trace and diagnostic IO included in window wall, not adaptive scope\n",
        "preflight=external Python source/config/checkpoint hashes required\n",
        "scientific_admission=NOT_ISSUED\n")).map_err(io)?;
    let mut trace=Trace::new(&a.out.join("raw/state_trace.bin"),state.photons.len(),add(a.accepted,1)?,driver.config.scientific_output_budget_bytes()?)?;
    let mut components=Components::new(&a.out)?;
    let mut t=Tables::new(&a.out)?;
    t.batch(&driver,&state,case,&a.out,true)?;
    t.flush()?; trace.push(&state)?;
    driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.start.txt"),&state)?;
    driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.txt"),&state)?;
    let mut last_spectrum_time=Some(start_time);
    let setup_wall_s=process_started.elapsed().as_secs_f64();
    let started=Instant::now();
    let mut last_save=Instant::now();
    let target_accepted=add(start.accepted,a.accepted)?;
    let mut endpoint_clips=0_usize;
    let outcome=(|| -> R<&'static str> {
        loop {
            state.wall_elapsed_s=prior_wall+started.elapsed().as_secs_f64();
            if state.a==end { return Ok("REPRESENTED_ENDPOINT_REACHED_IN_WINDOW"); }
            if a.stop_a==Some(state.a) {return Ok("FIXED_A_WINDOW_COMPLETE");}
            if state.accepted>=target_accepted {
                return if a.stop_a.is_some(){Err(fail("AX11_FIXED_A_ACCEPTED_CAP"))}else{Ok("ACCEPTED_WINDOW_COMPLETE")};
            }
            if started.elapsed().as_secs_f64()>=a.wall || state.attempts-start.attempts>=a.attempts
                || state.rhs_evaluations-start.rhs_evaluations>=a.rhs
            {return Err(fail("AX11_WINDOW_RESOURCE_CAP"));}
            if let Some(stop)=a.stop_a {if clip_to_exact_a(&mut state,stop,end)?{endpoint_clips+=1;}}
            let previous=state.clone();
            let to=(state.a*state.next_dln_a.exp()).min(end);
            let adaptive_started=Instant::now();
            let attempt=driver.adaptive_step(&mut state);
            let nanos=adaptive_started.elapsed().as_nanos();
            let (label,code)=match &attempt {Ok(true)=>("accepted","NONE"),Ok(false)=>("rejected","NONE"),Err(e)=>("error",e.code())};
            components.row(&driver,&previous,&state,to,label,code,nanos)?;
            let accepted=match attempt {
                Ok(v)=>v,
                Err(e)=>{
                    writeln!(t.rejects,"{},{},{},{e:?}",state.attempts,state.a,state.next_dln_a).map_err(io)?;
                    t.rejects.flush().map_err(io)?;
                    if state.consecutive_rejects>=30 || state.next_dln_a<1e-10 || state.rhs_evaluations>=driver.config.max_rhs {return Err(e);}
                    false
                }
            };
            if !accepted {
                writeln!(t.rejects,"{},{},{},local_metric={}",state.attempts,state.a,state.next_dln_a,state.last_error).map_err(io)?;
                if state.consecutive_rejects>=30 || state.next_dln_a<1e-10 {return Err(fail("AXBI_REJECT_CAP"));}
                continue;
            }
            let terminal=state.a==end || state.accepted>=target_accepted || a.stop_a==Some(state.a);
            let checkpoint_due=driver.spectrum_due(state.accepted,last_save.elapsed().as_secs_f64(),terminal);
            if let Err(e)=t.batch(&driver,&state,case,&a.out,checkpoint_due) {
                let failed=state.clone(); state=previous;
                state.attempts=failed.attempts; state.comparisons=failed.comparisons;
                state.rhs_evaluations=failed.rhs_evaluations; state.rejects=failed.rejects;
                state.wall_elapsed_s=failed.wall_elapsed_s;
                return Err(e);
            }
            trace.push(&state)?;
            if checkpoint_due {
                last_spectrum_time=Some(driver.background.point_at_scale(state.a)?.time_s);
                t.flush()?;
                state.wall_elapsed_s=prior_wall+started.elapsed().as_secs_f64();
                driver.save_checkpoint_budget(&a.out,&a.out.join(format!("checkpoints/{:08}.txt",state.accepted)),&state)?;
                driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.txt"),&state)?;
                resource_check(&a.out,driver.config.output_budget_mib as u64*1024*1024)?;
                last_save=Instant::now();
            }
        }
    })();
    state.wall_elapsed_s=prior_wall+started.elapsed().as_secs_f64();
    // Best-effort terminal persistence preserves the original error and counters.
    let mut final_error=None;
    macro_rules! persist { ($e:expr) => {if let Err(e)=$e {if final_error.is_none(){final_error=Some(e);}}}; }
    persist!(t.flush());
    persist!(driver.ensure_spectrum_snapshot(&state,case,&a.out,&mut last_spectrum_time,&mut t.p));
    persist!(t.p.flush().map_err(io));
    persist!(driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.txt"),&state));
    persist!(driver.save_checkpoint_budget(&a.out,&a.out.join("checkpoint.end.txt"),&state));
    persist!(trace.finish());
    #[cfg(ax11_profile)] {
        persist!(fs::write(a.out.join("raw/driver_timing.csv"),driver.profile_snapshot()).map_err(io));
        persist!(fs::write(a.out.join("raw/background_timing.csv"),driver.background.profile_snapshot()).map_err(io));
    }
    let end_time=driver.background.point_at_scale(state.a)?.time_s;
    let fresh_wall_s=state.wall_elapsed_s-prior_wall;
    let status=match &outcome {Ok(s)=>*s,Err(e)=>e.code()};
    let final_code=final_error.as_ref().map_or("NONE",ForwardError::code);
    let counts=Counts::state(&state);
    let delta=Counts { accepted:counts.accepted-old.accepted,attempts:counts.attempts-old.attempts,
        comparisons:counts.comparisons-old.comparisons,rejects:counts.rejects-old.rejects,
        consecutive:counts.consecutive,rhs:counts.rhs-old.rhs };
    let stop=a.stop_a.map_or_else(||"null".into(),|x|format!("{x:.17e}"));
    let summary=format!(concat!("{{\n\"schema\":\"AX11_BOUNDED_WINDOW_V1\",\n\"status\":\"{}\",\n\"finalization_error\":\"{}\",\n",
        "\"scientific_admission\":\"NOT_ISSUED\",\n\"start_counts\":{},\n\"end_counts\":{},\n\"delta_counts\":{},\n",
        "\"a_start\":{:.17e},\n\"a_end\":{:.17e},\n\"proper_time_start_s\":{:.17e},\n\"proper_time_end_s\":{:.17e},\n",
        "\"proper_time_delta_s\":{:.17e},\n\"prior_wall_s\":{:.17e},\n\"fresh_evolution_wall_s\":{:.17e},\n",
        "\"cumulative_wall_s\":{:.17e},\n\"setup_wall_s\":{:.17e},\n\"process_wall_s\":{:.17e},\n",
        "\"accepted_increment_requested\":{},\n\"attempt_delta_cap\":{},\n\"rhs_delta_cap\":{},\n\"fresh_wall_cap_s\":{:.17e},\n",
        "\"stop_a_requested\":{},\n\"fixed_a_step_clips\":{},\n\"trace_records\":{},\n",
        "\"delta_consecutive_rejects_semantics\":\"end value, not a difference\",\n",
        "\"timing_scopes\":\"inclusive, nested; do not sum\",\n\"wall_cadence_may_differ_across_variants\":true\n}}\n"),
        status,final_code,old.json(),counts.json(),delta.json(),start.a,state.a,start_time,end_time,end_time-start_time,
        prior_wall,fresh_wall_s,state.wall_elapsed_s,setup_wall_s,process_started.elapsed().as_secs_f64(),
        a.accepted,a.attempts,a.rhs,a.wall,stop,endpoint_clips,trace.n);
    fs::write(a.out.join("window_summary.json"),summary).map_err(io)?;
    fs::write(a.out.join("RETURN.txt"),format!("status={status}\nfinalization_error={final_code}\na={}\naccepted={}\nattempts={}\ncomparisons={}\nrejections={}\nrhs_evaluations={}\nprior_wall_s={}\nfresh_wall_s={}\nwall_s={}\nmax_newton_residual={}\nlast_error={}\nscientific_admission=NOT_ISSUED\n",state.a,state.accepted,state.attempts,state.comparisons,state.rejects,state.rhs_evaluations,prior_wall,fresh_wall_s,state.wall_elapsed_s,state.max_newton_residual,state.last_error)).map_err(io)?;
    println!("AX11_WINDOW status={status} finalization={final_code} accepted_delta={} attempts_delta={} rhs_delta={} a={:.17e} fresh_wall_s={:.6}",delta.accepted,delta.attempts,delta.rhs,state.a,fresh_wall_s);
    if let Some(e)=final_error {return Err(e);}
    outcome.map(|_|())
}

fn main() {
    if let Err(e)=Args::parse().and_then(run) {
        eprintln!("AX11_WINDOW_STOP {}",e.code());
        if e.code()=="AX11_WINDOW_USAGE" {eprintln!("usage: ax11_profile_window CONFIG CHECKPOINT|IC NEW_OUT ACCEPTED_DELTA ATTEMPT_DELTA_CAP RHS_DELTA_CAP FRESH_WALL_SECONDS [STOP_A|NONE] [CASE_ID]");}
        std::process::exit(2);
    }
}
