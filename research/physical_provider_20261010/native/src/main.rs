//! Conditional research consumer; does not modify PhysicalHistory admission.
use rei_microphysics::{
    axisym_coupled_derivative, ft03_coefficients, ft03_rhs, Absorber, AtomicProvider,
    AxisymCoupledState, AxisymLocalSources, AxisymmetricPoint, Ft03Model, HHeState,
    IsotopeNumberState, IsotopeSpecies,
};
use std::io::{self, BufRead, Write};

const ABSORBERS: [Absorber; 3] = [Absorber::HI, Absorber::HeI, Absorber::HeII];

#[derive(Clone, Copy, Debug)]
struct Node {
    energy_ev: f64,
    mu: f64,
    number_reference_cm3: f64,
    source_reference_cm3_s: f64,
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
    nodes: Vec<Node>,
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
    let mut model = Ft03Model::controlled().map_err(|e| e.to_string())?;
    model.gas.n_h_cm3 = input.n_h_cm3;
    model.gas.n_he_cm3 = input.n_he_cm3;
    let gas = &model.gas;
    let u = input.w_ev_per_h * input.n_h_cm3 * gas.ev_erg;
    let state = HHeState {
        fractions: input.fractions,
        u_erg_cm3: u,
        photon_cm3: [0.; 3],
        escaped_erg_cm3: 0.,
    };
    // Exactly native RR/CI/DR and native thermal moments, evaluated at stage T.
    let atomic = ft03_rhs(&model, &state).map_err(|e| e.to_string())?;
    let [h, he1, he2] = input.fractions;
    let lower = [input.n_h_cm3 * (1. - h), input.n_he_cm3 * (1. - (he1 + he2)), input.n_he_cm3 * he1];
    let provider = AtomicProvider::reference();
    let mut photo = [0.; 3];
    let mut gamma = [0.; 3];
    let mut photon_dot = Vec::with_capacity(input.nodes.len());
    let mut photon_number = 0.;
    let mut photon_energy = 0.;
    let mut photon_delta = 0.;
    let mut source_number_ref = 0.;
    let mut source_energy_ref = 0.;
    let mut absorbed_number_ref = 0.;
    let mut absorbed_energy_ref = 0.;
    let mut photo_heat = 0.;
    for node in &input.nodes {
        if ![node.energy_ev, node.mu, node.number_reference_cm3, node.source_reference_cm3_s]
            .iter().all(|x| x.is_finite())
            || node.energy_ev <= 0. || node.mu.abs() > 1.
            || node.number_reference_cm3 < 0. || node.source_reference_cm3_s < 0.
        {
            return Err("PHOTON_NODE_DOMAIN".into());
        }
        let number = node.number_reference_cm3 / volume;
        let energy = node.energy_ev * gas.ev_erg;
        let mut absorbed_ref = 0.;
        for (a, absorber) in ABSORBERS.iter().enumerate() {
            let sigma = provider.cross_section(*absorber, node.energy_ev).map_err(|e| e.to_string())?;
            let rate = gas.c_cm_s * sigma * number;
            let event = lower[a] * rate;
            gamma[a] += rate;
            photo[a] += event;
            absorbed_ref += event * volume;
            photo_heat += event * (node.energy_ev - gas.threshold_ev[a]) * gas.ev_erg;
        }
        photon_dot.push(node.source_reference_cm3_s - absorbed_ref);
        photon_number += number;
        photon_energy += number * energy;
        photon_delta += 0.5 * (3. * node.mu * node.mu - 1.) * number * energy;
        source_number_ref += node.source_reference_cm3_s;
        source_energy_ref += node.source_reference_cm3_s * energy;
        absorbed_number_ref += absorbed_ref;
        absorbed_energy_ref += absorbed_ref * energy;
    }
    let mut j = std::array::from_fn::<_, 3, _>(|a|
        atomic.collision_per_cm3_s[a] - atomic.recombination_per_cm3_s[a] + photo[a]);
    j[1] -= atomic.dr_per_cm3_s.iter().sum::<f64>();
    let thermal_power = atomic.derivative[3] + photo_heat;
    let internal_power = (0..3).map(|a| j[a] * gas.threshold_ev[a] * gas.ev_erg).sum::<f64>();
    let photon_power = (source_energy_ref - absorbed_energy_ref) / volume;
    let source_power = source_energy_ref / volume;
    let escape = atomic.escaped_energy_rate;
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
        external_power_j_m3_s: source_power * 0.1,
    };
    // Actual existing AXI derivative, including all native source-ledger guards.
    let derivative = axisym_coupled_derivative(input.time_s, geometry, &coupled, gas.kb_erg_k * 1e-7,
        |_, _| Ok(sources)).map_err(|e| e.to_string())?;
    let dx = [
        (derivative.species_m3_s[IsotopeSpecies::H1Ionized as usize] / 1e6 + 3. * input.h_per_s * input.n_h_cm3 * h) / input.n_h_cm3,
        (derivative.species_m3_s[IsotopeSpecies::He4SinglyIonized as usize] / 1e6 + 3. * input.h_per_s * input.n_he_cm3 * he1) / input.n_he_cm3,
        (derivative.species_m3_s[IsotopeSpecies::He4DoublyIonized as usize] / 1e6 + 3. * input.h_per_s * input.n_he_cm3 * he2) / input.n_he_cm3,
    ];
    let wdot = derivative.thermal_energy_j_m3_s * 10. / (input.n_h_cm3 * gas.ev_erg)
        + 3. * input.h_per_s * input.w_ev_per_h;
    let work_ref = (input.h_per_s * photon_energy + 2. * input.s_per_s * photon_delta + 2. * input.h_per_s * u) * volume;
    let number_residual = scaled_residual(photon_dot.iter().sum::<f64>() - source_number_ref + absorbed_number_ref,
        photon_dot.iter().map(|x| x.abs()).sum::<f64>() + source_number_ref + absorbed_number_ref);
    let energy_terms = [photon_power, thermal_power, internal_power, escape, -source_power];
    let energy_residual = scaled_residual(energy_terms.iter().sum(), energy_terms.iter().map(|x| x.abs()).sum());
    let mut output = vec![dx[0], dx[1], dx[2], wdot, escape * volume, work_ref, source_energy_ref,
        absorbed_number_ref, gamma[0], gamma[1], gamma[2], derivative.temperature_k, number_residual, energy_residual];
    output.extend(photon_dot);
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
        "RATES" => {
            let c = ft03_coefficients(parse_f64(words.next())?).map_err(|e| e.to_string())?;
            c.alpha_rr_cm3_s.into_iter().chain(c.beta_ci_cm3_s).chain(c.alpha_dr_cm3_s)
                .chain(c.rr_kinetic_erg_cm3_s).chain(c.dr_energy_erg).collect()
        }
        "SIGMA" => {
            let provider = AtomicProvider::reference();
            let mut values = Vec::new();
            for word in words.by_ref() {
                let energy = parse_f64(Some(word))?;
                for absorber in ABSORBERS {
                    values.push(provider.cross_section(absorber, energy).map_err(|e| e.to_string())?);
                }
            }
            if values.is_empty() { return Err("MISSING_ENERGY".into()); }
            values
        }
        "RHS" => {
            let mut p = [0.; 11];
            for value in &mut p { *value = parse_f64(words.next())?; }
            let count_value = parse_f64(words.next())?;
            if !(0. ..=1_000_000.).contains(&count_value) || count_value.fract() != 0. {
                return Err("INVALID_NODE_COUNT".into());
            }
            let count = count_value as usize;
            let mut nodes = Vec::with_capacity(count);
            for _ in 0..count {
                nodes.push(Node { energy_ev: parse_f64(words.next())?, mu: parse_f64(words.next())?,
                    number_reference_cm3: parse_f64(words.next())?, source_reference_cm3_s: parse_f64(words.next())? });
            }
            rhs(&Input { time_s: p[0], a_rel: p[1], b: p[2], h_per_s: p[3], s_per_s: p[4],
                n_h_cm3: p[5], n_he_cm3: p[6], fractions: [p[7], p[8], p[9]], w_ev_per_h: p[10], nodes })?
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

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture() -> Input {
        let model = Ft03Model::controlled().unwrap();
        let state = model.initial_state();
        Input { time_s: 0., a_rel: 1., b: 0., h_per_s: 0., s_per_s: 0., n_h_cm3: model.gas.n_h_cm3,
            n_he_cm3: model.gas.n_he_cm3, fractions: state.fractions,
            w_ev_per_h: state.u_erg_cm3 / (model.gas.n_h_cm3 * model.gas.ev_erg),
            nodes: (0..3).map(|k| Node { energy_ev: model.gas.photon_energy_ev[k], mu: 1. / 3_f64.sqrt(),
                number_reference_cm3: state.photon_cm3[k], source_reference_cm3_s: 0. }).collect() }
    }
    fn close(a: f64, b: f64) { assert!((a - b).abs() <= 5e-13 * a.abs().max(b.abs()).max(1e-100), "{a:e} != {b:e}"); }

    #[test]
    fn arbitrary_node_consumer_matches_native_three_group_ft03() {
        let input = fixture();
        let output = rhs(&input).unwrap();
        let model = Ft03Model::controlled().unwrap();
        let expected = ft03_rhs(&model, &model.initial_state()).unwrap();
        for (got, want) in output[..3].iter().zip(expected.derivative[..3].iter()) { close(*got, *want); }
        close(output[3], expected.derivative[3] / (input.n_h_cm3 * model.gas.ev_erg));
        close(output[4], expected.escaped_energy_rate);
        for k in 0..3 { close(output[14+k], expected.derivative[4+k]); }
        close(output[11], 50_000.);
        assert!(output[12].abs() < 1e-14 && output[13].abs() < 1e-14);
    }

    #[test]
    fn proper_si_conversion_and_reference_volume_are_consistent() {
        let first = fixture();
        let mut second = first.clone();
        second.a_rel = 2.;
        for node in &mut second.nodes { node.number_reference_cm3 *= 8.; }
        let a = rhs(&first).unwrap();
        let b = rhs(&second).unwrap();
        for i in [0, 1, 2, 3, 8, 9, 10, 11] { close(a[i], b[i]); }
        for i in [4, 7, 14, 15, 16] { close(8. * a[i], b[i]); }
    }

    #[test]
    fn expansion_and_axisymmetric_shear_have_derived_work_signs() {
        let mut input = fixture();
        for node in &mut input.nodes { node.mu = 1.; }
        let no_expansion = rhs(&input).unwrap();
        input.h_per_s = 2e-17;
        input.s_per_s = 3e-18;
        let expanded = rhs(&input).unwrap();
        let g = Ft03Model::controlled().unwrap().gas;
        let u = input.w_ev_per_h * input.n_h_cm3 * g.ev_erg;
        let radiation = input.nodes.iter().map(|p| p.energy_ev * p.number_reference_cm3 * g.ev_erg).sum::<f64>();
        close(expanded[3] - no_expansion[3], -2. * input.h_per_s * input.w_ev_per_h);
        close(expanded[5], (input.h_per_s + 2. * input.s_per_s) * radiation + 2. * input.h_per_s * u);
        for i in 0..3 { close(expanded[i], no_expansion[i]); }
    }

    #[test]
    fn source_injection_is_external_power_and_no_instant_gas_heat() {
        let a = fixture();
        let mut b = a.clone();
        b.nodes[0].source_reference_cm3_s = 1e-15;
        let baseline = rhs(&a).unwrap();
        let injected = rhs(&b).unwrap();
        for i in [0, 1, 2, 3, 4, 7, 8, 9, 10, 11] { close(injected[i], baseline[i]); }
        close(injected[14] - baseline[14], 1e-15);
        close(injected[6], 1e-15 * 20. * 1.602_176_634e-12);
        assert!(injected[13].abs() < 1e-14);
    }

    #[test]
    fn domain_errors_are_not_clipped_or_replaced() {
        let good = fixture();
        let mut bad = good.clone(); bad.fractions[0] = 1.01; assert!(rhs(&bad).is_err());
        bad = good.clone(); bad.w_ev_per_h *= 0.1; assert_eq!(rhs(&bad).unwrap_err(), "FT03_TEMPERATURE_DOMAIN");
        bad = good.clone(); bad.nodes[0].number_reference_cm3 = -1.; assert_eq!(rhs(&bad).unwrap_err(), "PHOTON_NODE_DOMAIN");
        bad = good.clone(); bad.nodes[0].mu = 1.1; assert!(rhs(&bad).is_err());
        bad = good; bad.nodes[0].energy_ev = 50001.; assert_eq!(rhs(&bad).unwrap_err(), "VERNER_ENERGY_DOMAIN");
        assert!(command("RATES NaN").is_err());
        assert!(command("RATES 50000 extra").is_err());
        assert!(command("RHS 0 1").is_err());
    }

    #[test]
    fn rates_sigma_protocol_has_documented_order() {
        assert_eq!(command("RATES 50000").unwrap().len(), 13);
        let sigmas = command("SIGMA 10 20 70").unwrap();
        assert_eq!(sigmas.len(), 9);
        assert_eq!(&sigmas[..3], &[0., 0., 0.]);
        assert!(sigmas[3] > 0. && sigmas[4] == 0. && sigmas[5] == 0.);
        assert!(sigmas[6..].iter().all(|x| *x > 0.));
    }
}
