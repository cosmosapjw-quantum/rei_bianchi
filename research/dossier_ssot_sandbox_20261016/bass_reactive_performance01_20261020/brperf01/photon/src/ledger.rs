// Exact ordered accumulator copy from original BR06 reference.rs.
#[derive(Clone, Debug, Default)]
pub struct Ledger {
    pub born: f64,
    pub surviving: f64,
    pub age_sum_s: f64,
    pub age2_sum_s2: f64,
    pub events: [f64; 4],
    pub heat_j: [f64; 4],
    pub chemical_j: f64,
    pub source_energy_j: f64,
    pub surviving_energy_j: f64,
    pub absorbed_energy_j: f64,
    pub work_ledger_j: f64,
    pub work_independent_j: f64,
    pub q2_numerator_j: f64,
    pub cohorts: usize,
    pub samples: usize,
    pub inversions: usize,
    pub threshold_crossings: usize,
    pub max_path_number_residual: f64,
    pub max_path_energy_relative_residual: f64,
    pub max_inverse_residual: f64,
    pub zero_born_cohorts: usize,
    pub represented_survival_underflows: usize,
    pub represented_opacity_underflows: usize,
    pub represented_absorption_underflows: usize,
    pub represented_species_underflows: usize,
    pub represented_heat_underflows: usize,
    pub thin_time_paths: usize,
}

impl Ledger {
    fn add_birth(&mut self, fixture: &NativeFixture, co: &Cohort, path: &PathResult) {
        let n = co.n_comoving_m3;
        let retained = n * path.survival;
        let age = fixture.t1 - co.birth_time_s;
        self.born += n;
        self.surviving += retained;
        self.age_sum_s += retained * age;
        self.age2_sum_s2 += retained * age * age;
        self.source_energy_j += n * co.energy_at_birth_ev * EV_J;
        self.surviving_energy_j += n * path.surviving_energy_ev * EV_J;
        self.absorbed_energy_j += n * path.absorbed_energy_ev * EV_J;
        self.chemical_j += n * path.chemical_ev * EV_J;
        self.work_ledger_j += n * path.geometry_work_ledger_ev * EV_J;
        self.work_independent_j += n * path.geometry_work_independent_ev * EV_J;
        self.q2_numerator_j +=
            n * path.surviving_energy_ev * EV_J * 0.5 * (3.0 * path.end_direction[2].powi(2) - 1.0);
        for i in 0..4 {
            self.events[i] += n * path.events[i];
            self.heat_j[i] += n * path.heat_ev[i] * EV_J;
        }
        self.cohorts += 1;
        self.zero_born_cohorts += usize::from(n == 0.0);
        self.represented_survival_underflows += usize::from(path.represented_survival_underflow);
        self.represented_opacity_underflows += usize::from(path.represented_opacity_underflow);
        self.represented_absorption_underflows +=
            usize::from(path.represented_absorption_underflow);
        self.represented_species_underflows += path
            .represented_species_underflow
            .iter()
            .filter(|&&x| x)
            .count();
        self.represented_heat_underflows += path
            .represented_heat_underflow
            .iter()
            .filter(|&&x| x)
            .count();
        self.thin_time_paths += usize::from(path.thin_time_route);
        self.samples += path.samples;
        self.inversions += path.inverse_iterations;
        self.threshold_crossings += path.threshold_crossings;
        self.max_path_number_residual = self
            .max_path_number_residual
            .max(path.number_residual.abs());
        self.max_path_energy_relative_residual = self
            .max_path_energy_relative_residual
            .max((path.energy_residual_ev / co.energy_at_birth_ev).abs());
        self.max_inverse_residual = self.max_inverse_residual.max(path.max_inverse_residual);
    }
    pub fn number_residual(&self) -> f64 {
        self.surviving + self.events.iter().sum::<f64>() - self.born
    }
    pub fn energy_residual(&self) -> f64 {
        self.surviving_energy_j + self.absorbed_energy_j
            - self.source_energy_j
            - self.work_independent_j
    }
    fn validate(&self) -> Result<()> {
        if [
            self.born,
            self.surviving,
            self.age_sum_s,
            self.age2_sum_s2,
            self.chemical_j,
            self.source_energy_j,
            self.surviving_energy_j,
            self.absorbed_energy_j,
            self.work_ledger_j,
            self.work_independent_j,
            self.q2_numerator_j,
        ]
        .iter()
        .chain(self.events.iter())
        .chain(self.heat_j.iter())
        .any(|x| !x.is_finite())
        {
            return Err(Error::InvalidInput("source_integral_accumulator"));
        }
        Ok(())
    }
}
