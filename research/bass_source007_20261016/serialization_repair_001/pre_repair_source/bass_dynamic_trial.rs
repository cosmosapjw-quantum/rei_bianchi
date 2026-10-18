//! Opt-in source007 fixed-step component diagnostic; no adaptive or full-history admission.
use rei_microphysics::axbi_bass_background::{BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{Driver, DriverConfig, DriverState};
use rei_microphysics::axbi_rates::AxbiProvider;
use rei_microphysics::HHeModel;
use std::{
    env, fs,
    io::Write,
    path::{Path, PathBuf},
};

fn result() -> Result<(), Box<dyn std::error::Error>> {
    let args = env::args().collect::<Vec<_>>();
    if args.len() != 11 {
        return Err("usage: bass_dynamic_trial CSV MANIFEST CSV_SHA MANIFEST_SHA CASE GRID DLNA STEPS WORKERS OUTPUT_DIR".into());
    }
    let output = PathBuf::from(&args[10]);
    fs::create_dir(&output)?;
    let identity = BassSourceIdentity {
        producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
        source_csv_sha256: args[3].clone(),
        source_manifest_sha256: args[4].clone(),
        case: args[5].clone(),
        grid_points: args[6].parse()?,
    };
    let bg =
        BassBackground::from_files(Path::new(&args[1]), Path::new(&args[2]), identity.clone())?;
    let hamiltonian = bg.max_hamiltonian_normalized;
    let raychaudhuri = bg.max_raychaudhuri_normalized;
    let dln: f64 = args[7].parse()?;
    let steps: usize = args[8].parse()?;
    let workers: usize = args[9].parse()?;
    let mut config = DriverConfig::baseline();
    config.end_zbar = 19.99;
    config.initial_dln_a = dln;
    config.transport_threads = workers;
    config.max_steps = 512;
    config.max_wall_s = 1700.0;
    let (driver, initial) = Driver::new_bass(config.clone(), bg.clone())?;
    let mut uninterrupted = initial.clone();
    let output_record = output.join("output_identity.txt");
    fs::write(
        &output_record,
        format!(
            "BASS_REI_MINI_V1\n{}\n{}\n{}\n{}\n{}\n",
            identity.source_csv_sha256, identity.source_manifest_sha256, identity.case, dln, steps
        ),
    )?;
    let checkpoint = output.join("checkpoint.bass-v1");
    let epoch = "bass-mini-20261016-v1";
    let mut resumed: Option<DriverState> = None;
    let mut step_trace=String::from("step,mid_a,mid_time_s,dt_s,emissivity_per_h_s,expected_source_n_per_h,actual_source_n_per_h,source_residual_per_h,temperature_k,photon_work_ev_per_h,thermal_work_ev_per_h\n");
    let mut max_source_rate_change = 0.0_f64;
    let mut max_source_residual = 0.0_f64;
    let initial_rate = driver.source.at_redshift(20.0)?.per_h_s;
    for j in 0..steps {
        let old_a = uninterrupted.a;
        let next_a = old_a * dln.exp();
        let mid = (old_a * next_a).sqrt();
        let midpoint = driver.geometry_point(mid)?;
        let dt = driver.geometry_increment(old_a, next_a)?.proper_time_s;
        let rate = driver.source.at_redshift(1.0 / mid - 1.0)?.per_h_s;
        let old_source_n = uninterrupted.ledgers.source_n;
        driver.fixed_step(&mut uninterrupted, dln)?;
        let actual = uninterrupted.ledgers.source_n - old_source_n;
        max_source_residual = max_source_residual.max((actual - rate * dt).abs());
        max_source_rate_change =
            max_source_rate_change.max((rate - initial_rate).abs() / initial_rate);
        let temp = uninterrupted
            .gas
            .eos(
                driver.n_h0_cm3 / uninterrupted.a.powi(3),
                driver.n_he0_cm3 / uninterrupted.a.powi(3),
            )?
            .temperature_k;
        step_trace.push_str(&format!(
            "{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}\n",
            j + 1,
            mid,
            midpoint.time_s,
            dt,
            rate,
            rate * dt,
            actual,
            actual - rate * dt,
            temp,
            uninterrupted.ledgers.photon_work,
            uninterrupted.ledgers.thermal_work
        ));
        if j + 1 == steps / 2 {
            driver.save_bass_checkpoint(&checkpoint, &uninterrupted, epoch, &output_record)?;
            let (reader, _) = Driver::new_bass(config.clone(), bg.clone())?;
            resumed = Some(reader.read_bass_checkpoint(&checkpoint, epoch, &output_record)?);
        }
        if let Some(s) = resumed.as_mut() {
            if j + 1 > steps / 2 {
                driver.fixed_step(s, dln)?;
            }
        }
    }
    fs::write(output.join("step_trace.csv"), step_trace)?;
    fs::write(
        output.join("source_time_check.txt"),
        format!(
            "max_relative_rate_change={:.17e}\nmax_source_residual_per_h={:.17e}\n",
            max_source_rate_change, max_source_residual
        ),
    )?;
    let parity = if let Some(s) = &resumed {
        let (dn, de) = driver.residuals(s)?;
        let numeric = (s.a - uninterrupted.a)
            .abs()
            .max((s.gas.w_erg_per_h - uninterrupted.gas.w_erg_per_h).abs())
            .max(
                s.photons
                    .iter()
                    .zip(&uninterrupted.photons)
                    .map(|(a, b)| (a - b).abs())
                    .fold(0.0_f64, f64::max),
            )
            .max(dn.abs() * 0.0)
            .max(de.abs() * 0.0);
        if format!("{s:?}") == format!("{uninterrupted:?}") {
            numeric
        } else {
            numeric.max(1.0)
        }
    } else {
        f64::NAN
    };
    let (n, u) = driver.residuals(&uninterrupted)?;
    let p = driver.geometry_point(uninterrupted.a)?;
    let clock = driver.geometry_increment(initial.a, uninterrupted.a)?;
    let eos = uninterrupted.gas.eos(
        driver.n_h0_cm3 / uninterrupted.a.powi(3),
        driver.n_he0_cm3 / uninterrupted.a.powi(3),
    )?;
    let nh = driver.n_h0_cm3 / uninterrupted.a.powi(3);
    let nhe = driver.n_he0_cm3 / uninterrupted.a.powi(3);
    let geometry = p.geometry()?;
    let photons = PhotonState {
        number: uninterrupted.photons.clone(),
        energy_ref: uninterrupted.photon_energy_ref.clone(),
        support_lo: uninterrupted.photon_support_lo.clone(),
        support_hi: uninterrupted.photon_support_hi.clone(),
    };
    let prepared = driver.transport.prepare(&photons, &geometry)?;
    let [x, y, z] = uninterrupted.gas.fractions;
    let absorption = driver.transport.evaluate(
        &prepared,
        [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y],
        nh,
        0.0,
    )?;
    let rhs = AxbiProvider
        .point(
            &uninterrupted.gas,
            nh,
            nhe,
            0.0,
            2.7255 / uninterrupted.a,
            absorption.photo,
        )?
        .rhs;
    let model = HHeModel::controlled_fixture();
    let photo_binding = (0..3)
        .map(|i| rhs.photo_events_cm3_s[i] * model.threshold_ev[i] * model.ev_erg)
        .sum::<f64>();
    let photo_heat = rhs.photo_input_erg_cm3_s - photo_binding;
    let ci_sink = rhs.ci_thermal_sink_erg_cm3_s.iter().sum::<f64>();
    let rr_sink = rhs.rr_thermal_sink_erg_cm3_s.iter().sum::<f64>();
    let ce_sink = rhs.ce_thermal_sink_erg_cm3_s.iter().sum::<f64>();
    let owner_residual =
        rhs.thermal_micro_erg_cm3_s + rhs.binding_micro_erg_cm3_s + rhs.escape_erg_cm3_s
            - rhs.photo_input_erg_cm3_s
            - rhs.cmb_to_gas_erg_cm3_s;
    let owner_denom = rhs
        .photo_input_erg_cm3_s
        .abs()
        .max(rhs.escape_erg_cm3_s.abs())
        .max(rhs.thermal_micro_erg_cm3_s.abs())
        .max(1e-300);
    let owner_report=format!("{{\"scope\":\"instantaneous_final_chemistry_point\",\"units\":\"eV_per_H_per_s\",\"photo_binding\":{:.17e},\"photo_heat\":{:.17e},\"collisional_ionization_sink\":{:.17e},\"recombination_sink\":{:.17e},\"dielectronic_recombination_sink\":{:.17e},\"collisional_excitation_sink\":{:.17e},\"freefree_sink\":{:.17e},\"cmb_to_gas\":{:.17e},\"escape\":{:.17e},\"thermal_micro\":{:.17e},\"binding_micro\":{:.17e},\"owner_residual_erg_cm3_s\":{:.17e},\"owner_denominator_erg_cm3_s\":{:.17e},\"owner_normalized\":{:.17e}}}\n",
        photo_binding/(nh*model.ev_erg),photo_heat/(nh*model.ev_erg),ci_sink/(nh*model.ev_erg),rr_sink/(nh*model.ev_erg),rhs.dr_thermal_sink_erg_cm3_s/(nh*model.ev_erg),ce_sink/(nh*model.ev_erg),rhs.freefree_thermal_sink_erg_cm3_s/(nh*model.ev_erg),rhs.cmb_to_gas_erg_cm3_s/(nh*model.ev_erg),rhs.escape_erg_cm3_s/(nh*model.ev_erg),rhs.thermal_micro_erg_cm3_s/(nh*model.ev_erg),rhs.binding_micro_erg_cm3_s/(nh*model.ev_erg),owner_residual,owner_denom,owner_residual/owner_denom);
    fs::write(output.join("owner_rates.json"), owner_report)?;
    if owner_residual.abs() / owner_denom > 1e-12 {
        return Err("instantaneous owner balance".into());
    }
    let mut files = (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
    driver.output_row(
        &uninterrupted,
        &identity.case,
        &mut files.0,
        &mut files.1,
        &mut files.2,
        &mut files.3,
        &mut files.4,
    )?;
    for (name, bytes) in [
        ("history.csv", files.0),
        ("abundances.csv", files.1),
        ("spectra.csv", files.2),
        ("ledgers.csv", files.3),
        ("feedback.csv", files.4),
    ] {
        fs::write(output.join(name), bytes)?;
    }
    let photon_denominator = uninterrupted.ledgers.source_n.max(1.0);
    let energy_denominator = uninterrupted.ledgers.source_u.max(1.0);
    let report=format!("{{\"schema\":\"bass.rei.dynamic_mini.v1\",\"case\":\"{}\",\"grid_points\":{},\"workers\":{},\"dln_a\":{:.17e},\"steps\":{},\"a\":{:.17e},\"time_s\":{:.17e},\"interval_time_s\":{:.17e},\"clock_residual_s\":{:.17e},\"b\":{:.17e},\"h_per_s\":{:.17e},\"s_per_s\":{:.17e},\"signed_s_over_h\":{:.17e},\"temperature_k\":{:.17e},\"x_hii\":{:.17e},\"x_heii\":{:.17e},\"x_heiii\":{:.17e},\"source_n_per_h\":{:.17e},\"source_u_ev_per_h\":{:.17e},\"photon_residual_per_h\":{:.17e},\"photon_denominator_per_h\":{:.17e},\"photon_normalized\":{:.17e},\"energy_residual_ev_per_h\":{:.17e},\"energy_denominator_ev_per_h\":{:.17e},\"energy_normalized\":{:.17e},\"ledger_tolerance_normalized\":1e-8,\"max_hamiltonian_normalized\":{:.17e},\"hamiltonian_tolerance_normalized\":3e-12,\"max_raychaudhuri_normalized\":{:.17e},\"restart_max_abs\":{:.17e},\"adaptive_status\":\"{}\",\"adaptive_error\":{:.17e},\"adaptive_accepted\":{},\"adaptive_rejects\":{},\"rhs_evaluations\":{},\"newton_residual\":{:.17e}}}\n",
        identity.case,identity.grid_points,workers,dln,steps,p.a,p.time_s,clock.proper_time_s,p.time_s-clock.proper_time_s,p.b,p.h_per_s,p.s_per_s,p.sigma,eos.temperature_k,
        uninterrupted.gas.fractions[0],uninterrupted.gas.fractions[1],uninterrupted.gas.fractions[2],
        uninterrupted.ledgers.source_n,uninterrupted.ledgers.source_u,n,photon_denominator,n/photon_denominator,u,energy_denominator,u/energy_denominator,
        hamiltonian,raychaudhuri,parity,"NOT_RUN_FIXED_STEP_COMPONENT_ONLY",0.0,0,0,uninterrupted.rhs_evaluations,uninterrupted.max_newton_residual);
    let mut file = fs::File::create(output.join("result.json"))?;
    file.write_all(report.as_bytes())?;
    print!("{report}");
    if !parity.is_finite()
        || parity > 1e-14
        || max_source_rate_change <= 0.0
        || max_source_residual > 1e-10
    {
        return Err("fixed-step component parity/source failure".into());
    }
    Ok(())
}
fn main() {
    if let Err(e) = result() {
        eprintln!("BASS_DYNAMIC_ERROR: {e:?}");
        std::process::exit(2)
    }
}
