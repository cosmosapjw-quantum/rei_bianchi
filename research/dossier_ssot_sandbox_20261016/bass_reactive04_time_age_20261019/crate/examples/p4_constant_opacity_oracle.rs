//! Independent native-source frozen-gas oracle for photon birth/opacity clock.
//! Real MD14/BB50k owner 48*8 weights and actual Verner & H-equality D fits;
//! density, geometry, chemistry are deliberately frozen. Zero photons at t=0.
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    axbi_sources::AxbiSource,
    deuterium_atomic::DAtomicProvider,
    full_network::SPEED_OF_LIGHT_M_S,
    positive_birth_clock::photon_slab,
};
#[derive(Clone, Copy)]
struct Channel {
    kappa: [f64; 4],
    injection: f64,
}
fn cells() -> Vec<Channel> {
    let src = AxbiSource::new(1900. / (21.0_f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let vol = (1. / 21.0_f64).powi(3);
    let emission = src.at_redshift(20.).unwrap().proper_photons_cm3_s * 1e6 * vol;
    let provider = AtomicProvider::reference();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let d = DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let neutral = [1000., 300., 100., 25.];
    let mut out = vec![];
    for spectral in &src.spectral_cells {
        let e = spectral.energy_ev;
        let sigmas = [
            provider.cross_section(Absorber::HI, e).unwrap() * 1e-4,
            provider.cross_section(Absorber::HeI, e).unwrap() * 1e-4,
            provider.cross_section(Absorber::HeII, e).unwrap() * 1e-4,
            d.cross_section_m2(e).unwrap(),
        ];
        let kappa = std::array::from_fn(|i| neutral[i] * sigmas[i] * SPEED_OF_LIGHT_M_S);
        for angular in &src.angular_cells {
            out.push(Channel {
                kappa,
                injection: emission * spectral.photon_fraction * angular.count_fraction,
            });
        }
    }
    out
}
fn main() {
    let groups = cells();
    assert_eq!(groups.len(), 384);
    let total_duration_s = 8e10;
    println!(
        "nsteps,old_survivor,new_survivor,exact_survivor,old_survivor_rel_error,new_survivor_rel_error,old_number_relative_residual,new_number_relative_residual"
    );
    let mut prior_old = 0.0;
    for nsteps in [2usize, 4, 8, 16, 32, 64, 128] {
        let dt = total_duration_s / nsteps as f64;
        let (mut old_survivor, mut new_survivor, mut exact_survivor) = (0., 0., 0.);
        let (mut old_absorbed, mut new_absorbed, mut source_total) = (0., 0., 0.);
        for cell in &groups {
            let kappa = cell.kappa.iter().sum::<f64>();
            let tot = photon_slab(kappa * total_duration_s).unwrap();
            exact_survivor += cell.injection * total_duration_s * tot.new_surviving;
            let step = photon_slab(kappa * dt).unwrap();
            let (mut o, mut n) = (0., 0.);
            for _ in 0..nsteps {
                let birth = cell.injection * dt;
                old_absorbed += o * step.old_absorbed + birth * step.old_absorbed;
                new_absorbed += n * step.old_absorbed + birth * step.new_absorbed;
                o = o * step.old_surviving + birth * step.old_surviving;
                n = n * step.old_surviving + birth * step.new_surviving;
            }
            old_survivor += o;
            new_survivor += n;
            source_total += cell.injection * total_duration_s;
        }
        let old_err = (old_survivor - exact_survivor).abs() / exact_survivor;
        let new_err = (new_survivor - exact_survivor).abs() / exact_survivor;
        let old_ledger = (old_survivor + old_absorbed - source_total).abs() / source_total;
        let new_ledger = (new_survivor + new_absorbed - source_total).abs() / source_total;
        assert!(old_ledger < 3e-14 && new_ledger < 3e-14);
        assert!(new_err < 5e-14, "new error={new_err}");
        assert!(
            old_err <= prior_old || nsteps == 2,
            "old should monotonically improve"
        );
        // Prior error should *decrease* with N; record it for the paper table.
        prior_old = old_err;
        println!(
            "{nsteps},{old_survivor:.16e},{new_survivor:.16e},{exact_survivor:.16e},{old_err:.16e},{new_err:.16e},{old_ledger:.16e},{new_ledger:.16e}"
        );
    }
}
