//! Bounded manufactured, fixed-volume H/He4/D finite-bin physics campaign.
//! The photon spectrum and D-H threshold offset are intentionally invented fixtures;
//! NO actual reionization source, production/native solver or cosmological geometry.
use rei_iso_couple_reference::HHeModel;
use rei_iso_couple_reference::deuterium_atomic::DAtomicProvider;
use rei_iso_couple_reference::full_network::{FullState, NetworkConfig, PhotonBin, run_substeps};
use rei_iso_couple_reference::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use rei_iso_couple_reference::mixture_eos::{KB_J_K, MixtureState};
const SOURCE: &str = "MANUFACTURED_70EV_30EV_NO_EMISSIVITY";
const THRESHOLD: &str = "MANUFACTURED_D_H_OFFSET_0_0037_EV";
fn initial(he0: f64) -> FullState {
    let mut n = [0.0; 13];
    n[S::H1Neutral as usize] = 1000.0;
    n[S::H1Ionized as usize] = 900.0;
    n[S::DNeutral as usize] = 25.0;
    n[S::DIonized as usize] = 5.0;
    n[S::He4Neutral as usize] = he0;
    n[S::He4SinglyIonized as usize] = he0 / 3.0;
    n[S::He4DoublyIonized as usize] = he0 / 5.0;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let p = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5 * KB_J_K * p * 1e4,
        },
        photon_bins: vec![
            PhotonBin {
                energy_ev: 70.0,
                number_m3: 120.0,
            },
            PhotonBin {
                energy_ev: 30.0,
                number_m3: 70.0,
            },
        ],
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    }
}
fn config() -> NetworkConfig {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, THRESHOLD).unwrap(),
        SOURCE,
    )
}
fn main() {
    println!(
        "case,n_steps,total_s,nhp_m3,nhep_m3,nhepp_m3,ndp_m3,T_K,photons_m3,tau_event_m3,escaped_j_m3,cmb_reservoir_j_m3,freefree_integrated_j_m3,cx_m3,energy_rel_residual,baryon_rel_residual,photo_event_over_photon_loss,owner"
    );
    for case in [
        "baseline_no_helium",
        "helium_mixture",
        "no_source_photons",
        "no_cx",
        "no_cmb",
    ] {
        let he = if case == "baseline_no_helium" {
            0.0
        } else {
            300.0
        };
        let mut a = initial(he);
        let mut conf = config();
        if case == "no_source_photons" {
            a.photon_bins.clear();
        }
        if case == "no_cx" {
            conf.use_cx = false;
        }
        if case == "no_cmb" {
            conf.use_cmb = false;
        }
        for steps in [1, 2, 4, 8, 16, 32, 64, 128, 256] {
            let r = run_substeps(&a, &conf, 4e8, steps).unwrap();
            let final_e = r.state.energy_j_m3(&conf);
            let initial_e = a.energy_j_m3(&conf);
            let ec = (final_e - initial_e) / initial_e.abs().max(1e-50);
            let b0 = a.gas.eos().unwrap().baryons_m3;
            let b1 = r.state.gas.eos().unwrap().baryons_m3;
            let dn = a.photon_number() - r.state.photon_number();
            let ev = r.budget.photo_events_m3.iter().sum::<f64>();
            let frac = if dn > 0.0 { ev / dn } else { 1.0 };
            let n = &r.state.gas.nuclei;
            println!(
                "{case},{steps},{:.9e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},THERMAL_SUBSTEP",
                4e8,
                n.density_m3(S::H1Ionized),
                n.density_m3(S::He4SinglyIonized),
                n.density_m3(S::He4DoublyIonized),
                n.density_m3(S::DIonized),
                r.state.gas.eos().unwrap().temperature_k,
                r.state.photon_number(),
                ev,
                r.state.escaped_j_m3,
                r.state.cmb_reservoir_j_m3,
                r.budget.freefree_integrated_j_m3,
                r.budget.cx_signed_m3,
                ec,
                (b1 - b0) / b0,
                frac
            );
        }
    }
}
