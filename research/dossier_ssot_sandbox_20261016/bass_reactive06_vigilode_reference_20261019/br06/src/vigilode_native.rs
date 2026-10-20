//! Recovery R1 native scalar moment export; previous wrapper bytes were lost.
//!
//! Each row retains one of the 48 original spectral labels. The eight angular
//! rates are summed only for this frozen-opacity scalar diagnostic. The main
//! variable-geometry path reference keeps every source cohort and birth time.
use crate::{
    Error, Result,
    fixture::NativeFixture,
    quadrature::gauss_age_nodes,
    vigilode_moments::{MomentRefusal, MomentWork, positive_moment_table},
};
use rodas5p_core::directed::Interval;
use std::{fs, io::Write, path::Path};

fn scaled(interval: Interval, factor: f64) -> Result<Interval> {
    Ok(interval.scale(factor).map_err(MomentRefusal::Arithmetic)?)
}

fn actual_source_mass(fixture: &NativeFixture, j_mid: f64, tau: f64, degree: usize) -> Result<f64> {
    let dt = fixture.t1 - fixture.t0;
    let mut sum = 0.0;
    for (age, weight) in gauss_age_nodes(tau, 4, degree)? {
        let t_birth = fixture.t1 - dt * age;
        let geometry = fixture.bridge.0.geometry.snapshot(t_birth)?;
        let ratio = fixture.emission_amplitude(&geometry)? / fixture.source_midpoint_amplitude;
        sum += weight * (-tau * age).exp() * ratio;
    }
    let mass = j_mid * dt * sum;
    if !mass.is_finite() || mass < 0.0 {
        return Err(Error::InvalidInput("native_moment_source_mass"));
    }
    Ok(mass)
}

pub fn export(fixture: &NativeFixture, directory: &Path) -> Result<()> {
    fixture.validate_source()?;
    fs::create_dir_all(directory)?;
    let templates = fixture.templates(false)?;
    let dt = fixture.t1 - fixture.t0;
    let left_geometry = fixture.bridge.0.geometry.snapshot(fixture.t0)?;
    let right_geometry = fixture.bridge.0.geometry.snapshot(fixture.t1)?;
    let left_ratio =
        fixture.emission_amplitude(&left_geometry)? / fixture.source_midpoint_amplitude;
    let right_ratio =
        fixture.emission_amplitude(&right_geometry)? / fixture.source_midpoint_amplitude;
    let mut file = fs::File::create(directory.join("VIGILODE_NATIVE_MOMENTS.csv"))?;
    writeln!(
        file,
        "case,spectral,energy_ev,dt_s,kappa_per_s,tau,j_mid_com3_s,j_left_com3_s,j_right_com3_s,J00_lo,J00_hi,J10_lo,J10_hi,J20_lo,J20_hi,constant_mass_lo,constant_mass_hi,constant_age1_lo_s,constant_age1_hi_s,constant_age2_lo_s2,constant_age2_hi_s2,linear_mass_lo,linear_mass_hi,actual_source_gl8,actual_source_gl16,dyadic_levels,validation_attempts,kernel_calls,exponential_calls,dyadic_steps,interval_operations,width_checks"
    )?;
    if fixture.bridge.0.source.spectral_cells.len() != 48 || templates.len() != 384 {
        return Err(Error::InvalidInput("native_moment_48_by_8"));
    }
    for (spectral, cell) in fixture.bridge.0.source.spectral_cells.iter().enumerate() {
        let selected: Vec<_> = templates
            .iter()
            .filter(|c| c.spectral_index == spectral)
            .collect();
        if selected.len() != 8 {
            return Err(Error::InvalidInput("native_moment_angular_labels"));
        }
        let j_mid: f64 = selected.iter().map(|c| c.n_comoving_m3).sum();
        let energy_ev = cell.energy_ev;
        let rates = fixture
            .bridge
            .opacity_channels(energy_ev, &fixture.rate_gas, &fixture.conf)?;
        let kappa: f64 = rates.iter().sum();
        let tau = kappa * dt;
        let j_left = j_mid * left_ratio;
        let j_right = j_mid * right_ratio;
        let mut work = MomentWork::default();
        let table = positive_moment_table(tau, 1e-12, 0.0, &mut work)?;
        let m0 = table.get(0, 0);
        let m1 = table.get(1, 0);
        let m2 = table.get(2, 0);
        // Each exported scalar input is its exact binary64 value. Directed
        // operations enclose its scalar integral; source interpolation error
        // and changing opacity/geometry require separate comparisons.
        let constant = scaled(scaled(m0, j_mid)?, dt)?;
        let age1 = scaled(scaled(scaled(m1, j_mid)?, dt)?, dt)?;
        let age2 = scaled(scaled(scaled(scaled(m2, j_mid)?, dt)?, dt)?, dt)?;
        let linear = scaled(table.linear_source_mass(j_left, j_right)?, dt)?;
        let actual_gl8 = actual_source_mass(fixture, j_mid, tau, 8)?;
        let actual_gl16 = actual_source_mass(fixture, j_mid, tau, 16)?;
        writeln!(
            file,
            "{},{spectral},{energy_ev:.17e},{dt:.17e},{kappa:.17e},{tau:.17e},{j_mid:.17e},{j_left:.17e},{j_right:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{actual_gl8:.17e},{actual_gl16:.17e},{},{},{},{},{},{},{}",
            fixture.case,
            m0.lo,
            m0.hi,
            m1.lo,
            m1.hi,
            m2.lo,
            m2.hi,
            constant.lo,
            constant.hi,
            age1.lo,
            age1.hi,
            age2.lo,
            age2.hi,
            linear.lo,
            linear.hi,
            table.dyadic_levels,
            work.validation_attempts,
            work.kernel_calls,
            work.exponential_calls,
            work.dyadic_steps,
            work.interval_operations,
            work.width_checks,
        )?;
    }
    fs::write(
        directory.join("VIGILODE_NATIVE_SCOPE.json"),
        concat!(
            "{\n",
            "  \"revision\": \"BR06_RECOVERY_R1\",\n",
            "  \"scope\": \"48 scalar original-source energy labels; recorded step1 midpoint opacity frozen\",\n",
            "  \"interval_input\": \"exact binary64 tau, duration, and exported source endpoints\",\n",
            "  \"moment\": \"J_jk=int_0^1 exp(-tau*x)*x^j*(1-x)^k dx; x is normalized birth age\",\n",
            "  \"linear_source\": \"j_left*(1-u)+j_right*u, u=1-x\",\n",
            "  \"source_check\": \"actual MD14 amplitude at actual birth geometry, positive graded GL8 and GL16, refinement4\",\n",
            "  \"independent_errors\": \"source interpolation and variable-geometry opacity errors are outside scalar intervals\"\n",
            "}\n"
        ),
    )?;
    Ok(())
}
