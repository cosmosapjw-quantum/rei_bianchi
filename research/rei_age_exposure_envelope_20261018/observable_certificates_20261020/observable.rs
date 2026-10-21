//! Additive fixed-export observable certificates; upstream source is unchanged.
use rei_vigilode_age_transport::{certified::{exact,exp_negative,rational_interval}, directed::{self,Interval as I}};
use num_rational::BigRational as Q;
use num_traits::Zero;
use rayon::prelude::*;
use serde::Deserialize;
use serde_json::{json,Value};
use std::{collections::{BTreeMap,HashMap,HashSet},path::Path,time::Instant};
const CLOCKS:[usize;4]=[8,16,32,64];
const POPS:[&str;3]=["all","sensitive","passive"];
fn p(x:f64)->I{I::point(x).unwrap()}
fn add(a:I,b:I)->I{a.add(b).unwrap()}
fn sub(a:I,b:I)->I{a.sub(b).unwrap()}
fn mul(a:I,b:I)->I{a.mul(b).unwrap()}
fn neg(a:I)->I{I::new(-a.hi,-a.lo).unwrap()}
fn upadd(a:f64,b:f64)->f64{directed::add_up(a,b).unwrap()}
fn upmul(a:f64,b:f64)->f64{directed::mul_up(a,b).unwrap()}
fn updiv(a:f64,b:f64)->f64{directed::div_up(a,b).unwrap()}
fn absup(a:I)->f64{a.lo.abs().max(a.hi.abs())}
fn ji(a:I)->Value{json!([a.lo,a.hi])}
fn nonnegative(a:I)->I{I::new(a.lo.max(0.0),a.hi).unwrap()}
fn h(v:I)->I{let z=sub(p(1.0),v);I::new(z.lo.max(0.0),z.hi.min(1.0)).unwrap()}
#[derive(Deserialize)]struct Model{observe_time_s:f64,clocks:BTreeMap<String,Vec<f64>>}
struct Rate{lambda:Q,shares:[I;3]}
struct Node{cohort:usize,w:f64,energy:f64,rate:usize}
struct Input{nodes:Vec<Node>,rates:Vec<Rate>,ages:Vec<Vec<Q>>}
fn load(path:&Path)->Input{
 let m:Model=serde_json::from_slice(&std::fs::read(path.join("model.json")).unwrap()).unwrap();
 let ages=CLOCKS.iter().map(|n|m.clocks[&n.to_string()].iter().map(|b|exact(m.observe_time_s)-exact(*b)).collect()).collect();
 let data=std::fs::read_to_string(path.join("nodes.csv")).unwrap();let mut nodes=vec![];let mut rates=vec![];let mut lookup=HashMap::new();
 for line in data.lines().skip(1){let x:Vec<_>=line.split(',').collect();assert_eq!(x.len(),17);let f=|k:usize|x[k].parse::<f64>().unwrap();
 let ls=[f(12),f(13),f(14)];assert!(ls.iter().all(|x|x.is_finite()&&*x>=0.0));
 let rate=*lookup.entry(ls.map(f64::to_bits)).or_insert_with(||{let lambda=ls.iter().map(|x|exact(*x)).sum::<Q>();
 let shares=std::array::from_fn(|k|if lambda.is_zero(){p(0.0)}else{rational_interval(&(exact(ls[k])/&lambda))});let id=rates.len();rates.push(Rate{lambda,shares});id});
 let cohort=x[0].parse::<usize>().unwrap();assert!(cohort<64);assert_eq!(f(16),m.clocks["64"][cohort]);
 assert!(f(4).is_finite()&&f(4)>=0.0&&f(11).is_finite()&&f(11)>=0.0);
 nodes.push(Node{cohort,w:f(4),energy:f(11),rate});}
 Input{nodes,rates,ages}
}
struct Cache{values:HashMap<Q,I>,requests:usize,unique:usize}
impl Cache{
 fn new(input:&Input)->Self{let mut seen=HashSet::new();let mut qs=vec![];let mut requests=0;
 for node in &input.nodes{let r=&input.rates[node.rate];
 for k in 0..4{let age=&input.ages[k][node.cohort*CLOCKS[k]/64];let tau=&r.lambda*age;requests+=1;if seen.insert(tau.clone()){qs.push(tau);}}
 for k in 0..3{let a=&input.ages[k][node.cohort*CLOCKS[k]/64];let b=&input.ages[3][node.cohort];let d=if a>=b{a-b}else{b-a};let tau=&r.lambda*d;requests+=1;if seen.insert(tau.clone()){qs.push(tau);}}}
 // Identity pair needs exp(0), including a possible empty input.
 let zero=Q::zero();requests+=1;if seen.insert(zero.clone()){qs.push(zero);}
 let vs:Vec<_>=qs.par_iter().map(exp_negative).collect();let unique=qs.len();Self{values:qs.into_iter().zip(vs).collect(),requests,unique}}
 fn get(&self,lambda:&Q,age:&Q)->I{self.values[&(lambda*age)]}
}
#[derive(Clone)]struct Totals{v:[I;9],initial:I,initial_energy:I}
impl Totals{fn zero()->Self{Self{v:[p(0.0);9],initial:p(0.0),initial_energy:p(0.0)}}
 fn push(&mut self,row:[I;9],w:I,e:I){for k in 0..9{self.v[k]=add(self.v[k],row[k]);}self.initial=add(self.initial,w);self.initial_energy=add(self.initial_energy,mul(w,e));}
 fn mean(&self)->Option<I>{if self.v[0].lo>0.0{Some(self.v[2].div(self.v[0]).unwrap())}else{None}}
 fn value(&self)->Value{let num=sub(add(self.v[0],self.v[7]),self.initial);let energy=sub(add(self.v[1],self.v[8]),self.initial_energy);
 assert!(num.contains_zero()&&energy.contains_zero());json!({"observables":self.v[..7].iter().map(|x|ji(*x)).collect::<Vec<_>>(),"absorbed_number":ji(self.v[7]),"absorbed_same_energy":ji(self.v[8]),"initial_number":ji(self.initial),"initial_same_energy":ji(self.initial_energy),"photon_ledger":ji(num),"same_energy_ledger":ji(energy),"normalized_mean":self.mean().map(ji),"normalized_second":if self.v[0].lo>0.0{Some(ji(self.v[3].div(self.v[0]).unwrap()))}else{None},"normalization_status":if self.v[0].lo>0.0{"RESOLVED"}else{"UNRESOLVED"}})} }
fn cases(input:&Input,cache:&Cache)->Vec<[Totals;3]>{let mut out=vec![];for k in 0..4{let mut ts=std::array::from_fn(|_|Totals::zero());let ai:Vec<_>=input.ages[k].iter().map(rational_interval).collect();
 for node in &input.nodes{let r=&input.rates[node.rate];let idx=node.cohort*CLOCKS[k]/64;let a=ai[idx];let e=cache.get(&r.lambda,&input.ages[k][idx]);let w=p(node.w);let en=p(node.energy);let surv=nonnegative(mul(w,e));let absorbed=nonnegative(mul(w,h(e)));
 let row=[surv,mul(surv,en),mul(surv,a),mul(mul(surv,a),a),mul(absorbed,r.shares[0]),mul(absorbed,r.shares[1]),mul(absorbed,r.shares[2]),absorbed,mul(absorbed,en)];
 let pop=if r.lambda.is_zero(){2}else{1};ts[0].push(row,w,en);ts[pop].push(row,w,en);}out.push(ts);}out}
fn kernels(w:f64,energy:f64,r:&Rate,a:I,d:I,u:I,v:I,older:bool,identical:bool)->[I;7]{
 if identical{return [p(0.0);7];}let hv=h(v);let wu=mul(p(w),u);let k0=if r.lambda.is_zero(){p(0.0)}else{neg(mul(wu,hv))};
 let k1=mul(wu,sub(mul(d,v),mul(a,hv)));let k2=mul(wu,sub(mul(mul(d,add(mul(p(2.0),a),d)),v),mul(mul(a,a),hv)));
 let ks=[k0,mul(p(energy),k0),k1,k2,neg(mul(r.shares[0],k0)),neg(mul(r.shares[1],k0)),neg(mul(r.shares[2],k0))];
 if older{ks}else{ks.map(neg)}
}
fn centered_kernel(w:f64,a:I,d:I,u:I,v:I,c:f64)->I{mul(mul(p(w),u),sub(mul(d,v),mul(sub(a,p(c)),h(v))))}
fn center(mean:I)->(f64,f64){let c=mean.lo*0.5+mean.hi*0.5;let radius=directed::sub_up(c,mean.lo).unwrap().abs().max(directed::sub_up(mean.hi,c).unwrap().abs());(c,radius)}
struct Pair{signed:[[I;7];3],labs:[[f64;7];3],cost:[f64;3],amax:[f64;3],bc:[[f64;2];3]}
fn pair(input:&Input,cache:&Cache,cs:&[[Totals;3]],k:usize)->Value{let mut q=Pair{signed:[[p(0.0);7];3],labs:[[0.0;7];3],cost:[0.0;3],amax:[0.0;3],bc:[[0.0;2];3]};
 let centers:[[Option<(f64,f64)>;2];3]=std::array::from_fn(|pop|[cs[3][pop].mean().map(center),cs[k][pop].mean().map(center)]);
 let av:Vec<_>=(0..64).map(|c|{let aa=&input.ages[k][c*CLOCKS[k]/64];let bb=&input.ages[3][c];let older=aa>=bb;let a=aa.min(bb).clone();let d=if older{aa-bb}else{bb-aa};(rational_interval(&a),rational_interval(&d),a,d,older,rational_interval(aa.max(bb)).hi)}).collect();
 for node in &input.nodes{let r=&input.rates[node.rate];let (a,d,ar,dr,older,amax)=&av[node.cohort];let u=cache.get(&r.lambda,ar);let v=cache.get(&r.lambda,dr);let identical=dr.is_zero();let ks=kernels(node.w,node.energy,r,*a,*d,u,v,*older,identical);let pop=if r.lambda.is_zero(){2}else{1};
 for pp in [0,pop]{for j in 0..7{q.signed[pp][j]=add(q.signed[pp][j],ks[j]);q.labs[pp][j]=upadd(q.labs[pp][j],absup(ks[j]));}
 q.cost[pp]=upadd(q.cost[pp],upmul(node.w,d.hi));q.amax[pp]=q.amax[pp].max(*amax);
 if !identical{for side in 0..2{if let Some((c,_))=centers[pp][side]{q.bc[pp][side]=upadd(q.bc[pp][side],absup(centered_kernel(node.w,*a,*d,u,v,c)));}}}}}
 let mut pops=serde_json::Map::new();for pp in 0..3{let na=cs[k][pp].v[0].lo;let nb=cs[3][pp].v[0].lo;let global_m1=q.cost[pp];let global_m2=upmul(upmul(2.0,q.amax[pp]),q.cost[pp]);let e0=absup(q.signed[pp][0]);
 let normal=if na>0.0&&nb>0.0{let fwd=centers[pp][0].unwrap();let rev=centers[pp][1].unwrap();let uf=updiv(upadd(q.bc[pp][0],upmul(fwd.1,e0)),na);let ur=updiv(upadd(q.bc[pp][1],upmul(rev.1,e0)),nb);let ug=updiv(upadd(q.cost[pp],upmul(q.amax[pp],q.labs[pp][0])),na.min(nb));json!({"status":"RESOLVED","forward":{"center":fwd.0,"radius":fwd.1,"Bc":q.bc[pp][0],"E0":e0,"denominator_lo":na,"upper":uf},"reverse":{"center":rev.0,"radius":rev.1,"Bc":q.bc[pp][1],"E0":e0,"denominator_lo":nb,"upper":ur},"global_upper":ug,"chosen_upper":uf.min(ur).min(ug),"observed_signed_interval":ji(sub(cs[k][pp].mean().unwrap(),cs[3][pp].mean().unwrap()))})}else{json!({"status":"UNRESOLVED"})};
 pops.insert(POPS[pp].to_string(),json!({"signed_difference":q.signed[pp].iter().map(|x|ji(*x)).collect::<Vec<_>>(),"direct_case_difference":(0..7).map(|j|ji(sub(cs[k][pp].v[j],cs[3][pp].v[j]))).collect::<Vec<_>>(),"label_absolute_upper":q.labs[pp],"C_upper":q.cost[pp],"Amax_upper":q.amax[pp],"moment_global_upper":[global_m1,global_m2],"moment_chosen_upper":[q.labs[pp][2].min(global_m1),q.labs[pp][3].min(global_m2)],"normalized_mean_bound":normal}));}
 json!({"coarse":CLOCKS[k],"reference":64,"populations":pops})}
fn study(input:&Input)->Value{let start=Instant::now();let cache=Cache::new(input);let preload=start.elapsed().as_secs_f64();let cs=cases(input,&cache);let pairs:Vec<_>=(0..4).map(|k|pair(input,&cache,&cs,k)).collect();
 let cases:Vec<_>=(0..4).map(|k|{let ps:serde_json::Map<_,_>=(0..3).map(|pp|(POPS[pp].to_string(),cs[k][pp].value())).collect();json!({"clock":CLOCKS[k],"populations":ps})}).collect();
 json!({"schema":"rei.observable_source_age_certificates.v1","PRODUCTION_SCIENTIFIC_ADMISSION":"NOT_ISSUED","model":"same fixed exported labels, source weights, endpoint energies and opacity; birth clocks only","observable_order":["N","U_ev","M1_s","M2_s2","HI","HeI","HeII"],"nodes":input.nodes.len(),"passive_nodes":input.nodes.iter().filter(|n|input.rates[n.rate].lambda.is_zero()).count(),"rates":input.rates.len(),"mode":{"rayon_threads":rayon::current_num_threads(),"preload":true,"requests":cache.requests,"unique_exp_computed":cache.unique,"preload_seconds":preload},"cases":cases,"pairs":pairs,"wall_seconds":start.elapsed().as_secs_f64()})}
fn main(){let args:Vec<_>=std::env::args().collect();let input=load(Path::new(&args[1]));let result=study(&input);std::fs::write(&args[2],serde_json::to_string_pretty(&result).unwrap()+"\n").unwrap();println!("{}",json!({"status":"COMPLETED","nodes":input.nodes.len(),"wall_seconds":result["wall_seconds"]}));}
#[cfg(test)]mod tests{use super::*;fn rate(l:f64)->Rate{Rate{lambda:exact(l),shares:if l==0.0{[p(0.0);3]}else{[p(1.0),p(0.0),p(0.0)]}}}
 fn ks(l:f64,a:f64,d:f64,older:bool,ident:bool)->[I;7]{let r=rate(l);kernels(2.0,3.0,&r,p(a),p(d),exp_negative(&(exact(l)*exact(a))),exp_negative(&(exact(l)*exact(d))),older,ident)}
 #[test]fn passive_nonzero_age(){let x=ks(0.0,2.0,3.0,true,false);assert_eq!(x[0].as_pair(),[0.0,0.0]);assert!(x[2].contains(6.0));assert!(x[3].contains(42.0));}
 #[test]fn identical_birth_zero(){assert!(ks(1.0,2.0,0.0,true,true).iter().all(|x|x.lo==0.0&&x.hi==0.0));}
 #[test]fn positive_and_passive_rates(){assert!(ks(1.0,2.0,1.0,true,false)[0].hi<0.0);assert_eq!(ks(0.0,2.0,1.0,true,false)[0].hi,0.0);}
 #[test]fn moment_stationary_cancellation(){let x=ks(1.0,0.9,0.2,true,false);let truth=2.0*(1.1*(-1.1f64).exp()-0.9*(-0.9f64).exp());assert!((x[2].lo-truth).abs()<1e-14);assert!(x[2].hi.abs()<0.001);}
 #[test]fn both_pair_directions(){let a=ks(1.0,2.0,1.0,true,false);let b=ks(1.0,2.0,1.0,false,false);for j in 0..7{assert_eq!(a[j].lo,-b[j].hi);assert_eq!(a[j].hi,-b[j].lo);}}
 #[test]fn unresolved_empty_zero_mass(){assert!(Totals::zero().mean().is_none());}
 #[test]fn underflow_positive_upper(){let x=exp_negative(&exact(10000.0));assert_eq!(x.lo,0.0);assert!(x.hi>0.0);}
 #[test]fn species_conservation(){let x=ks(1.0,2.0,1.0,true,false);assert!(add(x[0],add(x[4],add(x[5],x[6]))).contains_zero());}
 #[test]fn fixture_thread_parity(){let taus:Vec<_>=[0.0,0.125,1.0,752.0].into_iter().map(exact).collect();let run=|n|rayon::ThreadPoolBuilder::new().num_threads(n).build().unwrap().install(||taus.par_iter().map(|q|exp_negative(q).as_pair().map(f64::to_bits)).collect::<Vec<_>>());assert_eq!(run(1),run(2));}
}
