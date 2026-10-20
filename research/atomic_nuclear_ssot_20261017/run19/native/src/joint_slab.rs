//! RUN07 local frozen-geometry photon + gas reference. Proper SI quantities.
//! All photon bins have fixed energies; source rates are continuous and fixed.
//! This is NOT a redshifting cosmological or spatial-transport reference.
use crate::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    full_network::{EV_J, FullState, NetworkConfig, NetworkError, SPEED_OF_LIGHT_M_S},
    gas_reference_rhs::gas_rates,
};

pub const GAS_LEN: usize = 27;
pub const LOWER: [usize; 4] = [1, 10, 11, 3];
pub const UPPER: [usize; 4] = [2, 11, 12, 4];
#[derive(Clone, Debug)]
pub struct SlabSpectrum {
    energies: Vec<f64>,
    source: Vec<f64>,
    sigma: Vec<[f64; 4]>,
    chi: [f64; 4],
}
impl SlabSpectrum {
    pub fn native(
        energies: Vec<f64>,
        source: Vec<f64>,
        c: &NetworkConfig,
    ) -> Result<Self, NetworkError> {
        if energies.is_empty()
            || energies.len() != source.len()
            || energies.len() > 64
            || energies.iter().any(|x| !x.is_finite() || *x <= 0.)
            || source.iter().any(|x| !x.is_finite() || *x < 0.)
        {
            return Err(NetworkError::InvalidInput);
        }
        let th = HHeModel::controlled_fixture().threshold_ev;
        let chi = [th[0], th[1], th[2], c.deuterium.chi_d_ev()];
        let p = AtomicProvider::reference();
        let mut sig = Vec::new();
        for &e in &energies {
            let mut row = [0.; 4];
            for a in 0..4 {
                row[a] = if a == 3 {
                    c.deuterium
                        .cross_section_m2(e)
                        .map_err(|_| NetworkError::InputOutsideDomain)?
                } else if e < chi[a] {
                    0.
                } else {
                    p.cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][a], e)
                        .map_err(|_| NetworkError::InputOutsideDomain)?
                        * 1e-4
                };
            }
            sig.push(row);
        }
        Ok(Self {
            energies,
            source,
            sigma: sig,
            chi,
        })
    }
    pub fn energies(&self) -> &[f64] {
        &self.energies
    }
    pub fn sources(&self) -> &[f64] {
        &self.source
    }
    pub fn cross_sections(&self) -> &[[f64; 4]] {
        &self.sigma
    }
    pub fn thresholds(&self) -> [f64; 4] {
        self.chi
    }
    pub fn dimension(&self) -> usize {
        37 + self.energies.len()
    }
    pub fn photo_index(&self) -> usize {
        GAS_LEN + self.energies.len()
    }
}
/// Layout: parent27; photons M; photo events4; photo heat4; born N; born U.
/// gas_mask is parent mask0..7; photo=false turns off photon absorption+source.
pub fn joint_rhs(
    s: &FullState,
    c: &NetworkConfig,
    spec: &SlabSpectrum,
    photons: &[f64],
    gas_mask: u8,
    photo: bool,
) -> Result<Vec<f64>, NetworkError> {
    if photons.len() != spec.energies.len() || photons.iter().any(|x| !x.is_finite() || *x < 0.) {
        return Err(NetworkError::NegativePopulation);
    }
    let mut out = vec![0.; spec.dimension()];
    out[..GAS_LEN].copy_from_slice(&gas_rates(s, c, gas_mask)?.vector());
    if photo {
        let eidx = spec.photo_index();
        for (b, &nb) in photons.iter().enumerate() {
            out[GAS_LEN + b] = spec.source[b];
            out[eidx + 8] += spec.source[b];
            out[eidx + 9] += spec.source[b] * spec.energies[b] * EV_J;
            for a in 0..4 {
                let na = s
                    .gas
                    .nuclei
                    .density_m3(crate::isotope_state::IsotopeSpecies::ALL[LOWER[a]]);
                let event = SPEED_OF_LIGHT_M_S * spec.sigma[b][a] * na * nb;
                let heat = event * (spec.energies[b] - spec.chi[a]) * EV_J;
                out[GAS_LEN + b] -= event;
                out[LOWER[a]] -= event;
                out[UPPER[a]] += event;
                out[13] += heat;
                out[eidx + a] += event;
                out[eidx + 4 + a] += heat;
            }
        }
    }
    if out.iter().any(|v| !v.is_finite()) {
        return Err(NetworkError::NonFinite);
    }
    Ok(out)
}
