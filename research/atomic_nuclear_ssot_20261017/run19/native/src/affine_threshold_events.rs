//! P4/S4B: genuinely time-dependent, but *analytically integrable*, Bianchi-I
//! directional Hubble rates H_i(t) = H_i(ref) + dotH_i*(t-ref).
//!
//! This is a prescribed off-shell geometry adapter. It is deliberately NOT an
//! arbitrary time-dependent background callback or on-shell Einstein solution.
//! The event locator only accepts a whole-interval certificate F''>=0 for
//! F=E^2; otherwise it fails closed rather than missing possible extra roots.
use crate::ForwardError;
use crate::atomic_provider::{Absorber, AtomicProvider};
use crate::bianchi_i::{GeometryBackground, GeometrySnapshot};
use crate::deuterium_atomic::DAtomicProvider;
use crate::full_network::{EV_J, NetworkError, SPEED_OF_LIGHT_M_S};
use crate::positive_birth_clock::photon_slab;
use crate::source_age::Cohort;
use crate::threshold_events::VERNER_FIT_EDGES_EV;

#[derive(Clone, Copy, Debug)]
pub struct AffineHubbleBackground {
    pub reference_time_s: f64,
    pub reference_scale: [f64; 3],
    pub hubble_at_reference_per_s: [f64; 3],
    pub hubble_slope_per_s2: [f64; 3],
    pub time_domain_s: [f64; 2],
}

impl AffineHubbleBackground {
    pub fn new(
        reference_time_s: f64,
        reference_scale: [f64; 3],
        hubble_at_reference_per_s: [f64; 3],
        hubble_slope_per_s2: [f64; 3],
        time_domain_s: [f64; 2],
    ) -> Result<Self, NetworkError> {
        if !reference_time_s.is_finite()
            || !time_domain_s.iter().all(|x| x.is_finite())
            || time_domain_s[0] >= time_domain_s[1]
            || reference_time_s < time_domain_s[0]
            || reference_time_s > time_domain_s[1]
            || !hubble_slope_per_s2.iter().all(|x| x.is_finite())
        {
            return Err(NetworkError::InvalidInput);
        }
        GeometrySnapshot::new(reference_scale, hubble_at_reference_per_s)
            .map_err(|_| NetworkError::InvalidInput)?;
        let bg = Self {
            reference_time_s,
            reference_scale,
            hubble_at_reference_per_s,
            hubble_slope_per_s2,
            time_domain_s,
        };
        bg.snapshot(time_domain_s[0])
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        bg.snapshot(time_domain_s[1])
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        Ok(bg)
    }

    pub fn checked_time(&self, t: f64) -> Result<(), NetworkError> {
        if !t.is_finite() || t < self.time_domain_s[0] || t > self.time_domain_s[1] {
            return Err(NetworkError::InputOutsideDomain);
        }
        Ok(())
    }

    /// Sufficient, source-independent certificate for F=E² convex on [t0,t1].
    /// F''=sum_i E_b² n_bi² exp(-2I_i)(4H_i²-2 dotH_i).
    /// All slopes <=0 pass; for positive slope a whole-interval minimum |H_i|
    /// must obey the *strict* inequality 2 min H_i² > dotH_i. It deliberately
    /// rejects potentially valid intervals when this sufficient gate is absent.
    pub fn certify_energy_squared_convex(&self, t0: f64, t1: f64) -> Result<(), NetworkError> {
        self.checked_time(t0)?;
        self.checked_time(t1)?;
        if t1 <= t0 {
            return Err(NetworkError::InvalidInput);
        }
        for i in 0..3 {
            let slope = self.hubble_slope_per_s2[i];
            if slope > 0.0 {
                let a = self.hubble_at_reference_per_s[i] + slope * (t0 - self.reference_time_s);
                let b = self.hubble_at_reference_per_s[i] + slope * (t1 - self.reference_time_s);
                let minabs = if a <= 0.0 && b >= 0.0 {
                    0.0
                } else {
                    a.abs().min(b.abs())
                };
                // This strict arithmetic guard prevents false claims near the
                // equality surface where rounding could flip a certificate.
                if !a.is_finite()
                    || !b.is_finite()
                    || 2.0 * minabs * minabs <= slope * (1.0 + 1e-12)
                {
                    return Err(NetworkError::InputOutsideDomain);
                }
            }
        }
        Ok(())
    }
}

impl GeometryBackground for AffineHubbleBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        if !t.is_finite() || t < self.time_domain_s[0] || t > self.time_domain_s[1] {
            return Err(ForwardError::InvalidInput("AffineTimeDomain"));
        }
        let delta = t - self.reference_time_s;
        let mut scales = [0.; 3];
        let mut hubbles = [0.; 3];
        for i in 0..3 {
            let h = self.hubble_at_reference_per_s[i];
            let d = self.hubble_slope_per_s2[i];
            let integral = h.mul_add(delta, 0.5 * d * delta * delta);
            hubbles[i] = d.mul_add(delta, h);
            scales[i] = self.reference_scale[i] * integral.exp();
        }
        GeometrySnapshot::new(scales, hubbles)
    }
}

fn e_and_derivative(
    co: &Cohort,
    bg: &AffineHubbleBackground,
    t: f64,
) -> Result<(f64, f64), NetworkError> {
    let g = bg
        .snapshot(t)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let ray = co.ray_at(&g)?;
    let en = ray.energy_ev;
    let directional_h = ray
        .direction
        .iter()
        .zip(g.hubble_per_s.iter())
        .map(|(n, h)| n * n * h)
        .sum::<f64>();
    let der = -2.0 * en * en * directional_h;
    if !en.is_finite() || en <= 0. || !der.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    Ok((en, der))
}

fn energy_crossing(
    co: &Cohort,
    bg: &AffineHubbleBackground,
    mut a: f64,
    mut b: f64,
    edge: f64,
) -> Result<Option<f64>, NetworkError> {
    let ea = e_and_derivative(co, bg, a)?.0 - edge;
    let eb = e_and_derivative(co, bg, b)?.0 - edge;
    if ea == 0.0 || eb == 0.0 || (ea < 0.0) == (eb < 0.0) {
        return Ok(None);
    }
    let sign_a = ea < 0.0;
    for _ in 0..90 {
        let mid = 0.5 * a + 0.5 * b;
        if mid <= a || mid >= b {
            break;
        }
        let f = e_and_derivative(co, bg, mid)?.0 - edge;
        if f == 0.0 {
            return Ok(Some(mid));
        }
        if (f < 0.0) == sign_a {
            a = mid;
        } else {
            b = mid;
        }
    }
    Ok(Some(0.5 * a + 0.5 * b))
}

/// True crossings of H I, He I, He II original Verner fit and original
/// DAtomicProvider binding cutoff. Tangencies without sign change are not
/// physical finite-width opacity events. Outputs are strictly interior times.
pub fn affine_threshold_cut_times(
    co: &Cohort,
    bg: &AffineHubbleBackground,
    t0: f64,
    t1: f64,
    deuterium_edge_ev: f64,
) -> Result<Vec<f64>, NetworkError> {
    if !co.birth_time_s.is_finite()
        || t0 < co.birth_time_s
        || !deuterium_edge_ev.is_finite()
        || deuterium_edge_ev <= VERNER_FIT_EDGES_EV[0]
    {
        return Err(NetworkError::InvalidInput);
    }
    bg.certify_energy_squared_convex(t0, t1)?;
    let d0 = e_and_derivative(co, bg, t0)?.1;
    let d1 = e_and_derivative(co, bg, t1)?.1;
    let mut pieces = vec![(t0, t1)];
    if d0 < 0. && d1 > 0. {
        let (mut a, mut b) = (t0, t1);
        for _ in 0..90 {
            let m = 0.5 * a + 0.5 * b;
            if m <= a || m >= b {
                break;
            }
            if e_and_derivative(co, bg, m)?.1 <= 0.0 {
                a = m;
            } else {
                b = m;
            }
        }
        let tm = 0.5 * a + 0.5 * b;
        if tm > t0 && tm < t1 {
            pieces = vec![(t0, tm), (tm, t1)];
        }
    }
    let mut cuts = Vec::new();
    for edge in VERNER_FIT_EDGES_EV.into_iter().chain([deuterium_edge_ev]) {
        for &(a, b) in &pieces {
            if let Some(t) = energy_crossing(co, bg, a, b, edge)?
                && t > t0
                && t < t1
            {
                cuts.push(t);
            }
        }
    }
    cuts.sort_by(f64::total_cmp);
    let eps_t = 16.0 * f64::EPSILON * t0.abs().max(t1.abs()).max(1.0);
    cuts.dedup_by(|a, b| (*a - *b).abs() <= eps_t);
    Ok(cuts)
}

pub fn affine_photo_segments(
    co: &Cohort,
    bg: &AffineHubbleBackground,
    t0: f64,
    t1: f64,
    deuterium_edge_ev: f64,
) -> Result<Vec<(f64, f64)>, NetworkError> {
    let mut last = t0;
    let mut out = Vec::new();
    for t in affine_threshold_cut_times(co, bg, t0, t1, deuterium_edge_ev)?
        .into_iter()
        .chain([t1])
    {
        if t <= last {
            return Err(NetworkError::NoForwardProgress);
        }
        out.push((last, t));
        last = t;
    }
    Ok(out)
}

/// Proper densities frozen in comoving counts (not a reacting gas solver).
#[derive(Clone, Copy, Debug)]
pub struct FrozenPhotoDensities {
    pub proper_reference_time_s: f64,
    /// Order: HI, HeI, HeII, DI. Unit: m^-3 at reference time.
    pub neutral_m3: [f64; 4],
}

#[derive(Clone, Copy, Debug)]
pub struct PhotonPhotoLedger {
    pub initial_count_com3: f64,
    pub survivor_count_com3: f64,
    pub absorbed_count_com3: [f64; 4],
    pub absorbed_energy_j_com3: f64,
    pub chemical_energy_j_com3: f64,
    pub thermal_energy_j_com3: f64,
    pub radiation_geometry_work_j_com3: f64,
    pub event_cuts: usize,
}
impl PhotonPhotoLedger {
    pub fn count_residual(&self) -> f64 {
        self.initial_count_com3
            - self.survivor_count_com3
            - self.absorbed_count_com3.iter().sum::<f64>()
    }

    pub fn event_energy_residual(&self) -> f64 {
        self.absorbed_energy_j_com3 - self.chemical_energy_j_com3 - self.thermal_energy_j_com3
    }
}

#[derive(Clone, Copy, Debug)]
pub struct AffinePhotoControls {
    pub substeps: usize,
    pub split_events: bool,
}

/// Positive source-native cross-section cohort transport with exact photo-edge
/// times, midpoint rates on each smooth interval and one photon owner.
/// No species depletion, no Case-A/CMB/FF/CX evolution, no full EoR claim.
pub fn affine_photo_cohort(
    co: &Cohort,
    bg: &AffineHubbleBackground,
    d: DAtomicProvider,
    gas: FrozenPhotoDensities,
    t0: f64,
    t1: f64,
    controls: AffinePhotoControls,
) -> Result<PhotonPhotoLedger, NetworkError> {
    let substeps = controls.substeps;
    let split_events = controls.split_events;
    if substeps == 0
        || substeps > 8192
        || !co.n_comoving_m3.is_finite()
        || co.n_comoving_m3 < 0.
        || !gas.neutral_m3.iter().all(|x| x.is_finite() && *x >= 0.)
    {
        return Err(NetworkError::InvalidInput);
    }
    bg.certify_energy_squared_convex(t0, t1)?;
    bg.checked_time(gas.proper_reference_time_s)?;
    let volume_ref = bg
        .snapshot(gas.proper_reference_time_s)
        .map_err(|_| NetworkError::InputOutsideDomain)?
        .volume_factor()
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let provider = AtomicProvider::reference();
    let chi = crate::HHeModel::controlled_fixture().threshold_ev;
    let energies = [chi[0], chi[1], chi[2], d.chi_d_ev()];
    let g0 = bg
        .snapshot(t0)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let e0 = co.ray_at(&g0)?.energy_ev;
    let mut n = co.n_comoving_m3;
    let mut events = [0.; 4];
    let mut deposited_ev = 0.;
    let mut chem_ev = 0.;
    let mut thermal_ev = 0.;
    let mut event_cuts = 0_usize;
    for j in 0..substeps {
        let aa = t0 + (t1 - t0) * j as f64 / substeps as f64;
        let bb = if j + 1 == substeps {
            t1
        } else {
            t0 + (t1 - t0) * (j + 1) as f64 / substeps as f64
        };
        let segments = if split_events {
            affine_photo_segments(co, bg, aa, bb, d.chi_d_ev())?
        } else {
            vec![(aa, bb)]
        };
        event_cuts += segments.len() - 1;
        for (a, b) in segments {
            let tm = 0.5 * a + 0.5 * b;
            let g = bg
                .snapshot(tm)
                .map_err(|_| NetworkError::InputOutsideDomain)?;
            let en = co.ray_at(&g)?.energy_ev;
            let vol = g
                .volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?;
            let nscale = volume_ref / vol;
            let mut rates = [0.; 4];
            for i in 0..4 {
                let sigma = if i == 3 {
                    d.cross_section_m2(en)
                        .map_err(|_| NetworkError::InputOutsideDomain)?
                } else if en < energies[i] {
                    0.0
                } else {
                    provider
                        .cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][i], en)
                        .map_err(|_| NetworkError::InputOutsideDomain)?
                        * 1e-4
                };
                rates[i] = SPEED_OF_LIGHT_M_S * gas.neutral_m3[i] * nscale * sigma;
                if !rates[i].is_finite() || rates[i] < 0.0 {
                    return Err(NetworkError::NonFinite);
                }
            }
            let kap = rates.iter().sum::<f64>();
            let frac = photon_slab(kap * (b - a))?;
            let absorbed = n * frac.old_absorbed;
            if kap > 0. {
                for i in 0..4 {
                    let x = absorbed * rates[i] / kap;
                    if x > 0. && en < energies[i] {
                        return Err(NetworkError::PhysicsLedger);
                    }
                    events[i] += x;
                    chem_ev += x * energies[i];
                    thermal_ev += x * (en - energies[i]);
                }
            }
            deposited_ev += absorbed * en;
            n *= frac.old_surviving;
        }
    }
    let g1 = bg
        .snapshot(t1)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let e1 = co.ray_at(&g1)?.energy_ev;
    let total = PhotonPhotoLedger {
        initial_count_com3: co.n_comoving_m3,
        survivor_count_com3: n,
        absorbed_count_com3: events,
        absorbed_energy_j_com3: deposited_ev * EV_J,
        chemical_energy_j_com3: chem_ev * EV_J,
        thermal_energy_j_com3: thermal_ev * EV_J,
        radiation_geometry_work_j_com3: (n * e1 - co.n_comoving_m3 * e0 + deposited_ev) * EV_J,
        event_cuts,
    };
    if !total.survivor_count_com3.is_finite() || !total.radiation_geometry_work_j_com3.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    Ok(total)
}

/// Opt-in original MD14/BB50k, 48-owner-cell x GL-angle retarded birth
/// injection on the affine time-varying geometry, using the original source's
/// proper photon rate and the original positive within-cell spectral adapter.
/// No approximation of the external source law or additional physical source.
pub fn affine_source_births(
    source: &crate::axbi_sources::AxbiSource,
    bg: &AffineHubbleBackground,
    time_s: f64,
    duration_weighted_s: f64,
    spectral: crate::positive_spectral::SpectralMode,
    d_binding_ev: f64,
) -> Result<Vec<Cohort>, NetworkError> {
    bg.checked_time(time_s)?;
    if !duration_weighted_s.is_finite() || duration_weighted_s <= 0. {
        return Err(NetworkError::InvalidInput);
    }
    let g = bg
        .snapshot(time_s)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let vol = g
        .volume_factor()
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let z = 1. / vol.cbrt() - 1.;
    let rate = source
        .at_redshift(z)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let birth_com3 = rate.proper_photons_cm3_s * 1e6 * duration_weighted_s * vol;
    if !birth_com3.is_finite() || birth_com3 <= 0. {
        return Err(NetworkError::NonFinite);
    }
    let mut cohorts = Vec::with_capacity(source.spectral_cells.len() * source.angular_cells.len());
    for (i, s) in source.spectral_cells.iter().enumerate() {
        for (j, a) in source.angular_cells.iter().enumerate() {
            let mu = a.mu;
            cohorts.push(Cohort {
                birth_time_s: time_s,
                birth_geometry: g,
                energy_at_birth_ev: s.energy_ev,
                direction_at_birth: [(1. - mu * mu).sqrt(), 0., mu],
                n_comoving_m3: birth_com3 * s.photon_fraction * a.count_fraction,
                spectral_index: i,
                angular_index: j,
            });
        }
    }
    crate::positive_spectral::expand_births(source, &cohorts, d_binding_ev, spectral)
}

#[derive(Clone, Copy, Debug, Default)]
pub struct SourcePhotonLedger {
    pub newborn_count_com3: f64,
    pub newborn_energy_j_com3: f64,
    pub survivor_count_com3: f64,
    pub absorber_events_com3: [f64; 4],
    pub photo_energy_j_com3: f64,
    pub binding_j_com3: f64,
    pub heat_j_com3: f64,
    pub radiation_geometry_work_j_com3: f64,
    pub true_cohorts: usize,
    pub event_cuts: usize,
}
impl SourcePhotonLedger {
    pub fn number_residual(&self) -> f64 {
        self.newborn_count_com3
            - self.survivor_count_com3
            - self.absorber_events_com3.iter().sum::<f64>()
    }
    pub fn event_energy_residual(&self) -> f64 {
        self.photo_energy_j_com3 - self.binding_j_com3 - self.heat_j_com3
    }
}

#[derive(Clone, Copy, Debug)]
pub struct AffineSourceControls {
    pub gauss_birth: usize,
    pub photon: AffinePhotoControls,
    pub spectrum: crate::positive_spectral::SpectralMode,
}

/// One affine-H prescribed-background pulse of continuous MD14/BB50k source
/// birth quadrature (GL2 or GL4). This is photon-only source-on microphysics:
/// reactions, thermal cooling, self-consistent gas feedback, physical Einstein
/// geometry and actual reionization history are NOT included here.
pub fn source_on_affine_photo_pilot(
    source: &crate::axbi_sources::AxbiSource,
    bg: &AffineHubbleBackground,
    d: DAtomicProvider,
    gas: FrozenPhotoDensities,
    t0: f64,
    t1: f64,
    controls: AffineSourceControls,
) -> Result<SourcePhotonLedger, NetworkError> {
    bg.certify_energy_squared_convex(t0, t1)?;
    let mut result = SourcePhotonLedger::default();
    let g_end = bg
        .snapshot(t1)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    for (u, w) in crate::retarded_transport::gauss_birth_nodes(controls.gauss_birth)? {
        let time = t0 + (t1 - t0) * u;
        for co in affine_source_births(
            source,
            bg,
            time,
            (t1 - t0) * w,
            controls.spectrum,
            d.chi_d_ev(),
        )? {
            let ledger = affine_photo_cohort(&co, bg, d, gas, time, t1, controls.photon)?;
            result.newborn_count_com3 += co.n_comoving_m3;
            result.newborn_energy_j_com3 += co.n_comoving_m3 * co.energy_at_birth_ev * EV_J;
            result.survivor_count_com3 += ledger.survivor_count_com3;
            for (j, x) in ledger.absorbed_count_com3.into_iter().enumerate() {
                result.absorber_events_com3[j] += x;
            }
            result.photo_energy_j_com3 += ledger.absorbed_energy_j_com3;
            result.binding_j_com3 += ledger.chemical_energy_j_com3;
            result.heat_j_com3 += ledger.thermal_energy_j_com3;
            result.radiation_geometry_work_j_com3 += ledger.radiation_geometry_work_j_com3;
            result.true_cohorts += 1;
            result.event_cuts += ledger.event_cuts;
            let _ = co.ray_at(&g_end)?; // actual end-state characteristic domain gate
        }
    }
    if !result.newborn_count_com3.is_finite()
        || !result.survivor_count_com3.is_finite()
        || !result.photo_energy_j_com3.is_finite()
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(result)
}
