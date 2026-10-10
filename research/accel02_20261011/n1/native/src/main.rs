//! Conditional research consumer; does not modify PhysicalHistory admission.
use rei_microphysics::{
    axisym_coupled_derivative, Absorber, AtomicProvider,
    AxisymCoupledState, AxisymLocalSources, AxisymmetricPoint, HHeModel,
    IsotopeNumberState, IsotopeSpecies,
};
use std::io::{self, BufRead, Write};
use rei_microphysics::{igm_rates::igm_rates, igm_state::IgmGasState, igm_thermal::{igm_point_rhs, IgmPhotoInput}};

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
    tcmb_k: f64,
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
    if input.time_s < 0. { return Err("NEGATIVE_TIME".into()); }
    let gas = HHeModel::controlled_fixture();
    let u = input.w_ev_per_h * input.n_h_cm3 * gas.ev_erg;
    let state = IgmGasState::new(input.fractions, input.w_ev_per_h * gas.ev_erg)
        .map_err(|e| e.to_string())?;
    let [h, he1, he2] = input.fractions;
    let lower = [input.n_h_cm3 * (1. - h), input.n_he_cm3 * (1. - (he1 + he2)), input.n_he_cm3 * he1];
    let provider = AtomicProvider::reference();
    let mut photo_heat_per_absorber = [0.; 3];
    let mut gamma = [0.; 3];
    let mut photon_dot = Vec::with_capacity(input.nodes.len());
    let mut photon_number = 0.;
    let mut photon_energy = 0.;
    let mut photon_delta = 0.;
    let mut source_number_ref = 0.;
    let mut source_energy_ref = 0.;
    let mut absorbed_number_ref = 0.;
    let mut absorbed_energy_ref = 0.;

    for node in &input.nodes {
        if ![node.energy_ev, node.mu, node.number_reference_cm3, node.source_reference_cm3_s]
            .iter().all(|x| x.is_finite())
            || node.energy_ev <= 0. || node.mu.abs() > 1.
            || node.number_reference_cm3 < 0. || node.source_reference_cm3_s < 0.
        {
            return Err("PHOTON_NODE_DOMAIN".into());
        }
        // q coverage extends beyond initial50keV to cover late births.
        // Only EMPTY, inactive characteristics may bypass the atomic band.
        if node.energy_ev > 50_000. && node.number_reference_cm3 == 0.
            && node.source_reference_cm3_s == 0. {
            photon_dot.push(0.);
            continue;
        }
        let number = node.number_reference_cm3 / volume;
        let energy = node.energy_ev * gas.ev_erg;
        let mut absorbed_ref = 0.;
        for (a, absorber) in ABSORBERS.iter().enumerate() {
            let sigma = provider.cross_section(*absorber, node.energy_ev).map_err(|e| e.to_string())?;
            let rate = gas.c_cm_s * sigma * number;
            let event = lower[a] * rate;
            gamma[a] += rate;
            photo_heat_per_absorber[a] += rate * (node.energy_ev - gas.threshold_ev[a]) * gas.ev_erg;
            absorbed_ref += event * volume;

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
        (derivative.species_m3_s[IsotopeSpecies::He4SinglyIonized as usize] / 1e6 + 3. * input.h_per_s * input.n_he_cm3 * he1) / input.n_he_cm3,
        (derivative.species_m3_s[IsotopeSpecies::He4DoublyIonized as usize] / 1e6 + 3. * input.h_per_s * input.n_he_cm3 * he2) / input.n_he_cm3,
    ];
    let wdot = derivative.thermal_energy_j_m3_s * 10. / (input.n_h_cm3 * gas.ev_erg)
        + 3. * input.h_per_s * input.w_ev_per_h;
    let work_ref = (input.h_per_s * photon_energy + 2. * input.s_per_s * photon_delta + 2. * input.h_per_s * u) * volume;
    let number_residual = scaled_residual(photon_dot.iter().sum::<f64>() - source_number_ref + absorbed_number_ref,
        photon_dot.iter().map(|x| x.abs()).sum::<f64>() + source_number_ref + absorbed_number_ref);
    let energy_terms = [photon_power, thermal_power, internal_power, escape, -source_power, -cmb];
    let energy_residual = scaled_residual(energy_terms.iter().sum(), energy_terms.iter().map(|x| x.abs()).sum());
    let mut output = vec![dx[0], dx[1], dx[2], wdot, escape * volume, work_ref, source_energy_ref,
        absorbed_number_ref, gamma[0], gamma[1], gamma[2], derivative.temperature_k, number_residual, energy_residual, cmb * volume];
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
            let c = igm_rates(parse_f64(words.next())?).map_err(|e| e.to_string())?;
            c.rr_cm3_s.into_iter().chain(c.ci_cm3_s).chain([c.dr_cm3_s])
                .chain(c.rr_cooling_erg_cm3_s).chain([c.dr_cooling_erg_cm3_s, c.freefree_erg_cm3_s]).collect()
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
            let mut p = [0.; 12];
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
                n_h_cm3: p[5], n_he_cm3: p[6], fractions: [p[7], p[8], p[9]], w_ev_per_h: p[10], tcmb_k: p[11], nodes })?
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
    fn fixture(t: f64) -> Input {
        let gas = HHeModel::controlled_fixture();
        let nh=1e-3; let nhe=8e-5; let x=[2e-4,1e-5,1e-7];
        let state=IgmGasState::from_temperature(x,nh,nhe,t).unwrap();
        Input {time_s:0.,a_rel:1.,b:0.,h_per_s:2e-17,s_per_s:1e-19,
            n_h_cm3:nh,n_he_cm3:nhe,fractions:x,w_ev_per_h:state.w_erg_per_h/gas.ev_erg,
            tcmb_k:46.,nodes:vec![Node{energy_ev:70.,mu:0.5,number_reference_cm3:1e-8,source_reference_cm3_s:1e-20}]}
    }
    fn close(a:f64,b:f64) { assert!((a-b).abs() <= 5e-12*a.abs().max(b.abs()).max(1e-100),"{a:e} != {b:e}"); }
    #[test]
    fn current_stage_cold_gas_and_case_a_energy_match_imported_provider() {
        for t in [20., 5000., 50000.] {
            let i=fixture(t);let out=rhs(&i).unwrap();let gas=HHeModel::controlled_fixture();
            let mut gamma=[0.;3];let mut heat=[0.;3];
            for a in 0..3 { gamma[a]=gas.c_cm_s*AtomicProvider::reference().cross_section(ABSORBERS[a],70.).unwrap()*1e-8;
                heat[a]=gamma[a]*(70.-gas.threshold_ev[a])*gas.ev_erg; }
            let s=IgmGasState::new(i.fractions,i.w_ev_per_h*gas.ev_erg).unwrap();
            let direct=igm_point_rhs(&s,i.n_h_cm3,i.n_he_cm3,i.h_per_s,i.tcmb_k,
                IgmPhotoInput{gamma_s:gamma,heat_erg_per_absorber_s:heat}).unwrap();
            for a in 0..3 {close(out[a],direct.fraction_dt[a]);}
            close(out[3],direct.w_dt_erg_per_h_s/gas.ev_erg);
            close(out[4],direct.escape_erg_cm3_s);close(out[14],direct.cmb_to_gas_erg_cm3_s);
            assert!(out[12].abs()<1e-12 && out[13].abs()<1e-12);
            assert_eq!(out.len(),16);
        }
    }
    #[test]
    fn signed_cmb_is_external_bath_not_escape_or_photon_birth() {
        let mut cold=fixture(20.); cold.nodes.clear(); cold.h_per_s=0.; cold.s_per_s=0.;
        let mut hot=cold.clone();hot.tcmb_k=10.;
        let a=rhs(&cold).unwrap();let b=rhs(&hot).unwrap();
        assert!(a[14]>0. && b[14]<0.);close(a[4],b[4]);assert_eq!(a.len(),15);assert_eq!(b.len(),15);
        close(a[3]-b[3],(a[14]-b[14])/(cold.n_h_cm3*1.602176634e-12));
    }
    #[test]
    fn reference_volume_and_empty_high_q_policy_are_explicit() {
        let a=fixture(20.);let mut b=a.clone();b.a_rel=2.;
        b.nodes[0].number_reference_cm3*=8.;b.nodes[0].source_reference_cm3_s*=8.;
        b.nodes.push(Node{energy_ev:1e5,mu:0.,number_reference_cm3:0.,source_reference_cm3_s:0.});
        let va=rhs(&a).unwrap();let vb=rhs(&b).unwrap();
        for k in [0,1,2,3,8,9,10,11] {close(va[k],vb[k]);}
        for k in [4,5,6,7,14,15] {close(va[k]*8.,vb[k]);}
        assert_eq!(vb[16],0.);
        b.nodes[1].source_reference_cm3_s=1e-30;assert!(rhs(&b).is_err());
        b.nodes[1].source_reference_cm3_s=0.;b.nodes[1].number_reference_cm3=1e-30;assert!(rhs(&b).is_err());
    }
    #[test]
    fn immutable_temperature_fraction_and_protocol_guards() {
        for t in [0.5,1e6*1.01] {assert!(rhs(&fixture(t)).is_err());}
        let mut i=fixture(20.);i.fractions[1]=0.8;i.fractions[2]=0.3;assert!(rhs(&i).is_err());
        i=fixture(20.);i.time_s=-1.;assert!(rhs(&i).is_err());
        assert!(command("RATES NaN").is_err());assert!(command("RATES 20 extra").is_err());
        assert_eq!(command("RATES 20").unwrap().len(),12);
        assert_eq!(command("SIGMA 5").unwrap(),vec![0.,0.,0.]);
        assert!(command("SIGMA 50001").is_err());
    }
}
