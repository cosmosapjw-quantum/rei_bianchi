use rei_microphysics::axbi_bass_background::{sha256_bytes, BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::{BassResearchNumerics, Driver, DriverConfig};
use std::{
    fs,
    path::{Path, PathBuf},
};

const CSV: &str = "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133";
const MANIFEST: &str = "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed";
fn root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/bass_dynamic_20261016/source_grids")
}
fn id(case: &str, csv: &str, manifest: &str, grid: usize) -> BassSourceIdentity {
    BassSourceIdentity {
        producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
        source_csv_sha256: csv.into(),
        source_manifest_sha256: manifest.into(),
        case: case.into(),
        grid_points: grid,
    }
}
fn bg(case: &str) -> BassBackground {
    BassBackground::from_files(
        &root().join("pr164_121.csv"),
        &root().join("pr164_121.json"),
        id(case, CSV, MANIFEST, 121),
    )
    .unwrap()
}
fn temp() -> PathBuf {
    let p = std::env::temp_dir().join(format!(
        "bass-dynamic-test-{}-{:?}",
        std::process::id(),
        std::thread::current().id()
    ));
    fs::create_dir_all(&p).unwrap();
    p
}
fn fail<T: std::fmt::Debug>(r: Result<T, rei_microphysics::ForwardError>, tag: &str) {
    assert!(
        format!("{:?}", r.unwrap_err()).contains(tag),
        "expected {tag}"
    );
}
fn cfg() -> DriverConfig {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.99;
    c.transport_cells = 16;
    c.energy_subdivisions = 2;
    c
}

#[test]
fn uniform_birth_cohort_preserves_nodes_and_species_ledger() {
    let (driver, state) = Driver::new_bass(cfg(), bg("COLD_FLRW")).unwrap();
    let g = driver.geometry_point(state.a).unwrap().geometry().unwrap();
    let mut old = driver.transport.empty_state();
    let mut birth = driver.transport.empty_state();
    driver.transport.add_delta(&mut old, 0, 30.0, 0.3).unwrap();
    driver.transport.add_delta(&mut birth, 0, 30.0, 0.2).unwrap();
    let old_p = driver.transport.prepare(&old, &g).unwrap();
    let birth_p = driver.transport.prepare(&birth, &g).unwrap();
    let dt = 1e12;
    let absorbers = [1e-4, 0.0, 0.0];
    let tau = old_p.optical_depth_rows(absorbers, dt)[0].5[0];
    let both = old_p.with_uniform_birth(birth_p).unwrap();
    let out = driver.transport.evaluate(&both, absorbers, 1e-4, dt).unwrap();
    let phi = if tau==0.0 {1.0} else {-(-tau).exp_m1()/tau};
    let expected = 0.3/(1.0+tau)+0.2*phi;
    let observed: f64 = out.state.number.iter().sum();
    assert!((observed-expected).abs()<1e-13);
    assert!((0.5-observed-out.absorbed_per_h.iter().sum::<f64>()).abs()<1e-13);
    assert!((30.0*(0.5-observed)-out.binding_ev_per_h-out.heat_ev_per_h).abs()<1e-12);
}

#[test]
fn mixed_h_he_birth_nodes_conserve_number_energy_and_photo_events() {
    let (driver,state)=Driver::new_bass(cfg(),bg("COLD_FLRW")).unwrap();
    let g=driver.geometry_point(state.a).unwrap().geometry().unwrap();
    let mut old=driver.transport.empty_state();
    let mut birth=driver.transport.empty_state();
    for (ray,q,no,nb) in [(0,30.0,0.21,0.13),(1,40.0,0.18,0.11),(2,80.0,0.09,0.07)] {
        driver.transport.add_delta(&mut old,ray,q,no).unwrap();
        driver.transport.add_delta(&mut birth,ray,q,nb).unwrap();
    }
    let dt=2e12; let nh=1e-4; let absorber=[8e-5,7e-6,2e-6];
    let op=driver.transport.prepare(&old,&g).unwrap();
    let bp=driver.transport.prepare(&birth,&g).unwrap();
    let mut expected_n=0.0; let mut expected_u=0.0;
    let mut events=[0.0_f64;3];
    for (newborn,prepared) in [(false,&op),(true,&bp)] {
        for (_,q,n,_,_,tau) in prepared.optical_depth_rows(absorber,dt) {
            let total=tau.iter().sum::<f64>();
            let phi=if total==0.0 {1.0} else {-(-total).exp_m1()/total};
            let survived=if newborn {n*phi} else {n/(1.0+total)};
            expected_n+=survived; expected_u+=q*survived;
            for j in 0..3 { events[j]+=if newborn {
                n*tau[j]*(1.0-phi)/total
            } else { n*tau[j]/(1.0+total) }; }
        }
    }
    let combined=op.with_uniform_birth(bp).unwrap();
    let result=driver.transport.evaluate(&combined,absorber,nh,dt).unwrap();
    let (number,energy)=driver.transport.inventory(&result.state,&g).unwrap();
    assert!((number-expected_n).abs()<2e-13);
    assert!((energy-expected_u).abs()<2e-11);
    for j in 0..3 {
        assert!((result.absorbed_per_h[j]-events[j]).abs()<2e-13);
        assert!((result.photo.gamma_s[j]*absorber[j]*dt/nh-events[j]).abs()<2e-13);
    }
    let input_energy=30.0*(0.21+0.13)+40.0*(0.18+0.11)+80.0*(0.09+0.07);
    assert!((input_energy-energy-result.binding_ev_per_h-result.heat_ev_per_h).abs()<2e-11);
    let zero=driver.transport.evaluate(&combined,[0.0;3],nh,dt).unwrap();
    let (zn,zu)=driver.transport.inventory(&zero.state,&g).unwrap();
    assert!((zn-(0.21+0.13+0.18+0.11+0.09+0.07)).abs()<2e-13);
    assert!((zu-input_energy).abs()<2e-11);
    assert_eq!(zero.absorbed_per_h,[0.0;3]);
}

#[test]
fn full_exponential_frozen_preserves_constant_slab_stock_and_owners() {
    let (driver,state)=Driver::new_bass(cfg(),bg("COLD_FLRW")).unwrap();
    let g=driver.geometry_point(state.a).unwrap().geometry().unwrap();
    let mut old=driver.transport.empty_state();
    driver.transport.add_delta(&mut old,0,30.0,0.3).unwrap();
    let dt=1e12; let nh=1e-4; let absorber=[1e-4,0.0,0.0];
    let op=driver.transport.prepare(&old,&g).unwrap();
    let tau=op.optical_depth_rows(absorber,dt)[0].5[0];
    assert!(tau>0.0);
    let emitted=0.3*tau;
    let mut birth=driver.transport.empty_state();
    driver.transport.add_delta(&mut birth,0,30.0,emitted).unwrap();
    let bp=driver.transport.prepare(&birth,&g).unwrap();
    let exact=driver.transport.evaluate(&op.clone().with_full_exponential_birth(bp.clone()).unwrap(),absorber,nh,dt).unwrap();
    let mixed=driver.transport.evaluate(&op.with_uniform_birth(bp).unwrap(),absorber,nh,dt).unwrap();
    let exact_n: f64=exact.state.number.iter().sum();
    let mixed_n: f64=mixed.state.number.iter().sum();
    assert!((exact_n-0.3).abs()<2e-13);
    assert!(mixed_n>exact_n);
    assert!((0.3+emitted-exact_n-exact.absorbed_per_h.iter().sum::<f64>()).abs()<2e-13);
    assert!((30.0*(0.3+emitted-exact_n)-exact.binding_ev_per_h-exact.heat_ev_per_h).abs()<2e-11);
    assert!((exact.photo.gamma_s[0]*absorber[0]*dt/nh-exact.absorbed_per_h[0]).abs()<2e-13);
}

#[test]
fn full_exponential_frozen_multispecies_optical_depth_sweep() {
    let (driver,state)=Driver::new_bass(cfg(),bg("COLD_FLRW")).unwrap();
    let g=driver.geometry_point(state.a).unwrap().geometry().unwrap();
    let mut old=driver.transport.empty_state();
    let mut birth=driver.transport.empty_state();
    for (ray,q,no,nb) in [(0,30.0,0.21,0.13),(1,40.0,0.18,0.11),(2,80.0,0.09,0.07)] {
        driver.transport.add_delta(&mut old,ray,q,no).unwrap();
        driver.transport.add_delta(&mut birth,ray,q,nb).unwrap();
    }
    let nh=1e-4; let absorber=[8e-5,7e-6,2e-6];
    let op=driver.transport.prepare(&old,&g).unwrap();
    let bp=driver.transport.prepare(&birth,&g).unwrap();
    let rate=op.optical_depth_rows(absorber,1.0)[0].5.iter().sum::<f64>();
    assert!(rate>0.0);
    let input_energy=30.0*(0.21+0.13)+40.0*(0.18+0.11)+80.0*(0.09+0.07);
    for target_tau in [0.0,1e-12,1e-6,0.1,1.0,10.0,1e3] {
        let dt=target_tau/rate;
        let mut expected_n=0.0; let mut expected_u=0.0; let mut events=[0.0_f64;3];
        for (newborn,prepared) in [(false,&op),(true,&bp)] {
            for (_,q,n,_,_,tau_j) in prepared.optical_depth_rows(absorber,dt) {
                let tau=tau_j.iter().sum::<f64>();
                let phi=if tau==0.0 {1.0} else if tau<1e-5 {
                    1.0+tau*(-0.5+tau*(1.0/6.0+tau*(-1.0/24.0+tau/120.0)))
                } else {-(-tau).exp_m1()/tau};
                let stock=if newborn {n*phi} else {n*(-tau).exp()};
                expected_n+=stock; expected_u+=q*stock;
                for j in 0..3 {events[j]+=if newborn {
                    if tau==0.0 {0.0} else {n*tau_j[j]*(1.0-phi)/tau}
                } else {n*tau_j[j]*phi};}
            }
        }
        let result=driver.transport.evaluate(&op.clone().with_full_exponential_birth(bp.clone()).unwrap(),absorber,nh,dt).unwrap();
        let (observed_n,observed_u)=driver.transport.inventory(&result.state,&g).unwrap();
        assert!((observed_n-expected_n).abs()<2e-13,"tau={target_tau}");
        assert!((observed_u-expected_u).abs()<2e-11,"tau={target_tau}");
        for j in 0..3 {
            assert!((result.absorbed_per_h[j]-events[j]).abs()<2e-13,"tau={target_tau} species={j}");
            assert!((result.photo.gamma_s[j]*absorber[j]*dt/nh-events[j]).abs()<2e-13);
        }
        assert!((0.79-observed_n-result.absorbed_per_h.iter().sum::<f64>()).abs()<2e-13);
        assert!((input_energy-observed_u-result.binding_ev_per_h-result.heat_ev_per_h).abs()<2e-11);
        assert!(result.state.number.iter().all(|n| n.is_finite() && *n>=0.0));
    }
}

#[test]
fn research_checkpoint_rejects_different_operator() {
    let dir = temp().join("research-operator");
    fs::create_dir_all(&dir).unwrap();
    let output=dir.join("output.txt");
    fs::write(&output,"operator identity\n").unwrap();
    let path=dir.join("checkpoint.bass-v2");
    let (driver,state)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::UniformBirth).unwrap();
    driver.save_bass_checkpoint(&path,&state,"epoch-birth",&output).unwrap();
    let (same,_)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::UniformBirth).unwrap();
    assert_eq!(same.read_bass_checkpoint(&path,"epoch-birth",&output).unwrap().a,state.a);
    let (legacy,_)=Driver::new_bass(cfg(),bg("COLD_FLRW")).unwrap();
    fail(legacy.read_bass_checkpoint(&path,"epoch-birth",&output),"BASS_CHECKPOINT_VERSION_OR_SHAPE");
    let (tight,_)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::TightNewton).unwrap();
    fail(tight.read_bass_checkpoint(&path,"epoch-birth",&output),"BASS_CHECKPOINT_PROVIDER_SCHEMA");
    let (full,_)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::FullExponentialFrozen).unwrap();
    fail(full.read_bass_checkpoint(&path,"epoch-birth",&output),"BASS_CHECKPOINT_PROVIDER_SCHEMA");
    let (split,_)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::SplitBe).unwrap();
    fail(split.read_bass_checkpoint(&path,"epoch-birth",&output),"BASS_CHECKPOINT_PROVIDER_SCHEMA");
    let fullpath=dir.join("checkpoint-full-exponential.bass-v2");
    full.save_bass_checkpoint(&fullpath,&state,"epoch-birth",&output).unwrap();
    assert_eq!(full.read_bass_checkpoint(&fullpath,"epoch-birth",&output).unwrap().a,state.a);
    fail(same.read_bass_checkpoint(&fullpath,"epoch-birth",&output),"BASS_CHECKPOINT_PROVIDER_SCHEMA");
    fail(split.read_bass_checkpoint(&fullpath,"epoch-birth",&output),"BASS_CHECKPOINT_PROVIDER_SCHEMA");
}

#[test]
fn full_exponential_direct_chemical_stage_without_birth_uses_old_operator() {
    let (legacy, mut be_state)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::Legacy).unwrap();
    let (full, mut exact_state)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::FullExponentialFrozen).unwrap();
    let mut old=legacy.transport.empty_state();
    legacy.transport.add_delta(&mut old,0,30.0,0.3).unwrap();
    for state in [&mut be_state,&mut exact_state] {
        state.photons=old.number.clone();
        state.photon_energy_ref=old.energy_ref.clone();
        state.photon_support_lo=old.support_lo.clone();
        state.photon_support_hi=old.support_hi.clone();
    }
    let mut be_count=0;
    let mut exact_count=0;
    legacy.chemical_stage(&mut be_state,1e11,&mut be_count).unwrap();
    full.chemical_stage(&mut exact_state,1e11,&mut exact_count).unwrap();
    let be_stock: f64=be_state.photons.iter().sum();
    let exact_stock: f64=exact_state.photons.iter().sum();
    assert!(be_stock.is_finite() && exact_stock.is_finite());
    assert!(exact_stock < be_stock, "old exact survival must differ from BE: {exact_stock} {be_stock}");
}

#[test]
fn research_birth_lane_runs_original_hhe_owners() {
    let (legacy,mut old)=Driver::new_bass(cfg(),bg("COLD_FLRW")).unwrap();
    let (birth,mut revised)=Driver::new_bass_research(cfg(),bg("COLD_FLRW"),BassResearchNumerics::UniformBirth).unwrap();
    legacy.fixed_step(&mut old,1e-4).unwrap();
    birth.fixed_step(&mut revised,1e-4).unwrap();
    assert!((old.a-revised.a).abs()<1e-15);
    assert_eq!(old.ledgers.source_n,revised.ledgers.source_n);
    assert_eq!(old.ledgers.source_u,revised.ledgers.source_u);
    assert!(old.ledgers.absorbed_n>=0.0 && revised.ledgers.absorbed_n>=0.0);
    let (n,u)=birth.residuals(&revised).unwrap();
    assert!(n.abs()<1e-8 && u.abs()<1e-8);
    assert!(revised.gas.fractions.iter().all(|x| x.is_finite() && *x>=0.0));
}

#[test]
fn original_geometry_and_identity() {
    let b = bg("COLD_FLRW");
    assert!(b.max_hamiltonian_normalized < 3e-12);
    assert!(b.max_raychaudhuri_normalized < 1e-9);
    let p = b.point_at_scale(1.0 / 21.0).unwrap();
    assert_eq!(p.b, 0.0);
    assert_eq!(p.sigma, 0.0);
    let x = b.point_at_scale((1.0 / 21.0) * 0.0001_f64.exp()).unwrap();
    assert!(x.time_s > 0.0);
    assert!((b.point_at_time(x.time_s).unwrap().a - x.a).abs() < 1e-13);
    let signed = bg("SIGNED_MINUS").point_at_scale(1.0 / 21.0).unwrap();
    assert!(signed.sigma < 0.0);
}
#[test]
fn changed_csv_and_manifest_are_rejected() {
    let dir = temp();
    let csv = dir.join("a.csv");
    let manifest = dir.join("a.json");
    let mut data = fs::read(root().join("pr164_121.csv")).unwrap();
    data[100] ^= 1;
    fs::write(&csv, data).unwrap();
    fs::copy(root().join("pr164_121.json"), &manifest).unwrap();
    fail(
        BassBackground::from_files(&csv, &manifest, id("COLD_FLRW", CSV, MANIFEST, 121)),
        "BASS_SOURCE_CSV_SHA256",
    );
    fs::copy(root().join("pr164_121.csv"), &csv).unwrap();
    let mut data = fs::read(&manifest).unwrap();
    data[20] ^= 1;
    fs::write(&manifest, data).unwrap();
    fail(
        BassBackground::from_files(&csv, &manifest, id("COLD_FLRW", CSV, MANIFEST, 121)),
        "BASS_SOURCE_MANIFEST_SHA256",
    );
}
fn altered_source(field: &str, new: &str) -> (PathBuf, PathBuf, String, String) {
    let dir = temp();
    let csv = dir.join(format!("{field}.csv"));
    let manifest = dir.join(format!("{field}.json"));
    let old = fs::read_to_string(root().join("pr164_121.csv")).unwrap();
    let mut lines = old.lines().map(str::to_owned).collect::<Vec<_>>();
    let columns = lines[0].split(',').collect::<Vec<_>>();
    let k = columns.iter().position(|c| *c == field).unwrap();
    let mut row = lines[2].split(',').map(str::to_owned).collect::<Vec<_>>();
    row[k] = new.into();
    lines[2] = row.join(",");
    let bytes = format!("{}\n", lines.join("\n")).into_bytes();
    let hash = sha256_bytes(&bytes).unwrap();
    fs::write(&csv, bytes).unwrap();
    let oldmanifest = fs::read_to_string(root().join("pr164_121.json")).unwrap();
    let text = oldmanifest.replace(CSV, &hash);
    let mh = sha256_bytes(text.as_bytes()).unwrap();
    fs::write(&manifest, text).unwrap();
    (csv, manifest, hash, mh)
}
#[test]
fn signed_shear_and_nonmonotone_clock_are_rejected() {
    let (c, m, ch, mh) = altered_source("signed_s_over_H", "0.2");
    fail(
        BassBackground::from_files(&c, &m, id("COLD_FLRW", &ch, &mh, 121)),
        "BASS_SIGNED_SHEAR",
    );
    let (c, m, ch, mh) = altered_source("proper_elapsed_s", "-1.0");
    fail(
        BassBackground::from_files(&c, &m, id("COLD_FLRW", &ch, &mh, 121)),
        "BASS_PROPER_TIME_MONOTONIC",
    );
}
#[test]
fn hamiltonian_row_is_rejected() {
    let (c, m, ch, mh) = altered_source("H_mean_per_s", "1.0e-16");
    fail(
        BassBackground::from_files(&c, &m, id("COLD_FLRW", &ch, &mh, 121)),
        "BASS_HAMILTONIAN",
    );
}
#[test]
fn signed_geometry_redshift_work_uses_physical_inventory() {
    let (driver, mut state) = Driver::new_bass(cfg(), bg("SIGNED_MINUS")).unwrap();
    driver.seed_delta(&mut state, 0, 30.0, 1e-3).unwrap();
    let (n0, u0) = driver.photon_inventory(&state);
    let b0 = driver.geometry_point(state.a).unwrap().b;
    let to = state.a * 0.0001_f64.exp();
    driver.geometry_map(&mut state, to).unwrap();
    let (n1, u1) = driver.photon_inventory(&state);
    let b1 = driver.geometry_point(state.a).unwrap().b;
    eprintln!("BASS_SIGNED_PHOTON_WORK raw_ev_per_h={:.17e} denominator_ev_per_h={:.17e} work_ev_per_h={:.17e}",state.ledgers.photon_work-(u0-u1),u0.abs().max(u1.abs()),state.ledgers.photon_work);
    assert!(b1 < b0);
    assert!((n1 - n0).abs() < 1e-15);
    assert!(
        (state.ledgers.photon_work - (u0 - u1)).abs() < 1e-15,
        "work={} u0={} u1={} diff={}",
        state.ledgers.photon_work,
        u0,
        u1,
        state.ledgers.photon_work - (u0 - u1)
    );
    assert!(u1 > 0.0);
}
#[test]
fn checkpoint_binding_and_restart() {
    let dir = temp();
    let (driver, mut state) = Driver::new_bass(cfg(), bg("COLD_FLRW")).unwrap();
    driver.fixed_step(&mut state, 1e-4).unwrap();
    let output = dir.join("output.txt");
    fs::write(&output, "first output epoch\n").unwrap();
    let path = dir.join("checkpoint.bass");
    driver
        .save_bass_checkpoint(&path, &state, "epoch1", &output)
        .unwrap();
    let (reader, _) = Driver::new_bass(cfg(), bg("COLD_FLRW")).unwrap();
    let read = reader
        .read_bass_checkpoint(&path, "epoch1", &output)
        .unwrap();
    assert_eq!(read.a, state.a);
    assert_eq!(read.photons, state.photons);
    fail(
        driver.save_bass_checkpoint(&path, &state, "epoch1", &output),
        "BASS_CHECKPOINT_EXISTS",
    );
    fail(
        reader.read_bass_checkpoint(&path, "epoch2", &output),
        "BASS_CHECKPOINT_EPOCH_OUTPUT",
    );
    let mut wrong = cfg();
    wrong.transport_cells = 32;
    let (different, _) = Driver::new_bass(wrong, bg("COLD_FLRW")).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_PROVIDER_SCHEMA",
    );
    let mut changed_workers = cfg();
    changed_workers.transport_threads = 2;
    let (different, _) = Driver::new_bass(changed_workers, bg("COLD_FLRW")).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_CONFIG",
    );
    let (different, _) = Driver::new_bass(cfg(), bg("SIGNED_MINUS")).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_SOURCE_BINDING",
    );
    let grid = &root().join("matched_n121_241_481_retry/n0241");
    let b = BassBackground::from_files(
        &grid.join("PROPOSED_REI_BACKGROUND.csv"),
        &grid.join("PRODUCER_RECEIPT.json"),
        id(
            "COLD_FLRW",
            "30a9abf166005f3c2f4073eb532b0ffd35891827562ed9f0d6816329c625b6c9",
            "9abb74b98a2896a1aee50b373981d2cf3c0c5ba0b65bb7c8437245643c2a90bd",
            241,
        ),
    )
    .unwrap();
    let (different, _) = Driver::new_bass(cfg(), b).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_SOURCE_BINDING",
    );
    let saved = fs::read_to_string(&path).unwrap();
    let mut lines = saved.lines().map(str::to_owned).collect::<Vec<_>>();
    lines[8].push_str("|wrong_signed_shear_and_hamiltonian");
    let bad_geometry = dir.join("bad-geometry.bass");
    fs::write(&bad_geometry, format!("{}\n", lines.join("\n"))).unwrap();
    fail(
        reader.read_bass_checkpoint(&bad_geometry, "epoch1", &output),
        "BASS_CHECKPOINT_GEOMETRY_STATE",
    );
    fail(
        reader.save_checkpoint(&dir.join("legacy-write.txt"), &state),
        "BASS_REJECT_LEGACY_CHECKPOINT",
    );
    fs::write(&output, "changed output\n").unwrap();
    fail(
        reader.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_OUTPUT_SHA256",
    );
    let corrupt = dir.join("truncated.bass");
    fs::write(&corrupt, "BASS_REI_CHECKPOINT_V1\n").unwrap();
    fail(
        reader.read_bass_checkpoint(&corrupt, "epoch1", &output),
        "BASS_CHECKPOINT_TRUNCATED",
    );
    let legacy = dir.join("old-v4.txt");
    fs::write(&legacy, "AXBI_CHECKPOINT_V4\n").unwrap();
    fail(
        reader.read_bass_checkpoint(&legacy, "epoch1", &output),
        "BASS_REJECT_LEGACY_CHECKPOINT",
    );
    fail(
        reader.read_checkpoint(&legacy),
        "BASS_REJECT_LEGACY_CHECKPOINT",
    );
}
