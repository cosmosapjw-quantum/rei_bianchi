//! Arithmetic-preserving optimization of the frozen BR06 path evaluator.
use crate::{Error, Result};
use rei_br06_reference::{
    fixture::NativeFixture,
    quadrature::PositiveGauss,
    reference::{PathControls, PathModel, PathResult, PathSample},
};
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
    bass_reactive::split_by_thresholds_from_energies,
    bianchi_i::CharacteristicRay,
    deuterium_atomic::DAtomicProvider,
    full_network::{NetworkError, SPEED_OF_LIGHT_M_S},
    isotope_state::IsotopeSpecies as S,
    source_age::Cohort,
};
use std::cell::Cell;

#[derive(Clone, Copy, Debug, Default)]
pub struct Work {
    pub opacity_integrals: usize,
    pub virtual_samples: usize,
}

/// Immutable nodes and weights are computed once for the control pair.
/// The work counter observes executed calls but does not enter the numerics.
pub struct Rules {
    opacity: PositiveGauss,
    event: PositiveGauss,
    work: Cell<Work>,
}
impl Rules {
    pub fn new(controls: PathControls) -> Result<Self> {
        Ok(Self {
            opacity: PositiveGauss::new(controls.opacity_degree)?,
            event: PositiveGauss::new(controls.event_degree)?,
            work: Cell::new(Work::default()),
        })
    }
    pub fn work(&self) -> Work {
        self.work.get()
    }
}

/// Frozen immutable input proof: the borrow prevents mutation of the fixture
/// during reuse. All spectral cross sections still use the original owners.
pub struct PreparedOpacity<'a> {
    fixture: &'a NativeFixture,
    densities: [f64; 4],
    thresholds: [f64; 4],
    atomic: AtomicProvider,
    deuterium: DAtomicProvider,
}
impl<'a> PreparedOpacity<'a> {
    pub fn new(fixture: &'a NativeFixture) -> Result<Self> {
        fixture.rate_gas.eos()?;
        let hhe = HHeModel::controlled_fixture().threshold_ev;
        Ok(Self {
            fixture,
            densities: [
                S::H1Neutral,
                S::He4Neutral,
                S::He4SinglyIonized,
                S::DNeutral,
            ]
            .map(|sp| fixture.rate_gas.nuclei.density_m3(sp)),
            thresholds: [hhe[0], hhe[1], hhe[2], fixture.conf.deuterium.chi_d_ev()],
            atomic: AtomicProvider::reference(),
            deuterium: fixture.conf.deuterium,
        })
    }
    pub fn rates(&self, energy_ev: f64, volume: f64) -> Result<[f64; 4]> {
        if !volume.is_finite() || volume <= 0.0 {
            return Err(Error::InvalidInput("rate_volume"));
        }
        // Exact arithmetic order from bound_source_age::opacity_channels.
        let mut rates = [0.0; 4];
        for (j, output) in rates.iter_mut().enumerate() {
            let sigma = if j == 3 {
                self.deuterium
                    .cross_section_m2(energy_ev)
                    .map_err(|_| NetworkError::InputOutsideDomain)?
            } else if energy_ev < self.thresholds[j] {
                0.0
            } else {
                self.atomic
                    .cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][j], energy_ev)
                    .map_err(|_| NetworkError::InputOutsideDomain)?
                    * 1e-4
            };
            *output = self.densities[j] * sigma * SPEED_OF_LIGHT_M_S;
            if !output.is_finite() {
                return Err(NetworkError::NonFinite.into());
            }
        }
        if rates.iter().any(|x| !x.is_finite() || *x < 0.0) {
            return Err(NetworkError::InvalidInput.into());
        }
        let scaled = rates.map(|x| x * (self.fixture.recorded_mid_volume / volume));
        if scaled.iter().any(|x| !x.is_finite() || *x < 0.0) {
            return Err(Error::InvalidInput("scaled_opacity"));
        }
        Ok(scaled)
    }
}

/// Original birth-ray normalization is hoisted; pullback remains the owner call.
pub struct PreparedNativePath<'a, 'b> {
    fixture: &'a NativeFixture,
    cohort: &'a Cohort,
    birth_ray: CharacteristicRay,
    opacity: &'b PreparedOpacity<'a>,
}
impl<'a, 'b> PreparedNativePath<'a, 'b> {
    pub fn new(
        fixture: &'a NativeFixture,
        cohort: &'a Cohort,
        opacity: &'b PreparedOpacity<'a>,
    ) -> Result<Self> {
        if !std::ptr::eq(fixture, opacity.fixture) {
            return Err(Error::InvalidInput("prepared_fixture_identity"));
        }
        if !cohort.n_comoving_m3.is_finite() || cohort.n_comoving_m3 < 0.0 {
            return Err(NetworkError::NonFinite.into());
        }
        let birth_ray =
            CharacteristicRay::new(cohort.energy_at_birth_ev, cohort.direction_at_birth, 0.0)
                .map_err(|_| NetworkError::InputOutsideDomain)?;
        Ok(Self {
            fixture,
            cohort,
            birth_ray,
            opacity,
        })
    }
}
impl PathModel for PreparedNativePath<'_, '_> {
    fn sample(&self, time_s: f64) -> Result<PathSample> {
        let geometry = self.fixture.bridge.0.geometry.snapshot(time_s)?;
        let ray = self
            .birth_ray
            .pullback(&self.cohort.birth_geometry, &geometry)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let derivative = -ray.energy_ev
            * (0..3)
                .map(|i| geometry.hubble_per_s[i] * ray.direction[i].powi(2))
                .sum::<f64>();
        Ok(PathSample {
            energy_ev: ray.energy_ev,
            direction: ray.direction,
            energy_derivative_ev_s: derivative,
            rates_per_s: self
                .opacity
                .rates(ray.energy_ev, geometry.volume_factor()?)?,
        })
    }
}

pub struct NativeKernel<'a> {
    fixture: &'a NativeFixture,
    controls: PathControls,
    rules: Rules,
    opacity: PreparedOpacity<'a>,
}
impl<'a> NativeKernel<'a> {
    pub fn new(fixture: &'a NativeFixture, controls: PathControls) -> Result<Self> {
        Ok(Self {
            fixture,
            controls,
            rules: Rules::new(controls)?,
            opacity: PreparedOpacity::new(fixture)?,
        })
    }
    pub fn work(&self) -> Work {
        self.rules.work()
    }
    pub fn native_path(&self, cohort: &Cohort) -> Result<PathResult> {
        let fixture = self.fixture;
        if cohort.n_comoving_m3 < 0.0 || !cohort.n_comoving_m3.is_finite() {
            return Err(Error::InvalidInput("cohort_population"));
        }
        fixture.bridge.0.geometry.validate_birth(cohort)?;
        let end = fixture.bridge.0.geometry.snapshot(fixture.t1)?;
        let e0 = cohort.ray_at(&cohort.birth_geometry)?.energy_ev;
        let e1 = cohort.ray_at(&end)?.energy_ev;
        let cuts = split_by_thresholds_from_energies(
            &fixture.bridge.0.geometry,
            cohort,
            cohort.birth_time_s,
            fixture.t1,
            e0,
            e1,
            fixture.thresholds_ev[3],
        )?;
        let model = PreparedNativePath::new(fixture, cohort, &self.opacity)?;
        let mut result = integrate_path_cached(
            &model,
            &cuts,
            fixture.thresholds_ev,
            self.controls,
            &self.rules,
        )?;
        result.threshold_crossings = [13.60, 24.59, 54.42, fixture.thresholds_ev[3]]
            .iter()
            .filter(|edge| e0 > **edge && e1 < **edge)
            .count();
        Ok(result)
    }
}

include!("path_core.rs");
