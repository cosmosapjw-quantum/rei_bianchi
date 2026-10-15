// This module is included in case_a_source.rs, sharing its private Gas type.
// Source: original cold AXBI Grackle 3.4.1 Case-A point RHS. It does not
// reconstruct chemical or thermal coefficients or introduce warm FT03 data.
use rei_microphysics::axbi_rates::AxbiProvider;
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::{IgmPhotoInput, IgmPointRhs};

const MICRO_MAX_DT_S: f64 = 1.0e10;
const MICRO_MAX_SUBSTEPS: usize = 100000;
#[derive(Clone, Copy, Debug, Default)]
struct MicroBook {
    ci: [f64; 3],
    rr: [f64; 3],
    dr: f64,
    thermal: f64,
    binding: f64,
    escaped: f64,
    cmb: f64,
    ci_floor: [f64; 3],
    ce_cap: f64,
    excluded_dr: f64,
    max_energy_local_residual: f64,
    max_charge_local_residual: f64,
    n_substeps: usize,
}
impl MicroBook {
    fn energy_residual(&self) -> f64 {
        self.thermal + self.binding + self.escaped - self.cmb
    }
}
fn cold_original_case_a_point(gas: &Gas, nh: f64, tcmb: f64) -> Result<IgmPointRhs, String> {
    let c = HHeModel::controlled_fixture();
    let phys = IgmGasState::new([gas.h_ii, gas.he_ii, gas.he_iii], gas.u_ev_h * c.ev_erg)
        .map_err(|e| format!("native GasState: {e:?}"))?;
    // h=0 because exact adiabatic half-maps are applied separately.
    // The original native operator retains ALL CI/RR/DR/CE/free-free/Compton
    // terms, but receives zero PHOTO input: the exact packet-resolved
    // absorptions were already applied to this gas in this same midpoint.
    let point = AxbiProvider
        .point(&phys, nh, nh * F_HE, 0., tcmb, IgmPhotoInput::default())
        .map_err(|e| format!("native Case-A RHS: {e:?}"))?;
    Ok(point.rhs)
}
fn micro_explicit(g: &Gas, rhs: &IgmPointRhs, nh: f64, dt: f64) -> Result<Gas, String> {
    let mut p = *g;
    for i in 0..3 {
        let df = rhs.fraction_dt[i] * dt;
        match i {
            0 => p.h_ii += df,
            1 => p.he_ii += df,
            2 => p.he_iii += df,
            _ => unreachable!(),
        }
    }
    p.u_ev_h += rhs.thermal_micro_erg_cm3_s * dt / (nh * HHeModel::controlled_fixture().ev_erg);
    if p.h_ii < -1e-12
        || p.h_ii > 1. + 1e-12
        || p.he_ii < -1e-12
        || p.he_iii < -1e-12
        || p.he_ii + p.he_iii > 1. + 1e-12
        || p.u_ev_h <= 0.
        || !p.u_ev_h.is_finite()
    {
        return Err("Case-A micro step outside species simplex or thermal positivity".into());
    }
    Ok(p)
}
fn apply_original_case_a(
    g: &mut Gas,
    nh: f64,
    tcmb: f64,
    dt: f64,
    book: &mut MicroBook,
) -> Result<(), String> {
    if !dt.is_finite() || dt <= 0. || !nh.is_finite() || nh <= 0. || !tcmb.is_finite() || tcmb <= 0.
    {
        return Err("Invalid native micro clock/density".into());
    }
    let count = (dt / MICRO_MAX_DT_S).ceil().max(1.) as usize;
    if count > MICRO_MAX_SUBSTEPS {
        return Err("Excessive requested micro CFL steps".into());
    }
    let h = dt / (count as f64);
    let ev = HHeModel::controlled_fixture().ev_erg;
    for _ in 0..count {
        let before = *g;
        let f0 = cold_original_case_a_point(&before, nh, tcmb)?;
        let predicted = micro_explicit(&before, &f0, nh, h)?;
        let f1 = cold_original_case_a_point(&predicted, nh, tcmb)?;
        // SSP RK2/Heun: conservative average of the original proper-time
        // species rates and micro thermal energy. No positivity projection.
        let mut avg = IgmPointRhs::default();
        for j in 0..3 {
            avg.fraction_dt[j] = (f0.fraction_dt[j] + f1.fraction_dt[j]) / 2.;
            avg.ci_events_cm3_s[j] = (f0.ci_events_cm3_s[j] + f1.ci_events_cm3_s[j]) / 2.;
            avg.rr_events_cm3_s[j] = (f0.rr_events_cm3_s[j] + f1.rr_events_cm3_s[j]) / 2.;
            avg.ci_floor_events_cm3_s[j] =
                (f0.ci_floor_events_cm3_s[j] + f1.ci_floor_events_cm3_s[j]) / 2.;
            avg.ce_cap_cooling_erg_cm3_s[j] =
                (f0.ce_cap_cooling_erg_cm3_s[j] + f1.ce_cap_cooling_erg_cm3_s[j]) / 2.;
        }
        avg.dr_events_cm3_s = (f0.dr_events_cm3_s + f1.dr_events_cm3_s) / 2.;
        avg.thermal_micro_erg_cm3_s =
            (f0.thermal_micro_erg_cm3_s + f1.thermal_micro_erg_cm3_s) / 2.;
        avg.binding_micro_erg_cm3_s =
            (f0.binding_micro_erg_cm3_s + f1.binding_micro_erg_cm3_s) / 2.;
        avg.escape_erg_cm3_s = (f0.escape_erg_cm3_s + f1.escape_erg_cm3_s) / 2.;
        avg.cmb_to_gas_erg_cm3_s = (f0.cmb_to_gas_erg_cm3_s + f1.cmb_to_gas_erg_cm3_s) / 2.;
        avg.excluded_dr_cooling_erg_cm3_s =
            (f0.excluded_dr_cooling_erg_cm3_s + f1.excluded_dr_cooling_erg_cm3_s) / 2.;
        // Native source identity energy balance is separate from photon photoheat:
        // thermal + atomic binding + escaping source - CMB = 0.
        let local_energy =
            avg.thermal_micro_erg_cm3_s + avg.binding_micro_erg_cm3_s + avg.escape_erg_cm3_s
                - avg.cmb_to_gas_erg_cm3_s;
        let magnitude = avg.thermal_micro_erg_cm3_s.abs()
            + avg.binding_micro_erg_cm3_s.abs()
            + avg.escape_erg_cm3_s.abs()
            + avg.cmb_to_gas_erg_cm3_s.abs();
        let local_relative = local_energy.abs() / magnitude.max(1e-290);
        book.max_energy_local_residual = book.max_energy_local_residual.max(local_relative);
        if local_relative > 1e-11 {
            return Err("Case-A native source energy operator mismatch".into());
        }
        let mut updated = micro_explicit(&before, &avg, nh, h)?;
        let d_e = updated.electron_per_h() - before.electron_per_h();
        let rhs_net = h / nh
            * (avg.ci_events_cm3_s.iter().sum::<f64>()
                - avg.rr_events_cm3_s.iter().sum::<f64>()
                - avg.dr_events_cm3_s);
        let charge_error = (d_e - rhs_net).abs();
        book.max_charge_local_residual = book.max_charge_local_residual.max(charge_error);
        if charge_error > 2e-14 {
            return Err("Case-A source electron/charge mismatch".into());
        }
        // Gas energy, ionization fractions and provenance remain separate.
        *g = updated;
        for j in 0..3 {
            book.ci[j] += h * avg.ci_events_cm3_s[j] / nh;
            book.rr[j] += h * avg.rr_events_cm3_s[j] / nh;
            book.ci_floor[j] += h * avg.ci_floor_events_cm3_s[j] / nh;
            book.ce_cap += h * avg.ce_cap_cooling_erg_cm3_s[j] / (nh * ev);
        }
        book.dr += h * avg.dr_events_cm3_s / nh;
        book.thermal += h * avg.thermal_micro_erg_cm3_s / (nh * ev);
        book.binding += h * avg.binding_micro_erg_cm3_s / (nh * ev);
        book.escaped += h * avg.escape_erg_cm3_s / (nh * ev);
        book.cmb += h * avg.cmb_to_gas_erg_cm3_s / (nh * ev);
        book.excluded_dr += h * avg.excluded_dr_cooling_erg_cm3_s / (nh * ev);
        book.n_substeps += 1;
    }
    Ok(())
}
