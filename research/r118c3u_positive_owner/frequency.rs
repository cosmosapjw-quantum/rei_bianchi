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
 // Local angular projection with the repaired finite cell edges. The
 // normalized reference is a conditional collisionless redshifted Planck shape,
 // not a new radiation energy reservoir or the exact BASS polarization spectrum.
 // Continuous finite-rate collision on a conservative two-moment local
 // reconstruction. Mean number AND energy per local cell already belong to
 // scalar chemistry, so only the angular-zero-mean part is deposited.
 // Tail packets outside physical cell edges are left unchanged.
 pub fn finite_moment_increment(&self,s:&[f64],g:&OwnedState,theta:f64,tr:f64,depth:f64)->Result<(Vec<f64>,[f64;4]),String>{
  if theta<=0.||tr<=0.||depth<0.||!theta.is_finite()||!tr.is_finite()||!depth.is_finite(){return Err("finite moment clock".into())}
  let rays=self.ray(g)?;let nr=rays.len();let nx=self.x.len();let nq=self.q.len();
  let y0=self.x[0].ln()-self.dl/2.;let y1=y0+nx as f64*self.dl;
  let edges:Vec<_>=(0..=nx).map(|k|(y0+k as f64*self.dl).exp()).collect();
  let dx:Vec<_>=edges.windows(2).map(|v|v[1]-v[0]).collect();
  let mut nn=vec![vec![0.;nx];nr];let mut uu=nn.clone();
  let cell=|y:f64|->usize{((y-y0)/self.dl).floor().max(0.).min((nx-1) as f64) as usize};
  let mut tail=0.;
  for (i,(row,(d,_,_))) in s.chunks_exact(nq).zip(&rays).enumerate(){
   for (&q,&n) in self.q.iter().zip(row){
    let x=q*d;let y=x.ln();
    if y<y0||y>=y1{tail+=n.abs();continue;}
    let j=cell(y);nn[i][j]+=n/self.cap;uu[i][j]+=n/self.cap*(x-self.x[j])/dx[j];
   }
  }
  let mut ratio=vec![vec![0.;nx];nr];let mut aa=ratio.clone();let mut bb=ratio.clone();
  // Piecewise constant angular reference multiplier, exact scalar Planck
  // frequency shape. This is an explicit conditional closure, not evolving
  // the full polarized Planck reference. GL8 local moments.
  let z=[-0.9602898564975363,-0.7966664774136267,-0.525532409916329,-0.1834346424956498,0.1834346424956498,0.525532409916329,0.7966664774136267,0.9602898564975363];
  let wt=[0.1012285362903763,0.2223810344533745,0.3137066458778873,0.362683783378362,0.362683783378362,0.3137066458778873,0.2223810344533745,0.1012285362903763];
  let mut minratio:f64=1.;
  for k in 0..nx{
   let x=self.x[k];let f0=1./x.exp_m1();let r:Vec<_>=rays.iter().map(|(d,_,_)|1./(x/d).exp_m1()).collect();
   let mean=(0..nr).map(|i|rays[i].2*r[i]).sum::<f64>();
   let (mut m0,mut m1,mut m2)=(0.,0.,0.);
   for (&q,&w) in z.iter().zip(&wt){
    let v=x*(q*self.dl/2.).exp();let b=(v-x)/dx[k];let p=w*self.dl/2.*v.powi(3)/v.exp_m1();
    m0+=p;m1+=p*b;m2+=p*b*b;
   }
   let det=m0*m2-m1*m1;
   if det<=0.||!det.is_finite(){return Err("finite reference moment matrix".into())}
   for i in 0..nr{
    let r=r[i]/mean;ratio[i][k]=r;
    let norm=r*rays[i].2;
    let a=(m2*nn[i][k]-m1*uu[i][k])/(det*norm);
    let b=(m0*uu[i][k]-m1*nn[i][k])/(det*norm);
    aa[i][k]=a;bb[i][k]=b;
    minratio=minratio.min(1.+a+b*(edges[k]-x)/dx[k]).min(1.+a+b*(edges[k+1]-x)/dx[k]);
   }
  }
  if minratio<=0.||!minratio.is_finite(){return Err(format!("finite local reconstruction realizability {minratio:e}"))}
  let mut dn=vec![vec![0.;nx];nr];let mut du=dn.clone();
  let mut pair_abs=0.;
  // Two positive GH4 nodes. All ordered angular pairs at positive eta
  // cover unordered scattering pairs once; exactly forward pair cancels.
  let gh=[(0.5246476232752903,0.4541241452319315),(1.6506801238857846,0.0458758547680685)];
  for i in 0..nr{for j in 0..nr{
   if i==j{continue}
   let mu=(0..3).map(|k|rays[i].1[k]*rays[j].1[k]).sum::<f64>().clamp(-1.,1.);
   let sig=(4.*theta*(1.-mu)).sqrt();
   let kw=0.75*(1.+mu*mu)*rays[i].2*rays[j].2;
   for &(z,w) in &gh{
    let eta=sig*z;let em=eta.exp_m1();let ratio_e=1.+em;let hi=y1-eta;
    if hi<=y0{continue}
    for a in 0..nx{
     let left=y0+a as f64*self.dl;let right=(left+self.dl).min(hi);
     if right<=left{continue}
     let b0=cell(left+eta+1e-14);let split=(y0+(b0+1) as f64*self.dl-eta).clamp(left,right);
     for (lo,hi) in [(left,split),(split,right)]{
      if hi<=lo{continue}
      let b=cell((lo+hi)/2.+eta);
      for t in [-0.5773502691896258,0.5773502691896258]{
       let x=((lo+hi)/2.+(hi-lo)/2.*t).exp();let xp=x*ratio_e;
       let ri=ratio[i][a]/x.exp_m1();let rj=ratio[j][b]/xp.exp_m1();
       let di=ri*(aa[i][a]+bb[i][a]*(x-self.x[a])/dx[a]);
       let dj=rj*(aa[j][b]+bb[j][b]*(xp-self.x[b])/dx[b]);
       let dg=x*em/tr;let p=kw*w*(hi-lo)/2.*(x*x*x).min(xp*xp*xp*(-dg).exp());
       let flux=depth*self.cap*p*(di-dj-dg.exp_m1()*(dj*(1.+ri)+rj*di+di*dj));
       dn[i][a]-=flux;dn[j][b]+=flux;
       du[i][a]-=flux*(x-self.x[a]);du[j][b]+=flux*(xp-self.x[b]);
       pair_abs+=flux.abs();
      }
     }
    }
   }
  }}
  let mut out=self.empty();let mut l1=0.;let mut el1=0.;let mut maxmean:f64=0.;
  for k in 0..nx{
   let n=(0..nr).map(|i|dn[i][k]).sum::<f64>();let u=(0..nr).map(|i|du[i][k]).sum::<f64>();
   let mut sn=0.;let mut su=0.;
   for i in 0..nr{
    let a=dn[i][k]-rays[i].2*n;let b=du[i][k]-rays[i].2*u;sn+=a;su+=b;
    let x=self.x[k];let d=rays[i].0;let q=x/d;let j=self.q.partition_point(|v|*v<=q);
    if j==0||j>=nq{return Err("finite remap boundary".into())}
    // Deposit signed N and centered U exactly in q; no positive constraint
    // on the signed increment alone. Full-field checks occur at next trial.
    let ql=self.q[j-1];let qr=self.q[j];let high=(a*(q-ql)+b/d)/(qr-ql);let low=a-high;
    out[i*nq+j-1]+=low;out[i*nq+j]+=high;
    l1+=low.abs()+high.abs();el1+=(low*ql*d*KT0/g.a).abs()+(high*qr*d*KT0/g.a).abs();
   }
   maxmean=maxmean.max(sn.abs()).max(su.abs()/self.x[k]);
  }
  let (u,_,n)=self.moments(&out,g)?;
  if n.abs()>1e-10*l1.max(pair_abs*1e-15).max(1e-300)||u.abs()>1e-10*el1.max(1e-300)||maxmean>1e-10*l1.max(pair_abs*1e-15).max(1e-300){return Err(format!("finite moment remap conservation {n:e} {u:e} {l1:e} {maxmean:e}"))}
  Ok((out,[l1,n.abs(),u.abs(),maxmean]))
 }
 pub fn angular_covariance(&self,s:&[f64],g:&OwnedState)->Result<(Vec<f64>,[f64;4]),String>{
  let rays=self.ray(g)?;let nr=rays.len();let nx=self.x.len();
  let mut stock=vec![vec![0.;nx];nr];let mut tail=0.;
  for (i,(row,(d,_,w))) in s.chunks_exact(self.q.len()).zip(&rays).enumerate(){
   for (&q,&n) in self.q.iter().zip(row){
    if n==0.{continue}let x=q*d;let j=self.x.partition_point(|v|*v<=x);
    if j==0||j==nx{
     if x>=self.x[0]*(-self.dl/2.).exp() && x<=self.x[nx-1]*(self.dl/2.).exp(){
      stock[i][if j==0{0}else{nx-1}]+=n;
     }else{tail+=n.abs();}
    }else{let t=(x-self.x[j-1])/(self.x[j]-self.x[j-1]);stock[i][j-1]+=n*(1.-t);stock[i][j]+=n*t;}
   }
   for (v,x) in stock[i].iter_mut().zip(&self.x){*v/=w*self.cap*x.powi(3)*self.dl;}
  }
  let w:Vec<_>=rays.iter().map(|z|z.2).collect();
  let mut m=vec![vec![0.;nr];nr];
  for i in 0..nr{for j in 0..nr{let mu=(0..3).map(|k|rays[i].1[k]*rays[j].1[k]).sum::<f64>();m[i][j]=w[i]*w[j]*0.75*(1.+mu*mu)*(1.-mu);}}
  for _ in 0..64{
   let a:Vec<_>=m.iter().zip(&w).map(|(r,w)|(w/r.iter().sum::<f64>()).sqrt()).collect();
   for i in 0..nr{for j in 0..nr{m[i][j]*=a[i]*a[j];}}
  }
  let err=m.iter().zip(&w).map(|(r,w)|(r.iter().sum::<f64>()-w).abs()).fold(0.,f64::max);
  if err>1e-12{return Err("angular covariance marginal".into())}
  let mut refd=vec![vec![0.;nx];nr];let mut min=f64::INFINITY;
  let mut maxref:f64=0.;let mut cov=vec![0.;nx];
  for j in 0..nx{
   let x=self.x[j];let f0=1./x.exp_m1();
   // R_i=f_P(x/d_i), normalized to have exact angle mean f_P(x).
   let r:Vec<_>=rays.iter().map(|(d,_,_)|1./(x/d).exp_m1()).collect();
   let mean=r.iter().zip(&w).map(|(a,b)|a*b).sum::<f64>();
   let dm=(0..nr).map(|i|w[i]*stock[i][j]).sum::<f64>();
   for i in 0..nr{
    let rr=r[i]*(f0/mean);
    let ratio=(rr+stock[i][j])/f0;min=min.min(ratio);
    refd[i][j]=rr-f0;maxref=maxref.max((rr/f0-1.).abs());
    stock[i][j]-=dm;
   }
  }
  if min<0.||!min.is_finite(){return Err(format!("angular full reference occupation {min:e}"))}
  for k in 0..nx-1{
   let mut c=0.;
   for i in 0..nr{for j in 0..nr{
    let a=stock[i][k];let b=stock[j][k+1];
    c+=m[i][j]*(a*b+refd[i][k]*b+a*refd[j][k+1]);
   }}
   cov[k]=c;
  }
  if cov.iter().any(|v|!v.is_finite()){return Err("angular covariance".into())}
  Ok((cov,[min,maxref,tail,err]))
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
 fn shape_identity_and_conservation(){
  let x:Vec<_>=(0..64).map(|i|0.01*(i as f64*0.1).exp()).collect();
  let own=ThomsonOwner::new(0.,32,4,8,4,8,16).unwrap();let g=own.initial(0.05,[0.;5]).unwrap().geometry;
  let m=FreqRays::new(&x,1e6,g.a,4).unwrap();let z=m.empty();
  let (a,_)=m.finite_moment_increment(&z,&g,1e-6,1.,1e-8).unwrap();assert_eq!(a,z);
  let mut s=z.clone();let nq=m.q.len();
  for (i,(_,n,w)) in m.ray(&g).unwrap().iter().enumerate(){s[i*nq+20]=w*(1.+0.2*(3.*n[2]*n[2]-1.)/2.);}
  let (a,d)=m.finite_moment_increment(&s,&g,1e-6,1.,1e-8).unwrap();assert!(d[0]>0.&&d[1]<1e-11*d[0]);
  assert!(a.iter().any(|v|*v!=0.));
 }
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
