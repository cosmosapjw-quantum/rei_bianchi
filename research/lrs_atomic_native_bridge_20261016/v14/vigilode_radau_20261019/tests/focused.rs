use rei_microphysics::{HHeModel, axbi_driver::PhysicalBirthRule, igm_state::w_erg_per_h_to_ev};
use rei_vigilode_radau_research::*;
fn close(a: f64, b: f64, rel: f64) {
    assert!(
        (a - b).abs() <= rel * a.abs().max(b.abs()).max(1e-290),
        "{a:e} != {b:e}"
    );
}
#[test]
fn direct_native_source_node_identities() {
    let (d, s, _) = initial(true).unwrap();
    let g = d.geometry_point(s.a).unwrap().geometry().unwrap();
    let p = photon(&s);
    let prepared = d.transport.prepare(&p, &g).unwrap();
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    let r = prepared
        .native_rates([nh * 0.925, nhe * 0.85, nhe * 0.12], nh)
        .unwrap();
    let fe = prepared
        .evaluate_forward_euler([nh * 0.925, nhe * 0.85, nhe * 0.12], nh, 0.)
        .unwrap();
    for j in 0..3 {
        close(r.photo.gamma_s[j], fe.photo.gamma_s[j], 1e-14);
        close(
            r.photo.heat_erg_per_absorber_s[j],
            fe.photo.heat_erg_per_absorber_s[j],
            1e-14,
        );
    }
    close(
        -r.number_dt.iter().sum::<f64>(),
        r.absorbed_per_h_s.iter().sum(),
        1e-14,
    );
    let rays = d.transport.ray_geometry(&g).unwrap();
    let du = r
        .energy_ref_dt
        .iter()
        .enumerate()
        .map(|(k, u)| -u * rays[k / d.transport.n_energy()].scale)
        .sum::<f64>();
    close(du, r.binding_ev_per_h_s + r.heat_ev_per_h_s, 2e-14);
    let point = rei_microphysics::axbi_rates::AxbiProvider
        .point(&s.gas, nh, nhe, 0., 2.7255 / s.a, r.photo)
        .unwrap();
    for j in 0..3 {
        close(
            point.rhs.photo_events_cm3_s[j] / nh,
            r.absorbed_per_h_s[j],
            2e-14,
        );
    }
    close(
        point.rhs.photo_input_erg_cm3_s / nh / HHeModel::controlled_fixture().ev_erg,
        r.binding_ev_per_h_s + r.heat_ev_per_h_s,
        2e-14,
    );
}
#[test]
fn affine_roundtrip_empty_point_and_extended_support() {
    let (d, s, _) = initial(true).unwrap();
    let p = photon(&s);
    let c = Coordinates::new(&p, &s.gas).unwrap();
    let y = c.encode(&p, &s.gas).unwrap();
    let (q, g) = c.decode(&y).unwrap();
    d.transport.validate_state(&q).unwrap();
    for k in 0..p.number.len() {
        close(q.number[k], p.number[k], 2e-15);
        close(q.energy_ref[k], p.energy_ref[k], 2e-15);
    }
    close(w_erg_per_h_to_ev(g.w_erg_per_h).unwrap(), c.wscale, 1e-15);
    let empty = d.transport.empty_state();
    let ce = Coordinates::new(&empty, &s.gas).unwrap();
    assert_eq!(ce.dimension, 4);
    assert_eq!(
        ce.decode(&ce.encode(&empty, &s.gas).unwrap()).unwrap().0,
        empty
    );
    let mut point = empty;
    d.transport.add_delta(&mut point, 0, 20., 0.5).unwrap();
    let cp = Coordinates::new(&point, &s.gas).unwrap();
    assert_eq!(cp.dimension, 5);
    assert!(cp.cells[0].offset_index.is_none());
    let decoded = cp.decode(&cp.encode(&point, &s.gas).unwrap()).unwrap().0;
    assert_eq!(decoded, point);
}
#[test]
fn failed_native_candidate_is_transactional() {
    let (d, mut s, k) = initial(true).unwrap();
    let before = state_json(&d, &s).unwrap();
    let budget = Budget::new(1, 30.);
    let e = chemical_step(&d, &mut s, 1. / (4. * k), 1e-13, budget.clone()).unwrap_err();
    assert!(e.contains("NATIVE_RHS_CAP"), "{e}");
    assert_eq!(budget.calls(), 1);
    let after = state_json(&d, &s).unwrap();
    for key in [
        "a",
        "fractions",
        "w_ev",
        "number",
        "energy_ref",
        "support_lo",
        "support_hi",
        "ledgers",
        "accepted",
    ] {
        assert_eq!(before[key], after[key], "{key}");
    }
    assert_eq!(s.attempts, 1);
    assert_eq!(s.rhs_evaluations, 1);
}
#[test]
fn public_gl2_birth_clock_algebra() {
    let (d, s, _) = initial(false).unwrap();
    let a0 = s.a;
    let dx = 1e-6_f64;
    let end = a0 * dx.exp();
    let mut old = a0;
    for (c, w) in PhysicalBirthRule::Gauss2.nodes() {
        let a = a0 * (c * dx).exp();
        assert!(a > old && a < end);
        let mid = (old * a).sqrt();
        let dt = ((a - old) / old).ln_1p() / d.geometry_point(mid).unwrap().h_flrw_per_s;
        assert!(dt > 0.);
        let proper = dx * w / d.geometry_point(a).unwrap().h_flrw_per_s;
        assert!(proper > 0.);
        old = a;
    }
    assert_eq!(
        PhysicalBirthRule::Gauss2.nodes(),
        PhysicalBirthRule::DisabledGauss2.nodes()
    );
}

#[test]
fn actual_radau_stage_reconstruction_and_common_event_quadrature() {
    let (d, mut s, k) = initial(true).unwrap();
    let before = s.clone();
    let coordinates = Coordinates::new(&photon(&before), &before.gas).unwrap();
    let y0 = coordinates.encode(&photon(&before), &before.gas).unwrap();
    let budget = Budget::new(200000, 30.);
    let dt = 1. / (64. * k);
    let report = chemical_step(&d, &mut s, dt, 1e-13, budget.clone()).unwrap();
    let (a, b, _) = rodas5p_integrators::radau_iia3_tableau();
    let ynew = coordinates.encode(&photon(&s), &s.gas).unwrap();
    for i in 0..3 {
        assert!(b[i] > 0.);
        for component in 0..y0.len() {
            let expected = y0[component]
                + (0..3)
                    .map(|j| a[(i, j)] * report.stages[j].increments[component])
                    .sum::<f64>();
            close(report.stages[i].scaled_state[component], expected, 4e-15);
        }
        for j in 0..3 {
            close(
                report.stages[i].events_per_h_s.p[j],
                report.stages[i].node_photo_per_h_s[j],
                3e-14,
            );
        }
        close(
            report.stages[i].events_per_h_s.photo_binding,
            report.stages[i].node_binding_ev_per_h_s,
            3e-14,
        );
        close(
            report.stages[i].events_per_h_s.photo_heat,
            report.stages[i].node_heat_ev_per_h_s,
            3e-14,
        );
    }
    for component in 0..y0.len() {
        let expected = y0[component]
            + (0..3)
                .map(|j| b[j] * report.stages[j].increments[component])
                .sum::<f64>();
        close(ynew[component], expected, 4e-15);
    }
    for j in 0..3 {
        let expected = dt
            * (0..3)
                .map(|i| b[i] * report.stages[i].events_per_h_s.p[j])
                .sum::<f64>();
        close(report.integrated.p[j], expected, 3e-15);
        close(
            s.ledgers.photo_events[j] - before.ledgers.photo_events[j],
            expected,
            3e-15,
        );
    }
    assert!(report.max_scaled_stage_residual < 1.);
    assert!(report.max_scaled_endpoint_closure < 1.);
    assert!(
        report
            .affine_identity_mismatch
            .iter()
            .all(|x| x.abs() < 2e-14)
    );
    println!(
        "NATIVE_TEST Radau-stage-replay native_rhs_attempts={}",
        budget.calls()
    );
    assert_eq!(budget.calls(), report.native_rhs_calls);
    assert!(report.native_rhs_calls > report.work["rhs_evaluations"].as_u64().unwrap() as usize);
}

#[test]
fn actual_gl2_birth_clock_and_injection_parity_with_native_ssprk() {
    let (d, mut radau, _) = initial(false).unwrap();
    let (_, mut ssprk, _) = initial(false).unwrap();
    let a0 = radau.a;
    let to = a0 * (1e-10_f64).exp();
    let dx = ((to - a0) / a0).ln_1p();
    let budget = Budget::new(200000, 30.);
    let r = birth_step(
        &d,
        &mut radau,
        to,
        PhysicalBirthRule::Gauss2,
        1e-13,
        budget.clone(),
    )
    .unwrap();
    let s = d
        .fixed_step_physical_birth_ssprk2(&mut ssprk, dx, PhysicalBirthRule::Gauss2)
        .unwrap();
    println!(
        "NATIVE_TEST GL2-parity radau_native_rhs_attempts={} ssprk_native_rhs_attempts={}",
        budget.calls(),
        ssprk.rhs_evaluations
    );
    assert_eq!(r.births.len(), s.birth.births.len());
    assert_eq!(r.segments.len(), s.birth.segments.len());
    assert_eq!(radau.a, to);
    for (rb, sb) in r.births.iter().zip(&s.birth.births) {
        close(rb.a, sb.a, 3e-15);
        close(rb.weight_dln_a, sb.weight_dln_a, 3e-15);
        close(rb.proper_time_weight_s, sb.proper_time_weight_s, 3e-15);
        close(rb.added_n, sb.added_photons_per_h, 3e-14);
        close(rb.added_u, sb.added_energy_ev_per_h, 3e-14);
    }
    for (rs, ss) in r.segments.iter().zip(&s.birth.segments) {
        close(rs.begin, ss.a_begin, 3e-15);
        close(rs.midpoint, ss.a_mid, 3e-15);
        close(rs.end, ss.a_end, 3e-15);
        close(rs.chemical.dt_s, ss.dt_s, 3e-15);
    }
}
