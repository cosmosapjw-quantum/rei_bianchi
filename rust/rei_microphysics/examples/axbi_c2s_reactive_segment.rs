//! Compact explicit continuation from an identity-compatible checkpoint.
//! Never changes the original run, configuration, or absolute solver caps.
//! Every accepted state is validated by the existing driver and recorded.
use rei_microphysics::axbi_covariant_driver::{
    compiled_identity, Driver, DriverConfig, DriverState,
};
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
    time::Instant,
};
fn row(d: &Driver, s: &DriverState, w: &mut impl Write) -> Result<(), Box<dyn std::error::Error>> {
    d.validate(s, 1e-8)?;
    let p = d.background.point_at_scale(s.a)?;
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let eos = s.gas.eos(nh, d.n_he0_cm3 / s.a.powi(3))?;
    let [x, y, z] = s.gas.fractions;
    let [an, au, pn, pu] = d.photon_pool_inventory(s)?;
    let [j0, j1, j2] = d.moments(s)?;
    let (rn, ru) = d.residuals(s)?;
    let photo = d.endpoint_photo(s)?;
    let above = s.heii_above.as_ref().ok_or("split state required")?;
    let above_n = above.number.iter().sum::<f64>();
    let middle_n = s
        .hei_middle
        .as_ref()
        .ok_or("multi-threshold state required")?
        .number
        .iter()
        .sum::<f64>();
    let rays = d.transport.ray_geometry(&p.geometry()?)?;
    let max_scale = rays.iter().map(|r| r.scale).fold(0., f64::max);
    let min_scale = rays.iter().map(|r| r.scale).fold(f64::INFINITY, f64::min);
    let a = [
        s.a,
        1. / s.a - 1.,
        p.time_s,
        nh,
        eos.electron_density_cm3,
        x,
        y,
        z,
        eos.temperature_k,
        an,
        au,
        pn,
        pu,
        j0,
        j1,
        j2,
        rn,
        ru,
        s.ledgers.source_n,
        s.ledgers.source_u,
        s.last_error,
        s.next_dln_a,
        s.max_newton_residual,
        above_n,
        middle_n,
        max_scale,
        min_scale,
        photo.gamma_s[0],
        photo.gamma_s[1],
        photo.gamma_s[2],
        photo.heat_erg_per_absorber_s[0],
        photo.heat_erg_per_absorber_s[1],
        photo.heat_erg_per_absorber_s[2],
        s.ledgers.photo_events[2],
    ];
    write!(
        w,
        "{},{},{},{}",
        s.accepted, s.attempts, s.rhs_evaluations, s.rejects
    )?;
    for v in a {
        if !v.is_finite() {
            return Err("nonfinite row".into());
        }
        write!(w, ",{v:.17e}")?
    }
    writeln!(w)?;
    Ok(())
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    if a.len() != 4 {
        return Err("usage ORIGINAL_CONFIG OLD_RUN_OR_FRESH NEW_DIR ADDITIONAL_WALL_S [ABS_STEP_CAP ABS_ATTEMPT_CAP [TIGHTER_LOCAL_TARGET]]".into());
    }
    let mut cfg = fs::read_to_string(&a[0])?;
    let input_cfg = cfg.clone();
    let old = Path::new(&a[1]);
    let out = Path::new(&a[2]);
    let budget: f64 = a[3].parse()?;
    if !budget.is_finite() || budget <= 0. || budget > 300. {
        return Err("segment wall domain".into());
    }
    let mut config = DriverConfig::read(&cfg)?;
    let original_caps = (config.max_steps, config.max_attempts);
    if a.len() >= 6 {
        if a[1] == "FRESH" {
            return Err("cap extension requires compatible checkpoint".into());
        }
        let steps: usize = a[4].parse()?;
        let attempts: usize = a[5].parse()?;
        if steps < config.max_steps
            || attempts < config.max_attempts
            || steps > 600000
            || attempts > 2400000
        {
            return Err("cap extension domain".into());
        }
        config.max_steps = steps;
        config.max_attempts = attempts;
    }
    let original_target = config.local_target;
    if a.len() == 7 {
        let t: f64 = a[6].parse()?;
        if !t.is_finite() || t <= 0. || t >= original_target {
            return Err("must tighten local target".into());
        }
        config.local_target = t;
        cfg = cfg
            .lines()
            .map(|l| {
                if l.starts_with("local_target=") {
                    format!("local_target={t:.17e}")
                } else {
                    l.to_string()
                }
            })
            .collect::<Vec<_>>()
            .join("\n")
            + "\n";
    }
    if !config.reactive_hi {
        return Err("split mode required".into());
    }
    let (d, mut s) = Driver::new(config)?;
    if a[1] != "FRESH" {
        if fs::read_to_string(old.join("config.cfg"))? != input_cfg
            || fs::read_to_string(old.join("source_identity.txt"))? != compiled_identity()
        {
            return Err("C2K resume identity mismatch".into());
        }
        s = d.read_checkpoint(&old.join("checkpoint.txt"))?;
    }
    fs::create_dir(out)?;
    fs::write(out.join("config.cfg"), cfg)?;
    fs::write(out.join("input_config.cfg"), input_cfg)?;
    fs::write(
        out.join("controller_trial.txt"),
        format!(
            "original_target={original_target:.17e}\neffective_target={:.17e}\n",
            d.config.local_target
        ),
    )?;
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    fs::write(out.join("resource_caps.txt"),format!("original_steps={}\noriginal_attempts={}\neffective_steps={}\neffective_attempts={}\nmax_rhs={}\nsegment_wall_s={}\n",original_caps.0,original_caps.1,d.config.max_steps,d.config.max_attempts,d.config.max_rhs,budget))?;
    let initial = s.accepted;
    let start_a = s.a;
    let prior_wall = s.wall_elapsed_s;
    d.save_checkpoint(&out.join("initial_checkpoint.txt"), &s)?;
    let mut w = BufWriter::new(fs::File::create(out.join("history.csv"))?);
    writeln!(w,"accepted,attempts,rhs,rejects,a,zbar,time_s,nH_proper_cm3,ne_proper_cm3,x_HII,x_HeII,x_HeIII,temperature_K,active_N,active_U,passive_N,passive_U,J0,J1,J2,number_defect,energy_defect,source_N,source_U,local_error,next_h,root_error,above_N,middle_N,max_ray_scale,min_ray_scale,Gamma_HI,Gamma_HeI,Gamma_HeII,heat_HI_erg,heat_HeI_erg,heat_HeII_erg,absorbed_HeII")?;
    row(&d, &s, &mut w)?;
    let begin = Instant::now();
    let end = 1. / (1. + d.config.end_zbar);
    let mut reason = "COMPLETE_REPRESENTED_INTERVAL".to_string();
    while s.a < end {
        if begin.elapsed().as_secs_f64() >= budget {
            reason = "STOPPED_SEGMENT_WALL_CAP".into();
            break;
        }
        if s.accepted >= d.config.max_steps
            || s.attempts >= d.config.max_attempts
            || s.rhs_evaluations >= d.config.max_rhs
        {
            reason = "STOPPED_ORIGINAL_ABSOLUTE_CAP".into();
            break;
        }
        match d.adaptive_step(&mut s) {
            Ok(true) => {
                if s.last_error >= d.config.local_target || s.last_error >= 2e-4 {
                    return Err("accepted local metric".into());
                }
                row(&d, &s, &mut w)?;
                if s.accepted % 10000 == 0 {
                    w.flush()?;
                    s.wall_elapsed_s = prior_wall + begin.elapsed().as_secs_f64();
                    d.save_checkpoint(&out.join("checkpoint.txt"), &s)?;
                    eprintln!("accepted={} z={}", s.accepted, 1. / s.a - 1.);
                }
            }
            Ok(false) => {}
            Err(e) => {
                if s.consecutive_rejects >= 30
                    || s.next_dln_a < 1e-10
                    || s.rhs_evaluations >= d.config.max_rhs
                {
                    reason = format!("STOPPED_NUMERICAL:{e:?}");
                    break;
                }
            }
        }
        if s.consecutive_rejects >= 30 || s.next_dln_a < 1e-10 {
            reason = "STOPPED_REJECT_CAP".into();
            break;
        }
    }
    w.flush()?;
    s.wall_elapsed_s = prior_wall + begin.elapsed().as_secs_f64();
    d.save_checkpoint(&out.join("checkpoint.txt"), &s)?;
    fs::write(out.join("RETURN.txt"),format!("status={reason}\nstart_a={start_a:.17e}\na={:.17e}\ninitial_accepted={initial}\naccepted={}\nadditional_accepted={}\nwall_budget_s={budget}\nsegment_wall_s={:.9}\nscientific_admission=NOT_ISSUED\n",s.a,s.accepted,s.accepted-initial,begin.elapsed().as_secs_f64()))?;
    println!(
        "{reason} z={} additional_steps={}",
        1. / s.a - 1.,
        s.accepted - initial
    );
    Ok(())
}
