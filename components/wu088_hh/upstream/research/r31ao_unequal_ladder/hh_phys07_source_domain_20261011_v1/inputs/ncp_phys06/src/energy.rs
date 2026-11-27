//! Exact-real lift of source leaves. Direct projection consumes existing Jets;
//! no FT03 callback, endpoint, BE point or root is invoked here.
use crate::*;
use hh_phys04_candidate::coupled_primary::Phys04DerivativeExport;
use std::sync::atomic::{AtomicUsize,Ordering};
static EXPORTS:AtomicUsize=AtomicUsize::new(0);
pub fn export_count()->usize{EXPORTS.load(Ordering::SeqCst)}
pub const CHI:[f64;3]=[13.598434599702,24.587389011,54.41776];
pub type Mat=[[Interval;4];4];
fn jconst(a:Interval)->R<Jet>{Jet::constant(a).map_err(|_|"Jet leaf")}
fn jsum(a:&Jet,b:&Jet)->R<Jet>{a.add(b).map_err(|_|"Jet sum")}
fn jmul(a:&Jet,b:&Jet)->R<Jet>{a.mul(b).map_err(|_|"Jet product")}
pub fn transform(f:f64)->R<(Mat,Mat)>{
 if !f.is_finite()||f<=0.0{return Err("fHe domain");}
 let z=point(0.)?;let o=point(1.)?;let beta=[point(CHI[0])?,mul(point(f)?,point(CHI[1])?)?,mul(point(f)?,add(point(CHI[1])?,point(CHI[2])?)?)?];
 let mut s=[[z;4];4];for i in 0..4{s[i][i]=o;}s[3][..3].copy_from_slice(&beta);let mut q=s;for i in 0..3{q[3][i]=neg(beta[i])?;}Ok((s,q))
}
pub fn project(jets:&[Jet;4],coeff:[Interval;4])->R<Jet>{let mut out=jconst(point(0.)?)?;for i in 0..4{out=jsum(&out,&jmul(&jconst(coeff[i])?,&jets[i])?)?;}Ok(out)}
pub fn matmul(a:&Mat,b:&Mat)->R<Mat>{let mut out=[[point(0.)?;4];4];for i in 0..4{for j in 0..4{for k in 0..4{out[i][j]=add(out[i][j],mul(a[i][k],b[k][j])?)?;}}}Ok(out)}
pub fn transform_c(c:[[f64;4];4],s:&Mat,q:&Mat)->R<Mat>{let mut ci=[[point(0.)?;4];4];for i in 0..4{for j in 0..4{ci[i][j]=point(c[i][j])?;}}matmul(&matmul(s,&ci)?,q)}
pub fn transform_box(x:[Interval;4],s:&Mat)->R<[Interval;4]>{let mut out=[point(0.)?;4];for i in 0..4{for j in 0..4{out[i]=add(out[i],mul(s[i][j],x[j])?)?;}}Ok(out)}
// Error-free TwoSum of moderate, finite binary64 energy leaves: exact E-chi
// equals rounded excess + low. E and chi are positive in this coefficient domain.
pub fn heat_epsilon(e:f64,chi:f64)->R<f64>{
 if !e.is_finite()||!(0.0..=1e6).contains(&e)||!chi.is_finite()||!(0.0..=1e6).contains(&chi){return Err("heat-leaf domain");}
 let b=-chi;let rounded=e+b;let v=rounded-e;let low=(e-(rounded-v))+(b-v);Ok(-low)
}
#[derive(Debug)]pub struct EnergyExport{
 pub ell_g:Jet,pub transformed:[Jet;4],pub s:Mat,pub q:Mat,
 pub j_norm:Jet,pub psi:Jet,pub epsilon:Vec<[f64;3]>,pub fhat:Interval,pub delta_f:Interval,
 pub coefficient_graph:&'static str,pub native_authority:bool,
}
pub fn export(existing:&Phys04DerivativeExport)->R<EnergyExport>{
 EXPORTS.fetch_add(1,Ordering::SeqCst);
 let f=existing.source_stage.f_he;let nh=existing.source_stage.n_h_cm3;
 if !nh.is_finite()||nh<=0.0||!existing.stored_n_he.is_finite()||existing.stored_n_he<=0.0||existing.stored_n_he.to_bits()!=(nh*f).to_bits()||!existing.dt.is_finite()||existing.dt<=0.0{return Err("source density/dt leaves");}
 if existing.photo_rates.len()!=existing.energy_leaves.len()||existing.denominators.len()!=existing.energy_leaves.len()||existing.photons.len()!=existing.energy_leaves.len(){return Err("energy layout");}
 if existing.denominators.iter().any(|x|x.value.lo<=0.0||valid(x.value).is_err()){return Err("positive photon denominator");}
 let(s,q)=transform(f)?;let ell_g=project(&existing.residual,s[3])?;
 let fhat=div(point(existing.stored_n_he)?,point(nh)?)?;let delta_f=sub(point(f)?,fhat)?;
 let helium=jsum(&jmul(&jconst(point(CHI[1])?)?,&existing.nonphoto[1])?,&jmul(&jconst(add(point(CHI[1])?,point(CHI[2])?)?)?,&existing.nonphoto[2])?)?;
 let j_norm=jmul(&jconst(delta_f)?,&helium)?;
 let mut psi=jconst(point(0.)?)?;let mut epsilon=Vec::new();
 for(j,e)in existing.energy_leaves.iter().enumerate(){let mut eps=[0.;3];for a in 0..3{eps[a]=heat_epsilon(*e,CHI[a])?;psi=jsum(&psi,&jmul(&existing.photo_rates[j][a],&jconst(point(eps[a])?)?)?)?;}epsilon.push(eps);}
 let projected:[R<Jet>;4]=std::array::from_fn(|i|project(&existing.residual,s[i]));let mut transformed:[Jet;4]=std::array::from_fn(|_|jconst(point(0.).unwrap()).unwrap());
 // Both state-coordinate derivative indices are pulled back by diag(Q,I3).
 let mut input=[[point(0.)?;7];7];for i in 0..7{input[i][i]=point(1.)?;}for i in 0..4{for j in 0..4{input[i][j]=q[i][j];}}
 for i in 0..4{let raw=projected[i].as_ref().map_err(|e|*e)?;transformed[i].value=raw.value;
  for a in 0..7{for j in 0..7{transformed[i].gradient[a]=add(transformed[i].gradient[a],mul(raw.gradient[j],input[j][a])?)?;}
   for b in 0..7{for j in 0..7{for k in 0..7{transformed[i].hessian[a][b]=add(transformed[i].hessian[a][b],mul(mul(raw.hessian[j][k],input[j][a])?,input[k][b])?)?;}}}
  }
 }
 Ok(EnergyExport{ell_g,transformed,s,q,j_norm,psi,epsilon,fhat,delta_f,coefficient_graph:"ell*G exact-real source leaves; Jnorm=(f-fhat)*He nonphoto; Psi=sum eliminated channel rates*epsilon; no kernel normalization change",native_authority:false})
}
