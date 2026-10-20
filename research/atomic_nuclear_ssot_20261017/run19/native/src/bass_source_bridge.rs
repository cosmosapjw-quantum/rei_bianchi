//! RUN04 minimal new BASS geometry adapter. Selected method bodies are copied
//! verbatim from source_age.rs; original gas/atomic owners remain unmodified.
use crate::atomic_provider::{Absorber, AtomicProvider};
use crate::axbi_sources::{AxbiSource, SOURCE_ID};
use crate::bass_geometry::BassGeometry;
use crate::bianchi_i::{GeometryBackground, GeometrySnapshot};
use crate::full_network::{self, EV_J, FullState, NetworkConfig, NetworkError};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_eos::MixtureState;
use crate::source_age::{AgeHistory, Cohort};
#[derive(Clone, Debug)]
pub struct BassSourceBridge {
    pub source: AxbiSource,
    pub geometry: BassGeometry,
    pub cmb_t0_k: f64,
}
fn finite(x: f64) -> Result<f64, NetworkError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(NetworkError::NonFinite)
    }
}
fn positive(x: f64) -> Result<f64, NetworkError> {
    if x.is_finite() && x > 0.0 {
        Ok(x)
    } else {
        Err(NetworkError::InputOutsideDomain)
    }
}
impl BassSourceBridge {
    pub fn new(
        source: AxbiSource,
        geometry: BassGeometry,
        cmb_t0_k: f64,
    ) -> Result<Self, NetworkError> {
        if !cmb_t0_k.is_finite()
            || cmb_t0_k <= 0.0
            || source.spectral_cells.is_empty()
            || source.angular_cells.is_empty()
        {
            return Err(NetworkError::InvalidInput);
        }
        source
            .at_redshift(20.0)
            .map_err(|_| NetworkError::SourceMismatch)?;
        Ok(Self {
            source,
            geometry,
            cmb_t0_k,
        })
    }
    pub(crate) fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, NetworkError> {
        self.geometry
            .snapshot(t)
            .map_err(|_| NetworkError::InputOutsideDomain)
    }

    pub(crate) fn total_com_energy(
        &self,
        s: &AgeHistory,
        conf: &NetworkConfig,
        g: &GeometrySnapshot,
    ) -> Result<f64, NetworkError> {
        let v = positive(
            g.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?,
        )?;
        let local = s.full.gas.thermal_j_m3
            + s.full.binding_j_m3(conf)
            + s.full.escaped_j_m3
            + s.full.cmb_reservoir_j_m3;
        let photons = s
            .cohorts
            .iter()
            .map(|c| Ok(c.n_comoving_m3 * c.ray_at(g)?.energy_ev * EV_J))
            .collect::<Result<Vec<_>, NetworkError>>()?
            .iter()
            .sum::<f64>();
        finite(local * v + photons)
    }

    pub fn initial(
        &self,
        full: FullState,
        conf: &NetworkConfig,
        t: f64,
    ) -> Result<AgeHistory, NetworkError> {
        if conf.photon_source != SOURCE_ID || !full.photon_bins.is_empty() || full.elapsed_s != t {
            return Err(NetworkError::SourceMismatch);
        }
        full.validate(conf)?;
        let g = self.snapshot(t)?;
        let z = 1.0
            / g.volume_factor()
                .map_err(|_| NetworkError::InvalidInput)?
                .cbrt()
            - 1.0;
        let emission = self
            .source
            .at_redshift(z)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let nh =
            full.gas.nuclei.density_m3(S::H1Neutral) + full.gas.nuclei.density_m3(S::H1Ionized);
        let e_nh = emission.proper_photons_cm3_s * 1e6 / emission.per_h_s;
        if (nh - e_nh).abs() > 2e-10 * nh.max(e_nh).max(1.0) {
            return Err(NetworkError::SourceMismatch);
        }
        Ok(AgeHistory {
            full,
            cohorts: Vec::new(),
            time_s: t,
            geometry_work_j_com3: 0.0,
            source_injected_count_com3: 0.0,
            source_injected_energy_j_com3: 0.0,
            photon_absorbed_count_com3: 0.0,
            max_grey_number_relative_error: 0.0,
            max_grey_species_relative_error: [0.0; 4],
            chemistry_accepted: 0,
        })
    }

    pub fn source_births(&self, t: f64, dt: f64) -> Result<Vec<Cohort>, NetworkError> {
        if !dt.is_finite() || dt <= 0.0 {
            return Err(NetworkError::InvalidInput);
        }
        let g = self.snapshot(t)?;
        let vol = positive(
            g.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?,
        )?;
        let z = 1.0 / vol.cbrt() - 1.0;
        let rate = self
            .source
            .at_redshift(z)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let ncom = rate.proper_photons_cm3_s * 1e6 * dt * vol;
        if !ncom.is_finite() || ncom <= 0.0 {
            return Err(NetworkError::NonFinite);
        }
        let mut out =
            Vec::with_capacity(self.source.spectral_cells.len() * self.source.angular_cells.len());
        for (i, s) in self.source.spectral_cells.iter().enumerate() {
            for (j, a) in self.source.angular_cells.iter().enumerate() {
                let mu = a.mu;
                let dir = [(1.0 - mu * mu).sqrt(), 0.0, mu];
                out.push(Cohort {
                    birth_time_s: t,
                    birth_geometry: g,
                    energy_at_birth_ev: s.energy_ev,
                    direction_at_birth: dir,
                    n_comoving_m3: ncom * s.photon_fraction * a.count_fraction,
                    spectral_index: i,
                    angular_index: j,
                });
            }
        }
        Ok(out)
    }

    pub(crate) fn opacity_channels(
        &self,
        en: f64,
        gas: &MixtureState,
        conf: &NetworkConfig,
    ) -> Result<[f64; 4], NetworkError> {
        let a = [
            S::H1Neutral,
            S::He4Neutral,
            S::He4SinglyIonized,
            S::DNeutral,
        ];
        let ch = crate::HHeModel::controlled_fixture().threshold_ev;
        let th = [ch[0], ch[1], ch[2], conf.deuterium.chi_d_ev()];
        let p = AtomicProvider::reference();
        let mut op = [0.0; 4];
        for j in 0..4 {
            let sigma = if j == 3 {
                conf.deuterium
                    .cross_section_m2(en)
                    .map_err(|_| NetworkError::InputOutsideDomain)?
            } else if en < th[j] {
                0.0
            } else {
                p.cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][j], en)
                    .map_err(|_| NetworkError::InputOutsideDomain)?
                    * 1e-4
            };
            op[j] = finite(gas.nuclei.density_m3(a[j]) * sigma * full_network::SPEED_OF_LIGHT_M_S)?;
        }
        Ok(op)
    }

    pub(crate) fn drift(
        &self,
        s: &mut AgeHistory,
        from: &GeometrySnapshot,
        to: &GeometrySnapshot,
    ) -> Result<(f64, f64), NetworkError> {
        let v0 = positive(
            from.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?,
        )?;
        let v1 = positive(
            to.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?,
        )?;
        let ratio = positive(v0 / v1)?;
        let u0 = s.full.gas.thermal_j_m3 * v0;
        let old = s.full.gas.nuclei;
        let mut array = [0.0; 13];
        for sp in S::ALL {
            array[sp as usize] = old.density_m3(sp) * ratio;
        }
        let nuclei =
            IsotopeNumberState::new(array).map_err(|_| NetworkError::NegativePopulation)?;
        s.full.gas = MixtureState {
            nuclei,
            thermal_j_m3: s.full.gas.thermal_j_m3 * ratio.powf(5.0 / 3.0),
        };
        s.full.escaped_j_m3 *= ratio;
        s.full.cmb_reservoir_j_m3 *= ratio;
        let u1 = s.full.gas.thermal_j_m3 * v1;
        let mut work_photon = 0.0;
        for x in &s.cohorts {
            let start = x.ray_at(from)?.energy_ev;
            let end = x.ray_at(to)?.energy_ev;
            work_photon += x.n_comoving_m3 * (end - start) * EV_J;
        }
        let work_gas = u1 - u0;
        s.geometry_work_j_com3 += work_photon + work_gas;
        Ok((work_photon, work_gas))
    }
}
