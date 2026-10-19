//! One source-bound complete short history. Flush each accepted step for recovery.
#[path = "../tests/bass_common/mod.rs"]
mod bass_common;
use rei_iso_couple_reference::{
    bass_reactive::GeometryChoice,
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground},
    bound_adaptive::{events_comoving, photon_projection},
    isotope_state::IsotopeSpecies as S,
};
use std::{
    io::{self, Write},
    time::Instant,
};
fn main() {
    let a: Vec<_> = std::env::args().collect();
    assert_eq!(a.len(), 8, "case grid nsteps t0 duration split frozen");
    let case = &a[1];
    let grid = a[2].parse().unwrap();
    let n: usize = a[3].parse().unwrap();
    let t0: f64 = a[4].parse().unwrap();
    let dur: f64 = a[5].parse().unwrap();
    let split: bool = a[6].parse().unwrap();
    let frozen: bool = a[7].parse().unwrap();
    assert!(n > 0 && dur > 0.);
    let (mut b, c, g) = bass_common::fixture(case, grid, t0, split, 8192);
    if frozen {
        let p = b.0.geometry.snapshot(t0).unwrap();
        let mean = p.hubble_per_s.iter().sum::<f64>() / 3.;
        let shear = (p.hubble_per_s[2] - p.hubble_per_s[0]) / 3.;
        let aa = p.volume_factor().unwrap().cbrt();
        let bb = (p.scale_factors[2] / aa).ln() / 2.;
        b.0.geometry = GeometryChoice::constant(
            ConstantAxisymmetricBackground::new(
                t0,
                AxisymmetricPoint::new(aa, bb, mean, shear).unwrap(),
                [t0, t0 + dur],
            )
            .unwrap(),
        );
    }
    let mut state = b.initial(g, &c, t0).unwrap();
    let timer = Instant::now();
    let (mut max_n, mut max_e, mut max_w) = (0f64, 0f64, 0f64);
    let mut ev = [0.; 4];
    let (mut rr, mut cx, mut ff, mut cmb) = (0., 0., 0., 0.);
    let mut o = io::BufWriter::new(io::stdout().lock());
    writeln!(o,"case,grid,nsteps,t0,duration,split,frozen,step,time_s,T_K,DII_m3,photons_com3,absorbed_com3,HI,HeI,HeII,DI,source_count,source_energy,geom_work,q2,H_perp,H_parallel,volume,cohorts,maxN,maxE,maxW,RR,CX_abs,FF,CMB_abs,hits,misses,cache_size,wall_s").unwrap();
    for step in 1..=n {
        let next = if step == n {
            t0 + dur
        } else {
            t0 + dur * step as f64 / n as f64
        };
        let dt = next - state.time_s;
        let begin = state.time_s;
        let (s, d) = match b.advance_with_diagnostics(&state, &c, dt) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("FAILED_AT step={step} t={begin} {e:?}");
                std::process::exit(2);
            }
        };
        let v =
            b.0.geometry
                .snapshot(begin + 0.5 * dt)
                .unwrap()
                .volume_factor()
                .unwrap();
        for (i, x) in events_comoving(&b, &s, begin).unwrap().iter().enumerate() {
            ev[i] += x;
        }
        rr += s.chemistry_budget.rr_events_m3.iter().sum::<f64>() * v;
        cx += s.chemistry_budget.cx_signed_m3.abs() * v;
        ff += s.chemistry_budget.freefree_integrated_j_m3 * v;
        cmb += s.chemistry_budget.cmb_change_j_m3.abs() * v;
        max_e = max_e.max(s.global_energy_relative_error);
        let p = photon_projection(&b, &s.state).unwrap();
        max_n = max_n.max(
            ((p.count + s.state.photon_absorbed_count_com3 - s.state.source_injected_count_com3)
                / s.state.source_injected_count_com3)
                .abs(),
        );
        max_w = max_w.max(
            (d.photon_work_ledger_j_com3 - d.photon_work_independent_j_com3).abs()
                / s.state.source_injected_energy_j_com3,
        );
        state = s.state;
        let q = b.0.geometry.snapshot(state.time_s).unwrap();
        let (h, m, k) = b.0.geometry.cache_stats();
        writeln!(o,"{case},{grid},{n},{t0:.17e},{dur:.17e},{split},{frozen},{step},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{max_n:.17e},{max_e:.17e},{max_w:.17e},{rr:.17e},{cx:.17e},{ff:.17e},{cmb:.17e},{h},{m},{k},{:.9e}",state.time_s,state.full.gas.eos().unwrap().temperature_k,state.full.gas.nuclei.density_m3(S::DIonized),p.count,state.photon_absorbed_count_com3,ev[0],ev[1],ev[2],ev[3],state.source_injected_count_com3,state.source_injected_energy_j_com3,state.geometry_work_j_com3,p.q2_energy,q.hubble_per_s[0],q.hubble_per_s[2],q.volume_factor().unwrap(),state.cohorts.len(),timer.elapsed().as_secs_f64()).unwrap();
        o.flush().unwrap();
    }
    assert!(rr > 0. && cx > 0. && ff > 0. && cmb > 0.);
    assert!(max_n < 3e-10 && max_e < 3e-10);
}
