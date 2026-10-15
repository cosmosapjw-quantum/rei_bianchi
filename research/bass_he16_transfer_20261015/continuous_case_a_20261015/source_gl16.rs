//! Independent source-birth integral over ln(a), no cumulative age subtraction.
//! Reuse original cold native AxbiSource rate and AxbiBackground H(a).
//! This crosschecks the separately coded midpoint source injection in A/B.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
const X:[f64;8]=[
 0.09501250983763744,0.2816035507792589,0.4580167776572274,
 0.6178762444026437,0.7554044083550030,0.8656312023878318,
 0.9445750230732326,0.9894009349916499];
const W:[f64;8]=[
 0.1894506104550685,0.1826034150449236,0.1691565193950025,
 0.1495959888165767,0.1246289712555339,0.0951585116824928,
 0.0622535239386479,0.0271524594117541];
fn main(){
 println!("q_ref,N_photons_per_H_GL16,U_eV_per_H_GL16,mean_source_E_eV,source_shape_norm_residual");
 for q in [-0.005_f64,0.,0.005]{
  let mut c=DriverConfig::baseline();
  c.q_ref=q;c.end_zbar=19.998;c.background_panels=4096;
  let (d,initial)=Driver::new(c).unwrap();
  let u0=initial.a.ln();let u1=(1.0_f64/20.998).ln();
  let m=(u0+u1)/2.;let h=(u1-u0)/2.;
  let mut total=0.0;
  for i in 0..8 {
   for sgn in [-1.,1.] {
     let u=m+sgn*h*X[i];
     let a=u.exp();
     let z=1.0/a-1.0;
     let src=d.source.at_redshift(z).unwrap().per_h_s;
     let point=d.background.point_at_scale(a).unwrap();
     total+=h*W[i]*(src/point.h_per_s);
   }
  }
  let mean=d.source.spectral_cells.iter().map(|x|x.photon_fraction*x.energy_ev).sum::<f64>();
  let f_sum=d.source.spectral_cells.iter().map(|x|x.photon_fraction).sum::<f64>();
  let q=d.source.angular_cells.iter().map(|x|x.count_fraction).sum::<f64>();
  assert!((f_sum-1.).abs()<1e-11 && (q-1.).abs()<1e-11);
  println!("{:.6e},{:.17e},{:.17e},{:.17e},{:.17e}",
       d.config.q_ref,total,total*mean,mean,d.source.normalization_relative_residual);
 }
}
