use rei_microphysics::{
    cold_hii_rr::{self, ComponentError},
    AtomicProvider, ForwardError, RawProcess, RecombinationCase,
};
use std::io::{self, BufRead};
fn main() {
    for t in [2.999, 1e9 + 1.0, f64::NAN, f64::INFINITY] {
        assert_eq!(
            cold_hii_rr::coefficients(t).unwrap_err(),
            ComponentError::TemperatureDomain
        );
    }
    for t in [3.0, 1e9] {
        assert!(cold_hii_rr::coefficients(t).is_ok());
    }
    for args in [
        (10.0, -1.0, 1.0, 0.1),
        (10.0, 1.0, -1.0, 0.1),
        (10.0, 1.0, 1.0, 1.1),
        (10.0, 0.0, 0.0, 0.0),
    ] {
        assert_eq!(
            cold_hii_rr::stage(args.0, args.1, args.2, args.3).unwrap_err(),
            ComponentError::DensityDomain
        );
    }
    for (nh, nhe, xe) in [(1.0, 0.1, 0.0), (0.0, 1.0, 0.5)] {
        let s = cold_hii_rr::stage(10.0, nh, nhe, xe).unwrap();
        assert_eq!(s.recombinations_m3_s, 0.0);
        assert_eq!(s.cooling_w_m3, 0.0);
        assert_eq!(s.d_escape_w_m3, 0.0);
        assert_eq!(s.d_temperature_k_s, 0.0);
    }
    for line in io::stdin().lock().lines() {
        let x: Vec<f64> = line
            .unwrap()
            .split_whitespace()
            .map(|s| s.parse().unwrap())
            .collect();
        assert_eq!(x.len(), 4);
        assert!(matches!(
            AtomicProvider::reference().raw_coefficient(RawProcess::K2, x[0], RecombinationCase::A),
            Err(ForwardError::InvalidInput("RAW_TEMPERATURE_DOMAIN"))
        ));
        let s = cold_hii_rr::stage(x[0], x[1], x[2], x[3]).unwrap();
        println!("{{\"alpha_m3_s\":{:.17e},\"cooling_j_m3_s\":{:.17e},\"r\":{:.17e},\"C\":{:.17e},\"dnHI\":{:.17e},\"dnHII\":{:.17e},\"dne\":{:.17e},\"duth\":{:.17e},\"dubinding\":{:.17e},\"duescape\":{:.17e},\"Tdot\":{:.17e},\"dHe\":0,\"raw_guard\":\"RAW_TEMPERATURE_DOMAIN\"}}", s.coefficients.alpha_m3_s,s.coefficients.cooling_j_m3_s,s.recombinations_m3_s,s.cooling_w_m3,s.dn_hi_m3_s,s.dn_hii_m3_s,s.dn_e_m3_s,s.d_thermal_w_m3,s.d_binding_w_m3,s.d_escape_w_m3,s.d_temperature_k_s);
    }
}
