use rei_microphysics::{igm_config::parse_config, igm_continuous::ContinuousHistory as History};
const CFG: &str = include_str!("../../../configs/igm_manufactured_v1.cfg");
#[test]
fn continuous_source_emits_before_first_legacy_birth() {
    let c = parse_config(CFG).unwrap();
    let end = c.start + 1e-7;
    let (h, s) = History::new(c, 32).unwrap();
    let q = h.advance_to(&s, end).unwrap();
    assert!(
        q.ledger.emitted_n > 0.0,
        "continuous proper emissivity must act immediately, without waiting for a birth grid node"
    );
}

#[test]
fn nodes_cover_full_source_union_and_future_nodes_start_empty() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = History::new(c.clone(), 64).unwrap();
    assert_eq!(h.nodes.len(), 128);
    let i = h
        .nodes
        .iter()
        .position(|n| {
            let e = n.eta - c.source.energy_max_ev.ln();
            e > c.start && e < c.end
        })
        .unwrap();
    let entry = h.nodes[i].eta - c.source.energy_max_ev.ln();
    assert_eq!(s.counts[i], 0.0);
    assert_eq!(h.source_rate(i, c.start), 0.0);
    let before = h.advance_to(&s, entry).unwrap();
    assert_eq!(before.counts[i], 0.0);
    let after = h.advance_to(&before, (entry + 1e-7).min(c.end)).unwrap();
    assert!(after.counts[i] > 0.0);
    assert!(after.log_counts[i].is_finite());
}

#[test]
fn full_continuous_history_closes_budgets_with_bounded_fixed_node_count() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = History::new(c.clone(), 32).unwrap();
    let q = h.advance_to(&s, c.end).unwrap();
    assert_eq!(q.ln_a, c.end);
    assert_eq!(q.counts.len(), 64);
    assert!(q.gas.fractions[1] > 0.0);
    let b = h.balances(&q).unwrap();
    assert!(b[0].abs() <= 1e-10 * q.ledger.emitted_n.max(1e-10));
    assert!(
        b[1].abs()
            <= 1e-10
                * (q.ledger.emitted_e + q.ledger.work_e + q.ledger.escape_e + q.ledger.cmb_abs_e)
                    .max(1e-20)
    );
    assert!(q.ledger.underflow_n_bound <= 1e-20 && q.ledger.underflow_e_bound <= 1e-30);
}

#[test]
fn cutoff_export_is_owned_by_exact_event_identity() {
    use rei_microphysics::{verner_cutoff_ev, Absorber};
    let mut c = parse_config(CFG).unwrap();
    c.source.energy_max_ev = 13.8;
    let (h, s) = History::new(c.clone(), 8).unwrap();
    let cutoff = verner_cutoff_ev(Absorber::HI);
    let i = h
        .nodes
        .iter()
        .position(|n| {
            let cross = n.eta - cutoff.ln();
            cross > c.start && cross < c.end
        })
        .unwrap();
    let cross = h.nodes[i].eta - cutoff.ln();
    assert_eq!(h.energy(i, cross), cutoff);
    let q = h.advance_to(&s, cross).unwrap();
    assert_eq!(q.counts[i], 0.0);
    assert!(q.ledger.out_n > 0.0 && q.ledger.out_e > 0.0);
    let b = h.balances(&q).unwrap();
    assert!(b[0].abs() < 1e-10 * q.ledger.emitted_n.max(1e-10));
    assert!(b[1].abs() < 1e-10 * q.ledger.emitted_e.max(1e-20));
}

#[test]
fn subcutoff_source_is_continuous_immediate_outflow() {
    let mut c = parse_config(CFG).unwrap();
    c.source.energy_min_ev = 10.0;
    c.source.energy_max_ev = 12.0;
    let (h, s) = History::new(c.clone(), 16).unwrap();
    let q = h.advance_to(&s, c.end).unwrap();
    assert!(q.counts.iter().all(|n| *n == 0.0));
    assert!(q.ledger.emitted_n > 0.0);
    assert_eq!(q.ledger.emitted_n, q.ledger.out_n);
    assert_eq!(q.ledger.emitted_e, q.ledger.out_e);
    assert_eq!(q.ledger.redshift_e, 0.0);
}

#[test]
fn source_clock_midpoint_converges_to_exact_matter_only_node_integral() {
    let text = CFG
        .replace("omega_r=9e-5", "omega_r=0")
        .replace("omega_m=0.3", "omega_m=1")
        .replace("omega_lambda=0.69991", "omega_lambda=0");
    let mut errors = Vec::new();
    for dx in [2e-4, 1e-4] {
        let mut c = parse_config(&text).unwrap();
        c.max_dln_a = dx;
        let (h, s) = History::new(c.clone(), 16).unwrap();
        let q = h.advance_to(&s, c.end).unwrap();
        let norm = 1.0 / c.source.energy_min_ev - 1.0 / c.source.energy_max_ev;
        let mut exact = 0.0;
        for n in &h.nodes {
            let a = c.start.max(n.eta - c.source.energy_max_ev.ln());
            let b = c.end.min(n.eta - c.source.energy_min_ev.ln());
            if b > a {
                exact += c.source.photons_per_h_per_s * n.weight / norm
                    * (-n.eta).exp()
                    * ((2.5 * b).exp() - (2.5 * a).exp())
                    / (2.5 * 2.2e-18);
            }
        }
        errors.push((q.ledger.emitted_n - exact).abs());
    }
    assert!(
        errors[0] / errors[1] > 3.5,
        "midpoint clock errors {errors:?}"
    );
}

#[test]
fn zero_source_neutral_adiabatic_history_remains_first_order() {
    let mut errors = Vec::new();
    for dx in [2e-3, 1e-3, 5e-4] {
        let mut c = parse_config(CFG).unwrap();
        c.source.photons_per_h_per_s = 0.0;
        c.fractions = [0.0; 3];
        c.max_dln_a = dx;
        let (h, s) = History::new(c.clone(), 8).unwrap();
        let q = h.advance_to(&s, c.end).unwrap();
        assert_eq!(q.gas.fractions, [0.0; 3]);
        assert!(q.counts.iter().all(|n| *n == 0.0));
        let exact = s.gas.w_erg_per_h * (-2.0 * (c.end - c.start)).exp();
        errors.push((q.gas.w_erg_per_h / exact - 1.0).abs());
    }
    assert!(
        errors[0] / errors[1] > 1.7 && errors[1] / errors[2] > 1.7,
        "{errors:?}"
    );
}

#[test]
fn rejection_keeps_state_immutable_and_resource_limits_are_strict() {
    let mut c = parse_config(CFG).unwrap();
    assert!(History::new(c.clone(), 0).is_err());
    assert!(History::new(c.clone(), c.max_packets).is_err());
    c.max_steps = 1;
    let (h, s) = History::new(c.clone(), 8).unwrap();
    let before = format!("{s:?}");
    assert!(h.advance_to(&s, c.end).is_err());
    assert_eq!(before, format!("{s:?}"));
}

#[test]
fn endpoint_photo_is_right_sided_at_exact_helium_cutoff() {
    use rei_microphysics::{verner_cutoff_ev, Absorber};
    let c = parse_config(CFG).unwrap();
    let (h, mut s) = History::new(c.clone(), 64).unwrap();
    let cutoff = verner_cutoff_ev(Absorber::HeII);
    let i = h
        .nodes
        .iter()
        .position(|n| {
            let t = n.eta - cutoff.ln();
            t > c.start && t < c.end
        })
        .unwrap();
    s.ln_a = h.nodes[i].eta - cutoff.ln();
    s.counts[i] = 1.0;
    s.log_counts[i] = 0.0;
    let photo = h.endpoint_photo(&s).unwrap();
    assert_eq!(
        photo.input.gamma_s[2], 0.0,
        "post-event HeII channel must be inactive at its exact crossing"
    );
    assert!(photo.input.gamma_s[0] > 0.0 && photo.input.gamma_s[1] > 0.0);
}

#[test]
fn malformed_nan_state_time_cannot_report_success() {
    let c = parse_config(CFG).unwrap();
    let (h, mut s) = History::new(c.clone(), 8).unwrap();
    s.ln_a = f64::NAN;
    assert!(h.advance_to(&s, c.end).is_err());
}

#[test]
fn threshold_band_quadrature_resolves_swept_edges_with_exact_log_moments() {
    use rei_microphysics::{igm_continuous::SpectralGrid, verner_cutoff_ev, Absorber};
    let c = parse_config(CFG).unwrap();
    let panels = 3;
    let (h, _) = History::new_with_grid(c.clone(), panels, SpectralGrid::ThresholdBands).unwrap();
    let lo = c.start + c.source.energy_min_ev.ln();
    let hi = c.end + c.source.energy_max_ev.ln();
    let mut edges = vec![lo, hi];
    for e in [
        c.source.energy_min_ev,
        c.source.energy_max_ev,
        verner_cutoff_ev(Absorber::HI),
        verner_cutoff_ev(Absorber::HeI),
        verner_cutoff_ev(Absorber::HeII),
    ] {
        for epoch in [c.start, c.end] {
            let v = epoch + e.ln();
            if lo < v && v < hi {
                edges.push(v);
            }
        }
    }
    edges.sort_by(f64::total_cmp);
    edges.dedup();
    assert_eq!(h.nodes.len(), 2 * panels * (edges.len() - 1));
    for band in edges.windows(2) {
        let nodes: Vec<_> = h
            .nodes
            .iter()
            .filter(|n| band[0] < n.eta && n.eta < band[1])
            .collect();
        assert_eq!(nodes.len(), 2 * panels);
        for power in 0..=3 {
            let value = nodes
                .iter()
                .map(|n| n.weight * n.eta.powi(power))
                .sum::<f64>();
            let exact = (band[1].powi(power + 1) - band[0].powi(power + 1)) / (power + 1) as f64;
            assert!((value - exact).abs() < 2e-14 * (band[1] - band[0]).max(exact.abs()));
        }
    }
    let mut limited = c;
    limited.max_packets = 2 * panels;
    assert!(History::new_with_grid(limited, panels, SpectralGrid::ThresholdBands).is_err());
}

#[test]
fn adjacent_representable_events_are_integrated_without_merging_or_losing_source() {
    use rei_microphysics::igm_continuous::SpectralGrid;
    let c = parse_config(CFG).unwrap();
    for panels in [3, 8] {
        let (h, s) =
            History::new_with_grid(c.clone(), panels, SpectralGrid::ThresholdBands).unwrap();
        assert!(h
            .events
            .windows(2)
            .any(|e| e[0] + 0.5 * (e[1] - e[0]) == e[0] || e[0] + 0.5 * (e[1] - e[0]) == e[1]));
        let q = h.advance_to(&s, c.end).expect(
            "positive-width adjacent-float intervals must be integrated, not merged or skipped",
        );
        assert_eq!(q.ln_a, c.end);
        let residual = h.balances(&q).unwrap();
        assert!(residual[0].abs() <= 1e-10 * q.ledger.emitted_n.max(1e-10));
        assert!(
            residual[1].abs()
                <= 1e-10
                    * (q.ledger.emitted_e
                        + q.ledger.escape_e
                        + q.ledger.work_e
                        + q.ledger.cmb_abs_e)
                        .max(1e-20)
        );
    }
}
