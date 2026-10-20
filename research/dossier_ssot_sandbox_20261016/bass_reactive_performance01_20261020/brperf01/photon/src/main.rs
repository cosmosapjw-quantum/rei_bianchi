//! Exploratory paired benchmark: same prepared actual native labels and accuracy.
use rei_br06_reference::{
    fixture::NativeFixture,
    reference::{BirthMethod, PathControls, RunControls},
};
use rei_brperf01_photon::{
    Error, Mode, Result,
    batch::{self, BatchResult, Ledger, ParallelPool, PreparedBatch},
    fingerprint::{ledger_bits, path_bits},
    fixture_root,
};
use std::{env, fs, hint::black_box, io::Write, path::Path, time::Instant};

fn integer(value: &str) -> Result<usize> {
    value
        .parse()
        .map_err(|_| Error::InvalidInput("benchmark_integer"))
}
fn main() {
    if let Err(error) = execute() {
        eprintln!("{error}");
        std::process::exit(2);
    }
}
fn execute() -> Result<()> {
    let args: Vec<_> = env::args().collect();
    if args.len() != 10 {
        return Err(Error::InvalidInput(
            "usage: photon_bench OUT CASE LIMIT REF SLABS OPACITY EVENT PAIRS THREADS",
        ));
    }
    let out = Path::new(&args[1]);
    fs::create_dir_all(out)?;
    let case = &args[2];
    let controls = RunControls {
        birth: BirthMethod::Fitted,
        refinement: integer(&args[4])?,
        birth_degree: 8,
        path: PathControls {
            slabs: integer(&args[5])?,
            opacity_degree: integer(&args[6])?,
            event_degree: integer(&args[7])?,
            ..PathControls::default()
        },
        split_spectrum: false,
        template_limit: integer(&args[3])?,
        source_scale: 1.0,
    };
    let pairs = integer(&args[8])?;
    let threads = integer(&args[9])?;
    if pairs == 0 || pairs > 100 {
        return Err(Error::InvalidInput("benchmark_pairs"));
    }
    let fixture = NativeFixture::load(&fixture_root(), case)?;
    let start = Instant::now();
    let input = PreparedBatch::build(&fixture, controls)?;
    let prepare_s = start.elapsed().as_secs_f64();
    let start = Instant::now();
    let pool = ParallelPool::new(&fixture_root(), case, threads)?;
    let worker_setup_s = start.elapsed().as_secs_f64();
    let mut measurements = fs::File::create(out.join("TIMINGS.csv"))?;
    writeln!(
        measurements,
        "session,case,stage,pair,position,mode,threads,seconds,paths,samples,opacity_integrals,checksum"
    )?;
    let mut truth: Option<Vec<Vec<u64>>> = None;
    let mut truth_ledger = None;
    let mut first_cached_work = None;
    let mut runner = |stage: &str, pair: usize, position: usize, label: &str| -> Result<()> {
        let start = Instant::now();
        let result: BatchResult = match label {
            "baseline" => batch::evaluate_serial(&fixture, &input, controls.path, Mode::Baseline)?,
            "cached" => batch::evaluate_serial(&fixture, &input, controls.path, Mode::Cached)?,
            "parallel" => pool.evaluate(&input, controls.path)?,
            _ => return Err(Error::InvalidInput("benchmark_mode")),
        };
        let ledger: Ledger = input.reduce(&fixture, &result.paths)?;
        black_box(&result.paths);
        black_box(&ledger);
        let elapsed = start.elapsed().as_secs_f64();
        let fingerprint: Vec<_> = result.paths.iter().map(path_bits).collect();
        let ledger_fingerprint = ledger_bits(&ledger);
        if let Some(expected) = &truth {
            if expected != &fingerprint || truth_ledger.as_ref() != Some(&ledger_fingerprint) {
                return Err(Error::InvalidInput("bitwise_parity_failure"));
            }
        } else {
            truth = Some(fingerprint.clone());
            truth_ledger = Some(ledger_fingerprint.clone());
            export_births(out, &input, &result.paths)?;
            fs::write(out.join("LEDGER.txt"), format!("{ledger:#?}\n"))?;
        }
        if label == "cached" && first_cached_work.is_none() {
            first_cached_work = Some(result.work);
        }
        if stage == "warmup" && pair == 0 {
            let bytes: Vec<u8> = fingerprint
                .iter()
                .flatten()
                .flat_map(|value| value.to_le_bytes())
                .collect();
            fs::write(out.join(format!("PATH_BITS_{label}.bin")), bytes)?;
            let bytes: Vec<u8> = ledger_fingerprint
                .iter()
                .flat_map(|value| value.to_le_bytes())
                .collect();
            fs::write(out.join(format!("LEDGER_BITS_{label}.bin")), bytes)?;
        }
        let checksum = fingerprint
            .iter()
            .flatten()
            .fold(0u64, |s, v| s.rotate_left(7) ^ v);
        writeln!(
            measurements,
            "{},{case},{stage},{pair},{position},{label},{},{elapsed:.9e},{},{},{},{checksum:016x}",
            std::process::id(),
            if label == "parallel" { threads } else { 1 },
            result.paths.len(),
            result.work.virtual_samples,
            result.work.opacity_integrals
        )?;
        measurements.flush()?;
        println!(
            "{case} {stage} {pair} {label}: {elapsed:.6}s paths={} samples={} parity=PASS",
            result.paths.len(),
            result.work.virtual_samples
        );
        Ok(())
    };
    // Two warmups of every compared implementation, then fixed alternating
    // A-B/B-A order. The process/session count remains one per CLI invocation.
    for warmup in 0..2 {
        for (position, mode) in ["baseline", "cached", "parallel"].iter().enumerate() {
            runner("warmup", warmup, position, mode)?;
        }
    }
    for pair in 0..pairs {
        let modes = if pair % 2 == 0 {
            ["baseline", "cached", "baseline", "parallel"]
        } else {
            ["parallel", "baseline", "cached", "baseline"]
        };
        for (position, mode) in modes.iter().enumerate() {
            runner("paired", pair, position, mode)?;
        }
    }
    for pair in 0..3 {
        runner("aa", pair, 0, "baseline")?;
        runner("aa", pair, 1, "baseline")?;
    }
    let work = first_cached_work.unwrap();
    fs::write(
        out.join("CONTRACT.json"),
        format!(
            "{{\n  \"case\": \"{case}\",\n  \"templates\": {},\n  \"births\": {},\n  \"unique_paths\": {},\n  \"birth_refinement\": {},\n  \"path_slabs\": {},\n  \"opacity_degree\": {},\n  \"event_degree\": {},\n  \"source_prepare_seconds\": {prepare_s:.9e},\n  \"worker_setup_seconds\": {worker_setup_s:.9e},\n  \"threads\": {threads},\n  \"cohort_payload_bytes\": {},\n  \"path_result_payload_bytes\": {},\n  \"scratch_bytes_per_active_path\": 1024,\n  \"removed_opacity_heap_allocations\": {},\n  \"removed_opacity_heap_payload_bytes\": {},\n  \"baseline_sample_eos_calls\": {},\n  \"cached_serial_eos_calls\": 1,\n  \"baseline_gauss_constructions\": {},\n  \"cached_serial_gauss_constructions\": 2,\n  \"all_path_fields_bitwise_equal\": true,\n  \"all_ordered_ledger_fields_equal\": true,\n  \"old_physical_owner_changes\": 0,\n  \"gas_evolved\": false,\n  \"timing_status\": \"EXPLORATORY_ONE_PROCESS_PER_CASE_NOT_CONFIRMATORY\",\n  \"cache_policy\": \"geometry caches cleared before each timed call; original exact reflection reuse retained\",\n  \"scope\": \"frozen recorded native source paths; source preparation and worker construction separately timed\"\n}}\n",
            input.templates,
            input.births().len(),
            input.unique_cohorts().len(),
            controls.refinement,
            controls.path.slabs,
            controls.path.opacity_degree,
            controls.path.event_degree,
            std::mem::size_of::<rei_iso_couple_reference::source_age::Cohort>(),
            std::mem::size_of::<rei_br06_reference::reference::PathResult>(),
            work.opacity_integrals,
            work.opacity_integrals * controls.path.opacity_degree * 16,
            work.virtual_samples,
            2 * input.unique_cohorts().len(),
        ),
    )?;
    Ok(())
}

fn export_births(
    out: &Path,
    input: &PreparedBatch,
    paths: &[rei_br06_reference::reference::PathResult],
) -> Result<()> {
    let mut file = std::io::BufWriter::new(fs::File::create(out.join("BIRTH_PATHS.csv"))?);
    writeln!(
        file,
        "template,node,spectral,angular,target_age,emission_weight,birth_time_s,a1,a2,a3,H1,H2,H3,energy_ev,n1,n2,n3,K1,K2,K3,born,survival,HI,HeI,HeII,DI,heat_ev,chemical_ev,work_independent_ev,number_residual,energy_residual_ev,surviving_energy_ev,absorbed_energy_ev,end_n3,path_fingerprint"
    )?;
    for (index, birth) in input.births().iter().enumerate() {
        let co = &birth.cohort;
        let ray = co.ray_at(&co.birth_geometry)?;
        let k: [f64; 3] = std::array::from_fn(|j| {
            co.birth_geometry.scale_factors[j] * ray.energy_ev * ray.direction[j]
        });
        let path = input.result_for_birth(index, paths);
        let checksum = path_bits(&path)
            .iter()
            .fold(0u64, |s, v| s.rotate_left(7) ^ v);
        write!(
            file,
            "{},{},{},{}",
            birth.template, birth.node, co.spectral_index, co.angular_index
        )?;
        for value in [
            birth.target_age,
            birth.emission_weight,
            co.birth_time_s,
            co.birth_geometry.scale_factors[0],
            co.birth_geometry.scale_factors[1],
            co.birth_geometry.scale_factors[2],
            co.birth_geometry.hubble_per_s[0],
            co.birth_geometry.hubble_per_s[1],
            co.birth_geometry.hubble_per_s[2],
            co.energy_at_birth_ev,
            co.direction_at_birth[0],
            co.direction_at_birth[1],
            co.direction_at_birth[2],
            k[0],
            k[1],
            k[2],
            co.n_comoving_m3,
            path.survival,
            path.events[0],
            path.events[1],
            path.events[2],
            path.events[3],
            path.heat_ev.iter().sum::<f64>(),
            path.chemical_ev,
            path.geometry_work_independent_ev,
            path.number_residual,
            path.energy_residual_ev,
            path.surviving_energy_ev,
            path.absorbed_energy_ev,
            path.end_direction[2],
        ] {
            write!(file, ",{value:.17e}")?;
        }
        writeln!(file, ",{checksum:016x}")?;
    }
    file.flush()?;
    Ok(())
}
