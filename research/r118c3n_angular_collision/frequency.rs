//! Signed canonical photon-number stock. Local isotropic injection, collisionless transport.
use bianchi_rustcore::kinetic::{owned_vlasov::OwnedState,sphere::SphereGrid};
const KT0:f64=8.617333262145e-5*2.7255;
pub struct FreqRays{dir:Vec<[f64;3]>,w:Vec<f64>,q:Vec<f64>,x:Vec<f64>,dl:f64,cap:f64}
impl FreqRays{
 pub fn new(x:&[f64],bb:f64,a:f64,nmu:usize)->Result<Self,String>{
  if x.len()<16||!bb.is_finite()||bb<=0.{return Err("freq grid".into())}
  let dl=(x[1]/x[0]).ln();let g=SphereGrid::new(nmu,2*nmu);
  let dir=g.ehat.chunks_exact(3).map(|z|[z[0],z[1],z[2]]).collect();
  let w=g.w.iter().map(|v|v/(4.*std::f64::consts::PI)).collect();
  let mut q=Vec::new();for i in -4..(x.len() as isize+4){q.push(x[0]*(i as f64*dl).exp());}
  let cap=bb*a/KT0*15./std::f64::consts::PI.powi(4);
  Ok(Self{dir,w,q,x:x.to_vec(),dl,cap})
 }
 pub fn empty(&self)->Vec<f64>{vec![0.;self.dir.len()*self.q.len()]}
 pub fn ray(&self,g:&OwnedState)->Result<Vec<(f64,[f64;3],f64)>,String>{
  let f=g.f.try_inverse().ok_or("inverse")?.transpose();
  let mut rays=Vec::new();let mut sum=0.;
  for (n,w) in self.dir.iter().zip(&self.w){
   let p:[f64;3]=std::array::from_fn(|i|(0..3).map(|j|f[(i,j)]*n[j]).sum());let d=p.iter().map(|v|v*v).sum::<f64>().sqrt();
   let wt=w/d.powi(3);sum+=wt;rays.push((d,p.map(|x|x/d),wt));
  }
  if (sum-1.).abs()>1e-7{return Err(format!("solid angle quadrature {sum:e}"))}
  for r in &mut rays{r.2/=sum;}Ok(rays)
 }
 pub fn moments(&self,s:&[f64],g:&OwnedState)->Result<(f64,[[f64;3];3],f64),String>{
  if s.len()!=self.dir.len()*self.q.len()||s.iter().any(|v|!v.is_finite()){return Err("signed stock".into())}
  let mut u=0.;let mut n=0.;let mut p=[[0.;3];3];let fac=KT0/g.a;
  for (row,(d,k,_)) in s.chunks_exact(self.q.len()).zip(self.ray(g)?){
   let v=row.iter().zip(&self.q).map(|(a,b)|a*b).sum::<f64>()*fac*d;
   u+=v;n+=row.iter().sum::<f64>();for i in 0..3{for j in 0..3{p[i][j]+=v*k[i]*k[j];}}
  }
  Ok((u,p,n))
 }
 // Signed linear local-frame elastic redistribution. One collision conditioned
 // on scattering in a short interval. Frozen geometry, unpolarized closure.
 pub fn scatter(&self,s:&mut [f64],g:&OwnedState,depth:f64)->Result<[f64;5],String>{
  if !depth.is_finite()||depth<0.||depth>1e-3{return Err("elastic depth".into())}
  if depth==0.{return Ok([0.;5])}
  let rays=self.ray(g)?;let prob=-(-depth).exp_m1();let nq=self.q.len();
  let (u0,_,n0)=self.moments(s,g)?;let mut change=vec![0.;s.len()];let mut blocked=0.;let mut moved=0.;let mut lossmax:f64=0.;
  for (i,(di,ni,_)) in rays.iter().enumerate(){
   let mut loss=0.;
   for (j,(dj,nj,wj)) in rays.iter().enumerate(){
    if i==j{continue}
    let cos=(0..3).map(|k|ni[k]*nj[k]).sum::<f64>();
    let k=0.75*wj*(1.+cos*cos);loss+=k;
    let r=di/dj;let z=(r.ln()/self.dl).floor();let shift=z as isize;
    let l=(z*self.dl).exp();let h=((z+1.)*self.dl).exp();
    let t=((r-l)/(h-l)).clamp(0.,1.);
    let w=prob*k;
    for q in 0..nq{
     let a=w*s[i*nq+q];if a==0.{continue}
     let k=q as isize+shift;
     // Exact edge packet can be deposited on last node if upper weight zero.
     if k<0||k>=nq as isize||(k+1>=nq as isize&&t>0.){
      blocked+=a.abs();continue
     }
     let lo=j*nq+k as usize;change[i*nq+q]-=a;change[lo]+=a*(1.-t);
     if t>0.{change[lo+1]+=a*t;}
     moved+=a.abs();
    }
   }
   if loss>1.+1e-12{return Err("angular kernel not stochastic".into())}
   lossmax=lossmax.max(loss);
  }
  for (v,d) in s.iter_mut().zip(change){*v+=d;}
  let (u1,_,n1)=self.moments(s,g)?;
  let du=(u1-u0).abs();let dn=(n1-n0).abs();
  if du>1e-14||dn>1e-12{return Err("elastic collision ledger".into())}
  Ok([depth,moved,blocked,du,dn])
 }
 pub fn advance(&self,s:&mut [f64],old:&OwnedState,mid:&OwnedState,end:&OwnedState,delta:&[f64],depth:f64)->Result<(f64,f64,f64,f64,[f64;5]),String>{
  if delta.len()!=self.x.len(){return Err("spectral delta".into())}
  let (u0,_,n0)=self.moments(s,old)?;let qn:Vec<_>=delta.iter().zip(&self.x).map(|(f,x)|self.cap*x.powi(3)*self.dl*f).collect();
  let birth_n=qn.iter().sum::<f64>();let birth_u=qn.iter().zip(&self.x).map(|(a,b)|a*b).sum::<f64>()*KT0/mid.a;
  let m=self.ray(mid)?;let mut before_mid=0.;let mut deposited_n=0.;
  for (row,(d,_,w)) in s.chunks_exact_mut(self.q.len()).zip(m){
   before_mid+=row.iter().zip(&self.q).map(|(a,b)|a*b).sum::<f64>()*KT0/mid.a*d;
   for (x,dn) in self.x.iter().zip(&qn){
    let q=x/d;let k=self.q.partition_point(|x|*x<=q);
    if k==0||k>=self.q.len(){return Err("canonical padded boundary".into())}
    let t=(q-self.q[k-1])/(self.q[k]-self.q[k-1]);let n=w*dn;
    row[k-1]+=n*(1.-t);row[k]+=n*t;deposited_n+=n;
   }
  }
  let diag=self.scatter(s,mid,depth)?;
  let after_mid=self.moments(s,mid)?.0;
  let (u1,_,n1)=self.moments(s,end)?;
  let work=u0-before_mid+after_mid-u1;
  if (u1-u0+work-birth_u).abs()>1e-14 || (n1-n0-birth_n).abs()>1e-12 || (deposited_n-birth_n).abs()>1e-12{return Err("frequency deposition ledger".into())}
  Ok((u1,work,birth_n,birth_u,diag))
 }
 // Angle-integrated physical frequency spectrum for the scalar reaction operator.
 // Out-of-grid packet weight is reported, not removed from physical stock.
 pub fn project(&self,s:&[f64],g:&OwnedState)->Result<(Vec<f64>,[f64;4]),String>{
  let mut stock=vec![0.;self.x.len()];let mut out=[0.;4];
  for (row,(d,_,_)) in s.chunks_exact(self.q.len()).zip(self.ray(g)?){
   for (&q,&n) in self.q.iter().zip(row){
    if n==0.{continue}
    let x=q*d;
    let k=self.x.partition_point(|v|*v<=x);
    if k==0||k==self.x.len(){
     // A cell is defined by its log-midpoint edges, not by its center.
     // Assign within-edge packets to the edge cell by number; explicitly
     // carry signed energy quadrature defect without changing physical rays.
     let i=if k==0{0}else{self.x.len()-1};
     let lo=self.x[0]*(-self.dl/2.).exp();
     let hi=self.x[self.x.len()-1]*(self.dl/2.).exp();
     if x>=lo&&x<=hi{
      stock[i]+=n;let e=n*(x-self.x[i])*KT0/g.a;
      out[1]+=e;out[3]+=e.abs();continue
     }
     out[0]+=n;out[1]+=n*x*KT0/g.a;out[2]+=n.abs();out[3]+=(n*x*KT0/g.a).abs();continue
    }
    let t=(x-self.x[k-1])/(self.x[k]-self.x[k-1]);stock[k-1]+=n*(1.-t);stock[k]+=n*t;
   }
  }
  let (u,_,n)=self.moments(s,g)?;
  let en=stock.iter().zip(&self.x).map(|(n,x)|n*x*KT0/g.a).sum::<f64>();
  if (stock.iter().sum::<f64>()+out[0]-n).abs()>1e-12||(en+out[1]-u).abs()>1e-14{return Err("project ledger".into())}
  let occ=stock.iter().zip(&self.x).map(|(n,x)|n/(self.cap*x.powi(3)*self.dl)).collect();
  Ok((occ,out))
 }
 pub fn min_full_ratio(&self,s:&[f64],g:&OwnedState)->Result<f64,String>{
  let rays=self.ray(g)?;let mut min=f64::INFINITY;
  for (i,(row,(d,_,_))) in s.chunks_exact(self.q.len()).zip(rays).enumerate(){
   for (&q,&n) in self.q.iter().zip(row){
    let refn=self.cap*self.w[i]*q.powi(3)*self.dl/(q*d).exp_m1();
    if !refn.is_finite()||refn<=0.{return Err("reference stock domain".into())}
    min=min.min(1.+n/refn);
   }
  }
  Ok(min)
 }
 pub fn output(&self,s:&[f64],g:&OwnedState,path:&std::path::Path)->Result<(),String>{
  use std::io::Write;
  let mut f=std::io::BufWriter::new(std::fs::File::create(path).map_err(|e|e.to_string())?);
  writeln!(f,"ray,q,x,N_per_H,nx,ny,nz").map_err(|e|e.to_string())?;
  for (j,(row,(d,k,_))) in s.chunks_exact(self.q.len()).zip(self.ray(g)?).enumerate(){
   for (&q,&n) in self.q.iter().zip(row){writeln!(f,"{j},{q:.17e},{:.17e},{n:.17e},{:.17e},{:.17e},{:.17e}",q*d,k[0],k[1],k[2]).map_err(|e|e.to_string())?;}
  }
  f.flush().map_err(|e|e.to_string())
 }
}

#[cfg(test)]
mod tests{
 use super::*;
 use bianchi_rustcore::kinetic::owned_thomson::ThomsonOwner;
 #[test]
 fn quadrupole_and_conservation(){
  let x:Vec<_>=(0..64).map(|i|0.01*(i as f64*0.1).exp()).collect();
  let own=ThomsonOwner::new(0.,32,4,8,4,8,16).unwrap();
  let g=own.initial(0.05,[0.;5]).unwrap().geometry;
  let m=FreqRays::new(&x,1e6,g.a,4).unwrap();let mut s=m.empty();
  let rays=m.ray(&g).unwrap();let nq=m.q.len();let k=20;
  for (i,(_,n,w)) in rays.iter().enumerate(){s[i*nq+k]=w*(1.+0.2*(3.*n[2]*n[2]-1.)/2.);}
  let (_,p,n)=m.moments(&s,&g).unwrap();let u=p[0][0]+p[1][1]+p[2][2];let z=p[2][2]-u/3.;
  let diag=m.scatter(&mut s,&g,0.0001).unwrap();let (_,pp,nn)=m.moments(&s,&g).unwrap();
  let zz=pp[2][2]-u/3.;let expected=1.-0.9*(-(-0.0001_f64).exp_m1());
  assert!((zz/z-expected).abs()<1e-11);
  assert!((nn-n).abs()<1e-13&&diag[2]==0.);
  let b=s.clone();m.scatter(&mut s,&g,0.).unwrap();assert_eq!(b,s);
  // Signed linearity with negative occupation differences.
  let mut r=b.iter().map(|x|-x).collect::<Vec<_>>();let mut p=b.clone();
  m.scatter(&mut r,&g,0.0001).unwrap();m.scatter(&mut p,&g,0.0001).unwrap();
  assert!(r.iter().zip(p).all(|(a,b)|(*a+b).abs()<1e-15));
 }
}
