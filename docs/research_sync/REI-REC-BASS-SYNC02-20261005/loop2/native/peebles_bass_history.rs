//! Bounded source-bound benchmark; not the full BASS application.
//! Usage: peebles_bass_history N [constant]
//! Execute only after the coordinator establishes LOOP1_SYNC.json.

#[path = "../../loop1/bass_clock/baseline_bass/_rustcore/src/microphysics/frame.rs"]
mod frame;
#[path = "../../loop1/bass_clock/baseline_bass/_rustcore/src/microphysics/visibility.rs"]
mod visibility;
#[path = "../../loop1/bass_clock/baseline_bass/_rustcore/src/microphysics/rei_visibility.rs"]
mod rei_visibility;
#[path = "../../loop1/bass_clock/bass/_rustcore/src/microphysics/visibility_clock.rs"]
mod visibility_clock;

use rei_peebles_reference::{ReferenceInput, collapsed_redshift_rhs, SOURCE_PROFILE};
use rei_microphysics::{HHeModel, HHeState};
use frame::MaterialFrame;
use rei_visibility::{ReiOpacityCell, integrate_rei_visibility};
use visibility::C_M_S;
use visibility_clock::{RayClockGrid, integrate_clock_visibility};

const Z_START: f64 = 1200.0;
const Z_END: f64 = 1000.0;
const H_REF: f64 = 5e-14;
const N_H_TODAY: f64 = 0.2;
const T_TODAY: f64 = 2.7255;
const X_INITIAL: f64 = 0.8;
const OBSERVER_TAIL: f64 = 0.2;

fn background(z: f64) -> (f64, f64, f64) {
    let w=1.0+z;
    (H_REF*(w/(1.0+Z_START)).powf(1.5),N_H_TODAY*w.powi(3),T_TODAY*w)
}
fn rhs(z: f64, x: f64) -> Result<f64,String> {
    let (h,n,t)=background(z);
    let input=ReferenceInput::from_si(t,t,n,h,x,0.0).map_err(|e|format!("input z={z} x={x}: {e:?}"))?;
    collapsed_redshift_rhs(input,z).map_err(|e|format!("source z={z} x={x}: {e:?}"))
}
fn rk4(z:f64,x:f64,dz:f64)->Result<f64,String> {
    let k1=rhs(z,x)?;
    let k2=rhs(z+dz/2.0,x+dz*k1/2.0)?;
    let k3=rhs(z+dz/2.0,x+dz*k2/2.0)?;
    let k4=rhs(z+dz,x+dz*k3)?;
    let next=x+dz*(k1+2.0*k2+2.0*k3+k4)/6.0;
    rhs(z+dz,next)?; // The accepted endpoint must satisfy the same source domain.
    Ok(next)
}
fn times(z:f64)->(f64,f64) {
    let log_ratio=((1.0+Z_START)/(1.0+z)).ln();
    let t=(2.0/(3.0*H_REF))*(1.5*log_ratio).exp_m1();
    let eta=(2.0*(1.0+Z_START)/H_REF)*(0.5*log_ratio).exp_m1();
    (t,eta)
}
fn vector(v:&[f64])->String {
    format!("[{}]",v.iter().map(|x|format!("{x:.17e}")).collect::<Vec<_>>().join(","))
}
fn run()->Result<(),String> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.is_empty()||args.len()>2 {return Err("usage: peebles_bass_history N [constant]".into());}
    let n=args[0].parse::<usize>().map_err(|_|"invalid N")?;
    if ![400,800,1600].contains(&n) {return Err("N outside preregistered 400/800/1600 grids".into());}
    let constant=match args.get(1).map(String::as_str) {None=>false,Some("constant")=>true,_=>return Err("unknown mode".into())};
    let mut z_edges=Vec::with_capacity(n+1);
    let mut x_edges=Vec::with_capacity(n+1);
    let mut time_edges=Vec::with_capacity(n+1);
    let mut eta_edges=Vec::with_capacity(n+1);
    let mut chi_edges=Vec::with_capacity(n+1);
    let mut midpoint_z=Vec::with_capacity(n);
    let mut midpoint_x=Vec::with_capacity(n);
    let mut midpoint_n_h=Vec::with_capacity(n);
    let mut models=Vec::with_capacity(n);
    let mut states=Vec::with_capacity(n);
    let dz=(Z_END-Z_START)/(n as f64);
    let mut x=X_INITIAL;
    for i in 0..=n {
        let z=if i==n {Z_END}else{Z_START+(i as f64)*dz};
        let (t,eta)=times(z);
        z_edges.push(z);x_edges.push(x);time_edges.push(t);eta_edges.push(eta);chi_edges.push(C_M_S*eta);
        if i==n {break;}
        let zm=z+dz/2.0;
        let xm=if constant {X_INITIAL}else{rk4(z,x,dz/2.0)?};
        let (_,nh,temperature)=background(zm);
        midpoint_z.push(zm);midpoint_x.push(xm);midpoint_n_h.push(nh);
        // HHe is a typed density carrier here. Its RHS is never evaluated.
        // The positive ideal-gas u only supplies the carrier's state validation;
        // it is not a REC binding-energy/thermal mapping or evolved heat ledger.
        let model=HHeModel {
            n_h_cm3:nh/1e6,n_he_cm3:0.0,c_cm_s:C_M_S*100.0,
            kb_erg_k:1.380649e-16,ev_erg:1.602176634e-12,
            threshold_ev:[0.0;3],photon_energy_ev:[0.0;3],
            sigma_cm2:[[0.0;3];3],alpha_cm3_s:[0.0;3],beta_cm3_s:[0.0;3],
        };
        let state=HHeState {fractions:[xm,0.0,0.0],
            u_erg_cm3:1.5*model.n_h_cm3*(1.0+xm)*model.kb_erg_k*temperature,
            photon_cm3:[0.0;3],escaped_erg_cm3:0.0};
        models.push(model);states.push(state);
        x=if constant {X_INITIAL}else{rk4(z,x,dz)?};
    }
    let a_effective:Vec<_>=time_edges.windows(2).zip(eta_edges.windows(2))
        .map(|(t,e)|(t[1]-t[0])/(e[1]-e[0])).collect();
    let frame=MaterialFrame::new([0.0;3]).map_err(|e|format!("{e:?}"))?;
    let cells:Vec<_>=models.iter().zip(&states).map(|(model,state)|ReiOpacityCell::HHe {
        model,state,frame,e_normal:[1.0,0.0,0.0]}).collect();
    let base=integrate_rei_visibility(&time_edges,&cells,OBSERVER_TAIL).map_err(|e|format!("{e:?}"))?;
    let normal=integrate_clock_visibility(RayClockGrid::NormalSeconds{edges_seconds:&time_edges},
        &base.interval_rates_s_inverse,OBSERVER_TAIL).map_err(|e|format!("{e:?}"))?;
    let eta=integrate_clock_visibility(RayClockGrid::ConformalSeconds{
        edges_seconds:&eta_edges,scale_factors:&a_effective},&base.interval_rates_s_inverse,
        OBSERVER_TAIL).map_err(|e|format!("{e:?}"))?;
    let chi=integrate_clock_visibility(RayClockGrid::ConformalLengthMeters{
        edges_meters:&chi_edges,scale_factors:&a_effective},&base.interval_rates_s_inverse,
        OBSERVER_TAIL).map_err(|e|format!("{e:?}"))?;
    if normal.visibility.optical_depth!=base.visibility.optical_depth
        ||normal.visibility.survival!=base.visibility.survival
        ||normal.visibility.interval_probability!=base.visibility.interval_probability {
        return Err("normal-clock adapter changed the existing BASS result".into());
    }
    let mut fields=vec!["\"ok\":true".into(),format!("\"n_intervals\":{n}"),
        format!("\"kind\":\"{}\"",if constant {"CONSTANT_X_ANALYTIC_FIXTURE"} else {"PEEBLES_EVOLUTION"}),
        format!("\"profile\":\"{SOURCE_PROFILE}\""),
        format!("\"observer_tail\":{OBSERVER_TAIL:.17e}"),
        "\"physical_admission\":false".into(),"\"rct_enabled\":false".into(),
        "\"opacity_sampling\":\"INDEPENDENT_HALF_RK4_MIDPOINT_STATE\"".into(),
        "\"full_bass_build\":false".into()];
    for (key,data) in [
        ("z_edges",&z_edges),("x_edges",&x_edges),("time_edges_seconds",&time_edges),
        ("eta_edges_seconds",&eta_edges),("chi_edges_meters",&chi_edges),
        ("a_effective",&a_effective),("midpoint_z",&midpoint_z),("midpoint_x",&midpoint_x),
        ("midpoint_nH_m3",&midpoint_n_h),("midpoint_ne_m3",&base.electron_density_m3),
        ("interval_rates_s_inverse",&base.interval_rates_s_inverse),
        ("optical_depth",&normal.visibility.optical_depth),("survival",&normal.visibility.survival),
        ("interval_probability",&normal.visibility.interval_probability),
        ("eta_optical_depth",&eta.visibility.optical_depth),("eta_survival",&eta.visibility.survival),
        ("eta_interval_probability",&eta.visibility.interval_probability),
        ("chi_optical_depth",&chi.visibility.optical_depth),("chi_survival",&chi.visibility.survival),
        ("chi_interval_probability",&chi.visibility.interval_probability),
    ] {fields.push(format!("\"{key}\":{}",vector(data)));}
    println!("{{{}}}",fields.join(","));
    Ok(())
}
fn main() {
    if let Err(error)=run() {eprintln!("{error}");std::process::exit(1);}
}
