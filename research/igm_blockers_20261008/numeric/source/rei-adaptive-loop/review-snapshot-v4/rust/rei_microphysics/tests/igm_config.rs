use rei_microphysics::igm_config::parse_config;
const TEXT: &str = include_str!("../../../configs/igm_manufactured_v1.cfg");
#[test]
fn explicit_manufactured_config_parses_and_preflights_actual_eos() {
    let c = parse_config(TEXT).unwrap();
    assert_eq!(c.source.photons_per_h_per_s, 1e-15);
    assert_eq!(c.fractions, [2e-4, 0.0, 0.0]);
    assert_eq!(c.temperature_k, 30.0);
    assert_eq!(c.birth_panels, 16);
}
#[test]
fn missing_duplicate_unknown_and_invalid_inputs_reject() {
    for t in [
        TEXT.replace("temperature_k=30\n", ""),
        format!("{TEXT}\nx_hii=0.1"),
        format!("{TEXT}\nunknown=2"),
        TEXT.replace("temperature_k=30", "temperature_k=0.9"),
        TEXT.replace("birth_panels=16", "birth_panels=0"),
        TEXT.replace("source_rate=1e-15", "source_rate=NaN"),
    ] {
        assert!(parse_config(&t).is_err());
    }
}
#[test]
fn resource_bound_precedes_energy_node_allocation() {
    let t = TEXT.replace("energy_panels=2", "energy_panels=1000000000");
    assert!(parse_config(&t).is_err());
}
