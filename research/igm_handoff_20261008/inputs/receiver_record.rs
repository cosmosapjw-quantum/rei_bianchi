//! Observations of the existing NORMAL-domain midpoint calculation, never a new enclosure.
//! No provider/RHS/kernel call occurs in capture or replay. Original arithmetic owns science.
use crate::{coupled::State, diagnostics::{Trace,Summary}, material::MaterialOwners, radiation::Grid, v2::Owners, Fallible};
use rei_microphysics::{igm_background::FlrwPoint, igm_config::HistoryConfig, igm_thermal::IgmPointRhs};
use canonical::Wide;
use std::cell::{Cell,RefCell};
pub const AUTHORITY:&str="OBSERVED_BINARY64_OWNER_OPERANDS__KERNEL_PROVIDER_STATE_ERROR_UNRESOLVED__NOT_FULL_WIDE_ADMISSION";
pub const NAMES:[&str;13]=["N","U","QN","QE","red","outN","outE","A_HI","A_HeI","A_HeII","B_HI","B_HeI","B_HeII"];
pub fn fields(o:Owners)->[f64;13]{[o.n,o.u,o.qn,o.qe,o.red,o.outn,o.oute,o.an[0],o.an[1],o.an[2],o.be[0],o.be[1],o.be[2]]}
pub fn owner(a:[f64;13],ln_n:Option<f64>,ln_u:Option<f64>)->Owners{Owners{n:a[0],u:a[1],qn:a[2],qe:a[3],red:a[4],outn:a[5],oute:a[6],an:[a[7],a[8],a[9]],be:[a[10],a[11],a[12]],ln_n,ln_u}}
pub fn context(p:FlrwPoint)->[f64;8]{[p.a,p.redshift,p.hubble_per_s,p.n_h_cm3,p.n_he_cm3,p.tcmb_k,p.dt_dln_a_s,p.dt_dz_s]}
pub fn material_fields(m:MaterialOwners)->[f64;19]{[m.ci[0],m.ci[1],m.ci[2],m.rr[0],m.rr[1],m.rr[2],m.dr,m.escape,m.work,m.cmb,m.floor[0],m.floor[1],m.floor[2],m.cap[0],m.cap[1],m.cap[2],m.excluded_dr,m.nonphoto_binding,m.nonphoto_thermal]}
pub fn material_owner(a:[f64;19])->MaterialOwners{MaterialOwners{ci:[a[0],a[1],a[2]],rr:[a[3],a[4],a[5]],dr:a[6],escape:a[7],work:a[8],cmb:a[9],floor:[a[10],a[11],a[12]],cap:[a[13],a[14],a[15]],excluded_dr:a[16],nonphoto_binding:a[17],nonphoto_thermal:a[18]}}
fn rhs_fields(r:IgmPointRhs)->[f64;45]{let mut v=Vec::new();v.extend(r.fraction_dt);v.extend(r.species_chemical_cm3_s);v.extend([r.w_dt_erg_per_h_s,r.temperature_dt_k_s]);v.extend(r.photo_events_cm3_s);v.extend(r.ci_events_cm3_s);v.extend(r.rr_events_cm3_s);v.push(r.dr_events_cm3_s);v.extend(r.ci_thermal_sink_erg_cm3_s);v.extend(r.rr_thermal_sink_erg_cm3_s);v.push(r.dr_thermal_sink_erg_cm3_s);v.extend(r.ce_thermal_sink_erg_cm3_s);v.extend([r.freefree_thermal_sink_erg_cm3_s,r.thermal_micro_erg_cm3_s,r.binding_micro_erg_cm3_s,r.escape_erg_cm3_s,r.cmb_to_gas_erg_cm3_s,r.photo_input_erg_cm3_s,r.expansion_work_erg_cm3_s]);v.extend(r.ci_floor_events_cm3_s);v.extend(r.ce_cap_cooling_erg_cm3_s);v.push(r.excluded_dr_cooling_erg_cm3_s);v.try_into().unwrap()}
#[derive(Clone,Debug,PartialEq)]
pub struct Segment{pub node:usize,pub ordinal:usize,pub eta:f64,pub weight:f64,pub a:f64,pub b:f64,pub gas:[f64;4],pub background:[f64;8],pub incoming:f64,pub q:f64,pub rates:[f64;3],pub energy_start:f64,pub owners:[f64;13],pub dyadic:[Wide;13],pub ln_n:Option<f64>,pub ln_u:Option<f64>}
#[derive(Clone,Debug,PartialEq)]
pub struct Node{pub index:usize,pub owners:[f64;13],pub ln_n:Option<f64>,pub ln_u:Option<f64>}
#[derive(Clone,Debug,PartialEq)]
pub struct Accepted{pub s0:f64,pub s1:f64,pub y0:[f64;4],pub y1:[f64;4],pub midpoint:f64,pub midpoint_gas:[f64;4],pub midpoint_background:[f64;8],pub rhs:[f64;45],pub segments:Vec<Segment>,pub nodes:Vec<Node>,pub total:[f64;13],pub material:[f64;19]}
thread_local!{static ENABLED:Cell<bool>=const{Cell::new(false)};static DRAFT:RefCell<Option<Accepted>>=const{RefCell::new(None)};static NODE:Cell<(usize,f64)>=const{Cell::new((0,0.))};}
pub fn set_enabled(on:bool){ENABLED.with(|x|x.set(on));DRAFT.with(|x|*x.borrow_mut()=None)}
pub fn begin(s0:f64,s1:f64,y0:[f64;4],y1:[f64;4]){DRAFT.with(|x|*x.borrow_mut()=if ENABLED.with(Cell::get){Some(Accepted{s0,s1,y0,y1,midpoint:0.,midpoint_gas:[0.;4],midpoint_background:[0.;8],rhs:[0.;45],segments:Vec::new(),nodes:Vec::new(),total:[0.;13],material:[0.;19]})}else{None});}
pub fn midpoint(sm:f64,y:[f64;4],p:FlrwPoint,r:IgmPointRhs){DRAFT.with(|x|if let Some(x)=x.borrow_mut().as_mut(){x.midpoint=sm;x.midpoint_gas=y;x.midpoint_background=context(p);x.rhs=rhs_fields(r)})}
pub fn node(j:usize,w:f64){NODE.with(|x|x.set((j,w)))}
pub fn segment(eta:f64,a:f64,b:f64,gas:[f64;4],p:FlrwPoint,incoming:f64,q:f64,rates:[f64;3],energy_start:f64,o:Owners)->Fallible<()>{DRAFT.with(|x|if let Some(x)=x.borrow_mut().as_mut(){let(j,w)=NODE.with(Cell::get);let values=fields(o);if x.segments.len()>=16384{return Err("RECORD_SEGMENT_CAP".into())}let mut dyadic=[Wide::ZERO;13];for i in 0..13{dyadic[i]=Wide::from_f64(values[i]).map_err(crate::err)?;}x.segments.push(Segment{node:j,ordinal:x.segments.len(),eta,weight:w,a,b,gas,background:context(p),incoming,q,rates,energy_start,owners:values,dyadic,ln_n:o.ln_n,ln_u:o.ln_u});Ok(())}else{Ok(())})}
pub fn node_output(index:usize,o:Owners){DRAFT.with(|x|if let Some(x)=x.borrow_mut().as_mut(){x.nodes.push(Node{index,owners:fields(o),ln_n:o.ln_n,ln_u:o.ln_u})})}
pub fn finish(o:Owners,m:MaterialOwners)->Fallible<Option<Accepted>>{let mut x=DRAFT.with(|x|x.borrow_mut().take());if let Some(x)=x.as_mut(){if x.segments.len()>16384||x.nodes.len()>4096{return Err("RECORD_CAP".into())}x.total=fields(o);x.material=material_fields(m);}Ok(x)}
pub fn bits_eq(a:&[f64],b:&[f64])->bool{a.len()==b.len()&&a.iter().zip(b).all(|(x,y)|x.to_bits()==y.to_bits())}
/// Named canonical observations retain occurrence/coefficient/unit identity BEFORE eta aggregation.
/// Unknown original numerical error is explicitly UNKNOWN, never manufactured as a zero bound.
pub fn provenance(s:&Segment,transaction:usize,term:usize)->Fallible<(String,Wide,Wide,&'static str,&'static str)>{if term>=13{return Err("OWNER_NAME".into())}let units=if [0,2,5,7,8,9].contains(&term){"photons/H/unit_eta"}else{"erg/H/unit_eta"};Ok((format!("tx{transaction}/node{}/segment{}/{}",s.node,s.ordinal,NAMES[term]),s.dyadic[term],Wide::from_f64(s.weight).map_err(|e|e.to_string())?,units,AUTHORITY))}
/// Replay existing returned owners in the original node/weight order; no new scientific evaluations.
/// This is recorded-result replay, not re-solving or an independent accuracy reference.
fn rhs_owner(a:[f64;45])->IgmPointRhs{
 IgmPointRhs{fraction_dt:a[0..3].try_into().unwrap(),species_chemical_cm3_s:a[3..9].try_into().unwrap(),w_dt_erg_per_h_s:a[9],temperature_dt_k_s:a[10],photo_events_cm3_s:a[11..14].try_into().unwrap(),ci_events_cm3_s:a[14..17].try_into().unwrap(),rr_events_cm3_s:a[17..20].try_into().unwrap(),dr_events_cm3_s:a[20],ci_thermal_sink_erg_cm3_s:a[21..24].try_into().unwrap(),rr_thermal_sink_erg_cm3_s:a[24..27].try_into().unwrap(),dr_thermal_sink_erg_cm3_s:a[27],ce_thermal_sink_erg_cm3_s:a[28..31].try_into().unwrap(),freefree_thermal_sink_erg_cm3_s:a[31],thermal_micro_erg_cm3_s:a[32],binding_micro_erg_cm3_s:a[33],escape_erg_cm3_s:a[34],cmb_to_gas_erg_cm3_s:a[35],photo_input_erg_cm3_s:a[36],expansion_work_erg_cm3_s:a[37],ci_floor_events_cm3_s:a[38..41].try_into().unwrap(),ce_cap_cooling_erg_cm3_s:a[41..44].try_into().unwrap(),excluded_dr_cooling_erg_cm3_s:a[44]}
}
pub fn replay(cfg:&HistoryConfig,grid:&Grid,records:&[Accepted],initial_y:[f64;4])->Fallible<(Vec<f64>,Owners,MaterialOwners,[f64;4],f64)>{
 if records.is_empty()||records.len()>2{return Err("SHORT_RECORD_WINDOW".into())}
 let mut y=initial_y;let mut time=cfg.start;let mut density:Vec<f64>=vec![0.;grid.nodes.len()];let mut radiation=Owners::default();let mut material=MaterialOwners::default();
 for(t,r)in records.iter().enumerate(){
  if r.s0.to_bits()!=time.to_bits()||r.s1.to_bits()!=crate::radiation::time_at(cfg,t+1,192).to_bits()||!bits_eq(&r.y0,&y)||r.midpoint.to_bits()!=((r.s0+r.s1)*0.5).to_bits()||!bits_eq(&r.midpoint_gas,&std::array::from_fn::<_,4,_>(|i|(r.y0[i]+r.y1[i])*0.5)){return Err("EXACT_GAS_CLOCK_CONTEXT".into())}
  // Pure FLRW metadata and algebra only: never call material::rhs, opacity or the kernel.
  let pm=cfg.background.at_ln_a(r.midpoint).map_err(crate::err)?;
  if !bits_eq(&context(pm),&r.midpoint_background){return Err("MIDPOINT_BACKGROUND_CONTEXT".into())}
  let raw=rhs_owner(r.rhs);let reconstructed=MaterialOwners::stage(raw,pm,r.s1-r.s0)?;
  if !bits_eq(&material_fields(reconstructed),&r.material)||raw.photo_events_cm3_s!=[0.;3]||raw.photo_input_erg_cm3_s!=0.{return Err("MIDPOINT_RHS_OWNER_CONTEXT".into())}
  if r.nodes.len()!=grid.nodes.len(){return Err("NODE_CONTEXT".into())}
  let mut index=0;let mut next=Vec::new();let mut total=Owners::default();
  for(j,&(eta,w))in grid.nodes.iter().enumerate(){
   let tau=eta-rei_microphysics::verner_cutoff_ev(crate::radiation::SPECIES[0]).ln();let end=r.s1.min(tau);
   let mut sum=Owners::default();let mut stock=density[j];let mut last_u=None;
   if tau>r.s0{
    let source_start=eta-cfg.source.energy_max_ev.ln();let source_stop=eta-cfg.source.energy_min_ev.ln();let mut events=vec![source_start,source_stop];for a in crate::radiation::SPECIES{events.push(eta-rei_microphysics::verner_cutoff_ev(a).ln())}
    let cuts=crate::v2::topology(r.s0,end,&events);
    for ab in cuts.windows(2){
     let seg=r.segments.get(index).ok_or("MISSING_SEGMENT")?;let(a,b)=(ab[0],ab[1]);let mid=(a+b)*0.5;let theta=(mid-r.s0)/(r.s1-r.s0);
     let p=cfg.background.at_ln_a(mid).map_err(crate::err)?;let e=(eta-mid).exp();let q=if mid>=source_start&&mid<source_stop{cfg.source.photons_per_h_per_s/((1./cfg.source.energy_min_ev-1./cfg.source.energy_max_ev)*e*p.hubble_per_s)}else{0.};let(energy_start,_)=crate::event_anchor::start_energy(eta,a,b)?;
     if seg.ordinal!=index||seg.node!=j||seg.eta.to_bits()!=eta.to_bits()||seg.weight.to_bits()!=w.to_bits()||seg.a.to_bits()!=a.to_bits()||seg.b.to_bits()!=b.to_bits()||seg.incoming.to_bits()!=stock.to_bits()||!bits_eq(&seg.gas,&crate::radiation::affine(r.y0,r.y1,theta))||!bits_eq(&seg.background,&context(p))||seg.q.to_bits()!=q.to_bits()||seg.energy_start.to_bits()!=energy_start.to_bits(){return Err("AFFINE_SOURCE_SEGMENT_CONTEXT".into())}
     for k in 0..13{if seg.dyadic[k]!=Wide::from_f64(seg.owners[k]).map_err(crate::err)?{return Err("CANONICAL_OBSERVATION_MISMATCH".into())}let _=provenance(seg,t,k)?;}
     if seg.rates.iter().any(|x|*x<0.||!x.is_finite()){return Err("OBSERVED_OPACITY_DOMAIN".into())}
     stock=seg.owners[0];last_u=Some(seg.owners[1]);let mut inc=owner(seg.owners,None,None);inc.n=0.;inc.u=0.;crate::v2::try_add_scaled(&mut sum,inc,1.).map_err(crate::err)?;index+=1;
    }
    if tau<=r.s1{sum.outn=stock;sum.oute=crate::product(crate::product(crate::v2::EPS,rei_microphysics::verner_cutoff_ev(crate::radiation::SPECIES[0]))?,stock)?;}else{sum.n=stock;sum.u=last_u.unwrap_or(0.);if stock>0.{sum.ln_n=Some(stock.ln());sum.ln_u=Some(sum.u.ln())}}
   }else if stock!=0.{return Err("UNSUPPORTED_INITIAL_OUTFLOW".into())}
   let n=&r.nodes[j];if n.index!=j||!bits_eq(&fields(sum),&n.owners)||sum.ln_n.map(f64::to_bits)!=n.ln_n.map(f64::to_bits)||sum.ln_u.map(f64::to_bits)!=n.ln_u.map(f64::to_bits){return Err("SEGMENT_NODE_OWNER_MISMATCH".into())}
   next.push(sum.n);crate::v2::try_add_scaled(&mut total,sum,w).map_err(crate::err)?;
  }
  if index!=r.segments.len()||!bits_eq(&fields(total),&r.total){return Err("ORIGINAL_ORDER_REPLAY_MISMATCH".into())}
  total.n=0.;total.u=0.;total.ln_n=None;total.ln_u=None;crate::v2::try_add_scaled(&mut radiation,total,1.).map_err(crate::err)?;material=material.plus(reconstructed)?;density=next;y=r.y1;time=r.s1;
 }
 Ok((density,radiation,material,y,time))
}
pub fn verify_state(cfg:&HistoryConfig,grid:&Grid,state:&State,initial_y:[f64;4])->Fallible<()>{let(d,o,m,y,s)=replay(cfg,grid,&state.accepted_records,initial_y)?;if !bits_eq(&d,&state.density)||!bits_eq(&fields(o),&fields(state.radiation))||!bits_eq(&material_fields(m),&material_fields(state.material))||!bits_eq(&y,&state.y)||s.to_bits()!=state.s.to_bits(){return Err("TYPED_REPLAY_STATE_MISMATCH".into())}let last=state.accepted_records.last().unwrap();if state.accepted_trace.stages[0].count!=1||state.accepted_trace.stages[1].count!=1||state.accepted_trace.stages[2].count!=last.segments.len(){return Err("ACCEPTED_TRIAL_SEPARATION".into())}if !bits_eq(&state.active,&last.total[..2]){return Err("ACTIVE_OWNER_MISMATCH".into())}Ok(())}
pub fn science_image(s:&State)->String{format!("{:?}\n{:?}\n{:?}\n{:?}\n{:?}\n{:?}\n{:?}\n{:?}\n{:?}\n{:?}\n",s.s,s.y,&s.density,(s.active,s.radiation),s.material,(s.iterations,s.norm),(s.n_ratio,s.e_ratio),s.accepted_trace,s.trial_trace,AUTHORITY)}
pub struct W(pub Vec<u8>);
impl W{pub fn n(&mut self,x:u64){self.0.extend(x.to_le_bytes())}pub fn f(&mut self,x:f64){self.n(x.to_bits())}pub fn a(&mut self,x:&[f64]){for v in x{self.f(*v)}}pub fn text(&mut self,x:&str){self.n(x.len()as u64);self.0.extend(x.as_bytes())}pub fn option(&mut self,x:Option<f64>){self.n(x.is_some()as u64);if let Some(x)=x{self.f(x)}}pub fn wide(&mut self,x:Wide){self.f(x.mantissa());self.n(x.exponent()as i64 as u64)}}
pub struct D<'a>{pub b:&'a[u8],pub i:usize}
impl<'a>D<'a>{pub fn take(&mut self,n:usize)->Fallible<&'a[u8]>{let end=self.i.checked_add(n).ok_or("SIZE_OVERFLOW")?;let b=self.b.get(self.i..end).ok_or("INCOMPLETE_RECORD")?;self.i=end;Ok(b)}pub fn n(&mut self)->Fallible<u64>{Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap()))}pub fn size(&mut self,cap:usize)->Fallible<usize>{let n=usize::try_from(self.n()?).map_err(crate::err)?;if n>cap{return Err("SCHEMA_CAP".into())}Ok(n)}pub fn raw(&mut self)->Fallible<f64>{let x=f64::from_bits(self.n()?);if x.is_nan(){return Err("NAN_RECORD".into())}Ok(x)}pub fn f(&mut self)->Fallible<f64>{let x=self.raw()?;if !x.is_finite(){return Err("NONFINITE_RECORD".into())}Ok(x)}pub fn a<const N:usize>(&mut self)->Fallible<[f64;N]>{let mut a=[0.;N];for x in &mut a{*x=self.f()?}Ok(a)}pub fn text(&mut self,cap:usize)->Fallible<String>{let n=self.size(cap)?;String::from_utf8(self.take(n)?.to_vec()).map_err(crate::err)}pub fn option(&mut self)->Fallible<Option<f64>>{match self.n()?{0=>Ok(None),1=>Ok(Some(self.f()?)),_=>Err("OPTION_TAG".into())}}pub fn wide(&mut self)->Fallible<Wide>{let m=self.f()?;let k=i32::try_from(self.n()?as i64).map_err(crate::err)?;let w=Wide::from_parts(m,k).map_err(crate::err)?;if w.mantissa().to_bits()!=m.to_bits()||w.exponent()!=k{return Err("NONCANONICAL_DYADIC".into())}Ok(w)}}
fn write_trace(w:&mut W,t:Trace){for s in t.stages{w.n(s.count as u64);w.a(&[s.min,s.max]);w.n(s.any as u64);w.n(s.all as u64)}w.f(t.continuity_max_relative);w.n(t.continuity_checks as u64)}
fn read_trace(d:&mut D)->Fallible<Trace>{let mut stages=[Summary::default();3];for s in &mut stages{let count=d.size(10000000)?;let min=d.raw()?;let max=d.f()?;if (count==0&&min!=f64::INFINITY)||(count>0&&(!min.is_finite()||min>max)){return Err("TRACE_DOMAIN".into())}*s=Summary{count,min,max,any:u16::try_from(d.n()?).map_err(crate::err)?,all:u16::try_from(d.n()?).map_err(crate::err)?}}Ok(Trace{stages,continuity_max_relative:d.f()?,continuity_checks:d.size(10000000)?})}
pub fn write_state(w:&mut W,s:&State){w.f(s.s);w.a(&s.y);w.n(s.density.len()as u64);w.a(&s.density);w.a(&s.active);w.a(&fields(s.radiation));w.option(s.radiation.ln_n);w.option(s.radiation.ln_u);w.a(&material_fields(s.material));w.n(s.iterations as u64);w.a(&[s.norm,s.n_ratio,s.e_ratio]);write_trace(w,s.accepted_trace);write_trace(w,s.trial_trace);w.n(s.accepted_records.len()as u64);
 write_records(w,&s.accepted_records);
}
fn write_records(w:&mut W,records:&[Accepted]){
 for r in records{w.a(&[r.s0,r.s1]);w.a(&r.y0);w.a(&r.y1);w.f(r.midpoint);w.a(&r.midpoint_gas);w.a(&r.midpoint_background);w.a(&r.rhs);w.a(&r.total);w.a(&r.material);w.n(r.segments.len()as u64);for s in &r.segments{w.n(s.node as u64);w.n(s.ordinal as u64);w.a(&[s.eta,s.weight,s.a,s.b]);w.a(&s.gas);w.a(&s.background);w.a(&[s.incoming,s.q]);w.a(&s.rates);w.f(s.energy_start);w.a(&s.owners);for x in s.dyadic{w.wide(x)}w.option(s.ln_n);w.option(s.ln_u)}w.n(r.nodes.len()as u64);for n in &r.nodes{w.n(n.index as u64);w.a(&n.owners);w.option(n.ln_n);w.option(n.ln_u)}}
}
pub fn same_records(a:&[Accepted],b:&[Accepted])->bool{let mut x=W(Vec::new());let mut y=W(Vec::new());write_records(&mut x,a);write_records(&mut y,b);x.0==y.0}
pub fn state_bytes(s:&State)->Vec<u8>{let mut w=W(Vec::new());write_state(&mut w,s);w.0}
pub fn read_state(d:&mut D)->Fallible<State>{let s=d.f()?;let y=d.a()?;let n=d.size(4096)?;let mut density=Vec::new();for _ in 0..n{density.push(d.f()?)}let active=d.a()?;let vals=d.a()?;let ln_n=d.option()?;let ln_u=d.option()?;let radiation=owner(vals,ln_n,ln_u);let material=material_owner(d.a()?);let iterations=d.size(16)?;let [norm,n_ratio,e_ratio]=d.a()?;let accepted_trace=read_trace(d)?;let trial_trace=read_trace(d)?;let count=d.size(2)?;let mut accepted_records=Vec::new();
 for _ in 0..count{let[s0,s1]=d.a()?;let y0=d.a()?;let y1=d.a()?;let midpoint=d.f()?;let midpoint_gas=d.a()?;let midpoint_background=d.a()?;let rhs=d.a()?;let total=d.a()?;let mat=d.a()?;let n=d.size(16384)?;let mut segments=Vec::new();for _ in 0..n{let node=d.size(4095)?;let ordinal=d.size(16383)?;let[eta,weight,a,b]=d.a()?;let gas=d.a()?;let background=d.a()?;let[incoming,q]=d.a()?;let rates=d.a()?;let energy_start=d.f()?;let owners=d.a()?;let mut dyadic=[Wide::ZERO;13];for x in &mut dyadic{*x=d.wide()?}let ln_n=d.option()?;let ln_u=d.option()?;segments.push(Segment{node,ordinal,eta,weight,a,b,gas,background,incoming,q,rates,energy_start,owners,dyadic,ln_n,ln_u})}let n=d.size(4096)?;let mut nodes=Vec::new();for _ in 0..n{nodes.push(Node{index:d.size(4095)?,owners:d.a()?,ln_n:d.option()?,ln_u:d.option()?})}accepted_records.push(Accepted{s0,s1,y0,y1,midpoint,midpoint_gas,midpoint_background,rhs,segments,nodes,total,material:mat});}
 Ok(State{s,y,density:crate::diagnostics::Density::new(density),active,radiation,material,iterations,norm,n_ratio,e_ratio,accepted_trace,trial_trace,accepted_records})}

