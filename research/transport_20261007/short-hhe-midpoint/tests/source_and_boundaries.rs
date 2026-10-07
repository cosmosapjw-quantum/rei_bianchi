use rei_microphysics::{
    igm_config::{parse_config, HistoryConfig},
    igm_state::IgmGasState,
};
use short_hhe_control::{diagnostics, material, radiation, v2};
fn fixture() -> HistoryConfig {
    parse_config(include_str!(
        "../../../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg"
    ))
    .unwrap()
}
fn gas(c: &HistoryConfig, x: [f64; 3]) -> [f64; 4] {
    let p = c.background.at_ln_a(c.start).unwrap();
    material::values(&IgmGasState::from_temperature(x, p.n_h_cm3, p.n_he_cm3, 300.).unwrap())
}
fn integrate<F: Fn(f64) -> f64>(f: F, a: f64, b: f64) -> f64 {
    let n = 256;
    let h = (b - a) / n as f64;
    let mut s = f(a) + f(b);
    for i in 1..n {
        s += if i % 2 == 0 { 2. } else { 4. } * f(a + i as f64 * h);
    }
    s * h / 3.
}
#[test]
fn actual_source_background_smooth_and_nonsymmetric_events_local3() {
    let cfg = fixture();
    let y = gas(&cfg, [1., 0., 1.]);
    for mode in ["smooth", "entry", "exit"] {
        let mut en = vec![];
        let mut ee = vec![];
        for h in [0.08, 0.04, 0.02, 0.01] {
            let s0 = cfg.start;
            let s1 = s0 + h;
            let event = s0 + h / 3.;
            let eta = match mode {
                "entry" => event + cfg.source.energy_max_ev.ln(),
                "exit" => event + cfg.source.energy_min_ev.ln(),
                _ => s0 + 50f64.ln(),
            };
            let a = s0.max(eta - cfg.source.energy_max_ev.ln());
            let b = s1.min(eta - cfg.source.energy_min_ev.ln());
            let q = |s: f64| {
                cfg.source.photons_per_h_per_s
                    / ((1. / cfg.source.energy_min_ev - 1. / cfg.source.energy_max_ev)
                        * (eta - s).exp()
                        * cfg.background.at_ln_a(s).unwrap().hubble_per_s)
            };
            let on = integrate(q, a, b);
            let oe = integrate(|s| q(s) * v2::EPS * (eta - s).exp(), a, b);
            let o = radiation::characteristic_path(&cfg, y, y, eta, s0, s1, 0.).unwrap();
            en.push((o.qn - on).abs());
            ee.push((o.qe - oe).abs());
            println!(
                "SOURCE mode={mode} h={h:e} N_error={:.17e} E_error={:.17e}",
                en.last().unwrap(),
                ee.last().unwrap()
            );
            let nn = o.n + o.outn;
            assert!((nn - o.qn).abs() < 2e-12 * o.qn);
            assert!((o.u + o.oute + o.red - o.qe).abs() < 2e-12 * o.qe);
        }
        for e in [en, ee] {
            let p = (e[2] / e[3]).log2();
            assert!(p > 2.8 && p < 3.2, "{mode}: p={p}");
        }
    }
}
#[test]
fn actual_cross_transaction_energy_and_cutoff_outflow() {
    let cfg = fixture();
    let y = gas(&cfg, [0.1, 0.2, 0.1]);
    let h = cfg.max_dln_a;
    let s0 = cfg.start;
    for energy in [13.6f64, 24.59, 54.42, 13.7, 100.] {
        let eta = s0 + h / 3. + energy.ln();
        let event = eta - energy.ln();
        let cuts = [s0, s0 + h / 7., event, s0 + 2. * h / 3., s0 + h];
        let initial_n = if energy == 100. { 0. } else { 1e-5 };
        let mut stock = initial_n;
        let mut nsum = 0.;
        let mut esum = 0.;
        let mut qn = 0.;
        let mut qe = 0.;
        let initial = v2::EPS * (eta - s0).exp() * stock;
        let mut last_u = initial;
        for ab in cuts.windows(2) {
            diagnostics::reset();
            let o = radiation::characteristic_path(&cfg, y, y, eta, ab[0], ab[1], stock).unwrap();
            let begin = v2::EPS * (eta - ab[0]).exp() * stock;
            let rel = if begin == 0. {
                0.
            } else {
                (last_u - begin).abs() / begin
            };
            assert!(rel <= 2e-12);
            let t = diagnostics::snapshot();
            assert!(t.continuity_max_relative <= 2e-12);
            println!(
                "BOUNDARY energy={energy} end={:.17e} relative={:.17e} observed={:.17e}",
                ab[1], rel, t.continuity_max_relative
            );
            stock = o.n;
            last_u = o.u;
            nsum += o.outn + o.an.iter().sum::<f64>();
            esum += o.oute + o.be.iter().sum::<f64>() + o.red;
            qn += o.qn;
            qe += o.qe;
        }
        assert!((stock + nsum - initial_n - qn).abs() < 2e-12 * (initial_n + qn));
        assert!((last_u + esum - initial - qe).abs() < 2e-12 * (initial + qe));
        if energy == 13.6 {
            assert_eq!(stock, 0.);
            assert_eq!(last_u, 0.);
        }
    }
}
