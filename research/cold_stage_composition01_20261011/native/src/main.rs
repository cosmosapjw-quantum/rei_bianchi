use rei_microphysics::{
    axisym_coupled_derivative, cold_hii_rr, cold_stage_composition as cold, AxisymCoupledState,
    AxisymLocalSources, AxisymmetricPoint, IsotopeNumberState,
};
use std::io::{self, BufRead};
fn state(t: f64, nh: f64, nhe: f64, xe: f64) -> AxisymCoupledState {
    let mut n = [0.0; 13];
    n[1] = nh * (1.0 - xe);
    n[2] = nh * xe;
    n[10] = nhe;
    AxisymCoupledState {
        isotopes: IsotopeNumberState::new(n).unwrap(),
        thermal_energy_j_m3: 1.5 * cold_hii_rr::KB * t * (nh + nhe + nh * xe),
        photon_number_m3: 0.0,
        photon_energy_j_m3: 0.0,
        photon_delta_pressure_j_m3: 0.0,
    }
}
fn emit(label: &str, g: AxisymmetricPoint, s: &AxisymCoupledState, tg: f64, o: cold::Stage) {
    let d = o.derivative;
    let p = d.sources;
    println!("{{\"label\":\"{}\",\"a\":{:.17e},\"H\":{:.17e},\"u\":{:.17e},\"Tgamma\":{:.17e},\"T\":{:.17e},\"nh\":{:.17e},\"nhe\":{:.17e},\"xe\":{:.17e},\"particles\":{:.17e},\"HI\":{:.17e},\"HII\":{:.17e},\"r\":{:.17e},\"C\":{:.17e},\"q\":{:.17e},\"du\":{:.17e},\"dT\":{:.17e},\"dnHI\":{:.17e},\"dnHII\":{:.17e},\"dnHeI\":{:.17e},\"dne\":{:.17e},\"dparticles\":{:.17e},\"binding\":{:.17e},\"dbinding\":{:.17e},\"thermal_source\":{:.17e},\"internal\":{:.17e},\"escape\":{:.17e},\"external\":{:.17e},\"bath\":{:.17e},\"dnphoton\":{:.17e},\"duphoton\":{:.17e},\"species\":{:?},\"sources_species\":{:?}}}",
        label,g.mean_scale_factor,g.mean_hubble_per_s,s.thermal_energy_j_m3,tg,o.temperature_k,
        o.n_h_m3,o.n_he_m3,o.xe,o.particles_m3,s.isotopes.density_m3(rei_microphysics::IsotopeSpecies::H1Neutral),
        s.isotopes.density_m3(rei_microphysics::IsotopeSpecies::H1Ionized),o.recombinations_m3_s,o.cooling_w_m3,o.compton_w_m3,
        d.thermal_energy_j_m3_s,d.temperature_k_s,d.species_m3_s[1],d.species_m3_s[2],d.species_m3_s[10],d.electron_m3_s,
        d.thermal_particle_m3_s,o.binding_j_m3,o.binding_w_m3,p.thermal_power_j_m3_s,p.internal_power_j_m3_s,
        p.escape_power_j_m3_s,p.external_power_j_m3_s,o.cmb_bath_w_m3,d.photon_number_m3_s,d.photon_energy_j_m3_s,d.species_m3_s,p.species_m3_s);
}
fn near(a: f64, b: f64, scale: f64) {
    assert!((a - b).abs() <= 3e-12 * scale, "{a} {b}");
}
fn main() {
    let mut first = None;
    let mut attempts = 0;
    for (i, line) in io::stdin().lock().lines().enumerate() {
        let x: Vec<f64> = line
            .unwrap()
            .split_whitespace()
            .map(|s| s.parse().unwrap())
            .collect();
        assert_eq!(x.len(), 7);
        let g = AxisymmetricPoint::new(x[0], 0.0, x[1], 0.0).unwrap();
        let s = state(x[2], x[3], x[4], x[5]);
        attempts += 1;
        let o = cold::stage(0.0, g, &s, x[6]).unwrap();
        emit(&format!("endpoint_{i}"), g, &s, x[6], o);
        if first.is_none() {
            first = Some((g, s, x[6], o));
        }
    }
    assert_eq!(attempts, 4);
    let (g, s, tg, o) = first.unwrap();
    let t = o.temperature_k;
    let zero = AxisymLocalSources {
        species_m3_s: [0.0; 13],
        electron_m3_s: 0.0,
        photon_number_m3_s: 0.0,
        photon_power_j_m3_s: 0.0,
        thermal_power_j_m3_s: 0.0,
        internal_power_j_m3_s: 0.0,
        escape_power_j_m3_s: 0.0,
        external_power_j_m3_s: 0.0,
    };
    attempts += 1;
    let free = axisym_coupled_derivative(0.0, g, &s, cold_hii_rr::KB, |_, _| Ok(zero)).unwrap();
    near(
        free.thermal_energy_j_m3_s,
        -5.0 * g.mean_hubble_per_s * s.thermal_energy_j_m3,
        free.thermal_energy_j_m3_s.abs(),
    );
    near(
        free.temperature_k_s,
        -2.0 * g.mean_hubble_per_s * t,
        free.temperature_k_s.abs(),
    );
    for i in 0..13 {
        near(
            free.species_m3_s[i],
            -3.0 * g.mean_hubble_per_s
                * s.isotopes
                    .density_m3(rei_microphysics::IsotopeSpecies::ALL[i]),
            free.species_m3_s[i].abs(),
        );
    }
    attempts += 1;
    let h0 = AxisymmetricPoint::new(g.mean_scale_factor, 0.0, 0.0, 0.0).unwrap();
    let oh0 = cold::stage(0.0, h0, &s, tg).unwrap();
    emit("H0", h0, &s, tg, oh0);
    let mut rr = o.derivative.sources;
    rr.thermal_power_j_m3_s = -o.cooling_w_m3;
    rr.external_power_j_m3_s = 0.0;
    attempts += 1;
    let dr = axisym_coupled_derivative(0.0, g, &s, cold_hii_rr::KB, |_, _| Ok(rr)).unwrap();
    let mut cmb = zero;
    cmb.thermal_power_j_m3_s = o.compton_w_m3;
    cmb.external_power_j_m3_s = o.compton_w_m3;
    attempts += 1;
    let dc = axisym_coupled_derivative(0.0, g, &s, cold_hii_rr::KB, |_, _| Ok(cmb)).unwrap();
    near(
        o.derivative.temperature_k_s,
        dr.temperature_k_s + dc.temperature_k_s - free.temperature_k_s,
        dr.temperature_k_s.abs() + dc.temperature_k_s.abs() + free.temperature_k_s.abs(),
    );
    let sn = state(t, o.n_h_m3, o.n_he_m3, 0.0);
    attempts += 1;
    let on = cold::stage(0.0, g, &sn, tg).unwrap();
    assert_eq!(on.recombinations_m3_s, 0.0);
    assert_eq!(on.compton_w_m3, 0.0);
    emit("ne0", g, &sn, tg, on);
    attempts += 1;
    let eq = cold::stage(0.0, g, &s, t).unwrap();
    assert_eq!(eq.compton_w_m3, 0.0);
    emit("equal_bath", g, &s, t, eq);
    attempts += 1;
    let hot = cold::stage(0.0, g, &s, t / 2.0).unwrap();
    assert!(hot.compton_w_m3 < 0.0 && hot.cmb_bath_w_m3 > 0.0);
    emit("hot", g, &s, t / 2.0, hot);
    let sx = state(t, o.n_h_m3, o.n_he_m3, 2.0 * o.xe);
    attempts += 1;
    let ox = cold::stage(0.0, g, &sx, tg).unwrap();
    near(
        ox.recombinations_m3_s,
        4.0 * o.recombinations_m3_s,
        ox.recombinations_m3_s.abs(),
    );
    near(ox.compton_w_m3, 2.0 * o.compton_w_m3, ox.compton_w_m3.abs());
    emit("xe2", g, &sx, tg, ox);
    let mut he = s;
    let mut ns = [0.0; 13];
    ns[1] = o.n_h_m3;
    ns[11] = o.n_he_m3;
    he.isotopes = IsotopeNumberState::new(ns).unwrap();
    attempts += 1;
    assert!(cold::stage(0.0, g, &he, tg).is_err());
    let mut ph = s;
    ph.photon_number_m3 = 1.0;
    attempts += 1;
    assert!(cold::stage(0.0, g, &ph, tg).is_err());
    let shear =
        AxisymmetricPoint::new(g.mean_scale_factor, 0.0, g.mean_hubble_per_s, 1e-20).unwrap();
    attempts += 1;
    assert!(cold::stage(0.0, shear, &s, tg).is_err());
    let low = state(2.0, o.n_h_m3, o.n_he_m3, o.xe);
    attempts += 1;
    assert!(cold::stage(0.0, g, &low, tg).is_err());
    assert!(attempts <= 20);
    println!("{{\"controls\":\"PASS\",\"derivative_attempts\":{attempts},\"history_executions\":0,\"solver_steps\":0}}");
}
