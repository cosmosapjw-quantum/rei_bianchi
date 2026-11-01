//! C3 matched-accuracy event-aware small numerical benchmark, not a full EoR.
use rei_microphysics::axbi_q_advance::{advance_batch, advance_frozen_expanding, EnergySoA};
use rei_microphysics::axbi_q_reference::{emit_from_axbi_source, CovariantPhoton};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::AxisymmetricPoint;
use std::time::Instant;

fn run() -> Result<(), rei_microphysics::ForwardError> {
    let g = AxisymmetricPoint::new(1.0, 0.0, 1e-16, 0.0)?.snapshot()?;
    let src = AxbiSource::new(1.9e-7, 0.2, 16, 8)?;
    let base = emit_from_axbi_source(&src, &g, 20.0, 1e11)?;
    let packets: Vec<CovariantPhoton> = base.repeat(64);
    let dens = [2e-11, 3e-12, 1e-12];
    let anis = [1.0e-16, 1.0e-16, 1.3e-16];
    let isot = [1.0e-16; 3];
    let dt = 2e14;
    let mut ref_sum = 0.;
    let initial = Instant::now();
    for part in [1, 2, 4, 8, 16, 32, 64, 256] {
        let r = advance_frozen_expanding(
            &CovariantPhoton::from_local(&g, 54.9, [1.0, 0.0, 0.0], 1.0)?,
            &g,
            isot,
            [0.0, 0.0, 1e-10],
            1e15,
            part,
        )?;
        ref_sum += r.absorbed_per_h[2];
        println!(
            "REFINE,{part},{:.17e},{:.17e},{:.17e}",
            r.absorbed_per_h[2], r.heat_ev_per_h, r.redshift_work_ev_per_h
        );
    }
    std::hint::black_box(ref_sum);
    eprintln!("C3_SCOPED_REFINEMENT_S={}", initial.elapsed().as_secs_f64());
    // Keep the physics, inputs, slices and packet ordering fixed.
    let slice_count = 8;
    let mut reference = None;
    for h in [isot, anis] {
        let shape = if h == isot { "FLRW" } else { "AXISYM" };
        for threads in [1, 2, 4] {
            let mut timings = Vec::new();
            let mut final_count = 0.;
            let mut checksum = 0.;
            let mut outputs = Vec::new();
            for rep in 0..4 {
                let start = Instant::now();
                outputs = advance_batch(&packets, &g, h, dens, dt, slice_count, threads)?;
                let elapsed = start.elapsed().as_secs_f64();
                if rep > 0 {
                    timings.push(elapsed);
                }
            }
            timings.sort_by(|a, b| a.total_cmp(b));
            // Same-order summation for serial & parallel; all returned
            // packet observables are compared at the same binary64 inputs.
            for o in &outputs {
                final_count += o.final_packet.photons_per_h;
                checksum += o.heat_ev_per_h + o.binding_ev_per_h + o.redshift_work_ev_per_h;
            }
            if threads == 1 {
                reference = Some(outputs.clone());
            } else {
                let original = reference.as_ref().unwrap();
                assert_eq!(original.len(), outputs.len());
                for (x, y) in original.iter().zip(outputs.iter()) {
                    assert_eq!(
                        x.final_packet.photons_per_h.to_bits(),
                        y.final_packet.photons_per_h.to_bits()
                    );
                    assert_eq!(x.heat_ev_per_h.to_bits(), y.heat_ev_per_h.to_bits());
                }
            }
            println!(
                "BENCH,{shape},{threads},{},{:.6},{:.17e},{:.17e},{}",
                outputs.len(),
                timings[1],
                final_count,
                checksum,
                std::mem::size_of::<rei_microphysics::axbi_q_advance::EvolvingPacket>()
            );
        }
    }
    // SoA explicitly changes layout, not science or the source stream.
    let soa = EnergySoA::from_packets(&packets)?;
    let check_geom = AxisymmetricPoint::new(0.3, 0.025, 1e-16, 0.0)?.snapshot()?;
    let check = soa.energies_at(&check_geom)?;
    for (p, e) in packets.iter().zip(&check) {
        let direct = p.energy_at(&check_geom)?;
        assert!((direct - *e).abs() <= 5e-14 * direct.abs().max(1.0));
    }
    for mode in ["AOS", "SOA"] {
        let start = Instant::now();
        let mut signature = 0.0;
        for _ in 0..48 {
            if mode == "AOS" {
                for p in &packets {
                    signature += p.energy_at(&check_geom)?;
                }
            } else {
                for e in soa.energies_at(&check_geom)? {
                    signature += e;
                }
            }
        }
        let elapsed = start.elapsed().as_secs_f64();
        println!(
            "ENERGY,{mode},{},{:.6},{:.17e},{}",
            packets.len(),
            elapsed,
            signature,
            soa.allocated_bytes()
        );
        std::hint::black_box(signature);
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
