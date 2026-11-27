const KT0:f64=8.617333262145e-5*2.7255;
struct Grid{x:Vec<f64>,dl:f64,cap:f64}
struct State{a:f64}
impl Grid {
fn check(&self,mut stock:Vec<f64>,g:&State)->Result<Vec<f64>,String>{
let nx=self.x.len();
  let before=stock.clone();
  let refs:Vec<f64>=self.x.iter().map(|x|x.powi(3)*self.dl/x.exp_m1()).collect();
  let mut full:Vec<f64>=stock.iter().zip(&refs).map(|(s,r)|s+r).collect();
  let floor:Vec<f64>=refs.iter().map(|x|x*1e-12).collect();
  let mut repairs=0usize;
  for i in 0..nx {
   let need=floor[i]-full[i];
   if need<=0.{continue}
   let mut rem=need;
   let mut left=i;let mut right=i+1;
   while rem>1e-14*need {
    while left>0 {left-=1;if full[left]>floor[left]{break}}
    while right<nx&&full[right]<=floor[right]{right+=1}
    if left>=i||right>=nx||full[left]<=floor[left]{return Err(format!("DG positive scalar projection infeasible at bin {i} x={:e}, need={rem:e}",self.x[i]))}
    let f=(self.x[right]-self.x[i])/(self.x[right]-self.x[left]);let g=1.-f;
    if !(f>0.&&g>0.){return Err("DG positive scalar donor geometry".into())}
    let m=rem.min((full[left]-floor[left])/f).min((full[right]-floor[right])/g);
    if m<=0.||!m.is_finite(){return Err("DG positive scalar donor".into())}
    // Both sum of number and sum x*number are unchanged in exact arithmetic.
    stock[i]+=m;stock[left]-=f*m;stock[right]-=g*m;
    full[i]+=m;full[left]-=f*m;full[right]-=g*m;rem-=m;
    if rem>1e-14*need {
     // At least one donor is exhausted; restart nearest-donor search.
     left=i;right=i+1;
    }
   }
   repairs+=1;
  }
  if repairs>0 {
   let n: f64=stock.iter().zip(&before).map(|(a,b)|a-b).sum();
   let u: f64=stock.iter().zip(&before).zip(&self.x).map(|((a,b),x)|(a-b)*x).sum();
   let moved: f64=stock.iter().zip(&before).map(|(a,b)|(a-b).abs()).sum();
   let total: f64=before.iter().map(|x|x.abs()).sum();
   if n.abs()>1e-12*moved||u.abs()>1e-12*moved*self.x[nx-1]{return Err("DG positive scalar correction moment defect".into())}
   eprintln!("DG_POSITIVE_SCALAR repairs={repairs} relative_L1={:.17e} number_res={:.17e} energy_res={:.17e}",moved/total.max(1e-300),n*self.cap,u*self.cap*KT0/g.a);
  }

Ok(stock)
}
}
fn main()->Result<(),String>{
 let g=Grid{x:vec![1.,2.,3.,4.,5.],dl:0.1,cap:1.};
 let s=State{a:0.05};
 let r:Vec<f64>=g.x.iter().map(|x|x.powi(3)*g.dl/x.exp_m1()).collect();
 let sum=|q:&[f64]|q.iter().sum::<f64>();
 let en=|q:&[f64]|q.iter().zip(&g.x).map(|(a,b)|a*b).sum::<f64>();
 for f in [vec![1.,1.,-0.1,1.,1.],vec![1.,0.01,-0.1,0.01,1.],vec![1.,1.,0.1,1.,1.]] {
 let q:Vec<f64>=f.iter().zip(&r).map(|(x,y)|x-y).collect();
 let z=g.check(q.clone(),&s)?;
 assert!(z.iter().zip(&r).all(|(a,b)|a+b>=0.));
 assert!((sum(&z)-sum(&q)).abs()<1e-14 && (en(&z)-en(&q)).abs()<1e-14);
 println!("positive repair {:?}, number {:.17e}, energy {:.17e}",f,sum(&z)-sum(&q),en(&z)-en(&q));
 }
 let q:Vec<f64>=[-0.1,1.,1.,1.,1.].iter().zip(&r).map(|(x,y)|x-y).collect();
 assert!(g.check(q,&s).is_err());println!("edge infeasibility correctly rejected");Ok(())
}
