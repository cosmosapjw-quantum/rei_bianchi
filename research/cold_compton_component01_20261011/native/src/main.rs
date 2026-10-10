use rei_microphysics::cold_compton::{self, Stage};
use std::io::{self, BufRead};
fn zeros(s: &Stage) {
    for v in [
        s.dn_hi_m3_s,
        s.dn_hii_m3_s,
        s.dn_hei_m3_s,
        s.dn_heii_m3_s,
        s.dn_heiii_m3_s,
        s.dn_e_m3_s,
        s.d_binding_w_m3,
    ] {
        assert_eq!(v, 0.0);
    }
}
fn main() {
    let equal = cold_compton::stage(50.0, 50.0, 1.0, 0.08, 0.001).unwrap();
    let no_e = cold_compton::stage(10.0, 50.0, 1.0, 0.08, 0.0).unwrap();
    for s in [equal, no_e] {
        zeros(&s);
        assert_eq!(s.d_temperature_k_s, 0.0);
        assert_eq!(s.d_gas_thermal_w_m3, 0.0);
        assert_eq!(s.d_cmb_bath_w_m3, 0.0);
    }
    let hot = cold_compton::stage(50.01, 50.0, 1.0, 0.08, 0.001).unwrap();
    zeros(&hot);
    assert!(hot.d_gas_thermal_w_m3 < 0.0 && hot.d_cmb_bath_w_m3 > 0.0);
    for line in io::stdin().lock().lines() {
        let x: Vec<f64> = line
            .unwrap()
            .split_whitespace()
            .map(|v| v.parse().unwrap())
            .collect();
        assert_eq!(x.len(), 6);
        let s = cold_compton::stage(x[0], x[1], x[2], x[3], x[4]).unwrap();
        zeros(&s);
        assert!(x[1] / x[0] - 1.0 >= 1e-10);
        let legacy = -2.0 * x[0]
            + cold_compton::A_K4_S * x[1] * x[1] * x[1] * x[1] * x[4] / (1.0 + x[4] + x[3] / x[2])
                * (x[1] - x[0])
                / x[5];
        let recovered = x[5] * legacy + 2.0 * x[5] * x[0];
        println!("{{\"Tdot\":{:.17e},\"du_gas\":{:.17e},\"du_CMBbath\":{:.17e},\"legacy_recovered\":{:.17e},\"dnHI\":0,\"dnHII\":0,\"dnHeI\":0,\"dnHeII\":0,\"dnHeIII\":0,\"dne\":0,\"dubinding\":0}}",s.d_temperature_k_s,s.d_gas_thermal_w_m3,s.d_cmb_bath_w_m3,recovered);
    }
}
