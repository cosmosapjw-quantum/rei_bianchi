//! Small actual --release fixed-q grid benchmark; not a full cosmological solver.
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::AxisymmetricPoint;
use std::time::Instant;
fn run() -> Result<(), rei_microphysics::ForwardError> {
    let g0 = AxisymmetricPoint::new(1.0 / 21.0, 0.0, 1e-16, 0.0)?.snapshot()?;
    let g1 = AxisymmetricPoint::new(1.00002 / 21.0, 0.0000003, 1e-16, 0.0)?.snapshot()?;
    let source = AxbiSource::new(1.9e-7, 0.2, 16, 32)?;
    println!("kind,threads,N_E,N_mu,state_bytes,median_ms,checksum");
    for ne in [64, 128, 256, 512] {
        let empty = QFixedGrid::new(&source, g0, ne, 433.0)?;
        let mut active = empty.clone();
        active.inject(&g0, 20.0, 1e10, 1)?;
        for kind in ["SOURCE", "ABSORB", "ADVANCE"] {
            for threads in [1, 2, 4] {
                let mut durations = Vec::new();
                let mut checksum = 0.0;
                for trial in 0..5 {
                    let mut trial_state = if kind == "SOURCE" {
                        empty.clone()
                    } else {
                        active.clone()
                    };
                    let t0 = Instant::now();
                    checksum = match kind {
                        "SOURCE" => {
                            trial_state
                                .inject(&g0, 20.0, 1e10, threads)?
                                .added_photons_per_h
                        }
                        "ABSORB" => {
                            trial_state
                                .absorb_frozen(&g0, [2e-5, 2e-6, 1e-7], 1e9, threads)?
                                .heat_ev_per_h
                        }
                        _ => {
                            trial_state
                                .advance_frozen(&g0, &g1, [2e-5, 2e-6, 1e-7], 1e10, 6, threads)?
                                .heat_ev_per_h
                        }
                    };
                    std::hint::black_box(checksum);
                    if trial > 0 {
                        durations.push(t0.elapsed().as_secs_f64() * 1e3);
                    }
                }
                durations.sort_by(|a, b| a.total_cmp(b));
                println!(
                    "{kind},{threads},{ne},32,{}, {:.6},{:.17e}",
                    empty.buffer_capacity_bytes(),
                    (durations[1] + durations[2]) * 0.5,
                    checksum
                );
            }
        }
    }
    Ok(())
}
fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
