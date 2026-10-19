//! Independent control axes; unmodified P6 kernel with full source/gas owners.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::KB_J_K,
    positive_spectral::SpectralMode,
    resolution_study::{PositiveStudyBridge, observer_moments},
};
fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().collect();
    if a.len() != 10 {
        return Err("args: id scenario nsteps cells angles birth opacity split shear_ratio".into());
    }
    let parse = |i: usize| a[i].parse::<usize>().map_err(|e| e.to_string());
    let (id, scenario) = (&a[1], &a[2]);
    let (n, cells, angles, birth, m, split) = (
        parse(3)?,
        parse(4)?,
        parse(5)?,
        parse(6)?,
        parse(7)?,
        parse(8)?,
    );
    let shear = a[9].parse::<f64>().map_err(|e| e.to_string())?;
    if n == 0
        || n > 256
        || split > 1
        || !["coupled", "transparent", "static"].contains(&scenario.as_str())
    {
        return Err("unsupported numerical study configuration".into());
    }
    let full = scenario == "coupled";
    let spectrum = if split == 1 {
        SpectralMode::SplitPositiveGauss3
    } else {
        SpectralMode::OriginalCellMean
    };
    let (base, ctr, conf, mut gas) = fixture(0.06, full, 0.2, spectrum, birth, m);
    let (h, duration) = if scenario == "transparent" {
        (2e-15, 1e14)
    } else {
        (1.2e-16, 8e10)
    };
    let geometry = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, shear * h).map_err(|e| format!("{e:?}"))?,
        [0., 1.5e14],
    )
    .map_err(|e| format!("{e:?}"))?;
    if scenario == "transparent" {
        let mut v = [0.; 13];
        v[S::H1Ionized as usize] = 1900.;
        v[S::He4DoublyIonized as usize] = 460.;
        v[S::DIonized as usize] = 30.;
        let ni = IsotopeNumberState::new(v).map_err(|e| format!("{e:?}"))?;
        gas.gas.nuclei = ni;
        gas.gas.thermal_j_m3 =
            1.5 * KB_J_K * ni.thermal_particle_density_all_thermal_m3().unwrap() * 10000.;
    }
    let bridge = PositiveStudyBridge::new(
        1900. / (21_f64.powi(3) * 1e6),
        0.2,
        cells,
        angles,
        geometry,
        ctr,
    )
    .map_err(|e| format!("construction: {e:?}"))?;
    if scenario == "static" {
        let r = bridge
            .frozen_spectrum(&gas.gas, &conf, duration)
            .map_err(|e| format!("{e:?}"))?;
        println!(
            "id,cells,split,survive,HI,HeI,HeII,DI,mean_E_eV,surv_E_eV,abs_E_eV,heat_eV,binding_eV"
        );
        println!(
            "{id},{cells},{split},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            r.surviving_fraction,
            r.events_per_injected_photon[0],
            r.events_per_injected_photon[1],
            r.events_per_injected_photon[2],
            r.events_per_injected_photon[3],
            r.injected_mean_energy_ev,
            r.surviving_energy_ev,
            r.absorbed_energy_ev,
            r.heat_ev,
            r.binding_ev
        );
        return Ok(());
    }
    let mut s = bridge
        .initial(gas, &conf, 0.)
        .map_err(|e| format!("{e:?}"))?;
    let mut events = [0.; 4];
    let (mut rr, mut cx, mut ff, mut cmb) = (0., 0., 0., 0.);
    let (mut maxn, mut maxe) = (0_f64, 0_f64);
    let (mut computed, mut reused, mut crossings) = (0usize, 0usize, 0usize);
    let start = std::time::Instant::now();
    for step in 0..n {
        let dt = duration / (n as f64);
        let vm = bridge
            .geometry()
            .snapshot(s.time_s + 0.5 * dt)
            .unwrap()
            .volume_factor()
            .unwrap();
        let (r, d) = bridge
            .advance(&s, &conf, dt)
            .map_err(|e| format!("{id} step{step}: {e:?}"))?;
        for (v, e) in events.iter_mut().zip(r.chemistry_budget.photo_events_m3) {
            *v += e * vm;
        }
        rr += r.chemistry_budget.rr_events_m3.iter().sum::<f64>() * vm;
        cx += r.chemistry_budget.cx_signed_m3.abs() * vm;
        ff += r.chemistry_budget.freefree_integrated_j_m3 * vm;
        cmb += r.chemistry_budget.cmb_change_j_m3.abs() * vm;
        computed += d.computed_paths;
        reused += d.reused_paths;
        crossings += d.threshold_crossings;
        let live: f64 = r.state.cohorts.iter().map(|q| q.n_comoving_m3).sum();
        let residual =
            (live + r.state.photon_absorbed_count_com3 - r.state.source_injected_count_com3).abs()
                / r.state.source_injected_count_com3;
        maxn = maxn.max(residual);
        maxe = maxe.max(r.global_energy_relative_error);
        s = r.state;
    }
    let elapsed = start.elapsed().as_secs_f64();
    let moment = observer_moments(&s, bridge.geometry()).map_err(|e| format!("{e:?}"))?;
    let q2 = moment.energy_p2_j_com3 / moment.energy_j_com3;
    if maxn >= 3e-10 || maxe >= 3e-10 {
        return Err("inherited conservation gate violated".into());
    }
    if full && !(rr > 0. && cx > 0. && ff > 0. && cmb > 0.) {
        return Err("requested full chemistry not active".into());
    }
    if scenario == "transparent" && events.iter().any(|e| *e != 0.) {
        return Err("transparent case absorbed".into());
    }
    println!(
        "id,scenario,nsteps,cells,angles,birth,opacity,split,shear_ratio,H_s,duration_s,full_chemistry,wall_s,T_K,HII_m3,HeII_m3,HeIII_m3,DII_m3,photons_com3,emitted_com3,absorbed_com3,HI,HeI,HeII,DI,photon_E_J,q2_E,mean_age_s,max_number_ledger,max_energy_ledger,cohorts,computed,reused,crossings,source_norm,RR_com3,CX_abs_com3,FF_J,CMB_abs_J"
    );
    println!(
        "{id},{scenario},{n},{cells},{angles},{birth},{m},{split},{shear:.17e},{h:.17e},{duration:.17e},{full},{elapsed:.9e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{q2:.17e},{:.17e},{maxn:.17e},{maxe:.17e},{},{computed},{reused},{crossings},{:.17e},{rr:.17e},{cx:.17e},{ff:.17e},{cmb:.17e}",
        s.full.gas.eos().unwrap().temperature_k,
        s.full.gas.nuclei.density_m3(S::H1Ionized),
        s.full.gas.nuclei.density_m3(S::He4SinglyIonized),
        s.full.gas.nuclei.density_m3(S::He4DoublyIonized),
        s.full.gas.nuclei.density_m3(S::DIonized),
        moment.photons_com3,
        s.source_injected_count_com3,
        s.photon_absorbed_count_com3,
        events[0],
        events[1],
        events[2],
        events[3],
        moment.energy_j_com3,
        moment.mean_age_s,
        s.cohorts.len(),
        bridge.source().normalization_relative_residual
    );
    let _ = base;
    Ok(())
}
