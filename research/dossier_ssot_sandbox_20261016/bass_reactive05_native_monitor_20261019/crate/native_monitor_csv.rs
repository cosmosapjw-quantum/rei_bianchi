//! Streaming CSV export for accepted native birth monitor data.
//! All scientific f64 values use round-trip decimal precision. Empty fields
//! denote undefined shape/ratios, never zero observations. Existing files are
//! not overwritten. The driver uses persistent append indices without compaction.

use crate::bianchi_i::GeometrySnapshot;
use crate::birth_age_certificate::MeasureCertificate;
use crate::bound_source_age::AgeHistory;
use crate::isotope_state::IsotopeSpecies;
use crate::native_birth_monitor::StepMonitor;
use std::fs::{File, OpenOptions};
use std::io::{self, BufWriter, Write};
use std::path::Path;

struct Row<'a> {
    out: &'a mut BufWriter<File>,
    first: bool,
}

impl<'a> Row<'a> {
    fn new(out: &'a mut BufWriter<File>) -> Self {
        Self { out, first: true }
    }

    fn separator(&mut self) -> io::Result<()> {
        if self.first {
            self.first = false;
            Ok(())
        } else {
            self.out.write_all(b",")
        }
    }

    fn text(&mut self, text: impl std::fmt::Display) -> io::Result<()> {
        self.separator()?;
        write!(self.out, "{text}")
    }

    fn number(&mut self, number: f64) -> io::Result<()> {
        self.separator()?;
        write!(self.out, "{number:.17e}")
    }

    fn optional(&mut self, number: Option<f64>) -> io::Result<()> {
        match number {
            Some(value) => self.number(value),
            None => self.text(""),
        }
    }

    fn numbers(&mut self, values: impl IntoIterator<Item = f64>) -> io::Result<()> {
        for value in values {
            self.number(value)?;
        }
        Ok(())
    }

    fn measure(&mut self, measure: MeasureCertificate) -> io::Result<()> {
        self.numbers([measure.exact_mass, measure.discrete_mass])?;
        self.optional(measure.relative_mass_defect)?;
        self.optional(measure.log_mass_ratio)?;
        self.text(measure.absolute_mass_underflow)?;
        let shape = measure.shape;
        self.optional(shape.map(|s| s.cdf_sup))?;
        self.optional(shape.map(|s| s.w1))?;
        for i in 0..2 {
            self.optional(shape.map(|s| s.exact_moments[i]))?;
            self.optional(shape.map(|s| s.discrete_moments[i]))?;
            self.optional(shape.map(|s| s.signed_moment_defects[i]))?;
        }
        self.text(shape.map_or_else(String::new, |s| s.normalized_weight_underflows.to_string()))
    }

    fn end(self) -> io::Result<()> {
        self.out.write_all(b"\n")
    }
}

fn open(path: &Path, name: &str, header: &str) -> io::Result<BufWriter<File>> {
    let file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path.join(name))?;
    let mut out = BufWriter::with_capacity(1 << 20, file);
    writeln!(out, "{header}")?;
    Ok(out)
}

fn measure_header(prefix: &str) -> String {
    [
        "exact_mass",
        "discrete_mass",
        "relative_mass_defect",
        "log_mass_ratio",
        "absolute_mass_underflow",
        "cdf_sup",
        "w1_normalized",
        "exact_mean",
        "discrete_mean",
        "mean_defect",
        "exact_second",
        "discrete_second",
        "second_defect",
        "normalized_weight_underflows",
    ]
    .map(|suffix| format!("{prefix}_{suffix}"))
    .join(",")
}

pub struct MonitorCsv {
    steps: BufWriter<File>,
    rules: BufWriter<File>,
    panels: BufWriter<File>,
    templates: BufWriter<File>,
    births: BufWriter<File>,
    final_cohorts: BufWriter<File>,
    pub steps_written: usize,
    pub births_written: usize,
}

impl MonitorCsv {
    pub fn create(path: &Path) -> io::Result<Self> {
        std::fs::create_dir_all(path)?;
        let rate_names = IsotopeSpecies::ALL
            .map(|s| format!("rate_{s:?}_m3"))
            .join(",");
        let accepted_names = IsotopeSpecies::ALL
            .map(|s| format!("accepted_{s:?}_m3"))
            .join(",");
        let steps = format!(
            "step,t0_s,tm_s,t1_s,dt_s,prior_cohorts,newborn_cohorts,rules,templates,{rate_names},rate_thermal_j_m3,rate_temperature_K,mid_a1,mid_a2,mid_a3,mid_H1_per_s,mid_H2_per_s,mid_H3_per_s,mid_volume,end_a1,end_a2,end_a3,end_H1_per_s,end_H2_per_s,end_H3_per_s,end_volume,{accepted_names},accepted_thermal_j_m3,accepted_binding_j_m3,accepted_escaped_j_m3,accepted_cmb_reservoir_j_m3,source_count_com3,source_energy_j_com3,absorbed_count_com3,geometry_work_j_com3,retained_count_com3,retained_age_sum_com_s,retained_age2_sum_com_s2,positive_cohorts,zero_cohorts,first_moment_underflows,second_moment_underflows"
        );
        let rules = format!(
            "step,rule_id,energy_bits,energy_ev,refinement,k_HI_per_s,k_HeI_per_s,k_HeII_per_s,k_DI_per_s,tau,nodes,panels,{},{}",
            measure_header("kernel_emitted_unit"),
            measure_header("kernel_survivor_unit")
        );
        let panels = format!(
            "step,rule_id,panel_id,left_x,right_x,width_from_actual_weights,width_bits_match,nominal_width_s,optical_width,represented_birth_left_s,represented_birth_right_s,represented_width_s,represented_width_defect_s,physical_bound_excess_s,optical_bound_excess,exact_survival_per_unit_born,reference_underflow,{}",
            measure_header("local_kernel_survivor_unit")
        );
        let templates = format!(
            "step,template_id,rule_id,spectral_index,angular_index,energy_ev,raw_birth_direction1,raw_birth_direction2,raw_birth_direction3,midpoint_rate_com3_s,constant_j_born_com3,first_cohort_index,birth_count,native_born_com3,after_photo_count_com3,after_photo_age_sum_com_s,after_photo_age2_sum_com_s2,accepted_count_com3,accepted_age_sum_com_s,accepted_age2_sum_com_s2,accepted_positive_cohorts,accepted_zero_cohorts,accepted_first_moment_underflows,accepted_second_moment_underflows,{},{}",
            measure_header("native_source_frozen_emitted"),
            measure_header("native_source_frozen_survivor")
        );
        Ok(Self {
            steps: open(path, "MONITOR_STEPS.csv", &steps)?,
            rules: open(path, "MONITOR_RULES.csv", &rules)?,
            panels: open(path, "MONITOR_PANELS.csv", &panels)?,
            templates: open(path, "MONITOR_TEMPLATES.csv", &templates)?,
            births: open(
                path,
                "MONITOR_BIRTHS.csv",
                "step,cohort_index,template_id,rule_id,node_id,panel_id,target_age_x,emission_weight,actual_birth_time_s,actual_clock_age_x,clock_age_defect_x,clock_age_defect_s,source_amplitude_ratio,born_count_com3,born_count_underflow,after_photo_count_com3,accepted_count_com3,native_source_frozen_survivor_com3,native_source_frozen_underflow,birth_a1,birth_a2,birth_a3,birth_H1_per_s,birth_H2_per_s,birth_H3_per_s,K1_ev_scale,K2_ev_scale,K3_ev_scale,end_energy_ev,end_direction1,end_direction2,end_direction3",
            )?,
            final_cohorts: open(
                path,
                "MONITOR_FINAL_COHORTS.csv",
                "cohort_index,final_time_s,retained_count_com3,age_s,energy_ev,direction1,direction2,direction3",
            )?,
            steps_written: 0,
            births_written: 0,
        })
    }

    pub fn write_step(&mut self, data: &StepMonitor) -> io::Result<()> {
        let invalid = || io::Error::new(io::ErrorKind::InvalidData, "incomplete accepted monitor");
        let accepted = data.accepted.as_ref().ok_or_else(invalid)?;
        let mut row = Row::new(&mut self.steps);
        row.text(data.step_id)?;
        row.numbers([data.t0, data.tm, data.t1, data.dt])?;
        for value in [
            data.prior_cohorts,
            data.births.len(),
            data.rules.len(),
            data.templates.len(),
        ] {
            row.text(value)?;
        }
        row.numbers(IsotopeSpecies::ALL.map(|s| data.rate_gas.nuclei.density_m3(s)))?;
        row.number(data.rate_gas.thermal_j_m3)?;
        row.number(data.rate_gas.eos().map_err(|_| invalid())?.temperature_k)?;
        for g in [data.midpoint_geometry, data.end_geometry] {
            row.numbers(g.scale_factors)?;
            row.numbers(g.hubble_per_s)?;
            row.number(g.volume_factor().map_err(|_| invalid())?)?;
        }
        row.numbers(accepted.populations_m3)?;
        row.numbers([
            accepted.thermal_j_m3,
            accepted.binding_j_m3,
            accepted.escaped_j_m3,
            accepted.cmb_reservoir_j_m3,
            accepted.source_count_com3,
            accepted.source_energy_j_com3,
            accepted.absorbed_count_com3,
            accepted.geometry_work_j_com3,
            accepted.photons.count,
            accepted.photons.age_sum_s,
            accepted.photons.age2_sum_s2,
        ])?;
        row.text(accepted.photons.positive_cohorts)?;
        row.text(accepted.photons.zero_cohorts)?;
        row.text(accepted.photons.first_moment_underflows)?;
        row.text(accepted.photons.second_moment_underflows)?;
        row.end()?;

        for rule in &data.rules {
            let mut row = Row::new(&mut self.rules);
            row.text(data.step_id)?;
            row.text(rule.rule_id)?;
            row.text(format_args!("{:016x}", rule.energy_ev.to_bits()))?;
            row.number(rule.energy_ev)?;
            row.text(rule.refinement)?;
            row.numbers(rule.rates_per_s)?;
            row.number(rule.tau)?;
            row.text(rule.nodes.len())?;
            row.text(rule.panels.len())?;
            row.measure(rule.frozen_kernel_reference.emitted)?;
            row.measure(rule.frozen_kernel_reference.survivors)?;
            row.end()?;
            for panel in &rule.panels {
                let mut row = Row::new(&mut self.panels);
                row.text(data.step_id)?;
                row.text(rule.rule_id)?;
                row.text(panel.panel_id)?;
                row.numbers([panel.left, panel.right, panel.width_from_weights])?;
                row.text(panel.width_bits_match)?;
                row.numbers([
                    panel.nominal_width_s,
                    panel.optical_width,
                    panel.represented_birth_left_s,
                    panel.represented_birth_right_s,
                    panel.represented_width_s,
                    panel.represented_width_defect_s,
                    panel.physical_bound_excess_s,
                    panel.optical_bound_excess,
                    panel.exact_survival_per_unit_born,
                ])?;
                row.text(panel.reference_underflow)?;
                row.measure(panel.local_reference.survivors)?;
                row.end()?;
            }
        }
        for template in &data.templates {
            let mut row = Row::new(&mut self.templates);
            row.text(data.step_id)?;
            for value in [
                template.template_id,
                template.rule_id,
                template.spectral_index,
                template.angular_index,
            ] {
                row.text(value)?;
            }
            row.number(template.energy_ev)?;
            row.numbers(template.direction)?;
            row.numbers([template.midpoint_rate_com3_s, template.constant_j_born_com3])?;
            row.text(data.prior_cohorts + template.first_birth_row)?;
            row.text(template.birth_count)?;
            row.number(template.native_born_com3)?;
            for m in [template.native_after_photo, template.native_accepted] {
                row.numbers([m.count, m.age_sum_s, m.age2_sum_s2])?;
            }
            row.text(template.native_accepted.positive_cohorts)?;
            row.text(template.native_accepted.zero_cohorts)?;
            row.text(template.native_accepted.first_moment_underflows)?;
            row.text(template.native_accepted.second_moment_underflows)?;
            row.measure(template.native_source_frozen_reference.emitted)?;
            row.measure(template.native_source_frozen_reference.survivors)?;
            row.end()?;
        }
        for record in &data.births {
            let mut row = Row::new(&mut self.births);
            for value in [
                data.step_id,
                record.cohort_index,
                record.template_id,
                record.rule_id,
                record.node_id,
                record.node_id / 2,
            ] {
                row.text(value)?;
            }
            row.numbers([
                record.target_age,
                record.emission_weight,
                record.birth.birth_time_s,
                record.clock_age,
                record.clock_age_defect,
                record.clock_age_defect_s,
                record.source_amplitude_ratio,
                record.birth.n_comoving_m3,
            ])?;
            row.text(record.born_count_underflow)?;
            row.numbers([
                record.after_photo_com3.ok_or_else(invalid)?,
                record.accepted_com3.ok_or_else(invalid)?,
                record.frozen_source_survivor_com3,
            ])?;
            row.text(record.frozen_source_underflow)?;
            row.numbers(record.birth.birth_geometry.scale_factors)?;
            row.numbers(record.birth.birth_geometry.hubble_per_s)?;
            row.numbers(record.killing_ev_scale)?;
            row.number(record.end_energy_ev.ok_or_else(invalid)?)?;
            row.numbers(record.end_direction.ok_or_else(invalid)?)?;
            row.end()?;
        }
        self.steps_written += 1;
        self.births_written += data.births.len();
        self.flush()
    }

    pub fn write_final(
        &mut self,
        state: &AgeHistory,
        geometry: &GeometrySnapshot,
    ) -> io::Result<()> {
        for (index, cohort) in state.cohorts.iter().enumerate() {
            let ray = cohort
                .ray_at(geometry)
                .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "final retained ray"))?;
            let mut row = Row::new(&mut self.final_cohorts);
            row.text(index)?;
            row.numbers([
                state.time_s,
                cohort.n_comoving_m3,
                state.time_s - cohort.birth_time_s,
                ray.energy_ev,
            ])?;
            row.numbers(ray.direction)?;
            row.end()?;
        }
        self.flush()
    }

    pub fn flush(&mut self) -> io::Result<()> {
        for out in [
            &mut self.steps,
            &mut self.rules,
            &mut self.panels,
            &mut self.templates,
            &mut self.births,
            &mut self.final_cohorts,
        ] {
            out.flush()?;
            out.get_ref().sync_data()?;
        }
        Ok(())
    }
}
