#[path = "common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    birth_layers::graded_birth_nodes,
    full_network::SPEED_OF_LIGHT_M_S,
    isotope_state::IsotopeSpecies as S,
    retarded_transport::gauss_birth_nodes,
};
fn main() {
    let g = common::load("SIGNED_MINUS", 121);
    let dt = (g.point_at_x(0.7004).unwrap().time_s - g.point_at_x(0.7).unwrap().time_s) / 8.0;
    let (full, c, source) = common::fixture(&g, 0.7002);
    let sp = [
        S::H1Neutral,
        S::He4Neutral,
        S::He4SinglyIonized,
        S::DNeutral,
    ];
    let chi = HHeModel::controlled_fixture().threshold_ev;
    let chi = [chi[0], chi[1], chi[2], c.deuterium.chi_d_ev()];
    let provider = AtomicProvider::reference();
    let rates = |e: f64| {
        let mut k = [0.0; 4];
        for j in 0..4 {
            let sigma = if j == 3 {
                c.deuterium.cross_section_m2(e).unwrap()
            } else if e < chi[j] {
                0.0
            } else {
                provider
                    .cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][j], e)
                    .unwrap()
                    * 1e-4
            };
            k[j] = full.gas.nuclei.density_m3(sp[j]) * SPEED_OF_LIGHT_M_S * sigma;
        }
        k
    };
    let mut energies = source
        .spectral_cells
        .iter()
        .map(|s| s.energy_ev)
        .collect::<Vec<_>>();
    energies.extend([13.6, 24.59, 54.42, chi[3]]);
    let seed = energies
        .iter()
        .map(|e| rates(*e).iter().sum::<f64>() * dt)
        .fold(0.0_f64, f64::max);
    println!(
        "cell,energy_eV,fraction,dt_s,seed_tau,k_HI,k_HeI,k_HeII,k_DI,method,surv_frac,HI_frac,HeI_frac,HeII_frac,DI_frac,heat_eV_per_source_photon"
    );
    for (i, s) in source.spectral_cells.iter().enumerate() {
        let k = rates(s.energy_ev);
        let total = k.iter().sum::<f64>();
        for growth in [0.0, 1.0, 2.0, 1.5, 1.25] {
            let (method, pts) = if growth <= 1.0 {
                let n = if growth == 0.0 { 2 } else { 4 };
                (format!("uniform{n}"), gauss_birth_nodes(n).unwrap())
            } else {
                (
                    format!("graded{growth}"),
                    graded_birth_nodes(seed, growth, 128)
                        .unwrap()
                        .into_iter()
                        .map(|n| (n.remaining_fraction, n.weight))
                        .collect(),
                )
            };
            let sv = pts
                .iter()
                .map(|(v, w)| w * (-total * dt * v).exp())
                .sum::<f64>();
            let ab = pts
                .iter()
                .map(|(v, w)| w * (-(-total * dt * v).exp_m1()))
                .sum::<f64>();
            let mut events = [0.0; 4];
            if total > 0.0 {
                for j in 0..4 {
                    events[j] = s.photon_fraction * ab * k[j] / total;
                }
            }
            let heat = events
                .iter()
                .zip(chi)
                .map(|(v, ch)| v * (s.energy_ev - ch))
                .sum::<f64>();
            println!(
                "{i},{:.17e},{:.17e},{dt:.17e},{seed:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{method},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{heat:.17e}",
                s.energy_ev,
                s.photon_fraction,
                k[0],
                k[1],
                k[2],
                k[3],
                s.photon_fraction * sv,
                events[0],
                events[1],
                events[2],
                events[3]
            );
        }
    }
}
