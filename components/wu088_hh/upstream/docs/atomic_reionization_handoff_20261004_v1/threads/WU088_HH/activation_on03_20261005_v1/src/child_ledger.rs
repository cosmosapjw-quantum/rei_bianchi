//! Source-specific arithmetic enclosure for one executed static HH/FT03 BE child.
//! This bounds exact dyadic arithmetic on the supplied binary64 record, not a
//! continuous trajectory, transcendental rate fit, or a parameter/state box.
use crate::{ForwardError,Ft03Model,HHeState,Ft03Events};
use crate::hh_optin::HhSelection;

#[derive(Clone,Copy,Debug)]
pub struct I {pub lo:f64,pub hi:f64}
impl I {
 pub fn point(x:f64)->Self{Self{lo:x,hi:x}}
 fn zero(self)->bool{self.lo==0. && self.hi==0.}
 pub fn add(self,b:Self)->Self{if self.zero(){return b;}if b.zero(){return self;}Self{lo:(self.lo+b.lo).next_down(),hi:(self.hi+b.hi).next_up()}}
 pub fn neg(self)->Self{Self{lo:-self.hi,hi:-self.lo}}
 pub fn sub(self,b:Self)->Self{if self.lo==self.hi && b.lo==b.hi && self.lo==b.lo{return Self::point(0.);}self.add(b.neg())}
 pub fn mul(self,b:Self)->Self{if self.zero()||b.zero(){return Self::point(0.);}let a=[self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi];Self{lo:a.iter().copied().fold(f64::INFINITY,f64::min).next_down(),hi:a.iter().copied().fold(f64::NEG_INFINITY,f64::max).next_up()}}
 pub fn div_positive(self,b:Self)->Self{if !(b.lo>0.){return Self{lo:f64::NAN,hi:f64::NAN};}if self.zero(){return self;}self.mul(Self{lo:(1./b.hi).next_down(),hi:(1./b.lo).next_up()})}
 pub fn abs_upper(self)->f64{self.lo.abs().max(self.hi.abs())}
 pub fn finite(self)->bool{self.lo.is_finite()&&self.hi.is_finite()&&self.lo<=self.hi}
}
pub fn up_add(a:f64,b:f64)->f64{if a==0.{b}else if b==0.{a}else{(a+b).next_up()}}
pub fn weights(m:&Ft03Model)->[I;8]{let g=&m.gas;let p=I::point;let ev=p(g.ev_erg);[p(g.n_h_cm3).mul(ev).mul(p(g.threshold_ev[0])),p(g.n_he_cm3).mul(ev).mul(p(g.threshold_ev[1])),p(g.n_he_cm3).mul(ev).mul(p(g.threshold_ev[1]).add(p(g.threshold_ev[2]))),p(1.),ev.mul(p(g.photon_energy_ev[0])),ev.mul(p(g.photon_energy_ev[1])),ev.mul(p(g.photon_energy_ev[2])),p(1.)]}
pub fn state8(s:&HHeState)->[f64;8]{let q=s.coordinates();[q[0],q[1],q[2],q[3],q[4],q[5],q[6],s.escaped_erg_cm3]}
pub fn energy(m:&Ft03Model,s:&HHeState)->I{weights(m).iter().zip(state8(s)).fold(I::point(0.),|v,(w,x)|v.add(w.mul(I::point(x))))}
#[derive(Clone,Copy,Debug)]
pub struct Budget {pub horizon:f64,pub tolerance:f64,pub energy0:f64,pub energy0_lower:f64}
impl Budget {
 pub fn new(m:&Ft03Model,s:&HHeState,horizon:f64,tolerance:f64)->Result<Self,ForwardError>{
  if !horizon.is_finite()||horizon<=0.||!tolerance.is_finite()||tolerance<=0.||tolerance>=1.{return Err(ForwardError::InvalidInput("HH_BUDGET_DOMAIN"));}
  let e=m.gas.total_energy(s)?;let ei=energy(m,s);if !ei.finite()||ei.lo<=0.{return Err(ForwardError::InvalidInput("HH_BUDGET_ENERGY_DOMAIN"));}
  Ok(Self{horizon,tolerance,energy0:e,energy0_lower:ei.lo})
 }
 pub fn allocation(self,dt:f64)->Result<f64,ForwardError>{
  if !dt.is_finite()||dt<0.||dt>self.horizon{return Err(ForwardError::InvalidInput("HH_BUDGET_TIME_DOMAIN"));}
  let b=I::point(self.tolerance).mul(I::point(0.75)).mul(I::point(dt)).div_positive(I::point(self.horizon));
  if !b.finite()||b.lo<0.{return Err(ForwardError::InvalidInput("HH_BUDGET_ARITHMETIC"));}Ok(b.lo)
 }
}
#[derive(Clone,Copy,Debug)]
pub struct ChildAudit {
 pub old:[f64;8],pub new:[f64;8],pub rhs:[f64;8],pub dt:f64,
 pub vector_residual:[I;8],pub energy_residual_l1:f64,pub source_balance:I,
 pub energy_bound:f64,pub event_bound:[f64;6],pub allocation:f64,
 pub events:[f64;17],pub hh_event:f64,pub hh_per_h:f64,pub hh_heat:f64,
}
impl ChildAudit {pub fn admissible(&self,b:Budget)->bool{self.energy_bound<=I::point(self.allocation).mul(I::point(b.energy0_lower)).lo && self.event_bound.iter().all(|x|*x<=self.allocation)}}
pub fn audit(m:&Ft03Model,old:&HHeState,new:&HHeState,dt:f64,sel:HhSelection,events:&Ft03Events,hh_event:f64,hh_per_h:f64,hh_heat:f64,budget:Budget)->Result<ChildAudit,ForwardError>{
 let ep=crate::hh_optin::combined_ft03_rhs(m,new,sel)?;let f=ep.combined.derivative;let f=[f[0],f[1],f[2],f[3],f[4],f[5],f[6],ep.combined.escaped_energy_rate];
 let x=state8(old);let y=state8(new);let p=I::point;let a=weights(m);let d=p(dt);
 let r=std::array::from_fn(|i|p(y[i]).sub(p(x[i])).sub(d.mul(p(f[i]))));
 let mut l1=0.;let mut source=p(0.);
 for i in 0..8{l1=up_add(l1,a[i].mul(r[i]).abs_upper());source=source.add(a[i].mul(p(f[i])));}
 let bound=up_add(l1,d.mul(source).abs_upper());
 let mut j=[p(0.);3];let mut out=[0.;17];
 for aa in 0..3{for k in 0..3{let v=events.photo_per_cm3[aa][k];j[aa]=j[aa].add(p(v));out[aa*3+k]=v;}j[aa]=j[aa].add(p(events.collision_per_cm3[aa])).sub(p(events.recombination_per_cm3[aa]));out[9+aa]=events.collision_per_cm3[aa];out[12+aa]=events.recombination_per_cm3[aa];}
 j[0]=j[0].add(p(hh_event));j[1]=j[1].sub(p(events.dr_per_cm3[0])).sub(p(events.dr_per_cm3[1]));out[15]=events.dr_per_cm3[0];out[16]=events.dr_per_cm3[1];
 let nh=p(m.gas.n_h_cm3);let he=p(m.gas.n_he_cm3);let mut eb=[0.;6];
 eb[0]=nh.mul(p(y[0]).sub(p(x[0]))).sub(j[0]).div_positive(nh).abs_upper();
 eb[1]=he.mul(p(y[1]).sub(p(x[1]))).sub(j[1]).add(j[2]).div_positive(he).abs_upper();
 eb[2]=he.mul(p(y[2]).sub(p(x[2]))).sub(j[2]).div_positive(he).abs_upper();
 for k in 0..3{let mut absorb=p(0.);for aa in 0..3{absorb=absorb.add(p(events.photo_per_cm3[aa][k]));}eb[3+k]=p(x[4+k]).sub(p(y[4+k])).sub(absorb).div_positive(nh).abs_upper();}
 if !bound.is_finite()||!source.finite()||r.iter().any(|v|!v.finite())||eb.iter().any(|v|!v.is_finite()){return Err(ForwardError::InvalidInput("HH_BUDGET_ARITHMETIC"));}
 Ok(ChildAudit{old:x,new:y,rhs:f,dt,vector_residual:r,energy_residual_l1:l1,source_balance:source,energy_bound:bound,event_bound:eb,allocation:budget.allocation(dt)?,events:out,hh_event,hh_per_h,hh_heat})
}
