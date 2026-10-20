//! RUN06 independent instantaneous gas assembly, using immutable native rates.
//! Proper densities m^-3, thermal/escape/CMB powers J m^-3 s^-1.
//! No photon step, expansion step, clipping, or hidden finite-difference timestep.
use crate::HHeModel;
use crate::deuterium_atomic::{DChargeExchange, d_atomic_rhs_from_prepared};
use crate::full_network::{EV_J, FullState, NetworkConfig, NetworkError};
use crate::isotope_state::IsotopeSpecies as S;
use crate::mixture_eos::EosSnapshot;
use crate::rate_table::{IgmRateBackend, PreparedIgmRates};

pub const GAS_VECTOR_LEN: usize = 27;
#[derive(Clone, Copy, Debug, Default)]
pub struct GasRates {
    pub species: [f64; 13],
    pub heat: f64,
    pub escape: f64,
    pub cmb: f64,
    pub chemical: f64,
    pub ci: [f64; 4],
    pub rr: [f64; 4],
    pub dr: f64,
    pub cx: f64,
    pub ff: f64,
}
impl GasRates {
    /// State [n_0..n_12,u,escape,CMB,CI_4,RR_4,DR,CX,FF].
    pub fn vector(&self) -> [f64; GAS_VECTOR_LEN] {
        let mut a = [0.0; GAS_VECTOR_LEN];
        a[..13].copy_from_slice(&self.species);
        a[13..16].copy_from_slice(&[self.heat, self.escape, self.cmb]);
        a[16..20].copy_from_slice(&self.ci);
        a[20..24].copy_from_slice(&self.rr);
        a[24..].copy_from_slice(&[self.dr, self.cx, self.ff]);
        a
    }
    pub fn residual(&self) -> f64 {
        self.heat + self.chemical + self.escape + self.cmb
    }
}
fn edge(out: &mut GasRates, lo: S, hi: S, flux: f64) {
    out.species[lo as usize] -= flux;
    out.species[hi as usize] += flux;
}
/// mask: bit0 = CI/RR/DR/CE/FF, bit1 = reversible Savin CX, bit2 = CMB.
/// The native photon owner is OFF here; incoming photon bins are rejected.
pub fn gas_rates(s: &FullState, c: &NetworkConfig, mask: u8) -> Result<GasRates, NetworkError> {
    gas_rates_with_backend(s, c, mask, &IgmRateBackend::Direct)
}

/// Explicit numerical backend. Default `gas_rates` remains Direct. One bundle
/// supplies both H/He and the unchanged D H-equality approximation; no density,
/// ion fraction, opacity or heating power is cached. Mask2 retains the original
/// D atomic validation, including coefficients unused by its CX-only result.
pub fn gas_rates_with_backend(
    s: &FullState, c: &NetworkConfig, mask: u8, backend: &IgmRateBackend,
) -> Result<GasRates, NetworkError> {
    let eos = checked_eos(s, c, mask)?;
    let prepared = prepare_for_mask(backend, eos.temperature_k, mask)?;
    gas_rates_prepared(s, c, mask, eos, prepared.as_ref(), backend)
}

fn checked_eos(s: &FullState, c: &NetworkConfig, mask: u8) -> Result<EosSnapshot, NetworkError> {
    if mask > 7 || c.use_photo || !s.photon_bins.is_empty() {
        return Err(NetworkError::OwnershipConflict);
    }
    s.validate(c)?;
    Ok(s.gas.eos()?)
}

fn prepare_for_mask(backend: &IgmRateBackend, t: f64, mask: u8)
    -> Result<Option<PreparedIgmRates>, NetworkError> {
    if mask & 3 == 0 { return Ok(None); }
    backend.prepare(t).map(Some).map_err(|_| if mask & 1 != 0 {
        NetworkError::TemperatureOutsideSource
    } else { NetworkError::InputOutsideDomain })
}

fn gas_rates_prepared(
    s: &FullState, c: &NetworkConfig, mask: u8, eos: EosSnapshot,
    prepared: Option<&PreparedIgmRates>, backend: &IgmRateBackend,
) -> Result<GasRates, NetworkError> {
    let t = eos.temperature_k;
    let n = |sp| s.gas.nuclei.density_m3(sp);
    let ne = eos.free_electrons_m3;
    let ne_cm = ne * 1e-6;
    let mut q = GasRates::default();
    let chi = HHeModel::controlled_fixture().threshold_ev;
    if mask & 1 != 0 {
        let rates = prepared.ok_or(NetworkError::InvalidInput)?.rates();
        let edges = [
            (S::H1Neutral, S::H1Ionized),
            (S::He4Neutral, S::He4SinglyIonized),
            (S::He4SinglyIonized, S::He4DoublyIonized),
        ];
        for (j, (lo, hi)) in edges.into_iter().enumerate() {
            q.ci[j] = ne_cm * n(lo) * rates.ci_cm3_s[j];
            q.rr[j] = ne_cm * n(hi) * rates.rr_cm3_s[j];
            let net = q.ci[j] - q.rr[j];
            edge(&mut q, lo, hi, net);
            q.chemical += chi[j] * EV_J * net;
            let rr_kin = ne_cm * (n(hi) * 1e-6) * rates.rr_cooling_erg_cm3_s[j] * 0.1;
            q.heat -= chi[j] * EV_J * q.ci[j] + rr_kin;
            q.escape += chi[j] * EV_J * q.rr[j] + rr_kin;
        }
        q.dr = ne_cm * n(S::He4SinglyIonized) * rates.dr_cm3_s;
        let dr_flux = q.dr;
        edge(&mut q, S::He4SinglyIonized, S::He4Neutral, dr_flux);
        q.chemical -= chi[1] * EV_J * q.dr;
        let dr_kin = ne_cm * (n(S::He4SinglyIonized) * 1e-6) * rates.dr_cooling_erg_cm3_s * 0.1;
        let ce = 0.1
            * (ne_cm * n(S::H1Neutral) * 1e-6 * rates.ce_erg[0]
                + ne_cm * ne_cm * n(S::He4SinglyIonized) * 1e-6 * rates.ce_erg[1]
                + ne_cm * n(S::He4SinglyIonized) * 1e-6 * rates.ce_erg[2]);
        let z2 = S::ALL
            .into_iter()
            .map(|sp| f64::from(sp.charge()).powi(2) * n(sp))
            .sum::<f64>();
        q.ff = ne_cm * (z2 * 1e-6) * rates.freefree_erg_cm3_s * 0.1;
        q.heat -= dr_kin + ce + q.ff;
        q.escape += dr_kin + ce + q.ff + chi[1] * EV_J * q.dr;
    }
    if mask & 3 != 0 {
        let photo = c
            .deuterium
            .photo_input_from_bound_rates(0., 0., c.photon_source)
            .map_err(|_| NetworkError::SourceMismatch)?;
        let d = d_atomic_rhs_from_prepared(
            c.deuterium,
            &s.gas.nuclei,
            t,
            &photo,
            if mask & 2 != 0 {
                DChargeExchange::Savin2002
            } else {
                DChargeExchange::Disabled
            },
            prepared.ok_or(NetworkError::InvalidInput)?,
            backend,
        )
        .map_err(|_| NetworkError::InputOutsideDomain)?;
        if mask & 1 != 0 {
            q.ci[3] = d.ci_events_m3_s;
            q.rr[3] = d.rr_events_m3_s;
            edge(
                &mut q,
                S::DNeutral,
                S::DIonized,
                d.ci_events_m3_s - d.rr_events_m3_s,
            );
            for e in &d.channel_energy[1..4] {
                q.heat += e.thermal;
                q.chemical += e.chemical;
                q.escape += e.escape;
            }
        }
        if mask & 2 != 0 {
            q.cx = d.cx_forward_events_m3_s - d.cx_reverse_events_m3_s;
            let flux = q.cx;
            edge(&mut q, S::H1Ionized, S::H1Neutral, flux);
            edge(&mut q, S::DNeutral, S::DIonized, flux);
            for e in &d.channel_energy[4..6] {
                q.heat += e.thermal;
                q.chemical += e.chemical;
            }
        }
    }
    if mask & 4 != 0 {
        let hc = HHeModel::controlled_fixture();
        let a_rad = 8.0 * std::f64::consts::PI.powi(5) * hc.kb_erg_k.powi(4)
            / (15.0 * 6.626_070_15e-27_f64.powi(3) * hc.c_cm_s.powi(3));
        let coeff =
            4.0 * 6.652_458_705_1e-25 * a_rad * hc.kb_erg_k / (9.109_383_713_9e-28 * hc.c_cm_s);
        let power = coeff * ne_cm * c.cmb_temperature_k.powi(4) * (c.cmb_temperature_k - t) * 0.1;
        q.heat += power;
        q.cmb = -power;
    }
    if !q
        .vector()
        .iter()
        .chain([q.chemical].iter())
        .all(|x| x.is_finite())
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(q)
}

/// A bounded one-entry exact-T cache tied by lifetime to one immutable backend.
/// Reuse is allowed only when the newly evaluated EOS temperature has identical
/// f64 bits. This is particularly useful for consecutive same-T batch states.
pub struct GasRateWorkspace<'a> {
    backend: &'a IgmRateBackend,
    prepared: Option<PreparedIgmRates>,
    pub stats: GasBatchStats,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct GasBatchStats {
    pub evaluations: usize,
    pub preparations: usize,
    pub exact_temperature_hits: usize,
}

impl<'a> GasRateWorkspace<'a> {
    pub fn new(backend: &'a IgmRateBackend) -> Self {
        Self { backend, prepared: None, stats: GasBatchStats::default() }
    }
    pub fn evaluate(&mut self, s: &FullState, c: &NetworkConfig, mask: u8)
        -> Result<GasRates, NetworkError> {
        let eos = checked_eos(s, c, mask)?;
        let prepared = if mask & 3 == 0 { None } else {
            if self.prepared.as_ref().is_some_and(|p|
                p.temperature_k().to_bits() == eos.temperature_k.to_bits()) {
                self.stats.exact_temperature_hits += 1;
            } else {
                self.prepared = prepare_for_mask(self.backend, eos.temperature_k, mask)?;
                self.stats.preparations += 1;
            }
            self.prepared.as_ref()
        };
        let result = gas_rates_prepared(s, c, mask, eos, prepared, self.backend)?;
        self.stats.evaluations += 1;
        Ok(result)
    }
}

/// Typed source-off batch: fixed caller-owned config/mask, caller-owned output,
/// and a separate exact-T workspace per worker. At most four scoped workers.
/// On any error the output may be partially written and must be discarded.
/// There is no SIMD or speedup claim; thread startup is included in benchmarks.
pub fn gas_rates_batch_into(
    states: &[FullState], c: &NetworkConfig, mask: u8, backend: &IgmRateBackend,
    output: &mut [GasRates], workers: usize,
) -> Result<GasBatchStats, NetworkError> {
    if output.len() != states.len() || !(1..=4).contains(&workers) || states.len() > 65_536 {
        return Err(NetworkError::InvalidInput);
    }
    if mask > 7 || c.use_photo { return Err(NetworkError::OwnershipConflict); }
    if states.is_empty() { return Ok(GasBatchStats::default()); }
    fn chunk(states: &[FullState], c: &NetworkConfig, mask: u8,
        backend: &IgmRateBackend, output: &mut [GasRates]) -> Result<GasBatchStats, NetworkError> {
        let mut workspace = GasRateWorkspace::new(backend);
        for (s, out) in states.iter().zip(output) { *out = workspace.evaluate(s, c, mask)?; }
        Ok(workspace.stats)
    }
    if workers == 1 { return chunk(states, c, mask, backend, output); }
    let width = states.len().div_ceil(workers);
    std::thread::scope(|scope| {
        let handles: Vec<_> = states.chunks(width).zip(output.chunks_mut(width)).map(|(s,o)|
            scope.spawn(move || chunk(s,c,mask,backend,o))).collect();
        let mut total = GasBatchStats::default();
        for handle in handles {
            let stats = handle.join().map_err(|_| NetworkError::InvalidInput)??;
            total.evaluations += stats.evaluations;
            total.preparations += stats.preparations;
            total.exact_temperature_hits += stats.exact_temperature_hits;
        }
        Ok(total)
    })
}
