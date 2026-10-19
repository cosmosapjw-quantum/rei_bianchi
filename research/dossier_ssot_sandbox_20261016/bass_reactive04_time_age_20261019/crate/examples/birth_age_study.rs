//! Lightweight constant-source/constant-opacity time x age diagnostic matrix.
//! Run as: cargo run --release --example birth_age_study -- OUTPUT_DIRECTORY
//! No gas history, geometry, source owner, or quadrature rule is changed here.
use rei_iso_couple_reference::birth_age_certificate::{BirthAgeCertificate, compare_nodes};
use rei_iso_couple_reference::fitted_birth;
use rei_iso_couple_reference::full_network::NetworkError;
use rei_iso_couple_reference::retarded_transport::gauss_birth_nodes;
use std::fs::{File, create_dir_all};
use std::io::{BufWriter, Write};
use std::path::Path;

fn global_nodes(
    tau: f64,
    nsteps: usize,
    family: &str,
    resolution: usize,
) -> Result<Vec<(f64, f64)>, NetworkError> {
    let local = if family == "AP" {
        fitted_birth::rule(tau / nsteps as f64, resolution)?
    } else {
        // Original GL nodes use birth fraction u. Convert to age x=1-u.
        gauss_birth_nodes(resolution)?
            .into_iter()
            .map(|(u, w)| (1.0 - u, w))
            .collect()
    };
    Ok((0..nsteps)
        .flat_map(|elapsed_cells| {
            local.iter().map(move |(age, weight)| {
                (
                    (elapsed_cells as f64 + age) / nsteps as f64,
                    weight / nsteps as f64,
                )
            })
        })
        .collect())
}

fn write_certificate(
    writer: &mut impl Write,
    family: &str,
    nsteps: usize,
    resolution: usize,
    certificate: BirthAgeCertificate,
) -> std::io::Result<()> {
    for (kind, measure) in [
        ("emitted", certificate.emitted),
        ("survivor", certificate.survivors),
    ] {
        let shape = measure
            .shape
            .expect("positive unit source and nonempty rule");
        writeln!(
            writer,
            "{family},{:.17e},{nsteps},{resolution},{},{kind},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{}",
            certificate.tau,
            certificate.input_nodes,
            measure.exact_mass,
            measure.discrete_mass,
            measure.relative_mass_defect.unwrap(),
            measure.log_mass_ratio.unwrap(),
            shape.cdf_sup,
            shape.w1,
            shape.exact_moments[0],
            shape.discrete_moments[0],
            shape.signed_moment_defects[0],
            shape.exact_moments[1],
            shape.discrete_moments[1],
            shape.signed_moment_defects[1],
            shape.normalized_weight_underflows,
            measure.absolute_mass_underflow,
        )?;
    }
    Ok(())
}

fn write_edge_cases(directory: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut file = BufWriter::new(File::create(directory.join("AGE_EDGE_CASES.csv"))?);
    writeln!(
        file,
        "case,tau,born,node_count,result,survivor_exact_mass,survivor_discrete_mass,shape_defined,cdf_sup,w1,absolute_mass_underflow"
    )?;
    let cases = [
        ("zero_source", 1000.0, 0.0, vec![(0.5, 1.0)]),
        ("empty_source", 1000.0, 0.0, vec![]),
        ("empty_positive_source", 1000.0, 1.0, vec![]),
        ("zero_opacity", 0.0, 1.0, vec![(0.5, 1.0)]),
        (
            "underflowed_absolute_survivors",
            1000.0,
            1.0,
            vec![(1.0, 1.0)],
        ),
        ("huge_tau_young_atom", 1e300, 1.0, vec![(0.0, 1.0)]),
        ("huge_tau_mean_atom", 1e300, 1.0, vec![(1e-300, 1.0)]),
        ("negative_population", 1.0, 1.0, vec![(0.5, -1.0)]),
        ("negative_source", 1.0, -1.0, vec![(0.5, 1.0)]),
        ("invalid_age", 1.0, 1.0, vec![(1.5, 1.0)]),
    ];
    for (name, tau, born, nodes) in cases {
        match compare_nodes(tau, born, &nodes) {
            Ok(result) => {
                let shape = result.survivors.shape;
                writeln!(
                    file,
                    "{name},{tau:.17e},{born:.17e},{},OK,{:.17e},{:.17e},{},{},{},{}",
                    nodes.len(),
                    result.survivors.exact_mass,
                    result.survivors.discrete_mass,
                    shape.is_some(),
                    shape.map_or_else(String::new, |s| format!("{:.17e}", s.cdf_sup)),
                    shape.map_or_else(String::new, |s| format!("{:.17e}", s.w1)),
                    result.survivors.absolute_mass_underflow,
                )?;
            }
            Err(error) => writeln!(
                file,
                "{name},{tau:.17e},{born:.17e},{},{error:?},,,,,,",
                nodes.len()
            )?,
        }
    }
    file.flush()?;
    Ok(())
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let directory = std::env::args()
        .nth(1)
        .ok_or("usage: birth_age_study OUTPUT_DIRECTORY")?;
    let directory = Path::new(&directory);
    create_dir_all(directory)?;
    let mut output = BufWriter::new(File::create(directory.join("AGE_CERTIFICATES.csv"))?);
    let mut actual_nodes = BufWriter::new(File::create(directory.join("AGE_ACTUAL_NODES.csv"))?);
    let mut errors = BufWriter::new(File::create(directory.join("AGE_RULE_FAILURES.csv"))?);
    writeln!(
        output,
        "family,tau,nsteps,resolution,node_count,measure,exact_mass,discrete_mass,relative_mass_defect,log_mass_ratio,cdf_sup,w1,exact_mean,discrete_mean,mean_defect,exact_second,discrete_second,second_defect,normalized_weight_underflows,absolute_mass_underflow"
    )?;
    writeln!(
        actual_nodes,
        "family,tau,nsteps,resolution,node,age,emitted_weight"
    )?;
    writeln!(errors, "family,tau,nsteps,resolution,error,class")?;
    let mut comparisons = 0;
    let mut failures = 0;
    for tau in [0.0, 1e-8, 1.0, 93.0, 1e3, 1e12] {
        let grids: &[usize] = if tau == 93.0 {
            &[1, 2, 4, 8, 16, 32, 64]
        } else {
            &[1]
        };
        for nsteps in grids.iter().copied() {
            for (family, resolutions) in [("AP", &[1, 2, 4, 8, 16][..]), ("GL", &[2, 4][..])] {
                for resolution in resolutions {
                    let result = global_nodes(tau, nsteps, family, *resolution)
                        .and_then(|nodes| compare_nodes(tau, 1.0, &nodes).map(|c| (nodes, c)));
                    match result {
                        Ok((nodes, certificate)) => {
                            write_certificate(
                                &mut output,
                                family,
                                nsteps,
                                *resolution,
                                certificate,
                            )?;
                            comparisons += 1;
                            // Every actual input supports an independent quadrature/CDF audit.
                            {
                                for (i, (age, weight)) in nodes.iter().enumerate() {
                                    writeln!(
                                        actual_nodes,
                                        "{family},{tau:.17e},{nsteps},{resolution},{i},{age:.17e},{weight:.17e}"
                                    )?;
                                }
                            }
                        }
                        Err(error) => {
                            failures += 1;
                            writeln!(
                                errors,
                                "{family},{tau:.17e},{nsteps},{resolution},{error:?},{}",
                                if error == NetworkError::NoForwardProgress {
                                    "NUMERICAL_REPRESENTATION_LIMIT"
                                } else {
                                    "DIAGNOSTIC_OR_INPUT_ERROR"
                                }
                            )?;
                        }
                    }
                }
            }
        }
    }
    for refinement in [1, 2, 4, 8, 16] {
        match fitted_birth::rule(1e300, refinement) {
            Err(error) => writeln!(
                errors,
                "AP,1.00000000000000005e300,1,{refinement},{error:?},NUMERICAL_REPRESENTATION_LIMIT"
            )?,
            Ok(_) => return Err("huge-tau fitted representation unexpectedly changed".into()),
        }
    }
    output.flush()?;
    actual_nodes.flush()?;
    errors.flush()?;
    write_edge_cases(directory)?;
    println!(
        "AGE_STUDY comparisons={comparisons} main_matrix_failures={failures} huge_tau_resolution_witnesses=5"
    );
    if failures != 0 {
        return Err(
            "the planned age matrix had a diagnostic error; inspect AGE_RULE_FAILURES.csv".into(),
        );
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("AGE_STUDY_FAILED {error}");
        std::process::exit(2);
    }
}
