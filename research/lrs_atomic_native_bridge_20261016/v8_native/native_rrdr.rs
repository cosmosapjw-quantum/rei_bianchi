//! Standalone RR/DR-only experiment linked to the frozen PR150 native crate.
//! X=ln(a/a0), gas energy and all radiation energies are erg per total H nucleus.
use rei_microphysics::HHeModel;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::igm_rates::igm_rates;
use rei_microphysics::igm_state::IgmGasState;
use std::env;

const A0: f64 = 1.0 / 21.0;
const Y: f64 = 0.2454 / (4.0 * (1.0 - 0.2454));
const LO: f64 = 10000.0;
const HI: f64 = 24000.0;
const ORDER: [usize; 8] = [0, 1, 2, 3, 3, 2, 1, 0];
const ION: [usize; 4] = [1, 3, 4, 3];
const PRODUCT: [usize; 4] = [0, 2, 3, 2];
const NAMES: [&str; 4] = ["RR_HII", "RR_HeII", "RR_HeIII", "DR_HeII"];

#[derive(Clone, Copy)]
struct State {
    s: [f64; 5], // HI, HII, HeI, HeII, HeIII, normalized to total H
    w: f64,
    events: [f64; 4],
    cooling: [f64; 4],
    binding_escape: [f64; 4],
    work: f64,
}
fn electron(s: &[f64; 5]) -> f64 { s[1] + s[3] + 2.0 * s[4] }
fn binding(s: &[f64; 5], chi: &[f64; 4]) -> f64 {
    chi[0]*s[1] + chi[1]*(s[3]+s[4]) + chi[2]*s[4]
}
fn temp(w: f64, s: &[f64; 5], kb: f64) -> f64 { w/(1.5*kb*(1.0+Y+electron(s))) }
fn pair(ion: f64, ne: f64, k: f64) -> f64 {
    if ion == 0.0 || ne == 0.0 || k == 0.0 { return 0.0; }
    let small = ion.min(ne);
    let large = ion.max(ne);
    let diff = large-small;
    if diff == 0.0 { return small*small*k/(1.0+small*k); }
    let u = -(-diff*k).exp_m1();
    (small*large*u/(diff+small*u)).max(0.0).min(small)
}
#[derive(Clone, Copy)]
struct Probe { s: [f64; 5], ev: [f64; 4], q: [f64; 4], b: [f64; 4], tmid: f64, w: f64, alpha: [f64; 4] }
fn probe(t: f64, before: [f64; 5], w_ad: f64, strength: f64, kb: f64, chi: &[f64; 4]) -> Result<Probe,String> {
    let r = igm_rates(t).map_err(|e| format!("igm_rates: {e:?}"))?;
    let alpha = [r.rr_cm3_s[0],r.rr_cm3_s[1],r.rr_cm3_s[2],r.dr_cm3_s];
    let cool = [r.rr_cooling_erg_cm3_s[0],r.rr_cooling_erg_cm3_s[1],r.rr_cooling_erg_cm3_s[2],r.dr_cooling_erg_cm3_s];
    let mut s=before; let mut ev=[0.0;4]; let mut q=[0.0;4]; let mut b=[0.0;4];
    for j in ORDER {
        if alpha[j] <= 0.0 { if cool[j] > 0.0 { return Err("cooling with zero rate".into()); } continue; }
        let a=pair(s[ION[j]],electron(&s),0.5*strength*alpha[j]);
        s[ION[j]]-=a; s[PRODUCT[j]]+=a; ev[j]+=a;
        q[j]+=a*cool[j]/alpha[j]; b[j]+=a*chi[j];
    }
    let qt: f64=q.iter().sum();
    let w=w_ad-qt;
    let wm=w_ad-0.5*qt;
    let nm=1.0+Y+0.5*(electron(&before)+electron(&s));
    if !(w>=0.0 && wm>0.0 && nm>0.0 && s.iter().all(|v|*v>=-1e-12)) { return Err("thermal/species domain".into()); }
    Ok(Probe{s,ev,q,b,tmid:wm/(1.5*kb*nm),w,alpha})
}
fn background(xend:f64)->Result<FlatFlrwBackground,String> {
    let h0=67.4e5/3.0856775814913673e24;
    let om=0.315; let orad=9.2e-5;
    FlatFlrwBackground::new(FlatFlrwConfig{
        h0_per_s:h0,omega_r:orad,omega_m:om,omega_b:0.0224/0.674_f64.powi(2),
        omega_lambda:1.0-om-orad,helium_mass_fraction:0.2454,tcmb0_k:2.7255,
        ln_a_min:A0.ln()-1e-12,ln_a_max:A0.ln()+xend+1e-12,
        parameter_source:"PR150 6ea2b1b4 fixed FLRW values".into(),
    }).map_err(|e|format!("FLRW: {e:?}"))
}
fn parse<T:std::str::FromStr>(s:&str,label:&str)->Result<T,String> { s.parse().map_err(|_|format!("bad {label}")) }
fn run()->Result<(),String> {
    let a:Vec<String>=env::args().collect();
    if a.len()!=5 { return Err("usage: native_rrdr STEPS XEND DENSITY_FACTOR T0".into()); }
    let n:usize=parse(&a[1],"steps")?; let xend:f64=parse(&a[2],"xend")?;
    let d:f64=parse(&a[3],"density")?; let t0:f64=parse(&a[4],"T0")?;
    if n==0 || n>50000 || !xend.is_finite() || xend<0.0 || !d.is_finite() || d<0.0 || !(LO..=HI).contains(&t0) { return Err("input domain".into()); }
    let bg=background(xend)?;
    let model=HHeModel::controlled_fixture();
    let kb=model.kb_erg_k;
    let chi=[model.threshold_ev[0]*model.ev_erg, model.threshold_ev[1]*model.ev_erg,
             model.threshold_ev[2]*model.ev_erg, model.threshold_ev[1]*model.ev_erg];
    let p0=bg.at_ln_a(A0.ln()).map_err(|e|format!("initial point: {e:?}"))?;
    let init=IgmGasState::from_temperature([0.075,0.12,0.03],d*p0.n_h_cm3,d*p0.n_he_cm3,t0)
        .map_err(|e|format!("initial EOS: {e:?}"))?;
    let mut st=State{s:[0.925,0.075,Y*0.85,Y*0.12,Y*0.03],w:init.w_erg_per_h,
        events:[0.0;4],cooling:[0.0;4],binding_escape:[0.0;4],work:0.0};
    let w0=st.w; let b0=binding(&st.s,&chi);
    let dx=xend/(n as f64);
    println!("step,X,a,H_s,nh_cm3,nhe_cm3,dtmid_s,Tbegin_K,Tmid_K,Tend_K,HI,HII,HeI,HeII,HeIII,e_per_H,ne_cm3,w_erg_per_H,work_step_erg_per_H,root_residual_K,exposure_RR_HII,exposure_RR_HeII,exposure_RR_HeIII,exposure_DR_HeII,exposure_HeII_sum,events_RR_HII,events_RR_HeII,events_RR_HeIII,events_DR_HeII,cooling_RR_HII,cooling_RR_HeII,cooling_RR_HeIII,cooling_DR_HeII,binding_RR_HII,binding_RR_HeII,binding_RR_HeIII,binding_DR_HeII,escape_RR_HII,escape_RR_HeII,escape_RR_HeIII,escape_DR_HeII,cum_work,cum_events_RR_HII,cum_events_RR_HeII,cum_events_RR_HeIII,cum_events_DR_HeII,cum_cooling_RR_HII,cum_cooling_RR_HeII,cum_cooling_RR_HeIII,cum_cooling_DR_HeII,cum_binding_RR_HII,cum_binding_RR_HeII,cum_binding_RR_HeIII,cum_binding_DR_HeII,energy_residual_erg_per_H,exposure_begin_RR_HII,exposure_begin_RR_HeII,exposure_begin_RR_HeIII,exposure_begin_DR_HeII,exposure_mid_RR_HII,exposure_mid_RR_HeII,exposure_mid_RR_HeIII,exposure_mid_DR_HeII,exposure_end_RR_HII,exposure_end_RR_HeII,exposure_end_RR_HeIII,exposure_end_DR_HeII,exposure_begin_HeII_sum,exposure_mid_HeII_sum,exposure_end_HeII_sum");
    for i in 0..n {
        let xm=(i as f64+0.5)*dx;
        let p=bg.at_ln_a(A0.ln()+xm).map_err(|e|format!("midpoint: {e:?}"))?;
        let strength=dx*d*p.n_h_cm3/p.hubble_per_s;
        let before=st.s; let e0=electron(&before); let tb=temp(st.w,&before,kb);
        let wad=st.w*(-dx).exp(); let work1=st.w-wad;
        let flo=LO-probe(LO,before,wad,strength,kb,&chi)?.tmid;
        let fhi=HI-probe(HI,before,wad,strength,kb,&chi)?.tmid;
        if flo*fhi>0.0 { return Err(format!("no midpoint root step {i}, endpoints {flo:e} {fhi:e}")); }
        let(mut lo,mut hi)=(LO,HI); let mut tmid=0.0;
        for _ in 0..75 { tmid=0.5*(lo+hi); let f=tmid-probe(tmid,before,wad,strength,kb,&chi)?.tmid;
            if f.abs()<=2e-10 || hi-lo<=2e-10 { break; }
            if f*flo>0.0 { lo=tmid; } else { hi=tmid; }
        }
        let pr=probe(tmid,before,wad,strength,kb,&chi)?;
        let residual=(tmid-pr.tmid).abs();
        if residual>3e-7 { return Err(format!("midpoint residual step {i}: {residual:e}")); }
        let wend=pr.w*(-dx).exp(); let work2=pr.w-wend;
        let work_step=work1+work2;
        st.s=pr.s; st.w=wend; st.work+=work_step;
        for j in 0..4 { st.events[j]+=pr.ev[j];st.cooling[j]+=pr.q[j];st.binding_escape[j]+=pr.b[j]; }
        let te=temp(st.w,&st.s,kb);
        if !(LO..=HI).contains(&te) { return Err(format!("Tend outside 10-24k step {i}: {te}")); }
        let de=e0-electron(&st.s);
        let evsum:f64=pr.ev.iter().sum();
        if (de-evsum).abs()>5e-12 || (st.s[0]+st.s[1]-1.0).abs()>5e-12 || (st.s[2]+st.s[3]+st.s[4]-Y).abs()>5e-12 { return Err(format!("species/electron ledger step {i}")); }
        let escaped:f64=st.cooling.iter().sum::<f64>()+st.binding_escape.iter().sum::<f64>();
        let er=w0+b0-st.w-binding(&st.s,&chi)-st.work-escaped;
        if er.abs()>5e-12*(w0+b0).abs() { return Err(format!("energy ledger step {i}: {er:e}")); }
        let ex=[strength*e0*pr.alpha[0],strength*e0*pr.alpha[1],strength*e0*pr.alpha[2],strength*e0*pr.alpha[3]];
        print!("{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",i+1,(i+1) as f64*dx,p.a,p.hubble_per_s,d*p.n_h_cm3,d*p.n_he_cm3,dx/p.hubble_per_s,tb,tmid,te);
        for v in st.s { print!(",{v:.17e}"); }
        print!(",{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",electron(&st.s),electron(&st.s)*d*p.n_h_cm3,st.w,work_step,residual);
        for v in ex { print!(",{v:.17e}"); }
        print!(",{:.17e}",ex[1]+ex[3]);
        for arr in [&pr.ev,&pr.q,&pr.b] { for v in arr { print!(",{v:.17e}"); } }
        for j in 0..4 { print!(",{:.17e}",pr.q[j]+pr.b[j]); }
        print!(",{:.17e}",st.work);
        for arr in [&st.events,&st.cooling,&st.binding_escape] { for v in arr { print!(",{v:.17e}"); } }
        print!(",{er:.17e}");
        let rbegin=igm_rates(tb).map_err(|e|format!("rate begin step {i}: {e:?}"))?;
        let rend=igm_rates(te).map_err(|e|format!("rate end step {i}: {e:?}"))?;
        let ab=[rbegin.rr_cm3_s[0],rbegin.rr_cm3_s[1],rbegin.rr_cm3_s[2],rbegin.dr_cm3_s];
        let ae=[rend.rr_cm3_s[0],rend.rr_cm3_s[1],rend.rr_cm3_s[2],rend.dr_cm3_s];
        let eb:[f64;4]=std::array::from_fn(|j|strength*e0*ab[j]);
        let em:[f64;4]=std::array::from_fn(|j|strength*0.5*(e0+electron(&st.s))*pr.alpha[j]);
        let ee:[f64;4]=std::array::from_fn(|j|strength*electron(&st.s)*ae[j]);
        for arr in [&eb,&em,&ee] { for v in arr { print!(",{v:.17e}"); } }
        println!(",{:.17e},{:.17e},{:.17e}",eb[1]+eb[3],em[1]+em[3],ee[1]+ee[3]);
    }
    eprintln!("OK steps={n} Xend={xend} D={d} T0={t0} final_T={} final_e={} channels={:?} photon_number=0 photon_energy=0",temp(st.w,&st.s,kb),electron(&st.s),NAMES);
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("FAIL {e}");std::process::exit(2)}}
