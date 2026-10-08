use rei_microphysics::coupled_primary::*;
use rei_microphysics::*;
fn init() -> (PrimaryStage, PrimaryState) {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    (
        PrimaryStage {
            n_h_cm3: 1e-4,
            f_he: 0.083,
            h_mean_per_s: 0.,
        },
        PrimaryState {
            fractions: s.fractions,
            w_ev_per_h: s.u_erg_cm3 / (m.gas.n_h_cm3 * m.gas.ev_erg),
            escape_ev_per_h: 0.,
            packets: vec![
                PrimaryPacket {
                    energy_ev: 13.7,
                    per_h: 0.05,
                },
                PrimaryPacket {
                    energy_ev: 35.,
                    per_h: 0.005,
                },
                PrimaryPacket {
                    energy_ev: 70.,
                    per_h: 0.001,
                },
            ],
        },
    )
}
fn control() -> StepControl {
    StepControl {
        max_iterations: 200,
        residual_tolerance: 1e-14,
    }
}
#[test]
fn identity_and_transaction() {
    let (g, mut s) = init();
    let x = primary_stage_step(&g, &s, 0., control()).unwrap();
    assert_eq!(x.state.fractions, s.fractions);
    assert_eq!(x.state.w_ev_per_h, s.w_ev_per_h);
    assert_eq!(x.state.packets[0].per_h, s.packets[0].per_h);
    let before = format!("{:?}", s);
    assert!(try_primary_stage_step(
        &g,
        &mut s,
        1e9,
        StepControl {
            max_iterations: 0,
            residual_tolerance: 1e-14
        }
    )
    .is_err());
    assert_eq!(before, format!("{:?}", s));
}
#[test]
fn positive_energy_and_owners() {
    let (g, s) = init();
    let q = primary_stage_step(&g, &s, 1e9, control()).unwrap();
    let f = g.f_he;
    let chi = [13.598434599702, 24.587389011, 54.41776];
    let energy = |v: &PrimaryState| {
        v.w_ev_per_h
            + chi[0] * v.fractions[0]
            + f * (chi[1] * v.fractions[1] + (chi[1] + chi[2]) * v.fractions[2])
            + v.escape_ev_per_h
            + v.packets.iter().map(|p| p.energy_ev * p.per_h).sum::<f64>()
    };
    assert!(
        (energy(&q.state) + q.events.thermal_work_ev_per_h - energy(&s)).abs() / energy(&s) < 1e-12
    );
    for k in 0..s.packets.len() {
        assert!(q.state.packets[k].per_h >= 0.);
        let loss = q.events.photo_per_h[k].iter().sum::<f64>();
        assert!(
            (s.packets[k].per_h - q.state.packets[k].per_h - loss).abs() / s.packets[k].per_h
                < 1e-12
        );
    }
    let a = primary_stage_step(&g, &s, 5e8, control()).unwrap();
    let b = primary_stage_step(&g, &a.state, 5e8, control()).unwrap();
    assert!((q.state.fractions[0] - b.state.fractions[0]).abs() < 2e-4);
}
#[test]
fn zero_photons_and_invalid_stage() {
    let (g, mut s) = init();
    for p in &mut s.packets {
        p.per_h = 0.;
    }
    let q = primary_stage_step(&g, &s, 1e9, control()).unwrap();
    assert!(q.state.packets.iter().all(|p| p.per_h == 0.));
    assert!(q
        .events
        .photo_per_h
        .iter()
        .all(|p| p.iter().all(|v| *v == 0.)));
    let bad = PrimaryStage {
        n_h_cm3: 1e-4,
        f_he: 0.083,
        h_mean_per_s: -1e-14,
    };
    assert!(primary_stage_step(&bad, &s, 1e9, control()).is_err());
}

#[test]
fn fixed_energy_gate_with_loose_control() {
    let (mut g, s) = init();
    g.h_mean_per_s = 1e-14;
    let q = primary_stage_step(
        &g,
        &s,
        1e9,
        StepControl {
            max_iterations: 200,
            residual_tolerance: 1e-4,
        },
    )
    .unwrap();
    let chi = [13.598434599702, 24.587389011, 54.41776];
    let energy = |v: &PrimaryState| {
        v.w_ev_per_h
            + chi[0] * v.fractions[0]
            + g.f_he * (chi[1] * v.fractions[1] + (chi[1] + chi[2]) * v.fractions[2])
            + v.escape_ev_per_h
            + v.packets.iter().map(|p| p.energy_ev * p.per_h).sum::<f64>()
    };
    assert!(
        (energy(&q.state) + q.events.thermal_work_ev_per_h - energy(&s)).abs() / energy(&s)
            <= 1e-12
    );
    assert!(q.iterations > 1);
}
#[test]
fn tiny_positive_photons_are_not_silently_lost() {
    let (g, mut s) = init();
    s.packets[0].per_h = f64::from_bits(1);
    let before = format!("{:?}", s);
    assert!(try_primary_stage_step(&g, &mut s, 1e9, control()).is_err());
    assert_eq!(before, format!("{:?}", s));
}
