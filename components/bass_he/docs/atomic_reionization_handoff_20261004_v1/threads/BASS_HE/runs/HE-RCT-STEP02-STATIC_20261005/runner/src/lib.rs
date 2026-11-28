//! Bounded static research caller. Original add-on and consumer stay unchanged.
use bass_he_rct_step_addon::{EventControl, RctIntegral, RctStep};
use rei_microphysics::he_rct::RctSelection;
use rei_microphysics::{ForwardError, Ft03Model, HHeState, StepControl};
#[derive(Clone, Copy, Debug)]
pub struct Control {
    pub end_s: f64,
    pub max_dt_s: f64,
    pub min_dt_s: f64,
    pub max_attempts: usize,
}
#[derive(Clone, Debug)]
pub struct Accepted {
    pub t: f64,
    pub dt: f64,
    pub step: RctStep,
}
#[derive(Clone, Debug)]
pub struct Rejected {
    pub t: f64,
    pub dt: f64,
    pub code: &'static str,
    pub unchanged: bool,
}
#[derive(Clone, Debug)]
pub struct History {
    pub state: HHeState,
    pub rct_total: RctIntegral,
    pub accepted: Vec<Accepted>,
    pub rejected: Vec<Rejected>,
}
fn bits(s: &HHeState) -> [u64; 8] {
    [
        s.fractions[0],
        s.fractions[1],
        s.fractions[2],
        s.u_erg_cm3,
        s.photon_cm3[0],
        s.photon_cm3[1],
        s.photon_cm3[2],
        s.escaped_erg_cm3,
    ]
    .map(f64::to_bits)
}
fn total_bits(r: RctIntegral) -> [u64; 4] {
    [r.events, r.heat, r.escaped, r.chemical].map(f64::to_bits)
}
fn error(s: &'static str) -> ForwardError {
    ForwardError::InvalidInput(s)
}
/// Frozen-source, reject-only subdivision of the already delivered static step.
/// This research caller retains accepted steps for inspection. It is not a
/// production checkpoint engine or a certified continuous-time integrator.
pub fn run(
    m: &Ft03Model,
    old: &HHeState,
    sel: RctSelection,
    sc: StepControl,
    ec: EventControl,
    ctl: Control,
) -> Result<History, ForwardError> {
    if !ctl.end_s.is_finite()
        || ctl.end_s < 0.
        || !ctl.max_dt_s.is_finite()
        || ctl.max_dt_s <= 0.
        || !ctl.min_dt_s.is_finite()
        || ctl.min_dt_s <= 0.
        || ctl.min_dt_s > ctl.max_dt_s
        || ctl.max_attempts == 0
    {
        return Err(error("HISTORY_CONTROL"));
    }
    let mut h = History {
        state: *old,
        rct_total: RctIntegral::default(),
        accepted: Vec::new(),
        rejected: Vec::new(),
    };
    let mut t = 0.;
    let mut dt = ctl.max_dt_s;
    let mut attempts = 0;
    while t < ctl.end_s {
        if attempts >= ctl.max_attempts {
            return Err(error("HISTORY_ATTEMPT_LIMIT"));
        }
        attempts += 1;
        let remainder = ctl.end_s - t;
        let trial = dt.min(remainder);
        if trial <= 0. || t + trial == t {
            return Err(error("HISTORY_TIME_STAGNATION"));
        }
        let before = bits(&h.state);
        let before_count = total_bits(h.rct_total);
        match bass_he_rct_step_addon::try_adaptive_step(
            m,
            &mut h.state,
            &mut h.rct_total,
            trial,
            sc,
            sel,
            ec,
        ) {
            Ok(step) => {
                t = if trial == remainder {
                    ctl.end_s
                } else {
                    t + trial
                };
                h.accepted.push(Accepted { t, dt: trial, step });
            }
            Err(e) => {
                let code = e.code();
                let unchanged = before == bits(&h.state) && before_count == total_bits(h.rct_total);
                if !unchanged {
                    return Err(error("HISTORY_REJECTION_MUTATED_INPUT"));
                }
                h.rejected.push(Rejected {
                    t,
                    dt: trial,
                    code,
                    unchanged,
                });
                if !matches!(
                    code,
                    "RCT_EVENT_LOCAL_ERROR"
                        | "RCT_LOCAL_ERROR"
                        | "RCT_NONCONVERGENCE"
                        | "FT03_LOCAL_ERROR"
                        | "FT03_NONCONVERGENCE"
                ) {
                    return Err(e);
                }
                if trial / 2. < ctl.min_dt_s {
                    return Err(error("HISTORY_MIN_STEP"));
                }
                dt = trial / 2.;
            }
        }
    }
    Ok(h)
}
