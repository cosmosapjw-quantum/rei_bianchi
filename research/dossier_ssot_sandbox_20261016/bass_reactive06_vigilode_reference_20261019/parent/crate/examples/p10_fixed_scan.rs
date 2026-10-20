//! Fixed-interval diagnostic: only DII has a stringent absolute budget.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    adaptive_step::LocalTolerances,
    budget_native::{NativeBudgetControls, attempt},
    isotope_state::IsotopeSpecies as S,
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
fn main() {
    let (base, ctl, mut c, g) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.cx_controls.max_attempts = 20000;
    c.cx_controls.max_rate_calls = 2500000;
    let b = MidpointBridge(base, ctl, PoolLimits::default(), Centering::JointCxSplit);
    let s = b.initial(g, &c, 0.).unwrap();
    println!(
        "h_s,DII_atol,action,pairs,comparison,lo,hi,outer_max,inner_max,coarse_loose,fine_loose,coarse_tight,fine_tight,scale,decision"
    );
    for h in [1e9, 1e10] {
        for atol in [1e-5, 1e-7, 1e-9, 1e-11] {
            let mut t = LocalTolerances {
                rtol: 0.,
                nuclei_m3: [1e10; 13],
                gas_energy_j_m3: 1e10,
                photon_number_com3: 1e10,
                photon_energy_j_com3: 1e10,
                photo_events_com3: [1e10; 4],
                angular_p2_energy: 1e10,
            };
            t.nuclei_m3[S::DIonized as usize] = atol;
            let x = attempt(&b, &s, &c, h, &t, &NativeBudgetControls::default()).unwrap();
            let key = format!("nucleus_{}", S::DIonized as usize);
            for (j, cmp) in x.comparisons.iter().enumerate() {
                let q = cmp
                    .four
                    .each_ref()
                    .map(|a| a.iter().find(|x| x.key == key).unwrap().value);
                println!(
                    "{h:.17e},{atol:.17e},{:?},{},{j},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{atol:.17e},{:?}",
                    x.action,
                    x.pairs_evaluated,
                    cmp.loose.relative,
                    cmp.tight.relative,
                    cmp.report.outer_max,
                    cmp.report.inner_max,
                    q[0],
                    q[1],
                    q[2],
                    q[3],
                    cmp.report.decision
                );
            }
        }
    }
}
