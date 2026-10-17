//! Source-age cohomology prototype: exact PR150 MD14/BB50k birth and Bianchi-I
//! collisionless Killing rays, moment projection to the exact PR150 H/He/D P2
//! chemistry step. Projection is GREY, not production source-age transport.
//! Original producers are imported byte-for-byte through lib.rs. No clipping.
use crate::atomic_provider::{Absorber, AtomicProvider};
use crate::axbi_sources::{AxbiSource, SOURCE_ID};
use crate::bianchi_i::{
    CharacteristicRay, ConstantAxisymmetricBackground, GeometryBackground, GeometrySnapshot,
};
use crate::full_network::{
    self, EV_J, EventBudget, FullState, NetworkConfig, NetworkError, PhotonBin,
};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_eos::MixtureState;

#[derive(Clone, Debug)]
pub struct Cohort {
    pub birth_time_s: f64,
    pub birth_geometry: GeometrySnapshot,
    pub energy_at_birth_ev: f64,
    pub direction_at_birth: [f64; 3],
    pub n_comoving_m3: f64,
    pub spectral_index: usize,
    pub angular_index: usize,
}
impl Cohort {
    pub fn ray_at(&self, now: &GeometrySnapshot) -> Result<CharacteristicRay, NetworkError> {
        if !self.n_comoving_m3.is_finite() || self.n_comoving_m3 < 0.0 {
            return Err(NetworkError::NonFinite);
        }
        CharacteristicRay::new(self.energy_at_birth_ev, self.direction_at_birth, 0.0)
            .and_then(|r| r.pullback(&self.birth_geometry, now))
            .map_err(|_| NetworkError::InputOutsideDomain)
    }
}
#[derive(Clone, Debug)]
pub struct AgeHistory {
    pub full: FullState,
    pub cohorts: Vec<Cohort>,
    pub time_s: f64,
    /// Signed geometric (gas p dV plus free-streaming photon redshift) work,
    /// integrated as energy per reference comoving m^3, NOT a photon creation.
    pub geometry_work_j_com3: f64,
    pub source_injected_count_com3: f64,
    pub source_injected_energy_j_com3: f64,
    pub photon_absorbed_count_com3: f64,
    pub max_grey_number_relative_error: f64,
    pub max_grey_species_relative_error: [f64; 4],
    pub chemistry_accepted: usize,
}
#[derive(Clone, Debug)]
pub struct AgeStep {
    pub state: AgeHistory,
    pub source_birth_com3: f64,
    pub radiation_redshift_work_j_com3: f64,
    pub adiabatic_gas_work_j_com3: f64,
    pub projected_grey_absorption_relative_error: f64,
    pub projected_grey_species_relative_error: [f64; 4],
    pub global_energy_relative_error: f64,
    pub chemistry_budget: EventBudget,
}
#[derive(Clone, Copy, Debug)]
pub struct GreyError {
    pub cohort_photo_events_m3: [f64; 4],
    pub projected_photo_events_m3: [f64; 4],
    pub species_relative_error: [f64; 4],
    pub total_relative_error: f64,
}
#[derive(Clone, Debug)]
pub struct SourceAgeBridge {
    pub source: AxbiSource,
    pub geometry: ConstantAxisymmetricBackground,
    pub spectral_groups_per_segment: [usize; 3],
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
impl SourceAgeBridge {
    pub fn new(
        source: AxbiSource,
        geometry: ConstantAxisymmetricBackground,
    ) -> Result<Self, NetworkError> {
        Self::with_groups(source, geometry, [2, 3, 3])
    }
    pub fn with_groups(
        source: AxbiSource,
        geometry: ConstantAxisymmetricBackground,
        groups: [usize; 3],
    ) -> Result<Self, NetworkError> {
        if source.spectral_cells.is_empty()
            || source.angular_cells.is_empty()
            || source.angular_cells.len() * groups.iter().sum::<usize>()
                > full_network::MAX_PHOTON_BINS
            || !source.spectral_cells.len().is_multiple_of(3)
            || groups
                .iter()
                .any(|&x| x == 0 || x > source.spectral_cells.len() / 3)
        {
            return Err(NetworkError::InputOutsideDomain);
        }
        let g = geometry
            .snapshot(geometry.time_domain_s[0])
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let a = positive(
            g.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?
                .cbrt(),
        )?;
        let z = 1.0 / a - 1.0;
        source
            .at_redshift(z)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        Ok(Self {
            source,
            geometry,
            spectral_groups_per_segment: groups,
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
    fn group_of(&self, spectral_index: usize) -> Result<usize, NetworkError> {
        let per = self.source.spectral_cells.len() / 3;
        if spectral_index >= self.source.spectral_cells.len() {
            return Err(NetworkError::InputOutsideDomain);
        }
        let segment = spectral_index / per;
        let prefix = self.spectral_groups_per_segment[..segment]
            .iter()
            .sum::<usize>();
        Ok(prefix + (spectral_index % per) * self.spectral_groups_per_segment[segment] / per)
    }
    pub fn project(
        &self,
        c: &[Cohort],
        g: &GeometrySnapshot,
    ) -> Result<Vec<PhotonBin>, NetworkError> {
        let nmu = self.source.angular_cells.len();
        let n = self.spectral_groups_per_segment.iter().sum::<usize>() * nmu;
        let vol = positive(
            g.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?,
        )?;
        let mut counts = vec![0.0; n];
        let mut energies = vec![0.0; n];
        for x in c {
            let k = self.group_of(x.spectral_index)? * nmu + x.angular_index;
            if k >= n {
                return Err(NetworkError::InputOutsideDomain);
            }
            let en = x.ray_at(g)?.energy_ev;
            let count = x.n_comoving_m3 / vol;
            counts[k] += count;
            energies[k] += count * en;
        }
        let mut bins = Vec::with_capacity(n);
        for k in 0..n {
            let energy = if counts[k] > 0.0 {
                energies[k] / counts[k]
            } else {
                let group = k / nmu;
                let (mut energy, mut denom) = (0.0, 0.0);
                for (i, cell) in self.source.spectral_cells.iter().enumerate() {
                    if self.group_of(i)? == group {
                        energy += cell.photon_fraction * cell.energy_ev;
                        denom += cell.photon_fraction;
                    }
                }
                energy / denom
            };
            if !energy.is_finite() || energy <= 0.0 {
                return Err(NetworkError::NonFinite);
            }
            bins.push(PhotonBin {
                energy_ev: energy,
                number_m3: counts[k],
            });
        }
        Ok(bins)
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
    pub fn grey_absorption_error(
        &self,
        c: &[Cohort],
        g: &GeometrySnapshot,
        gas: &MixtureState,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<GreyError, NetworkError> {
        let v = positive(
            g.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?,
        )?;
        let bins = self.project(c, g)?;
        let mut ref_events = [0.0; 4];
        let mut projected = [0.0; 4];
        for x in c {
            let rates = self.opacity_channels(x.ray_at(g)?.energy_ev, gas, conf)?;
            let lambda = rates.iter().sum::<f64>();
            if lambda > 0.0 {
                let total = x.n_comoving_m3 / v * (-(-lambda * dt).exp_m1());
                for j in 0..4 {
                    ref_events[j] += total * rates[j] / lambda;
                }
            }
        }
        for x in bins {
            let rates = self.opacity_channels(x.energy_ev, gas, conf)?;
            let lambda = rates.iter().sum::<f64>();
            if lambda > 0.0 {
                let total = x.number_m3 * (-(-lambda * dt).exp_m1());
                for j in 0..4 {
                    projected[j] += total * rates[j] / lambda;
                }
            }
        }
        let rel = std::array::from_fn(|j| {
            if ref_events[j] > 0.0 {
                (ref_events[j] - projected[j]).abs() / ref_events[j]
            } else if projected[j] == 0.0 {
                0.0
            } else {
                f64::INFINITY
            }
        });
        let all_ref = ref_events.iter().sum::<f64>();
        let all_proj = projected.iter().sum::<f64>();
        let total_relative_error = if all_ref > 0.0 {
            (all_ref - all_proj).abs() / all_ref
        } else {
            0.0
        };
        Ok(GreyError {
            cohort_photo_events_m3: ref_events,
            projected_photo_events_m3: projected,
            species_relative_error: rel,
            total_relative_error: finite(total_relative_error)?,
        })
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
    // no fake provider may be created; drift validation occurs at the next
    // physical P2 stage where its actual source-bound config is passed.
    pub fn advance(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<AgeStep, NetworkError> {
        if conf.photon_source != SOURCE_ID || !conf.use_photo || dt <= 0.0 || !dt.is_finite() {
            return Err(NetworkError::SourceMismatch);
        }
        let t = initial.time_s;
        let tm = t + dt * 0.5;
        let tn = t + dt;
        let g0 = self.snapshot(t)?;
        let gm = self.snapshot(tm)?;
        let gn = self.snapshot(tn)?;
        let e0 = self.total_com_energy(initial, conf, &g0)?;
        let mut s = initial.clone();
        let (wph0, wgas0) = self.drift(&mut s, &g0, &gm)?;
        let birth = self.source_births(tm, dt)?;
        let born_count = birth.iter().map(|x| x.n_comoving_m3).sum::<f64>();
        let born_energy = birth
            .iter()
            .map(|x| x.n_comoving_m3 * x.energy_at_birth_ev * EV_J)
            .sum::<f64>();
        s.source_injected_count_com3 += born_count;
        s.source_injected_energy_j_com3 += born_energy;
        s.cohorts.extend(birth);
        let bins = self.project(&s.cohorts, &gm)?;
        let grey = self.grey_absorption_error(&s.cohorts, &gm, &s.full.gas, conf, dt)?;
        s.max_grey_number_relative_error = s
            .max_grey_number_relative_error
            .max(grey.total_relative_error);
        for j in 0..4 {
            s.max_grey_species_relative_error[j] =
                s.max_grey_species_relative_error[j].max(grey.species_relative_error[j]);
        }
        s.full.photon_bins = bins.clone();
        let rr = full_network::step(&s.full, conf, dt)?;
        // One transaction: prepare every moment-survivor fraction, then apply
        // once per cohort (O(N_cohorts+N_groups), no repeated 64-bin search).
        let mut factors = vec![1.0; bins.len()];
        for (k, p) in bins.iter().enumerate() {
            let after = rr.state.photon_bins[k].number_m3;
            if after < 0.0 || after > p.number_m3 * (1.0 + 5e-13) {
                return Err(NetworkError::PhysicsLedger);
            }
            let factor = if p.number_m3 > 0.0 {
                after / p.number_m3
            } else {
                1.0
            };
            if !(0.0..=1.0 + 5e-13).contains(&factor) {
                return Err(NetworkError::PhysicsLedger);
            }
            factors[k] = factor;
        }
        let n_mu = self.source.angular_cells.len();
        for co in &mut s.cohorts {
            let k = self.group_of(co.spectral_index)? * n_mu + co.angular_index;
            co.n_comoving_m3 *= factors[k];
        }
        let events = rr.budget;
        s.photon_absorbed_count_com3 += events.photo_events_m3.iter().sum::<f64>()
            * gm.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?;
        s.chemistry_accepted += 1;
        s.full = rr.state;
        s.full.photon_bins.clear();
        let (wph1, wgas1) = self.drift(&mut s, &gm, &gn)?;
        s.time_s = tn;
        let e1 = self.total_com_energy(&s, conf, &gn)?;
        let expected = e0 + born_energy + wph0 + wgas0 + wph1 + wgas1;
        let rel = (e1 - expected).abs() / e0.abs().max(e1.abs()).max(expected.abs()).max(1e-50);
        if rel > 3e-10 || !rel.is_finite() {
            return Err(NetworkError::PhysicsLedger);
        }
        Ok(AgeStep {
            state: s,
            source_birth_com3: born_count,
            radiation_redshift_work_j_com3: wph0 + wph1,
            adiabatic_gas_work_j_com3: wgas0 + wgas1,
            projected_grey_absorption_relative_error: grey.total_relative_error,
            projected_grey_species_relative_error: grey.species_relative_error,
            global_energy_relative_error: rel,
            chemistry_budget: events,
        })
    }
}
