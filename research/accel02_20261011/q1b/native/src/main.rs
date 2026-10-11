//! Versioned integrated-cell bridge. No opacity closure, Jacobian or history admission.
use rei_microphysics::{
    axisym_coupled_derivative,
    AxisymCoupledState, AxisymLocalSources, AxisymmetricPoint, HHeModel,
    IsotopeNumberState, IsotopeSpecies,
};
use std::io::{self, BufRead, Write};
use rei_microphysics::{igm_state::IgmGasState, igm_thermal::{igm_point_rhs, IgmPhotoInput}};

// The frozen cross-section turn-on energies differ from chemical chi.
const SIGMA_THRESHOLD_EV: [f64; 3] = [13.60, 24.59, 54.42];
#[derive(Clone, Copy, Debug)]
struct Cell {
    mu: f64,
    redshift_r: f64,
    lambda_per_s: f64,
    number_reference_cm3: f64,
    energy_reference_ev_cm3: f64,
    source_number_reference_cm3_s: f64,
    source_energy_reference_ev_cm3_s: f64,
    k0_s: [f64; 3],
    ke_ev_s: [f64; 3],
}

#[derive(Clone, Debug)]
struct Input {
    time_s: f64,
    a_rel: f64,
    b: f64,
    h_per_s: f64,
    s_per_s: f64,
    n_h_cm3: f64,
    n_he_cm3: f64,
    fractions: [f64; 3],
    w_ev_per_h: f64,
    tcmb_k: f64,
    cells: Vec<Cell>,
}

fn scaled_residual(residual: f64, scale: f64) -> f64 {
    if scale == 0. { residual } else { residual / scale }
}

fn rhs(input: &Input) -> Result<Vec<f64>, String> {
    let geometry = AxisymmetricPoint::new(input.a_rel, input.b, input.h_per_s, input.s_per_s)
        .map_err(|e| e.to_string())?;
    let volume = input.a_rel.powi(3);
    if !volume.is_finite() || volume <= 0. || !input.time_s.is_finite() {
        return Err("REFERENCE_VOLUME_OR_TIME_DOMAIN".into());
    }
    if input.time_s < 0. { return Err("NEGATIVE_TIME".into()); }
    let gas = HHeModel::controlled_fixture();
    let u = input.w_ev_per_h * input.n_h_cm3 * gas.ev_erg;
    let state = IgmGasState::new(input.fractions, input.w_ev_per_h * gas.ev_erg)
        .map_err(|e| e.to_string())?;
    state.eos(input.n_h_cm3, input.n_he_cm3).map_err(|e| e.to_string())?;
    let [h, he1, he2] = input.fractions;
    let lower = [input.n_h_cm3 * (1. - h), input.n_he_cm3 * (1. - (he1 + he2)), input.n_he_cm3 * he1];
    let mut photo_heat_per_absorber = [0.; 3];
    let mut gamma = [0.; 3];
    let mut cell_dot = Vec::with_capacity(2 * input.cells.len());
    let mut number_dot_sum = 0.;
    let mut number_dot_abs_sum = 0.;
    let mut photon_number = 0.;
    let mut photon_energy = 0.;
    let mut photon_delta = 0.;
    let mut source_number_ref = 0.;
    let mut source_energy_ref = 0.;
    let mut absorbed_number_ref = 0.;
    let mut absorbed_energy_ref = 0.;

    for cell in &input.cells {
        let values = [cell.mu, cell.redshift_r, cell.lambda_per_s,
            cell.number_reference_cm3, cell.energy_reference_ev_cm3,
            cell.source_number_reference_cm3_s, cell.source_energy_reference_ev_cm3_s];
        if !values.iter().chain(cell.k0_s.iter()).chain(cell.ke_ev_s.iter()).all(|x| x.is_finite())
            || cell.mu.abs() > 1. || cell.redshift_r <= 0.
            || values[3..].iter().chain(cell.k0_s.iter()).chain(cell.ke_ev_s.iter()).any(|x| *x < 0.) {
            return Err("CELL_DOMAIN".into());
        }
        // R labels the fixed-q-to-current-energy map. Its consistency with q
        // bounds and previous epochs is a caller obligation, not proved here.
        let lambda = input.h_per_s + input.s_per_s * (3. * cell.mu * cell.mu - 1.);
        let lambda_scale = input.h_per_s.abs() + (input.s_per_s * (3. * cell.mu * cell.mu - 1.)).abs();
        if (lambda - cell.lambda_per_s).abs() > 64. * f64::EPSILON * lambda_scale {
            return Err("CELL_LAMBDA_GEOMETRY_MISMATCH".into());
        }
        if (cell.number_reference_cm3 == 0.) != (cell.energy_reference_ev_cm3 == 0.) {
            return Err("CELL_EMPTY_MOMENT_MISMATCH".into());
        }
        if cell.energy_reference_ev_cm3 > 50_000. * cell.number_reference_cm3 {
            return Err("CELL_RADIATION_MEAN_ABOVE_PROVIDER_BAND".into());
        }
        if cell.number_reference_cm3 == 0. && cell.k0_s.iter().chain(cell.ke_ev_s.iter()).any(|x| *x != 0.) {
            return Err("CELL_EMPTY_OPACITY".into());
        }
        if (cell.source_number_reference_cm3_s == 0.) != (cell.source_energy_reference_ev_cm3_s == 0.) {
            return Err("CELL_SOURCE_MOMENT_MISMATCH".into());
        }
        let source_energy = cell.source_energy_reference_ev_cm3_s;
        if source_energy < 10. * cell.source_number_reference_cm3_s
            || source_energy > 50_000. * cell.source_number_reference_cm3_s {
            return Err("CELL_SOURCE_BAND".into());
        }
        let mut absorbed_ref = 0.;
        let mut absorbed_energy_ev_ref = 0.;
        for a in 0..3 {
            if (cell.k0_s[a] == 0.) != (cell.ke_ev_s[a] == 0.)
                || cell.ke_ev_s[a] < SIGMA_THRESHOLD_EV[a] * cell.k0_s[a]
                || cell.ke_ev_s[a] > 50_000. * cell.k0_s[a] {
                return Err("CELL_OPACITY_MOMENT_DOMAIN".into());
            }
            // No division by n_abs: the zero-absorber boundary is regular.
            gamma[a] += cell.k0_s[a] / volume;
            photo_heat_per_absorber[a] += (cell.ke_ev_s[a] - gas.threshold_ev[a] * cell.k0_s[a]) * gas.ev_erg / volume;
            absorbed_ref += lower[a] * cell.k0_s[a];
            absorbed_energy_ev_ref += lower[a] * cell.ke_ev_s[a];
        }
        let ndot = cell.source_number_reference_cm3_s - absorbed_ref;
        let udot = cell.source_energy_reference_ev_cm3_s - absorbed_energy_ev_ref
            - cell.lambda_per_s * cell.energy_reference_ev_cm3;
        cell_dot.extend([ndot, udot]);
        number_dot_sum += ndot;
        number_dot_abs_sum += ndot.abs();
        photon_number += cell.number_reference_cm3 / volume;
        let proper_energy = cell.energy_reference_ev_cm3 * gas.ev_erg / volume;
        photon_energy += proper_energy;
        photon_delta += 0.5 * (3. * cell.mu * cell.mu - 1.) * proper_energy;
        source_number_ref += cell.source_number_reference_cm3_s;
        source_energy_ref += source_energy * gas.ev_erg;
        absorbed_number_ref += absorbed_ref;
        absorbed_energy_ref += absorbed_energy_ev_ref * gas.ev_erg;
    }
    // Exact imported Grackle subset at the CURRENT gas stage. It owns expansion,
    // cooling, Case-A escape and signed CMB exchange; no FT03 call or guard change.
    let atomic = igm_point_rhs(&state, input.n_h_cm3, input.n_he_cm3,
        input.h_per_s, input.tcmb_k, IgmPhotoInput { gamma_s: gamma,
            heat_erg_per_absorber_s: photo_heat_per_absorber })
        .map_err(|e| e.to_string())?;
    let j = [atomic.species_chemical_cm3_s[1], -atomic.species_chemical_cm3_s[2],
             atomic.species_chemical_cm3_s[4]];
    let thermal_power = atomic.thermal_micro_erg_cm3_s;
    let internal_power = atomic.binding_micro_erg_cm3_s;
    let photon_power = (source_energy_ref - absorbed_energy_ref) / volume;
    let source_power = source_energy_ref / volume;
    let escape = atomic.escape_erg_cm3_s;
    let cmb = atomic.cmb_to_gas_erg_cm3_s;
    let mut densities = [0.; 13];
    for (species, value) in [
        (IsotopeSpecies::H1Neutral, lower[0]),
        (IsotopeSpecies::H1Ionized, input.n_h_cm3 * h),
        (IsotopeSpecies::He4Neutral, lower[1]),
        (IsotopeSpecies::He4SinglyIonized, input.n_he_cm3 * he1),
        (IsotopeSpecies::He4DoublyIonized, input.n_he_cm3 * he2),
    ] { densities[species as usize] = value * 1e6; }
    let coupled = AxisymCoupledState {
        isotopes: IsotopeNumberState::new(densities).map_err(|e| e.to_string())?,
        thermal_energy_j_m3: u * 0.1,
        photon_number_m3: photon_number * 1e6,
        photon_energy_j_m3: photon_energy * 0.1,
        photon_delta_pressure_j_m3: photon_delta * 0.1,
    };
    let mut species_source = [0.; 13];
    for (species, value) in [
        (IsotopeSpecies::H1Neutral, -j[0]),
        (IsotopeSpecies::H1Ionized, j[0]),
        (IsotopeSpecies::He4Neutral, -j[1]),
        (IsotopeSpecies::He4SinglyIonized, j[1] - j[2]),
        (IsotopeSpecies::He4DoublyIonized, j[2]),
    ] { species_source[species as usize] = value * 1e6; }
    let sources = AxisymLocalSources {
        species_m3_s: species_source,
        electron_m3_s: j.iter().sum::<f64>() * 1e6,
        photon_number_m3_s: (source_number_ref - absorbed_number_ref) / volume * 1e6,
        photon_power_j_m3_s: photon_power * 0.1,
        thermal_power_j_m3_s: thermal_power * 0.1,
        internal_power_j_m3_s: internal_power * 0.1,
        escape_power_j_m3_s: escape * 0.1,
        external_power_j_m3_s: (source_power + cmb) * 0.1,
    };
    // Actual existing AXI derivative, including all native source-ledger guards.
    let derivative = axisym_coupled_derivative(input.time_s, geometry, &coupled, gas.kb_erg_k * 1e-7,
        |_, _| Ok(sources)).map_err(|e| e.to_string())?;
    let dx = [
        (derivative.species_m3_s[IsotopeSpecies::H1Ionized as usize] / 1e6 + 3. * input.h_per_s * input.n_h_cm3 * h) / input.n_h_cm3,
        if input.n_he_cm3 == 0. { 0. } else { (derivative.species_m3_s[IsotopeSpecies::He4SinglyIonized as usize] / 1e6 + 3. * input.h_per_s * input.n_he_cm3 * he1) / input.n_he_cm3 },
        if input.n_he_cm3 == 0. { 0. } else { (derivative.species_m3_s[IsotopeSpecies::He4DoublyIonized as usize] / 1e6 + 3. * input.h_per_s * input.n_he_cm3 * he2) / input.n_he_cm3 },
    ];
    let wdot = derivative.thermal_energy_j_m3_s * 10. / (input.n_h_cm3 * gas.ev_erg)
        + 3. * input.h_per_s * input.w_ev_per_h;
    let work_ref = (input.h_per_s * photon_energy + 2. * input.s_per_s * photon_delta + 2. * input.h_per_s * u) * volume;
    let number_residual = scaled_residual(number_dot_sum - source_number_ref + absorbed_number_ref,
        number_dot_abs_sum + source_number_ref + absorbed_number_ref);
    let energy_terms = [photon_power, thermal_power, internal_power, escape, -source_power, -cmb];
    let energy_residual = scaled_residual(energy_terms.iter().sum(), energy_terms.iter().map(|x| x.abs()).sum());
    let mut output = vec![dx[0], dx[1], dx[2], wdot, escape * volume, work_ref, source_energy_ref,
        absorbed_number_ref, gamma[0], gamma[1], gamma[2], derivative.temperature_k, number_residual, energy_residual, cmb * volume];
    output.extend(cell_dot);
    if output.iter().any(|x| !x.is_finite()) { return Err("RESULT_OVERFLOW".into()); }
    Ok(output)
}

fn parse_f64(word: Option<&str>) -> Result<f64, String> {
    let value = word.ok_or("MISSING_NUMBER")?.parse::<f64>().map_err(|_| "INVALID_NUMBER")?;
    if value.is_finite() { Ok(value) } else { Err("NONFINITE_NUMBER".into()) }
}

fn command(line: &str) -> Result<Vec<f64>, String> {
    let mut words = line.split_whitespace();
    let result = match words.next().ok_or("EMPTY_COMMAND")? {
        "CELL_RHS_V1" => {
            let mut p = [0.; 12];
            for value in &mut p { *value = parse_f64(words.next())?; }
            let count_value = parse_f64(words.next())?;
            if !(0. ..=1_000_000.).contains(&count_value) || count_value.fract() != 0. {
                return Err("INVALID_CELL_COUNT".into());
            }
            let count = count_value as usize;
            let mut cells = Vec::with_capacity(count);
            for _ in 0..count {
                let mut v = [0.; 13];
                for value in &mut v { *value = parse_f64(words.next())?; }
                cells.push(Cell { mu: v[0], redshift_r: v[1], lambda_per_s: v[2],
                    number_reference_cm3: v[3], energy_reference_ev_cm3: v[4],
                    source_number_reference_cm3_s: v[5], source_energy_reference_ev_cm3_s: v[6],
                    k0_s: [v[7], v[8], v[9]], ke_ev_s: [v[10], v[11], v[12]] });
            }
            rhs(&Input { time_s: p[0], a_rel: p[1], b: p[2], h_per_s: p[3], s_per_s: p[4],
                n_h_cm3: p[5], n_he_cm3: p[6], fractions: [p[7], p[8], p[9]], w_ev_per_h: p[10], tcmb_k: p[11], cells })?
        }
        _ => return Err("UNKNOWN_COMMAND".into()),
    };
    if words.next().is_some() { return Err("EXTRA_ARGUMENT".into()); }
    Ok(result)
}

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = stdout.lock();
    for line in stdin.lock().lines() {
        let line = line?;
        match command(&line) {
            Ok(values) => {
                write!(out, "OK")?;
                for value in values { write!(out, " {value:.17e}")?; }
                writeln!(out)?;
            }
            Err(error) => writeln!(out, "ERR {error}")?,
        }
        out.flush()?;
    }
    Ok(())
}

