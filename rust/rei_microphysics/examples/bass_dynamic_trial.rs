//! Bounded native BASS+REI H/He mini-history; independent fixed-step refinements.
use rei_microphysics::axbi_bass_background::{BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{BassResearchNumerics, Driver, DriverConfig, DriverState};
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
    let numerics = match env::var("BASS_NUMERICS").unwrap_or_else(|_| "legacy".into()).as_str() {
        "legacy" => BassResearchNumerics::Legacy,
        "legacy_trace" => BassResearchNumerics::LegacyTrace,
        "tight_newton" => BassResearchNumerics::TightNewton,
        "split_be" => BassResearchNumerics::SplitBe,
        "tight_split_be" => BassResearchNumerics::TightSplitBe,
        "uniform_birth" => BassResearchNumerics::UniformBirth,
        "tight_uniform_birth" => BassResearchNumerics::TightUniformBirth,
        "full_exponential_frozen" => BassResearchNumerics::FullExponentialFrozen,
        _ => return Err("unknown BASS_NUMERICS".into()),
    };
    // Output-only switch for refined reference runs; physics is unchanged.
    let optical_detail = env::var("BASS_OPTICAL_DETAIL").unwrap_or_else(|_| "1".into()) != "0";
    // Opt-in final-step roundoff closure; bound to output identity and epoch.
    let exact_endpoint = env::var("BASS_EXACT_ENDPOINT").unwrap_or_else(|_| "0".into()) == "1";
    let mut config = DriverConfig::baseline();
    config.end_zbar = 19.99;
    config.initial_dln_a = dln;
    config.transport_threads = workers;
    config.max_steps = steps.max(512);
    config.max_wall_s = 1700.0;
    let (driver, initial) = Driver::new_bass_research(config.clone(), bg.clone(), numerics)?;
    let total_dln = if exact_endpoint {
        env::var("BASS_TOTAL_DLNA").unwrap_or_else(|_| "4e-4".into()).parse::<f64>()?
    } else {
        dln * steps as f64
    };
    let target_a = initial.a * total_dln.exp();
    let mut uninterrupted = initial.clone();
    let output_record = output.join("output_identity.txt");
    fs::write(
        &output_record,
        format!(
            "BASS_REI_MINI_V2\n{}\n{}\n{}\n{}\n{}\n{:?}\nexact_endpoint={}\ntotal_dln={:.17e}\ntarget_a={:.17e}\n",
            identity.source_csv_sha256, identity.source_manifest_sha256, identity.case, dln, steps, numerics, exact_endpoint, total_dln, target_a
        ),
    )?;
    let checkpoint = output.join(if numerics==BassResearchNumerics::Legacy {"checkpoint.bass-v1"} else {"checkpoint.bass-v2"});
    let epoch = if exact_endpoint {"bass-longstep-20261016-exact-endpoint-v1"} else {"bass-longstep-20261016-v2"};
    let mut resumed: Option<DriverState> = None;
    let mut step_trace=String::from("step,mid_a,mid_time_s,dt_s,emissivity_per_h_s,expected_source_n_per_h,actual_source_n_per_h,source_residual_per_h,old_photons_per_h,newborn_photons_per_h,temperature_k,x_hii,x_heii,x_heiii,photo_hi_per_h,photo_hei_per_h,photo_heii_per_h,photon_work_ev_per_h,thermal_work_ev_per_h\n");
    let mut optical_trace=String::from("step,opacity_phase,cohort,cell,ray_index,mu,energy_physical_ev,q_ref_ev,number_per_h,support_lo_ref_ev,support_hi_ref_ev,tau_hi,tau_hei,tau_heii\n");
    let mut ledger_trace=String::from("step,source_n_per_h,source_u_ev_per_h,absorbed_n_per_h,escaped_u_ev_per_h,cmb_u_ev_per_h,rr_hi_per_h,rr_hei_per_h,rr_heii_per_h,ci_hi_per_h,ci_hei_per_h,ci_heii_per_h,photon_work_ev_per_h,thermal_work_ev_per_h,gas_w_erg_per_h\n");
    let mut max_source_rate_change = 0.0_f64;
    let mut max_source_residual = 0.0_f64;
    let initial_rate = driver.source.at_redshift(20.0)?.per_h_s;
    for j in 0..steps {
        let old_a = uninterrupted.a;
        let step_dln = if exact_endpoint && j+1==steps {(target_a/old_a).ln()} else {dln};
        let next_a = old_a * step_dln.exp();
        let mid = (old_a * next_a).sqrt();
        let midpoint = driver.geometry_point(mid)?;
        let dt = driver.geometry_increment(old_a, next_a)?.proper_time_s;
        let rate = driver.source.at_redshift(1.0 / mid - 1.0)?.per_h_s;
        let mut at_mid=uninterrupted.clone();
        driver.geometry_map(&mut at_mid,mid)?;
        let geometry=driver.geometry_point(mid)?.geometry()?;
        let rays=driver.transport.ray_geometry(&geometry)?;
        let old_photons=PhotonState {number:at_mid.photons.clone(),energy_ref:at_mid.photon_energy_ref.clone(),
            support_lo:at_mid.photon_support_lo.clone(),support_hi:at_mid.photon_support_hi.clone()};
        let mut newborn=driver.transport.empty_state();
        driver.transport.inject(&mut newborn,&geometry,1.0/mid-1.0,dt)?;
        let [xh,yh,zh]=at_mid.gas.fractions;
        let nhmid=driver.n_h0_cm3/mid.powi(3);
        let nhemid=driver.n_he0_cm3/mid.powi(3);
        let absorbers=[nhmid*(1.0-xh),nhemid*(1.0-yh-zh),nhemid*yh];
        if optical_detail {
            for (label,photons) in [("old",&old_photons),("newborn",&newborn)] {
                let prepared=driver.transport.prepare(photons,&geometry)?;
                for (cell,q,n,lo,hi,tau) in prepared.optical_depth_rows(absorbers,dt) {
                    let ray=cell/driver.config.transport_cells;
                    optical_trace.push_str(&format!("{j},pre,{label},{cell},{ray},{:.17e},{:.17e},{q:.17e},{n:.17e},{lo:.17e},{hi:.17e},{:.17e},{:.17e},{:.17e}\n",rays[ray].mu,q*rays[ray].scale,tau[0],tau[1],tau[2]));
                }
            }
        }
        let old_count=old_photons.number.iter().sum::<f64>();
        let newborn_count=newborn.number.iter().sum::<f64>();
        let old_source_n = uninterrupted.ledgers.source_n;
        let old_events=uninterrupted.ledgers.photo_events;
        let before=uninterrupted.ledgers.clone();
        driver.fixed_step(&mut uninterrupted, step_dln)?;
        let [xa,ya,za]=uninterrupted.gas.fractions;
        let accepted_absorbers=[nhmid*(1.0-xa),nhemid*(1.0-ya-za),nhemid*ya];
        if optical_detail {
            for (label,photons) in [("old",&old_photons),("newborn",&newborn)] {
                let prepared=driver.transport.prepare(photons,&geometry)?;
                for (cell,q,n,lo,hi,tau) in prepared.optical_depth_rows(accepted_absorbers,dt) {
                    let ray=cell/driver.config.transport_cells;
                    optical_trace.push_str(&format!("{j},accepted,{label},{cell},{ray},{:.17e},{:.17e},{q:.17e},{n:.17e},{lo:.17e},{hi:.17e},{:.17e},{:.17e},{:.17e}\n",rays[ray].mu,q*rays[ray].scale,tau[0],tau[1],tau[2]));
                }
            }
        }
        let actual = uninterrupted.ledgers.source_n - old_source_n;
        let after=&uninterrupted.ledgers;
        ledger_trace.push_str(&format!("{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}\n",
            j+1,after.source_n-before.source_n,after.source_u-before.source_u,
            after.absorbed_n-before.absorbed_n,after.escaped_u-before.escaped_u,
            after.cmb_input-before.cmb_input,
            after.rr_events[0]-before.rr_events[0],after.rr_events[1]-before.rr_events[1],after.rr_events[2]-before.rr_events[2],
            after.ci_events[0]-before.ci_events[0],after.ci_events[1]-before.ci_events[1],after.ci_events[2]-before.ci_events[2],
            after.photon_work-before.photon_work,after.thermal_work-before.thermal_work,uninterrupted.gas.w_erg_per_h));
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
            "{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}\n",
            j + 1,
            mid,
            midpoint.time_s,
            dt,
            rate,
            rate * dt,
            actual,
            actual - rate * dt,
            old_count,newborn_count,
            temp,
            uninterrupted.gas.fractions[0],uninterrupted.gas.fractions[1],uninterrupted.gas.fractions[2],
            uninterrupted.ledgers.photo_events[0]-old_events[0],
            uninterrupted.ledgers.photo_events[1]-old_events[1],
            uninterrupted.ledgers.photo_events[2]-old_events[2],
            uninterrupted.ledgers.photon_work,
            uninterrupted.ledgers.thermal_work
        ));
        if j + 1 == steps / 2 {
            driver.save_bass_checkpoint(&checkpoint, &uninterrupted, epoch, &output_record)?;
            let (reader, _) = Driver::new_bass_research(config.clone(), bg.clone(), numerics)?;
            resumed = Some(reader.read_bass_checkpoint(&checkpoint, epoch, &output_record)?);
        }
        if let Some(s) = resumed.as_mut() {
            if j + 1 > steps / 2 {
                driver.fixed_step(s, step_dln)?;
            }
        }
    }
    fs::write(output.join("step_trace.csv"), step_trace)?;
    if optical_detail { fs::write(output.join("optical_nodes.csv"),optical_trace)?; }
    fs::write(output.join("ledger_steps.csv"),ledger_trace)?;
    fs::write(
        output.join("source_time_check.txt"),
        format!(
            "max_relative_rate_change={:.17e}\nmax_source_residual_per_h={:.17e}\nexact_endpoint={}\ntotal_dln={:.17e}\ntarget_a={:.17e}\n",
            max_source_rate_change, max_source_residual, exact_endpoint, total_dln, target_a
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
    let mut adaptive = initial;
    let mut adaptive_status = "NOT_ACCEPTED";
    for _ in 0..20 {
        match driver.adaptive_step(&mut adaptive) {
            Ok(true) => {
                adaptive_status = "ACCEPTED";
                break;
            }
            Ok(false) => {}
            Err(_) => {
                adaptive_status = "ERROR";
                break;
            }
        }
    }
    let photon_denominator = uninterrupted.ledgers.source_n.max(1.0);
    let energy_denominator = uninterrupted.ledgers.source_u.max(1.0);
    let report=format!("{{\"schema\":\"bass.rei.dynamic_mini.v2\",\"numerics\":\"{:?}\",\"case\":\"{}\",\"grid_points\":{},\"workers\":{},\"dln_a\":{:.17e},\"steps\":{},\"a\":{:.17e},\"time_s\":{:.17e},\"interval_time_s\":{:.17e},\"clock_residual_s\":{:.17e},\"b\":{:.17e},\"h_per_s\":{:.17e},\"s_per_s\":{:.17e},\"signed_s_over_h\":{:.17e},\"temperature_k\":{:.17e},\"x_hii\":{:.17e},\"x_heii\":{:.17e},\"x_heiii\":{:.17e},\"source_n_per_h\":{:.17e},\"source_u_ev_per_h\":{:.17e},\"photon_residual_per_h\":{:.17e},\"photon_denominator_per_h\":{:.17e},\"photon_normalized\":{:.17e},\"energy_residual_ev_per_h\":{:.17e},\"energy_denominator_ev_per_h\":{:.17e},\"energy_normalized\":{:.17e},\"ledger_tolerance_normalized\":1e-8,\"max_hamiltonian_normalized\":{:.17e},\"hamiltonian_tolerance_normalized\":3e-12,\"max_raychaudhuri_normalized\":{:.17e},\"restart_max_abs\":{:.17e},\"adaptive_status\":\"{}\",\"adaptive_error\":{:.17e},\"adaptive_accepted\":{},\"adaptive_rejects\":{},\"rhs_evaluations\":{},\"newton_residual\":{:.17e}}}\n",
        numerics,identity.case,identity.grid_points,workers,dln,steps,p.a,p.time_s,clock.proper_time_s,p.time_s-clock.proper_time_s,p.b,p.h_per_s,p.s_per_s,p.sigma,eos.temperature_k,
        uninterrupted.gas.fractions[0],uninterrupted.gas.fractions[1],uninterrupted.gas.fractions[2],
        uninterrupted.ledgers.source_n,uninterrupted.ledgers.source_u,n,photon_denominator,n/photon_denominator,u,energy_denominator,u/energy_denominator,
        hamiltonian,raychaudhuri,parity,adaptive_status,adaptive.last_error,adaptive.accepted,adaptive.rejects,uninterrupted.rhs_evaluations,uninterrupted.max_newton_residual);
    let mut file = fs::File::create(output.join("result.json"))?;
    file.write_all(report.as_bytes())?;
    print!("{report}");
    if !parity.is_finite()
        || parity > 1e-14
        || adaptive_status != "ACCEPTED"
        || max_source_rate_change <= 0.0
        || max_source_residual > 1e-10
    {
        return Err("mini-history parity/adaptive failure".into());
    }
    Ok(())
}
fn main() {
    if let Err(e) = result() {
        eprintln!("BASS_DYNAMIC_ERROR: {e:?}");
        std::process::exit(2)
    }
}
