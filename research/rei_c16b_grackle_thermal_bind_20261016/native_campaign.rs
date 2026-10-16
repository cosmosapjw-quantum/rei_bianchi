#[path = "c16b_grackle/native_bind.rs"]
mod native_bind;
use native_bind::*;
use std::{fs, path::Path};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    let mode = args.get(1).map(String::as_str).unwrap_or("campaign");
    if mode == "rhs" {
        return rhs_server(
            args.get(2).map(|v| v.parse()).transpose()?.unwrap_or(0.1),
            args.get(3).map(|v| v.parse()).transpose()?.unwrap_or(0.0),
            args.get(4).map(|v| v != "0").unwrap_or(true),
        );
    }
    let out = Path::new(args.get(2).map(String::as_str).unwrap_or("native_output"));
    fs::create_dir_all(out)?;
    let f = fixtures()?;
    // Freeze full numeric fixture values before any campaign output is interpreted.
    let manifest = format!(
        "[{}]",
        f.iter().map(fixture_json).collect::<Vec<_>>().join(",")
    );
    fs::write(out.join("frozen_manifest.json"), manifest)?;
    if mode == "manifest" {
        return Ok(());
    }
    if mode == "tests" {
        rollback_tests(&out.join("rollback.json"))?;
        return isolated_event_tests(&out.join("isolated_event_controls.jsonl"));
    }
    if mode == "dynamic" {
        return dynamic_smoke(&out.join("dynamic_smoke.jsonl"));
    }
    if mode == "stiff" {
        let strong = f.iter().find(|v| v.name == "strong_absorption").unwrap();
        return run_one(
            strong,
            1,
            1,
            16,
            8,
            64,
            &out.join("strong_absorption_n1.jsonl"),
        );
    }
    if mode == "campaign" {
        for fixture in &f {
            let levels = if ["recomb8000", "collision1e5", "mixed1e4"].contains(&fixture.name) {
                vec![32, 64, 128]
            } else {
                vec![32]
            };
            for n in levels {
                run_one(
                    fixture,
                    n,
                    1,
                    16,
                    8,
                    64,
                    &out.join(format!("{}_n{}.jsonl", fixture.name, n)),
                )?;
            }
        }
        let mixed = f.iter().find(|v| v.name == "mixed1e4").unwrap();
        run_one(
            mixed,
            32,
            8,
            16,
            8,
            64,
            &out.join("mixed1e4_n32_threads8.jsonl"),
        )?;
        rollback_tests(&out.join("rollback.json"))?;
        return Ok(());
    }
    if mode == "pulse_repair" {
        for name in ["pulse_early", "pulse_delayed"] {
            let fixture = f.iter().find(|v| v.name == name).unwrap();
            run_one(
                fixture,
                32,
                1,
                16,
                8,
                64,
                &out.join(format!("{}_n32.jsonl", name)),
            )?;
        }
        rollback_tests(&out.join("rollback.json"))?;
        return retry_recovery_test(&out.join("retry_recovery.json"));
    }
    if mode == "essential" {
        let source = f.iter().find(|v| v.name == "mixed1e4").unwrap();
        return run_one(source, 32, 1, 16, 8, 64, &out.join("mixed1e4_n32.jsonl"));
    }
    if mode == "temporal_refine" || mode == "temporal_refine1024" {
        let source = f.iter().find(|v| v.name == "mixed1e4").unwrap();
        let levels = if mode == "temporal_refine" {
            vec![256, 512]
        } else {
            vec![1024]
        };
        for n in levels {
            run_one(
                source,
                n,
                1,
                16,
                8,
                64,
                &out.join(format!("mixed1e4_n{}.jsonl", n)),
            )?;
        }
        return Ok(());
    }
    if mode == "stiff_ci" {
        let mut source = f.iter().find(|v| v.name == "collision1e5").unwrap().clone();
        source.name = "stiff_collision1e5";
        source.horizon = source.horizon / 0.08 * 10.0;
        fs::write(
            out.join("stiff_ci_frozen_manifest.json"),
            fixture_json(&source),
        )?;
        return run_one(
            &source,
            1,
            1,
            16,
            8,
            64,
            &out.join("stiff_collision1e5_n1.jsonl"),
        );
    }
    if mode == "retry_test" {
        return retry_recovery_test(&out.join("retry_recovery.json"));
    }
    if mode == "stiff_rr" {
        let mut source = f.iter().find(|v| v.name == "recomb8000").unwrap().clone();
        source.name = "stiff_recomb8000";
        source.horizon = source.horizon / 0.03 * 10.0;
        fs::write(
            out.join("stiff_rr_frozen_manifest.json"),
            fixture_json(&source),
        )?;
        return run_one(
            &source,
            1,
            1,
            16,
            8,
            64,
            &out.join("stiff_recomb8000_n1.jsonl"),
        );
    }
    if mode == "cohort_refinement" {
        let mut source = f.iter().find(|v| v.name == "md14_smoke").unwrap().clone();
        source.name = "md14_birth_cohort";
        source.source = Source::None;
        source.q_ref = 0.1;
        fs::write(out.join("cohort_frozen_manifest.json"),format!("{{\"fixture\":{},\"birth_a\":{},\"birth_z\":20,\"native_MD14_emission_interval_s\":1e14,\"construction\":\"native inject at birth then geometry_map; reset local gas and ledger anchor at a=.1; source off during local reaction\"}}",fixture_json(&source),1.0/21.0))?;
        for sub in [16, 32, 64] {
            run_one(
                &source,
                32,
                1,
                sub,
                32,
                128,
                &out.join(format!("spectral_sub{}.jsonl", sub)),
            )?;
        }
        for nmu in [8, 16, 32] {
            run_one(
                &source,
                32,
                1,
                64,
                nmu,
                128,
                &out.join(format!("angular_mu{}.jsonl", nmu)),
            )?;
        }
        for cells in [32, 64, 128] {
            run_one(
                &source,
                32,
                1,
                64,
                32,
                cells,
                &out.join(format!("transport_cells{}.jsonl", cells)),
            )?;
        }
        return Ok(());
    }
    if mode == "refinement" {
        let mut source = f.iter().find(|v| v.name == "md14_smoke").unwrap().clone();
        source.q_ref = 0.1;
        for sub in [16, 32, 64] {
            run_one(
                &source,
                32,
                1,
                sub,
                32,
                128,
                &out.join(format!("spectral_sub{}.jsonl", sub)),
            )?;
        }
        for nmu in [8, 16, 32] {
            run_one(
                &source,
                32,
                1,
                64,
                nmu,
                128,
                &out.join(format!("angular_mu{}.jsonl", nmu)),
            )?;
        }
        for cells in [32, 64, 128] {
            run_one(
                &source,
                32,
                1,
                64,
                32,
                cells,
                &out.join(format!("transport_cells{}.jsonl", cells)),
            )?;
        }
        return Ok(());
    }
    Err("unknown mode".into())
}
