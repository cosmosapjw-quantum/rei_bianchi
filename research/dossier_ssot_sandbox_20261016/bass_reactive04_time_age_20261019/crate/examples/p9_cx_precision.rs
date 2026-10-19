//! Isolate the ORIGINAL inner CX tolerance at fixed outer gas-grid resolution.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    full_network::FullState, isotope_state::IsotopeSpecies as S, midpoint_gas,
    mixture_coupling::MixtureCxComponent, positive_spectral::SpectralMode,
};
fn vec(s: &FullState) -> Vec<u64> {
    let mut v = S::ALL
        .map(|sp| s.gas.nuclei.density_m3(sp).to_bits())
        .to_vec();
    v.extend([
        s.gas.thermal_j_m3.to_bits(),
        s.escaped_j_m3.to_bits(),
        s.cmb_reservoir_j_m3.to_bits(),
        s.elapsed_s.to_bits(),
    ]);
    v
}
fn main() {
    println!(
        "T0_K,nsteps,rtol,atol,inner_attempts,inner_rejects,rate_calls,T_K,DII_m3,energy_ledger,wall_s"
    );
    for temp in [1e4, 4e4] {
        for n in [8, 32, 128, 512] {
            for rt in [1e-8, 1e-10, 1e-12, 1e-14] {
                let (_, _, mut c, mut s) =
                    fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
                s.gas.thermal_j_m3 *= temp / 1e4;
                c.use_photo = false;
                c.cx_controls.max_attempts = 20_000;
                c.cx_controls.max_rate_calls = 2_500_000;
                c.cx_controls.rtol = rt;
                c.cx_controls.atol_normalized = rt * 1e-3;
                let h = if temp == 1e4 { 8e10 } else { 1e10 } / n as f64;
                let component = MixtureCxComponent::new(c.deuterium, c.owner);
                let (mut attempts, mut reject, mut calls) = (0usize, 0usize, 0usize);
                let start = std::time::Instant::now();
                let e0 = s.energy_j_m3(&c);
                for j in 0..n {
                    let before = s.clone();
                    let a = component
                        .advance_cx_only(s.gas, h / 2., c.cx_controls)
                        .unwrap();
                    s.gas = a.final_state;
                    let mut nc = c;
                    nc.use_cx = false;
                    s = midpoint_gas::step(&s, &nc, h).unwrap().state;
                    let b = component
                        .advance_cx_only(s.gas, h / 2., c.cx_controls)
                        .unwrap();
                    s.gas = b.final_state;
                    for q in [a.counts, b.counts] {
                        attempts += q.attempts;
                        reject += q.rejected_steps;
                        calls += q.rate_calls;
                    }
                    if j == 0 {
                        let oracle = midpoint_gas::step_strang(&before, &c, h).unwrap();
                        assert_eq!(vec(&oracle.state), vec(&s));
                    }
                }
                println!(
                    "{temp:.17e},{n},{rt:.17e},{:.17e},{attempts},{reject},{calls},{:.17e},{:.17e},{:.17e},{:.9e}",
                    c.cx_controls.atol_normalized,
                    s.gas.eos().unwrap().temperature_k,
                    s.gas.nuclei.density_m3(S::DIonized),
                    (s.energy_j_m3(&c) - e0).abs() / e0.abs(),
                    start.elapsed().as_secs_f64()
                );
            }
        }
    }
}
