#![forbid(unsafe_code)]
use rei_microphysics::axbi_background::{AxbiBackground,BackgroundPoint,BackgroundFamily,Cosmology};
use rei_microphysics::ForwardError;
use std::{cell::Cell,rc::Rc,collections::{HashMap,VecDeque}};
pub const AR:f64=1.0/21.0;
pub const AE:f64=0.2;
pub fn cosmology()->Cosmology { Cosmology{h0_per_s:67.4*1e5/3.0856775814913673e24,omega_m:0.315,omega_r:9.2e-5,omega_lambda:1.0-0.315-9.2e-5} }
#[derive(Clone,Default)]
pub struct Counts {pub direct:Rc<Cell<u64>>,pub candidate:Rc<Cell<u64>>,pub integrand:Rc<Cell<u64>>}
fn count(c:&Cell<u64>,cap:u64)->Result<(),ForwardError>{if c.get()>=cap {return Err(ForwardError::InvalidInput("BenchmarkQuota"))} c.set(c.get()+1);Ok(())}
#[derive(Clone)]
pub struct Model{ pub bg:AxbiBackground,pub q:f64,pub family:BackgroundFamily,pub counts:Counts }
impl Model {
 pub fn new(q:f64,family:BackgroundFamily,counts:Counts)->Result<Self,ForwardError>{count(&counts.direct,65536)?;let bg=AxbiBackground::new(cosmology(),AR,AE,0.0,q,family,4096)?;Ok(Self{bg,q,family,counts})}
 pub fn direct(&self,a:f64)->Result<BackgroundPoint,ForwardError>{count(&self.counts.direct,65536)?;self.bg.point_at_scale(a)}
 pub fn rates(&self,a:f64)->Result<BackgroundPoint,ForwardError>{
  if !a.is_finite() {return Err(ForwardError::InvalidInput("AxbiNonFinite"))} if a<=0.0 {return Err(ForwardError::InvalidInput("AxbiPositive"))} if !(AR..=AE).contains(&a){return Err(ForwardError::InvalidInput("AxbiScaleDomain"))}
  let hf=cosmology().hubble_flrw(a)?;let s=self.q*cosmology().hubble_flrw(AR)?*(AR/a).powi(3);let h=match self.family{BackgroundFamily::PhysicalDensityFixed=>hf.hypot(s),BackgroundFamily::SameHDiagnostic=>hf};
  Ok(BackgroundPoint{a,b:0.0,time_s:0.0,h_flrw_per_s:hf,h_per_s:h,s_per_s:s,sigma:s/h})
 }
 pub fn local_integral(&self,a1:f64,a2:f64,n:usize)->Result<f64,ForwardError>{self.rates(a1)?;self.rates(a2)?;if a2<=a1{return Err(ForwardError::InvalidInput("IntervalOrder"))}let delta=((a2-a1)/a1).ln_1p();let dx=delta/n as f64;let mut sum=0.0;for i in 0..=n{count(&self.counts.integrand,2000000)?;let a=if i==0{a1}else if i==n{a2}else{a1*(dx*i as f64).exp()};let w=if i==0||i==n{1.0}else if i%2==0{2.0}else{4.0};sum+=w/self.rates(a)?.h_per_s;}Ok(sum*dx/3.0)}
}
pub struct ExactCache{pub model:Model,items:HashMap<u64,BackgroundPoint>,fifo:VecDeque<u64>,pub hits:u64,pub misses:u64}
impl ExactCache{
 pub fn new(model:Model)->Self{Self{model,items:HashMap::new(),fifo:VecDeque::new(),hits:0,misses:0}}
 pub fn query(&mut self,a:f64)->Result<BackgroundPoint,ForwardError>{count(&self.model.counts.candidate,8000000)?; if let Some(p)=self.items.get(&a.to_bits()){self.hits+=1;return Ok(*p)} self.misses+=1;let p=self.model.direct(a)?;if self.items.len()==256{let key=self.fifo.pop_front().unwrap();self.items.remove(&key);}self.items.insert(a.to_bits(),p);self.fifo.push_back(a.to_bits());Ok(p)}
}
pub struct Table{pub model:Model,pub knots:Vec<BackgroundPoint>,pub h:f64,exact:HashMap<u64,usize>}
impl Table{
 pub fn from_reference(model:Model,refs:&[BackgroundPoint],n:usize)->Self{let knots:Vec<_>=(0..=n).map(|j|refs[j*(8192/n)]).collect();let exact=knots.iter().enumerate().map(|(j,p)|(p.a.to_bits(),j)).collect();Self{model,knots,h:(AE/AR).ln()/n as f64,exact}}
 fn cell(&self,a:f64)->Result<(usize,f64),ForwardError>{self.model.rates(a)?;let x=(a/AR).ln()/self.h;let j=(x.floor() as usize).min(self.knots.len()-2);Ok((j,x-j as f64))}
 fn coefficients(&self,j:usize,clock:bool)->[f64;4]{let p=self.knots[j];let q=self.knots[j+1];let (y,z,d,e)=if clock{(p.time_s,q.time_s,1.0/p.h_per_s,1.0/q.h_per_s)}else{(p.b,q.b,p.sigma,q.sigma)};let delta=z-y;[y,self.h*d,3.0*delta-self.h*(2.0*d+e),-2.0*delta+self.h*(d+e)]}
 pub fn query(&self,a:f64)->Result<BackgroundPoint,ForwardError>{count(&self.model.counts.candidate,8000000)?;let mut p=self.model.rates(a)?;if let Some(&j)=self.exact.get(&a.to_bits()){return Ok(self.knots[j])} let(j,u)=self.cell(a)?;let t=self.coefficients(j,true);let b=self.coefficients(j,false);p.time_s=t[0]+u*(t[1]+u*(t[2]+u*t[3]));p.b=b[0]+u*(b[1]+u*(b[2]+u*b[3]));Ok(p)}
 pub fn derivatives(&self,a:f64)->Result<(f64,f64),ForwardError>{let(j,u)=self.cell(a)?;let t=self.coefficients(j,true);let b=self.coefficients(j,false);Ok(((t[1]+u*(2.0*t[2]+3.0*u*t[3]))/self.h,(b[1]+u*(2.0*b[2]+3.0*u*b[3]))/self.h))}
 pub fn increment(&self,a:f64,b:f64)->Result<f64,ForwardError>{self.model.rates(a)?;self.model.rates(b)?;if b<=a{return Err(ForwardError::InvalidInput("IntervalOrder"))}let mut left=a;let mut sum=0.0;while left<b{let j=match self.knots.binary_search_by(|p|p.a.partial_cmp(&left).unwrap()){Ok(i)=>i.min(self.knots.len()-2),Err(i)=>i-1};let right=b.min(self.knots[j+1].a);let u=if left.to_bits()==self.knots[j].a.to_bits(){0.0}else{((left-self.knots[j].a)/self.knots[j].a).ln_1p()/self.h};let du=((right-left)/left).ln_1p()/self.h;let c=self.coefficients(j,true);sum+=du*(c[1]+(2.0*u+du)*c[2]+(3.0*u*u+3.0*u*du+du*du)*c[3]);left=right;}Ok(sum)}
}
pub fn point_bits(p:BackgroundPoint)->[u64;7]{[p.a,p.b,p.time_s,p.h_flrw_per_s,p.h_per_s,p.s_per_s,p.sigma].map(f64::to_bits)}
pub fn scale(j:usize,n:usize)->f64{if j==0{AR}else if j==n{AE}else{AR*((AE/AR).ln()*j as f64/n as f64).exp()}}
