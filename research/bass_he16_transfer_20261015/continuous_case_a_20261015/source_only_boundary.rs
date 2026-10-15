//! Real original source + photon geometry transport only, NO gas absorption.
//! Demonstrates whether lower-energy numerical loss survives dt refinement.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::CharacteristicRay;
fn main(){
 println!("q_ref,substeps,source_total_per_H,boundary_loss_per_H,boundary_fraction,first_source_cell_lower_node_weight,first_bin_expected_fraction,photon_count_residual");
 for q in [-0.005_f64,0.,0.005]{
  let mut cfg=DriverConfig::baseline();
  cfg.q_ref=q;cfg.end_zbar=19.998;cfg.background_panels=4096;
  let (d,init)=Driver::new(cfg).unwrap();
  let s0=init.a;let sf=1./20.998;let delta=(sf/s0).ln();
  let gref=d.background.point_at_scale(s0).unwrap().geometry().unwrap();
  let spec=&d.source.spectral_cells[0];
  let w0=(d.energies[1]-spec.energy_ev)/(d.energies[1]-d.energies[0]);
  assert!(w0>0.&&w0<1.);
  for n in [1_usize,8,32,128,512]{
    let mut s=init.clone();
    s.photons.iter_mut().for_each(|x|*x=0.);
    s.ledgers.source_n=0.;s.ledgers.source_u=0.;
    for k in 1..=n {
      let a0=if k==1{s0}else{s0*(delta*((k-1) as f64)/(n as f64)).exp()};
      let a1=if k==n{sf}else{s0*(delta*(k as f64)/(n as f64)).exp()};
      let am=(a0*a1).sqrt();
      let dt=d.background.point_at_scale(a1).unwrap().time_s-
              d.background.point_at_scale(a0).unwrap().time_s;
      let gm=d.background.point_at_scale(am).unwrap().geometry().unwrap();
      d.geometry_map(&mut s,am).unwrap();
      let mut weights=Vec::new();
      for ang in &d.source.angular_cells {
        let ray=CharacteristicRay::new(1.,[(1.-ang.mu*ang.mu).sqrt(),0.,ang.mu],0.).unwrap();
        weights.push(ang.count_fraction*ray.solid_angle_jacobian(&gref,&gm).unwrap());
      }
      let sum=weights.iter().sum::<f64>();
      let rate=d.source.at_redshift(1./am-1.).unwrap().per_h_s;
      for (j,&w) in weights.iter().enumerate(){
        for e in &d.source.spectral_cells {
          let photons=rate*dt*e.photon_fraction*w/sum;
          let (bn,bu)=d.deposit(&mut s.photons,j,e.energy_ev,photons).unwrap();
          s.ledgers.source_n+=photons;
          s.ledgers.source_u+=photons*e.energy_ev;
          s.ledgers.boundary_n+=bn;s.ledgers.boundary_u+=bu;
        }
      }
      d.geometry_map(&mut s,a1).unwrap();
    }
    let surv=s.photons.iter().sum::<f64>();
    let residual=surv+s.ledgers.boundary_n-s.ledgers.source_n;
    assert!(residual.abs()<1e-12*s.ledgers.source_n);
    println!("{q:.6e},{n},{:.17e},{:.17e},{:.17e},{w0:.17e},{:.17e},{residual:.17e}",
        s.ledgers.source_n,s.ledgers.boundary_n,
        s.ledgers.boundary_n/s.ledgers.source_n,
        spec.photon_fraction*w0);
  }
 }
}
