//! Label-preserving certificates for the restored BR03 frozen-source inventory.
//!
//! This reuses the 384 source labels, emitted counts, and opacity channels from
//! AP_FROZEN_SOURCE_INPUTS.csv, with the original constant-opacity reference
//! duration 8e12 s. Identical scalar rules may share read-only diagnostics.
//! Physical photons, source labels, directions, or birth times are never pooled.
//! Mixture outputs are label-weighted upper bounds, not exact mixture distances.
//! This inventory CLI requires strictly positive label masses. The core API
//! separately supports zero source with an undefined conditional age shape.
use rei_iso_couple_reference::birth_age_certificate::{BirthAgeCertificate, compare_nodes};
use rei_iso_couple_reference::fitted_birth;
use rei_iso_couple_reference::full_network::NetworkError;
use rei_iso_couple_reference::retarded_transport::gauss_birth_nodes;
use std::collections::HashMap;
use std::fs::{File, create_dir_all, read_to_string};
use std::io::{BufWriter, Write};
use std::path::Path;

const DURATION: f64 = 8e12;
const NSTEPS: usize = 32;

#[derive(Clone, Copy)]
struct SourceLabel {
    energy_ev: f64,
    born_com3: f64,
    tau: f64,
}

fn read_inputs(path: &Path) -> Result<Vec<SourceLabel>, Box<dyn std::error::Error>> {
    let text = read_to_string(path)?;
    let mut lines = text.lines();
    if lines.next() != Some("energy_ev,total_birth_com3,k_HI,k_HeI,k_HeII,k_DI") {
        return Err("frozen-source CSV schema mismatch".into());
    }
    let mut result = Vec::new();
    for line in lines {
        let values: Vec<_> = line
            .split(',')
            .map(str::parse::<f64>)
            .collect::<Result<_, _>>()?;
        if values.len() != 6
            || values.iter().any(|v| !v.is_finite() || *v < 0.0)
            || values[0] <= 0.0
            || values[1] <= 0.0
        {
            return Err("invalid frozen-source row: energy and label mass must be positive".into());
        }
        let tau = values[2..].iter().sum::<f64>() * DURATION;
        if !tau.is_finite() {
            return Err("nonfinite source optical depth".into());
        }
        result.push(SourceLabel {
            energy_ev: values[0],
            born_com3: values[1],
            tau,
        });
    }
    if result.is_empty() || result.iter().map(|label| label.born_com3).sum::<f64>() <= 0.0 {
        return Err("source inventory has no positive emitted mass".into());
    }
    Ok(result)
}

fn nodes(tau: f64, family: &str, resolution: usize) -> Result<Vec<(f64, f64)>, NetworkError> {
    let local = if family == "AP" {
        fitted_birth::rule(tau / NSTEPS as f64, resolution)?
    } else {
        gauss_birth_nodes(resolution)?
            .into_iter()
            .map(|(u, w)| (1.0 - u, w))
            .collect()
    };
    Ok((0..NSTEPS)
        .flat_map(|elapsed_cells| {
            local.iter().map(move |(age, weight)| {
                (
                    (elapsed_cells as f64 + age) / NSTEPS as f64,
                    weight / NSTEPS as f64,
                )
            })
        })
        .collect())
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 3 {
        return Err("usage: birth_age_source_study INPUT_CSV OUTPUT_DIRECTORY".into());
    }
    let labels = read_inputs(Path::new(&args[1]))?;
    let directory = Path::new(&args[2]);
    create_dir_all(directory)?;
    let mut output = BufWriter::new(File::create(directory.join("AGE_SOURCE_CERTIFICATES.csv"))?);
    let mut actual_nodes =
        BufWriter::new(File::create(directory.join("AGE_SOURCE_ACTUAL_NODES.csv"))?);
    let mut bounds = BufWriter::new(File::create(
        directory.join("AGE_SOURCE_MIXTURE_BOUNDS.csv"),
    )?);
    writeln!(
        output,
        "source_id,rule_id,energy_ev,tau,duration_s,nsteps,family,resolution,measure,born_com3,exact_mass_com3,discrete_mass_com3,relative_mass_defect,cdf_sup,w1,exact_mean,discrete_mean,mean_defect,exact_second,discrete_second,second_defect"
    )?;
    writeln!(
        actual_nodes,
        "rule_id,tau,nsteps,family,resolution,node,age,emitted_weight"
    )?;
    writeln!(
        bounds,
        "duration_s,nsteps,family,resolution,measure,labels,unique_rules,exact_mass_com3,discrete_mass_com3,relative_mass_defect,exact_weighted_cdf_sup,exact_weighted_w1,label_weight_tv,mixture_cdf_upper_bound,mixture_w1_upper_bound,mixture_exact_mean,mixture_discrete_mean,mixture_mean_defect,mixture_exact_second,mixture_discrete_second,mixture_second_defect"
    )?;

    let mut next_rule_id = 0;
    let mut node_rows = 0;
    for (family, resolutions) in [("AP", &[1, 2, 4, 8][..]), ("GL", &[2, 4][..])] {
        for resolution in resolutions {
            let mut cache = HashMap::<u64, (usize, BirthAgeCertificate)>::new();
            let mut records = Vec::new();
            for (source_id, label) in labels.iter().enumerate() {
                let key = label.tau.to_bits();
                if let std::collections::hash_map::Entry::Vacant(entry) = cache.entry(key) {
                    let nodes = nodes(label.tau, family, *resolution)
                        .map_err(|error| format!("source_id={source_id}: {error:?}"))?;
                    let certificate = compare_nodes(label.tau, 1.0, &nodes)
                        .map_err(|error| format!("source_id={source_id}: {error:?}"))?;
                    let rule_id = next_rule_id;
                    next_rule_id += 1;
                    for (i, (age, weight)) in nodes.iter().enumerate() {
                        writeln!(
                            actual_nodes,
                            "{rule_id},{:.17e},{NSTEPS},{family},{resolution},{i},{age:.17e},{weight:.17e}",
                            label.tau,
                        )?;
                        node_rows += 1;
                    }
                    entry.insert((rule_id, certificate));
                }
                let (rule_id, certificate) = cache[&key];
                records.push((label.born_com3, certificate));
                for (kind, measure) in [
                    ("emitted", certificate.emitted),
                    ("survivor", certificate.survivors),
                ] {
                    let shape = measure
                        .shape
                        .expect("unit-source rule has a probability shape");
                    writeln!(
                        output,
                        "{source_id},{rule_id},{:.17e},{:.17e},{DURATION:.17e},{NSTEPS},{family},{resolution},{kind},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                        label.energy_ev,
                        label.tau,
                        label.born_com3,
                        label.born_com3 * measure.exact_mass,
                        label.born_com3 * measure.discrete_mass,
                        measure.relative_mass_defect.unwrap(),
                        shape.cdf_sup,
                        shape.w1,
                        shape.exact_moments[0],
                        shape.discrete_moments[0],
                        shape.signed_moment_defects[0],
                        shape.exact_moments[1],
                        shape.discrete_moments[1],
                        shape.signed_moment_defects[1],
                    )?;
                }
            }
            for (kind, survivor) in [("emitted", false), ("survivor", true)] {
                let measures: Vec<_> = records
                    .iter()
                    .map(|(born, c)| (*born, if survivor { c.survivors } else { c.emitted }))
                    .collect();
                let exact_total: f64 = measures.iter().map(|(born, m)| born * m.exact_mass).sum();
                let discrete_total: f64 = measures
                    .iter()
                    .map(|(born, m)| born * m.discrete_mass)
                    .sum();
                if ![exact_total, discrete_total]
                    .iter()
                    .all(|v| v.is_finite() && *v > 0.0)
                {
                    return Err(
                        "aggregate source mass has no representable probability normalization"
                            .into(),
                    );
                }
                let mut weighted_ks = 0.0;
                let mut weighted_w1 = 0.0;
                let mut weight_tv = 0.0;
                let mut exact_moments = [0.0; 2];
                let mut discrete_moments = [0.0; 2];
                for (born, measure) in measures {
                    let p = born * measure.exact_mass / exact_total;
                    let q = born * measure.discrete_mass / discrete_total;
                    let shape = measure.shape.unwrap();
                    weighted_ks += p * shape.cdf_sup;
                    weighted_w1 += p * shape.w1;
                    weight_tv += 0.5 * (p - q).abs();
                    for i in 0..2 {
                        exact_moments[i] += p * shape.exact_moments[i];
                        discrete_moments[i] += q * shape.discrete_moments[i];
                    }
                }
                // The extra TV term handles different exact/discrete label
                // weights. The support diameter is 1 in normalized-age units.
                writeln!(
                    bounds,
                    "{DURATION:.17e},{NSTEPS},{family},{resolution},{kind},{},{},{exact_total:.17e},{discrete_total:.17e},{:.17e},{weighted_ks:.17e},{weighted_w1:.17e},{weight_tv:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                    labels.len(),
                    cache.len(),
                    (discrete_total - exact_total) / exact_total,
                    weighted_ks + weight_tv,
                    weighted_w1 + weight_tv,
                    exact_moments[0],
                    discrete_moments[0],
                    discrete_moments[0] - exact_moments[0],
                    exact_moments[1],
                    discrete_moments[1],
                    discrete_moments[1] - exact_moments[1],
                )?;
            }
        }
    }
    output.flush()?;
    actual_nodes.flush()?;
    bounds.flush()?;
    println!(
        "SOURCE_AGE_STUDY labels={} cases={} unique_rules={next_rule_id} actual_node_rows={node_rows} mixture_rows=12",
        labels.len(),
        labels.len() * 6
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("SOURCE_AGE_STUDY_FAILED {error}");
        std::process::exit(2);
    }
}
