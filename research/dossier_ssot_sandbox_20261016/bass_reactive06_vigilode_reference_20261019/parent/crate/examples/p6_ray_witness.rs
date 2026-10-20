//! Point values of exact original Killing map for an independent Python check.
#[path = "../tests/common/mod.rs"]
mod common;
use common::{fixture, pulse};
use rei_iso_couple_reference::{bianchi_i::GeometryBackground, positive_spectral::SpectralMode};
fn main() {
    println!("shear_ratio,t_s,sign_mask,Eb_eV,E_eV,nx_b,ny_b,nz_b,nx,ny,nz");
    for shear in [-0.8, 0., 0.06, 1.5] {
        let (base, _, _, _) = fixture(shear, false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
        for time in [0., 1e12, 1e14] {
            for sign in 0..8 {
                let mut c = pulse(&base, 65., 0.4, 0.01);
                c.direction_at_birth = [0.3, 0.4, (0.75f64).sqrt()];
                for i in 0..3 {
                    if sign & (1 << i) != 0 {
                        c.direction_at_birth[i] *= -1.;
                    }
                }
                let r = c.ray_at(&base.geometry.snapshot(time).unwrap()).unwrap();
                println!(
                    "{shear:.17e},{time:.17e},{sign},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                    c.energy_at_birth_ev,
                    r.energy_ev,
                    c.direction_at_birth[0],
                    c.direction_at_birth[1],
                    c.direction_at_birth[2],
                    r.direction[0],
                    r.direction[1],
                    r.direction[2]
                );
            }
        }
    }
}
