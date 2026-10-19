//! Native four-corner budget campaign. All physics is inherited, full chemistry ON.
//! Each process writes bounded, flushed raw comparisons and its accepted schedule.
#[path = "../tests/bass_common/mod.rs"]
mod bass_common;
use rei_iso_couple_reference::{
    bound_adaptive::{LocalTolerances, photon_projection},
    bound_budget::{BudgetTrial, NativeBudgetControls, attempt},
    budget_kernel::Action,
    isotope_state::IsotopeSpecies as S,
};
use std::{
    fs::{File, create_dir_all},
    io::{BufWriter, Write},
    path::Path,
    time::Instant,
};
struct Logs {
    trace: BufWriter<File>,
    raw: BufWriter<File>,
}
impl Logs {
    fn new(path: &str, case: &str) -> Self {
        create_dir_all(path).unwrap();
        let path = Path::new(path);
        let mut trace =
            BufWriter::new(File::create(path.join(format!("{case}_trace.csv"))).unwrap());
        let mut raw = BufWriter::new(File::create(path.join(format!("{case}_four.csv"))).unwrap());
        writeln!(
            trace,
            "trial,start_s,h_s,action,pairs,next_h_s,selected_cx,outer,inner,reason"
        )
        .unwrap();
        writeln!(raw,"trial,comparison,key,unit,scale,coarse_loose,fine_loose,coarse_tight,fine_tight,cx_loose,cx_tight,outer,inner,decision").unwrap();
        Self { trace, raw }
    }
    fn write(&mut self, n: usize, t: f64, h: f64, x: &BudgetTrial) {
        let (o, i) = x.comparisons.last().map_or((f64::NAN, f64::NAN), |q| {
            (q.report.outer_max, q.report.inner_max)
        });
        let cx = x
            .accepted
            .as_ref()
            .map_or(f64::NAN, |a| a.precision.relative);
        writeln!(
            self.trace,
            "{n},{t:.17e},{h:.17e},{:?},{},{:.17e},{cx:.17e},{o:.17e},{i:.17e},{:?}",
            x.action, x.pairs_evaluated, x.next_h_s, x.reason
        )
        .unwrap();
        for (j, c) in x.comparisons.iter().enumerate() {
            for r in &c.report.components {
                let s = x.scales.iter().find(|s| s.key == r.key).unwrap();
                let q = c
                    .four
                    .each_ref()
                    .map(|v| v.iter().find(|a| a.key == r.key).unwrap().value);
                writeln!(self.raw,"{n},{j},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:?}",r.key,s.unit,s.value,q[0],q[1],q[2],q[3],c.loose.relative,c.tight.relative,r.outer,r.inner,c.report.decision).unwrap();
            }
        }
        self.trace.flush().unwrap();
        self.raw.flush().unwrap();
    }
}
fn tolerances(profile: &str, value: f64) -> LocalTolerances {
    if profile == "standard" {
        LocalTolerances {
            rtol: value,
            ..Default::default()
        }
    } else {
        let mut t = LocalTolerances {
            rtol: 0.,
            nuclei_m3: [1e10; 13],
            gas_energy_j_m3: 1e10,
            photon_number_com3: 1e10,
            photon_energy_j_com3: 1e10,
            photo_events_com3: [1e10; 4],
            angular_p2_energy: 1e10,
        };
        t.nuclei_m3[S::DIonized as usize] = value;
        t
    }
}
fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(
        a.len(),
        8,
        "case profile tolerance beta duration initial_h output_dir"
    );
    let case = &a[1];
    let profile = &a[2];
    assert!(profile == "standard" || profile == "dii_only");
    let value: f64 = a[3].parse().unwrap();
    let beta: f64 = a[4].parse().unwrap();
    let end: f64 = a[5].parse().unwrap();
    let mut h: f64 = a[6].parse().unwrap();
    assert!(end > 0. && end <= 1.5e14 && h > 0.);
    let donor_case = std::env::var("BASS_CASE").unwrap_or_else(|_| "SIGNED_MINUS".into());
    let (b, mut c, g) = bass_common::fixture(&donor_case, 121, 0., false, 8192);
    c.cx_controls.max_attempts = 20000;
    c.cx_controls.max_rate_calls = 2500000;
    let mut state = b.initial(g, &c, 0.).unwrap();
    let tol = tolerances(profile, value);
    let controls = NativeBudgetControls {
        beta,
        ..Default::default()
    };
    let mut logs = Logs::new(&a[7], case);
    let mut ev = [0.; 4];
    let (mut accepted, mut rejected, mut trials, mut pairs, mut refinements) = (0, 0, 0, 0, 0);
    let (mut max_o, mut max_i, mut max_a, mut max_n, mut max_e) = (0f64, 0f64, 0f64, 0f64, 0f64);
    let (mut tight_min, mut tight_max) = (f64::INFINITY, 0f64);
    let mut status = "COMPLETE";
    let timer = Instant::now();
    while end - state.time_s > 16. * f64::EPSILON * end.max(1.) {
        if trials >= 256 || state.cohorts.len() > 160000 || timer.elapsed().as_secs_f64() > 35. {
            status = "RESOURCE_LIMIT";
            break;
        }
        h = h.min(end - state.time_s);
        if h < 1. {
            status = "STEP_FLOOR";
            break;
        }
        trials += 1;
        let t0 = state.time_s;
        let x = match attempt(&b, &state, &c, h, &tol, &controls) {
            Ok(x) => x,
            Err(e) => {
                eprintln!("FATAL {e:?}");
                status = "NATIVE_ERROR";
                break;
            }
        };
        logs.write(trials, t0, h, &x);
        pairs += x.pairs_evaluated;
        refinements += x.comparisons.len().saturating_sub(1);
        if x.reason.is_some() {
            status = "PHYSICAL_REJECTION";
            break;
        } // preserve partial attempt; no uncounted trial calls.
        if let Some(out) = x.accepted {
            let rr = &x.comparisons.last().unwrap().report;
            max_o = max_o.max(rr.outer_max);
            max_i = max_i.max(rr.inner_max);
            max_a = max_a
                .max(rr.outer_max / (1. - beta))
                .max(rr.inner_max / beta);
            for (v, w) in ev.iter_mut().zip(out.photo_events_com3) {
                *v += w;
            }
            tight_min = tight_min.min(out.precision.relative);
            tight_max = tight_max.max(out.precision.relative);
            max_e = max_e.max(out.max_energy_ledger);
            state = out.state;
            accepted += 1;
            let p = photon_projection(&b, &state).unwrap();
            let n = state.source_injected_count_com3;
            max_n =
                max_n.max((p.count + state.photon_absorbed_count_com3 - n).abs() / n.max(1e-100));
        } else if x.action == Action::RetrySmallerOuterInterval {
            rejected += 1;
        } else {
            status = if x.action == Action::StopInnerUnresolved {
                "INNER_UNRESOLVED"
            } else {
                "PAIR_WORK_LIMIT"
            };
            break;
        }
        h = x.next_h_s;
    }
    eprintln!("BASS_SNAPSHOT_CACHE {:?}", b.0.geometry.cache_stats());
    let p = photon_projection(&b, &state).unwrap();
    println!(
        "case,profile,tolerance,beta,end_s,reached_s,status,accepted,rejected,trials,pairs,native_macro_calls,inner_refinements,min_selected_cx,max_selected_cx,cohorts,T_K,DII_m3,photons_com3,HI,HeI,HeII,DI,max_outer,max_inner,max_allocated_ratio,max_photon_ledger,max_energy_ledger,wall_s"
    );
    println!(
        "{case},{profile},{value:.17e},{beta:.17e},{end:.17e},{:.17e},{status},{accepted},{rejected},{trials},{pairs},{},{refinements},{tight_min:.17e},{tight_max:.17e},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{max_o:.17e},{max_i:.17e},{max_a:.17e},{max_n:.17e},{max_e:.17e},{:.9e}",
        state.time_s,
        pairs * 3,
        state.cohorts.len(),
        state.full.gas.eos().unwrap().temperature_k,
        state.full.gas.nuclei.density_m3(S::DIonized),
        p.count,
        ev[0],
        ev[1],
        ev[2],
        ev[3],
        timer.elapsed().as_secs_f64()
    );
    if status != "COMPLETE" {
        std::process::exit(2);
    }
}
