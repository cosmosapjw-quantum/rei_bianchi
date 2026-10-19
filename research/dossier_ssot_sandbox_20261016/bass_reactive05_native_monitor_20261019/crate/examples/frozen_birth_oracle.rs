//! Frozen t=0 original source and HHeD absorbers, no evolving gas or geometry.
//! Analytic constant-slab recurrence isolates birth integration from chemistry.
#[path = "../tests/bass_common/mod.rs"]
mod bass_common;
#[path = "../birth_oracle.rs"]
mod birth_oracle;
use birth_oracle::{exact_phi, gauss_phi};
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    full_network::{EV_J, SPEED_OF_LIGHT_M_S},
    isotope_state::IsotopeSpecies as S,
};
fn main() {
    let (bridge, conf, gas) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut input_file = std::env::args().nth(1).map(|name| {
        std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(name)
            .expect("new source witness path")
    });
    use std::io::Write;
    if let Some(f) = &mut input_file {
        writeln!(f, "energy_ev,total_birth_com3,k_HI,k_HeI,k_HeII,k_DI").unwrap();
    }
    let duration = 8e12;
    let births = bridge.0.source_births(0., duration).unwrap();
    let atom = AtomicProvider::reference();
    let binding = HHeModel::controlled_fixture().threshold_ev;
    let edges = [
        binding[0],
        binding[1],
        binding[2],
        conf.deuterium.chi_d_ev(),
    ];
    let species = [
        S::H1Neutral,
        S::He4Neutral,
        S::He4SinglyIonized,
        S::DNeutral,
    ];
    println!(
        "nsteps,birth_gl,duration_s,source_com3,exact_survivor,GL_survivor,relative_survivor_difference,exact_HI,exact_HeI,exact_HeII,exact_DI,GL_HI,GL_HeI,GL_HeII,GL_DI,tau_step_min,tau_step_max,birth_fraction_tau_above_10,number_ledger_rel,energy_ledger_rel"
    );
    for n in [16, 32, 64, 128] {
        for gl in [2, 4] {
            let mut source = 0.;
            let mut surv = [0.; 2];
            let mut events = [[0.; 4]; 2];
            let mut energy = 0.;
            let mut esurv = [0.; 2];
            let mut eabs = [0.; 2];
            let (mut tau_min, mut tau_max) = (f64::INFINITY, 0f64);
            let mut thick_birth = 0.;
            for co in &births {
                let e = co.energy_at_birth_ev;
                let b = co.n_comoving_m3;
                // Exactly the source-native opacity formula, with immutable public
                // provider methods. Rates are frozen at t0 and are not new fit data.
                let rates: [f64; 4] = std::array::from_fn(|j| {
                    let sigma = if j == 3 {
                        conf.deuterium.cross_section_m2(e).unwrap()
                    } else if e < edges[j] {
                        0.
                    } else {
                        atom.cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][j], e)
                            .unwrap()
                            * 1e-4
                    };
                    gas.gas.nuclei.density_m3(species[j]) * sigma * SPEED_OF_LIGHT_M_S
                });
                if n == 16
                    && gl == 2
                    && let Some(f) = &mut input_file
                {
                    writeln!(
                        f,
                        "{e:.17e},{b:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                        rates[0], rates[1], rates[2], rates[3]
                    )
                    .unwrap();
                }
                let k = rates.iter().sum::<f64>();
                let tau = k * duration / (n as f64);
                tau_min = tau_min.min(tau);
                tau_max = tau_max.max(tau);
                source += b;
                energy += b * e * EV_J;
                if tau > 10. {
                    thick_birth += b;
                }
                // After N identical steps starting with zero photons, GL/exact
                // survival ratio = Phi_GL(k*h)/Phi(k*h). No history loop needed.
                let ex = b * exact_phi(k * duration).unwrap();
                let approx = ex * gauss_phi(tau, gl).unwrap() / exact_phi(tau).unwrap();
                for (m, survivor) in [ex, approx].into_iter().enumerate() {
                    surv[m] += survivor;
                    esurv[m] += survivor * e * EV_J;
                    let absorb = b - survivor;
                    eabs[m] += absorb * e * EV_J;
                    if k > 0. {
                        for (j, r) in rates.iter().enumerate() {
                            events[m][j] += absorb * r / k;
                        }
                    }
                }
            }
            let nerr = (0..2)
                .map(|m| (surv[m] + events[m].iter().sum::<f64>() - source).abs() / source)
                .fold(0f64, f64::max);
            let eerr = (0..2)
                .map(|m| (esurv[m] + eabs[m] - energy).abs() / energy)
                .fold(0f64, f64::max);
            println!(
                "{n},{gl},{duration:.17e},{source:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{tau_min:.17e},{tau_max:.17e},{:.17e},{nerr:.17e},{eerr:.17e}",
                surv[0],
                surv[1],
                surv[1] / surv[0] - 1.,
                events[0][0],
                events[0][1],
                events[0][2],
                events[0][3],
                events[1][0],
                events[1][1],
                events[1][2],
                events[1][3],
                thick_birth / source
            );
        }
    }
    // Scalar quadrature witnesses, independent of the source model.
    eprintln!("tau,GL2,GL4,exact_phi");
    for tau in [0., 1e-4, 0.1, 1., 10., 40., 100., 300.] {
        eprintln!(
            "{tau:.17e},{:.17e},{:.17e},{:.17e}",
            gauss_phi(tau, 2).unwrap(),
            gauss_phi(tau, 4).unwrap(),
            exact_phi(tau).unwrap()
        );
    }
}
