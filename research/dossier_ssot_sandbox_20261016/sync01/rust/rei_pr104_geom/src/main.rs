use rei_pr104_geom::{FLRW_SAMPLES, RP01_SAMPLES, delta_ln_energy, p2_coefficient, parse_samples};
fn main() {
    let r = parse_samples(RP01_SAMPLES).expect("source-backed RP01 samples");
    let f = parse_samples(FLRW_SAMPLES).expect("source-backed FLRW samples");
    let a2 = p2_coefficient(r[0], r[2], 1024).unwrap();
    let a2_ref = p2_coefficient(r[0], r[2], 2048).unwrap();
    let eq = delta_ln_energy(r[0], r[2], 0.0).unwrap();
    let pole = delta_ln_energy(r[0], r[2], 1.0).unwrap();
    println!(
        "{{\"scope\":\"COLLISIONLESS_PR104_SAMPLED_GEOMETRY\",\"tau_segment\":{{\"rp01\":{:.17e},\"flrw\":{:.17e}}},\"delta_b\":{:.17e},\"delta_ln_energy_equator\":{:.17e},\"delta_ln_energy_pole\":{:.17e},\"a2_log_energy\":{:.17e},\"a2_1024_minus_2048\":{:.17e},\"ionizing_spectrum\":null,\"directional_intensity\":null,\"total_cmb_tau\":null}}",
        r[2].tau,
        f[2].tau,
        r[2].b - r[0].b,
        eq,
        pole,
        a2,
        a2 - a2_ref
    );
}
