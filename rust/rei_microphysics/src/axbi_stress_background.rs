//! Independent initial quadrupole radiation anisotropic stress for LRS Bianchi I.
//!
//! A new OPT-IN RESEARCH component. The original stress-free AX03 source,
//! chemistry clock, checkpoints, and existing signed ionization histories
//! remain unchanged. No production driver calls this module.
//!
//! Real axisymmetric massless Einstein–Vlasov background with initially
//! positive phase density W(mu0)=1+kappa P2(mu0), |kappa|<=.5, and
//! q_ref=s_ref/Hflrw_ref.  pi_s_ref/epsilon_rad_ref=kappa/15.
//! P = <W R P2(mu_late)>/3 and M=<W R>, M_b=-6P.
//! G^z_z-G^x_x gives dot s+3Hs=8piG pi_s/c²:
//! H² = H0²(Om/a³+Or M/a⁴+Ol)+s².
//! No radiation/cold-gas collision and no CMB/ionizing opacity assumed.
use crate::axbi_background::Cosmology;
use crate::ForwardError;
use std::f64::consts::PI;

fn invalid(tag:&'static str)->ForwardError{ForwardError::InvalidInput(tag)}
pub const ANGULAR_N:usize=32;
#[derive(Clone,Copy,Debug)]
pub struct StressPoint {
 pub a:f64,
 pub elapsed_proper_s:f64,
 pub b:f64,
 pub s_per_s:f64,
 pub h_per_s:f64,
 pub s_over_h:f64,
 pub radiation_m:f64,
 pub radiation_p:f64,
 pub radiation_rho_over_crit0:f64,
 pub pi_s_over_crit0:f64,
}
#[derive(Clone,Debug)]
pub struct AxbiInitialStressBackground {
 cos:Cosmology, a_ref:f64,a_end:f64,href:f64,f0:f64,
 q:f64,kappa:f64,nodes:[f64;ANGULAR_N],weights:[f64;ANGULAR_N],
}
impl AxbiInitialStressBackground {
 pub fn new(cos:Cosmology,a_ref:f64,a_end:f64,q:f64,kappa:f64)->Result<Self,ForwardError>{
  if !a_ref.is_finite()||!a_end.is_finite()||!(a_ref>0.&&a_end>a_ref)
    || !q.is_finite()||!kappa.is_finite()||kappa.abs()>0.5
    || ![0.,0.005,-0.005,0.01,-0.01].contains(&q){
    return Err(invalid("AxbiStressInitialDomain"));
  }
  let href=cos.hubble_flrw(a_ref)?;
  let f0=(cos.h0_per_s/href).powi(2);
  let (nodes,weights)=Self::gauss_nodes()?;
  Ok(Self{cos,a_ref,a_end,href,f0,q,kappa,nodes,weights})
 }
 fn gauss_nodes()->Result<([f64;ANGULAR_N],[f64;ANGULAR_N]),ForwardError>{
  let mut nodes=[0.;ANGULAR_N];
  let mut weights=[0.;ANGULAR_N];
  for i in 0..ANGULAR_N/2{
   let mut z=(PI*((i as f64)+0.75)/((ANGULAR_N as f64)+0.5)).cos();
   for _ in 0..24{
    let (pn,dn)=Self::legendre(ANGULAR_N,z);
    let delta=pn/dn;
    z-=delta;
    if delta.abs()<1e-15{break;}
   }
   let (_p,d)=Self::legendre(ANGULAR_N,z);
   let weight=1.0/((1.0-z*z)*d*d);
   nodes[i]=-z;nodes[ANGULAR_N-1-i]=z;
   weights[i]=weight;weights[ANGULAR_N-1-i]=weight;
  }
  let total:f64=weights.iter().sum();
  if !total.is_finite()||(total-1.).abs()>5e-13||weights.iter().any(|x|*x<=0.){
    return Err(invalid("AxbiStressGaussSource"));
  }
  Ok((nodes,weights))
 }
 fn legendre(n:usize,x:f64)->(f64,f64){
  let (mut pprev,mut p)=(1.0,x);
  for k in 2..=n{
   let v=((2*k-1) as f64*x*p-(k-1) as f64*pprev)/k as f64;
   pprev=p;p=v;
  }
  (p,n as f64*(x*p-pprev)/(x*x-1.0))
 }
 pub fn initial_pi_over_radiation(&self)->f64{self.kappa/15.}
 pub fn angular_moments(&self,b:f64)->Result<(f64,f64),ForwardError>{
  if !b.is_finite()||b.abs()>0.25{return Err(invalid("AxbiStressSmallAnisotropyDomain"))}
  if b==0.0&&self.kappa==0.0{return Ok((1.,0.))}
  let e2=(2.*b).exp();let en=(-4.*b).exp();
  let (mut m,mut p)=(0.,0.);
  for i in 0..ANGULAR_N{
   let u=self.nodes[i];let pu=(3.*u*u-1.)/2.;
   let w=1.+self.kappa*pu;
   let rr=(e2*(1.-u*u)+en*u*u).sqrt();
   let ul2=en*u*u/(rr*rr);
   let wr=self.weights[i]*w*rr;
   m+=wr;p+=wr*(3.*ul2-1.)/2.;
  }
  let pi=p/3.;
  if !m.is_finite()||!pi.is_finite()||m<=0.{
   return Err(invalid("AxbiStressNonpositiveRadiation"))
  }
  Ok((m,pi))
 }
 fn fields(&self,x:f64,y:[f64;3])->Result<(f64,f64,f64,f64,f64),ForwardError>{
  let a=self.a_ref*x.exp();
  let (m,p)=self.angular_moments(y[1])?;
  let s=y[2];
  let e2=self.f0*(self.cos.omega_m/a.powi(3)+
       self.cos.omega_r*m/a.powi(4)+self.cos.omega_lambda)+s*s;
  if !e2.is_finite()||e2<=0.{return Err(invalid("AxbiStressEinsteinConstraint"))}
  let e=e2.sqrt();
  Ok((a,e,s,m,p))
 }
 fn rhs(&self,x:f64,y:[f64;3])->Result<[f64;3],ForwardError>{
  let (a,e,s,_m,p)=self.fields(x,y)?;
  Ok([1./e,s/e,-3.*s+3.*self.f0*self.cos.omega_r*p/(a.powi(4)*e)])
 }
 fn step(&self,x:f64,y:[f64;3],h:f64)->Result<[f64;3],ForwardError>{
  let k1=self.rhs(x,y)?;
  let y2=std::array::from_fn(|i|y[i]+h*k1[i]/2.);
  let k2=self.rhs(x+h/2.,y2)?;
  let y3=std::array::from_fn(|i|y[i]+h*k2[i]/2.);
  let k3=self.rhs(x+h/2.,y3)?;
  let y4=std::array::from_fn(|i|y[i]+h*k3[i]);
  let k4=self.rhs(x+h,y4)?;
  Ok(std::array::from_fn(|i|y[i]+h*(k1[i]+2.*k2[i]+2.*k3[i]+k4[i])/6.))
 }
 fn point(&self,x:f64,y:[f64;3])->Result<StressPoint,ForwardError>{
  let (a,e,s,m,p)=self.fields(x,y)?;
  let h=self.href*e;
  Ok(StressPoint{a,elapsed_proper_s:y[0]/self.href,b:y[1],
    s_per_s:s*self.href,h_per_s:h,s_over_h:s/e,radiation_m:m,
    radiation_p:p,radiation_rho_over_crit0:self.cos.omega_r*m/a.powi(4),
    pi_s_over_crit0:self.cos.omega_r*p/a.powi(4)})
 }
 pub fn trajectory(&self,n_intervals:usize)->Result<Vec<StressPoint>,ForwardError>{
  if n_intervals<2||n_intervals>32768{return Err(invalid("AxbiStressPanels"))}
  let xend=(self.a_end/self.a_ref).ln();
  let h=xend/n_intervals as f64;
  let mut result=Vec::with_capacity(n_intervals+1);
  let mut y=[0.,0.,self.q];
  result.push(self.point(0.,y)?);
  for i in 0..n_intervals{
   let x=i as f64*h;
   y=self.step(x,y,h)?;
   let xn=(i+1) as f64*h;
   result.push(self.point(xn,y)?);
  }
  Ok(result)
 }
 pub fn endpoint(&self,n_intervals:usize)->Result<StressPoint,ForwardError>{
  self.trajectory(n_intervals).map(|p|*p.last().unwrap())
 }
}
