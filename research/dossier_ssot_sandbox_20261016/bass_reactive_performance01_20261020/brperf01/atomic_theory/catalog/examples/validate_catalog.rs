use rei_atomic_catalog::{PreparedTemperature, TemperatureTable, catalog};
use std::fs::{File, create_dir_all};
use std::hint::black_box;
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::time::Instant;

fn grid(lo: f64, hi: f64, fraction: f64) -> f64 {
    if fraction == 0.0 {
        lo
    } else if fraction == 1.0 {
        hi
    } else {
        lo * ((hi / lo).ln() * fraction).exp()
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let out = PathBuf::from(
        std::env::args()
            .nth(1)
            .unwrap_or_else(|| "evidence".to_string()),
    );
    create_dir_all(&out)?;
    let mut values = BufWriter::new(File::create(out.join("ATOMIC_VALUES.csv"))?);
    writeln!(values, "process,z,electrons,input,value_si")?;
    let mut scans = BufWriter::new(File::create(out.join("TABLE_SCANS.csv"))?);
    writeln!(
        scans,
        "process,z,electrons,tolerance,nodes,storage_bytes,bound,max_relative_error,worst_temperature_k,scan_points"
    )?;
    for fit in catalog() {
        let ion = fit.ion();
        let z = ion.atomic_number();
        let n = ion.electrons();
        let ci = fit.collisional_ionization();
        let photo = fit.photo();
        let [lo, hi] = ci.temperature_domain_k();
        for i in 0..=256 {
            let t = grid(lo, hi, i as f64 / 256.0);
            writeln!(
                values,
                "ci,{z},{n},{t:.17e},{:.17e}",
                ci.rate_m3_s(t).unwrap()
            )?;
        }
        let [lo, hi] = photo.energy_domain_ev();
        for i in 0..=128 {
            let e = grid(lo, hi, i as f64 / 128.0);
            writeln!(
                values,
                "pi,{z},{n},{e:.17e},{:.17e}",
                photo.cross_section_m2(e).unwrap()
            )?;
        }
        if let Some(rr) = fit.recombination_toward() {
            let [lo, hi] = rr.temperature_domain_k();
            for i in 0..=128 {
                let t = grid(lo, hi, i as f64 / 128.0);
                writeln!(
                    values,
                    "rr,{z},{n},{t:.17e},{:.17e}",
                    rr.rate_m3_s(t).unwrap()
                )?;
            }
        }
        for tolerance in [1e-4, 1e-5, 1e-6] {
            for process in ["ci", "rr"] {
                let table = if process == "ci" {
                    TemperatureTable::from_ci(ci, tolerance).unwrap()
                } else if let Some(rr) = fit.recombination_toward() {
                    TemperatureTable::from_rr(rr, tolerance).unwrap()
                } else {
                    continue;
                };
                let [lo, hi] = table.temperature_domain_k();
                let mut max_error = 0.0_f64;
                let mut worst_t = lo;
                let mut points = 0;
                for cell in 0..table.nodes() - 1 {
                    for theta in [0.173, 0.5, 0.827] {
                        let t = grid(lo, hi, (cell as f64 + theta) / (table.nodes() - 1) as f64);
                        let direct = if process == "ci" {
                            ci.rate_m3_s(t).unwrap()
                        } else {
                            fit.recombination_toward().unwrap().rate_m3_s(t).unwrap()
                        };
                        let tabulated = table.rate_m3_s(t).unwrap();
                        let error = (tabulated / direct - 1.0).abs();
                        if error > max_error {
                            max_error = error;
                            worst_t = t;
                        }
                        points += 1;
                    }
                }
                assert!(max_error <= table.interpolation_relative_bound() + 2e-13);
                writeln!(
                    scans,
                    "{process},{z},{n},{tolerance:.17e},{},{},{:.17e},{max_error:.17e},{worst_t:.17e},{points}",
                    table.nodes(),
                    table.storage_bytes(),
                    table.interpolation_relative_bound()
                )?;
            }
        }
    }
    values.flush()?;
    scans.flush()?;
    let build_start = Instant::now();
    let tables = catalog()
        .iter()
        .map(|r| TemperatureTable::from_ci(r.collisional_ionization(), 1e-4).unwrap())
        .collect::<Vec<_>>();
    let build_s = build_start.elapsed().as_secs_f64();
    let count = 300_000;
    let queries = (0..count)
        .map(|i| {
            let j = (i * 17 + 3) % catalog().len();
            let [lo, hi] = catalog()[j].collisional_ionization().temperature_domain_k();
            let t = grid(lo, hi, ((i * 7919 + 3253) % 100_003) as f64 / 100_003.0);
            (j, t)
        })
        .collect::<Vec<_>>();
    for &(j, t) in &queries[..10_000] {
        black_box(catalog()[j].collisional_ionization().rate_m3_s(t).unwrap());
        black_box(tables[j].rate_m3_s(t).unwrap());
    }
    let mut bench = BufWriter::new(File::create(out.join("CATALOG_BENCHMARK.csv"))?);
    writeln!(bench, "repeat,backend,queries,seconds,checksum")?;
    for repeat in 0..12 {
        let modes = if repeat % 2 == 0 {
            ["direct", "table"]
        } else {
            ["table", "direct"]
        };
        for mode in modes {
            let start = Instant::now();
            let mut sum = 0.0;
            for &(j, t) in black_box(&queries) {
                sum += black_box(if mode == "direct" {
                    catalog()[j]
                        .collisional_ionization()
                        .rate_m3_s(black_box(t))
                        .unwrap()
                } else {
                    tables[j].rate_m3_s(black_box(t)).unwrap()
                });
            }
            let seconds = start.elapsed().as_secs_f64();
            writeln!(bench, "{repeat},{mode},{count},{seconds:.17e},{sum:.17e}")?;
        }
    }
    bench.flush()?;
    // Every ion sees the same T; the common domain is the intersection of all
    // individual CI validity domains. Log(T) setup is INCLUDED in timed loops.
    let common_lo = catalog()
        .iter()
        .map(|r| r.collisional_ionization().temperature_domain_k()[0])
        .fold(0.0_f64, f64::max);
    let common_hi = catalog()
        .iter()
        .map(|r| r.collisional_ionization().temperature_domain_k()[1])
        .fold(f64::INFINITY, f64::min);
    let common_temperatures = (0..12_500)
        .map(|i| {
            grid(
                common_lo,
                common_hi,
                ((i * 7919 + 3253) % 100_003) as f64 / 100_003.0,
            )
        })
        .collect::<Vec<_>>();
    let mut bundle_bench = BufWriter::new(File::create(out.join("CATALOG_BUNDLE_BENCHMARK.csv"))?);
    writeln!(
        bundle_bench,
        "repeat,backend,temperatures,channels,seconds,checksum"
    )?;
    for repeat in 0..12 {
        let modes = if repeat % 2 == 0 {
            ["direct", "table_scalar", "table_shared_log"]
        } else {
            ["table_shared_log", "table_scalar", "direct"]
        };
        for mode in modes {
            let start = Instant::now();
            let mut sum = 0.0;
            for &t in black_box(&common_temperatures) {
                let prepared = PreparedTemperature::new(black_box(t)).unwrap();
                for (fit, table) in catalog().iter().zip(&tables) {
                    sum += black_box(match mode {
                        "direct" => fit
                            .collisional_ionization()
                            .rate_m3_s(black_box(t))
                            .unwrap(),
                        "table_scalar" => table.rate_m3_s(black_box(t)).unwrap(),
                        _ => table.rate_prepared(prepared).unwrap(),
                    });
                }
            }
            let seconds = start.elapsed().as_secs_f64();
            writeln!(
                bundle_bench,
                "{repeat},{mode},{},24,{seconds:.17e},{sum:.17e}",
                common_temperatures.len()
            )?;
        }
    }
    bundle_bench.flush()?;
    let bytes: usize = tables.iter().map(TemperatureTable::storage_bytes).sum();
    std::fs::write(
        out.join("CATALOG_BUILD.json"),
        format!(
            "{{\n  \"ci_table_build_seconds\": {build_s:.17e},\n  \"ci_table_payload_bytes\": {bytes},\n  \"ci_table_count\": 24,\n  \"requested_relative_interpolation_error\": 1e-4\n}}\n"
        ),
    )?;
    println!(
        "catalog validation complete; 24 PI, 24 CI, 12 sparse RR coefficient fits; CI table payload {bytes} bytes"
    );
    Ok(())
}
