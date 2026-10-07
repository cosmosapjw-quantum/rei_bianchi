use rei_microphysics::{coupled_primary::PrimaryPacket,igm_state::IgmGasState,igm_step::*};
fn main() {
 let args:Vec<_>=std::env::args().collect(); let nodes:usize=args[1].parse().unwrap();let repeats:usize=args[2].parse().unwrap();
 let b=StepBackground{n_h:4e-4,n_he:3.16e-5,hubble:6e-17,tcmb:35.0};
 let g=IgmGasState::from_temperature([2e-4,0.0,0.0],b.n_h,b.n_he,30.0).unwrap();
 let packets:Vec<_>=(0..nodes).map(|j|PrimaryPacket{energy_ev:14.0+86.0*(j as f64+0.5)/nodes as f64,per_h:0.001/nodes as f64}).collect();
 let rates=vec![1e-14/nodes as f64;nodes];let masks=vec![[true;3];nodes];let mut checksum=0u64;let mut iters=0;
 for _ in 0..repeats {
  let r=implicit_step_with_source_masked(std::hint::black_box(&g),std::hint::black_box(&packets),std::hint::black_box(&rates),&masks,b,1e11,StepControl::default()).unwrap();
  checksum=checksum.wrapping_add(std::hint::black_box(r.gas.w_erg_per_h.to_bits()));iters+=r.iterations;
 }
 println!("nodes={nodes} repeats={repeats} iterations={iters} checksum={checksum}");
}
