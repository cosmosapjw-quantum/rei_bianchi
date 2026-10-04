use rei_microphysics::{Ft03Model,Interval,StepControl,certified_ft03_trial,ft03_scaled};
fn main(){
 let m=Ft03Model::controlled().unwrap(); let radii=[1e-7,1e-7,1e-7,1e-5,1e-8,1e-8,1e-8];
 for factor in [1.0,0.5,0.25] {
  let mut s=m.initial_state();let init=s;
  let z=ft03_scaled(&m,&s);let mut b=std::array::from_fn(|i| {let c=Interval::point(z[i]).unwrap();let d=Interval::point(radii[i]).unwrap();Interval::new(c.sub(&d).unwrap().lo,c.add(&d).unwrap().hi).unwrap()});
  let mut absorbed=[0.0;3];let mut max_step:f64=0.0;
  for _ in 0..3 {
   let q=certified_ft03_trial(&m,&s,&b,1e9*factor,StepControl{max_iterations:200,residual_tolerance:2e-16}).unwrap();
   for k in 0..3 {let a=(0..3).map(|i|q.events.photo_per_cm3[i][k]).sum::<f64>();absorbed[k]+=a;max_step=max_step.max(((s.photon_cm3[k]-q.state.photon_cm3[k]-a)/s.photon_cm3[k]).abs());}
   s=q.state;b=q.next_box;
  }
  let r=(0..3).map(|k|((init.photon_cm3[k]-s.photon_cm3[k]-absorbed[k])/init.photon_cm3[k]).abs()).fold(0.0,f64::max);
  println!("factor={} target=2e-16 accepted=3 max_step={} end_budget={}",factor,max_step,r);
 }
}
