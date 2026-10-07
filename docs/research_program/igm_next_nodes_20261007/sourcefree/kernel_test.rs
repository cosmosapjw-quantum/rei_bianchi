#[path = "kernel.rs"] mod kernel;
#[test]
fn fixed_density_constant_alpha_isothermal_limit() {
 let mut previous=f64::INFINITY;
 for n in [256,512,1024] {
  let r=kernel::run(n);
  assert!(r.error<previous/1.7);
  assert!(r.temp_relative<1e-9);
  assert!(r.energy_relative<1e-10);
  assert!(r.recombination_defect<1e-10);
  if n==1024 { assert!(r.error/(1e-6+1e-3*r.exact)<=1.); }
  previous=r.error;
 }
}
