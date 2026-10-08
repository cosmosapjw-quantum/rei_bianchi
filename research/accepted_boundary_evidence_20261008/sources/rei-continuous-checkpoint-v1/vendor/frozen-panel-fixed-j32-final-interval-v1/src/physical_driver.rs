//! Bounded first-base frozen-gas transaction. MODEL_UNRESOLVED.
//! Run only after the parent has admitted the unit/oracle stage and resources.
//! No continuation or temporal/panel matrix is silently substituted on failure.
#[path="lib.rs"] mod bridge;
use bridge::*;
use bridge::physics::Frame;
use std::fs::{File,OpenOptions};
use std::io::{BufWriter,Write};

const NAMES:[&str;13]=["N","U","QN","QE","red","outN","outE","A_HI","A_HeI","A_HeII","B_HI","B_HeI","B_HeII"];
const D_NAMES:[&str;10]=["P.Gamma_HI","P.Gamma_HeI","P.Gamma_HeII","P.Hdot","H.Gamma_HI","H.Gamma_HeI","H.Gamma_HeII","H.Hdot","L1.N","L1.U"];
struct Csv { out:BufWriter<File> }
impl Csv {
 fn new(path:&str)->R<Self>{let f=OpenOptions::new().write(true).create_new(true).open(path).map_err(err)?;let mut out=BufWriter::with_capacity(8192,f);writeln!(out,"kind,id,field,bits,exp").map_err(err)?;count("csv_buffer_capacity_bytes",8192);Ok(Self{out})}
 fn scalar(&mut self,k:&str,id:&str,key:&str,x:f64)->R<()>{writeln!(self.out,"{k},{id},{key},{:016x},0",x.to_bits()).map_err(err)}
 fn wide(&mut self,k:&str,id:&str,key:&str,x:Wide)->R<()>{writeln!(self.out,"{k},{id},{key},{:016x},{}",x.mantissa().to_bits(),x.exponent()).map_err(err)}
 fn output(&mut self,k:&str,id:&str,key:&str,x:Tracked)->R<()>{let(v,b)=x.value.readout().map_err(err)?;self.wide(k,id,key,x.value)?;self.wide(k,id,&format!("{key}.loss"),x.loss)?;self.scalar(k,id,&format!("{key}.readout"),v)?;self.wide(k,id,&format!("{key}.readout_bound"),b)?;self.scalar(k,id,&format!("{key}.log"),x.value.log())}
 fn owners(&mut self,k:&str,id:&str,o:Owners)->R<()>{for(key,x)in NAMES.into_iter().zip(fields(o)){self.output(k,id,key,x)?;}Ok(())}
 fn flush(&mut self)->R<()>{self.out.flush().map_err(err)}
}
fn canonical(o:Owners)->Owners{from_fields(fields(o).map(|x|Tracked::exact(x.value)))}
fn retained(o:Owners)->[Wide;11]{let a=fields(o);std::array::from_fn(|j|a[j+2].value)}
fn energy_factor(s:f64)->R<Wide>{w(EPS)?.mul(Wide::from_log(-s).map_err(err)?).map_err(err)}
fn charge(c:&mut Csv,ledger:&mut Ledger,lane:&str,boundary:&str,id:&str,term:usize,bound:Wide,coefficient:Wide)->R<()>{ledger.charge(Charge{lane:lane.into(),transition:0,boundary:boundary.into(),id:id.into(),term,bound,coefficient,units:if photon_term(term){"photons/H"}else{"erg/H"}})?;if !bound.is_empty(){let key=format!("{lane}:{boundary}:{id}:term{term}");c.wide("loss_occurrence",&key,"unweighted_bound",bound)?;c.wide("loss_occurrence",&key,"physical_coefficient",coefficient)?;c.wide("loss_occurrence",&key,"dimensional_bound",bound.upper_mul(coefficient).map_err(err)?)?;}Ok(())}
fn emit_charges(c:&mut Csv,ledger:&Ledger)->R<()>{let used:usize=ledger.charges.iter().map(|x|x.lane.len()+x.boundary.len()+x.id.len()).sum();let cap:usize=ledger.charges.iter().map(|x|x.lane.capacity()+x.boundary.capacity()+x.id.capacity()).sum();let lane=ledger.charges.first().map(|x|x.lane.as_str()).unwrap_or("empty");println!("BUFFER {lane}.charge_strings used_bytes={used} allocated_capacity_bytes={cap} append_only_lane_hwm=true");for(i,x)in ledger.charges.iter().enumerate(){let id=format!("{}:{}:{}:{}:{}",x.lane,x.transition,x.boundary,x.id,i);c.scalar("charge",&id,"term",x.term as f64)?;c.wide("charge",&id,"unweighted_bound",x.bound)?;c.wide("charge",&id,"physical_coefficient",x.coefficient)?;c.wide("charge",&id,"dimensional_bound",x.bound.upper_mul(x.coefficient).map_err(err)?)?;}Ok(())}
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
struct Lane { panels:Vec<Owners>,total:Owners,ledger:Ledger,diag:[Tracked;10] }
// Each lane has only one live node batch. After weighted terminal losses are
// captured, every node owner is exact canonical before deterministic reduction.
fn source_lane(frame:&Frame,c:&mut Csv,lane:&str,order:usize,edges:&[f64],mut candidate:Option<&mut Vec<Panel>>,projection:Option<&[Panel]>)->R<Lane>{
 let mut summaries=Vec::with_capacity(edges.len()-1);let mut diagnostic_panels=Vec::<[Tracked;10]>::with_capacity(edges.len()-1);let mut ledger=Ledger::default();
 record_vec(&format!("driver.{lane}.panel_owner_summaries"),&summaries);record_vec(&format!("driver.{lane}.diagnostic_panel_summaries"),&diagnostic_panels);
 for(i,ab)in edges.windows(2).enumerate(){
  let _sites=SiteGuard::new(order)?;let nodes=v2::gauss(ab[0],ab[1],order);record_vec("driver.current_nodes",&nodes);count("quadrature_sites_created",nodes.len());
  let mut values=Vec::with_capacity(order);let mut direct_m=Vec::with_capacity(order);let mut diagnostic_values=Vec::<[Tracked;10]>::with_capacity(if projection.is_some(){order}else{0});
  record_vec("driver.current_site_owners",&values);record_vec("driver.current_direct_M",&direct_m);record_vec("driver.current_diagnostic_values",&diagnostic_values);
  for(j,(eta,q))in nodes.into_iter().enumerate(){
   let id=format!("{lane}:p{i}:q{j}");if !(eta>ab[0]&&eta<ab[1]&&q>0.){return Err(format!("invalid positive node {id}"));}
   c.scalar("node",&id,"eta",eta)?;c.scalar("node",&id,"eta_weight",q)?;
   let raw=frame.replay(eta,0,1,1,Tracked::empty(),true).map_err(|e|format!("{id}: {e}"))?;
   let coefficient=w(q)?;let weighted=EtaWeight(q).apply(raw)?;
   // Raw provenance and its physical geometric coefficient are retained. The
   // terminal bound is charged once here, never again as panel input uncertainty.
   for(term,x)in fields(raw).into_iter().enumerate(){charge(c,&mut ledger,lane,"terminal-point",&format!("p{i}:q{j}"),term,x.loss,coefficient)?;}
   let exact=canonical(weighted);direct_m.push(exact.n.mul(Tracked::exact(Wide::from_log(eta).map_err(err)?)).map_err(err)?);
   if let Some(ps)=projection{let p=ps.get(i).ok_or("missing diagnostic panel")?;let fp=p.density(eta)?;let fh=raw.n.value;let rates=frame.diagnostic_rates(eta,frame.times[4])?;let mut d=[Tracked::empty();10];for k in 0..4{d[k]=Tracked::exact(fp).scale(rates[k]).map_err(err)?.scale(q).map_err(err)?;d[k+4]=Tracked::exact(fh).scale(rates[k]).map_err(err)?.scale(q).map_err(err)?;}let df=positive_difference(fp,fh)?;d[8]=Tracked::exact(df).scale(q).map_err(err)?;d[9]=d[8].scale(EPS*(eta-frame.times[4]).exp()).map_err(err)?;diagnostic_values.push(d);}
   values.push(exact);record_vec("driver.current_site_owners",&values);record_vec("driver.current_direct_M",&direct_m);record_vec("driver.current_diagnostic_values",&diagnostic_values);
  }
  let panel_total=sum_owners(&values)?;let id=format!("{lane}:p{i}");c.owners("panel_owners",&id,panel_total)?;
  let direct=sorted_sum(&direct_m)?;
  if let Some(ref mut ps)=candidate{
   let front=ab[1]==*edges.last().ok_or("empty geometry")?;let endpoint=endpoint_pair(ab[0],ab[1],frame.times[4],panel_total,front).map_err(|e|format!("{id} endpoint_pair {e}; L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()))?;
   charge(c,&mut ledger,lane,"endpoint-N",&format!("p{i}"),0,endpoint.n_loss,w(1.)?)?;
   charge(c,&mut ledger,lane,"endpoint-M",&format!("p{i}"),1,endpoint.m_loss,energy_factor(frame.times[4])?)?;
   let p=Panel::from_owners(ab[0],ab[1],frame.times[4],panel_total,front,1).map_err(|e|format!("{id} reconstruction {e}; L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()))?;
   closure_audit(c,&id,&p,panel_total,direct.value,frame.times[4])?;ps.push(p);record_vec("driver.private_candidate_panels",ps);
  }else{for term in 0..2{let x=fields(panel_total)[term];charge(c,&mut ledger,lane,"panel-stock-construction",&format!("p{i}"),term,x.loss,w(1.)?)?;}}
  for(term,x)in fields(panel_total).into_iter().enumerate().skip(2){charge(c,&mut ledger,lane,"panel-owner-construction",&format!("p{i}"),term,x.loss,w(1.)?)?;}
  summaries.push(canonical(panel_total));record_vec(&format!("driver.{lane}.panel_owner_summaries"),&summaries);
  if projection.is_some(){let mut d=[Tracked::empty();10];for k in 0..10{let v:Vec<Tracked>=diagnostic_values.iter().map(|x|x[k]).collect();record_vec("driver.diagnostic_component_buffer",&v);d[k]=sorted_sum(&v)?;c.output("panel_diagnostic",&id,D_NAMES[k],d[k])?;}c.scalar("panel_diagnostic",&id,"normalized_local_photon_L1",if panel_total.n.value.is_empty(){0.}else{ratio(d[8].value,panel_total.n.value)?})?;c.scalar("panel_diagnostic",&id,"normalized_local_energy_L1",if panel_total.u.value.is_empty(){0.}else{ratio(d[9].value,panel_total.u.value)?})?;diagnostic_panels.push(d);record_vec(&format!("driver.{lane}.diagnostic_panel_summaries"),&diagnostic_panels);}
  count("quadrature_sites_retired",order);
 }
 let total=sum_owners(&summaries)?;
 // The 11-owner reduction becomes an authoritative increment, so only these
 // newly lost fields are committed. N/U reduction is a temporary stock cache.
 for(term,x)in fields(total).into_iter().enumerate().skip(2){charge(c,&mut ledger,lane,"retained11-reduction","base0",term,x.loss,w(1.)?)?;}
 let mut diag=[Tracked::empty();10];for k in 0..10{let v:Vec<Tracked>=diagnostic_panels.iter().map(|x|x[k]).collect();record_vec("driver.global_diagnostic_component",&v);diag[k]=sorted_sum(&v)?;}
 c.owners("global_owners",lane,total)?;emit_charges(c,&ledger)?;record_vec(&format!("driver.{lane}.charges"),&ledger.charges);c.flush()?;
 Ok(Lane{panels:summaries,total,ledger,diag})
}
fn ratio(a:Wide,b:Wide)->R<f64>{if a.is_empty(){Ok(0.)}else if b.is_empty(){Ok(f64::INFINITY)}else{Ok(rel(a,b)?+1.)}}
fn heat(c:&mut Csv,id:&str,o:Owners)->R<Wide>{let threshold=rei_microphysics::HHeModel::controlled_fixture().threshold_ev;let mut terms=Vec::with_capacity(3);for i in 0..3{let binding=o.a[i].value.mul(w(EPS*threshold[i])?).map_err(err)?;if !binding.le(o.b[i].value){return Err(format!("negative shared path heat species {i}"));}let x=positive_difference(o.b[i].value,binding)?;c.wide("path_heat",id,&format!("species{i}"),x)?;terms.push(Tracked::exact(x));}record_vec("driver.path_heat_terms",&terms);let total=sorted_sum(&terms)?;c.output("path_heat",id,"erg_per_H",total)?;Ok(total.value)}
fn local_row(c:&mut Csv,id:&str,incoming:[Wide;2],outgoing:[Wide;2],inc:[Wide;11],r:(f64,f64,Wide,Wide),loss:(Wide,Wide))->R<()>{for(key,x)in [("in.N",incoming[0]),("in.U",incoming[1]),("out.N",outgoing[0]),("out.U",outgoing[1])]{c.wide("local",id,key,x)?;}for(key,x)in NAMES[2..].iter().zip(inc){c.wide("local",id,key,x)?;}for(key,x)in [("rN",r.0),("rE",r.1)]{c.scalar("local",id,key,x)?;}for(key,x)in [("bN",r.2),("bE",r.3),("lossN",loss.0),("lossE",loss.1)]{c.wide("local",id,key,x)?;}Ok(())}
fn gate_budget(c:&mut Csv,id:&str,r:(f64,f64,Wide,Wide),loss:(Wide,Wide),inc:[Wide;11])->R<()>{let qn=inc[0].readout().map_err(err)?.0;let qe=inc[1].readout().map_err(err)?.0;let bn=r.2.upper_add(loss.0).map_err(err)?;let be=r.3.upper_add(loss.1).map_err(err)?;c.scalar("budget",id,"rN",r.0)?;c.scalar("budget",id,"rE",r.1)?;c.wide("budget",id,"temporary_N",r.2)?;c.wide("budget",id,"temporary_E",r.3)?;c.wide("budget",id,"committed_N",loss.0)?;c.wide("budget",id,"committed_E",loss.1)?;if !admit(r.0,bn,1e-10*qn.max(1e-10),1e-20).map_err(err)?||!admit(r.1,be,1e-10*qe.max(1e-20),1e-30).map_err(err)?{return Err(format!("{id} complete residual/loss/audit gate"));}Ok(())}
fn witness(frame:&Frame,panels:&[Panel],c:&mut Csv,reverse:bool)->R<()>{let l=frame.times[0]+frame.cfg.source.energy_min_ev.ln();let mut points=[("source_off",l+1e-5),("lower_u1e-7",l+1e-7),("lower_u1e-6",l+1e-6)];if reverse{points.reverse();}for(name,eta)in points{let id=format!("{}:{name}",if reverse{"reversed"}else{"forward"});let h=frame.replay(eta,0,1,1,Tracked::empty(),true)?;let p=panels.iter().find(|p|eta>=p.l&&eta<p.r).ok_or("witness outside retained support")?;let f=p.density(eta)?;let u=f.mul(w(EPS*(eta-frame.times[4]).exp())?).map_err(err)?;c.scalar("witness",&id,"eta",eta)?;c.output("witness",&id,"H.f",h.n)?;c.output("witness",&id,"H.U",h.u)?;c.output("witness",&id,"P.f",Tracked::exact(f))?;c.output("witness",&id,"P.U",Tracked::exact(u))?;c.scalar("witness",&id,"log_f_defect",f.log()-h.n.value.log())?;c.scalar("witness",&id,"local.L",p.l)?;c.scalar("witness",&id,"local.R",p.r)?;let[n,m]=p.moments()?;c.wide("witness",&id,"local.N",n)?;c.wide("witness",&id,"local.M",m)?;}
 let p=panels.last().ok_or("no frontier panel")?;let f=p.density(p.r)?;c.wide("front_trace",if reverse{"reversed"}else{"forward"},"density",f)?;if !p.front||!f.is_empty(){return Err("front trace or tag gate".into());}Ok(())}
fn snapshot(panels:&[Panel],ledger:&Ledger)->u64{use std::hash::{Hash,Hasher};let mut h=std::collections::hash_map::DefaultHasher::new();for p in panels{p.l.to_bits().hash(&mut h);p.r.to_bits().hash(&mut h);let(k,n,m)=p.pair.components();k.hash(&mut h);n.to_bits().hash(&mut h);m.to_bits().hash(&mut h);p.closure.beta.to_bits().hash(&mut h);p.closure.l.to_bits().hash(&mut h);p.closure.r.to_bits().hash(&mut h);p.closure.n.to_bits().hash(&mut h);p.closure.front.hash(&mut h);let(ln,lm)=p.pair.logs();ln.to_bits().hash(&mut h);lm.to_bits().hash(&mut h);for x in p.incoming_loss_metadata{x.mantissa().to_bits().hash(&mut h);x.exponent().hash(&mut h);}p.front.hash(&mut h);p.provenance.hash(&mut h);}for inc in &ledger.increments{for x in inc{x.mantissa().to_bits().hash(&mut h);x.exponent().hash(&mut h);}}for x in &ledger.charges{x.lane.hash(&mut h);x.transition.hash(&mut h);x.boundary.hash(&mut h);x.id.hash(&mut h);x.term.hash(&mut h);x.bound.mantissa().to_bits().hash(&mut h);x.bound.exponent().hash(&mut h);x.coefficient.mantissa().to_bits().hash(&mut h);x.coefficient.exponent().hash(&mut h);}h.finish()}
fn run(c:&mut Csv,oracle:&mut Csv)->R<()>{
 let frame=Frame::new(128)?;let s0=frame.times[0];let s1=frame.times[4];let lo=(s0+frame.cfg.source.energy_min_ev.ln()).max(s1+13.6f64.ln());let hi=s1+frame.cfg.source.energy_max_ev.ln();
 for(j,s)in frame.times.iter().enumerate(){c.scalar("lattice",&format!("t{j}"),"s",*s)?;}for(j,x)in frame.mesh.iter().enumerate(){c.scalar("persistent_mesh",&format!("g{j}"),"eta",*x)?;}
 let mut edges=Vec::with_capacity(258);edges.push(lo);for x in &frame.mesh{if *x>lo&&*x<hi{edges.push(*x);}}edges.push(hi);record_vec("driver.occupied_edges",&edges);if edges.len()-1>256{return Err("actual occupied panel cap".into());}
 // frame.mesh already includes every transformed edge for all 17 stored epochs;
 // this is the exact union required by H1, with its own counted C_ref.
 count("reference_topology_cells",edges.len()-1);for(i,ab)in edges.windows(2).enumerate(){c.scalar("occupied_support",&format!("p{i}"),"L",ab[0])?;c.scalar("occupied_support",&format!("p{i}"),"R",ab[1])?;if ab[1]-ab[0]<1e-7{return Err(format!("unsupported persistent width panel={i} L={:016x} R={:016x}",ab[0].to_bits(),ab[1].to_bits()));}}
 let mut accepted=Vec::<Panel>::with_capacity(256);let mut committed=Ledger::default();record_vec("driver.old_panels",&accepted);let before=snapshot(&accepted,&committed);
 inventory(oracle,"B128_m1:initial",&accepted,s0)?;inventory(oracle,"B128_m1:in:0",&accepted,s0)?;let(incoming,in_bound)=stock_cache(&accepted,s0)?;
 c.owners("initial_stock_control","exact_empty",Owners::empty())?;println!("INITIAL_STOCK_CONTROL=EXACT_EMPTY_NOT_APPLICABLE; moment J2/J4 have zero initial-stock sites");
 let qlo=source_lane(&frame,c,"Qlo8",8,&edges,None,None)?;
 let mut candidate=Vec::<Panel>::with_capacity(256);record_vec("driver.private_candidate_panels",&candidate);
 let qhi=source_lane(&frame,c,"Qhi16",16,&edges,Some(&mut candidate),None)?;
 for i in 0..qhi.panels.len(){compare_panel(c,&format!("Qlo_Qhi:p{i}"),qlo.panels[i],qhi.panels[i])?;}
 require_relative(c,"Qlo8_Qhi16",qlo.total,qhi.total,1e-6)?;drop(qlo);println!("QUADRATURE_QLO_QHI=PASS");
 let href16=source_lane(&frame,c,"H1_G16",16,&edges,None,Some(&candidate))?;
 let href32=source_lane(&frame,c,"H1_G32",32,&edges,None,Some(&candidate))?;
 require_relative(c,"H1_G16_G32",href16.total,href32.total,1e-6)?;
 for i in 0..href32.panels.len(){compare_panel(c,&format!("H16_H32:p{i}"),href16.panels[i],href32.panels[i])?;compare_panel(c,&format!("Qhi_H32:p{i}"),qhi.panels[i],href32.panels[i])?;}
 println!("REFERENCE_H1_TIGHTENING=PASS");
 let heat_q=heat(c,"Qhi16",qhi.total)?;let heat_h16=heat(c,"H1_G16",href16.total)?;let heat_h32=heat(c,"H1_G32",href32.total)?;physical_agreement(c,"shared_path_heat_projection",heat_q,heat_h32,1e-20,1.)?;physical_agreement(c,"shared_path_heat_tightening",heat_h16,heat_h32,1e-20,0.1)?;
 // Same-m owner/stock comparison retains the original dimensional allowances.
 for(j,(a,b))in fields(qhi.total).into_iter().zip(fields(href32.total)).enumerate(){physical_agreement(c,&format!("Qhi_H32:{}",NAMES[j]),a.value,b.value,if photon_term(j){1e-8}else{1e-20},1.)?;physical_agreement(c,&format!("H16_H32_allowance:{}",NAMES[j]),fields(href16.total)[j].value,b.value,if photon_term(j){1e-8}else{1e-20},0.1)?;}
 for k in 0..10{c.output("endpoint_diagnostic","G16",D_NAMES[k],href16.diag[k])?;c.output("endpoint_diagnostic","G32",D_NAMES[k],href32.diag[k])?;}
 for k in 0..8{let a=href16.diag[k].value;let b=href32.diag[k].value;let d=if b.is_empty(){if a.is_empty(){0.}else{f64::INFINITY}}else{rel(a,b)?.abs()};c.scalar("diagnostic_tightening","G16_G32",D_NAMES[k],d)?;if k%4==3 {if d>1e-6{return Err(format!("Hdot tightening {}",D_NAMES[k]));}}else{physical_agreement(c,&format!("Gamma_tightening:{}",D_NAMES[k]),a,b,1e-22,0.1)?;}}
 for k in 0..3{physical_agreement(c,&format!("Gamma_projection:{k}"),href32.diag[k].value,href32.diag[k+4].value,1e-22,1.)?;}
 let hdot=if href32.diag[7].value.is_empty(){if href32.diag[3].value.is_empty(){0.}else{f64::INFINITY}}else{rel(href32.diag[3].value,href32.diag[7].value)?.abs()};c.scalar("shape","Hdot","relative",hdot)?;if hdot>1e-3{return Err("instantaneous Hdot projection gate".into());}
 for(k,reference,abs)in [(8,href32.total.n.value,1e-8),(9,href32.total.u.value,1e-20)]{let allowance=w(abs)?.add(reference.mul(w(1e-3)?).map_err(err)?).map_err(err)?.0;c.wide("shape",D_NAMES[k],"allowance",allowance)?;if !href32.diag[k].value.le(allowance){return Err(format!("global {} gate",D_NAMES[k]));}physical_agreement(c,&format!("L1_tightening:{}",D_NAMES[k]),href16.diag[k].value,href32.diag[k].value,abs,0.1)?;}
 println!("PROJECTION_GLOBAL_SHAPE=PASS; LOCAL_WAKE_SHAPE_ADMISSION=NOT_CLAIMED");
 // Full local capture is based on stored canonical panels, not source U cache.
 inventory(oracle,"B128_m1:out:0",&candidate,s1)?;let(outgoing,out_bound)=stock_cache(&candidate,s1)?;let increment=retained(qhi.total);let loss=qhi.ledger.totals()?;
 let ms:Vec<Tracked>=candidate.iter().map(|p|p.moments().map(|x|Tracked::exact(x[1]))).collect::<R<Vec<_>>>()?;record_vec("driver.stored_M_audit",&ms);let stored_m=sorted_sum(&ms)?;let mfac=Wide::from_log(s1).map_err(err)?.mul(w(1./EPS)?).map_err(err)?;let reference_m=href32.total.u.value.mul(mfac).map_err(err)?;let m_allowance=w(1e-20)?.add(href32.total.u.value.mul(w(1e-3)?).map_err(err)?).map_err(err)?.0.mul(mfac).map_err(err)?;c.output("endpoint_M","projection","stored",stored_m)?;c.wide("endpoint_M","projection","reference",reference_m)?;c.wide("endpoint_M","projection","U_derived_allowance",m_allowance)?;if !positive_difference(stored_m.value,reference_m)?.le(m_allowance){return Err("stored M with U-derived allowance".into());}
 let(mut rn,mut re,mut bn,mut be)=residual(incoming,outgoing,increment)?;bn=bn.upper_add(in_bound[0]).map_err(err)?.upper_add(out_bound[0]).map_err(err)?;be=be.upper_add(in_bound[1]).map_err(err)?.upper_add(out_bound[1]).map_err(err)?;
 let local=(rn,re,bn,be);local_row(oracle,"B128_m1:0",incoming,outgoing,increment,local,loss)?;gate_budget(c,"local",local,loss,increment)?;
 // A fresh read of the candidate panel list and separate retained11 list. The
 // one-step telescope is intentionally trivial algebra, but not shared caches.
 let private_increments=[increment];let mut global_increment=[Wide::ZERO;11];let(mut gn,mut ge)=(Wide::ZERO,Wide::ZERO);
 for j in 0..11{let values:Vec<Tracked>=private_increments.iter().map(|v|Tracked::exact(v[j])).collect();record_vec("driver.global_increment_audit",&values);let total=sorted_sum(&values)?;global_increment[j]=total.value;if photon_term(j+2){gn=gn.upper_add(total.loss).map_err(err)?;}else{ge=ge.upper_add(total.loss).map_err(err)?;}}
 let(global_stock,global_stock_bounds)=stock_cache(&candidate,s1)?;let global_initial:[Wide;2]=[Wide::ZERO;2];(rn,re,bn,be)=residual(global_initial,global_stock,global_increment)?;bn=bn.upper_add(gn).map_err(err)?.upper_add(global_stock_bounds[0]).map_err(err)?;be=be.upper_add(ge).map_err(err)?.upper_add(global_stock_bounds[1]).map_err(err)?;let global=(rn,re,bn,be);gate_budget(c,"global",global,loss,global_increment)?;
 // Read-only observation order executes before accepted state can change.
 let observation_before=snapshot(&candidate,&qhi.ledger);witness(&frame,&candidate,c,false)?;witness(&frame,&candidate,c,true)?;if observation_before!=snapshot(&candidate,&qhi.ledger){return Err("observation order mutated candidate or ledger".into());}
 if before!=snapshot(&accepted,&committed){return Err("private candidate mutated accepted state".into());}
 committed.commit(increment,qhi.ledger.charges,true)?;accepted=candidate;record_vec("driver.accepted_panels",&accepted);
 inventory(oracle,"B128_m1:final",&accepted,s1)?;for(step,inc)in committed.increments.iter().enumerate(){for(key,x)in NAMES[2..].iter().zip(inc){oracle.wide("increment",&format!("B128_m1:{step}"),key,*x)?;}}
 for(key,x)in [("rN",global.0),("rE",global.1)]{oracle.scalar("global","B128_m1",key,x)?;}for(key,x)in [("bN",global.2),("bE",global.3),("lossN",committed.totals()?.0),("lossE",committed.totals()?.1)]{oracle.wide("global","B128_m1",key,x)?;}
 oracle.flush()?;c.flush()?;
 println!("LOCAL_GLOBAL_BUDGET=PASS; PRIVATE_COMMIT=PASS; OBSERVATION_ORDER=PASS");
 println!("ONE_INTERVAL_ONLY_IMPLEMENTATION_PARTIAL: first interval stored; high-precision physical canonical audit is still required before certification. This executable has no continuation implementation or predeclared upper-count workload for C/D. Resource feasibility must be assessed from these measured segment/fit counts and the parent aggregate receipt; no resource-exhaustion or matrix claim is made.");
 println!("COMMITTED_PANELS={}; COMMITTED_INCREMENTS={}; MODEL_UNRESOLVED",accepted.len(),committed.increments.len());Ok(())
}
fn main(){let result=(||->R<()>{let mut c=Csv::new("results/physical.csv")?;let mut oracle=Csv::new("results/physical_oracle.csv")?;let r=run(&mut c,&mut oracle);let _=c.flush();let _=oracle.flush();r})();let t=telemetry();println!("TELEMETRY live={} peak={} created={} retired={}",t.live,t.peak,t.created,t.retired);for(k,v)in t.counters{println!("COUNT {k} {v}");}for(k,(len,cap,size))in t.arrays{println!("ARRAY {k} used_hwm={len} capacity_hwm={cap} element_bytes={size} capacity_bytes={}",cap*size);}match result{Ok(())=>{},Err(e)=>{eprintln!("PHYSICAL_PARTIAL_NO_COMMIT: {e}");eprintln!("Earlier rows preserve exact attempted inputs and canonical values. Later mandatory gates are NOT_RUN; no failed panel is dropped or repaired. MODEL_UNRESOLVED");std::process::exit(1);}}}
