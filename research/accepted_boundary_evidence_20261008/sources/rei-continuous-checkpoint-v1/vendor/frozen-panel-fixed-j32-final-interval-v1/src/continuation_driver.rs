//! Reload the admitted B128/m1 state and continue without replaying its first transition.
//! MODEL_UNRESOLVED; all new transactions remain private until every gate passes.
#[path="lib.rs"] mod bridge;
use bridge::*;
use bridge::physics::Frame;
#[path="durable.rs"]mod durable;
use std::fs::{File,OpenOptions};
use std::io::{BufReader,BufRead,BufWriter,Write};
use std::collections::BTreeMap;

#[path="study_rule.rs"] mod rule;
const NAMES:[&str;13]=["N","U","QN","QE","red","outN","outE","A_HI","A_HeI","A_HeII","B_HI","B_HeI","B_HeII"];
const D_NAMES:[&str;10]=["P.Gamma_HI","P.Gamma_HeI","P.Gamma_HeII","P.Hdot","H.Gamma_HI","H.Gamma_HeI","H.Gamma_HeII","H.Hdot","L1.N","L1.U"];
enum CsvOut{File(BufWriter<File>),Memory(Vec<u8>)}
impl Write for CsvOut{fn write(&mut self,b:&[u8])->std::io::Result<usize>{match self{Self::File(f)=>f.write(b),Self::Memory(v)=>{if v.len()+b.len()>1024*1024{return Err(std::io::Error::other("panel row buffer cap"))}v.extend_from_slice(b);Ok(b.len())}}}fn flush(&mut self)->std::io::Result<()>{match self{Self::File(f)=>f.flush(),Self::Memory(_)=>Ok(())}}}
struct Csv { out:CsvOut }
impl Csv {
 fn memory()->Self{Self{out:CsvOut::Memory(Vec::with_capacity(8192))}}
 fn rows(self)->Vec<u8>{if let CsvOut::Memory(v)=self.out{v}else{panic!("file CSV cannot drain as rows")}}
 fn drain(&mut self,rows:&[u8])->R<()>{self.out.write_all(rows).map_err(err)}
 fn new(path:&str)->R<Self>{let f=OpenOptions::new().write(true).create_new(true).open(path).map_err(err)?;let mut out=BufWriter::with_capacity(8192,f);writeln!(out,"kind,id,field,bits,exp").map_err(err)?;count("csv_buffer_capacity_bytes",8192);Ok(Self{out:CsvOut::File(out)})}
 fn scalar(&mut self,k:&str,id:&str,key:&str,x:f64)->R<()>{writeln!(self.out,"{k},{id},{key},{:016x},0",x.to_bits()).map_err(err)}
 fn wide(&mut self,k:&str,id:&str,key:&str,x:Wide)->R<()>{writeln!(self.out,"{k},{id},{key},{:016x},{}",x.mantissa().to_bits(),x.exponent()).map_err(err)}
 fn output(&mut self,k:&str,id:&str,key:&str,x:Tracked)->R<()>{let(v,b)=x.value.readout().map_err(err)?;self.wide(k,id,key,x.value)?;self.wide(k,id,&format!("{key}.loss"),x.loss)?;self.scalar(k,id,&format!("{key}.readout"),v)?;self.wide(k,id,&format!("{key}.readout_bound"),b)?;self.scalar(k,id,&format!("{key}.log"),x.value.log())}
 fn owners(&mut self,k:&str,id:&str,o:Owners)->R<()>{for(j,(key,x))in NAMES.into_iter().zip(fields(o)).enumerate(){if j>=2&&(k=="panel_owners"||k=="stock_density"){self.wide(k,id,key,x.value)?;self.wide(k,id,&format!("{key}.loss"),x.loss)?;}else{self.output(k,id,key,x)?;}}Ok(())}
 fn flush(&mut self)->R<()>{self.out.flush().map_err(err)}
}
fn canonical(o:Owners)->Owners{from_fields(fields(o).map(|x|Tracked::exact(x.value)))}
fn retained(o:Owners)->[Wide;11]{let a=fields(o);std::array::from_fn(|j|a[j+2].value)}
fn energy_factor(s:f64)->R<Wide>{w(EPS)?.mul(Wide::from_log(-s).map_err(err)?).map_err(err)}
fn charge(c:&mut Csv,ledger:&mut Ledger,lane:&str,boundary:&str,id:&str,term:usize,bound:Wide,coefficient:Wide)->R<()>{ledger.charge(Charge{lane:lane.into(),transition:lane.rsplit(':').next().and_then(|v|v.parse().ok()).unwrap_or(0),boundary:boundary.into(),id:id.into(),term,bound,coefficient,units:if photon_term(term){"photons/H"}else{"erg/H"}})?;if !bound.is_empty(){let key=format!("{lane}:{boundary}:{id}:term{term}");c.wide("loss_occurrence",&key,"unweighted_bound",bound)?;c.wide("loss_occurrence",&key,"physical_coefficient",coefficient)?;c.wide("loss_occurrence",&key,"dimensional_bound",bound.upper_mul(coefficient).map_err(err)?)?;}Ok(())}
fn emit_charges(c:&mut Csv,ledger:&Ledger)->R<()>{let used:usize=ledger.charges().iter().map(|x|x.lane.len()+x.boundary.len()+x.id.len()).sum();let cap:usize=ledger.charges().iter().map(|x|x.lane.capacity()+x.boundary.capacity()+x.id.capacity()).sum();let lane=ledger.charges().first().map(|x|x.lane.as_str()).unwrap_or("empty");println!("BUFFER {lane}.charge_strings used_bytes={used} allocated_capacity_bytes={cap} append_only_lane_hwm=true");for(i,x)in ledger.charges().iter().enumerate(){let id=format!("{}:{}:{}:{}:{}",x.lane,x.transition,x.boundary,x.id,i);c.scalar("charge",&id,"term",x.term as f64)?;c.wide("charge",&id,"unweighted_bound",x.bound)?;c.wide("charge",&id,"physical_coefficient",x.coefficient)?;c.wide("charge",&id,"dimensional_bound",x.bound.upper_mul(x.coefficient).map_err(err)?)?;}Ok(())}
fn require_relative(c:&mut Csv,id:&str,a:Owners,b:Owners,tol:f64)->R<()>{let mut fail=None;for(j,(x,y))in fields(a).into_iter().zip(fields(b)).enumerate(){let d=if y.value.is_empty(){if x.value.is_empty(){0.}else{f64::INFINITY}}else{rel(x.value,y.value)?.abs()};c.scalar("comparison",id,NAMES[j],d)?;c.wide("comparison",id,&format!("{}.denominator",NAMES[j]),y.value)?;if d>tol&&fail.is_none(){fail=Some(format!("{id} {} relative={d:.17e} tolerance={tol:.1e}",NAMES[j]));}}if let Some(e)=fail{Err(e)}else{Ok(())}}
fn compare_panel(c:&mut Csv,id:&str,a:Owners,b:Owners)->R<()>{for(j,(x,y))in fields(a).into_iter().zip(fields(b)).enumerate(){let d=if y.value.is_empty(){if x.value.is_empty(){0.}else{f64::INFINITY}}else{rel(x.value,y.value)?.abs()};c.scalar("panel_comparison",id,NAMES[j],d)?;c.wide("panel_comparison",id,&format!("{}.denominator",NAMES[j]),y.value)?;}Ok(())}
fn physical_agreement(c:&mut Csv,id:&str,a:Wide,b:Wide,abs:f64,factor:f64)->R<()>{let d=positive_difference(a,b)?;let allowance=w(abs*factor)?.add(b.mul(w(1e-3*factor)?).map_err(err)?).map_err(err)?.0;c.wide("physical_comparison",id,"difference",d)?;c.wide("physical_comparison",id,"reference",b)?;c.wide("physical_comparison",id,"allowance",allowance)?;if d.le(allowance){Ok(())}else{Err(format!("physical comparison {id}"))}}
fn inventory(c:&mut Csv,id:&str,panels:&[Panel],s:f64)->R<()>{c.scalar("inventory",id,"s",s)?;c.scalar("inventory",id,"EPS",EPS)?;for(i,p)in panels.iter().enumerate(){let[n,m]=p.moments()?;c.wide("inventory",id,&format!("p{i}.N"),n)?;c.wide("inventory",id,&format!("p{i}.M"),m)?;}Ok(())}
fn stock_cache(panels:&[Panel],s:f64)->R<([Wide;2],[Wide;2])>{let mut ns=Vec::with_capacity(panels.len());let mut ms=Vec::with_capacity(panels.len());for p in panels{let[n,m]=p.moments()?;ns.push(Tracked::exact(n));ms.push(Tracked::exact(m));}record_vec("driver.stock_number_audit",&ns);record_vec("driver.stock_comoving_audit",&ms);let n=sorted_sum(&ns)?;let m=sorted_sum(&ms)?;let u=m.mul(Tracked::exact(energy_factor(s)?)).map_err(err)?;Ok(([n.value,u.value],[n.loss,u.loss]))}
fn closure_audit(c:&mut Csv,id:&str,p:&Panel,carried:Owners,direct_m:Wide,s:f64)->R<()>{
 let _lease=SiteGuard::new(32)?;let nodes=v2::gauss(p.l,p.r,32);record_vec("driver.closure_reintegration_nodes",&nodes);let mut nv=Vec::with_capacity(32);let mut mv=Vec::with_capacity(32);
 for(eta,q)in nodes{let n=Tracked::exact(p.density(eta)?).scale(q).map_err(err)?;nv.push(n);mv.push(n.mul(Tracked::exact(Wide::from_log(eta).map_err(err)?)).map_err(err)?);}
 record_vec("driver.closure_reintegration_N",&nv);record_vec("driver.closure_reintegration_M",&mv);let[n,m]=p.moments()?;let nr=sorted_sum(&nv)?;let mr=sorted_sum(&mv)?;let ur=m.mul(energy_factor(s)?).map_err(err)?;
 for(key,x)in [("stored.N",n),("stored.M",m),("carried.U",carried.u.value),("recovered.U",ur),("direct.exp_eta_N",direct_m)]{c.output("panel",id,key,Tracked::exact(x))?;}
 c.output("panel",id,"reintegrated.N",nr)?;c.output("panel",id,"reintegrated.M",mr)?;
 for(key,x,y,tol)in [("N_reintegration",nr.value,n,3e-12),("M_reintegration",mr.value,m,3e-12),("U_roundtrip",ur,carried.u.value,2e-12),("direct_M_discrepancy",direct_m,m,2e-12)]{let d=rel(x,y)?.abs();c.scalar("panel",id,key,d)?;if d>tol{return Err(format!("{id} {key} {d:.17e}"));}}
 c.scalar("panel",id,"L",p.l)?;c.scalar("panel",id,"R",p.r)?;c.scalar("panel",id,"beta",p.closure.beta)?;c.scalar("panel",id,"front",p.front as u8 as f64)?;c.scalar("panel",id,"provenance",p.provenance as f64)?;
 let(logn,logm)=p.pair.logs();if !logn.is_finite()||!logm.is_finite(){return Err("positive panel lost finite logs".into());}c.scalar("panel",id,"canonical_logN",logn)?;c.scalar("panel",id,"canonical_logM",logm)?;Ok(())
}
#[derive(Clone)]
struct Lane { panels:Vec<Owners>,direct:Vec<Wide>,total:Owners,ledger:Ledger,diag:[Tracked;10] }
// Each lane has only one live node batch. After weighted terminal losses are
// captured, every node owner is exact canonical before deterministic reduction.
fn source_lane(frame:&Frame,c:&mut Csv,lane:&str,order:usize,start:usize,end:usize,edges:&[f64],mut candidate:Option<&mut Vec<Panel>>,projection:Option<&[Panel]>)->R<Lane>{
 if candidate.is_none(){return source_lane_parallel(frame,c,lane,order,start,end,edges,projection)}

 let mut directs=Vec::with_capacity(edges.len()-1);let mut summaries=Vec::with_capacity(edges.len()-1);let mut diagnostic_panels=Vec::<[Tracked;10]>::with_capacity(edges.len()-1);let mut ledger=Ledger::default();
 record_vec(&format!("driver.{lane}.panel_owner_summaries"),&summaries);record_vec(&format!("driver.{lane}.diagnostic_panel_summaries"),&diagnostic_panels);
 for(i,ab)in edges.windows(2).enumerate(){
  let _sites=SiteGuard::new(order)?;let nodes=v2::gauss(ab[0],ab[1],order);record_vec("driver.current_nodes",&nodes);count("quadrature_sites_created",nodes.len());
  let mut values=Vec::with_capacity(order);let mut direct_m=Vec::with_capacity(order);let mut diagnostic_values=Vec::<[Tracked;10]>::with_capacity(if projection.is_some(){order}else{0});
  record_vec("driver.current_site_owners",&values);record_vec("driver.current_direct_M",&direct_m);record_vec("driver.current_diagnostic_values",&diagnostic_values);
  for(j,(eta,q))in nodes.into_iter().enumerate(){
   let id=format!("{lane}:p{i}:q{j}");if !(eta>ab[0]&&eta<ab[1]&&q>0.){return Err(format!("invalid positive node {id}"));}
   if i>=182{c.scalar("node",&id,"eta",eta)?;c.scalar("node",&id,"eta_weight",q)?;}else if j==0{c.scalar("node_geometry_reuse_from_first_interval",&format!("{lane}:p{i}"),"panel_index",i as f64)?;c.scalar("node_geometry_reuse_from_first_interval",&format!("{lane}:p{i}"),"gauss_order",order as f64)?;}
   let raw=frame.replay(eta,start,end,1,Tracked::empty(),true).map_err(|e|format!("{id}: {e}"))?;
   let coefficient=w(q)?;let weighted=EtaWeight(q).apply(raw)?;
   // Raw provenance and its physical geometric coefficient are retained. The
   // terminal bound is charged once here, never again as panel input uncertainty.
   for(term,x)in fields(raw).into_iter().enumerate(){charge(c,&mut ledger,lane,"terminal-point",&format!("p{i}:q{j}"),term,x.loss,coefficient)?;}
   let exact=canonical(weighted);direct_m.push(exact.n.mul(Tracked::exact(Wide::from_log(eta).map_err(err)?)).map_err(err)?);
   if let Some(ps)=projection{let p=ps.get(i).ok_or("missing diagnostic panel")?;let fp=p.density(eta)?;let fh=raw.n.value;let rates=frame.diagnostic_rates(eta,frame.times[4*end])?;let mut d=[Tracked::empty();10];for k in 0..4{d[k]=Tracked::exact(fp).scale(rates[k]).map_err(err)?.scale(q).map_err(err)?;d[k+4]=Tracked::exact(fh).scale(rates[k]).map_err(err)?.scale(q).map_err(err)?;}let df=positive_difference(fp,fh)?;d[8]=Tracked::exact(df).scale(q).map_err(err)?;d[9]=d[8].scale(EPS*(eta-frame.times[4*end]).exp()).map_err(err)?;diagnostic_values.push(d);}
   values.push(exact);record_vec("driver.current_site_owners",&values);record_vec("driver.current_direct_M",&direct_m);record_vec("driver.current_diagnostic_values",&diagnostic_values);
  }
  let panel_total=sum_owners(&values)?;let id=format!("{lane}:p{i}");c.owners("panel_owners",&id,panel_total)?;
  let direct=sorted_sum(&direct_m)?;directs.push(direct.value);record_vec("driver.direct_panel_M",&directs);
  if let Some(ref mut ps)=candidate{
   let front=ab[1]==*edges.last().ok_or("empty geometry")?;let endpoint=endpoint_pair(ab[0],ab[1],frame.times[4*end],panel_total,front).map_err(|e|format!("{id} endpoint_pair {e}; L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()))?;
   charge(c,&mut ledger,lane,"endpoint-N",&format!("p{i}"),0,endpoint.n_loss,w(1.)?)?;
   charge(c,&mut ledger,lane,"endpoint-M",&format!("p{i}"),1,endpoint.m_loss,energy_factor(frame.times[4*end])?)?;
   let p=Panel::from_owners(ab[0],ab[1],frame.times[4*end],panel_total,front,1).map_err(|e|format!("{id} reconstruction {e}; L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()))?;
   closure_audit(c,&id,&p,panel_total,direct.value,frame.times[4*end])?;ps.push(p);record_vec("driver.private_candidate_panels",ps);
  }else{for term in 0..2{let x=fields(panel_total)[term];charge(c,&mut ledger,lane,"panel-stock-construction",&format!("p{i}"),term,x.loss,w(1.)?)?;}}
  for(term,x)in fields(panel_total).into_iter().enumerate().skip(2){charge(c,&mut ledger,lane,"panel-owner-construction",&format!("p{i}"),term,x.loss,w(1.)?)?;}
  summaries.push(canonical(panel_total));record_vec(&format!("driver.{lane}.panel_owner_summaries"),&summaries);
  if projection.is_some(){let mut d=[Tracked::empty();10];for k in 0..10{let v:Vec<Tracked>=diagnostic_values.iter().map(|x|x[k]).collect();record_vec("driver.diagnostic_component_buffer",&v);d[k]=sorted_sum(&v)?;if order==16{c.wide("panel_diagnostic",&id,D_NAMES[k],d[k].value)?;c.wide("panel_diagnostic",&id,&format!("{}.loss",D_NAMES[k]),d[k].loss)?;}else{c.output("panel_diagnostic",&id,D_NAMES[k],d[k])?;}}c.scalar("panel_diagnostic",&id,"normalized_local_photon_L1",if panel_total.n.value.is_empty(){0.}else{ratio(d[8].value,panel_total.n.value)?})?;c.scalar("panel_diagnostic",&id,"normalized_local_energy_L1",if panel_total.u.value.is_empty(){0.}else{ratio(d[9].value,panel_total.u.value)?})?;diagnostic_panels.push(d);record_vec(&format!("driver.{lane}.diagnostic_panel_summaries"),&diagnostic_panels);}
  count("quadrature_sites_retired",order);
 }
 let total=sum_owners(&summaries)?;
 // The 11-owner reduction becomes an authoritative increment, so only these
 // newly lost fields are committed. N/U reduction is a temporary stock cache.
 for(term,x)in fields(total).into_iter().enumerate().skip(2){charge(c,&mut ledger,lane,"retained11-reduction","base0",term,x.loss,w(1.)?)?;}
 let mut diag=[Tracked::empty();10];for k in 0..10{let v:Vec<Tracked>=diagnostic_panels.iter().map(|x|x[k]).collect();record_vec("driver.global_diagnostic_component",&v);diag[k]=sorted_sum(&v)?;}
 c.owners("global_owners",lane,total)?;emit_charges(c,&ledger)?;record_vec(&format!("driver.{lane}.charges()"),&ledger.charges());c.flush()?;
 Ok(Lane{panels:summaries,direct:directs,total,ledger,diag})
}
fn ratio(a:Wide,b:Wide)->R<f64>{if a.is_empty(){Ok(0.)}else if b.is_empty(){Ok(f64::INFINITY)}else{Ok(rel(a,b)?+1.)}}
fn heat(c:&mut Csv,id:&str,o:Owners)->R<Wide>{let threshold=rei_microphysics::HHeModel::controlled_fixture().threshold_ev;let mut terms=Vec::with_capacity(3);for i in 0..3{let binding=o.a[i].value.mul(w(EPS*threshold[i])?).map_err(err)?;if !binding.le(o.b[i].value){return Err(format!("negative shared path heat species {i}"));}let x=positive_difference(o.b[i].value,binding)?;c.wide("path_heat",id,&format!("species{i}"),x)?;terms.push(Tracked::exact(x));}record_vec("driver.path_heat_terms",&terms);let total=sorted_sum(&terms)?;c.output("path_heat",id,"erg_per_H",total)?;Ok(total.value)}
fn local_row(c:&mut Csv,id:&str,incoming:[Wide;2],outgoing:[Wide;2],inc:[Wide;11],r:(f64,f64,Wide,Wide),loss:(Wide,Wide))->R<()>{for(key,x)in [("in.N",incoming[0]),("in.U",incoming[1]),("out.N",outgoing[0]),("out.U",outgoing[1])]{c.wide("local",id,key,x)?;}for(key,x)in NAMES[2..].iter().zip(inc){c.wide("local",id,key,x)?;}for(key,x)in [("rN",r.0),("rE",r.1)]{c.scalar("local",id,key,x)?;}for(key,x)in [("bN",r.2),("bE",r.3),("lossN",loss.0),("lossE",loss.1)]{c.wide("local",id,key,x)?;}Ok(())}
fn gate_budget(c:&mut Csv,id:&str,r:(f64,f64,Wide,Wide),loss:(Wide,Wide),inc:[Wide;11])->R<()>{let qn=inc[0].readout().map_err(err)?.0;let qe=inc[1].readout().map_err(err)?.0;let bn=r.2.upper_add(loss.0).map_err(err)?;let be=r.3.upper_add(loss.1).map_err(err)?;c.scalar("budget",id,"rN",r.0)?;c.scalar("budget",id,"rE",r.1)?;c.wide("budget",id,"temporary_N",r.2)?;c.wide("budget",id,"temporary_E",r.3)?;c.wide("budget",id,"committed_N",loss.0)?;c.wide("budget",id,"committed_E",loss.1)?;if !admit(r.0,bn,1e-10*qn.max(1e-10),1e-20).map_err(err)?||!admit(r.1,be,1e-10*qe.max(1e-20),1e-30).map_err(err)?{return Err(format!("{id} complete residual/loss/audit gate"));}Ok(())}
fn witness(frame:&Frame,panels:&[Panel],c:&mut Csv,end:usize,reverse:bool)->R<()>{let l=frame.times[0]+frame.cfg.source.energy_min_ev.ln();let mut points=[("source_off",l+1e-5),("lower_u1e-7",l+1e-7),("lower_u1e-6",l+1e-6)];if reverse{points.reverse();}for(name,eta)in points{let id=format!("{}:{name}",if reverse{"reversed"}else{"forward"});let id=format!("k{end}:{id}");let h=frame.replay(eta,0,end,1,Tracked::empty(),true)?;let p=panels.iter().find(|p|eta>=p.l&&eta<p.r).ok_or("witness outside retained support")?;let f=p.density(eta)?;let u=f.mul(w(EPS*(eta-frame.times[4*end]).exp())?).map_err(err)?;c.scalar("witness",&id,"eta",eta)?;c.output("witness",&id,"H.f",h.n)?;c.output("witness",&id,"H.U",h.u)?;c.output("witness",&id,"P.f",Tracked::exact(f))?;c.output("witness",&id,"P.U",Tracked::exact(u))?;c.scalar("witness",&id,"log_f_defect",f.log()-h.n.value.log())?;c.scalar("witness",&id,"local.L",p.l)?;c.scalar("witness",&id,"local.R",p.r)?;let[n,m]=p.moments()?;c.wide("witness",&id,"local.N",n)?;c.wide("witness",&id,"local.M",m)?;}
 let p=panels.last().ok_or("no frontier panel")?;let f=p.density(p.r)?;c.wide("front_trace",&format!("k{end}:{}",if reverse{"reversed"}else{"forward"}),"density",f)?;if !p.front||!f.is_empty(){return Err("front trace or tag gate".into());}Ok(())}
fn snapshot(panels:&[Panel],ledger:&Ledger)->u64{use std::hash::{Hash,Hasher};let mut h=std::collections::hash_map::DefaultHasher::new();for p in panels{p.l.to_bits().hash(&mut h);p.r.to_bits().hash(&mut h);let(k,n,m)=p.pair.components();k.hash(&mut h);n.to_bits().hash(&mut h);m.to_bits().hash(&mut h);p.closure.beta.to_bits().hash(&mut h);p.closure.l.to_bits().hash(&mut h);p.closure.r.to_bits().hash(&mut h);p.closure.n.to_bits().hash(&mut h);p.closure.front.hash(&mut h);let(ln,lm)=p.pair.logs();ln.to_bits().hash(&mut h);lm.to_bits().hash(&mut h);for x in p.incoming_loss_metadata{x.mantissa().to_bits().hash(&mut h);x.exponent().hash(&mut h);}p.front.hash(&mut h);p.provenance.hash(&mut h);}for inc in &ledger.increments{for x in inc{x.mantissa().to_bits().hash(&mut h);x.exponent().hash(&mut h);}}for x in ledger.charges(){x.lane.hash(&mut h);x.transition.hash(&mut h);x.boundary.hash(&mut h);x.id.hash(&mut h);x.term.hash(&mut h);x.bound.mantissa().to_bits().hash(&mut h);x.bound.exponent().hash(&mut h);x.coefficient.mantissa().to_bits().hash(&mut h);x.coefficient.exponent().hash(&mut h);}h.finish()}

#[derive(Clone,Copy)]struct Saved{bits:u64,exp:i32}
impl Saved{fn f(self)->f64{f64::from_bits(self.bits)}fn wide(self)->R<Wide>{let x=Wide::from_parts(self.f(),self.exp).map_err(err)?;if x.mantissa().to_bits()!=self.bits||x.exponent()!=self.exp{return Err("noncanonical persisted Wide".into())}Ok(x)}}
type Record=BTreeMap<String,Saved>;
fn saved(r:&Record,key:&str)->R<Saved>{r.get(key).copied().ok_or_else(||format!("missing saved {key}"))}
fn load(frame:&Frame,c:&mut Csv,oracle:&mut Csv)->R<(Vec<Panel>,Ledger)>{
 let mut panels:BTreeMap<usize,Record>=BTreeMap::new();let mut charges:BTreeMap<String,Record>=BTreeMap::new();let mut metadata:BTreeMap<usize,[Wide;2]>=BTreeMap::new();
 for line in BufReader::new(File::open("results/physical.csv").map_err(err)?).lines().skip(1){let line=line.map_err(err)?;let a:Vec<_>=line.split(',').collect();if a.len()!=5{return Err("malformed persisted row".into())}let v=Saved{bits:u64::from_str_radix(a[3],16).map_err(err)?,exp:a[4].parse().map_err(err)?};
  if a[0]=="panel"&&a[1].starts_with("Qhi16:p"){let i=a[1][7..].parse().map_err(err)?;if ["stored.N","stored.M","L","R","beta","front","provenance","canonical_logN","canonical_logM"].contains(&a[2]){panels.entry(i).or_default().insert(a[2].into(),v);}}
  if a[0]=="panel_owners"&&a[1].starts_with("Qhi16:p")&&["N.loss","U.loss"].contains(&a[2]){let i=a[1][7..].parse().map_err(err)?;metadata.entry(i).or_insert([Wide::ZERO;2])[if a[2]=="N.loss"{0}else{1}]=v.wide()?;}
  if a[0]=="charge"&&a[1].starts_with("Qhi16:"){charges.entry(a[1].into()).or_default().insert(a[2].into(),v);}
 }
 if panels.is_empty()||panels.len()>256{return Err("invalid accepted panel count".into())}let mut accepted=Vec::with_capacity(256);
 for(i,r)in panels{if i!=accepted.len(){return Err("noncontiguous accepted panel records".into())}let l=saved(&r,"L")?.f();let rr=saved(&r,"R")?.f();let n=saved(&r,"stored.N")?.wide()?;let m=saved(&r,"stored.M")?.wide()?;let k=n.exponent().max(m.exponent());let ns=n.mantissa()*2f64.powi(n.exponent()-k);let ms=m.mantissa()*2f64.powi(m.exponent()-k);let front=saved(&r,"front")?.f()==1.;let pair={let _lease=SiteGuard::new(64)?;count("reload_pair_validations",1);MomentPair::new(l,rr,k,ns,ms,front).map_err(err)?};let log=pair.logs();if log.0.to_bits()!=saved(&r,"canonical_logN")?.bits||log.1.to_bits()!=saved(&r,"canonical_logM")?.bits{return Err("reload changed canonical logs".into())}let raw=metadata.get(&i).ok_or("missing saved input loss metadata")?;
  // endpoint_pair multiplies loss with ordinary Tracked::mul's exact coefficient
  // and upward bound, in the same two operations used during the accepted fit.
  let restored_m_loss=Tracked{value:Wide::ZERO,loss:raw[1]}.mul(Tracked::exact(Wide::from_log(frame.times[4]).map_err(err)?)).map_err(err)?.scale(1./EPS).map_err(err)?.loss;
  let p=Panel{l,r:rr,pair,closure:v2::Closure{l,r:rr,n:ns,beta:saved(&r,"beta")?.f(),front},front,provenance:saved(&r,"provenance")?.f()as u32,incoming_loss_metadata:[raw[0],restored_m_loss]};if p.moments()!=Ok([n,m]){return Err("reload changed canonical moment bits".into())}accepted.push(p);
 }
 record_vec("driver.loaded_old_panels",&accepted);let mut increment=[Wide::ZERO;11];let mut got=[false;11];
 for line in BufReader::new(File::open("results/physical_oracle.csv").map_err(err)?).lines().skip(1){let line=line.map_err(err)?;let a:Vec<_>=line.split(',').collect();if a.len()!=5{return Err("malformed first oracle row".into())}if a[0]=="increment"&&a[1]=="B128_m1:0"{let j=NAMES[2..].iter().position(|x|*x==a[2]).ok_or("unknown retained owner")?;increment[j]=Saved{bits:u64::from_str_radix(a[3],16).map_err(err)?,exp:a[4].parse().map_err(err)?}.wide()?;got[j]=true;}else if !(a[0]=="global"||(a[0]=="inventory"&&a[1]=="B128_m1:final")){writeln!(oracle.out,"{line}").map_err(err)?;}}
 if !got.into_iter().all(|x|x){return Err("missing first canonical increment".into())}let mut ledger=Ledger::default();let mut restored=Vec::with_capacity(charges.len());
 for(id,r)in charges{let a:Vec<_>=id.split(':').collect();if a.len()<5{return Err("invalid persisted charge provenance".into())}let term=saved(&r,"term")?.f()as usize;let bound=saved(&r,"unweighted_bound")?.wide()?;let coefficient=saved(&r,"physical_coefficient")?.wide()?;if bound.upper_mul(coefficient).map_err(err)?!=saved(&r,"dimensional_bound")?.wide()?{return Err("persisted dimensional charge mismatch".into())}restored.push((a[a.len()-1].parse::<usize>().map_err(err)?,Charge{lane:a[0].into(),transition:a[1].parse().map_err(err)?,boundary:a[2].into(),id:a[3..a.len()-1].join(":"),term,bound,coefficient,units:if photon_term(term){"photons/H"}else{"erg/H"}}));}
 // Restore append order from the recorded terminal index, not lexical panel order.
 restored.sort_by_key(|x|x.0);for (i,x) in restored.iter().enumerate(){if x.0!=i{return Err("noncontiguous charge ordinal".into())}}
 ledger.commit(increment,restored.into_iter().map(|x|x.1).collect(),true)?;c.scalar("reload","accepted_first","panels",accepted.len()as f64)?;c.scalar("reload","accepted_first","increments",ledger.increments.len()as f64)?;inventory(c,"loaded:first",&accepted,frame.times[4])?;println!("LOADED_FIRST_STATE_CANONICAL_BITS=PASS; FIRST_HISTORY_NOT_REPLAYED");Ok((accepted,ledger))
}

fn stock_rule(frame:&Frame,c:&mut Csv,old:&[Panel],edges:&[f64],k:usize,jcount:usize)->R<Lane>{
 let lane=format!("stockJ{jcount}:{k}");let mut ledger=Ledger::default();let mut panels=Vec::with_capacity(edges.len()-1);let mut direct=Vec::with_capacity(edges.len()-1);
 let results=panel_map_with(worker_count(),edges.len()-1,|i|{let ab=&edges[i..i+2];let mut csv=Csv::memory();let c=&mut csv;let mut ledger=Ledger::default();let mut panels=Vec::with_capacity(1);let mut direct=Vec::with_capacity(1);
let _batch_lease=SiteGuard::new(2*jcount)?;let mut values=Vec::with_capacity(jcount);let mut ms=Vec::with_capacity(jcount);
  for(pidx,p)in old.iter().enumerate(){let l=ab[0].max(p.l);let r=ab[1].min(p.r);if r<=l{continue}for j in 0..jcount{let(a,b)=rule::interval(l,r,j,jcount)?;let id=format!("p{pidx}:dst{i}:j{j}");let before=ledger.charges().len();let(n,m,eta)=ledger.canonical_restrict(ClosureInput{l:p.l,r:p.r,beta:p.closure.beta,front:p.front,n:Tracked::exact(p.moments()?[0])},a,b,frame.times[4*k],&id)?;ledger.relabel_pending(before,&lane,k)?;if !(eta>=a && eta<=b && eta.is_finite()){return Err("stock abscissa outside declared subcell".into())}let _lease=SiteGuard::new(1)?;c.scalar("stock_node",&format!("{lane}:{id}"),"eta",eta)?;c.wide("stock_node",&format!("{lane}:{id}"),"nJ",n.value)?;c.wide("stock_node",&format!("{lane}:{id}"),"mJ",m.value)?;let raw=frame.replay(eta,k,k+1,1,Tracked::from_f64(1.).map_err(err)?,false)?;for(t,x)in fields(raw).into_iter().enumerate(){charge(c,&mut ledger,&lane,"terminal-unit-stock",&id,t,x.loss,n.value)?;}let exact=canonical(PhotonMeasure(n.value).apply(raw)?);ms.push(exact.n.mul(Tracked::exact(Wide::from_log(eta).map_err(err)?)).map_err(err)?);values.push(exact);count("stock_sites_created",1);count("stock_sites_retired",1);}}
  record_vec("driver.stock_current_nodes",&values);record_vec("driver.stock_current_direct_M",&ms);let total=sum_owners(&values)?;for(t,x)in fields(total).into_iter().enumerate(){charge(c,&mut ledger,&lane,"stock-panel-reduction",&format!("p{i}"),t,x.loss,w(1.)?)?;}panels.push(canonical(total));direct.push(sorted_sum(&ms)?.value);record_vec("driver.stock_panel_owners",&panels);record_vec("driver.stock_panel_direct_M",&direct);
 
 Ok((panels[0],direct[0],ledger.into_charges(),csv.rows()))})?;
 for(owner,m,charges,rows)in results{c.drain(&rows)?;for ch in charges{ledger.charge(ch)?}panels.push(owner);direct.push(m)}
 let total=sum_owners(&panels)?;emit_charges(c,&ledger)?;Ok(Lane{panels,direct,total,ledger,diag:[Tracked::empty();10]})
}
fn stock_controls(frame:&Frame,c:&mut Csv,old:&[Panel],qhi:&Lane,k:usize)->R<()>{
 let mut a=Vec::with_capacity(old.len());let mut b=Vec::with_capacity(old.len());
 let results=panel_map_with(worker_count(),old.len(),|i|{let p=&old[i];let mut csv=Csv::memory();let c=&mut csv;let mut a=Vec::with_capacity(1);let mut b=Vec::with_capacity(1);
let g16=frame.stock_density_control(p,k,1,16)?;let g32=frame.stock_density_control(p,k,1,32)?;c.owners("stock_density",&format!("k{k}:p{i}:G16"),g16)?;c.owners("stock_density",&format!("k{k}:p{i}:G32"),g32)?;compare_panel(c,&format!("stock_G16_G32:k{k}:p{i}"),g16,g32)?;compare_panel(c,&format!("stock_J32_G32:k{k}:p{i}"),qhi.panels[i],g32)?;
  for order in [16,32]{let _lease=SiteGuard::new(order)?;let nodes=v2::gauss(p.l,p.r,order);let mut ns=Vec::with_capacity(order);let mut us=Vec::with_capacity(order);for(eta,q)in nodes{let n=Tracked::exact(p.density(eta)?).scale(q).map_err(err)?;ns.push(n);us.push(n.scale(EPS*(eta-frame.times[4*k]).exp()).map_err(err)?);}let n=sorted_sum(&ns)?;let u=sorted_sum(&us)?;let pn=p.moments()?[0];let pu=p.moments()?[1].mul(energy_factor(frame.times[4*k])?).map_err(err)?;let id=format!("k{k}:p{i}:G{order}");c.output("incoming_density_control",&id,"quadrature.N",n)?;c.output("incoming_density_control",&id,"quadrature.U",u)?;c.wide("incoming_density_control",&id,"canonical.N",pn)?;c.wide("incoming_density_control",&id,"canonical.U",pu)?;c.scalar("incoming_density_control",&id,"relative.N",rel(n.value,pn)?.abs())?;c.scalar("incoming_density_control",&id,"relative.U",rel(u.value,pu)?.abs())?;record_vec("driver.incoming_density_N",&ns);record_vec("driver.incoming_density_U",&us);}
  a.push(canonical(g16));b.push(canonical(g32));record_vec("driver.stock_control_G16",&a);record_vec("driver.stock_control_G32",&b);
 
 Ok((a[0],b[0],csv.rows()))})?;
 for(x,y,rows)in results{c.drain(&rows)?;a.push(x);b.push(y)}
 require_relative(c,&format!("stock_global_G16_G32:k{k}"),sum_owners(&a)?,sum_owners(&b)?,1e-6)?;require_relative(c,&format!("stock_global_J32_G32:k{k}"),qhi.total,sum_owners(&b)?,1e-6)?;println!("BASE{k}_INITIAL_STOCK_CONTROLS=PASS");Ok(())
}
fn combine(frame:&Frame,c:&mut Csv,stock:Lane,source:Lane,edges:&[f64],k:usize,high:bool,mut candidate:Option<&mut Vec<Panel>>)->R<Lane>{let lane=format!("{}:{k}",if high{"Qhi16"}else{"Qlo8"});let mut ledger=stock.ledger;for ch in source.ledger.into_charges(){if ch.boundary!="retained11-reduction"{ledger.charge(ch)?;}}let mut panels=Vec::with_capacity(edges.len()-1);let mut direct=Vec::with_capacity(edges.len()-1);
 for(i,ab)in edges.windows(2).enumerate(){let o=sum_owners(&[stock.panels[i],source.panels[i]])?;let dm=sorted_sum(&[Tracked::exact(stock.direct[i]),Tracked::exact(source.direct[i])])?;let id=format!("{lane}:p{i}");c.owners("panel_owners",&id,o)?;
  if let Some(ref mut ps)=candidate{let front=ab[1]==*edges.last().ok_or("empty destination")?;let ep=endpoint_pair(ab[0],ab[1],frame.times[4*(k+1)],o,front).map_err(|e|format!("{id} endpoint: {e}"))?;charge(c,&mut ledger,&lane,"endpoint-N",&format!("p{i}"),0,ep.n_loss,w(1.)?)?;charge(c,&mut ledger,&lane,"endpoint-M",&format!("p{i}"),1,ep.m_loss,energy_factor(frame.times[4*(k+1)])?)?;let p=Panel::from_owners(ab[0],ab[1],frame.times[4*(k+1)],o,front,(k+1)as u32).map_err(|e|format!("{id} fit: {e}"))?;closure_audit(c,&id,&p,o,dm.value,frame.times[4*(k+1)])?;ps.push(p);record_vec("driver.private_candidate_panels",ps);}else{for(t,x)in fields(o).into_iter().enumerate().take(2){charge(c,&mut ledger,&lane,"panel-stock-construction",&format!("p{i}"),t,x.loss,w(1.)?)?;}}
  for(t,x)in fields(o).into_iter().enumerate().skip(2){charge(c,&mut ledger,&lane,"panel-owner-construction",&format!("p{i}"),t,x.loss,w(1.)?)?;}panels.push(canonical(o));direct.push(dm.value);
 }
 let total=sum_owners(&panels)?;for(t,x)in fields(total).into_iter().enumerate().skip(2){charge(c,&mut ledger,&lane,"retained11-reduction",&format!("base{k}"),t,x.loss,w(1.)?)?;}c.owners("global_owners",&lane,total)?;emit_charges(c,&ledger)?;record_vec("driver.combined_panel_owners",&panels);Ok(Lane{panels,direct,total,ledger,diag:[Tracked::empty();10]})}

fn projection_gates(c:&mut Csv,k:usize,cumulative:Owners,href16:&Lane,href32:&Lane)->R<()>{
 let heat_q=heat(c,"Qhi16",cumulative)?;let heat_h16=heat(c,"H1_G16",href16.total)?;let heat_h32=heat(c,"H1_G32",href32.total)?;physical_agreement(c,"shared_path_heat_projection",heat_q,heat_h32,1e-20,1.)?;physical_agreement(c,"shared_path_heat_tightening",heat_h16,heat_h32,1e-20,0.1)?;
 // Same-m owner/stock comparison retains the original dimensional allowances.
 for(j,(a,b))in fields(cumulative).into_iter().zip(fields(href32.total)).enumerate(){physical_agreement(c,&format!("Qhi_H32:{}",NAMES[j]),a.value,b.value,if photon_term(j){1e-8}else{1e-20},1.)?;physical_agreement(c,&format!("H16_H32_allowance:{}",NAMES[j]),fields(href16.total)[j].value,b.value,if photon_term(j){1e-8}else{1e-20},0.1)?;}
 for k in 0..10{c.output("endpoint_diagnostic","G16",D_NAMES[k],href16.diag[k])?;c.output("endpoint_diagnostic","G32",D_NAMES[k],href32.diag[k])?;}
 for k in 0..8{let a=href16.diag[k].value;let b=href32.diag[k].value;let d=if b.is_empty(){if a.is_empty(){0.}else{f64::INFINITY}}else{rel(a,b)?.abs()};c.scalar("diagnostic_tightening","G16_G32",D_NAMES[k],d)?;if k%4==3 {if d>1e-6{return Err(format!("Hdot tightening {}",D_NAMES[k]));}}else{physical_agreement(c,&format!("Gamma_tightening:{}",D_NAMES[k]),a,b,1e-22,0.1)?;}}
 for k in 0..3{physical_agreement(c,&format!("Gamma_projection:{k}"),href32.diag[k].value,href32.diag[k+4].value,1e-22,1.)?;}
 let hdot=if href32.diag[7].value.is_empty(){if href32.diag[3].value.is_empty(){0.}else{f64::INFINITY}}else{rel(href32.diag[3].value,href32.diag[7].value)?.abs()};c.scalar("shape","Hdot","relative",hdot)?;if hdot>1e-3{return Err("instantaneous Hdot projection gate".into());}
 for(k,reference,abs)in [(8,href32.total.n.value,1e-8),(9,href32.total.u.value,1e-20)]{let allowance=w(abs)?.add(reference.mul(w(1e-3)?).map_err(err)?).map_err(err)?.0;c.wide("shape",D_NAMES[k],"allowance",allowance)?;if !href32.diag[k].value.le(allowance){return Err(format!("global {} gate",D_NAMES[k]));}physical_agreement(c,&format!("L1_tightening:{}",D_NAMES[k]),href16.diag[k].value,href32.diag[k].value,abs,0.1)?;}
 println!("BASE{}_PROJECTION_GLOBAL_SHAPE=PASS; LOCAL_WAKE_SHAPE_ADMISSION=NOT_CLAIMED",k);
Ok(())}
fn aggregate_increments(ledger:&Ledger,next:Option<[Wide;11]>)->R<([Wide;11],[Wide;2])>{let mut values=Vec::with_capacity(4);values.extend(ledger.increments.iter().copied());if let Some(x)=next{values.push(x)}let mut all=[Wide::ZERO;11];let mut bounds=[Wide::ZERO;2];for j in 0..11{let x:Vec<_>=values.iter().map(|v|Tracked::exact(v[j])).collect();let t=sorted_sum(&x)?;all[j]=t.value;let d=if photon_term(j+2){0}else{1};bounds[d]=bounds[d].upper_add(t.loss).map_err(err)?;}record_vec("driver.private_retained11",&values);Ok((all,bounds))}
fn canonical_global(panels:&[Panel],ledger:&Ledger,s:f64,next:Option<[Wide;11]>)->R<((f64,f64,Wide,Wide),[Wide;11],Owners)>{let(stock,sb)=stock_cache(panels,s)?;let(inc,ib)=aggregate_increments(ledger,next)?;let(rn,re,bn,be)=residual([Wide::ZERO;2],stock,inc)?;let mut a=[Tracked::empty();13];a[0]=Tracked::exact(stock[0]);a[1]=Tracked::exact(stock[1]);for j in 0..11{a[j+2]=Tracked::exact(inc[j]);}Ok(((rn,re,bn.upper_add(sb[0]).map_err(err)?.upper_add(ib[0]).map_err(err)?,be.upper_add(sb[1]).map_err(err)?.upper_add(ib[1]).map_err(err)?),inc,from_fields(a)))}
fn final_rows(oracle:&mut Csv,panels:&[Panel],ledger:&Ledger,s:f64)->R<()>{inventory(oracle,"B128_m1:final",panels,s)?;for(step,inc)in ledger.increments.iter().enumerate(){for(key,x)in NAMES[2..].iter().zip(inc){oracle.wide("increment",&format!("B128_m1:{step}"),key,*x)?;}}let(g,_,_)=canonical_global(panels,ledger,s,None)?;for(key,x)in[("rN",g.0),("rE",g.1)]{oracle.scalar("global","B128_m1",key,x)?;}let loss=ledger.totals()?;for(key,x)in[("bN",g.2),("bE",g.3),("lossN",loss.0),("lossE",loss.1)]{oracle.wide("global","B128_m1",key,x)?;}oracle.flush()}
fn verify_common_stock_clone(a:&Lane,b:&Lane)->R<()>{
 if a.panels.len()!=b.panels.len() || a.direct!=b.direct || a.ledger!=b.ledger{return Err("common stock clone metadata/value mismatch".into())}
 for (x,y) in a.panels.iter().zip(&b.panels).chain(std::iter::once((&a.total,&b.total))){for(u,v)in fields(*x).into_iter().zip(fields(*y)){if u.value!=v.value || u.loss!=v.loss{return Err("common stock clone owner mismatch".into())}}}
 for (u,v) in a.diag.iter().zip(&b.diag){if u.value!=v.value || u.loss!=v.loss{return Err("common stock clone diagnostic mismatch".into())}}
 if !a.panels.is_empty() && a.panels.as_ptr()==b.panels.as_ptr(){return Err("stock clone aliases panel storage".into())}
 if !a.ledger.charges().is_empty() && a.ledger.charges().as_ptr()==b.ledger.charges().as_ptr(){return Err("stock clone aliases charge storage".into())}
 record_vec("driver.common_J32_clone_panel_owners",&b.panels);record_vec("driver.common_J32_clone_direct_M",&b.direct);record_vec("driver.common_J32_clone_charges",&b.ledger.charges());Ok(())
}
fn precommit_oracle(frame:&Frame,oracle:&mut Csv,candidate:&[Panel],committed:&Ledger,increment:[Wide;11],charges:&[Charge],k:usize)->R<()>{
 let mut pending=committed.clone();pending.commit(increment,charges.to_vec(),true)?;
 oracle.flush()?;let path=format!("results/precommit_k{}_oracle.csv",k+1);let mut checkpoint=Csv::new(&path)?;
 for line in BufReader::new(File::open("results/continuation_oracle.csv").map_err(err)?).lines().skip(1){writeln!(checkpoint.out,"{}",line.map_err(err)?).map_err(err)?;}
 final_rows(&mut checkpoint,candidate,&pending,frame.times[4*(k+1)])?;drop(checkpoint);
 let stdout=OpenOptions::new().write(true).create_new(true).open(format!("results/precommit_k{}_oracle.stdout",k+1)).map_err(err)?;
 let stderr=OpenOptions::new().write(true).create_new(true).open(format!("results/precommit_k{}_oracle.stderr",k+1)).map_err(err)?;
 let status=std::process::Command::new("python3").args(["oracle.py",&path,"--output",&format!("results/precommit_k{}_HIGH_PRECISION.json",k+1),"--metrics",&format!("results/precommit_k{}_oracle_metrics.csv",k+1),"--require","inventory,local,increment,global"]).stdout(stdout).stderr(stderr).status().map_err(err)?;
 if !status.success(){return Err(format!("independent canonical precommit oracle k{k}: {status}"))}
 println!("BASE{k}_INDEPENDENT_PRECOMMIT_ORACLE=PASS");Ok(())
}
fn step(frame:&Frame,c:&mut Csv,oracle:&mut Csv,old:&[Panel],committed:&Ledger,k:usize)->R<(Vec<Panel>,[Wide;11],Vec<Charge>)>{
 let start=std::time::Instant::now();let before=snapshot(old,committed);let s0=frame.times[4*k];let s1=frame.times[4*(k+1)];let lo=(frame.times[0]+frame.cfg.source.energy_min_ev.ln()).max(s1+13.6f64.ln());let hi=s1+frame.cfg.source.energy_max_ev.ln();let mut edges=Vec::with_capacity(258);edges.push(lo);for x in &frame.mesh{if *x>lo&&*x<hi{edges.push(*x)}}edges.push(hi);record_vec("driver.destination_edges",&edges);if edges.len()-1>256{return Err("occupied panel cap".into())}for(i,ab)in edges.windows(2).enumerate(){if ab[1]-ab[0]<1e-7{return Err(format!("unsupported destination width k{k} p{i}"))}c.scalar("occupied_support",&format!("k{k}:p{i}"),"L",ab[0])?;c.scalar("occupied_support",&format!("k{k}:p{i}"),"R",ab[1])?;}
 // Static persistent geometry means every old panel is one exact destination
 // prefix cell. Reject rather than silently using a mismatched stock control.
 for(i,p)in old.iter().enumerate(){if p.l.to_bits()!=edges[i].to_bits()||p.r.to_bits()!=edges[i+1].to_bits(){return Err("old panel/destination topology mismatch".into())}}
 inventory(c,&format!("B128_m1:in:{k}"),old,s0)?;let(incoming,in_bound)=stock_cache(old,s0)?;
 let jhi=stock_rule(frame,c,old,&edges,k,32)?;stock_controls(frame,c,old,&jhi,k)?;
 let jlo=jhi.clone();verify_common_stock_clone(&jhi,&jlo)?;println!("BASE{k}_COMMON_J32_CLONE=PASS; NUMERIC_WORKERS={} DISTINCT_PHYSICAL_CORES=true",worker_count());
 let slo=source_lane(frame,c,&format!("Qlo_source:{k}"),8,k,k+1,&edges,None,None)?;let qlo=combine(frame,c,jlo,slo,&edges,k,false,None)?;
 let shi=source_lane(frame,c,&format!("Qhi_source:{k}"),16,k,k+1,&edges,None,None)?;let mut candidate=Vec::with_capacity(256);let qhi=combine(frame,c,jhi,shi,&edges,k,true,Some(&mut candidate))?;
 for i in 0..qhi.panels.len(){compare_panel(c,&format!("Qlo_Qhi:k{k}:p{i}"),qlo.panels[i],qhi.panels[i])?;}require_relative(c,&format!("Qlo8_Qhi16:k{k}"),qlo.total,qhi.total,1e-6)?;drop(qlo);println!("BASE{k}_QUADRATURE_QLO_QHI=PASS");
 let href16=source_lane(frame,c,&format!("H1_G16:{k}"),16,0,k+1,&edges,None,Some(&candidate))?;let href32=source_lane(frame,c,&format!("H1_G32:{k}"),32,0,k+1,&edges,None,Some(&candidate))?;require_relative(c,&format!("H1_G16_G32:k{k}"),href16.total,href32.total,1e-6)?;for i in 0..href32.panels.len(){compare_panel(c,&format!("H16_H32:k{k}:p{i}"),href16.panels[i],href32.panels[i])?;}
 let increment=retained(qhi.total);let(global,global_increment,cumulative)=canonical_global(&candidate,committed,s1,Some(increment))?;projection_gates(c,k,cumulative,&href16,&href32)?;
 let ms:Vec<Tracked>=candidate.iter().map(|p|p.moments().map(|x|Tracked::exact(x[1]))).collect::<R<Vec<_>>>()?;record_vec("driver.stored_M_audit",&ms);let stored_m=sorted_sum(&ms)?;let mfac=Wide::from_log(s1).map_err(err)?.mul(w(1./EPS)?).map_err(err)?;let reference_m=href32.total.u.value.mul(mfac).map_err(err)?;let m_allowance=w(1e-20)?.add(href32.total.u.value.mul(w(1e-3)?).map_err(err)?).map_err(err)?.0.mul(mfac).map_err(err)?;c.output("endpoint_M",&format!("k{k}"),"stored",stored_m)?;c.wide("endpoint_M",&format!("k{k}"),"reference",reference_m)?;c.wide("endpoint_M",&format!("k{k}"),"U_derived_allowance",m_allowance)?;if !positive_difference(stored_m.value,reference_m)?.le(m_allowance){return Err("stored M U-derived allowance".into())}
 let(outgoing,out_bound)=stock_cache(&candidate,s1)?;let(rn,re,bn,be)=residual(incoming,outgoing,increment)?;let local=(rn,re,bn.upper_add(in_bound[0]).map_err(err)?.upper_add(out_bound[0]).map_err(err)?,be.upper_add(in_bound[1]).map_err(err)?.upper_add(out_bound[1]).map_err(err)?);let loss=qhi.ledger.totals()?;gate_budget(c,&format!("local:k{k}"),local,loss,increment)?;
 let historical=committed.totals()?;let cumulative_loss=(historical.0.upper_add(loss.0).map_err(err)?,historical.1.upper_add(loss.1).map_err(err)?);gate_budget(c,&format!("global:k{k}"),global,cumulative_loss,global_increment)?;
 if !cumulative_loss.0.upper_add(local.2).map_err(err)?.le(w(1e-20)?)||!cumulative_loss.1.upper_add(local.3).map_err(err)?.le(w(1e-30)?){return Err("cumulative loss plus local audit cap".into())}
 let observation=snapshot(&candidate,&qhi.ledger);witness(frame,&candidate,c,k+1,false)?;witness(frame,&candidate,c,k+1,true)?;if observation!=snapshot(&candidate,&qhi.ledger){return Err("observation order mutated candidate".into())}if before!=snapshot(old,committed){return Err("private attempt mutated accepted state".into())}
 inventory(oracle,&format!("B128_m1:in:{k}"),old,s0)?;inventory(oracle,&format!("B128_m1:out:{k}"),&candidate,s1)?;local_row(oracle,&format!("B128_m1:{k}"),incoming,outgoing,increment,local,loss)?;oracle.flush()?;c.flush()?;precommit_oracle(frame,oracle,&candidate,committed,increment,&qhi.ledger.charges(),k)?;if before!=snapshot(old,committed){return Err("precommit oracle mutated accepted state".into())}println!("BASE{k}_ALL_GATES=PASS elapsed_seconds={:.6}",start.elapsed().as_secs_f64());Ok((candidate,increment,qhi.ledger.into_charges()))
}
fn directory_bytes(path:&std::path::Path)->R<u64>{let mut total=0;for e in std::fs::read_dir(path).map_err(err)?{let p=e.map_err(err)?.path();let m=p.symlink_metadata().map_err(err)?;if m.is_dir(){total+=directory_bytes(&p)?}else{total+=m.len()}}Ok(total)}
fn load_checkpoint2(frame:&Frame,c:&mut Csv,oracle:&mut Csv)->R<(Vec<Panel>,Ledger)>{
 let mut records:BTreeMap<usize,Record>=BTreeMap::new();
 for line in BufReader::new(File::open("inputs/accepted_panels.csv").map_err(err)?).lines().skip(1){let line=line.map_err(err)?;let a:Vec<_>=line.split(',').collect();if a.len()!=5||a[0]!="panel"{return Err("invalid resume panel record".into())}let i:usize=a[1].strip_prefix('p').ok_or("resume panel ID")?.parse().map_err(err)?;let v=Saved{bits:u64::from_str_radix(a[3],16).map_err(err)?,exp:a[4].parse().map_err(err)?};if records.entry(i).or_default().insert(a[2].into(),v).is_some(){return Err("duplicate resume field".into())}}
 if records.len()!=186{return Err("resume requires the exact admitted second state".into())}let mut accepted=Vec::with_capacity(256);
 for(i,r)in records{if i!=accepted.len()||r.len()!=11{return Err("noncontiguous/incomplete resume panels".into())}let l=saved(&r,"L")?.f();let rr=saved(&r,"R")?.f();let n=saved(&r,"stored.N")?.wide()?;let m=saved(&r,"stored.M")?.wide()?;let k=n.exponent().max(m.exponent());let ns=n.mantissa()*2f64.powi(n.exponent()-k);let ms=m.mantissa()*2f64.powi(m.exponent()-k);let front=saved(&r,"front")?.f()==1.;let pair={let _lease=SiteGuard::new(64)?;MomentPair::new(l,rr,k,ns,ms,front).map_err(err)?};let log=pair.logs();if log.0.to_bits()!=saved(&r,"canonical_logN")?.bits||log.1.to_bits()!=saved(&r,"canonical_logM")?.bits{return Err("resume changed canonical logs".into())}let p=Panel{l,r:rr,pair,closure:v2::Closure{l,r:rr,n:ns,beta:saved(&r,"beta")?.f(),front},front,provenance:saved(&r,"provenance")?.f()as u32,incoming_loss_metadata:[saved(&r,"incoming_lossN")?.wide()?,saved(&r,"incoming_lossM")?.wide()?]};if p.moments()!=Ok([n,m])||p.provenance!=2{return Err("resume changed accepted moments/provenance".into())}accepted.push(p);}
 let mut increments=[[Wide::ZERO;11];2];let mut got=[[false;11];2];
 for line in BufReader::new(File::open("inputs/accepted_k2_oracle.csv").map_err(err)?).lines().skip(1){let line=line.map_err(err)?;let a:Vec<_>=line.split(',').collect();if a.len()!=5{return Err("invalid resume oracle row".into())}if a[0]=="increment"{let step:usize=a[1].strip_prefix("B128_m1:").ok_or("resume increment ID")?.parse().map_err(err)?;if step>=2{return Err("resume increment count".into())}let j=NAMES[2..].iter().position(|x|*x==a[2]).ok_or("resume retained owner")?;if got[step][j]{return Err("duplicate resume increment".into())}increments[step][j]=Saved{bits:u64::from_str_radix(a[3],16).map_err(err)?,exp:a[4].parse().map_err(err)?}.wide()?;got[step][j]=true;}else if !(a[0]=="global"||(a[0]=="inventory"&&a[1]=="B128_m1:final")){writeln!(oracle.out,"{line}").map_err(err)?;}}
 if !got.iter().flatten().all(|x|*x){return Err("missing resume increment".into())}let mut groups=[Vec::new(),Vec::new()];let mut count_charges=0;let mut previous_transition=0;
 for line in BufReader::new(File::open("inputs/accepted_charges.tsv").map_err(err)?).lines(){let line=line.map_err(err)?;let a:Vec<_>=line.split('\t').collect();if a.len()!=12{return Err("invalid resume charge".into())}let ordinal:usize=a[0].parse().map_err(err)?;let transition:usize=a[2].parse().map_err(err)?;if ordinal!=count_charges||transition>=2||transition<previous_transition{return Err("resume charge order changed".into())}previous_transition=transition;count_charges+=1;let term:usize=a[5].parse().map_err(err)?;if term>=13{return Err("resume term index".into())}let bound=Saved{bits:u64::from_str_radix(a[6],16).map_err(err)?,exp:a[7].parse().map_err(err)?}.wide()?;let coefficient=Saved{bits:u64::from_str_radix(a[8],16).map_err(err)?,exp:a[9].parse().map_err(err)?}.wide()?;let dimensional=Saved{bits:u64::from_str_radix(a[10],16).map_err(err)?,exp:a[11].parse().map_err(err)?}.wide()?;if bound.upper_mul(coefficient).map_err(err)?!=dimensional{return Err("resume dimensional charge changed".into())}groups[transition].push(Charge{lane:a[1].into(),transition,boundary:a[3].into(),id:a[4].into(),term,bound,coefficient,units:if photon_term(term){"photons/H"}else{"erg/H"}});}
 let mut ledger=Ledger::default();for (inc,charges)in increments.into_iter().zip(groups){ledger.commit(inc,charges,true)?;}
 if ledger.charges().len()!=count_charges{return Err("resume omitted charge".into())}
 // Re-emit the canonical accepted checkpoint byte-for-byte before any new transition.
 let mut roundtrip=Csv::new("results/reloaded_k2_oracle.csv")?;oracle.flush()?;for line in BufReader::new(File::open("results/continuation_oracle.csv").map_err(err)?).lines().skip(1){writeln!(roundtrip.out,"{}",line.map_err(err)?).map_err(err)?;}final_rows(&mut roundtrip,&accepted,&ledger,frame.times[8])?;drop(roundtrip);
 if std::fs::read("results/reloaded_k2_oracle.csv").map_err(err)?!=std::fs::read("inputs/accepted_k2_oracle.csv").map_err(err)?{return Err("resume canonical checkpoint differs in any byte".into())}
 println!("RELOADED_SECOND_STATE_CANONICAL_BYTES=PASS; PANELS={} INCREMENTS={} CHARGES={} SNAPSHOT={:016x}; FIRST_TWO_TRANSITIONS_NOT_REPLAYED",accepted.len(),ledger.increments.len(),ledger.charges().len(),snapshot(&accepted,&ledger));emit_charges(c,&ledger)?;c.flush()?;Ok((accepted,ledger))
}
fn load_checkpoint3(frame:&Frame,c:&mut Csv,oracle:&mut Csv)->R<(Vec<Panel>,Ledger)>{
 let mut records:BTreeMap<usize,Record>=BTreeMap::new();
 for line in BufReader::new(File::open("inputs/accepted_panels.csv").map_err(err)?).lines().skip(1){let line=line.map_err(err)?;let a:Vec<_>=line.split(',').collect();if a.len()!=5||a[0]!="panel"{return Err("invalid resume panel record".into())}let i:usize=a[1].strip_prefix('p').ok_or("resume panel ID")?.parse().map_err(err)?;let v=Saved{bits:u64::from_str_radix(a[3],16).map_err(err)?,exp:a[4].parse().map_err(err)?};if records.entry(i).or_default().insert(a[2].into(),v).is_some(){return Err("duplicate resume field".into())}}
 if records.len()!=190{return Err("resume requires the exact admitted third state".into())}let mut accepted=Vec::with_capacity(256);
 for(i,r)in records{if i!=accepted.len()||r.len()!=11{return Err("noncontiguous/incomplete resume panels".into())}let l=saved(&r,"L")?.f();let rr=saved(&r,"R")?.f();let n=saved(&r,"stored.N")?.wide()?;let m=saved(&r,"stored.M")?.wide()?;let k=n.exponent().max(m.exponent());let ns=n.mantissa()*2f64.powi(n.exponent()-k);let ms=m.mantissa()*2f64.powi(m.exponent()-k);let front=saved(&r,"front")?.f()==1.;let pair={let _lease=SiteGuard::new(64)?;MomentPair::new(l,rr,k,ns,ms,front).map_err(err)?};let log=pair.logs();if log.0.to_bits()!=saved(&r,"canonical_logN")?.bits||log.1.to_bits()!=saved(&r,"canonical_logM")?.bits{return Err("resume changed canonical logs".into())}let p=Panel{l,r:rr,pair,closure:v2::Closure{l,r:rr,n:ns,beta:saved(&r,"beta")?.f(),front},front,provenance:saved(&r,"provenance")?.f()as u32,incoming_loss_metadata:[saved(&r,"incoming_lossN")?.wide()?,saved(&r,"incoming_lossM")?.wide()?]};if p.moments()!=Ok([n,m])||p.provenance!=3{return Err("resume changed accepted moments/provenance".into())}accepted.push(p);}
 let mut increments=[[Wide::ZERO;11];3];let mut got=[[false;11];3];
 for line in BufReader::new(File::open("inputs/accepted_k3_oracle.csv").map_err(err)?).lines().skip(1){let line=line.map_err(err)?;let a:Vec<_>=line.split(',').collect();if a.len()!=5{return Err("invalid resume oracle row".into())}if a[0]=="increment"{let step:usize=a[1].strip_prefix("B128_m1:").ok_or("resume increment ID")?.parse().map_err(err)?;if step>=3{return Err("resume increment count".into())}let j=NAMES[2..].iter().position(|x|*x==a[2]).ok_or("resume retained owner")?;if got[step][j]{return Err("duplicate resume increment".into())}increments[step][j]=Saved{bits:u64::from_str_radix(a[3],16).map_err(err)?,exp:a[4].parse().map_err(err)?}.wide()?;got[step][j]=true;}else if !(a[0]=="global"||(a[0]=="inventory"&&a[1]=="B128_m1:final")){writeln!(oracle.out,"{line}").map_err(err)?;}}
 if !got.iter().flatten().all(|x|*x){return Err("missing resume increment".into())}let mut groups=[Vec::new(),Vec::new(),Vec::new()];let mut count_charges=0;let mut previous_transition=0;
 for line in BufReader::new(File::open("inputs/accepted_charges.tsv").map_err(err)?).lines(){let line=line.map_err(err)?;let a:Vec<_>=line.split('\t').collect();if a.len()!=12{return Err("invalid resume charge".into())}let ordinal:usize=a[0].parse().map_err(err)?;let transition:usize=a[2].parse().map_err(err)?;if ordinal!=count_charges||transition>=3||transition<previous_transition{return Err("resume charge order changed".into())}previous_transition=transition;count_charges+=1;let term:usize=a[5].parse().map_err(err)?;if term>=13{return Err("resume term index".into())}let bound=Saved{bits:u64::from_str_radix(a[6],16).map_err(err)?,exp:a[7].parse().map_err(err)?}.wide()?;let coefficient=Saved{bits:u64::from_str_radix(a[8],16).map_err(err)?,exp:a[9].parse().map_err(err)?}.wide()?;let dimensional=Saved{bits:u64::from_str_radix(a[10],16).map_err(err)?,exp:a[11].parse().map_err(err)?}.wide()?;if bound.upper_mul(coefficient).map_err(err)?!=dimensional{return Err("resume dimensional charge changed".into())}groups[transition].push(Charge{lane:a[1].into(),transition,boundary:a[3].into(),id:a[4].into(),term,bound,coefficient,units:if photon_term(term){"photons/H"}else{"erg/H"}});}
 let mut ledger=Ledger::default();for (inc,charges)in increments.into_iter().zip(groups){ledger.commit(inc,charges,true)?;}
 if ledger.charges().len()!=count_charges{return Err("resume omitted charge".into())}
 // Re-emit the canonical accepted checkpoint byte-for-byte before any new transition.
 let mut roundtrip=Csv::new("results/reloaded_k3_oracle.csv")?;oracle.flush()?;for line in BufReader::new(File::open("results/continuation_oracle.csv").map_err(err)?).lines().skip(1){writeln!(roundtrip.out,"{}",line.map_err(err)?).map_err(err)?;}final_rows(&mut roundtrip,&accepted,&ledger,frame.times[12])?;drop(roundtrip);
 if std::fs::read("results/reloaded_k3_oracle.csv").map_err(err)?!=std::fs::read("inputs/accepted_k3_oracle.csv").map_err(err)?{return Err("resume canonical checkpoint differs in any byte".into())}
 println!("RELOADED_THIRD_STATE_CANONICAL_BYTES=PASS; PANELS={} INCREMENTS={} CHARGES={} SNAPSHOT={:016x}; FIRST_THREE_TRANSITIONS_NOT_REPLAYED",accepted.len(),ledger.increments.len(),ledger.charges().len(),snapshot(&accepted,&ledger));emit_charges(c,&ledger)?;c.flush()?;Ok((accepted,ledger))
}
fn run(c:&mut Csv,oracle:&mut Csv)->R<()>{
 durable::refuse_native_be()?;
 let mode=durable::mode();
 if mode.as_ref().is_some_and(|m|!["prime","live","resume","probe","pending-control"].contains(&m.as_str())){return Err("UNKNOWN_DURABLE_MODE_REFUSED".into())}
 let frame=Frame::new(128)?;
 let mut durable_store=None;
 let (mut accepted,mut committed)=if matches!(mode.as_deref(),Some("resume")|Some("probe")) {
   let (store,panels,ledger,history)=durable::Store::resume(&durable::root()?,&frame)?;
   oracle.out.write_all(history.strip_prefix("kind,id,field,bits,exp\n").ok_or("audit header")?.as_bytes()).map_err(err)?;
   durable_store=Some(store);(panels,ledger)
 }else{load_checkpoint3(&frame,c,oracle)?};
 if matches!(mode.as_deref(),Some("prime")|Some("live")|Some("pending-control")) {
   oracle.flush()?;let history=std::fs::read_to_string("results/continuation_oracle.csv").map_err(err)?;
   let mut store=durable::Store::create(&durable::root()?)?;store.publish(&frame,&accepted,&committed,&history)?;durable_store=Some(store);
 }
 if mode.as_deref()==Some("pending-control") {
   oracle.flush()?;let history=std::fs::read_to_string("results/continuation_oracle.csv").map_err(err)?;
   durable_store.as_mut().ok_or("missing pending control store")?.stop_pending_control(&frame,&accepted,&committed,&history)?;
 }
 if mode.as_deref()==Some("prime") {
   std::fs::write(durable::root()?.join("READY_FOR_KILL"),b"synced frozen k3 checkpoint\n").map_err(err)?;
   loop{std::thread::sleep(std::time::Duration::from_millis(20))}
 }
 if mode.as_deref()==Some("probe")||std::env::var("RESUME_ROUNDTRIP_ONLY").ok().as_deref()==Some("1"){
   final_rows(oracle,&accepted,&committed,frame.times[4*committed.increments.len()])?;
   println!("FROZEN_DISK_RESTORE_ONLY stage={} snapshot={:016x} panels={} physical_history_full_wide=HOLD",committed.increments.len(),snapshot(&accepted,&committed),accepted.len());return Ok(())
 }
 if committed.increments.len()!=3{return Err("FROZEN_BOUNDARY_REQUIRES_K3_INPUT_NO_HISTORY_EXTENSION".into())}
 let started=std::time::Instant::now();let budget=std::env::var("CONTINUATION_WALL_BUDGET_SECONDS").ok().and_then(|v|v.parse::<f64>().ok()).unwrap_or(34.);let mut last_cost=20.;let mut last_growth=0u64;let mut failure=None;
 for k in 3..4{let disk_before=directory_bytes(std::path::Path::new("."))?;if disk_before+524288+last_growth*3/2>256*1024*1024{failure=Some(format!("RESOURCE_PARTIAL output admission before base{k}: observed_bytes={disk_before} last_step_growth={last_growth}"));break}let remaining=budget-started.elapsed().as_secs_f64();if remaining<=5.+last_cost*1.5{failure=Some(format!("RESOURCE_PARTIAL before base{k}: remaining={remaining:.6} reserve=5 next_estimate={:.6}",last_cost*1.5));break}let before=snapshot(&accepted,&committed);let stage=std::time::Instant::now();let counts_before=telemetry();match step(&frame,c,oracle,&accepted,&committed,k){Ok((candidate,increment,charges))=>{let mut next=committed.clone();next.commit(increment,charges,true)?;
 if let Some(store)=durable_store.as_mut(){oracle.flush()?;let history=std::fs::read_to_string("results/continuation_oracle.csv").map_err(err)?;store.publish(&frame,&candidate,&next,&history)?;}
 committed=next;accepted=candidate;last_cost=stage.elapsed().as_secs_f64();record_vec("driver.accepted_panels",&accepted);let path=format!("results/continuation_k{}_oracle.csv",k+1);let mut checkpoint=Csv::new(&path)?;oracle.flush()?;for line in BufReader::new(File::open("results/continuation_oracle.csv").map_err(err)?).lines().skip(1){writeln!(checkpoint.out,"{}",line.map_err(err)?).map_err(err)?;}final_rows(&mut checkpoint,&accepted,&committed,frame.times[4*(k+1)])?;emit_charges(c,&committed)?;c.flush()?;last_growth=directory_bytes(std::path::Path::new("."))?.saturating_sub(disk_before);let counts=telemetry();let delta=|key:&str|counts.counters.get(key).copied().unwrap_or(0)-counts_before.counters.get(key).copied().unwrap_or(0);println!("ACCEPTED_BASES={} PANELS={} step_elapsed_seconds={last_cost:.6} segments={} fits={} loaded_history_preserved=true",committed.increments.len(),accepted.len(),delta("characteristic_segments"),delta("endpoint_fits"));},Err(e)=>{if before!=snapshot(&accepted,&committed){return Err("FAILED ATTEMPT MUTATED ACCEPTED STATE".into())}failure=Some(format!("BASE{k} FIRST_REAL_GATE_FAILURE: {e}; accepted_state_and_ledger_immutable=true"));break;}}}
 let end=committed.increments.len();final_rows(oracle,&accepted,&committed,frame.times[4*end])?;c.flush()?;println!("COMMITTED_PANELS={}; COMMITTED_INCREMENTS={}; MODEL_UNRESOLVED",accepted.len(),end);if let Some(e)=failure{Err(e)}else{println!("FOUR_INTERVAL_IMPLEMENTATION_GATES=PASS; independent canonical oracle still required; MODEL_UNRESOLVED");Ok(())}}
fn main(){let result=(||->R<()>{let mut c=Csv::new("results/continuation.csv")?;let mut oracle=Csv::new("results/continuation_oracle.csv")?;let r=run(&mut c,&mut oracle);let _=c.flush();let _=oracle.flush();r})();let t=telemetry();println!("SIMD_GAUSS_CALLS {} mode={}",v2::simd_calls(),std::env::var("REI_SIMD").unwrap_or_else(|_|"scalar".into()));let(global_live,global_peak)=p::site_counts();println!("GLOBAL_SITE_CAPACITY live={global_live} peak={global_peak} cap=4096");println!("TELEMETRY live={} peak={} created={} retired={}",t.live,t.peak,t.created,t.retired);for(k,v)in t.counters{println!("COUNT {k} {v}");}for(k,(len,cap,size))in t.arrays{println!("ARRAY {k} used_hwm={len} capacity_hwm={cap} element_bytes={size} capacity_bytes={}",cap*size);}if let Err(e)=result{eprintln!("CONTINUATION_PARTIAL_NO_FAILED_COMMIT: {e}");eprintln!("Later mandatory gates NOT_RUN; exact attempted rows retained; no panel dropped or repaired. MODEL_UNRESOLVED");std::process::exit(1);}}

fn source_lane_parallel(frame:&Frame,c:&mut Csv,lane:&str,order:usize,start:usize,end:usize,edges:&[f64],projection:Option<&[Panel]>)->R<Lane>{
 let results=panel_map_with(worker_count(),edges.len()-1,|i|{
  let ab=&edges[i..i+2];let mut csv=Csv::memory();let c=&mut csv;let mut ledger=Ledger::default();let mut directs=Vec::with_capacity(1);let mut summaries=Vec::with_capacity(1);let mut diagnostic_panels=Vec::with_capacity(1);let mut candidate:Option<&mut Vec<Panel>>=None;

  let _sites=SiteGuard::new(order)?;let nodes=v2::gauss(ab[0],ab[1],order);record_vec("driver.current_nodes",&nodes);count("quadrature_sites_created",nodes.len());
  let mut values=Vec::with_capacity(order);let mut direct_m=Vec::with_capacity(order);let mut diagnostic_values=Vec::<[Tracked;10]>::with_capacity(if projection.is_some(){order}else{0});
  record_vec("driver.current_site_owners",&values);record_vec("driver.current_direct_M",&direct_m);record_vec("driver.current_diagnostic_values",&diagnostic_values);
  for(j,(eta,q))in nodes.into_iter().enumerate(){
   let id=format!("{lane}:p{i}:q{j}");if !(eta>ab[0]&&eta<ab[1]&&q>0.){return Err(format!("invalid positive node {id}"));}
   if i>=182{c.scalar("node",&id,"eta",eta)?;c.scalar("node",&id,"eta_weight",q)?;}else if j==0{c.scalar("node_geometry_reuse_from_first_interval",&format!("{lane}:p{i}"),"panel_index",i as f64)?;c.scalar("node_geometry_reuse_from_first_interval",&format!("{lane}:p{i}"),"gauss_order",order as f64)?;}
   let raw=frame.replay(eta,start,end,1,Tracked::empty(),true).map_err(|e|format!("{id}: {e}"))?;
   let coefficient=w(q)?;let weighted=EtaWeight(q).apply(raw)?;
   // Raw provenance and its physical geometric coefficient are retained. The
   // terminal bound is charged once here, never again as panel input uncertainty.
   for(term,x)in fields(raw).into_iter().enumerate(){charge(c,&mut ledger,lane,"terminal-point",&format!("p{i}:q{j}"),term,x.loss,coefficient)?;}
   let exact=canonical(weighted);direct_m.push(exact.n.mul(Tracked::exact(Wide::from_log(eta).map_err(err)?)).map_err(err)?);
   if let Some(ps)=projection{let p=ps.get(i).ok_or("missing diagnostic panel")?;let fp=p.density(eta)?;let fh=raw.n.value;let rates=frame.diagnostic_rates(eta,frame.times[4*end])?;let mut d=[Tracked::empty();10];for k in 0..4{d[k]=Tracked::exact(fp).scale(rates[k]).map_err(err)?.scale(q).map_err(err)?;d[k+4]=Tracked::exact(fh).scale(rates[k]).map_err(err)?.scale(q).map_err(err)?;}let df=positive_difference(fp,fh)?;d[8]=Tracked::exact(df).scale(q).map_err(err)?;d[9]=d[8].scale(EPS*(eta-frame.times[4*end]).exp()).map_err(err)?;diagnostic_values.push(d);}
   values.push(exact);record_vec("driver.current_site_owners",&values);record_vec("driver.current_direct_M",&direct_m);record_vec("driver.current_diagnostic_values",&diagnostic_values);
  }
  let panel_total=sum_owners(&values)?;let id=format!("{lane}:p{i}");c.owners("panel_owners",&id,panel_total)?;
  let direct=sorted_sum(&direct_m)?;directs.push(direct.value);record_vec("driver.direct_panel_M",&directs);
  if let Some(ref mut ps)=candidate{
   let front=ab[1]==*edges.last().ok_or("empty geometry")?;let endpoint=endpoint_pair(ab[0],ab[1],frame.times[4*end],panel_total,front).map_err(|e|format!("{id} endpoint_pair {e}; L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()))?;
   charge(c,&mut ledger,lane,"endpoint-N",&format!("p{i}"),0,endpoint.n_loss,w(1.)?)?;
   charge(c,&mut ledger,lane,"endpoint-M",&format!("p{i}"),1,endpoint.m_loss,energy_factor(frame.times[4*end])?)?;
   let p=Panel::from_owners(ab[0],ab[1],frame.times[4*end],panel_total,front,1).map_err(|e|format!("{id} reconstruction {e}; L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()))?;
   closure_audit(c,&id,&p,panel_total,direct.value,frame.times[4*end])?;ps.push(p);record_vec("driver.private_candidate_panels",ps);
  }else{for term in 0..2{let x=fields(panel_total)[term];charge(c,&mut ledger,lane,"panel-stock-construction",&format!("p{i}"),term,x.loss,w(1.)?)?;}}
  for(term,x)in fields(panel_total).into_iter().enumerate().skip(2){charge(c,&mut ledger,lane,"panel-owner-construction",&format!("p{i}"),term,x.loss,w(1.)?)?;}
  summaries.push(canonical(panel_total));record_vec(&format!("driver.{lane}.panel_owner_summaries"),&summaries);
  if projection.is_some(){let mut d=[Tracked::empty();10];for k in 0..10{let v:Vec<Tracked>=diagnostic_values.iter().map(|x|x[k]).collect();record_vec("driver.diagnostic_component_buffer",&v);d[k]=sorted_sum(&v)?;if order==16{c.wide("panel_diagnostic",&id,D_NAMES[k],d[k].value)?;c.wide("panel_diagnostic",&id,&format!("{}.loss",D_NAMES[k]),d[k].loss)?;}else{c.output("panel_diagnostic",&id,D_NAMES[k],d[k])?;}}c.scalar("panel_diagnostic",&id,"normalized_local_photon_L1",if panel_total.n.value.is_empty(){0.}else{ratio(d[8].value,panel_total.n.value)?})?;c.scalar("panel_diagnostic",&id,"normalized_local_energy_L1",if panel_total.u.value.is_empty(){0.}else{ratio(d[9].value,panel_total.u.value)?})?;diagnostic_panels.push(d);record_vec(&format!("driver.{lane}.diagnostic_panel_summaries"),&diagnostic_panels);}
  count("quadrature_sites_retired",order);
 
  Ok((summaries[0],directs[0],diagnostic_panels.first().copied(),ledger.into_charges(),csv.rows()))
 })?;
 let mut directs=Vec::with_capacity(edges.len()-1);let mut summaries=Vec::with_capacity(edges.len()-1);let mut diagnostic_panels=Vec::with_capacity(edges.len()-1);let mut ledger=Ledger::default();
 for(owner,direct,diagnostic,charges,rows)in results{c.drain(&rows)?;for ch in charges{ledger.charge(ch)?}summaries.push(owner);directs.push(direct);if let Some(d)=diagnostic{diagnostic_panels.push(d)}}

 let total=sum_owners(&summaries)?;
 // The 11-owner reduction becomes an authoritative increment, so only these
 // newly lost fields are committed. N/U reduction is a temporary stock cache.
 for(term,x)in fields(total).into_iter().enumerate().skip(2){charge(c,&mut ledger,lane,"retained11-reduction","base0",term,x.loss,w(1.)?)?;}
 let mut diag=[Tracked::empty();10];for k in 0..10{let v:Vec<Tracked>=diagnostic_panels.iter().map(|x|x[k]).collect();record_vec("driver.global_diagnostic_component",&v);diag[k]=sorted_sum(&v)?;}
 c.owners("global_owners",lane,total)?;emit_charges(c,&ledger)?;record_vec(&format!("driver.{lane}.charges()"),&ledger.charges());c.flush()?;
 Ok(Lane{panels:summaries,direct:directs,total,ledger,diag})
}
