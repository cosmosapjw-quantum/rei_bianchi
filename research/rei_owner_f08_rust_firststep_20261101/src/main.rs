//! Original-source REI F08 S0 first-step photon/HI physical consequence.
//! Native original REI atomic_provider.rs byte-copied from original historical Rust.
//! No chemistry or MPRK/SDIRK evolution: a frozen-HI, frozen-dt photon operator comparator.
#![allow(dead_code)]
use std::error::Error;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

#[derive(Clone, Copy, Debug)]
pub enum ForwardError { InvalidInput(&'static str) }
#[path="original_atomic_provider.rs"]
mod atomic_provider;
use atomic_provider::{Absorber,AtomicProvider};

const C: f64 = 29_979_245_800.0; // cm/s
const DT: f64 = 625_000_000.0; // original proper s
const E_BIRTH: f64 = 13.7; // original S0 monoenergetic birth eV
const CHI_H: f64 = 13.598434599702; // physical ionization potential eV
const N_INITIAL: f64 = 0.05; // original photon/H
const SOURCE_RATE: f64 = 5e-15; // original photon/H/s
const N_DIR: usize = 128;
#[derive(Clone, Debug)]
struct Ray { label:String,id:usize,q:[f64;3],h:[f64;3],nhi:f64,el:f64,eu:f64,gamma_original:f64 }
#[derive(Default)]
struct Totals { n_dir:usize, source: f64, leak:f64, a_c:f64,a_h:f64,q_c:f64,q_h:f64,
                mean_em:f64, mean_variance:f64, min_e:f64, max_e:f64 }
fn read_input(path: &Path) -> Result<Vec<Ray>, Box<dyn Error>> {
    let txt=std::fs::read_to_string(path)?;
    let mut lines=txt.lines();
    let header=lines.next().ok_or("missing source CSV header")?;
    if header!="branch,direction_id,qx,qy,qz,hx,hy,hz,nHI_cm3,e_lower_ev,e_upper_ev,owner_gamma_hi_per_s" {
        return Err("unexpected original source CSV schema".into())
    }
    let mut rows=Vec::new();
    for line in lines {
        let fs:Vec<&str>=line.split(',').collect();
        if fs.len()!=12 {return Err("original source row wrong length".into())}
        let v:Vec<f64>=fs[2..].iter().map(|s| s.parse::<f64>()).collect::<Result<_,_>>()?;
        if !["S0_BI","S0_FLRW"].contains(&fs[0]) { return Err("unknown original source label".into()) }
        let id=fs[1].parse::<usize>()?;
        let q=[v[0],v[1],v[2]];let h=[v[3],v[4],v[5]];
        if !v.iter().all(|x|x.is_finite()) || !(v[6]>0.0 && v[7]>0.0 && v[8]>v[7] && v[9]>0.0) ||
           (q.iter().map(|x|x*x).sum::<f64>()-1.0).abs()>1e-12 {return Err("unphysical original source row".into())}
        rows.push(Ray{label:fs[0].to_owned(),id,q,h,nhi:v[6],el:v[7],eu:v[8],gamma_original:v[9]});
    }
    if rows.len()!=2*N_DIR || rows[..N_DIR].iter().any(|r|r.label!="S0_BI") ||
      rows[N_DIR..].iter().any(|r|r.label!="S0_FLRW") ||
      rows.iter().enumerate().any(|(i,r)|r.id!=i%N_DIR) {return Err("original source has incomplete/unsorted 128x2 rays".into())}
    Ok(rows)
}
fn g(ray:&Ray)->f64 {
    ray.q.iter().zip(ray.h.iter()).map(|(&q,&h)|q*q*(-2.0*h*DT).exp()).sum::<f64>().sqrt()
}
fn frac_abs(nhi:f64, sig:f64)->f64 {
    let tau=C*DT*nhi*sig;
    tau/(1.0+tau)
}
fn eval_group<'a>(rows: impl Iterator<Item=&'a Ray>, provider: &AtomicProvider,
  out:&mut impl Write, label:&str)->Result<Totals,Box<dyn Error>> {
    let rays:Vec<&Ray>=rows.collect();
    if rays.len()!=N_DIR {return Err("incomplete original qhat grid".into())}
    let shapes:Vec<f64>=rays.iter().map(|r|(-r.h.iter().sum::<f64>()*DT).exp()/g(r).powi(3)).collect();
    let sum_shapes=shapes.iter().sum::<f64>();
    let mut t=Totals {min_e:f64::MAX, ..Totals::default()};
    for (r,sw) in rays.iter().zip(shapes.iter()) {
        let e=E_BIRTH*g(r);
        if !(r.el < e && e < r.eu && (r.eu-E_BIRTH).abs()<1e-11) {
            return Err("original first-step only-neighbour redshift contract failed".into())
        }
        let lower=(r.eu-e)/(r.eu-r.el);
        let upper=1.0-lower;
        let sig_l=provider.cross_section(Absorber::HI,r.el).map_err(|_|"original atomic provider low")?;
        let sig_u=provider.cross_section(Absorber::HI,r.eu).map_err(|_|"original atomic provider high")?;
        let sig_c=provider.cross_section(Absorber::HI,e).map_err(|_|"original atomic provider char")?;
        let n0=N_INITIAL/(N_DIR as f64);
        let ns=SOURCE_RATE*DT*sw/sum_shapes;
        let abs_l=frac_abs(r.nhi,sig_l);
        let abs_u=frac_abs(r.nhi,sig_u);
        let abs_c=frac_abs(r.nhi,sig_c);
        // New source photons are emitted at the ENDPOINT E_BIRTH and do not redshift in this step.
        let event_c=n0*abs_c+ns*abs_u;
        let event_h=n0*(lower*abs_l+upper*abs_u)+ns*abs_u;
        let heat_c=n0*abs_c*(e-CHI_H)+ns*abs_u*(E_BIRTH-CHI_H);
        let heat_h=n0*(lower*abs_l*(r.el-CHI_H)+upper*abs_u*(r.eu-CHI_H))
                   +ns*abs_u*(E_BIRTH-CHI_H);
        let var_e=(e-r.el)*(r.eu-e);
        let energy_hat=lower*r.el+upper*r.eu;
        if !(event_c>=0.0 && event_h>=0.0 && heat_c>=0.0 && heat_h>=0.0 &&
             (energy_hat-e).abs()<2e-13 && lower>=0.0 && upper>=0.0) {
            return Err("first-step photon conservation, physics or positivity failed".into())
        }
        let leak=n0*lower;
        writeln!(out,"{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                 label,r.id,r.nhi,e,lower,ns,leak,sig_c,lower*sig_l+upper*sig_u,
                 event_c,event_h,event_h-event_c,heat_c,heat_h,heat_h-heat_c,var_e,r.gamma_original)?;
        t.n_dir+=1; t.source+=ns;t.leak+=leak;t.a_c+=event_c;t.a_h+=event_h;
        t.q_c+=heat_c;t.q_h+=heat_h;t.mean_em+=e/(N_DIR as f64);
        t.mean_variance+=var_e/(N_DIR as f64);
        t.min_e=t.min_e.min(e);t.max_e=t.max_e.max(e);
    }
    if (t.source-SOURCE_RATE*DT).abs()>1e-18 {return Err("birth number sum not conserved".into())}
    Ok(t)
}
fn main()->Result<(),Box<dyn Error>>{
    let args:Vec<String>=std::env::args().collect();
    if args.len()!=4 {return Err("usage: rei_f08_firststep INPUT.csv RESULT.csv SUMMARY.json".into())}
    let rows=read_input(Path::new(&args[1]))?;
    let mut out=BufWriter::new(File::create(&args[2])?);
    writeln!(out,"branch,direction_id,nHI_cm3,exact_energy_ev,hat_lower_weight,source_birth_photon_per_H,hat_forbidden_photon_per_H,sigma_exact_cm2,sigma_hat_cm2,absorbed_characteristic_per_H,absorbed_hat_per_H,delta_absorption_hat_minus_characteristic_per_H,photoelectron_excess_characteristic_ev_per_H,photoelectron_excess_hat_ev_per_H,delta_excess_hat_minus_characteristic_ev_per_H,hat_energy_variance_ev2,original_full_coupled_gamma_HI_per_s")?;
    let owner=AtomicProvider::reference();
    let tb=eval_group(rows[..N_DIR].iter(),&owner,&mut out,"S0_BI")?;
    let tf=eval_group(rows[N_DIR..].iter(),&owner,&mut out,"S0_FLRW")?;
    out.flush()?;
    let mut js=BufWriter::new(File::create(&args[3])?);
    writeln!(js,"{{\n  \"schema\":\"REI_F08_ORIGINAL_RUST_ATOMIC_FIRST_STEP_HI_PHYSICAL_CONSEQUENCE_V1\",\n  \"source_model\":\"original 13.7eV S0 128 rays, frozen original HI, first-step original backward-Euler absorption\",\n  \"original_full_26event_replayed\":false,\n  \"production\":\"HOLD\",\n  \"canonical_delta\":0,\n  \"central_DAG\":\"28/88\",\n  \"accepted_F05_tick\":\"160/131072\",\n  \"branch_results\":[")?;
    for (i,(name,t)) in [("S0_BI",&tb),("S0_FLRW",&tf)].iter().enumerate() {
        writeln!(js,"    {{\"branch\":\"{}\",\"ray_count\":{},\"first_step_exact_energy_floor_ev\":{:.17e},\"first_step_exact_energy_ceiling_ev\":{:.17e},\"source_birth_in_step_per_H\":{:.17e},\"first_step_hat_forbidden_weight_before_absorption_per_H\":{:.17e},\"absorbed_characteristic_per_H\":{:.17e},\"absorbed_hat_per_H\":{:.17e},\"delta_absorbed_per_H\":{:.17e},\"relative_delta_absorption\":{:.17e},\"photoelectron_excess_characteristic_ev_per_H\":{:.17e},\"photoelectron_excess_hat_ev_per_H\":{:.17e},\"relative_delta_photoelectron_excess\":{:.17e},\"mean_hat_added_energy_variance_ev2\":{:.17e}}}{}",
                name,t.n_dir,t.min_e,t.max_e,t.source,t.leak,t.a_c,t.a_h,t.a_h-t.a_c,
                (t.a_h-t.a_c)/t.a_c,t.q_c,t.q_h,(t.q_h-t.q_c)/t.q_c,t.mean_variance,if i==0{","}else{""})?;
    }
    writeln!(js,"  ]\n}}")?;
    js.flush()?;
    Ok(())
}
#[cfg(test)]
mod tests {
use super::*;
#[test] fn original_verner_physical_threshold_and_positive(){
 let p=AtomicProvider::reference();
 assert_eq!(p.cross_section(Absorber::HI,13.5).unwrap(),0.0);
 assert!(p.cross_section(Absorber::HI,13.7).unwrap()>6e-18);
 assert!(p.cross_section(Absorber::HI,13.7).unwrap()<7e-18);
}
#[test] fn hat_two_moments_and_spurious_variance() {
 let (l,u,e):(f64,f64,f64)=(13.675,13.7,13.699913519022955);
 let lo=(u-e)/(u-l);let hi=1.0-lo;
 assert!((lo+hi-1.0).abs()<1e-14);
 assert!((lo*l+hi*u-e).abs()<1e-13);
 assert!(lo*(l-e)*(l-e)+hi*(u-e)*(u-e)>0.0);
}
#[test] fn radiation_absorption_monotone(){
 let p=AtomicProvider::reference();
 let sig=p.cross_section(Absorber::HI,13.7).unwrap();
 assert!(frac_abs(1e-5,sig)>0.0 && frac_abs(1e-5,sig)<1.0);
 assert!(frac_abs(1e-4,sig)>frac_abs(1e-5,sig));
}
}