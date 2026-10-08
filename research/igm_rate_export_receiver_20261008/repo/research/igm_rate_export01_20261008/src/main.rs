use std::{fs,path::Path};
use igm_rate_export01::{observe,validate};
use short_hhe_control::{record::{self,D},durable,radiation::{self,Grid,SPECIES},Fallible};
use rei_microphysics::{igm_config::HistoryConfig,igm_background::{FlatFlrwConfig,FlatFlrwBackground},igm_source::ConstantSource,HHeModel,AtomicProvider,verner_cutoff_ev,audit_counts};

// This purpose-bound loader accepts ONLY the already validated, build-pinned
// archived configuration. It reconstructs metadata for observation/replay;
// it is not a replacement general parser and cannot validate a new history.
fn archived_metadata(text:&str)->Fallible<HistoryConfig> {
    const PINNED:&str=include_str!("../../../../source/rei-next-nodes/long-flrw/configs/igm_manufactured_z12_to10.cfg");
    if text!=PINNED {return Err("ARCHIVED_CONFIG_SOURCE_NOT_PINNED".into())}
    let mut m=std::collections::BTreeMap::new();for l in text.lines(){let l=l.trim();if l.is_empty()||l.starts_with('#'){continue}let(k,v)=l.split_once('=').ok_or("CONFIG")?;if m.insert(k,v).is_some(){return Err("CONFIG_DUPLICATE".into())}}
    let f=|k:&str|->Fallible<f64>{m.get(k).ok_or("CONFIG_KEY")?.parse().map_err(short_hhe_control::err)};
    let u=|k:&str|->Fallible<usize>{m.get(k).ok_or("CONFIG_KEY")?.parse().map_err(short_hhe_control::err)};
    let start=-f("z_start")?.ln_1p();let end=-f("z_end")?.ln_1p();let model_id=m["model_id"].to_string();
    let background=FlatFlrwBackground::new(FlatFlrwConfig{h0_per_s:f("h0")?,omega_r:f("omega_r")?,omega_m:f("omega_m")?,omega_b:f("omega_b")?,omega_lambda:f("omega_lambda")?,helium_mass_fraction:f("y_he")?,tcmb0_k:f("tcmb0")?,ln_a_min:start,ln_a_max:end,parameter_source:model_id.clone()}).map_err(short_hhe_control::err)?;
    Ok(HistoryConfig{model_id,provider_id:m["provider_id"].to_string(),closure_id:m["closure_id"].to_string(),background,start,end,fractions:[f("x_hii")?,f("x_heii")?,f("x_heiii")?],temperature_k:f("temperature_k")?,source:ConstantSource{photons_per_h_per_s:f("source_rate")?,energy_min_ev:f("energy_min_ev")?,energy_max_ev:f("energy_max_ev")?},birth_panels:u("birth_panels")?,energy_panels:u("energy_panels")?,max_dln_a:f("max_dln_a")?,min_dln_a:f("min_dln_a")?,output_panels:u("output_panels")?,max_packets:u("max_packets")?,max_steps:u("max_steps")?})
}

fn checked_read(p:&Path,cap:usize)->Fallible<Vec<u8>> {let m=fs::symlink_metadata(p).map_err(short_hhe_control::err)?;if !m.file_type().is_file()||m.len()>cap as u64{return Err("FILE_CAP_OR_SYMLINK".into())}fs::read(p).map_err(short_hhe_control::err)}
fn pinned_read(p:&Path,n:usize,sha:&str)->Fallible<Vec<u8>> {let b=checked_read(p,n)?;if b.len()!=n||durable::sha(&b)?!=sha{return Err("ACCEPTED_INPUT_PIN_MISMATCH".into())}Ok(b)}
fn delta(a:(usize,usize),b:(usize,usize))->[usize;2]{[b.0-a.0,b.1-a.1]}
fn run()->Fallible<()> {
    let args:Vec<_>=std::env::args().collect();if args.len()!=3{return Err("payload_directory fresh_output_directory".into())}
    let input=Path::new(&args[1]);let output=Path::new(&args[2]);if output.exists(){return Err("FRESH_OUTPUT_REQUIRED".into())}
    let first=audit_counts::read();
    let raw=pinned_read(&input.join("context.bin"),39983,"e74580584a74ad4bddc4c65933a8454a8a6cbde965623f75affa9ee6b745b6fb")?;let mut d=D{b:&raw,i:0};
    let pin=d.text(256)?;if pin!="e34740bf7972cc4bd9223373024450fdb85dab25331e8354e1273701134c2cd0"{return Err("BUILD_CONTEXT".into())}
    let config=d.text(65536)?;if d.text(1024)?!=record::AUTHORITY||d.n()?!=192||d.n()?!=2{return Err("ORIGINAL_SCHEMA_CLOCK".into())}
    let values=d.a::<8>()?;let fractions=d.a::<3>()?;let initial=d.a::<4>()?;
    let base=d.n()? as usize;let order=d.n()? as usize;let n=d.size(4096)?;
    let mut stored=Vec::new();for _ in 0..n {let x=d.a::<2>()?;stored.push((x[0],x[1]));}if d.i!=d.b.len(){return Err("TRAILING_CONTEXT".into())}
    let cfg=archived_metadata(&config)?;
    if !record::bits_eq(&values,&[cfg.start,cfg.end,cfg.max_dln_a,cfg.min_dln_a,cfg.temperature_k,cfg.source.photons_per_h_per_s,cfg.source.energy_min_ev,cfg.source.energy_max_ev])||!record::bits_eq(&fractions,&cfg.fractions){return Err("CONFIG_CONTEXT".into())}
    let grid=Grid::new(&cfg,base,order)?;
    if n!=2440||grid.nodes.len()!=n||!grid.nodes.iter().zip(&stored).all(|(a,b)|a.0.to_bits()==b.0.to_bits()&&a.1.to_bits()==b.1.to_bits()) {return Err("GRID_RECIPE_NOT_BITWISE_ORIGINAL".into())}
    if durable::Context::new(&cfg,&grid,initial).bytes!=raw {return Err("RECONSTRUCTED_CONTEXT_NOT_EXACT".into())}
    let bytes=pinned_read(&input.join("typed.bin"),3336248,"9929edc36232b3620264f3a8b3cf55104ba31c4f63df238f02ed25079738b2b0")?;let mut d=D{b:&bytes,i:0};let state=record::read_state(&mut d)?;if d.i!=bytes.len(){return Err("TRAILING_TYPED_STATE".into())}
    let head=pinned_read(&input.join("HEAD"),3376662,"786b97e47fc58897f8ed2eacf58df3b75ff465107e3c0453241823e354b060d3")?;
    if !head.starts_with(durable::MAGIC){return Err("HEAD_SCHEMA".into())}let env=&head[durable::MAGIC.len()..];if env.len()<65||env[64]!=b'\n'||durable::sha(&env[65..])?.as_bytes()!=&env[..64] {return Err("HEAD_CHECKSUM".into())}
    if durable::sha(&head)?!=String::from_utf8(pinned_read(&input.join("committed-2"),64,"6d8d8db5384a387b0f69a7d4bd07f4ff38bb534a72e0a6bef737117bd171e0c0")?).map_err(short_hhe_control::err)?{return Err("COMMIT_MARKER".into())}
    let mut d=D{b:&env[65..],i:0};let k=d.size(1024*1024)?;if d.take(k)?!=raw{return Err("HEAD_CONTEXT".into())}
    // Namespace is read as archival evidence only, never used as restart authority.
    let _namespace=d.text(65536)?;let _attempt=d.n()?;let _initial_material=d.f()?;
    if d.b[d.i..]!=bytes {return Err("ACCEPTED_HEAD_TYPED_IDENTITY".into())}
    record::verify_state(&cfg,&grid,&state,initial)?;
    if record::science_image(&state)!=String::from_utf8(pinned_read(&input.join("step2.science.txt"),55214,"84547fa28929112ab30e6b994ff20a2b9290706559ed9d75c2cdef3a000556e8")?).map_err(short_hhe_control::err)?{return Err("SCIENCE_IMAGE_IDENTITY".into())}
    if state.accepted_records.len()!=2||state.s.to_bits()!=radiation::time_at(&cfg,2,192).to_bits(){return Err("ACCEPTED_TRANSACTION_EPOCH".into())}
    let after_replay=audit_counts::read();if delta(first,after_replay)!=[0,0]{return Err("REPLAY_SCIENCE_COST".into())}
    let p=cfg.background.at_ln_a(state.s).map_err(short_hhe_control::err)?;
    let observation=observe(&grid,state.s,&state.density,p)?;let after_observer=audit_counts::read();
    if delta(after_replay,after_observer)!=[0,3*n]{return Err("OBSERVER_COST".into())}
    let legacy=radiation::gamma(&grid,state.s,&state.density,p)?;let after_parity=audit_counts::read();
    if !record::bits_eq(&legacy,&observation.gamma)||delta(after_observer,after_parity)!=[0,3*n]{return Err("ORIGINAL_GAMMA_ARITHMETIC_PARITY".into())}
    let mut controls=0;
    let mut bad=grid.clone();bad.nodes[0].1=-1.;if validate(&bad,state.s,&state.density,p).is_ok(){return Err("NEGATIVE_WEIGHT_NOT_REFUSED".into())}controls+=1;
    if validate(&grid,f64::NAN,&state.density,p).is_ok()||validate(&grid,state.s,&state.density[..n-1],p).is_ok(){return Err("CONTEXT_NOT_REFUSED".into())}controls+=2;
    let mut f=state.density.clone();f[0]=-1.;if validate(&grid,state.s,&f,p).is_ok(){return Err("NEGATIVE_DENSITY_NOT_REFUSED".into())}controls+=1;
    for species in SPECIES {let t=verner_cutoff_ev(species);let below=f64::from_bits(t.to_bits()-1);let above=f64::from_bits(t.to_bits()+1);let provider=AtomicProvider::reference();if provider.cross_section(species,below).map_err(short_hhe_control::err)?!=0.||provider.cross_section(species,t).map_err(short_hhe_control::err)?<=0.||provider.cross_section(species,above).map_err(short_hhe_control::err)?<=0.{return Err("PROVIDER_THRESHOLD".into())}controls+=1;}
    let after_tests=audit_counts::read();if delta(after_parity,after_tests)!=[0,9]||record::state_bytes(&state)!=bytes{return Err("STATE_OR_TEST_COST".into())}
    let c=HHeModel::controlled_fixture();let sigma_t=6.6524587051e-25_f64; // exact existing igm_thermal.rs constant
    fs::create_dir(output).map_err(short_hhe_control::err)?;
    let report=format!("{{\"epoch_ln_a\":{:?},\"gas\":{:?},\"background\":{:?},\"constants\":{:?},\"chi_ev\":{:?},\"provider_cutoffs_ev\":{:?},\"Gamma\":{:?},\"incident_Ecal\":{:?},\"gamma_native\":{:?},\"node_count\":{},\"accepted_transactions\":2,\"cost\":{{\"stored_replay\":{:?},\"six_moment_observer\":{:?},\"original_gamma_parity\":{:?},\"threshold_tests\":{:?}}},\"native_controls\":{},\"grid_context_bitwise\":true,\"state_unchanged\":true}}\n",state.s,state.y,record::context(p),[c.c_cm_s,c.kb_erg_k,c.ev_erg,sigma_t*c.c_cm_s],c.threshold_ev,SPECIES.map(verner_cutoff_ev),observation.gamma,observation.incident_ev,legacy,n,delta(first,after_replay),delta(after_replay,after_observer),delta(after_observer,after_parity),delta(after_parity,after_tests),controls);
    fs::write(output.join("observation.raw.json"),report).map_err(short_hhe_control::err)?;
    let mut rows=String::new();for x in observation.samples{rows.push_str(&x.map(|v|format!("{:016x}",v.to_bits())).join(","));rows.push('\n');}
    fs::write(output.join("samples.binary64.csv"),rows).map_err(short_hhe_control::err)?;
    println!("EXPORT01_PASS nodes={n} replay={:?} observer={:?} parity={:?} threshold_tests={:?}",delta(first,after_replay),delta(after_replay,after_observer),delta(after_observer,after_parity),delta(after_parity,after_tests));Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("{e}");std::process::exit(2)}}
