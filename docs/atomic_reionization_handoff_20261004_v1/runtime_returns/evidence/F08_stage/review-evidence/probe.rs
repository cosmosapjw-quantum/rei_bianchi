extern crate rei_microphysics;
pub use rei_microphysics::*;
#[path="/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/coupled_primary.rs"]
mod coupled_primary;
use coupled_primary::*;
fn main() {
    let m=Ft03Model::controlled().unwrap();
    let s=m.initial_state();
    let stage=PrimaryStage{n_h_cm3:1e-4,f_he:0.083,h_mean_per_s:1e-14};
    let old=PrimaryState{fractions:s.fractions,w_ev_per_h:s.u_erg_cm3/(m.gas.n_h_cm3*m.gas.ev_erg),escape_ev_per_h:0.0,packets:vec![PrimaryPacket{energy_ev:13.7,per_h:0.05},PrimaryPacket{energy_ev:35.0,per_h:0.005},PrimaryPacket{energy_ev:70.0,per_h:0.001}]};
    let chi=[13.598434599702,24.587389011,54.41776];
    let energy=|v:&PrimaryState|v.w_ev_per_h+chi[0]*v.fractions[0]+stage.f_he*(chi[1]*v.fractions[1]+(chi[1]+chi[2])*v.fractions[2])+v.escape_ev_per_h+v.packets.iter().map(|p|p.energy_ev*p.per_h).sum::<f64>();
    let q=primary_stage_step(&stage,&old,1e9,StepControl{max_iterations:200,residual_tolerance:1e-4}).unwrap();
    let e0=energy(&old);let e1=energy(&q.state)+q.events.thermal_work_ev_per_h;
    println!("energy_probe accepted=true residual={:.17e} iterations={} relative_energy_error={:.17e} frozen_energy_limit=1e-12",q.residual,q.iterations,(e1-e0).abs()/e0);
    println!("identity nH_bits={:016x} stage_fhe_bits={:016x} stage_nhe_bits={:016x} old_model_nhe_bits={:016x}",stage.n_h_cm3.to_bits(),stage.f_he.to_bits(),(stage.n_h_cm3*stage.f_he).to_bits(),m.gas.n_he_cm3.to_bits());
    let provider=AtomicProvider::reference();
    for a in [Absorber::HI,Absorber::HeI,Absorber::HeII] {for p in &old.packets {println!("sigma {:?} E={} bits={:016x}",a,p.energy_ev,provider.cross_section(a,p.energy_ev).unwrap().to_bits());}}
    assert!((e1-e0).abs()/e0>1e-12,"the candidate did not reproduce the hypothesized energy violation");
}
