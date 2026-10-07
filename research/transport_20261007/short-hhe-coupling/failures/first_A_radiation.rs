use crate::{v2::{self,Owners},Fallible,err,positive,nonnegative,product,material};
use rei_microphysics::{igm_config::HistoryConfig,igm_background::FlrwPoint,igm_photo::packet_opacity,HHeModel,Absorber,AtomicProvider,verner_cutoff_ev};
pub const SPECIES:[Absorber;3]=[Absorber::HI,Absorber::HeI,Absorber::HeII];
#[derive(Clone,Debug)]
pub struct Grid{pub nodes:Vec<(f64,f64)>,pub intervals:usize,pub base:usize,pub order:usize}
impl Grid{
 pub fn new(cfg:&HistoryConfig,base:usize,order:usize)->Fallible<Self>{
  if ![128,256,512].contains(&base)||![2,4].contains(&order){return Err("undeclared quadrature".into())}
  let s0=cfg.start;let s1=s0+cfg.max_dln_a;
  let lo=s0+cfg.source.energy_min_ev.ln();let hi=s1+cfg.source.energy_max_ev.ln();
  let mut cuts=(0..=base).map(|i|lo+(hi-lo)*i as f64/base as f64).collect::<Vec<_>>();
  let energies=[cfg.source.energy_min_ev,cfg.source.energy_max_ev,verner_cutoff_ev(SPECIES[0]),verner_cutoff_ev(SPECIES[1]),verner_cutoff_ev(SPECIES[2])];
  // Union of all prescribed phase-segment and endpoint-control time grids.
  for i in 0..=24{let s=time_at(cfg,i,24);for e in energies{let eta=s+e.ln();if eta>lo&&eta<hi{cuts.push(eta)}}}
  cuts.sort_by(f64::total_cmp);cuts.dedup();let intervals=cuts.len()-1;
  let mut nodes=Vec::new();
  for ab in cuts.windows(2){for (eta,w) in positive_rule(ab[0],ab[1],order){if !(eta>ab[0]&&eta<ab[1]){return Err(format!("unresolved quadrature cell {:?}",ab))}positive(w)?;nodes.push((eta,w));}}
  if nodes.len()>4096{return Err("live sample cap".into())}
  Ok(Self{nodes,intervals,base,order})
 }
}
#[derive(Clone,Debug)]
pub struct Radiation{pub density:Vec<f64>,pub owners:Owners,pub min_heat:f64}
pub fn characteristic(cfg:&HistoryConfig,p:FlrwPoint,y:[f64;4],eta:f64,s0:f64,s1:f64,f:f64)->Fallible<Owners>{
 nonnegative(f)?;
 if s1<=s0{return Err("invalid temporal cell".into())}
 let g=material::gas(y)?;
 let source_start=eta-cfg.source.energy_max_ev.ln();let source_stop=eta-cfg.source.energy_min_ev.ln();
 let tau=eta-verner_cutoff_ev(SPECIES[0]).ln();
 if tau<=s0{if f!=0.0{return Err("unsupported initial outflow stock".into())}return Ok(Owners::default())}
 let end=s1.min(tau);let mut events=vec![source_start,source_stop];for a in SPECIES{events.push(eta-verner_cutoff_ev(a).ln())}
 let cuts=v2::topology(s0,end,&events);let mut stock=f;let mut sum=Owners::default();
 for ab in cuts.windows(2){let (a,b)=(ab[0],ab[1]);let mid=(a+b)*0.5;if !(mid>a&&mid<b){return Err(format!("unresolved temporal geometry eta={eta:.17e},a={a:.17e},b={b:.17e}"))}
  let e=positive((eta-mid).exp())?;let opacity=packet_opacity(&g,e,p.n_h_cm3,p.n_he_cm3).map_err(err)?;
  let rates=std::array::from_fn(|i|opacity[i]/p.hubble_per_s);
  let q=if mid>=source_start&&mid<source_stop{positive(cfg.source.photons_per_h_per_s/((1.0/cfg.source.energy_min_ev-1.0/cfg.source.energy_max_ev)*e*p.hubble_per_s))?}else{0.0};
  let mut o=v2::kernel(stock,q,rates,b-a,(eta-a).exp()).map_err(|e|format!("kernel {e}; eta={eta:.17e},a={a:.17e},b={b:.17e},Eend={:.17e}",(eta-a).exp()*(-(b-a)).exp()))?;
  // Inspect authoritative final state before stripping stock from cumulative owners.
  let mut check=Owners::default();v2::try_add_scaled(&mut check,o,1.0).map_err(err)?;
  for i in 0..3 {nonnegative(o.be[i]-HHeModel::controlled_fixture().ev_erg*HHeModel::controlled_fixture().threshold_ev[i]*o.an[i])?;}
  stock=o.n;o.n=0.0;o.u=0.0;o.ln_n=None;o.ln_u=None;v2::try_add_scaled(&mut sum,o,1.0).map_err(err)?;
 }
 if tau<=s1{sum.outn=stock;sum.oute=product(product(HHeModel::controlled_fixture().ev_erg,verner_cutoff_ev(SPECIES[0]))?,stock)?;}else{
  sum.n=stock;sum.u=product(product(HHeModel::controlled_fixture().ev_erg,(eta-s1).exp())?,stock)?;
  if stock>0.0{sum.ln_n=Some(stock.ln());sum.ln_u=Some(sum.u.ln())}
 }
 if eta>=s1+cfg.source.energy_max_ev.ln()&&sum.n!=0.0{return Err("nonzero at/beyond causal source front".into())}
 Ok(sum)
}
pub fn transaction(cfg:&HistoryConfig,grid:&Grid,p:FlrwPoint,y:[f64;4],s0:f64,s1:f64,old:&[f64])->Fallible<Radiation>{
 if old.len()!=grid.nodes.len(){return Err("grid/state length mismatch".into())}
 material::rhs(y,p)?;
 let mut owners=Owners::default();let mut density=Vec::with_capacity(old.len());let mut min_heat=f64::INFINITY;
 for (j,&(eta,w)) in grid.nodes.iter().enumerate(){let o=characteristic(cfg,p,y,eta,s0,s1,old[j])?;density.push(o.n);v2::try_add_scaled(&mut owners,o,w).map_err(err)?;for i in 0..3{min_heat=min_heat.min(o.be[i]-v2::EPS*v2::CHI[i]*o.an[i]);}}
 Ok(Radiation{density,owners,min_heat})
}
pub fn inventory(grid:&Grid,s:f64,density:&[f64])->Fallible<[f64;2]>{let mut n=0.;let mut e=0.;for (&(eta,w),&f) in grid.nodes.iter().zip(density){n+=product(w,f)?;e+=product(product(product(w,f)?,(eta-s).exp())?,HHeModel::controlled_fixture().ev_erg)?;}Ok([nonnegative(n)?,nonnegative(e)?])}
pub fn gamma(grid:&Grid,s:f64,density:&[f64],p:FlrwPoint)->Fallible<[f64;3]>{let c=HHeModel::controlled_fixture();let mut out=[0.;3];for (&(eta,w),&f) in grid.nodes.iter().zip(density){for i in 0..3{let sigma=AtomicProvider::reference().cross_section(SPECIES[i],(eta-s).exp()).map_err(err)?;out[i]+=product(product(product(product(c.c_cm_s,p.n_h_cm3)?,sigma)?,f)?,w)?;}}for v in out{nonnegative(v)?;}Ok(out)}

/// Canonical common time lattice: all prescribed denominators divide 24.
pub fn time_at(cfg:&HistoryConfig,k:usize,n:usize)->f64{assert!(n>0&&24%n==0);cfg.start+cfg.max_dln_a*(k*(24/n)) as f64/24.0}
/// Explicit positive Gauss4, independently formed from closed-form nodes/weights.
fn positive_rule(a:f64,b:f64,order:usize)->Vec<(f64,f64)>{
 let h=(b-a)*0.5;
 let nodes=if order==2{vec![(-1./3f64.sqrt(),1.),(1./3f64.sqrt(),1.)]}else{
  let d=(6f64/5.).sqrt();let inner=((3.-2.*d)/7.).sqrt();let outer=((3.+2.*d)/7.).sqrt();let wi=(18.+30f64.sqrt())/36.;let wo=(18.-30f64.sqrt())/36.;vec![(-outer,wo),(-inner,wi),(inner,wi),(outer,wo)]
 };nodes.into_iter().map(|(x,w)|(a+h*(1.+x),h*w)).collect()
}
