//! Conditional outward arithmetic. Supplied whole-domain enclosure truth and C2
//! regularity remain premises. No value of these structs grants native authority.
use crate::*;
use crate::energy::Mat;
use std::sync::atomic::{AtomicUsize,Ordering};
static ROOT_ARITH:AtomicUsize=AtomicUsize::new(0);static LINEAR:AtomicUsize=AtomicUsize::new(0);
pub fn counts()->[usize;2]{[ROOT_ARITH.load(Ordering::SeqCst),LINEAR.load(Ordering::SeqCst)]}
#[derive(Clone,Debug,PartialEq,Eq)]pub struct Identity{
 pub source:String,pub abi:String,pub seed:String,pub family:String,pub start:u64,pub terminal:u64,pub density:u64,pub leaf_graph:String,pub initial_carry:String,
}
impl Identity{fn require(&self)->R<()>{if [&self.source,&self.abi,&self.seed,&self.family,&self.leaf_graph,&self.initial_carry].iter().any(|s|s.is_empty())||!f64::from_bits(self.start).is_finite()||!f64::from_bits(self.terminal).is_finite()||f64::from_bits(self.terminal)<=f64::from_bits(self.start)||!f64::from_bits(self.density).is_finite()||f64::from_bits(self.density)<=0.0{return Err("missing source/family/clock/density/carry");}Ok(())}}
#[derive(Clone,Debug)]pub enum Coverage{Whole{state:[Interval;4],theta:[Interval;2]},Point,BooleanClaim(bool)}
#[derive(Clone,Debug)]pub enum Regularity{ConditionalC2{open_domain_premise:String,branch_premise:String},BooleanClaim(bool)}
#[derive(Clone,Debug)]pub struct Domain{pub identity:Identity,pub theta:[Interval;2],pub x:[Interval;4],pub coverage:Coverage,pub regularity:Regularity,pub denominator_min:Interval,pub temperature:Interval,pub no_hat_guard_crossing:bool}
impl Domain{
 pub fn require(&self)->R<()>{self.identity.require()?;for x in self.x.iter().chain(self.theta.iter()).chain([&self.denominator_min,&self.temperature]){valid(*x)?;}
  if self.theta.iter().any(|x|x.lo>=x.hi){return Err("nondegenerate parameter rectangle required");}
  match &self.coverage{Coverage::Whole{state,theta} if state.iter().zip(self.x).all(|(a,b)|same(*a,b))&&theta.iter().zip(self.theta).all(|(a,b)|same(*a,b))=>(),_=>return Err("whole X times Theta coverage required")}
  match &self.regularity{Regularity::ConditionalC2{open_domain_premise,branch_premise} if !open_domain_premise.is_empty()&&!branch_premise.is_empty()=>(),_=>return Err("C2 premise required; boolean not proof")}
  if self.x[0].lo<=0.0||self.x[0].hi>=1.0||self.x[1].lo<=0.0||self.x[2].lo<=0.0||add(self.x[1],self.x[2])?.hi>=1.0||self.x[3].lo<=0.0||self.denominator_min.lo<=0.0||self.temperature.lo<35000.0||self.temperature.hi>60000.0||!self.no_hat_guard_crossing{return Err("physical/thermal/denominator/chart domain");}Ok(())
 }
 fn paired(&self,other:&Self)->R<()>{self.require()?;other.require()?;if self.identity!=other.identity||!self.theta.iter().zip(other.theta).all(|(a,b)|same(*a,b)){return Err("paired family/source/clock/Theta mismatch");}Ok(())}
}
#[derive(Clone,Debug)]pub struct FixedC{matrix:[[f64;4];4],identity:Identity,centre_jacobian_bits:[[u64;4];4]}
impl FixedC{
 // Approximate inverse is derived once from the supplied source-center Jacobian.
 // The supplied Jacobian/source provenance is conditional; not a trusted issuer.
 pub fn from_center(identity:&Identity,center_jacobian:[[f64;4];4])->R<Self>{identity.require()?;if center_jacobian.iter().flatten().any(|x|!x.is_finite()){return Err("center Jacobian finite");}
  let mut aug=[[0.;8];4];for i in 0..4{aug[i][..4].copy_from_slice(&center_jacobian[i]);aug[i][i+4]=1.;}
  for k in 0..4{let mut pivot=k;for i in k+1..4{if aug[i][k].abs()>aug[pivot][k].abs(){pivot=i;}}if aug[pivot][k]==0.0{return Err("singular center Jacobian");}aug.swap(k,pivot);let d=aug[k][k];for j in 0..8{aug[k][j]/=d;}for i in 0..4{if i!=k{let a=aug[i][k];for j in 0..8{aug[i][j]-=a*aug[k][j];}}}}
  let matrix=std::array::from_fn(|i|std::array::from_fn(|j|aug[i][j+4]));if matrix.iter().flatten().any(|x|!x.is_finite()){return Err("nonfinite preconditioner");}Ok(Self{matrix,identity:identity.clone(),centre_jacobian_bits:center_jacobian.map(|r|r.map(f64::to_bits))})
 }
 pub fn matrix(&self)->[[f64;4];4]{self.matrix}
 pub fn centre_bits(&self)->[[u64;4];4]{self.centre_jacobian_bits}
}
#[derive(Clone,Debug)]pub enum CChoice{Fixed(FixedC),VariableClaim}
#[derive(Clone,Debug)]pub struct Partials{pub ga:[Interval;4],pub gb:[Interval;4],pub gab:[Interval;4],pub gya:Mat,pub gyb:Mat,pub gyy:[Mat;4]}
#[derive(Clone,Debug)]pub struct UniformData{pub domain:Domain,pub center:[f64;4],pub radius:[f64;4],pub gc:[Interval;4],pub a:Mat,pub c:CChoice,pub partials:Partials}
#[derive(Clone,Debug)]pub struct RootBounds{domain:Domain,a:Mat,c:FixedC,partials:Partials,scales:[f64;4],b:Mat,beta:[Interval;4],image_radius:[Interval;4],margins:[Interval;4],q:Interval,native_authority:bool}
impl RootBounds{pub fn b(&self)->Mat{self.b}pub fn beta(&self)->[Interval;4]{self.beta}pub fn image_radius(&self)->[Interval;4]{self.image_radius}pub fn margins(&self)->[Interval;4]{self.margins}pub fn q(&self)->Interval{self.q}pub fn native_authority(&self)->bool{self.native_authority}}
fn zero()->R<Interval>{point(0.)}
fn matvec(a:&Mat,v:[Interval;4])->R<[Interval;4]>{let mut out=[zero()?;4];for i in 0..4{for j in 0..4{out[i]=add(out[i],mul(a[i][j],v[j])?)?;}}Ok(out)}
fn cmat(c:&FixedC)->R<Mat>{let mut out=[[zero()?;4];4];for i in 0..4{for j in 0..4{out[i][j]=point(c.matrix[i][j])?;}}Ok(out)}
fn defect(a:&Mat,c:&FixedC,scales:[f64;4])->R<(Mat,Interval)>{if scales.iter().any(|x|!x.is_finite()||*x<=0.){return Err("positive scales");}let ca=crate::energy::matmul(&cmat(c)?,a)?;let mut b=[[zero()?;4];4];let mut qhi=0_f64;for i in 0..4{let mut row=zero()?;for j in 0..4{let v=sub(point(if i==j{1.}else{0.})?,ca[i][j])?;b[i][j]=point(mag(v))?;row=add(row,mul(b[i][j],div(point(scales[j])?,point(scales[i])?)?)?)?;}qhi=qhi.max(row.hi);}let q=Interval{lo:0.,hi:qhi};if qhi>=1.{return Err("scaled contraction >=1");}Ok((b,q))}
pub fn root_arithmetic(data:&UniformData)->R<RootBounds>{ROOT_ARITH.fetch_add(1,Ordering::SeqCst);data.domain.require()?;let c=match &data.c{CChoice::Fixed(c)if c.identity==data.domain.identity=>c.clone(),_=>return Err("fixed source-bound C required")};for x in data.gc.iter().chain(data.a.iter().flatten()){valid(*x)?;}
 if data.center.iter().any(|x|!x.is_finite())||data.radius.iter().any(|x|!x.is_finite()||*x<=0.){return Err("positive finite radius/center");}
 for i in 0..4{let hull=sub(point(data.center[i])?,point(data.radius[i])?)?.lo;let high=add(point(data.center[i])?,point(data.radius[i])?)?.hi;if data.domain.x[i].lo>hull||data.domain.x[i].hi<high{return Err("state coverage does not enclose declared center+radius");}}
 let(b,q)=defect(&data.a,&c,data.radius)?;let cg=matvec(&cmat(&c)?,data.gc)?;let beta=cg.map(|x|Interval{lo:0.,hi:mag(x)});let br=matvec(&b,data.radius.map(|x|point(x).unwrap()))?;let mut image_radius=[zero()?;4];let mut margins=[zero()?;4];for i in 0..4{image_radius[i]=add(beta[i],br[i])?;margins[i]=sub(point(data.radius[i])?,image_radius[i])?;if margins[i].lo<=0.0{return Err("strict beta+Br<r failed");}}
 Ok(RootBounds{domain:data.domain.clone(),a:data.a,c,partials:data.partials.clone(),scales:data.radius,b,beta,image_radius,margins,q,native_authority:false})
}
#[derive(Clone,Debug)]pub struct LinearBounds{enclosure:[Interval;4],image:[Interval;4],q:Interval,native_authority:bool}
impl LinearBounds{pub fn enclosure(&self)->[Interval;4]{self.enclosure}pub fn image(&self)->[Interval;4]{self.image}pub fn q(&self)->Interval{self.q}pub fn native_authority(&self)->bool{self.native_authority}}
pub fn linear(root:&RootBounds,rhs:[Interval;4],candidate:[Interval;4])->R<LinearBounds>{LINEAR.fetch_add(1,Ordering::SeqCst);let(b,q)=defect(&root.a,&root.c,root.scales)?;let _=b;let ca=crate::energy::matmul(&cmat(&root.c)?,&root.a)?;let mut image=matvec(&cmat(&root.c)?,rhs)?;for i in 0..4{valid(candidate[i])?;for j in 0..4{image[i]=add(image[i],mul(sub(point(if i==j{1.}else{0.})?,ca[i][j])?,candidate[j])?)?;}if !(candidate[i].lo<image[i].lo&&image[i].hi<candidate[i].hi){return Err("strict linear image inclusion failed");}}Ok(LinearBounds{enclosure:candidate,image,q,native_authority:false})}
pub fn forcing(p:&Partials,u:[Interval;4],v:[Interval;4])->R<[Interval;4]>{let av=matvec(&p.gya,v)?;let bu=matvec(&p.gyb,u)?;let mut out=[zero()?;4];for i in 0..4{let hv=matvec(&p.gyy[i],v)?;let mut bil=zero()?;for j in 0..4{bil=add(bil,mul(u[j],hv[j])?)?;}out[i]=neg(add(add(add(p.gab[i],av[i])?,bu[i])?,bil)?)?;}Ok(out)}
#[derive(Clone,Debug)]pub struct MixedBounds{root:RootBounds,u:LinearBounds,v:LinearBounds,w:LinearBounds,forcing:[Interval;4]}
impl MixedBounds{pub fn u(&self)->&LinearBounds{&self.u}pub fn v(&self)->&LinearBounds{&self.v}pub fn w(&self)->&LinearBounds{&self.w}pub fn forcing(&self)->[Interval;4]{self.forcing}}
pub fn mixed(root:&RootBounds,candidates:[[Interval;4];3])->R<MixedBounds>{let p=&root.partials;let mut ga=[zero()?;4];let mut gb=[zero()?;4];for i in 0..4{ga[i]=neg(p.ga[i])?;gb[i]=neg(p.gb[i])?;}let u=linear(root,ga,candidates[0])?;let v=linear(root,gb,candidates[1])?;let f=forcing(p,u.enclosure,v.enclosure)?;let w=linear(root,f,candidates[2])?;Ok(MixedBounds{root:root.clone(),u,v,w,forcing:f})}
#[derive(Debug)]pub struct ConditionalFinite{pub enclosure:[Interval;4],pub native_authority:bool,pub scope:&'static str}
fn area(theta:[Interval;2])->R<Interval>{mul(sub(point(theta[0].hi)?,point(theta[0].lo)?)?,sub(point(theta[1].hi)?,point(theta[1].lo)?)?)}
pub fn finite(bound:&MixedBounds,requested:[Interval;2])->R<ConditionalFinite>{bound.root.domain.require()?;if !requested.iter().zip(bound.root.domain.theta).all(|(a,b)|same(*a,b)){return Err("whole rectangle coverage mismatch");}let a=area(requested)?;let mut enclosure=[zero()?;4];for i in 0..4{enclosure[i]=mul(a,bound.w.enclosure[i])?;}Ok(ConditionalFinite{enclosure,native_authority:false,scope:"conditional on supplied whole-domain source bounds; not physical I"})}
pub struct ObservablePartials{pub gradient:[Interval;4],pub hessian:Mat,pub explicit_ab:Interval,pub gas_a:[Interval;4],pub gas_b:[Interval;4]}
pub fn observable(bound:&MixedBounds,o:&ObservablePartials)->R<Interval>{let hv=matvec(&o.hessian,bound.v.enclosure)?;let mut out=o.explicit_ab;for i in 0..4{out=add(out,add(add(mul(o.gradient[i],bound.w.enclosure[i])?,mul(bound.u.enclosure[i],hv[i])?)?,add(mul(o.gas_a[i],bound.v.enclosure[i])?,mul(o.gas_b[i],bound.u.enclosure[i])?)?)?)?;}Ok(out)}
pub fn finite_observable(bound:&MixedBounds,o:&ObservablePartials,requested:[Interval;2])->R<Interval>{finite(bound,requested)?;mul(observable(bound,o)?,area(requested)?)}
#[derive(Debug)]pub struct PairedBounds{pub linear:LinearBounds,pub forcing:[Interval;4],pub rectangle:[Interval;4],pub native_authority:bool}
pub fn paired(two:&RootBounds,full:&MixedBounds,delta_a:Mat,delta_f:[Interval;4],candidate:[Interval;4],joint_subtraction_premise:&str)->R<PairedBounds>{two.domain.paired(&full.root.domain)?;if joint_subtraction_premise.is_empty(){return Err("joint same-parameter difference enclosure premise missing");}let prod=matvec(&delta_a,full.w.enclosure)?;let mut f=[zero()?;4];for i in 0..4{f[i]=sub(delta_f[i],prod[i])?;}let lin=linear(two,f,candidate)?;let a=area(two.domain.theta)?;let mut rectangle=[zero()?;4];for i in 0..4{rectangle[i]=mul(a,lin.enclosure[i])?;}Ok(PairedBounds{linear:lin,forcing:f,rectangle,native_authority:false})}
// Opaque and unissued. Generic validators have no conversion into this authority.
pub struct NativeUniformCertificate{_sealed:()}
pub fn request_native_certificate()->R<NativeUniformCertificate>{Err("native authorization null / trusted uniform producer absent")}
pub fn actual_physical_values()->[Option<[Interval;4]>;6]{[None;6]}
