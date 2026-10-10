use rei_microphysics::{
    AtomicProvider, AxisymmetricPoint, ForwardError, IsotopeNumberState, RawProcess,
    RecombinationCase,
};
use std::io::{self, BufRead};

fn main() {
    // stdin: a, H_s1, Tm_K, nH_m3, nHe_m3, xe_per_H, kb_J_K.
    // Every input row is independently mapped using public production APIs.
    for line in io::stdin().lock().lines() {
        let line = line.expect("stdin");
        let x: Vec<f64> = line
            .split_whitespace()
            .map(|s| s.parse().expect("number"))
            .collect();
        assert_eq!(x.len(), 7);
        assert!(x.iter().all(|v| v.is_finite()));
        let (a, h, t, nh, nhe, xe, kb) = (x[0], x[1], x[2], x[3], x[4], x[5], x[6]);
        assert!(t > 0.0 && nh > 0.0 && nhe > 0.0 && (0.0..=1.0).contains(&xe));
        let mut species = [0.0; 13];
        species[1] = nh * (1.0 - xe);
        species[2] = nh * xe;
        species[10] = nhe;
        let state = IsotopeNumberState::new(species).expect("isotope intake");
        let moments = state.moments().expect("moments");
        let particles = nh + nhe + nh * xe;
        let u = 1.5 * kb * t * particles;
        let projection = state.try_legacy_hhe_projection().expect("projection");
        let eos = state.try_legacy_hhe_eos(u, kb).expect("eos");
        let geometry = AxisymmetricPoint::new(a, 0.0, h, 0.0)
            .expect("FLRW point")
            .snapshot()
            .expect("snapshot");
        let provider =
            AtomicProvider::reference().raw_coefficient(RawProcess::K2, t, RecombinationCase::A);
        assert!(matches!(
            provider,
            Err(ForwardError::InvalidInput("RAW_TEMPERATURE_DOMAIN"))
        ));
        // Unavailable coefficient has no numeric payload.
        print!("{{\"species_m3\":[");
        for (i, v) in species.iter().enumerate() {
            if i > 0 {
                print!(",");
            }
            print!("{v:.17e}");
        }
        println!("],\"baryons_m3\":{:.17e},\"heavy_m3\":{:.17e},\"ne_m3\":{:.17e},\"particles_m3\":{:.17e},\"u_J_m3\":{:.17e},\"nH_cm3\":{:.17e},\"nHe_cm3\":{:.17e},\"fractions\":[{:.17e},{:.17e},{:.17e}],\"u_erg_cm3\":{:.17e},\"Tm_roundtrip_K\":{:.17e},\"scale\":[{:.17e},{:.17e},{:.17e}],\"rate_s1\":[{:.17e},{:.17e},{:.17e}],\"provider\":{{\"status\":\"UNAVAILABLE\",\"error\":\"RAW_TEMPERATURE_DOMAIN\",\"process\":\"K2\",\"case\":\"A\"}}}}",
            moments.baryon_density_m3, moments.heavy_particle_density_m3, moments.neutral_free_electron_density_m3, eos.thermal_particle_density_m3, u, projection.n_h_cm3, projection.n_he_cm3, projection.fractions[0], projection.fractions[1], projection.fractions[2], eos.u_erg_cm3, eos.temperature_k, geometry.scale_factors[0], geometry.scale_factors[1], geometry.scale_factors[2], geometry.hubble_per_s[0], geometry.hubble_per_s[1], geometry.hubble_per_s[2]);
    }
}
