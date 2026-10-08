use crate::{checked, err, positive, product, Fallible};
use canonical::{Tracked, Wide};
use rei_microphysics::{
    igm_background::FlrwPoint,
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs, IgmPointRhs},
    HHeModel,
};

fn operation_rounding_bound(value: f64) -> Result<Wide, &'static str> {
    if !value.is_finite() {
        return Err("nonfinite photoheat operation");
    }
    if value == 0.0 || !value.is_normal() {
        // One binary64 subnormal ulp. This also encloses a result rounded to zero.
        Wide::from_parts(1.0, -1074)
    } else {
        let exponent = ((value.abs().to_bits() >> 52) & 0x7ff) as i32 - 1023;
        // Match the conservative whole-ulp convention used by the owner wrapper.
        Wide::from_parts(1.0, exponent - 51)
    }
}

/// One photoheating contribution for the stored binary64 A/B moments.
///
/// The value follows the existing operation order. The bound covers only those
/// coefficient/product/subtraction roundings; inherited A/B uncertainty is
/// propagated separately by the owner ledger.
pub(crate) fn photoheat_term(a: f64, b: f64, threshold_ev: f64) -> Fallible<(f64, Wide)> {
    let c = HHeModel::controlled_fixture();
    if !a.is_finite()
        || !b.is_finite()
        || !threshold_ev.is_finite()
        || a < 0.0
        || b < 0.0
        || threshold_ev <= 0.0
    {
        return Err("invalid photoheat operands".into());
    }
    if a == 0.0 && b == 0.0 {
        return Ok((0.0, Wide::ZERO));
    }
    let coefficient = c.ev_erg * threshold_ev;
    let coefficient_bound = operation_rounding_bound(coefficient).map_err(err)?;
    let threshold_energy = coefficient * a;
    if !threshold_energy.is_finite() {
        return Err("nonfinite photoheat threshold energy".into());
    }
    let mut bound = if a == 0.0 {
        Wide::ZERO
    } else {
        operation_rounding_bound(threshold_energy)
            .map_err(err)?
            .upper_add(
                coefficient_bound
                    .upper_mul(Wide::from_f64(a).map_err(err)?)
                    .map_err(err)?,
            )
            .map_err(err)?
    };
    let heat = b - threshold_energy;
    if !(b == 0.0 && threshold_energy == 0.0) {
        bound = bound
            .upper_add(operation_rounding_bound(heat).map_err(err)?)
            .map_err(err)?;
    }
    if !heat.is_finite() {
        return Err("nonfinite photoheat".into());
    }
    let magnitude = Wide::from_f64(heat.abs()).map_err(err)?;
    if heat < 0.0 {
        return Err(if magnitude.le(bound) {
            "unresolved photoheat sign"
        } else {
            "negative photoheat"
        }
        .into());
    }
    if heat == 0.0 {
        if bound.is_empty() {
            return Ok((heat, bound));
        }
        return Err("unresolved photoheat sign".into());
    }
    if magnitude.le(bound) {
        return Err("unresolved photoheat sign".into());
    }
    Ok((heat, bound))
}

/// Prefer the historical A/B operation order when its sign is resolved.  Only
/// the range-boundary case falls back to the positive excess-energy owner that
/// was formed in the radiation kernel before subnormal scaling.
pub(crate) fn photoheat_owner(
    a: f64,
    b: f64,
    threshold_ev: f64,
    heat: Tracked,
) -> Fallible<(f64, Wide)> {
    match photoheat_term(a, b, threshold_ev) {
        Ok(x) => Ok(x),
        Err(e) if e == "unresolved photoheat sign" && !heat.value.is_empty() => {
            if heat.value.le(heat.loss) {
                return Err("unresolved direct photoheat sign".into());
            }
            let (value, bound) = heat.readout().map_err(err)?;
            Ok((value, bound))
        }
        Err(e) => Err(e),
    }
}

pub fn photo_delta(a: [f64; 3], b: [f64; 3], fhe: f64) -> [f64; 4] {
    let c = HHeModel::controlled_fixture();
    [
        a[0],
        (a[1] - a[2]) / fhe,
        a[2] / fhe,
        (0..3)
            .map(|i| b[i] - c.ev_erg * c.threshold_ev[i] * a[i])
            .sum(),
    ]
}

pub(crate) fn photo_delta_bounded(owners: crate::v2::Owners, fhe: f64) -> Fallible<([f64; 4], Wide)> {
    let c = HHeModel::controlled_fixture();
    let ledger = crate::v2::owner_ledger(owners).map_err(err)?;
    let a = owners.an;
    let b = owners.be;
    let mut heat = 0.0;
    let mut heat_bound = Wide::ZERO;
    for i in 0..3 {
        let (term, term_bound) = photoheat_owner(a[i], b[i], c.threshold_ev[i], ledger.heat[i])?;
        let next = heat + term;
        heat_bound = heat_bound.upper_add(term_bound).map_err(err)?;
        if heat != 0.0 && term != 0.0 {
            heat_bound = heat_bound
                .upper_add(operation_rounding_bound(next).map_err(err)?)
                .map_err(err)?;
        }
        heat = next;
    }
    Ok(([a[0], (a[1] - a[2]) / fhe, a[2] / fhe, heat], heat_bound))
}
pub fn gas(y: [f64; 4]) -> Fallible<IgmGasState> {
    IgmGasState::new([y[0], y[1], y[2]], y[3]).map_err(err)
}
pub fn values(g: &IgmGasState) -> [f64; 4] {
    [
        g.fractions[0],
        g.fractions[1],
        g.fractions[2],
        g.w_erg_per_h,
    ]
}
pub fn rhs(y: [f64; 4], p: FlrwPoint) -> Fallible<IgmPointRhs> {
    igm_point_rhs(
        &gas(y)?,
        p.n_h_cm3,
        p.n_he_cm3,
        p.hubble_per_s,
        p.tcmb_k,
        Default::default(),
    )
    .map_err(err)
}
pub fn binding(y: [f64; 4], fhe: f64) -> f64 {
    let c = HHeModel::controlled_fixture();
    c.ev_erg
        * (c.threshold_ev[0] * y[0]
            + fhe * (c.threshold_ev[1] * y[1] + (c.threshold_ev[1] + c.threshold_ev[2]) * y[2]))
}
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct MaterialOwners {
    pub ci: [f64; 3],
    pub rr: [f64; 3],
    pub dr: f64,
    pub escape: f64,
    pub work: f64,
    pub cmb: f64,
    pub floor: [f64; 3],
    pub cap: [f64; 3],
    pub excluded_dr: f64,
    pub nonphoto_binding: f64,
    pub nonphoto_thermal: f64,
}
impl MaterialOwners {
    pub fn stage(r: IgmPointRhs, p: FlrwPoint, ds: f64) -> Fallible<Self> {
        let dt = positive(ds / p.hubble_per_s)?;
        let vol = positive(dt / p.n_h_cm3)?;
        let mut z = Self::default();
        for i in 0..3 {
            z.ci[i] = product(vol, r.ci_events_cm3_s[i])?;
            z.rr[i] = product(vol, r.rr_events_cm3_s[i])?;
            z.floor[i] = product(vol, r.ci_floor_events_cm3_s[i])?;
            z.cap[i] = product(vol, r.ce_cap_cooling_erg_cm3_s[i])?;
        }
        z.dr = product(vol, r.dr_events_cm3_s)?;
        z.escape = product(vol, r.escape_erg_cm3_s)?;
        z.work = product(vol, r.expansion_work_erg_cm3_s)?;
        z.cmb = -product(vol, r.cmb_to_gas_erg_cm3_s.abs())? * r.cmb_to_gas_erg_cm3_s.signum();
        z.excluded_dr = product(vol, r.excluded_dr_cooling_erg_cm3_s)?;
        z.nonphoto_binding = checked(vol * r.binding_micro_erg_cm3_s)?;
        z.nonphoto_thermal = checked(dt * r.w_dt_erg_per_h_s)?;
        Ok(z)
    }
    pub fn plus(self, b: Self) -> Fallible<Self> {
        let mut a = self;
        for i in 0..3 {
            a.ci[i] = checked(a.ci[i] + b.ci[i])?;
            a.rr[i] = checked(a.rr[i] + b.rr[i])?;
            a.floor[i] = checked(a.floor[i] + b.floor[i])?;
            a.cap[i] = checked(a.cap[i] + b.cap[i])?;
        }
        a.dr = checked(a.dr + b.dr)?;
        a.escape = checked(a.escape + b.escape)?;
        a.work = checked(a.work + b.work)?;
        a.cmb = checked(a.cmb + b.cmb)?;
        a.excluded_dr = checked(a.excluded_dr + b.excluded_dr)?;
        a.nonphoto_binding = checked(a.nonphoto_binding + b.nonphoto_binding)?;
        a.nonphoto_thermal = checked(a.nonphoto_thermal + b.nonphoto_thermal)?;
        Ok(a)
    }
}

#[cfg(test)]
mod photoheat_tests {
    use super::*;

    #[test]
    fn saved_positive_subnormal_heat_is_certified() {
        let (heat, bound) = photoheat_term(
            2.5091851155235384e-296,
            5.5049080207218545e-307,
            13.598434599702,
        )
        .unwrap();
        assert_eq!(heat.to_bits(), 0x0002_bdc7_4d33_9a20);
        assert!(heat > 0.0 && !heat.is_normal());
        assert!(bound.le(Wide::from_f64(heat).unwrap()));
    }

    #[test]
    fn normal_route_preserves_existing_operation_order() {
        let a = 0.25;
        let b = 1.0e-10;
        let threshold = 13.598434599702;
        let expected = b - HHeModel::controlled_fixture().ev_erg * threshold * a;
        let (heat, _) = photoheat_term(a, b, threshold).unwrap();
        assert_eq!(heat.to_bits(), expected.to_bits());
    }

    #[test]
    fn structural_zero_is_exact_but_negative_and_uncertain_are_rejected() {
        let (_, bound) = photoheat_term(0.0, 0.0, 13.598434599702).unwrap();
        assert!(bound.is_empty());
        assert!(photoheat_term(1.0, 0.0, 13.598434599702)
            .unwrap_err()
            .contains("negative photoheat"));
        let coefficient = HHeModel::controlled_fixture().ev_erg * 13.598434599702;
        assert!(photoheat_term(1.0, coefficient, 13.598434599702)
            .unwrap_err()
            .contains("unresolved photoheat sign"));
    }

    #[test]
    fn canonical_positive_heat_may_project_to_zero() {
        let a = 5.5661679234838235e-316;
        let heat = Tracked::exact(Wide::from_parts(1.25, -1100).unwrap());
        let (value, bound) = photoheat_owner(a, 0.0, 13.598434599702, heat).unwrap();
        assert_eq!(value, 0.0);
        assert!(!bound.is_empty());
    }
}
