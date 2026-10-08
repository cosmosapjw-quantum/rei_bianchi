//! Opt-in durable state of the ACTUAL frozen-panel continuation caller.
//! Point/BE replacement is refused: changing the gas/clock/characteristic scheme is not authorized.
use super::*;
use std::io::Read;
use std::path::{Path,PathBuf};
use std::process::{Command,Stdio};
#[path="run_identity.rs"]mod run_identity;
const MAGIC:&[u8]=b"REI_FROZEN_PANEL_CONTINUATION_CHECKPOINT_V1\n";
const MAX:usize=16*1024*1024;
const CONFIG:&str=include_str!("../../long-flrw/configs/igm_manufactured_z12_to10.cfg");
include!("build_identity.rs");
fn sha(bytes:&[u8])->R<String>{let mut p=Command::new("sha256sum").stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn().map_err(err)?;let written=p.stdin.take().ok_or("SHA stdin")?.write_all(bytes);let out=p.wait_with_output().map_err(err)?;written.map_err(err)?;if !out.status.success(){return Err("SHA failed".into())}let s=String::from_utf8(out.stdout).map_err(err)?;let h=s.split_whitespace().next().ok_or("SHA output")?;if h.len()!=64||!h.bytes().all(|b|b.is_ascii_digit()||(b'a'..=b'f').contains(&b)){return Err("SHA format".into())}Ok(h.into())}
struct W(Vec<u8>);
impl W{fn n(&mut self,x:u64){self.0.extend(x.to_le_bytes())}fn f(&mut self,x:f64){self.n(x.to_bits())}fn text(&mut self,x:&str){self.n(x.len() as u64);self.0.extend(x.as_bytes())}fn wide(&mut self,x:Wide){self.f(x.mantissa());self.n(x.exponent() as i64 as u64)}}
struct D<'a>{b:&'a[u8],i:usize}
impl<'a>D<'a>{
 fn take(&mut self,n:usize)->R<&'a[u8]>{let end=self.i.checked_add(n).ok_or("length overflow")?;let b=self.b.get(self.i..end).ok_or("INCOMPLETE_CHECKPOINT")?;self.i=end;Ok(b)}
 fn n(&mut self)->R<u64>{Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap()))}
 fn size(&mut self,cap:usize)->R<usize>{let n=usize::try_from(self.n()?).map_err(err)?;if n>cap{return Err("SCHEMA_CAP".into())}Ok(n)}
 fn f(&mut self)->R<f64>{let x=f64::from_bits(self.n()?);if !x.is_finite(){return Err("NONFINITE_CHECKPOINT".into())}Ok(x)}
 fn text(&mut self,cap:usize)->R<String>{let n=self.size(cap)?;String::from_utf8(self.take(n)?.to_vec()).map_err(err)}
 fn boolean(&mut self)->R<bool>{match self.n()?{0=>Ok(false),1=>Ok(true),_=>Err("INVALID_TAG".into())}}
 fn wide(&mut self)->R<Wide>{let x=self.f()?;let e=i32::try_from(self.n()? as i64).map_err(err)?;let w=Wide::from_parts(x,e).map_err(err)?;if w.mantissa().to_bits()!=x.to_bits()||w.exponent()!=e{return Err("NONCANONICAL_WIDE".into())}Ok(w)}
}
fn context(w:&mut W,frame:&Frame,namespace:&str,attempt:u64){
 w.text(BUILD_PIN);w.text(namespace);w.n(attempt);w.text(CONFIG);
 for x in frame.gas.fractions{w.f(x)}w.f(frame.gas.w_erg_per_h);
 for x in frame.times{w.f(x)}w.n(frame.mesh.len() as u64);for x in &frame.mesh{w.f(*x)}
}
fn state_image(panels:&[Panel],ledger:&Ledger)->String{
 // Full typed state comparison supplements envelope checksum; do not use hash-only occurrence authority.
 let mut s=format!("{ledger:?}\n");for p in panels{let(k,n,m)=p.pair.components();let logs=p.pair.logs();s.push_str(&format!("{:?}/{k}/{:016x}/{:016x}/{:016x}/{:016x}\n",p,n.to_bits(),m.to_bits(),logs.0.to_bits(),logs.1.to_bits()))}s
}
fn encode(frame:&Frame,panels:&[Panel],ledger:&Ledger,history:&str,namespace:&str,attempt:u64)->R<Vec<u8>>{
 let stage=ledger.increments.len();if ![3,4].contains(&stage){return Err("FROZEN_WINDOW_ONLY".into())}
 let mut w=W(Vec::new());context(&mut w,frame,namespace,attempt);w.n(stage as u64);w.n(panels.len() as u64);
 for p in panels{w.f(p.l);w.f(p.r);let(k,n,m)=p.pair.components();w.n(k as i64 as u64);w.f(n);w.f(m);for x in [p.closure.l,p.closure.r,p.closure.n,p.closure.beta]{w.f(x)}w.n(p.closure.front as u64);w.n(p.front as u64);w.n(p.provenance as u64);for x in p.incoming_loss_metadata{w.wide(x)}let(ln,lm)=p.pair.logs();w.f(ln);w.f(lm)}
 for inc in &ledger.increments{for x in inc{w.wide(*x)}}
 w.n(ledger.charges().len() as u64);
 for c in ledger.charges(){w.text(&c.lane);w.n(c.transition as u64);w.text(&c.boundary);w.text(&c.id);w.n(c.term as u64);w.wide(c.bound);w.wide(c.coefficient);w.text(c.units)}
 w.text(history);w.text(&sha(state_image(panels,ledger).as_bytes())?);
 let mut bytes=MAGIC.to_vec();bytes.extend(sha(&w.0)?.as_bytes());bytes.push(b'\n');bytes.extend(w.0);
 if bytes.len()>MAX{return Err("CHECKPOINT_CAP".into())}
 let (pp,ll,hh,aa)=decode(frame,&bytes,namespace)?;
 if state_image(&pp,&ll)!=state_image(panels,ledger)||hh!=history||aa!=attempt{return Err("ENCODER_ROUNDTRIP".into())}Ok(bytes)
}
fn decode(frame:&Frame,bytes:&[u8],namespace:&str)->R<(Vec<Panel>,Ledger,String,u64)>{
 if bytes.len()>MAX||!bytes.starts_with(MAGIC){return Err("SCHEMA_CAP".into())}
 let tail=&bytes[MAGIC.len()..];if tail.len()<65||tail[64]!=b'\n'||sha(&tail[65..])?.as_bytes()!=&tail[..64]{return Err("CHECKSUM".into())}
 let mut d=D{b:&tail[65..],i:0};
 if d.text(256)?!=BUILD_PIN{return Err("SOURCE_CONTEXT_MISMATCH".into())}
 if d.text(65536)?!=namespace{return Err("RUN_NAMESPACE_MISMATCH".into())}
 let attempt=d.n()?;
 if d.text(65536)?!=CONFIG{return Err("SOURCE_CONTEXT_MISMATCH".into())}
 for x in frame.gas.fractions.into_iter().chain([frame.gas.w_erg_per_h]){if d.n()?!=x.to_bits(){return Err("GAS_CONTEXT_MISMATCH".into())}}
 for x in frame.times{if d.n()?!=x.to_bits(){return Err("EXACT_CLOCK_MISMATCH".into())}}
 if d.size(257)?!=frame.mesh.len(){return Err("PANEL_TOPOLOGY_MISMATCH".into())}
 for x in &frame.mesh{if d.n()?!=x.to_bits(){return Err("PANEL_TOPOLOGY_MISMATCH".into())}}
 let stage=d.size(4)?;if ![3,4].contains(&stage){return Err("FROZEN_WINDOW_ONLY".into())}
 let n=d.size(256)?;
 let s=frame.times[4*stage];let lo=(frame.times[0]+frame.cfg.source.energy_min_ev.ln()).max(s+13.6f64.ln());let hi=s+frame.cfg.source.energy_max_ev.ln();
 let mut edges=vec![lo];edges.extend(frame.mesh.iter().copied().filter(|x|*x>lo&&*x<hi));edges.push(hi);
 if n+1!=edges.len(){return Err("PANEL_TOPOLOGY_MISMATCH".into())}
 let mut panels=Vec::with_capacity(n);
 for i in 0..n{
  let l=d.f()?;let r=d.f()?;if l.to_bits()!=edges[i].to_bits()||r.to_bits()!=edges[i+1].to_bits(){return Err("EXACT_PANEL_MISMATCH".into())}
  let k=i32::try_from(d.n()? as i64).map_err(err)?;let n=d.f()?;let m=d.f()?;
  let closure=bridge::v2::Closure{l:d.f()?,r:d.f()?,n:d.f()?,beta:d.f()?,front:d.boolean()?};let front=d.boolean()?;let provenance=u32::try_from(d.n()?).map_err(err)?;
  let incoming_loss_metadata=[d.wide()?,d.wide()?];let ln=d.n()?;let lm=d.n()?;
  if closure.l.to_bits()!=l.to_bits()||closure.r.to_bits()!=r.to_bits()||closure.n.to_bits()!=n.to_bits()||closure.front!=front||provenance!=stage as u32||front!=(i+1==edges.len()-1){return Err("PANEL_LINEAGE_CONTEXT_MISMATCH".into())}
  let pair={let _lease=SiteGuard::new(64)?;MomentPair::new(l,r,k,n,m,front).map_err(err)?};let logs=pair.logs();if logs.0.to_bits()!=ln||logs.1.to_bits()!=lm{return Err("PAIR_LOG_MISMATCH".into())}
  panels.push(Panel{l,r,pair,closure,front,provenance,incoming_loss_metadata});
 }
 let mut increments=Vec::new();for _ in 0..stage{let mut inc=[Wide::ZERO;11];for x in &mut inc{*x=d.wide()?}increments.push(inc)}
 let count=d.size(20000)?;let mut groups:Vec<Vec<Charge>>=(0..stage).map(|_|Vec::new()).collect();let mut previous=0;
 for _ in 0..count{let lane=d.text(65536)?;let transition=d.size(stage-1)?;if transition<previous{return Err("CHARGE_ORDER".into())}previous=transition;let boundary=d.text(65536)?;let id=d.text(65536)?;let term=d.size(12)?;let bound=d.wide()?;let coefficient=d.wide()?;let units=d.text(32)?;let expected=if photon_term(term){"photons/H"}else{"erg/H"};if units!=expected{return Err("CHARGE_UNITS".into())}groups[transition].push(Charge{lane,transition,boundary,id,term,bound,coefficient,units:expected})}
 let mut ledger=Ledger::default();for(inc,charges)in increments.into_iter().zip(groups){ledger.commit(inc,charges,true)?}if ledger.charges().len()!=count{return Err("CHARGE_LOSS".into())}
 let history=d.text(8*1024*1024)?;if !history.starts_with("kind,id,field,bits,exp\n"){return Err("SOURCE_HISTORY_AUDIT_SCHEMA".into())}
 let image=d.text(256)?;if d.i!=d.b.len()||sha(state_image(&panels,&ledger).as_bytes())?!=image{return Err("TYPED_STATE_DIGEST".into())}
 Ok((panels,ledger,history,attempt))
}
fn read_head(root:&Path)->R<Vec<u8>>{
 let path=root.join("HEAD");let meta=std::fs::symlink_metadata(&path).map_err(err)?;
 if !meta.file_type().is_file()||meta.len()>MAX as u64{return Err("HEAD_FILE_CAP".into())}
 let mut bytes=Vec::new();File::open(path).map_err(err)?.take(MAX as u64+1).read_to_end(&mut bytes).map_err(err)?;
 if bytes.len()>MAX{return Err("HEAD_READ_CAP".into())}Ok(bytes)
}
pub struct Store{run:run_identity::Run,serial:u64,generation:Option<usize>,head_hash:Option<String>}
impl Store{
 pub fn create(root:&Path)->R<Self>{let run=run_identity::Run::create(root)?;Ok(Self{run,serial:0,generation:None,head_hash:None})}
 pub fn resume(root:&Path,frame:&Frame)->R<(Self,Vec<Panel>,Ledger,String)>{
  let run=run_identity::Run::resume(root)?;let bytes=read_head(&run.root)?;
  let(panels,ledger,history,head_attempt)=decode(frame,&bytes,&run.namespace)?;
  let mut serial=0;for e in std::fs::read_dir(&run.root).map_err(err)?{let e=e.map_err(err)?;let name=e.file_name().to_string_lossy().into_owned();if let Some(s)=name.strip_prefix("attempt-"){let n=s.parse::<u64>().map_err(err)?;if !e.file_type().map_err(err)?.is_file()||std::fs::read_to_string(e.path()).map_err(err)?!=run.namespace{return Err("ATTEMPT_NAMESPACE_MISMATCH".into())}serial=serial.max(n.checked_add(1).ok_or("attempt exhaustion")?)}}
  if serial<=head_attempt || std::fs::read_to_string(run.root.join(format!("attempt-{head_attempt}"))).map_err(err)?!=run.namespace{return Err("MISSING_COMMITTED_ATTEMPT_LEASE".into())}
  let generation=Some(ledger.increments.len());let head_hash=Some(sha(&bytes)?);
  Ok((Self{run,serial,generation,head_hash},panels,ledger,history))
 }
 pub fn publish(&mut self,frame:&Frame,panels:&[Panel],ledger:&Ledger,history:&str)->R<()>{
  self.run.check_owner()?;
  let expected=self.generation.map_or(3,|g|g+1);
  if ledger.increments.len()!=expected{return Err("STALE_FROZEN_GENERATION".into())}
  if let Some(expected)=&self.head_hash{if sha(&read_head(&self.run.root)?)?!=*expected{return Err("STALE_FROZEN_HEAD".into())}}
  let attempt=self.serial;let bytes=encode(frame,panels,ledger,history,&self.run.namespace,attempt)?;self.serial=self.serial.checked_add(1).ok_or("attempt exhaustion")?;
  let mut lease=OpenOptions::new().write(true).create_new(true).open(self.run.root.join(format!("attempt-{attempt}"))).map_err(err)?;lease.write_all(self.run.namespace.as_bytes()).map_err(err)?;lease.sync_all().map_err(err)?;
  let published_hash=sha(&bytes)?;
  let pending=self.run.root.join(format!("pending-{attempt}"));let mut f=OpenOptions::new().write(true).create_new(true).open(&pending).map_err(err)?;f.write_all(&bytes).map_err(err)?;f.sync_all().map_err(err)?;File::open(&self.run.root).map_err(err)?.sync_all().map_err(err)?;
  std::fs::rename(pending,self.run.root.join("HEAD")).map_err(err)?;
  // Rename publishes. Report uncertain directory durability without rollback Err.
  self.generation=Some(ledger.increments.len());self.head_hash=Some(published_hash);
  let synced=File::open(&self.run.root).and_then(|f|f.sync_all()).is_ok();println!("FROZEN_DURABLE_COMMIT stage={} directory_synced={synced} physical_history_full_wide=HOLD",ledger.increments.len());Ok(())
 }
 /// Checkpoint-only process-stop control: no new scientific trial/transaction.
 /// Stages the current real admitted k3 state, consumes a fresh checkpoint lease,
 /// then exits before HEAD rename. Normal publication generation rules are untouched.
 pub fn stop_pending_control(&mut self,frame:&Frame,panels:&[Panel],ledger:&Ledger,history:&str)->R<()> {
  self.run.check_owner()?;
  if self.generation!=Some(3)||ledger.increments.len()!=3{return Err("pending control requires committed k3".into())}
  if self.head_hash.as_ref()!=Some(&sha(&read_head(&self.run.root)?)?){return Err("STALE_FROZEN_HEAD".into())}
  let attempt=self.serial;let bytes=encode(frame,panels,ledger,history,&self.run.namespace,attempt)?;
  let mut lease=OpenOptions::new().write(true).create_new(true).open(self.run.root.join(format!("attempt-{attempt}"))).map_err(err)?;
  lease.write_all(self.run.namespace.as_bytes()).map_err(err)?;lease.sync_all().map_err(err)?;
  let mut f=OpenOptions::new().write(true).create_new(true).open(self.run.root.join(format!("pending-{attempt}"))).map_err(err)?;
  f.write_all(&bytes).map_err(err)?;f.sync_all().map_err(err)?;File::open(&self.run.root).map_err(err)?.sync_all().map_err(err)?;
  eprintln!("CHECKPOINT_ONLY_REAL_K3_PENDING_SYNCED_STOP_BEFORE_RENAME_NO_SCIENCE_TRIAL");std::process::exit(73)
 }

}
pub fn mode()->Option<String>{std::env::var("REI_CONTINUOUS_DURABLE").ok()}
pub fn root()->R<PathBuf>{std::env::var_os("REI_CONTINUOUS_RUN_ROOT").map(PathBuf::from).ok_or("missing explicit frozen run root".into())}
pub fn refuse_native_be()->R<()>{if std::env::var_os("REI_NATIVE_BE_HANDOFF").is_some(){Err("NATIVE_BE_INCOMPATIBLE_FROZEN_GAS_MIDPOINT_CHARACTERISTIC_SOURCE_CUTOFF_PANELS".into())}else{Ok(())}}
