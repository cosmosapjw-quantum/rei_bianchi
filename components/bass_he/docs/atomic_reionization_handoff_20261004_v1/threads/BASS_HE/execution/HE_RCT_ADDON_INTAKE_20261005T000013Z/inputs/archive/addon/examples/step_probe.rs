use bass_he_rct_step_addon::*;
use rei_microphysics::he_rct::*;
use rei_microphysics::*;
fn state(s: HHeState) -> String {
    format!(
        "[{:e},{:e},{:e},{:e},{:e},{:e},{:e},{:e}]",
        s.fractions[0],
        s.fractions[1],
        s.fractions[2],
        s.u_erg_cm3,
        s.photon_cm3[0],
        s.photon_cm3[1],
        s.photon_cm3[2],
        s.escaped_erg_cm3
    )
}
fn main() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let c = StepControl::default();
    let g = &m.gas;
    println!("{{\"kind\":\"model\",\"nh\":{:e},\"nhe\":{:e},\"c\":{:e},\"kb\":{:e},\"ev\":{:e},\"chi\":{:?},\"energy\":{:?},\"sigma\":{:?},\"initial\":{}}}",g.n_h_cm3,g.n_he_cm3,g.c_cm_s,g.kb_erg_k,g.ev_erg,g.threshold_ev,g.photon_energy_ev,g.sigma_cm2,state(s));
    for dt in [1e8, 1e9, 1e10, 1e11] {
        for offset in [-1., 0., 1.] {
            let provider = RctProvider::new(
                RctSource::Kf96Nominal,
                RctScenario::W82GroundStateCommonTemperatureZeroDrift,
                true,
            )
            .unwrap();
            let energy = g.threshold_ev[2] - g.threshold_ev[0] + offset;
            let sel = RctSelection::Escaping {
                provider,
                closure: EscapingMeanPhotonEnergy::research_input_ev(energy).unwrap(),
            };
            let full = implicit_step(&m, &s, dt, c, sel).unwrap();
            let a = implicit_step(&m, &s, dt / 2., c, sel).unwrap();
            let b = implicit_step(&m, &a.state, dt / 2., c, sel).unwrap();
            let jfull = full.rct.unwrap().events;
            let jhalf = a.rct.unwrap().events + b.rct.unwrap().events;
            let local = (g.temperature(&full.state).unwrap().ln()
                - g.temperature(&b.state).unwrap().ln())
            .abs()
            .max(
                (0..3)
                    .map(|i| (full.state.fractions[i] - b.state.fractions[i]).abs())
                    .fold(0_f64, f64::max),
            );
            let defect = (jfull - jhalf).abs() / g.n_h_cm3;
            let allowed = 1e-14 + 2e-4 * jfull.max(jhalf) / g.n_h_cm3;
            let result = adaptive_step(
                &m,
                &s,
                dt,
                c,
                sel,
                EventControl {
                    absolute_per_h: 1e-14,
                    relative: 2e-4,
                },
            );
            let status = match result {
                Ok(_) => "ACCEPT",
                Err(ref e) => e.code(),
            };
            println!("{{\"kind\":\"step\",\"dt\":{:e},\"mean_ev\":{:e},\"k\":1e-14,\"full\":{},\"half1\":{},\"half2\":{},\"J_full\":{:e},\"J_half\":{:e},\"residual_norm\":{:e},\"iterations\":{},\"local_error\":{:e},\"event_defect_per_h\":{:e},\"event_allowed_per_h\":{:e},\"status\":\"{}\"}}",dt,energy,state(full.state),state(a.state),state(b.state),jfull,jhalf,full.residual_norm,full.iterations,local,defect,allowed,status);
        }
    }
}
