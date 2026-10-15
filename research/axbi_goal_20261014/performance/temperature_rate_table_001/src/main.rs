use axbi_temperature_rate_table_benchmark::{
    temperature,
    thermal_adapter::{igm_point_rhs, IgmPhotoInput},
    validation::{compare_rate_bundle, compare_rhs_pair, mixed_fixture},
    Table,
};
use rei_microphysics::{
    axbi_rates::AxbiProvider,
    igm_rates::{igm_rates, IgmRates},
    igm_state::IgmGasState,
    ForwardError,
};
use std::{fs, hint::black_box, path::PathBuf, time::Instant};
fn cpu() -> f64 {
    fs::read_to_string("/proc/self/schedstat")
        .ok()
        .and_then(|s| s.split_whitespace().next()?.parse::<f64>().ok())
        .unwrap_or(0.0)
        / 1e9
}
fn table_point(
    table: &Table,
    s: &IgmGasState,
    nh: f64,
    nhe: f64,
    h: f64,
    tcmb: f64,
    photo: IgmPhotoInput,
) -> Result<
    (
        f64,
        IgmRates,
        axbi_temperature_rate_table_benchmark::thermal_adapter::IgmPointRhs,
    ),
    ForwardError,
> {
    let t = s.eos(nh, nhe)?.temperature_k;
    let rhs = igm_point_rhs(s, nh, nhe, h, tcmb, photo, |q| table.query(q))?;
    let rates = table.query(t)?;
    Ok((t, rates, rhs))
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(2)
    }
}
fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 7 || args[1] != "--contract" || args[3] != "--table" || args[5] != "--output" {
        return Err("ARGS".into());
    }
    if fs::read(&args[2]).map_err(|e| e.to_string())?
        != include_bytes!("../AUTHORITY_CONTRACT.json")
    {
        return Err("CONTRACT_BYTES".into());
    }
    let path = PathBuf::from(&args[4]);
    let start = Instant::now();
    let cp = cpu();
    let table = Table::load(&path)?;
    let load_wall = start.elapsed().as_secs_f64();
    let load_cpu = cpu() - cp;
    let local = fs::read_to_string(
        path.parent()
            .unwrap()
            .parent()
            .unwrap()
            .join("gate_completion_001/raw/local_test_counts.json"),
    )
    .map_err(|e| e.to_string())?;
    fn count(text: &str, key: &str) -> Result<u64, String> {
        let pattern = format!("\"{key}\"");
        let after = text
            .split_once(&pattern)
            .ok_or_else(|| format!("MISSING_COUNT_{key}"))?
            .1;
        let after = after
            .strip_prefix(':')
            .ok_or_else(|| format!("COUNT_COLON_{key}"))?;
        after
            .split(|c: char| !c.is_ascii_digit())
            .find(|s| !s.is_empty())
            .ok_or_else(|| format!("COUNT_VALUE_{key}"))?
            .parse()
            .map_err(|_| format!("COUNT_PARSE_{key}"))
    }
    let mut direct = count(&local, "cumulative_direct")?;
    let mut lookups = count(&local, "cumulative_lookups")?;
    if count(&local, "invalid_rhs_cases")? != 13 {
        return Err("LOCAL_INVALID_FIXTURE_COUNT".into());
    }
    let mut rates: Vec<f64> = (0..257).map(|j| temperature(j * 65536 / 256)).collect();
    let saved = fs::read(path.parent().unwrap().join("saved_temperatures.bin"))
        .map_err(|e| e.to_string())?;
    if saved.len() != 2048 {
        return Err("SAVED_TEMPERATURE_DIMENSION".into());
    }
    for b in saved.chunks_exact(8) {
        rates.push(f64::from_bits(u64::from_le_bytes(b.try_into().unwrap())))
    }
    for &t in &rates {
        let a = igm_rates(t).map_err(|e| format!("{e:?}"))?;
        direct += 1;
        let b = table.query(t).map_err(|e| format!("{e:?}"))?;
        compare_rate_bundle(&a, &b, t)?;
    }
    let mut rhs_states = Vec::new();
    for j in 1..=64 {
        let index = 4 * j - 2;
        let t = temperature(index * 65536 / 256);
        let (state, nh, nhe, h, photo) = mixed_fixture(t)?;
        let a = AxbiProvider
            .point(&state, nh, nhe, h, 2.7255, photo)
            .map_err(|e| format!("PRETIMING_REFERENCE j={j} {e:?}"))?;
        direct += 2;
        let b = table_point(&table, &state, nh, nhe, h, 2.7255, photo)
            .map_err(|e| format!("PRETIMING_CANDIDATE j={j} {e:?}"))?;
        if a.temperature_k.to_bits() != b.0.to_bits() {
            return Err(format!(
                "PRETIMING_TEMPERATURE j={j} reference_bits={} candidate_bits={}",
                a.temperature_k.to_bits(),
                b.0.to_bits()
            ));
        }
        compare_rate_bundle(&a.rates, &b.1, a.temperature_k)?;
        compare_rhs_pair(&a.rhs, &b.2, &state, nh, nhe, a.temperature_k, photo)?;
        rhs_states.push((state, nh, nhe, h, photo));
    }
    if direct > 1_900_000 || lookups > 7_900_000 {
        return Err("INSUFFICIENT_RESERVED_QUOTA".into());
    }
    let mut lines = Vec::new();
    for rep in 0..3 {
        for mode in if rep % 2 == 0 {
            [0, 1, 2, 3]
        } else {
            [1, 0, 3, 2]
        } {
            let st = Instant::now();
            let ct = cpu();
            let mut checksum = 0.0;
            let mut count = 0;
            for _ in 0..8 {
                if mode < 2 {
                    for &t in &rates {
                        let v = if mode == 0 {
                            direct += 1;
                            igm_rates(black_box(t))
                        } else {
                            table.query(black_box(t))
                        }
                        .map_err(|e| format!("{e:?}"))?;
                        let all = axbi_temperature_rate_table_benchmark::columns(&black_box(v));
                        checksum += black_box(
                            all.iter().sum::<f64>()
                                + v.diagnostics.dr_excluded_erg_cm3_s
                                + v.diagnostics.ce_cap_erg.iter().sum::<f64>(),
                        );
                        count += 1
                    }
                } else {
                    for (state, nh, nhe, h, photo) in &rhs_states {
                        let (rates, rhs) = if mode == 2 {
                            direct += 2;
                            AxbiProvider
                                .point(black_box(state), *nh, *nhe, *h, 2.7255, *photo)
                                .map(|q| (q.rates, q.rhs))
                        } else {
                            table_point(&table, black_box(state), *nh, *nhe, *h, 2.7255, *photo)
                                .map(|q| (q.1, q.2))
                        }
                        .map_err(|e| format!("{e:?}"))?;
                        checksum += black_box(
                            rhs.temperature_dt_k_s
                                + rhs.w_dt_erg_per_h_s
                                + rhs.fraction_dt.iter().sum::<f64>()
                                + rhs.species_chemical_cm3_s.iter().sum::<f64>()
                                + rhs.photo_events_cm3_s.iter().sum::<f64>()
                                + rhs.ci_events_cm3_s.iter().sum::<f64>()
                                + rhs.rr_events_cm3_s.iter().sum::<f64>()
                                + rhs.thermal_micro_erg_cm3_s
                                + rhs.binding_micro_erg_cm3_s
                                + rhs.escape_erg_cm3_s
                                + axbi_temperature_rate_table_benchmark::columns(&rates)
                                    .iter()
                                    .sum::<f64>(),
                        );
                        black_box((rates, rhs));
                        count += 1
                    }
                }
            }
            let wall = st.elapsed().as_secs_f64();
            let c = cpu() - ct;
            lines.push(format!("{{\"rep\":{rep},\"mode\":{mode},\"count\":{count},\"wall_s\":{wall},\"cpu_s\":{c},\"checksum\":{checksum}}}"));
            black_box(checksum);
        }
    }
    lookups += table.lookup.get();
    direct += table.direct.get();
    if direct > 2_000_000 || lookups > 8_000_000 {
        return Err(format!("QUOTA direct={direct} lookups={lookups}"));
    }
    let bytes = fs::metadata(&path).map_err(|e| e.to_string())?.len();
    let output=format!("{{\"status\":\"COMPONENT_GATES_PASS\",\"load_wall_s\":{load_wall},\"load_cpu_s\":{load_cpu},\"artifact_bytes\":{bytes},\"direct_cumulative\":{direct},\"lookups_cumulative\":{lookups},\"fallback_remote\":{},\"timing\":[{}],\"whole_driver_speedup\":\"NOT_MEASURED\",\"scientific_admission\":\"NOT_ISSUED\"}}\n",table.fallback.get(),lines.join(","));
    fs::write(&args[6], output).map_err(|e| e.to_string())?;
    Ok(())
}
