//! Proper-SI isotope bookkeeping; this module selects no physical rates or ICs.
use crate::ForwardError;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(usize)]
pub enum IsotopeSpecies {
    Neutron,
    H1Neutral,
    H1Ionized,
    DNeutral,
    DIonized,
    TNeutral,
    TIonized,
    He3Neutral,
    He3SinglyIonized,
    He3DoublyIonized,
    He4Neutral,
    He4SinglyIonized,
    He4DoublyIonized,
}
impl IsotopeSpecies {
    pub const ALL: [Self; 13] = [
        Self::Neutron,
        Self::H1Neutral,
        Self::H1Ionized,
        Self::DNeutral,
        Self::DIonized,
        Self::TNeutral,
        Self::TIonized,
        Self::He3Neutral,
        Self::He3SinglyIonized,
        Self::He3DoublyIonized,
        Self::He4Neutral,
        Self::He4SinglyIonized,
        Self::He4DoublyIonized,
    ];
    pub const fn baryon_number(self) -> u8 {
        match self {
            Self::Neutron => 1,
            Self::H1Neutral | Self::H1Ionized => 1,
            Self::DNeutral | Self::DIonized => 2,
            Self::TNeutral | Self::TIonized => 3,
            Self::He3Neutral | Self::He3SinglyIonized | Self::He3DoublyIonized => 3,
            Self::He4Neutral | Self::He4SinglyIonized | Self::He4DoublyIonized => 4,
        }
    }
    pub const fn charge(self) -> u8 {
        match self {
            Self::H1Ionized
            | Self::DIonized
            | Self::TIonized
            | Self::He3SinglyIonized
            | Self::He4SinglyIonized => 1,
            Self::He3DoublyIonized | Self::He4DoublyIonized => 2,
            _ => 0,
        }
    }
    pub const fn nuclear_charge(self) -> u8 {
        match self {
            Self::Neutron => 0,
            Self::H1Neutral
            | Self::H1Ionized
            | Self::DNeutral
            | Self::DIonized
            | Self::TNeutral
            | Self::TIonized => 1,
            _ => 2,
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct IsotopeNumberMoments {
    pub baryon_density_m3: f64,
    pub heavy_particle_density_m3: f64,
    pub neutral_free_electron_density_m3: f64,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct IsotopeNumberState {
    density_m3: [f64; 13],
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct LegacyHHeProjection {
    pub n_h_cm3: f64,
    pub n_he_cm3: f64,
    pub fractions: [f64; 3],
}
impl IsotopeNumberState {
    pub fn new(density_m3: [f64; 13]) -> Result<Self, ForwardError> {
        if density_m3.iter().any(|x| !x.is_finite() || *x < 0.) {
            return Err(ForwardError::InvalidInput("ISOTOPE_DENSITY"));
        }
        let s = Self { density_m3 };
        s.moments()?;
        Ok(s)
    }
    pub fn density_m3(&self, s: IsotopeSpecies) -> f64 {
        self.density_m3[s as usize]
    }
    pub fn moments(&self) -> Result<IsotopeNumberMoments, ForwardError> {
        let mut b = 0.;
        let mut e = 0.;
        let mut h = 0.;
        for s in IsotopeSpecies::ALL {
            let n = self.density_m3[s as usize];
            b += f64::from(s.baryon_number()) * n;
            e += f64::from(s.charge()) * n;
            h += n;
        }
        if !(b.is_finite() && e.is_finite() && h.is_finite()) {
            return Err(ForwardError::InvalidInput("ISOTOPE_OVERFLOW"));
        }
        Ok(IsotopeNumberMoments {
            baryon_density_m3: b,
            heavy_particle_density_m3: h,
            neutral_free_electron_density_m3: e,
        })
    }
    pub fn abundances_per_baryon(&self) -> Result<[f64; 13], ForwardError> {
        let b = self.moments()?.baryon_density_m3;
        if b <= 0. {
            return Err(ForwardError::InvalidInput("ISOTOPE_VACUUM"));
        }
        let mut y = [0.; 13];
        for s in IsotopeSpecies::ALL {
            y[s as usize] = self.density_m3[s as usize] / b;
        }
        Ok(y)
    }
    /// Valid only for the explicit all-electrons-thermal, neutral, no-positron closure.
    pub fn thermal_particle_density_all_thermal_m3(&self) -> Result<f64, ForwardError> {
        let m = self.moments()?;
        let n = m.heavy_particle_density_m3 + m.neutral_free_electron_density_m3;
        if n.is_finite() {
            Ok(n)
        } else {
            Err(ForwardError::InvalidInput("ISOTOPE_OVERFLOW"))
        }
    }
    pub fn try_legacy_hhe_projection(&self) -> Result<LegacyHHeProjection, ForwardError> {
        for s in [
            IsotopeSpecies::Neutron,
            IsotopeSpecies::DNeutral,
            IsotopeSpecies::DIonized,
            IsotopeSpecies::TNeutral,
            IsotopeSpecies::TIonized,
            IsotopeSpecies::He3Neutral,
            IsotopeSpecies::He3SinglyIonized,
            IsotopeSpecies::He3DoublyIonized,
        ] {
            if self.density_m3(s) > 0. {
                return Err(ForwardError::InvalidInput("UNSUPPORTED_LEGACY_ISOTOPE"));
            }
        }
        let h0 = self.density_m3(IsotopeSpecies::H1Neutral);
        let hp = self.density_m3(IsotopeSpecies::H1Ionized);
        let he0 = self.density_m3(IsotopeSpecies::He4Neutral);
        let hep = self.density_m3(IsotopeSpecies::He4SinglyIonized);
        let hepp = self.density_m3(IsotopeSpecies::He4DoublyIonized);
        let h = h0 + hp;
        let he = he0 + hep + hepp;
        if !(h.is_finite() && he.is_finite()) {
            return Err(ForwardError::InvalidInput("ISOTOPE_OVERFLOW"));
        }
        if (h > 0. && h / 1e6 == 0.) || (he > 0. && he / 1e6 == 0.) {
            return Err(ForwardError::InvalidInput("ISOTOPE_UNIT_UNDERFLOW"));
        }
        Ok(LegacyHHeProjection {
            n_h_cm3: h / 1e6,
            n_he_cm3: he / 1e6,
            fractions: [
                if h > 0. { hp / h } else { 0. },
                if he > 0. { hep / he } else { 0. },
                if he > 0. { hepp / he } else { 0. },
            ],
        })
    }
}
