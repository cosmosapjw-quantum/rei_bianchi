//! P4/S4B independently measured variable-H manufactured photon-photo runs.
use rei_iso_couple_reference::HHeModel;
use rei_iso_couple_reference::affine_threshold_events::{
    AffineHubbleBackground, AffinePhotoControls, FrozenPhotoDensities, affine_photo_cohort,
    affine_threshold_cut_times,
};
use rei_iso_couple_reference::bianchi_i::GeometryBackground;
use rei_iso_couple_reference::deuterium_atomic::DAtomicProvider;
use rei_iso_couple_reference::source_age::Cohort;

fn main() {
    let tmax = 5e8;
    let bg =
        AffineHubbleBackground::new(0., [1., 1., 1.], [1e-12; 3], [-1e-21; 3], [0., tmax]).unwrap();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let d = DAtomicProvider::new(chi, 13.602134599702, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let gas = FrozenPhotoDensities {
        proper_reference_time_s: 0.,
        neutral_m3: [8000., 0., 0., 1600.],
    };
    println!(
        "birth_s,m,events_on,energy_birth_ev,photon_surv,HI_abs,DI_abs,abs_energy_ev,event_count,number_residual,event_energy_residual_j"
    );
    for birth in [0., 5e7] {
        let co = Cohort {
            birth_time_s: birth,
            birth_geometry: bg.snapshot(birth).unwrap(),
            energy_at_birth_ev: 13.604,
            direction_at_birth: [0., 0., 1.],
            n_comoving_m3: 1.,
            spectral_index: 0,
            angular_index: 0,
        };
        let cuts = affine_threshold_cut_times(&co, &bg, birth, tmax, d.chi_d_ev()).unwrap();
        eprintln!("birth={birth:.6e}; variable-H cut times = {cuts:?}");
        for m in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512] {
            for split in [false, true] {
                let p = affine_photo_cohort(
                    &co,
                    &bg,
                    d,
                    gas,
                    birth,
                    tmax,
                    AffinePhotoControls {
                        substeps: m,
                        split_events: split,
                    },
                )
                .unwrap();
                println!(
                    "{birth:.0},{m},{split},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{},{:.16e},{:.16e}",
                    co.energy_at_birth_ev,
                    p.survivor_count_com3,
                    p.absorbed_count_com3[0],
                    p.absorbed_count_com3[3],
                    p.absorbed_energy_j_com3 / rei_iso_couple_reference::full_network::EV_J,
                    p.event_cuts,
                    p.count_residual(),
                    p.event_energy_residual()
                );
            }
        }
    }
}
