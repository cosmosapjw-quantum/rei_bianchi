//! Independent original MD14 spectral centroid and photon support gate.
//! The most redshifted photon from earliest emission at a0 gives a
//! conservative lower bound for all later source cohorts over this interval.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
fn main() {
 println!("q_ref,earliest_source_E_ev,min_exact_end_E_ev,UV_lower_edge_ev,n_spectral,n_angular");
 for q in [-0.005_f64,0.,0.005] {
   let mut c=DriverConfig::baseline();c.q_ref=q;c.end_zbar=19.998;c.background_panels=4096;
   let (d,s)=Driver::new(c).unwrap();
   let g0=d.background.point_at_scale(s.a).unwrap().geometry().unwrap();
   let g1=d.background.point_at_scale(1./20.998).unwrap().geometry().unwrap();
   let mut min_end=f64::INFINITY;
   let mut min_src=f64::INFINITY;
   for spec in &d.source.spectral_cells {
     min_src=min_src.min(spec.energy_ev);
     for ang in &d.source.angular_cells {
       let mu=ang.mu;let direction=[(1.-mu*mu).sqrt(),0.,mu];
       let packet=CovariantPhoton::from_local(&g0,spec.energy_ev,direction,1.).unwrap();
       min_end=min_end.min(packet.energy_at(&g1).unwrap());
     }
   }
   assert!(min_end>13.6);
   println!("{q:.6e},{min_src:.17e},{min_end:.17e},{:.17e},{},{}",13.6,
            d.source.spectral_cells.len(),d.source.angular_cells.len());
 }
}
