//! Bounded postcache005 component profile; explicit terminal diagnostic fixture, never a production resume.
use rei_microphysics::axbi_covariant_transport::{PhotonState, AbsorptionResult};
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig};
use std::{error::Error, fs, hint::black_box, path::Path, time::Instant};

fn result_words(r: &AbsorptionResult) -> Vec<u64> {
 let mut words=Vec::new();
 for values in [&r.state.number[..], &r.state.energy_ref[..], &r.state.support_lo[..], &r.state.support_hi[..],
                &r.photo.gamma_s[..], &r.photo.heat_erg_per_absorber_s[..], &r.absorbed_per_h[..]] {
  words.extend(values.iter().map(|x|x.to_bits()));
 }
 words.push(r.binding_ev_per_h.to_bits());words.push(r.heat_ev_per_h.to_bits());words
}

fn guard(start: Instant) -> Result<(), Box<dyn Error>> {
    if start.elapsed().as_secs_f64() > 55.0 {
        Err("profile wall cap".into())
    } else {
        Ok(())
    }
}
fn main() -> Result<(), Box<dyn Error>> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len() != 3 {
        return Err("CONFIG CHECKPOINT FRESH_OUTPUT".into());
    }
    let out = Path::new(&a[2]);
    fs::create_dir(out)?;
    let config = fs::read_to_string(&a[0])?;
    let mut control=DriverConfig::read(&config)?; control.transport_threads=8;
    let (mut d, _) = Driver::new(control)?;
    let s = d.read_checkpoint(Path::new(&a[1]))?;
    d.config.max_rhs = 10000;
    let p = PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    };
    let g = d.background.point_at_scale(s.a)?.geometry()?;
    let to = s.a * (-s.next_dln_a).exp(); // preceding in-domain geometry probe only
    let end = d.background.point_at_scale(to)?.geometry()?;
    let dt = d.background.interval_increment(to, s.a)?.proper_time_s;
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    let [x, y, z] = s.gas.fractions;
    let absorbers = [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y];
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    fs::write(
        out.join("profile_source.rs"),
        include_str!("hpc_profile.rs"),
    )?;
    fs::copy(&a[0],out.join("input_config.cfg"))?;
    fs::copy(&a[1],out.join("input_checkpoint.txt"))?;
    black_box(d.transport.prepare(&p,&g)?); // warm persistent8 pool before timing
    fs::write(out.join("geometry_probe_contract.json"), r#"{"role":"preceding_geometry_probe_not_valid_scientific_step","terminal_fixture_unchanged":true,"from":"a*exp(-next_dln_a)","to":"a","partition_geometry":"earlier_from","positive_dt":"interval_increment(from,to)","first_failure_preserved":"/root/REI_FLRW_HPC_PROFILE_20261015_002"}"#)?;\n    let started = Instant::now();
    let phase = Instant::now();
    for _ in 0..20 {
        guard(started)?;
        black_box(d.background.point_at_scale(s.a)?);
    }
    let background = phase.elapsed().as_secs_f64();
    let phase = Instant::now();
    for _ in 0..20 {
        guard(started)?;
        black_box(d.background.interval_increment(to, s.a)?);
    }
    let interval = phase.elapsed().as_secs_f64();
    let phase = Instant::now();
    let mut prepared = None;
    for _ in 0..20 {
        guard(started)?;
        prepared = Some(black_box(d.transport.prepare(&p, &g)?));
    }
    let prepare = phase.elapsed().as_secs_f64();
    let cache = prepared.unwrap();
    let phase = Instant::now();
    for _ in 0..200 {
        guard(started)?;
        black_box(cache.evaluate(absorbers, nh, dt)?);
    }
    let evaluate = phase.elapsed().as_secs_f64();
    let phase = Instant::now();
    for _ in 0..20 {
        guard(started)?;
        let mut v = p.clone();
        black_box(d.transport.inject(&mut v, &g, 1.0 / s.a - 1.0, dt)?);
    }
    let inject = phase.elapsed().as_secs_f64();
    let phase = Instant::now();
    let mut partition_nodes = 0;
    for _ in 0..20 {
        guard(started)?;
        let v = d.transport.partition_below_hi(&p, &end)?;
        partition_nodes = v.quadrature_nodes;
        black_box(v);
    }
    let partition = phase.elapsed().as_secs_f64();
    let phase = Instant::now();
    let mut counter = 0;
    for _ in 0..10 {
        guard(started)?;
        let mut v = s.clone();
        d.chemical_stage(&mut v, dt, &mut counter)?;
        if counter>1000 {return Err("profile chemical RHS cap1000".into());}
        black_box(v);
    }
    let chemistry = phase.elapsed().as_secs_f64();

    // Drop/join the8 pool through the zero-worker serial path before creating16.
    d.transport=d.transport.clone().with_threads(1)?;
    d.transport=d.transport.clone().with_threads(16)?;
    black_box(d.transport.prepare(&p,&g)?); //16 warm, excluded from timed prepare
    let phase=Instant::now();let mut prepared16=None;
    for _ in 0..20 {guard(started)?;prepared16=Some(black_box(d.transport.prepare(&p,&g)?));}
    let prepare16=phase.elapsed().as_secs_f64();let cache16=prepared16.unwrap();
    let debug8=format!("{cache:?}");let debug16=format!("{cache16:?}");
    if debug8!=debug16 {return Err("ordered prepared-cache value mismatch8vs16".into());}
    for (label,delta) in [("zero",0.0),("finite",dt)] {
      let w8=result_words(&cache.evaluate(absorbers,nh,delta)?);
      let w16=result_words(&cache16.evaluate(absorbers,nh,delta)?);
      if w8!=w16 {return Err("survival/rate/heat/event bit mismatch8vs16".into());}
      fs::write(out.join(format!("prepare8_{label}_words.json")),format!("{w8:?}\n"))?;
      fs::write(out.join(format!("prepare16_{label}_words.json")),format!("{w16:?}\n"))?;
    }
    fs::write(out.join("prepare8_ordered_cache.txt"),debug8)?;
    fs::write(out.join("prepare16_ordered_cache.txt"),debug16)?;
    let comparison=format!(r#"{{"kind":"samefixture_prepare_only8vs16_not_trajectory","prepare8_calls":20,"prepare16_calls":20,"warm_calls_each":1,"persistent_pool_warm_excluded_from_phase_timing":true,"maximum_configured_diagnostic_workers":16,"prepare8_wall_s":{prepare},"prepare16_wall_s":{prepare16},"ratio8_over16":{},"ordered_cache_values_equal":true,"all_public_result_f64_bits_equal_dt0_and_finite":true,"extra_evaluate_calls_for_bitcheck":4,"nodes":{},"prepared_capacity_bytes":{}}}"#,prepare/prepare16,cache.node_count(),cache.buffer_capacity_bytes());
    fs::write(out.join("prepare_thread_comparison.json"),comparison)?;

    let json=format!("{{\"kind\":\"finite_postcache005_hotpath_diagnostic_not_history\",\"checkpoint_a\":{},\"checkpoint_accepted\":{},\"cells\":{},\"occupied_active_cells\":{},\"cached_nodes\":{},\"partition_nodes_per_call\":{partition_nodes},\"proper_dt_s\":{dt},\"background_point_calls\":20,\"background_point_wall_s\":{background},\"interval_increment_calls\":20,\"interval_increment_wall_s\":{interval},\"prepare_calls\":20,\"prepare_wall_s\":{prepare},\"evaluate_calls\":200,\"evaluate_wall_s\":{evaluate},\"inject_calls\":20,\"inject_wall_s\":{inject},\"partition_calls\":20,\"partition_wall_s\":{partition},\"chemical_stage_calls\":10,\"chemical_stage_wall_s\":{chemistry},\"chemical_rhs_evaluations\":{counter},\"profile_wall_s\":{},\"native_source_unmodified\":true}}\n",
        s.a,s.accepted,d.transport.cell_count(),s.photons.iter().filter(|&&n|n>0.0).count(),cache.node_count(),started.elapsed().as_secs_f64());
    fs::write(out.join("profile.json"), &json)?;
    println!("{json}");
    Ok(())
}
