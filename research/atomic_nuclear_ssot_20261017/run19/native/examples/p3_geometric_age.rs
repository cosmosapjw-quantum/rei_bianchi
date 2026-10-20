//! Collisionless source-age quadrature using exact PR150 axbi_sources and bianchi_i.
//! This is a prescribed OFF-SHELL constant-H background, not Einstein closure.
use rei_iso_couple_reference::axbi_sources::AxbiSource;
use rei_iso_couple_reference::bianchi_i::{
    AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground,
};
use rei_iso_couple_reference::source_age::SourceAgeBridge;
fn main() {
    let h = 1.2e-16f64;
    let duration = 1.0e15;
    println!(
        "geometry,n_age,n_mu,n_spec_per_segment,photons_birth_com_m3,photons_today_com_m3,energy_com_j_m3,q2_energy,mean_E_observer_ev,source_norm_relative,tail_trunc_fraction,log_scale_end,signed_delta_b"
    );
    for (label, sh) in [
        ("flrw", 0.0),
        ("shear_plus", 0.08 * h),
        ("shear_minus", -0.08 * h),
    ] {
        for n_age in [8, 16, 32, 64, 128] {
            for n_mu in if n_age == 128 {
                vec![8, 16, 32]
            } else {
                vec![8]
            } {
                let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), 0.2, 16, n_mu).unwrap();
                let norm = src.normalization_relative_residual;
                let tail = src.omitted_blackbody_tail_photon_fraction;
                let geom = ConstantAxisymmetricBackground::new(
                    0.0,
                    AxisymmetricPoint::new(1.0 / 21.0, 0.0, h, sh).unwrap(),
                    [0.0, duration],
                )
                .unwrap();
                // No H/He/D chemistry in this transparent comparator. Accept any angular N.
                let b = SourceAgeBridge {
                    source: src,
                    geometry: geom,
                    spectral_groups_per_segment: [2, 3, 3],
                };
                let gend = b.geometry.snapshot(duration).unwrap();
                let mut photons = 0.0;
                let mut energy = 0.0;
                let mut p2 = 0.0;
                let mut emitted = 0.0;
                for j in 0..n_age {
                    let t = (j as f64 + 0.5) * duration / n_age as f64;
                    let v = b.source_births(t, duration / n_age as f64).unwrap();
                    for c in &v {
                        let n = c.n_comoving_m3;
                        let r = c.ray_at(&gend).unwrap();
                        let u = n * r.energy_ev;
                        photons += n;
                        energy += u;
                        let mu = r.direction[2];
                        p2 += u * 0.5 * (3.0 * mu * mu - 1.0);
                        emitted += n;
                    }
                }
                let ao = gend.volume_factor().unwrap().cbrt();
                println!(
                    "{label},{n_age},{n_mu},16,{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e}",
                    emitted,
                    photons,
                    energy * rei_iso_couple_reference::full_network::EV_J,
                    p2 / energy,
                    energy / photons,
                    norm,
                    tail,
                    (ao * 21.0).ln(),
                    sh * duration
                );
            }
        }
    }
}
