#![allow(dead_code)]
#[path="../../shared-log-spectral-primitives/src/primitives.rs"] pub mod p;
#[path="../../continuous-boundary-prototype-v2/src/primitives.rs"] pub mod v2;
pub use p::{Wide,Tracked,Owners,MomentPair,ClosureInput,restrict,segment,endpoint_pair,admit,EPS};
pub type R<T>=Result<T,String>;
pub fn err<E:std::fmt::Debug>(e:E)->String{format!("{e:?}")}
pub fn w(x:f64)->R<Wide>{Wide::from_f64(x).map_err(err)}
pub fn rel(a:Wide,b:Wide)->R<f64>{if b.is_empty(){return if a.is_empty(){Ok(0.)}else{Err("positive candidate against exact zero".into())}};if a.is_empty(){return Ok(-1.)}let d=a.exponent()-b.exponent();if d.abs()>1022{return Ok(if d<0{-1.}else{f64::INFINITY})}Ok(a.mantissa()/b.mantissa()*2f64.powi(d)-1.)}
pub fn fields(o:Owners)->[Tracked;13]{[o.n,o.u,o.qn,o.qe,o.red,o.outn,o.oute,o.a[0],o.a[1],o.a[2],o.b[0],o.b[1],o.b[2]]}
pub fn from_fields(a:[Tracked;13])->Owners{Owners{n:a[0],u:a[1],qn:a[2],qe:a[3],red:a[4],outn:a[5],oute:a[6],a:[a[7],a[8],a[9]],b:[a[10],a[11],a[12]]}}
pub fn photon_term(t:usize)->bool{[0,2,5,7,8,9].contains(&t)}
#[derive(Clone,Copy)]pub struct PhotonMeasure(pub Wide);
#[derive(Clone,Copy)]pub struct EtaWeight(pub f64);
impl PhotonMeasure{pub fn apply(self,o:Owners)->R<Owners>{o.weighted(Tracked::exact(self.0)).map_err(err)}}
impl EtaWeight{pub fn apply(self,o:Owners)->R<Owners>{o.weighted(Tracked::from_f64(self.0).map_err(err)?).map_err(err)}pub fn integrate_density(self,d:Wide)->R<PhotonMeasure>{Ok(PhotonMeasure(d.mul(w(self.0)?).map_err(err)?))}}

#[derive(Clone,Debug,Default)]pub struct Telemetry{pub live:usize,pub peak:usize,pub created:usize,pub retired:usize,pub counters:std::collections::BTreeMap<String,usize>,pub arrays:std::collections::BTreeMap<String,(usize,usize,usize)>}
thread_local!{static TELEMETRY:std::cell::RefCell<Telemetry>=std::cell::RefCell::new(Telemetry::default());}
pub struct SiteGuard(usize,p::SiteLease);
impl SiteGuard{pub fn new(n:usize)->R<Self>{let lease=p::reserve_site_capacity(n).map_err(err)?;TELEMETRY.with(|v|{let mut t=v.borrow_mut();if t.live+n>4096{return Err("concurrent site cap".into())}t.live+=n;t.created+=n;t.peak=t.peak.max(t.live);Ok(Self(n,lease))})}}
impl Drop for SiteGuard{fn drop(&mut self){TELEMETRY.with(|v|{let mut t=v.borrow_mut();t.live-=self.0;t.retired+=self.0;})}}
pub fn count(name:&str,n:usize){TELEMETRY.with(|v|*v.borrow_mut().counters.entry(name.into()).or_default()+=n)}
pub fn record_vec<T>(name:&str,a:&Vec<T>){TELEMETRY.with(|v|{let mut t=v.borrow_mut();let e=t.arrays.entry(name.into()).or_insert((0,0,std::mem::size_of::<T>()));e.0=e.0.max(a.len());e.1=e.1.max(a.capacity());})}
pub fn telemetry()->Telemetry{TELEMETRY.with(|v|v.borrow().clone())}
pub fn record_heap_bytes(name:&str,len:usize,cap:usize){TELEMETRY.with(|v|{let mut t=v.borrow_mut();let e=t.arrays.entry(name.into()).or_insert((0,0,1));e.0=e.0.max(len);e.1=e.1.max(cap);})}
pub fn record_charge_memory(charges:&[Charge]){let len=charges.iter().map(|c|c.lane.len()+c.boundary.len()+c.id.len()).sum();let cap=charges.iter().map(|c|c.lane.capacity()+c.boundary.capacity()+c.id.capacity()).sum();let lane=charges.first().map(|x|x.lane.as_str()).unwrap_or("empty");record_heap_bytes(&format!("loss_string_heap.{lane}"),len,cap);}

#[derive(Clone,Debug,PartialEq)]pub struct Charge{pub lane:String,pub transition:usize,pub boundary:String,pub id:String,pub term:usize,pub bound:Wide,pub coefficient:Wide,pub units:&'static str}
// Derived ordered keys preserve full coefficient-aware equality; no hash-only identity.
fn coefficient_key(mant:f64,exp:i32)->R<(u64,i32)>{if !mant.is_finite()||mant<0.{return Err("invalid charge coefficient key".into())}Ok((if mant==0.{0}else{mant.to_bits()},exp))}
#[derive(Clone,Debug,PartialEq,Eq,PartialOrd,Ord)]struct ChargeKey{lane:String,transition:usize,boundary:String,id:String,term:usize,coefficient:(u64,i32)}
impl ChargeKey{fn new(c:&Charge)->R<Self>{Ok(Self{lane:c.lane.clone(),transition:c.transition,boundary:c.boundary.clone(),id:c.id.clone(),term:c.term,coefficient:coefficient_key(c.coefficient.mantissa(),c.coefficient.exponent())?})}}
#[derive(Clone,Debug,Default,PartialEq)]pub struct Ledger{index:std::collections::BTreeSet<ChargeKey>,charges:Vec<Charge>,pub increments:Vec<[Wide;11]>,group_bounds:Vec<(Wide,Wide)>,covered:usize}
impl Ledger{
 pub fn charges(&self)->&Vec<Charge>{&self.charges}
 pub fn into_charges(self)->Vec<Charge>{self.charges}

 pub fn charge(&mut self,c:Charge)->R<()>{
  if c.term>=13||c.id.is_empty()||c.boundary.is_empty()||c.lane.is_empty(){return Err("unclassified loss provenance".into())}
  if c.units!=if photon_term(c.term){"photons/H"}else{"erg/H"}{return Err("loss units mismatch".into())}
  let key=ChargeKey::new(&c)?;if self.index.contains(&key){return Err("duplicate loss occurrence".into())}
  if !c.bound.is_empty(){if c.coefficient.is_empty(){return Err("positive loss with zero coefficient".into())}self.index.insert(key);self.charges.push(c);record_vec("historical_loss_records",&self.charges);record_charge_memory(&self.charges);}Ok(())
 }
 pub fn relabel_pending(&mut self,start:usize,lane:&str,transition:usize)->R<()>{
  if start<self.covered||start>self.charges.len()||lane.is_empty(){return Err("invalid charge relabel".into())}
  if start==self.charges.len(){return Ok(())}
  let mut index=self.index.clone();
  for c in &self.charges[start..]{if !index.remove(&ChargeKey::new(c)?){return Err("stale charge index".into())}}
  let mut replacements=Vec::with_capacity(self.charges.len()-start);
  for c in &self.charges[start..]{let mut replacement=c.clone();replacement.lane=lane.into();replacement.transition=transition;if !index.insert(ChargeKey::new(&replacement)?){return Err("duplicate loss occurrence during relabel".into())}replacements.push(replacement)}
  self.charges.splice(start..,replacements);self.index=index;Ok(())
 }
 #[cfg(test)]fn index_is_consistent(&self)->bool{self.charges.iter().map(ChargeKey::new).collect::<R<std::collections::BTreeSet<_>>>().is_ok_and(|x|x==self.index&&x.len()==self.charges.len())}
 pub fn canonical_restrict(&mut self,c:ClosureInput,a:f64,b:f64,s:f64,id:&str)->R<(Tracked,Tracked,f64)>{
  if !c.n.loss.is_empty(){return Err("historical loss is not closure amplitude uncertainty".into())}
  count("restriction_calls",1);let(n,m)=restrict(c,a,b).map_err(err)?;
  if n.value.is_empty()||m.value.is_empty(){return Err("empty or unpaired canonical restriction".into())}
  let factor=w(EPS)?.mul(Wide::from_log(-s).map_err(err)?).map_err(err)?;
  for(term,bound,coefficient,units)in[(0,n.loss,w(1.)?,"photons/H"),(1,m.loss,factor,"erg/H")]{self.charge(Charge{lane:"unit".into(),transition:self.increments.len(),boundary:"restriction-before-abscissa".into(),id:id.into(),term,bound,coefficient,units})?;}
  let eta=(m.value.mantissa()/n.value.mantissa()).ln()+(m.value.exponent()-n.value.exponent())as f64*std::f64::consts::LN_2;
  if !eta.is_finite()||eta<c.l||eta>c.r{return Err("invalid canonical moment abscissa".into())}
  let round=n.value.mul(Wide::from_log(eta).map_err(err)?).map_err(err)?;
  if rel(round,m.value)?.abs()>2e-12{return Err("restriction moment-abscissa roundtrip".into())}
  Ok((Tracked::exact(n.value),Tracked::exact(m.value),eta))
 }
 fn pending_totals(&self)->R<(Wide,Wide)>{let(mut n,mut e)=(Wide::ZERO,Wide::ZERO);for c in &self.charges[self.covered..]{let b=c.bound.upper_mul(c.coefficient).map_err(err)?;if photon_term(c.term){n=n.upper_add(b).map_err(err)?}else{e=e.upper_add(b).map_err(err)?}}Ok((n,e))}
 pub fn totals(&self)->R<(Wide,Wide)>{let(mut n,mut e)=self.pending_totals()?;for(a,b)in &self.group_bounds{n=n.upper_add(*a).map_err(err)?;e=e.upper_add(*b).map_err(err)?;}Ok((n,e))}
 pub fn commit(&mut self,inc:[Wide;11],charges:Vec<Charge>,admitted:bool)->R<()>{
  if !admitted||self.increments.len()>=4{return Err("private transaction gate rejected".into())}
  let mut candidate=self.clone();for c in charges{candidate.charge(c)?}let group=candidate.pending_totals()?;candidate.group_bounds.push(group);candidate.covered=candidate.charges.len();let(n,e)=candidate.totals()?;
  if !n.le(w(1e-20)?)||!e.le(w(1e-30)?){return Err("cumulative conservation loss cap".into())}
  candidate.increments.push(inc);record_vec("retained11_increments",&candidate.increments);record_vec("per_step_loss_groups",&candidate.group_bounds);*self=candidate;Ok(())
 }
}
pub fn sorted_sum(a:&[Tracked])->R<Tracked>{let mut idx:Vec<usize>=(0..a.len()).collect();record_vec("reduction_sort_indices",&idx);idx.sort_by(|i,j|a[*i].value.exponent().cmp(&a[*j].value.exponent()).then(a[*i].value.mantissa().total_cmp(&a[*j].value.mantissa())).then(i.cmp(j)));let mut sum=Tracked::empty();for i in idx{sum=sum.add(a[i]).map_err(err)?;}Ok(sum)}
pub fn sum_owners(a:&[Owners])->R<Owners>{let mut out=[Tracked::empty();13];for j in 0..13{let x:Vec<Tracked>=a.iter().map(|v|fields(*v)[j]).collect();record_vec("component_reduction_buffer",&x);out[j]=sorted_sum(&x)?;}Ok(from_fields(out))}
pub fn positive_difference(a:Wide,b:Wide)->R<Wide>{if a==b{return Ok(Wide::ZERO)}let(hi,lo)=if a.le(b){(b,a)}else{(a,b)};if lo.is_empty(){return Ok(hi)}let d=hi.exponent()-lo.exponent();if d>1022{return Ok(hi)}Wide::from_parts(hi.mantissa()-lo.mantissa()*2f64.powi(-d),hi.exponent()).map_err(err)}
fn signed_sum(a:&[f64])->f64{let(mut s,mut e)=(0.,0.);for &x in a{let t=s+x;let v=t-s;e+=(s-(t-v))+(x-v);s=t;}s+e}
pub fn residual(incoming:[Wide;2],outgoing:[Wide;2],inc:[Wide;11])->R<(f64,f64,Wide,Wide)>{
 let mut n=Vec::new();let mut e=Vec::new();let(mut bn,mut be)=(Wide::ZERO,Wide::ZERO);
 for(i,x,sgn)in [(0,incoming[0],-1.),(1,incoming[1],-1.),(0,outgoing[0],1.),(1,outgoing[1],1.)]{let(v,b)=x.readout().map_err(err)?;if i==0{n.push(sgn*v);bn=bn.upper_add(b).map_err(err)?}else{e.push(sgn*v);be=be.upper_add(b).map_err(err)?}}
 for(j,x)in inc.into_iter().enumerate(){let(v,b)=x.readout().map_err(err)?;let sgn=if j<2{-1.}else{1.};if photon_term(j+2){n.push(sgn*v);bn=bn.upper_add(b).map_err(err)?}else{e.push(sgn*v);be=be.upper_add(b).map_err(err)?}}
 record_vec("signed_number_audit_terms",&n);record_vec("signed_energy_audit_terms",&e);Ok((signed_sum(&n),signed_sum(&e),bn,be))
}
#[derive(Clone,Debug)]pub struct Panel{pub l:f64,pub r:f64,pub pair:MomentPair,pub closure:v2::Closure,pub front:bool,pub provenance:u32,pub incoming_loss_metadata:[Wide;2]}
impl Panel{
 pub fn from_owners(l:f64,r:f64,s:f64,o:Owners,front:bool,provenance:u32)->R<Self>{
  let _lease=SiteGuard::new(64)?;count("endpoint_fits",1);count("statistics_rules_upper",132);let ep=endpoint_pair(l,r,s,o,front).map_err(err)?;let pair=ep.pair.ok_or("empty panel requires explicit empty state")?;let(_,n,m)=pair.components();let closure=v2::reconstruct(l,r,n,m,front).map_err(err)?;
  let(mu,mut z,mut got)=(pair.normalized_mean().map_err(err)?,0.,0.);let nodes=v2::gauss(0.,1.,64);record_vec("closure_statistics_nodes",&nodes);for(y,q)in nodes{let f=q*(closure.beta*y-closure.beta.max(0.)).exp()*if front{1.-y}else{1.};z+=f;got+=f*((r-l)*y).exp_m1()/(r-l).exp_m1();}if(got/z-mu).abs()>5e-13{return Err("independent normalized closure moment gate".into())}
  let(_,mr)=v2::closure_moments(closure);if(mr/m-1.).abs()>3e-12{return Err("closure M reconstruction gate".into())}Ok(Self{l,r,pair,closure,front,provenance,incoming_loss_metadata:[ep.n_loss,ep.m_loss]})
 }
 pub fn density(&self,eta:f64)->R<Wide>{if eta<self.l||eta>=self.r{return Ok(Wide::ZERO)}let _lease=SiteGuard::new(64)?;count("density_statistics_rules",1);let v=v2::density_value(self.closure,eta);if !(v>0.){return Err("positive interior closure density lost".into())}Wide::from_parts(v,self.pair.components().0).map_err(err)}
 pub fn moments(&self)->R<[Wide;2]>{let(k,n,m)=self.pair.components();Ok([Wide::from_parts(n,k).map_err(err)?,Wide::from_parts(m,k).map_err(err)?])}
 pub fn split(&self,c:f64,s:f64)->R<(Self,Self)>{if !(c>self.l&&c<self.r){return Err("split outside support".into())}let mk=|a,b,front|->R<Self>{let(n,m)=restrict(ClosureInput{l:self.l,r:self.r,beta:self.closure.beta,front:self.front,n:Tracked::exact(self.moments()?[0])},a,b).map_err(err)?;if !n.loss.is_empty()||!m.loss.is_empty(){return Err("standalone split needs explicit loss booking".into())}let mut o=Owners::empty();o.n=n;o.u=m.scale(EPS*(-s).exp()).map_err(err)?;Self::from_owners(a,b,s,o,front,self.provenance)};Ok((mk(self.l,c,false)?,mk(c,self.r,self.front)?))}
 pub fn merge(a:&Self,b:&Self,s:f64)->R<Self>{if a.r!=b.l||a.front||a.provenance!=b.provenance{return Err("gap or incompatible merge provenance".into())}let am=a.moments()?;let bm=b.moments()?;let n=Tracked::exact(am[0]).add(Tracked::exact(bm[0])).map_err(err)?;let m=Tracked::exact(am[1]).add(Tracked::exact(bm[1])).map_err(err)?;if !n.loss.is_empty()||!m.loss.is_empty(){return Err("standalone merge needs explicit loss booking".into())}let mut o=Owners::empty();o.n=n;o.u=m.scale(EPS*(-s).exp()).map_err(err)?;Self::from_owners(a.l,b.r,s,o,b.front,a.provenance)}
}
pub fn start_energy(eta:f64,a:f64,b:f64)->R<(f64,bool)>{if b<=a{return Err("invalid anchored segment".into())}let(mut start,mut end)=(None,None);for c in [13.6f64,24.59,54.42]{let t=eta-c.ln();if a==t{start=Some(c)}if b==t{end=Some(c)}}let decay=(-(b-a)).exp();if let Some(c)=end{let e=c/decay;if e*decay!=c{return Err("exact event multiplication incompatibility".into())}if start.is_some_and(|v|v!=e){return Err("incompatible event anchors".into())}Ok((e,true))}else if let Some(c)=start{Ok((c,true))}else{Ok(((eta-a).exp(),false))}}
pub mod physics;
#[cfg(test)]#[path="../tests/controls.rs"]mod controls;

#[cfg(test)]#[path="../tests/optimization.rs"]mod optimization_controls;

#[path="panel_workers.rs"]mod workers;pub use workers::{panel_map_with,worker_count};
