//! Full semantic fingerprints, never used to change numerical work.
use crate::batch::Ledger;
use rei_br06_reference::reference::PathResult;

pub fn path_bits(p: &PathResult) -> Vec<u64> {
    let mut bits = vec![
        p.survival,
        p.optical_depth,
        p.chemical_ev,
        p.absorbed_energy_ev,
        p.surviving_energy_ev,
        p.geometry_work_ledger_ev,
        p.geometry_work_independent_ev,
        p.end_energy_ev,
        p.number_residual,
        p.energy_residual_ev,
        p.photo_split_residual_ev,
        p.max_inverse_residual,
        p.opacity_weight_sum,
        p.event_weight_sum,
    ]
    .into_iter()
    .map(f64::to_bits)
    .collect::<Vec<_>>();
    bits.extend(p.events.map(f64::to_bits));
    bits.extend(p.heat_ev.map(f64::to_bits));
    bits.extend(p.end_direction.map(f64::to_bits));
    bits.extend([
        p.samples as u64,
        p.inverse_iterations as u64,
        p.slabs as u64,
        p.threshold_crossings as u64,
    ]);
    bits.extend(
        [
            p.represented_survival_underflow,
            p.represented_opacity_underflow,
            p.represented_absorption_underflow,
            p.thin_time_route,
        ]
        .map(u64::from),
    );
    bits.extend(p.represented_species_underflow.map(u64::from));
    bits.extend(p.represented_heat_underflow.map(u64::from));
    bits
}

pub fn ledger_bits(p: &Ledger) -> Vec<u64> {
    let mut bits = [
        p.born,
        p.surviving,
        p.age_sum_s,
        p.age2_sum_s2,
        p.chemical_j,
        p.source_energy_j,
        p.surviving_energy_j,
        p.absorbed_energy_j,
        p.work_ledger_j,
        p.work_independent_j,
        p.q2_numerator_j,
        p.max_path_number_residual,
        p.max_path_energy_relative_residual,
        p.max_inverse_residual,
    ]
    .map(f64::to_bits)
    .to_vec();
    bits.extend(p.events.map(f64::to_bits));
    bits.extend(p.heat_j.map(f64::to_bits));
    bits.extend(
        [
            p.cohorts,
            p.samples,
            p.inversions,
            p.threshold_crossings,
            p.zero_born_cohorts,
            p.represented_survival_underflows,
            p.represented_opacity_underflows,
            p.represented_absorption_underflows,
            p.represented_species_underflows,
            p.represented_heat_underflows,
            p.thin_time_paths,
        ]
        .map(|n| n as u64),
    );
    bits
}
