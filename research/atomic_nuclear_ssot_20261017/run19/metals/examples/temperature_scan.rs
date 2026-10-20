//! Bounded pointwise temperature scan; no time integration or gas/radiation run.
use rei_run19_metals::beryllium_rr::*;
use rei_run19_metals::lithium_backend::{LithiumBackend, lithium_flat};
use rei_run19_metals::lithium_rates::{
    COMMON_MIN_K, COMMON_MAX_K, IsotopeRatePolicy, LithiumIsotopeNumberState,
    LithiumProcess, LithiumProvider,
};
use std::error::Error;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::path::PathBuf;

fn temperatures(lo: f64, hi: f64, count: usize) -> Vec<f64> {
    let mut ts = vec![lo, hi];
    for i in 0..count {
        let f = (i as f64 + 0.3819660112501051) / count as f64;
        ts.push((lo.ln() + f * (hi / lo).ln()).exp());
    }
    ts
}

fn out(path: PathBuf) -> Result<BufWriter<std::fs::File>, Box<dyn Error>> {
    Ok(BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path)?))
}

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args().skip(1);
    if args.next().as_deref() != Some("--output") { return Err("usage: temperature_scan --output NEW_DIRECTORY".into()); }
    let destination = PathBuf::from(args.next().ok_or("missing output directory")?);
    if args.next().is_some() { return Err("unexpected argument".into()); }
    std::fs::create_dir(&destination)?;
    let mut coefficients = out(destination.join("coefficient_samples.csv"))?;
    let mut contributions = out(destination.join("number_contributions.csv"))?;
    writeln!(coefficients, "source,T_K,channel,direct_cm3_s,table_cm3_s,relative_error")?;
    writeln!(contributions, "source,T_K,dN0,dN1,dN2,dN3,dN4,dN5,dN6,dN7,delectron,event_sum,nuclei_residual_isotope0,nuclei_residual_isotope1,charge_minus_electron")?;

    let li_direct = LithiumBackend::direct().map_err(|e| format!("{e:?}"))?;
    let li_table = LithiumBackend::tabulated(8193).map_err(|e| format!("{e:?}"))?;
    let be_direct = BeRrBackend::direct().map_err(|e| format!("{e:?}"))?;
    let be_table = BeRrBackend::tabulated(8193).map_err(|e| format!("{e:?}"))?;
    let li_state = LithiumIsotopeNumberState::new([1.0, 2.0, 3.0, 4.0], [5.0, 7.0, 11.0, 13.0]).unwrap();
    let be_state = BerylliumIsotopeNumberState::new([1.0, 2.0, 3.0, 4.0], [5.0, 7.0, 11.0, 13.0]).unwrap();
    let policy = IsotopeRatePolicy::ElementalElectronicEquality;
    let li_ts = temperatures(COMMON_MIN_K, COMMON_MAX_K, 257);
    let be_ts = temperatures(BE_RR_MIN_K, BE_RR_MAX_K, 1021);
    let mut max_li_relative: f64 = 0.0;
    let mut max_be_relative: f64 = 0.0;
    let mut max_nuclei_scaled: f64 = 0.0;
    let mut max_charge_scaled: f64 = 0.0;
    let mut coefficient_rows = 0;
    let mut contribution_rows = 0;
    let mut minimum_nonzero_coefficient = f64::INFINITY;

    for (name, ts) in [("LI_PR150", &li_ts), ("BE_VF1996", &be_ts)] {
        for &t in ts {
            let (direct, table, species, electrons, event_sum, q0) = if name == "LI_PR150" {
                let p = li_table.prepare(t).map_err(|e| format!("{e:?}"))?;
                let r = li_table.number_contribution(t, &p, &li_state, 19.0, policy).map_err(|e| format!("{e:?}"))?;
                let event_sum = r.isotope_channels.iter().flat_map(|r|
                    r.ionization_events_m3_s.iter().chain(&r.recombination_events_m3_s)).sum::<f64>();
                (lithium_flat(li_direct.rates(t).unwrap()).to_vec(), lithium_flat(p.rates()).to_vec(),
                    r.species_m3_s, r.electron_m3_s, event_sum, 0usize)
            } else {
                let p = be_table.prepare(t).map_err(|e| format!("{e:?}"))?;
                let r = be_table.number_contribution(t, &p, &be_state, 19.0, policy).map_err(|e| format!("{e:?}"))?;
                (be_direct.rates(t).unwrap().alpha_cm3_s().to_vec(), p.rates().alpha_cm3_s().to_vec(),
                    r.species_m3_s, r.electron_m3_s,
                    r.recombination_events_m3_s.iter().flatten().sum::<f64>(), 1usize)
            };
            for (i, (&a, &b)) in direct.iter().zip(&table).enumerate() {
                let relative = if a == 0.0 {
                    if b != 0.0 { return Err("structural zero mismatch".into()); } 0.0
                } else { (b / a - 1.0).abs() };
                if a > 0.0 { minimum_nonzero_coefficient = minimum_nonzero_coefficient.min(a.min(b)); }
                if name == "LI_PR150" { max_li_relative = max_li_relative.max(relative); }
                else { max_be_relative = max_be_relative.max(relative); }
                writeln!(coefficients, "{name},{t:.17e},{i},{a:.17e},{b:.17e},{relative:.17e}")?;
                coefficient_rows += 1;
            }
            let nuclei = species.map(|r| r.iter().sum::<f64>());
            let charge = species.iter().map(|r| r.iter().enumerate()
                .map(|(q, n)| (q + q0) as f64 * n).sum::<f64>()).sum::<f64>();
            max_nuclei_scaled = max_nuclei_scaled.max(nuclei[0].abs().max(nuclei[1].abs()) / event_sum);
            max_charge_scaled = max_charge_scaled.max((charge - electrons).abs() / event_sum);
            write!(contributions, "{name},{t:.17e}")?;
            for v in species.into_iter().flatten() { write!(contributions, ",{v:.17e}")?; }
            writeln!(contributions, ",{electrons:.17e},{event_sum:.17e},{:.17e},{:.17e},{:.17e}", nuclei[0], nuclei[1], charge - electrons)?;
            contribution_rows += 1;
        }
    }
    coefficients.flush()?; contributions.flush()?;
    let be_at_1e4 = be_direct.rates(1e4).unwrap().alpha_cm3_s();
    let lp = LithiumProvider::from_primary_rows().unwrap();
    let li_cold_rr = [1, 2, 3].map(|q| lp.coefficient_cm3_s(LithiumProcess::RadiativeRecombination, q, 1e4).unwrap());
    println!("{{\n  \"scope\": \"BOUNDED_POINTWISE_TEMPERATURE_AND_NUMBER_CONTRIBUTION_SCAN\",\n  \"nodes_per_table\": 8193,\n  \"li_temperatures\": {},\n  \"be_temperatures\": {},\n  \"coefficient_rows\": {coefficient_rows},\n  \"number_contribution_rows\": {contribution_rows},\n  \"max_li_sampled_relative\": {max_li_relative:.17e},\n  \"max_be_sampled_relative\": {max_be_relative:.17e},\n  \"max_nuclei_residual_over_events\": {max_nuclei_scaled:.17e},\n  \"max_ionic_charge_minus_electrons_over_events\": {max_charge_scaled:.17e},\n  \"minimum_nonzero_sampled_coefficient_cm3_s\": {minimum_nonzero_coefficient:.17e},\n  \"be_rr_at_10000_K_cm3_s\": {:?},\n  \"li_badnell_rr_at_10000_K_cm3_s\": {:?},\n  \"li_full_bundle_at_10000_K\": \"OUTSIDE_SOURCE_DOMAIN\",\n  \"density_state_is_manufactured\": true,\n  \"isotope_densities_m3\": [[1.0,2.0,3.0,4.0],[5.0,7.0,11.0,13.0]],\n  \"prescribed_free_electron_density_m3\": 19.0,\n  \"isotope_policy\": \"ElementalElectronicEquality\",\n  \"physical_fit_error_included\": false,\n  \"trajectory_integrations\": 0,\n  \"whole_gas_or_radiation_runs\": 0,\n  \"benchmark_claim\": false\n}}", li_ts.len(), be_ts.len(), be_at_1e4, li_cold_rr);
    Ok(())
}

fn main() {
    if let Err(e) = run() { eprintln!("{e}"); std::process::exit(1); }
}
