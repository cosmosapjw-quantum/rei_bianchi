//! One bounded adaptive history per process. Per-attempt trace is flushed.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    adaptive_step::{LocalTolerances, Trial, attempt, photon_projection},
    isotope_state::IsotopeSpecies as S,
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
use std::{
    fs::File,
    io::{BufWriter, Write},
    time::Instant,
};
fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(a.len(), 6, "rtol cx_rtol duration initial_h trace_path");
    let rtol: f64 = a[1].parse().unwrap();
    let cx: f64 = a[2].parse().unwrap();
    let end: f64 = a[3].parse().unwrap();
    let mut h: f64 = a[4].parse().unwrap();
    assert!(end > 0. && end <= 1.5e14 && h > 0.);
    let (base, ctl, mut c, g) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.cx_controls.rtol = cx;
    c.cx_controls.atol_normalized = cx * 1e-3;
    let b = MidpointBridge(base, ctl, PoolLimits::default(), Centering::JointCxSplit);
    let mut s = b.initial(g, &c, 0.).unwrap();
    let tol = LocalTolerances {
        rtol,
        ..LocalTolerances::default()
    };
    let mut log = BufWriter::new(File::create(&a[5]).unwrap());
    writeln!(
        log,
        "attempt,time_start_s,h_s,accepted,error_max,worst,reason,cohorts_after,HI,HeI,HeII,DI"
    )
    .unwrap();
    let mut events = [0.; 4];
    let (mut accepted, mut rejected, mut tries) = (0, 0, 0);
    let (mut max_n, mut max_e, mut max_a) = (0f64, 0f64, 0f64);
    let mut status = "COMPLETE";
    let start = Instant::now();
    while end - s.time_s > 16. * f64::EPSILON * end.max(1.) {
        if tries >= 1024 || s.cohorts.len() > 160000 || start.elapsed().as_secs_f64() > 35. {
            status = "RESOURCE_LIMIT";
            break;
        }
        h = h.min(end - s.time_s);
        if h < 1. {
            status = "STEP_FLOOR";
            break;
        }
        let t0 = s.time_s;
        tries += 1;
        match attempt(&b, &s, &c, h, &tol) {
            Ok(Trial::Accepted(out)) => {
                for (x, y) in events.iter_mut().zip(out.photo_events_com3) {
                    *x += y;
                }
                max_a = max_a.max(out.report.maximum);
                max_e = max_e.max(out.max_energy_ledger);
                s = out.state;
                accepted += 1;
                let p = photon_projection(&b, &s).unwrap();
                let denom = s.source_injected_count_com3.max(1e-100);
                max_n = max_n.max(
                    (p.count + s.photon_absorbed_count_com3 - s.source_injected_count_com3).abs()
                        / denom,
                );
                writeln!(log,"{tries},{t0:.17e},{h:.17e},true,{:.17e},{},NONE,{},{:.17e},{:.17e},{:.17e},{:.17e}",out.report.maximum,out.report.worst,s.cohorts.len(),events[0],events[1],events[2],events[3]).unwrap();
                h = out.next_h_s;
            }
            Ok(Trial::Rejected {
                report,
                reason,
                next_h_s,
            }) => {
                rejected += 1;
                let (err, worst) = report
                    .as_ref()
                    .map_or((f64::NAN, "PHYSICAL_REJECTION"), |r| {
                        (r.maximum, r.worst.as_str())
                    });
                writeln!(log,"{tries},{t0:.17e},{h:.17e},false,{err:.17e},{worst},{reason:?},{},{:.17e},{:.17e},{:.17e},{:.17e}",s.cohorts.len(),events[0],events[1],events[2],events[3]).unwrap();
                h = next_h_s;
            }
            Err(e) => {
                writeln!(
                    log,
                    "{tries},{t0:.17e},{h:.17e},false,NaN,FATAL,{e:?},{},0,0,0,0",
                    s.cohorts.len()
                )
                .unwrap();
                status = "FATAL_KERNEL_ERROR";
                break;
            }
        }
        log.flush().unwrap();
    }
    log.flush().unwrap();
    let p = photon_projection(&b, &s).unwrap();
    println!(
        "status,rtol,cx_rtol,end_requested_s,time_reached_s,accepted,rejected,attempts,cohorts,T_K,DII_m3,photons_com3,HI,HeI,HeII,DI,max_photon_ledger,max_energy_ledger,max_accepted_defect,wall_s"
    );
    println!(
        "{status},{rtol:.17e},{cx:.17e},{end:.17e},{:.17e},{accepted},{rejected},{tries},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{max_n:.17e},{max_e:.17e},{max_a:.17e},{:.9e}",
        s.time_s,
        s.cohorts.len(),
        s.full.gas.eos().unwrap().temperature_k,
        s.full.gas.nuclei.density_m3(S::DIonized),
        p.count,
        events[0],
        events[1],
        events[2],
        events[3],
        start.elapsed().as_secs_f64()
    );
    if status != "COMPLETE" {
        std::process::exit(2);
    }
}
