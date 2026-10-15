use rei_microphysics::axbi_driver::{guard_output_bytes_with_limit, DriverConfig};
use std::{
    fs,
    time::{SystemTime, UNIX_EPOCH},
};
const MIB: u64 = 1024 * 1024;
#[test]
fn explicit_allocations_preserve_old_reserves_and_add_twelve_gib_only() {
    assert_eq!(DriverConfig::baseline().output_budget_mib, 256);
    for (total, science, reserve) in [
        (256, 224, 32),
        (2048, 1920, 128),
        (4096, 3968, 128),
        (12288, 12160, 128),
    ] {
        let config = DriverConfig::read(&format!("output_budget_mib={total}\n")).unwrap();
        assert_eq!(
            config.scientific_output_budget_bytes().unwrap(),
            science * MIB
        );
        assert_eq!(config.launcher_reserve_bytes().unwrap(), reserve * MIB);
        assert_eq!(
            config.scientific_output_budget_bytes().unwrap()
                + config.launcher_reserve_bytes().unwrap(),
            total as u64 * MIB
        );
        // Allocation leaves all numerical controls at their exact baseline values.
        let mut restored = config.clone();
        restored.output_budget_mib = 256;
        assert_eq!(
            format!("{restored:?}"),
            format!("{:?}", DriverConfig::baseline())
        );
    }
}
#[test]
fn unsupported_and_malformed_allocations_remain_rejected() {
    for value in [
        "0",
        "128",
        "255",
        "257",
        "1024",
        "4097",
        "8192",
        "12287",
        "12289",
        "16384",
        "18446744073709551615",
        "-1",
        "NaN",
        "12288.0",
    ] {
        assert!(
            DriverConfig::read(&format!("output_budget_mib={value}\n")).is_err(),
            "value {value}"
        );
    }
    let mut manual = DriverConfig::baseline();
    manual.output_budget_mib = 8192;
    assert!(manual.scientific_output_budget_bytes().is_err());
    assert!(manual.launcher_reserve_bytes().is_err());
}
#[test]
fn existing_recursive_guard_enforces_new_scientific_boundary_and_keeps_old_cap() {
    let path = std::env::temp_dir().join(format!(
        "rei_output005_{}_{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir(&path).unwrap();
    fs::create_dir(path.join("checkpoints")).unwrap();
    fs::write(path.join("checkpoints/tiny"), b"123").unwrap();
    let new = DriverConfig::read("output_budget_mib=12288\n").unwrap();
    let old = DriverConfig::read("output_budget_mib=4096\n").unwrap();
    let limit = new.scientific_output_budget_bytes().unwrap();
    assert!(guard_output_bytes_with_limit(&path, limit - 3, limit).is_ok());
    assert!(guard_output_bytes_with_limit(&path, limit - 2, limit).is_err());
    assert!(guard_output_bytes_with_limit(&path, 8 * 1024 * MIB, limit).is_ok());
    assert!(guard_output_bytes_with_limit(
        &path,
        8 * 1024 * MIB,
        old.scientific_output_budget_bytes().unwrap()
    )
    .is_err());
    assert!(guard_output_bytes_with_limit(&path, u64::MAX, limit).is_err());
    fs::remove_dir_all(path).unwrap();
}
