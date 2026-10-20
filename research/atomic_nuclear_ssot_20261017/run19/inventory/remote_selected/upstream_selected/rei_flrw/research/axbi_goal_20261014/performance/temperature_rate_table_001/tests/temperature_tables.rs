use axbi_temperature_rate_table_benchmark::{validation::validate, Table};
use std::path::Path;
#[test]
fn frozen_table_matrix() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let path = root.join("data/rates.bin");
    assert!(std::fs::metadata(&path).unwrap().len() <= 33554432);
    let loaded = Table::load(&path).unwrap();
    let repo = root.ancestors().nth(4).unwrap();
    let literal =
        repo.join("rust/rei_microphysics/tests/data/igm_grackle/grackle_literal_reference.csv");
    let samples = [
        repo.join("research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/ZERO/history.csv.complete_prefix"),
        repo.join("research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/SHEAR_PLUS/history.csv.complete_prefix"),
    ];
    let executable = Path::new(env!("CARGO_BIN_EXE_axbi_temperature_rate_table_benchmark"));
    assert!(
        executable.is_file(),
        "normal release benchmark executable missing"
    );
    let r = validate(
        &loaded,
        &literal,
        &[samples[0].as_path(), samples[1].as_path()],
    )
    .unwrap();
    assert_eq!(r.invalid_rhs_cases, 13);
    assert!(
        r.direct <= 400000,
        "new direct-call allocation exceeded: {}",
        r.direct
    );
    assert!(
        r.lookups <= 350000,
        "new lookup allocation exceeded: {}",
        r.lookups
    );
    assert!(360926 + r.direct <= 2000000);
    assert!(295329 + r.lookups <= 8000000);
    let raw = root.join("gate_completion_001/raw");
    std::fs::write(
        raw.join("invalid_rhs.jsonl"),
        format!("{}\n", r.invalid_rhs_records.join("\n")),
    )
    .unwrap();
    std::fs::write(raw.join("local_test_counts.json"),format!("{{\"new_direct\":{},\"new_lookups\":{},\"new_fallback\":{},\"cumulative_direct\":{},\"cumulative_lookups\":{},\"rhs_cases\":{},\"invalid_rhs_cases\":{},\"slope_candidates\":{},\"slope_compared\":{},\"slope_skipped_guard\":{},\"slope_skipped_domain\":{},\"saved\":{}}}\n",r.direct,r.lookups,r.fallback,360926+r.direct,295329+r.lookups,r.rhs_cases,r.invalid_rhs_cases,r.slope_candidates,r.slopes,r.slope_skipped_guard,r.slope_skipped_domain,r.saved)).unwrap();
}
