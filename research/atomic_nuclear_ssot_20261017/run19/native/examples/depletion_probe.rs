//! Explicit photo-only finite-pool stress control, not cosmological input.
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    deuterium_atomic::DAtomicProvider,
    full_network::{self, FullState, NetworkConfig, PhotonBin},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
};
fn main() {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        "MANUFACTURED_DEPLETION_PULSE",
    );
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    let e = 20.;
    let k = full_network::SPEED_OF_LIGHT_M_S
        * AtomicProvider::reference()
            .cross_section(Absorber::HI, e)
            .unwrap()
        * 1e-4;
    println!("ratio,tau,steps,k_m3_s,dt_s,status,N_m3,A_m3,T_K");
    for ratio in [0.2, 1., 2.] {
        for tau in [0.1, 1., 2., 10.] {
            for steps in [1, 2, 4, 8, 16, 32, 64, 128] {
                let mut n = [0.; 13];
                n[S::H1Neutral as usize] = 100.;
                n[S::H1Ionized as usize] = 1.;
                let nuclei = IsotopeNumberState::new(n).unwrap();
                let gas = MixtureState {
                    nuclei,
                    thermal_j_m3: 1.5
                        * KB_J_K
                        * nuclei.thermal_particle_density_all_thermal_m3().unwrap()
                        * 1e4,
                };
                let s = FullState {
                    gas,
                    photon_bins: vec![PhotonBin {
                        energy_ev: e,
                        number_m3: 100. * ratio,
                    }],
                    escaped_j_m3: 0.,
                    cmb_reservoir_j_m3: 0.,
                    elapsed_s: 0.,
                };
                let dt = tau / (100. * k);
                match full_network::run_substeps(&s, &c, dt, steps) {
                    Ok(r) => println!(
                        "{ratio},{tau},{steps},{k:.17e},{dt:.17e},OK,{:.17e},{:.17e},{:.17e}",
                        r.state.photon_number(),
                        r.state.gas.nuclei.density_m3(S::H1Neutral),
                        r.state.gas.eos().unwrap().temperature_k
                    ),
                    Err(err) => {
                        println!("{ratio},{tau},{steps},{k:.17e},{dt:.17e},{err:?},nan,nan,nan")
                    }
                }
            }
        }
    }
}
