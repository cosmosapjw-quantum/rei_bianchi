//! Linux-only bounded indexed workers; mathematical reductions remain on the caller.
use super::*;
#[repr(C)]struct TimeSpec{sec:i64,nsec:i64}
unsafe extern "C"{fn sched_setaffinity(pid:i32,len:usize,mask:*const u8)->i32;fn clock_gettime(clock:i32,time:*mut TimeSpec)->i32;}
fn clock(clock:i32)->u64{let mut t=TimeSpec{sec:0,nsec:0};assert_eq!(unsafe{clock_gettime(clock,&mut t)},0);t.sec as u64*1_000_000_000+t.nsec as u64}
fn pin(core:usize)->R<()>{let mut mask=[0u8;128];mask[core/8]|=1<<(core%8);if unsafe{sched_setaffinity(0,mask.len(),mask.as_ptr())}!=0{return Err("worker affinity failed".into())}Ok(())}
fn thread_position()->R<(u32,usize)>{let stat=std::fs::read_to_string("/proc/thread-self/stat").map_err(err)?;let tid=stat.split_whitespace().next().ok_or("tid missing")?.parse().map_err(err)?;let tail=stat.rsplit_once(')').ok_or("stat malformed")?.1;let cpu=tail.split_whitespace().nth(36).ok_or("stat cpu missing")?.parse().map_err(err)?;Ok((tid,cpu))}
pub fn worker_count()->usize{std::env::var("REI_WORKERS").ok().and_then(|x|x.parse::<usize>().ok()).filter(|x|(1..=8).contains(x)).unwrap_or(1)}
fn merge(t:Telemetry){TELEMETRY.with(|v|{let mut a=v.borrow_mut();a.created+=t.created;a.retired+=t.retired;a.peak=a.peak.max(t.peak);for(k,n)in t.counters{*a.counters.entry(k).or_default()+=n}for(k,(len,cap,size))in t.arrays{let e=a.arrays.entry(k).or_insert((0,0,size));e.0=e.0.max(len);e.1=e.1.max(cap)}})}
pub fn panel_map_with<T:Send,F:Fn(usize)->R<T>+Sync>(workers:usize,len:usize,f:F)->R<Vec<T>>{
 if !(1..=8).contains(&workers){return Err("unsupported worker count".into())}
 let _summaries=p::reserve_site_capacity(len.checked_mul(2).ok_or("summary capacity overflow")?).map_err(err)?;
 if workers==1{let _capacity=p::reserve_site_capacity(256).map_err(err)?;let begin=clock(1);let cpu=clock(3);let result=(0..len).map(|i|std::panic::catch_unwind(std::panic::AssertUnwindSafe(||f(i))).unwrap_or_else(|_|Err(format!("panel {i} worker panic")))).collect();println!("PANEL_COMPUTE workers=1 panels={len} wall_ns={} CPU_ns={}",clock(1)-begin,clock(3)-cpu);return result}
 // Reserve all per-worker live per-site buffer capacities conservatively, in addition
 // to the existing shared/driver leases. Fixed fixture cuts<=22, owners<=32,
 // direct/diagnostic<=32 each, reduction scratch<=64, control cuts capacity87.
 // Existing nested leases cover their 64-node closure arrays. Eight workers fit
 // the same shared global4096 cap; reservations are released on every exit/panic.
 let jobs=workers.min(len.max(1));let started=clock(1);
 let joined=std::thread::scope(|scope|{let f=&f;let mut handles=Vec::with_capacity(jobs);
  for core in 0..jobs{let start=len*core/jobs;let end=len*(core+1)/jobs;handles.push(scope.spawn(move||{
   let run=(||->R<(Vec<R<T>>,Telemetry)>{pin(core)?;let _capacity=p::reserve_site_capacity(256).map_err(err)?;let(tid,actual)=thread_position()?;let begin=clock(1);let cpu_begin=clock(3);let mut results=Vec::with_capacity(end-start);let mut evidence=String::new();
    for i in start..end{let before=clock(1);let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||f(i))).unwrap_or_else(|_|Err(format!("panel {i} worker panic")));let after=clock(1);let(_,observed)=thread_position()?;use std::fmt::Write;write!(evidence,"{i}@{observed}@{before}@{after};").map_err(err)?;results.push(result)}
    let finish=clock(1);let cpu=clock(3)-cpu_begin;println!("WORKER core={core} tid={tid} observed_start_core={actual} begin_ns={begin} end_ns={finish} CPU_ns={cpu} panels={evidence}");let t=telemetry();if t.live!=0{return Err("worker lease leak".into())}Ok((results,t))})();run
  }))}
  handles.into_iter().map(|h|h.join().unwrap_or_else(|_|Err("worker infrastructure panic".into()))).collect::<Vec<_>>()});
 let elapsed=clock(1)-started;let mut out=Vec::with_capacity(len);for group in joined{let(results,t)=group?;merge(t);for x in results{out.push(x?)}}
 let(live,peak)=p::site_counts();println!("PANEL_COMPUTE workers={jobs} panels={len} wall_ns={elapsed} GLOBAL_CAPACITY live={live} peak={peak} cap=4096");Ok(out)
}
