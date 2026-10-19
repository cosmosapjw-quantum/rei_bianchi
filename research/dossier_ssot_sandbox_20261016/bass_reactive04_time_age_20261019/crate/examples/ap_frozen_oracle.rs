//! Actual MD14/BB50k t0 source, native H/He/D opacities; gas and geometry frozen.
//! Independent N-step source/absorption recurrence, preserving species inventories.
#[path = "../tests/bass_common/mod.rs"]
mod bass_common;
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    fitted_birth::{frozen_inventory, phi, rule},
    full_network::{EV_J, SPEED_OF_LIGHT_M_S},
    isotope_state::IsotopeSpecies as S,
};
use std::{fs::OpenOptions, io::Write, path::Path};
fn new_file(root: &Path, name: &str) -> std::fs::File {
    OpenOptions::new()
        .create_new(true)
        .write(true)
        .open(root.join(name))
        .expect("new witness file")
}
fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(args.len(), 2, "supply new-output directory");
    let root = Path::new(&args[1]);
    let (bridge, conf, gas) = bass_common::fixture("SIGNED_MINUS", 121, 0.0, false, 8192);
    let duration = 8e12;
    let births = bridge.0.source_births(0.0, duration).unwrap();
    let atom = AtomicProvider::reference();
    let hhe = HHeModel::controlled_fixture().threshold_ev;
    let edges = [hhe[0], hhe[1], hhe[2], conf.deuterium.chi_d_ev()];
    let species = [
        S::H1Neutral,
        S::He4Neutral,
        S::He4SinglyIonized,
        S::DNeutral,
    ];
    let mut input = new_file(root, "AP_FROZEN_SOURCE_INPUTS.csv");
    writeln!(input, "energy_ev,total_birth_com3,k_HI,k_HeI,k_HeII,k_DI").unwrap();
    let mut source = Vec::new();
    for co in births {
        let e = co.energy_at_birth_ev;
        let rates: [f64; 4] = std::array::from_fn(|j| {
            let sigma = if j == 3 {
                conf.deuterium.cross_section_m2(e).unwrap()
            } else if e < edges[j] {
                0.0
            } else {
                atom.cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][j], e)
                    .unwrap()
                    * 1e-4
            };
            gas.gas.nuclei.density_m3(species[j]) * sigma * SPEED_OF_LIGHT_M_S
        });
        writeln!(
            input,
            "{e:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            co.n_comoving_m3, rates[0], rates[1], rates[2], rates[3]
        )
        .unwrap();
        source.push((e, co.n_comoving_m3, rates));
    }
    let mut output = new_file(root, "AP_FROZEN_FINAL.csv");
    writeln!(output,"nsteps,refinement,source_com3,exact_survivor,fitted_survivor,relative_bias,HI,HeI,HeII,DI,photon_ledger_rel,energy_ledger_rel,thermal_j_com3,chemical_j_com3,native_source_rows").unwrap();
    for n in [16, 32, 64, 128] {
        for r in [1, 2, 4, 8] {
            let (
                mut born,
                mut exact,
                mut fitted,
                mut thermal,
                mut chemical,
                mut esource,
                mut esurv,
            ) = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
            let mut events = [0.0; 4];
            for (energy, total, rates) in &source {
                let kappa: f64 = rates.iter().sum();
                born += total;
                exact += total * phi(kappa * duration).unwrap();
                esource += total * energy * EV_J;
                let mut survivor = 0.0;
                for _ in 0..n {
                    let out = frozen_inventory(
                        survivor,
                        total / n as f64,
                        *rates,
                        duration / n as f64,
                        r,
                    )
                    .unwrap();
                    for j in 0..4 {
                        assert!(out.species_absorbed[j] == 0.0 || *energy >= edges[j]);
                        events[j] += out.species_absorbed[j];
                        thermal += out.species_absorbed[j] * (energy - edges[j]) * EV_J;
                        chemical += out.species_absorbed[j] * edges[j] * EV_J;
                    }
                    survivor = out.survivor;
                }
                fitted += survivor;
                esurv += survivor * energy * EV_J;
            }
            let nerr = (fitted + events.iter().sum::<f64>() - born).abs() / born;
            let eerr = (esurv + thermal + chemical - esource).abs() / esource;
            writeln!(output,"{n},{r},{born:.17e},{exact:.17e},{fitted:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{nerr:.17e},{eerr:.17e},{thermal:.17e},{chemical:.17e},{}",fitted/exact-1.0,events[0],events[1],events[2],events[3],source.len()).unwrap();
        }
    }
    let mut scalar = new_file(root, "AP_SCALAR.csv");
    let mut nodes = new_file(root, "AP_RULE_NODES.csv");
    writeln!(
        scalar,
        "tau,refinement,nodes,mass,emitted_mean,phi,fitted_phi,age1,age2,age3,age4"
    )
    .unwrap();
    writeln!(nodes, "tau,refinement,index,age_fraction,emission_weight").unwrap();
    for tau in [
        0.0, 1e-12, 1e-6, 0.1, 1.0, 3.0, 20.0, 40.0, 93.0, 300.0, 1000.0, 1e6, 1e12,
    ] {
        for r in [1, 2, 4, 8, 16] {
            let qs = rule(tau, r).unwrap();
            let mut moments = [0.0; 5];
            let mut mass = 0.0;
            let mut mean = 0.0;
            for (i, (age, w)) in qs.iter().enumerate() {
                mass += w;
                mean += w * age;
                for (p, m) in moments.iter_mut().enumerate() {
                    *m += w * (-tau * age).exp() * age.powi(p as i32);
                }
                writeln!(nodes, "{tau:.17e},{r},{i},{age:.17e},{w:.17e}").unwrap();
            }
            writeln!(scalar,"{tau:.17e},{r},{},{mass:.17e},{mean:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",qs.len(),phi(tau).unwrap(),moments[0],moments[1]/moments[0],moments[2]/moments[0],moments[3]/moments[0],moments[4]/moments[0]).unwrap();
        }
    }
}
