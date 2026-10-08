//! Exact-input unit evidence only. Run under the parent's aggregate supervisor.
//! Compilation/execution intentionally waits for the preserved RED gate.
#[path="lib.rs"] mod bridge;
use bridge::*;
use std::fs::File;
use std::io::{BufWriter, Write};

const NAMES:[&str;13]=["N","U","QN","QE","red","outN","outE","A_HI","A_HeI","A_HeII","B_HI","B_HeI","B_HeII"];
struct Csv<W:Write>{out:W}
impl<W:Write> Csv<W>{
 fn new(mut out:W)->R<Self>{writeln!(out,"kind,id,field,bits,exp").map_err(err)?;Ok(Self{out})}
 fn bits(&mut self,k:&str,id:&str,key:&str,m:f64,e:i32)->R<()>{writeln!(self.out,"{k},{id},{key},{:016x},{e}",m.to_bits()).map_err(err)}
 fn scalar(&mut self,k:&str,id:&str,key:&str,x:f64)->R<()>{self.bits(k,id,key,x,0)}
 fn wide(&mut self,k:&str,id:&str,key:&str,x:Wide)->R<()>{self.bits(k,id,key,x.mantissa(),x.exponent())}
 fn output(&mut self,k:&str,id:&str,key:&str,x:Tracked)->R<()>{
  let(v,b)=x.value.readout().map_err(err)?;
  self.wide(k,id,key,x.value)?;self.wide(k,id,&format!("{key}.loss"),x.loss)?;
  self.scalar(k,id,&format!("{key}.readout"),v)?;
  self.wide(k,id,&format!("{key}.readout_bound"),b)?;
  self.scalar(k,id,&format!("{key}.log"),x.value.log())
 }
 fn finish(&mut self)->R<()>{self.out.flush().map_err(err)}
}
fn w(x:f64)->R<Wide>{Wide::from_f64(x).map_err(err)}
fn t(x:f64)->R<Tracked>{Tracked::from_f64(x).map_err(err)}
fn exact(x:Wide)->Tracked{Tracked::exact(x)}
fn fields(o:Owners)->[Tracked;13]{[o.n,o.u,o.qn,o.qe,o.red,o.outn,o.oute,o.a[0],o.a[1],o.a[2],o.b[0],o.b[1],o.b[2]]}
fn retained(o:Owners)->[Wide;11]{let a=fields(o);std::array::from_fn(|i|a[i+2].value)}
fn segment_row<W:Write>(c:&mut Csv<W>,id:&str,f:Tracked,q:Tracked,r:[f64;3],h:f64,e:f64)->R<Owners>{
 let k="segment";c.wide(k,id,"f",f.value)?;c.wide(k,id,"q",q.value)?;
 for(i,x)in r.into_iter().enumerate(){c.scalar(k,id,&format!("r{i}"),x)?;}
 for(key,x)in [("h",h),("E",e),("EPS",EPS)]{c.scalar(k,id,key,x)?;}
 let o=segment(f,q,r,h,e).map_err(err)?;
 for(key,x)in NAMES.into_iter().zip(fields(o)){c.output(k,id,key,x)?;}Ok(o)
}
fn restriction_row<W:Write>(c:&mut Csv<W>,id:&str,input:ClosureInput,a:f64,b:f64,minsub:bool)->R<()>{
 let k=if minsub{"restriction_min_subnormal"}else{"restriction"};
 for(key,x)in [("L",input.l),("R",input.r),("beta",input.beta),("front",if input.front{1.}else{0.}),("a",a),("b",b)]{c.scalar(k,id,key,x)?;}
 c.wide(k,id,"n",input.n.value)?;
 let(n,m)=restrict(input,a,b).map_err(err)?;c.output(k,id,"N",n)?;c.output(k,id,"M",m)
}
fn add_row<W:Write>(c:&mut Csv<W>,id:&str,a:Wide,b:Wide,sign:Option<f64>)->R<()>{
 let(sum,loss)=a.add(b).map_err(err)?;
 for(key,x)in [("a",a),("b",b),("sum",sum),("loss",loss)]{c.wide("add",id,key,x)?;}
 if let Some(s)=sign{c.scalar("add",id,"residual_sign",s)?;}Ok(())
}
fn primitive_controls<W:Write>(c:&mut Csv<W>)->R<()>{
 let empty=Tracked::empty();let stock=t(0.125)?;let source=t(0.3)?;
 segment_row(c,"stock_normal",stock,empty,[2.,1.,0.],0.1,100.)?;
 segment_row(c,"source_normal",empty,source,[2.,1.,0.],0.1,100.)?;
 segment_row(c,"joint_normal",stock,source,[2.,1.,0.],0.1,100.)?;
 let tail=exact(Wide::from_parts(1.25,-1200).map_err(err)?);
 segment_row(c,"stock_zero_readout_tail",tail,empty,[1000.,200.,0.],0.1,100.)?;
 segment_row(c,"source_restart_with_tail",tail,source,[2.,1.,0.],0.1,100.)?;
 segment_row(c,"transparent_tail",tail,empty,[0.;3],0.01,100.)?;
 segment_row(c,"tiny_rate_joint",stock,source,[f64::from_bits(1),0.,0.],0.01,100.)?;
 segment_row(c,"zero_duration",stock,source,[2.,1.,0.],0.,100.)?;
 for front in [false,true]{
  for (j,beta) in [0.,-1.,-128.,128.].into_iter().enumerate(){
   let input=ClosureInput{l:0.,r:1.,beta,front,n:t(1.)?};
   restriction_row(c,&format!("interior_{}_{}",front as u8,j),input,0.2,0.8,false)?;
  }
  let input=ClosureInput{l:0.,r:1.,beta:0.,front,n:t(1.)?};
  restriction_row(c,&format!("one_ulp_{}",front as u8),input,0.5,0.5f64.next_up(),false)?;
  restriction_row(c,&format!("minimum_subnormal_{}",front as u8),input,0.,f64::from_bits(1),true)?;
  restriction_row(c,&format!("tail_shape_{}",front as u8),ClosureInput{n:tail,..input},0.2,0.8,false)?;
 }
 for(id,a,b)in [("equal",w(1.)?,w(1.)?),("near_cancel",w(1f64.next_up())?,w(1.)?),
  ("tail_difference",tail.value,Wide::from_parts(1.25,-1201).map_err(err)?),
  ("reverse_tail_difference",Wide::from_parts(1.25,-1201).map_err(err)?,tail.value)]{
  c.wide("difference",id,"a",a)?;c.wide("difference",id,"b",b)?;
  c.output("difference",id,"d",exact(positive_difference(a,b)?))?;
 }
 add_row(c,"suppressed_minuscule",w(1.)?,Wide::from_parts(1.,-1200).map_err(err)?,None)?;
 add_row(c,"suppressed_half_ulp",w(1.)?,Wide::from_parts(1.,-53).map_err(err)?,None)?;
 add_row(c,"retained_ulp",w(1.)?,Wide::from_parts(1.,-52).map_err(err)?,None)?;
 Ok(())
}
fn density_controls<W:Write>(c:&mut Csv<W>)->R<()>{
 // The target input is the actual committed pair and fitted closure cache.
 // The generating beta below is not emitted or treated as the fitted beta.
 for tail in [false,true]{for front in [false,true]{
  let n=exact(Wide::from_parts(1.25,if tail{-1200}else{0}).map_err(err)?);
  let input=ClosureInput{l:0.125,r:0.875,beta:if front{-1.}else{1.},front,n};
  let(nn,mm)=restrict(input,input.l,input.r).map_err(err)?;
  let mut owners=Owners::empty();owners.n=nn;owners.u=mm.scale(EPS).map_err(err)?;
  let panel=Panel::from_owners(input.l,input.r,0.,owners,front,17)?;
  let fit=panel.closure;let canonical_n=panel.moments()?[0];
  for(j,eta)in [fit.l,fit.l+(fit.r-fit.l)*0.25,fit.l+(fit.r-fit.l)*0.75,fit.r].into_iter().enumerate(){
   let id=format!("fitted_density_{}_{}_{}",tail as u8,front as u8,j);
   for(key,x)in [("L",fit.l),("R",fit.r),("beta",fit.beta),("front",if fit.front{1.}else{0.}),("eta",eta)]{c.scalar("density",&id,key,x)?;}
   c.wide("density",&id,"N",canonical_n)?;
   c.output("density",&id,"f",exact(panel.density(eta)?))?;
  }
 }}Ok(())
}
fn inventory<W:Write>(c:&mut Csv<W>,id:&str,p:&Panel,s:f64)->R<()>{
 // Read the actual stored common-scale pair, not an aggregate owner cache.
 let(k,n,m)=p.pair.components();
 c.scalar("inventory",id,"s",s)?;c.scalar("inventory",id,"EPS",EPS)?;
 c.wide("inventory",id,"p0.N",Wide::from_parts(n,k).map_err(err)?)?;
 c.wide("inventory",id,"p0.M",Wide::from_parts(m,k).map_err(err)?)
}
fn stock_cache(p:&Panel,s:f64)->R<[Wide;2]>{
 let[n,m]=p.moments()?;
 Ok([n,m.mul(Wide::from_log(-s).map_err(err)?).map_err(err)?.mul(w(EPS)?).map_err(err)?])
}
fn charge(step:usize,id:&str,term:usize,bound:Wide)->Charge{
 Charge{lane:"canonical_two_step".into(),transition:step,boundary:"unit-endpoint-or-owner".into(),id:id.into(),term,bound,coefficient:Wide::from_f64(1.).unwrap(),units:if [0,2,5,7,8,9].contains(&term){"photons/H"}else{"erg/H"}}
}
fn local_row<W:Write>(c:&mut Csv<W>,id:&str,incoming:[Wide;2],outgoing:[Wide;2],inc:[Wide;11],r:(f64,f64,Wide,Wide),loss:(Wide,Wide))->R<()>{
 for(key,x)in [("in.N",incoming[0]),("in.U",incoming[1]),("out.N",outgoing[0]),("out.U",outgoing[1])]{c.wide("local",id,key,x)?;}
 for(key,x)in NAMES[2..].iter().zip(inc){c.wide("local",id,key,x)?;}
 for(key,x)in [("rN",r.0),("rE",r.1)]{c.scalar("local",id,key,x)?;}
 for(key,x)in [("bN",r.2),("bE",r.3),("lossN",loss.0),("lossE",loss.1)]{c.wide("local",id,key,x)?;}Ok(())
}
fn telescope_control<W:Write>(c:&mut Csv<W>)->R<()>{
 // Manufactured fixed-epoch algebra control, not a physical source history.
 // It uses real reconstruction, restriction, loss accounting and retained owners.
 let lane="canonical_two_step";let s=0.;
 let init=ClosureInput{l:0.,r:1.,beta:0.,front:true,n:t(1e-10)?};
 let(n,m)=restrict(init,0.,1.).map_err(err)?;let mut io=Owners::empty();io.n=n;io.u=m.scale(EPS).map_err(err)?;
 let mut panel=Panel::from_owners(0.,1.,s,io,true,1)?;
 inventory(c,&format!("{lane}:initial"),&panel,s)?;
 let initial_cache=stock_cache(&panel,s)?;
 let mut committed=Ledger::default();
 for step in 0..2{
  inventory(c,&format!("{lane}:in:{step}"),&panel,s)?;
  let incoming=stock_cache(&panel,s)?;
  let mut private=Ledger::default();
  // Both returned primitive bounds are genuinely nonzero and are canonicalized
  // before their retained moments enter source injection and endpoint construction.
  let sliver=ClosureInput{l:0.,r:1.,beta:0.,front:true,n:t(1e-100)?};
  let sliver_b=2f64.powi(-54);
  let(raw_n,raw_m)=restrict(sliver,0.,sliver_b).map_err(err)?;
  if raw_n.loss.is_empty()||raw_m.loss.is_empty(){return Err("restriction did not create both required fresh losses".into());}
  restriction_row(c,&format!("fresh_construction_{step}"),sliver,0.,sliver_b,false)?;
  let(sn,sm,_eta)=private.canonical_restrict(sliver,0.,sliver_b,s,&format!("fresh-{step}"))?;
  if !sn.loss.is_empty()||!sm.loss.is_empty(){return Err("restriction did not canonicalize before weighting".into());}
  for x in &mut private.charges{x.lane=lane.into();x.transition=step;}
  if private.charges.len()!=2{return Err("fresh restriction must book N and M once each".into());}
  let qfac=if step==0{0.5}else{2f64.powi(-100)};
  let afac=if step==0{2f64.powi(-100)}else{0.25};
  let source_n=exact(incoming[0]).scale(qfac).map_err(err)?;
  let source_u=exact(incoming[1]).scale(qfac).map_err(err)?;
  let sliver_u=sm.scale(EPS).map_err(err)?;
  let mut o=Owners::empty();
  o.qn=sorted_sum(&[source_n,sn])?;
  o.qe=sorted_sum(&[source_u,sliver_u])?;
  o.a[0]=exact(incoming[0]).scale(afac).map_err(err)?;
  o.b[0]=exact(incoming[1]).scale(afac).map_err(err)?;
  // The below-first-ulp tiny sink is intentionally absent from the binary64
  // retained fraction at step zero; its actual signed residual stays observable.
  let remaining=1.-afac;
  o.n=sorted_sum(&[exact(incoming[0]).scale(remaining).map_err(err)?,source_n,sn])?;
  o.u=sorted_sum(&[exact(incoming[1]).scale(remaining).map_err(err)?,source_u,sliver_u])?;
  let endpoint=endpoint_pair(0.,1.,s,o,true).map_err(err)?;
  private.charge(charge(step,"endpoint-N",0,endpoint.n_loss))?;
  let mut mc=charge(step,"endpoint-M",1,endpoint.m_loss);mc.coefficient=w(EPS)?;private.charge(mc)?;
  for(index,value)in fields(o).into_iter().enumerate().skip(2){private.charge(charge(step,&format!("owner-{index}"),index,value.loss))?;}
  let next=Panel::from_owners(0.,1.,s,o,true,1)?;
  inventory(c,&format!("{lane}:out:{step}"),&next,s)?;
  let outgoing=stock_cache(&next,s)?;let increment=retained(o);
  let actual_residual=residual(incoming,outgoing,increment)?;
  let new_loss=private.totals()?;
  local_row(c,&format!("{lane}:{step}"),incoming,outgoing,increment,actual_residual,new_loss)?;
  committed.commit(increment,private.charges,true)?;
  panel=next;
 }
 // Fresh final panel read and fresh authoritative increment-list read. Local
 // records above are not recomputed from either object.
 inventory(c,&format!("{lane}:final"),&panel,s)?;
 for(step,inc)in committed.increments.iter().enumerate(){
  for(key,value)in NAMES[2..].iter().zip(inc){c.wide("increment",&format!("{lane}:{step}"),key,*value)?;}
 }
 if committed.increments.len()!=2{return Err("canonical fixture must retain two increments".into());}
 let mut cache=[Wide::ZERO;11];let(mut bn,mut be)=(Wide::ZERO,Wide::ZERO);
 for j in 0..11{
  let values=[exact(committed.increments[0][j]),exact(committed.increments[1][j])];
  let sum=sorted_sum(&values)?;cache[j]=sum.value;
  if [0,3,5,6,7].contains(&j){bn=bn.upper_add(sum.loss).map_err(err)?;}else{be=be.upper_add(sum.loss).map_err(err)?;}
 }
 add_row(c,"source_cache_positive_defect",committed.increments[0][0],committed.increments[1][0],Some(-1.))?;
 add_row(c,"sink_cache_negative_defect",committed.increments[0][5],committed.increments[1][5],Some(1.))?;
 let current=stock_cache(&panel,s)?;let r=residual(initial_cache,current,cache)?;let loss=committed.totals()?;
 c.scalar("global",lane,"rN",r.0)?;c.scalar("global",lane,"rE",r.1)?;
 for(key,value)in [("bN",bn.upper_add(r.2).map_err(err)?),("bE",be.upper_add(r.3).map_err(err)?),("lossN",loss.0),("lossE",loss.1)]{c.wide("global",lane,key,value)?;}
 Ok(())
}
pub fn emit(path:&std::path::Path)->R<()>{
 let file=File::create(path).map_err(err)?;let mut c=Csv::new(BufWriter::with_capacity(8192,file))?;
 primitive_controls(&mut c)?;telescope_control(&mut c)?;density_controls(&mut c)?;c.finish()
}
pub fn emit_density(path:&std::path::Path)->R<()>{
 // Supplementary evidence must not overwrite the already accepted fixture file.
 let file=File::create_new(path).map_err(err)?;let mut c=Csv::new(BufWriter::with_capacity(8192,file))?;
 density_controls(&mut c)?;c.finish()
}
pub fn emit_witness(path:&std::path::Path)->R<()>{
 use rei_microphysics::{igm_photo::packet_opacity,igm_thermal::igm_point_rhs,verner_cutoff_ev,Absorber};
 let frame=physics::Frame::new(128)?;
 let species=[Absorber::HI,Absorber::HeI,Absorber::HeII];
 let(s0,s1)=(frame.times[0],frame.times[4]);
 let eta=s0+13.7f64.ln()+1e-5;
 let tau=eta-verner_cutoff_ev(species[0]).ln();
 if tau<=s0{return Err("source-off witness unexpectedly below initial opacity support".into());}
 let end=s1.min(tau);
 let _sites=SiteGuard::new(22)?;
 let mut cuts=Vec::with_capacity(22);cuts.push(s0);cuts.push(end);
 // m=1 uses the retained first-base endpoints, exactly as Frame::replay.
 for j in (0..=4).step_by(4){let s=frame.times[j];if s>s0&&s<end{cuts.push(s);}}
 for e in [frame.cfg.source.energy_min_ev,frame.cfg.source.energy_max_ev,verner_cutoff_ev(species[0]),verner_cutoff_ev(species[1]),verner_cutoff_ev(species[2])]{
  let event=eta-e.ln();if event>s0&&event<end{cuts.push(event);}
 }
 record_vec("witness.events.pre_dedup",&cuts);
 cuts.sort_by(f64::total_cmp);cuts.dedup_by(|a,b|*a==*b);record_vec("witness.events",&cuts);
 if cuts.len()>22{return Err("witness descriptor cap".into());}
 let source_start=eta-frame.cfg.source.energy_max_ev.ln();
 let source_stop=eta-frame.cfg.source.energy_min_ev.ln();
 let file=File::create_new(path).map_err(err)?;let mut c=Csv::new(BufWriter::with_capacity(8192,file))?;
 let(mut stock,mut last_u)=(Tracked::empty(),Tracked::empty());
 let(mut active,mut dark)=(0,0);
 for(index,ab)in cuts.windows(2).enumerate(){
  let(a,b)=(ab[0],ab[1]);let h=b-a;let mid=(a+b)*0.5;
  if h<1e-12||h>2.||!(mid>a&&mid<b){return Err("unsupported witness segment geometry".into());}
  let p=frame.cfg.background.at_ln_a(mid).map_err(err)?;count("background_calls",1);
  frame.gas.eos(p.n_h_cm3,p.n_he_cm3).map_err(err)?;count("eos_calls",1);
  igm_point_rhs(&frame.gas,p.n_h_cm3,p.n_he_cm3,p.hubble_per_s,p.tcmb_k,Default::default()).map_err(err)?;count("zero_photo_rhs_calls",1);
  let energy_mid=(eta-mid).exp();
  let opacity=packet_opacity(&frame.gas,energy_mid,p.n_h_cm3,p.n_he_cm3).map_err(err)?;count("opacity_calls",1);
  let rates=std::array::from_fn(|i|opacity[i]/p.hubble_per_s);
  let is_active=mid>=source_start&&mid<source_stop;
  let q=if is_active{frame.cfg.source.photons_per_h_per_s/((1./frame.cfg.source.energy_min_ev-1./frame.cfg.source.energy_max_ev)*energy_mid*p.hubble_per_s)}else{0.};
  if is_active{active+=1;}else{dark+=1;}
  let(energy_start,_)=start_energy(eta,a,b)?;
  if index>0{
   let beginning=stock.scale(energy_start).map_err(err)?.scale(EPS).map_err(err)?;
   let(lo,hi)=if last_u.value.le(beginning.value){(last_u.value,beginning.value)}else{(beginning.value,last_u.value)};
   if rel(lo,hi)?.abs()>2e-12{return Err("witness carried energy discontinuity".into());}
  }
  if !stock.loss.is_empty(){return Err("exact-input witness unexpectedly carries amplitude loss".into());}
  let id=format!("actual_source_off_witness_{index}");count("characteristic_segments",1);
  let o=segment_row(&mut c,&id,stock,t(q)?,rates,h,energy_start)?;
  // Preserve exact geometry/stage descriptors in the same segment record.
  for(key,x)in [("eta",eta),("s0",s0),("s1",s1),("a",a),("b",b),("mid",mid),("energy_mid",energy_mid),("source_active",if is_active{1.}else{0.})]{c.scalar("segment",&id,key,x)?;}
  if !o.a[2].value.is_empty()||!o.b[2].value.is_empty()||!o.outn.value.is_empty()||!o.oute.value.is_empty(){return Err("witness exact-zero owner invariant".into());}
  stock=o.n;last_u=o.u;
 }
 if end!=s1||active==0||dark==0{return Err("witness must include active and dark segments without physical export".into());}
 let replay=frame.replay(eta,0,1,1,Tracked::empty(),true)?;
 if replay.n!=stock||replay.u!=last_u{return Err("emitted witness endpoint differs from Frame::replay".into());}
 for(name,a,b)in [("N",stock.value,replay.n.value),("U",last_u.value,replay.u.value)]{
  let id=format!("actual_source_off_replay_{name}");c.wide("difference",&id,"a",a)?;c.wide("difference",&id,"b",b)?;
  c.output("difference",&id,"d",exact(positive_difference(a,b)?))?;
 }
 c.finish()?;
 eprintln!("WITNESS_REPLAY_PASS eta={:016x} s0={:016x} s1={:016x} active={active} dark={dark} segments={}",eta.to_bits(),s0.to_bits(),s1.to_bits(),cuts.len()-1);
 Ok(())
}
fn main()->R<()>{
 let mut args=std::env::args().skip(1);
 let path=args.next().unwrap_or_else(||"results/oracle.csv".into());
 if path=="--density-only"{let output=args.next().ok_or("density-only mode requires a new parent-designated output path")?;return emit_density(std::path::Path::new(&output));}
 if path=="--witness-only"{let output=args.next().ok_or("witness-only mode requires a new parent-designated output path")?;return emit_witness(std::path::Path::new(&output));}
 emit(std::path::Path::new(&path))
}
