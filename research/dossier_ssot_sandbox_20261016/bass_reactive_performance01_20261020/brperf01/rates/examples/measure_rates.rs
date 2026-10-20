use parent::igm_rates::igm_rates;
use parent::rate_table::{IgmRateTable, igm_flat};
use rei_brperf01_rates::{CompactRateTable, source_digest};
use std::fs::{File, create_dir_all};
use std::hint::black_box;
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::time::Instant;

fn relative(a: f64, b: f64) -> f64 {
    if a == 0.0 {
        if b == 0.0 { 0.0 } else { f64::INFINITY }
    } else {
        (b / a - 1.0).abs()
    }
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mode = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "probe".to_string());
    let out = PathBuf::from(
        std::env::args()
            .nth(2)
            .unwrap_or_else(|| "evidence".to_string()),
    );
    create_dir_all(&out)?;
    let start = Instant::now();
    let legacy = IgmRateTable::new(65537).unwrap();
    let legacy_build = start.elapsed().as_secs_f64();
    if mode == "probe" {
        let mut summary = BufWriter::new(File::create(out.join("RESOLUTION_SCAN.csv"))?);
        writeln!(
            summary,
            "nodes,storage_bytes,blocked_cells,source_evaluations,build_seconds,samples,max_relative_error,worst_channel,worst_temperature_k,max_legacy_relative_error,scalar_simd_mismatches"
        )?;
        let mut samples = BufWriter::new(File::create(out.join("INDEPENDENT_SAMPLES.csv"))?);
        writeln!(
            samples,
            "nodes,temperature_k,cell,theta,fallback,channel,direct,compact,legacy"
        )?;
        for nodes in [1025, 2049, 4097, 8193] {
            let start = Instant::now();
            let table = CompactRateTable::build(nodes).unwrap();
            let build = start.elapsed().as_secs_f64();
            let mut grid = BufWriter::new(File::create(out.join(format!("NODES_{nodes}.csv")))?);
            writeln!(
                grid,
                "index,log_t,temperature_k,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14"
            )?;
            let h = 1e6_f64.ln() / (nodes - 1) as f64;
            for i in 0..nodes {
                let x = h * i as f64;
                let t = if i == 0 {
                    1.0
                } else if i + 1 == nodes {
                    1e6
                } else {
                    x.exp()
                };
                write!(grid, "{i},{x:.17e},{t:.17e}")?;
                for v in igm_flat(igm_rates(t).unwrap()) {
                    write!(grid, ",{v:.17e}")?;
                }
                writeln!(grid)?;
            }
            grid.flush()?;
            let mut max = 0.0;
            let mut legacy_max = 0.0_f64;
            let mut worst_channel = 0;
            let mut worst_t = 0.0;
            let mut mismatch = 0;
            let mut count = 0;
            let mut queries = (0..20001)
                .map(|i| (1e6_f64.ln() * (i as f64 + 0.371) / 20002.0).exp())
                .collect::<Vec<_>>();
            for i in 0..nodes - 1 {
                for f in [0.211, 0.5, 0.789] {
                    queries.push((h * (i as f64 + f)).exp());
                }
            }
            for (q, &t) in queries.iter().enumerate() {
                let direct = igm_flat(igm_rates(t).unwrap());
                let scalar = igm_flat(table.rates(t).unwrap());
                let simd = igm_flat(table.rates_simd(t).unwrap());
                let old = igm_flat(legacy.rates(t).unwrap());
                let x = t.ln() * ((nodes - 1) as f64 / 1e6_f64.ln());
                let cell = (x.floor() as usize).min(nodes - 2);
                let theta = (x - cell as f64).clamp(0.0, 1.0);
                for j in 0..15 {
                    assert!(scalar[j] >= 0.0 && scalar[j].is_finite());
                    if scalar[j].to_bits() != simd[j].to_bits() {
                        mismatch += 1;
                    }
                    let error = relative(direct[j], scalar[j]);
                    if error > max {
                        max = error;
                        worst_channel = j;
                        worst_t = t;
                    }
                    legacy_max = legacy_max.max(relative(direct[j], old[j]));
                    if q % 127 == 0 {
                        writeln!(
                            samples,
                            "{nodes},{t:.17e},{cell},{theta:.17e},{},{j},{:.17e},{:.17e},{:.17e}",
                            table.direct_fallback(t),
                            direct[j],
                            scalar[j],
                            old[j]
                        )?;
                    }
                }
                count += 1;
            }
            assert_eq!(mismatch, 0);
            writeln!(
                summary,
                "{nodes},{},{},{},{build:.17e},{count},{max:.17e},{worst_channel},{worst_t:.17e},{legacy_max:.17e},{mismatch}",
                table.storage_bytes(),
                table.blocked_cells(),
                table.source_evaluations()
            )?;
            if nodes == 4097 || nodes == 8193 {
                std::fs::write(out.join(format!("COMPACT_{nodes}.cache")), table.to_bytes())?;
            }
            println!(
                "nodes={nodes} max_rel={max:.6e} bytes={} blocked={} build={build:.6e}s",
                table.storage_bytes(),
                table.blocked_cells()
            );
        }
        summary.flush()?;
        samples.flush()?;
        let source = source_digest()
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<String>();
        std::fs::write(
            out.join("LEGACY_BASELINE.json"),
            format!(
                "{{\n\"nodes\":65537,\n\"storage_bytes\":{},\n\"build_seconds\":{legacy_build:.17e},\n\"compiled_source_digest\":\"{source}\",\n\"wide_version\":\"1.7.1\",\n\"sha2_version\":\"0.10.9\",\n\"compiled_avx\":{},\n\"compiled_sse2\":{}\n}}\n",
                legacy.storage_bytes(),
                cfg!(target_feature = "avx"),
                cfg!(target_feature = "sse2")
            ),
        )?;
    } else {
        let tables = [1025, 2049, 4097, 8193].map(|n| CompactRateTable::build(n).unwrap());
        let queries = (0..100_000)
            .map(|i| {
                (1e6_f64.ln() * (((i * 7919 + 3521) % 100003) as f64 + 0.371) / 100004.0).exp()
            })
            .collect::<Vec<_>>();
        let mut bench = BufWriter::new(File::create(out.join("BENCHMARK_ABBA.csv"))?);
        writeln!(
            bench,
            "block,candidate,position,backend,queries,seconds,checksum"
        )?;
        let modes = [
            "legacy65537",
            "compact1025",
            "compact2049",
            "compact4097",
            "compact8193",
            "simd4097",
            "simd8193",
        ];
        // Warm every receiver on the same inputs before the paired timed blocks.
        for &t in queries.iter().take(10_000) {
            black_box(igm_rates(black_box(t)).unwrap());
            black_box(legacy.rates(black_box(t)).unwrap());
            for table in &tables {
                black_box(table.rates(black_box(t)).unwrap());
                black_box(table.rates_simd(black_box(t)).unwrap());
            }
        }
        for block in 0..6 {
            for candidate in modes {
                for (position, which) in ["direct", candidate, candidate, "direct"]
                    .into_iter()
                    .enumerate()
                {
                    let start = Instant::now();
                    let mut sum = 0.0;
                    for &t in black_box(&queries) {
                        let r = match which {
                            "direct" => igm_rates(black_box(t)).unwrap(),
                            "legacy65537" => legacy.rates(black_box(t)).unwrap(),
                            "compact1025" => tables[0].rates(black_box(t)).unwrap(),
                            "compact2049" => tables[1].rates(black_box(t)).unwrap(),
                            "compact4097" => tables[2].rates(black_box(t)).unwrap(),
                            "compact8193" => tables[3].rates(black_box(t)).unwrap(),
                            "simd4097" => tables[2].rates_simd(black_box(t)).unwrap(),
                            _ => tables[3].rates_simd(black_box(t)).unwrap(),
                        };
                        // Consume all channels and diagnostics so useful work cannot
                        // disappear. Common checksum reduction is timed on all paths.
                        for v in igm_flat(r) {
                            sum += black_box(v);
                        }
                        sum += black_box(
                            r.dr_cooling_erg_cm3_s
                                + r.diagnostics.ci_floor_cm3_s.iter().sum::<f64>(),
                        );
                    }
                    let seconds = start.elapsed().as_secs_f64();
                    writeln!(
                        bench,
                        "{block},{candidate},{position},{which},100000,{seconds:.17e},{sum:.17e}"
                    )?;
                }
            }
        }
        bench.flush()?;
        println!("ABBA coefficient benchmark complete");
    }
    Ok(())
}
