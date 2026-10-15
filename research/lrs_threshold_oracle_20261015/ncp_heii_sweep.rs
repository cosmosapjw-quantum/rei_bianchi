//! Independent HeII Bianchi I threshold sweep, Verner 1996 primary fit.
//! Units: E in eV, sigma in Mb; opacity c*n0*sigma(Eth)/H0=0.3.
//! A single fixed HeII absorber (not coupled EoR). Deterministic std threads.
use std::{f64::consts::PI, cmp::Ordering, io::{Write,BufWriter}, fs::File, time::Instant};
const ETH:f64=54.42;
const GL8:[(f64,f64);8]=[
(-0.9602898564975363,0.1012285362903763),
(-0.7966664774136267,0.2223810344533745),
(-0.5255324099163290,0.3137066458778873),
(-0.1834346424956498,0.3626837833783620),
(0.1834346424956498,0.3626837833783620),
(0.5255324099163290,0.3137066458778873),
(0.7966664774136267,0.2223810344533745),
(0.9602898564975363,0.1012285362903763)];
fn sigma(e:f64)->f64{
 if e<ETH{return 0.}
 let y=e/1.720;
 13690.0*(y-1.).powi(2)*y.powf(2.963/2.-5.5)*(1.+(y/32.88).sqrt()).powf(-2.963)
}
fn ray(e0:f64,mu:f64,s:f64,x:f64)->(f64,f64){
 let b=s*x;
 let f=(1.-mu*mu)*(2.*b).exp()+mu*mu*(-4.*b).exp();
 (e0*(-x).exp()*f.sqrt(),mu*(-2.*b).exp()/f.sqrt())
}
fn crossing(e0:f64,mu:f64,s:f64,xmax:f64)->f64{
 if e0<=ETH{return 0.}
 if ray(e0,mu,s,xmax).0>=ETH{return xmax;}
 let (mut low,mut high)=(0.,xmax);
 for _ in 0..64{let mid=(low+high)/2.;if ray(e0,mu,s,mid).0>ETH{low=mid;}else{high=mid;}}
 (low+high)/2.
}
fn absorbed(e0:f64,mu:f64,s:f64,xmax:f64,sigma_th:f64)->f64{
 let xcross=crossing(e0,mu,s,xmax);
 if xcross<=0.{return 0.}
 let dx=xcross/8.;let mut tau=0.;
 for k in 0..8{
   let center=(k as f64+0.5)*dx;let half=0.5*dx;
   for (node,weight) in GL8{
    let x=center+half*node;
    tau+=0.3*half*weight*(-3.*x).exp()*sigma(ray(e0,mu,s,x).0)/sigma_th;
   }
 }
 -(-tau).exp_m1()
}
fn gauss(n:usize)->Vec<(f64,f64)>{
 let mut xs=Vec::with_capacity(n);
 for i in 0..n{
  let mut x=((i as f64+0.75)*PI/(n as f64+0.5)).cos();
  let mut dp=1.;
  for _ in 0..25{
   let (mut p0,mut p1)=(1.,x);
   if n>1{for k in 2..=n{
      let q=((2*k-1) as f64*x*p1-(k-1) as f64*p0)/k as f64;
      p0=p1;p1=q;
   }}
   dp=if n==1{1.}else{(n as f64)*(x*p1-p0)/(x*x-1.)};
   let h=p1/dp;x-=h;
   if h.abs()<2e-15{break;}
  }
  xs.push((x,2./((1.-x*x)*dp*dp)));
 }
 xs.sort_by(|a,b|a.0.partial_cmp(&b.0).unwrap_or(Ordering::Equal));
 xs
}
fn cuts(e0:f64,s:f64,x:f64)->Vec<f64>{
 let b=s*x;if b.abs()<1e-14{return vec![-1.,1.];}
 let t=((ETH/e0)*x.exp()).powi(2);
 let v=(t-(2.*b).exp())/((-4.*b).exp()-(2.*b).exp());
 if v>0. && v<1.{let u=v.sqrt();vec![-1.,-u,u,1.]}else{vec![-1.,1.]}
}
#[derive(Clone,Copy)]struct Case{e0:f64,s:f64,x:f64}
#[derive(Clone,Copy)]struct Angular{a:f64,u:f64,par:f64}
impl Angular{fn pi(&self)->f64{(3.*self.par-self.u)/(2.*self.u)}}
fn integrate(c:Case,bounds:&[f64],q:&[(f64,f64)],sigma_th:f64)->Angular{
 let(mut a,mut u,mut p)=(0.,0.,0.);
 for interval in bounds.windows(2){
  let mid=(interval[0]+interval[1])/2.;let h=(interval[1]-interval[0])/2.;
  for &(node,w) in q{
   let mu=mid+h*node;let weight=0.5*h*w;
   let (e,muf)=ray(c.e0,mu,c.s,c.x);
   let absorbed=absorbed(c.e0,mu,c.s,c.x,sigma_th);
   a+=weight*absorbed;u+=weight*(1.-absorbed)*e;
   p+=weight*(1.-absorbed)*e*muf*muf;
  }
 }
 Angular{a,u,par:p}
}
#[derive(Clone)]struct Row{idx:usize,c:Case,cut:bool,reference:f64,plain_err:f64,cut_err:f64,plain_pi:f64,cut_pi:f64}
fn calc(idx:usize,c:Case,q8:&[(f64,f64)],q24:&[(f64,f64)],q64:&[(f64,f64)],sig:f64)->Row{
 let boundary=cuts(c.e0,c.s,c.x);let whole=[-1.,1.];
 let refv=integrate(c,&boundary,q64,sig);
 let plain=integrate(c,&whole,q24,sig);
 let adaptive=integrate(c,&boundary,q8,sig);
 Row{idx,c,cut:boundary.len()>2,reference:refv.a,
     plain_err:(plain.a-refv.a).abs(),cut_err:(adaptive.a-refv.a).abs(),
     plain_pi:(plain.pi()-refv.pi()).abs(),cut_pi:(adaptive.pi()-refv.pi()).abs()}
}
fn main()->std::io::Result<()>{
 let args:Vec<String>=std::env::args().collect();
 if args.len()!=3{panic!("usage output.csv workers");}
 let workers:usize=args[2].parse().expect("integer workers");
 assert!(workers>0 && workers<=64);
 let before=Instant::now();
 let mut cases=Vec::new();
 for i in 0..33{for j in 0..17{for k in 0..11{
    cases.push(Case{e0:62.+90.*i as f64/32.,
                    s:-0.08+0.01*j as f64,x:0.18+0.08*k as f64});
 }}}
 let (q8,q24,q64)=(gauss(8),gauss(24),gauss(64));
 let reference=&cases;let sig=sigma(ETH);
 let mut out=Vec::new();
 std::thread::scope(|scope|{
  let handles:Vec<_>=(0..workers).map(|id|{
    let q8r=&q8;let q24r=&q24;let q64r=&q64;
    scope.spawn(move||{
      let mut local=Vec::new();
      for idx in (id..reference.len()).step_by(workers){
        local.push(calc(idx,reference[idx],q8r,q24r,q64r,sig));
      }
      local
    })
  }).collect();
  for handle in handles{out.extend(handle.join().expect("worker failed"));}
 });
 out.sort_by_key(|r|r.idx);
 let mut file=BufWriter::new(File::create(&args[1])?);
 writeln!(file,"idx,E0_ev,s_over_H,Xend,has_cuts,heii_abs_ref,plain24_abs_error,split8_abs_error,plain24_pi_error,split8_pi_error")?;
 let (mut crossed,mut better,mut plain_errs,mut split_errs)=(0usize,0usize,Vec::<f64>::new(),Vec::<f64>::new());
 for r in &out{
   writeln!(file,"{},{:0.12},{:0.12},{:0.12},{},{:0.16e},{:0.16e},{:0.16e},{:0.16e},{:0.16e}",
      r.idx,r.c.e0,r.c.s,r.c.x,u8::from(r.cut),r.reference,
      r.plain_err,r.cut_err,r.plain_pi,r.cut_pi)?;
   if r.cut && r.reference>1e-8{
      crossed+=1;if r.cut_err<r.plain_err{better+=1;}
      plain_errs.push(r.plain_err/r.reference);
      split_errs.push(r.cut_err/r.reference);
   }
 }
 file.flush()?;
 plain_errs.sort_by(|a,b|a.partial_cmp(b).unwrap());split_errs.sort_by(|a,b|a.partial_cmp(b).unwrap());
 println!("N_CASES={}",out.len());println!("N_WORKERS={}",workers);
 println!("N_CROSSING_CASES={}",crossed);println!("SPLIT_WINS={}",better);
 if crossed>0{
  let rank=((crossed-1) as f64*0.95).round() as usize;
  println!("PLAIN_P95_REL={:0.12e}",plain_errs[rank]);
  println!("SPLIT_P95_REL={:0.12e}",split_errs[rank]);
  println!("PLAIN_MAX_REL={:0.12e}",plain_errs[crossed-1]);
  println!("SPLIT_MAX_REL={:0.12e}",split_errs[crossed-1]);
 }
 println!("SECONDS={:0.3}",before.elapsed().as_secs_f64());
 Ok(())
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn fit(){assert!((sigma(ETH)-1.5872802575386487).abs()<2e-13);}
 #[test]fn gaussian(){for n in [8,24,64]{let q=gauss(n);
   assert!((q.iter().map(|x|x.1).sum::<f64>()-2.).abs()<1e-12);
   assert!((q.iter().map(|x|x.0*x.0*x.1).sum::<f64>()-2./3.).abs()<1e-12);
 }}
 #[test]fn threshold(){let q=cuts(100.,0.03,0.61);
   assert_eq!(q.len(),4);assert!((ray(100.,q[1],0.03,0.61).0-ETH).abs()<1e-12);
 }
 #[test]fn positivity(){let refmb=sigma(ETH);for s in [-0.07,0.,0.07]{
    for mu in [-0.9,0.,0.9]{
       assert!((0.0..=1.0).contains(&absorbed(100.,mu,s,0.6,refmb)));
 }}}}
