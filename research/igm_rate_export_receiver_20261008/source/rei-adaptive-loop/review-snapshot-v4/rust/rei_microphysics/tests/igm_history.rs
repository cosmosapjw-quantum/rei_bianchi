use rei_microphysics::{igm_config::parse_config, igm_history::History};
const CFG: &str = include_str!("../../../configs/igm_manufactured_v1.cfg");
fn small() -> rei_microphysics::igm_config::HistoryConfig {
    parse_config(
        &CFG.replace("birth_panels=16", "birth_panels=2")
            .replace("energy_panels=2", "energy_panels=1"),
    )
    .unwrap()
}
#[test]
fn short_history_reaches_endpoint_and_closes_ledgers() {
    let c = small();
    let (h, s) = History::new(c.clone()).unwrap();
    let q = h.advance_to(&s, c.end).unwrap();
    assert_eq!(q.ln_a, c.end);
    assert_eq!(q.birth_cursor, h.births.len());
    assert!(q.gas.fractions[1] > 0.0);
    let b = h.balances(&q).unwrap();
    assert!(b[0].abs() < 1e-10 * q.ledger.emitted_n);
    assert!(b[1].abs() < 1e-10 * q.ledger.emitted_e);
}
#[test]
fn gas_step_refinement_does_not_change_births_or_duplicate_emissions() {
    let mut c = small();
    let (h, s) = History::new(c.clone()).unwrap();
    c.max_dln_a *= 0.5;
    let (f, t) = History::new(c.clone()).unwrap();
    assert_eq!(h.births, f.births);
    let a = h.advance_to(&s, c.end).unwrap();
    let b = f.advance_to(&t, c.end).unwrap();
    assert_eq!(a.ledger.emitted_n, b.ledger.emitted_n);
    assert_eq!(a.birth_cursor, b.birth_cursor);
}
#[test]
fn immutable_failure_preserves_accepted_state_and_birth_cursor() {
    let mut c = small();
    c.max_steps = 1;
    let (h, s) = History::new(c.clone()).unwrap();
    assert!(h.advance_to(&s, c.end).is_err());
    assert_eq!(s.ln_a, c.start);
    assert_eq!(s.birth_cursor, 0);
    assert_eq!(s.ledger.emitted_n, 0.0);
    assert!(s.packets.is_empty());
}
#[test]
fn zero_source_zero_electrons_adiabatic_first_order_converges() {
    let mut errors = vec![];
    for dx in [2e-3, 1e-3, 5e-4] {
        let mut c = small();
        c.source.photons_per_h_per_s = 0.0;
        c.fractions = [0.0; 3];
        c.max_dln_a = dx;
        let (h, s) = History::new(c.clone()).unwrap();
        let q = h.advance_to(&s, c.end).unwrap();
        let exact = s.gas.w_erg_per_h * (-2.0 * (c.end - c.start)).exp();
        errors.push((q.gas.w_erg_per_h / exact - 1.0).abs());
        assert_eq!(q.gas.fractions, [0.0; 3]);
        assert!(q.packets.is_empty());
    }
    assert!(errors[0] / errors[1] > 1.8);
    assert!(errors[1] / errors[2] > 1.8);
}

#[test]
fn lower_cutoff_crossing_exports_survivors_with_closed_budget() {
    let mut c = small();
    c.source.energy_max_ev = 13.8;
    let (h, s) = History::new(c.clone()).unwrap();
    let q = h.advance_to(&s, c.end).unwrap();
    assert!(q.ledger.out_n > 0.0);
    let b = h.balances(&q).unwrap();
    assert!(b[0].abs() < 1e-10 * q.ledger.emitted_n);
    assert!(b[1].abs() < 1e-10 * q.ledger.emitted_e);
}
#[test]
fn born_subcutoff_packets_are_immediate_outflow() {
    let mut c = small();
    c.source.energy_min_ev = 10.0;
    c.source.energy_max_ev = 12.0;
    let (h, s) = History::new(c.clone()).unwrap();
    let q = h.advance_to(&s, c.end).unwrap();
    assert!(q.packets.is_empty());
    assert_eq!(q.ledger.out_n, q.ledger.emitted_n);
    assert_eq!(q.ledger.out_e, q.ledger.emitted_e);
}
#[test]
fn extinguished_packet_identity_and_log_weight_survive() {
    let c = small();
    let (h, s) = History::new(c.clone()).unwrap();
    let q = h.advance_to(&s, c.end).unwrap();
    assert!(q
        .packets
        .iter()
        .any(|p| p.log_per_h < f64::MIN_POSITIVE.ln()));
    assert!(q.packets.iter().all(|p| p.log_per_h.is_finite()));
    assert!(q.ledger.underflow_n_bound > 0.0 && q.ledger.underflow_n_bound < 1e-20);
    assert!(q.ledger.underflow_e_bound > 0.0 && q.ledger.underflow_e_bound < 1e-30);
}
