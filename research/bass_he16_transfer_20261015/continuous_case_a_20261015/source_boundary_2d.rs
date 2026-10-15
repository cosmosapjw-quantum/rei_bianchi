//! Frequency×time convergence control: original MD14 source plus original grid
//! geometry_map, NO atomic collision. Compare exact source-centroid geodesic
//! support; do not extrapolate discrete-centroid support to continuum SED.
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
use rei_microphysics::CharacteristicRay;

fn main() {
    println!("cells_per_segment,substeps,source_n_per_H,source_u_eV_per_H,boundary_n_per_H,boundary_u_eV_per_H,boundary_n_fraction,first_cell_photon_fraction,first_source_weight_on_lower_node,predicted_first_node_fraction,loss_excess_over_first_node,first_source_centroid_eV,min_exact_source_centroid_end_eV,native_lower_node_eV,photon_count_residual_per_H");
    for cells in [4_usize, 8, 16, 32, 64] {
        let mut cfg = DriverConfig::baseline();
        cfg.q_ref = 0.0;
        cfg.end_zbar = 19.998;
        cfg.background_panels = 4096;
        cfg.energy_subdivisions = cells;
        cfg.n_mu = 8;
        let (d, initial) = Driver::new(cfg).expect("native source config");
        let a0 = initial.a;
        let afinal = 1.0 / 20.998_f64;
        let span = (afinal / a0).ln();
        let g0 = d.background.point_at_scale(a0).unwrap().geometry().unwrap();
        let gf = d
            .background
            .point_at_scale(afinal)
            .unwrap()
            .geometry()
            .unwrap();
        let e0 = d.energies[0];
        let spec = &d.source.spectral_cells[0];
        let w0 = (d.energies[1] - spec.energy_ev) / (d.energies[1] - e0);
        assert!(w0 >= 0. && w0 <= 1.);
        let expected = spec.photon_fraction * w0;
        let mut emin = f64::INFINITY;
        for ang in &d.source.angular_cells {
            let mu = ang.mu;
            let dir = [(1. - mu * mu).sqrt(), 0., mu];
            for source in &d.source.spectral_cells {
                let ph = CovariantPhoton::from_local(&g0, source.energy_ev, dir, 1.).unwrap();
                emin = emin.min(ph.energy_at(&gf).unwrap());
            }
        }
        for nsteps in [1_usize, 8, 32, 128] {
            let mut state = initial.clone();
            state.photons.fill(0.);
            state.ledgers.source_n = 0.;
            state.ledgers.source_u = 0.;
            for k in 1..=nsteps {
                let ai = if k == 1 {
                    a0
                } else {
                    a0 * (span * ((k - 1) as f64) / (nsteps as f64)).exp()
                };
                let aj = if k == nsteps {
                    afinal
                } else {
                    a0 * (span * (k as f64) / (nsteps as f64)).exp()
                };
                let am = (ai * aj).sqrt();
                let dt = d.background.point_at_scale(aj).unwrap().time_s
                    - d.background.point_at_scale(ai).unwrap().time_s;
                let gm = d.background.point_at_scale(am).unwrap().geometry().unwrap();
                d.geometry_map(&mut state, am)
                    .expect("native geometry half");
                let weights = d
                    .source
                    .angular_cells
                    .iter()
                    .map(|cell| {
                        let mu = cell.mu;
                        let dir = [(1. - mu * mu).sqrt(), 0., mu];
                        let ray = CharacteristicRay::new(1., dir, 0.).unwrap();
                        cell.count_fraction * ray.solid_angle_jacobian(&g0, &gm).unwrap()
                    })
                    .collect::<Vec<_>>();
                let ws = weights.iter().sum::<f64>();
                let rate = d.source.at_redshift(1. / am - 1.).unwrap().per_h_s;
                for (ray, &w) in weights.iter().enumerate() {
                    for cell in &d.source.spectral_cells {
                        let count = rate * dt * cell.photon_fraction * w / ws;
                        let (bn, bu) = d
                            .deposit(&mut state.photons, ray, cell.energy_ev, count)
                            .unwrap();
                        state.ledgers.source_n += count;
                        state.ledgers.source_u += count * cell.energy_ev;
                        state.ledgers.boundary_n += bn;
                        state.ledgers.boundary_u += bu;
                    }
                }
                d.geometry_map(&mut state, aj)
                    .expect("native geometry second half");
            }
            let survivor = state.photons.iter().sum::<f64>();
            let res = state.ledgers.source_n - survivor - state.ledgers.boundary_n;
            assert!(res.abs() / (state.ledgers.source_n) < 2e-10);
            println!("{cells},{nsteps},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                state.ledgers.source_n,state.ledgers.source_u,state.ledgers.boundary_n,
                state.ledgers.boundary_u,state.ledgers.boundary_n/state.ledgers.source_n,
                spec.photon_fraction,w0,expected,
                state.ledgers.boundary_n/state.ledgers.source_n-expected,
                spec.energy_ev,emin,e0,res);
        }
    }
}
