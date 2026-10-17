//! Pure diagnostic only. Never substitutes Savin source rates in the integrator.
use rei_iso_couple_reference::deuterium_charge_exchange::Savin2002;
fn main() {
    println!(
        "temperature_K,kf_Savin_m3_s,kr_Savin_m3_s,kf_over_kr_savin,expected_exp_minus_42p915_over_T,kr_DB_candidate_m3_s,relative_reverse_fit_difference"
    );
    for t in [
        2.7, 10.0, 100.0, 1000.0, 4500.0, 10_000.0, 30_000.0, 100_000.0, 200_000.0,
    ] {
        let r = Savin2002::rates(t).unwrap();
        let eq = (-42.915 / t).exp();
        let kr_db = r.forward_m3_s / eq;
        println!(
            "{t:.1},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e}",
            r.forward_m3_s,
            r.reverse_m3_s,
            r.forward_m3_s / r.reverse_m3_s,
            eq,
            kr_db,
            r.reverse_m3_s / kr_db - 1.0
        );
    }
}
