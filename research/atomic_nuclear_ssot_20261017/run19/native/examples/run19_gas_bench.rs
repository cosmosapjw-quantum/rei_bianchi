//! Bounded same-executable native core comparison; no trajectory integration.
//! Old gas assembly is included byte-for-byte from RUN13. Its D direct wrapper
//! uses the unchanged shared event/energy implementation in this RUN19 fork.
pub use rei_iso_couple_reference::{HHeModel,deuterium_atomic,full_network,igm_rates,isotope_state};
use rei_iso_couple_reference::{
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState,NetworkConfig},
    gas_reference_rhs::{gas_rates_with_backend,GasRateWorkspace,GasRates,GasBatchStats,gas_rates_batch_into},
    isotope_state::{IsotopeNumberState,IsotopeSpecies as S},
    mixture_eos::{MixtureState,KB_J_K},
    rate_table::{IgmRateBackend,IgmRateTable},
};
use std::{hint::black_box,sync::Arc,time::Instant};
#[allow(dead_code)]
#[path="../../../run13/recovered/code/rei_bass_coupled/src/gas_reference_rhs.rs"]
mod original_gas;

fn fixture(t:f64,variant:usize)->FullState {
    let mut n=[0.0;13];
    for(s,v)in[(S::H1Neutral,180.0),(S::H1Ionized,20.0),(S::DNeutral,0.0045),
        (S::DIonized,0.0005),(S::He4Neutral,12.0),(S::He4SinglyIonized,3.0),(S::He4DoublyIonized,1.0)]{
        n[s as usize]=v;
    }
    n[S::H1Neutral as usize]-=variant as f64;n[S::He4Neutral as usize]+=variant as f64;
    let nuclei=IsotopeNumberState::new(n).unwrap();
    let u=1.5*KB_J_K*nuclei.thermal_particle_density_all_thermal_m3().unwrap()*t;
    FullState{gas:MixtureState{nuclei,thermal_j_m3:u},photon_bins:Vec::new(),
        escaped_j_m3:0.0,cmb_reservoir_j_m3:0.0,elapsed_s:0.0}
}
fn config()->NetworkConfig{
    let h=HHeModel::controlled_fixture().threshold_ev[0];
    let mut c=NetworkConfig::source_bound(DAtomicProvider::new(h,h+0.0037,"RUN19_BENCH_THRESHOLD").unwrap(),"RUN19_BENCH_SOURCE");
    c.use_photo=false;c.cmb_temperature_k=29.0;c
}
fn run(mode:&str,states:&[FullState],c:&NetworkConfig,backend:&IgmRateBackend,loops:usize)
    ->(f64,f64,GasBatchStats){
    let mut workspace=GasRateWorkspace::new(backend);
    let mut output=vec![GasRates::default();states.len()];
    let mut checksum=0.0;let mut stats=GasBatchStats::default();
    let start=Instant::now();
    for _ in 0..loops {match mode {
        "original"=>for s in states{let q=black_box(original_gas::gas_rates(black_box(s),black_box(c),7).unwrap());checksum+=q.heat;},
        "shared"=>for s in states{let q=black_box(gas_rates_with_backend(black_box(s),black_box(c),7,black_box(backend)).unwrap());checksum+=q.heat;},
        "cached"=>for s in states{let q=black_box(workspace.evaluate(black_box(s),black_box(c),7).unwrap());checksum+=q.heat;},
        "batch1"|"batch2"|"batch4"=>{
            let workers=if mode=="batch1"{1}else if mode=="batch2"{2}else{4};
            let st=gas_rates_batch_into(black_box(states),black_box(c),7,black_box(backend),&mut output,workers).unwrap();
            stats.evaluations+=st.evaluations;stats.preparations+=st.preparations;stats.exact_temperature_hits+=st.exact_temperature_hits;
            for q in black_box(&output){checksum+=q.heat;}
        },
        _=>panic!("unknown mode"),
    }}
    let seconds=start.elapsed().as_secs_f64();
    if mode=="cached"{stats=workspace.stats;}
    (seconds,black_box(checksum),stats)
}
fn main(){
    let mut probe=false;let mut target=8192usize;let mut repeats=5usize;
    let mut args=std::env::args().skip(1);
    while let Some(a)=args.next(){match a.as_str(){
        "--probe"=>probe=true,
        "--target-evaluations"=>target=args.next().unwrap().parse().unwrap(),
        "--repetitions"=>repeats=args.next().unwrap().parse().unwrap(),
        _=>panic!("usage: run19_gas_bench [--probe] [--target-evaluations 8192] [--repetitions 5]"),
    }}
    assert!((1..=65536).contains(&target)&&(1..=7).contains(&repeats));
    if probe{target=1024;repeats=1;}
    let table_start=Instant::now();let table=IgmRateTable::build_default().unwrap();
    let construction=table_start.elapsed().as_secs_f64();let table_bytes=table.storage_bytes();
    let direct=IgmRateBackend::Direct;let table=IgmRateBackend::Table(Arc::new(table));
    let c=config();let mut rows=Vec::new();
    let sizes:Vec<_>=if probe{vec![512]}else{vec![1,32,512,4096]};
    for pattern in ["same_temperature","varying_temperature"]{for n in &sizes{
        let states:Vec<_>=(0..*n).map(|i|fixture(if pattern=="same_temperature"{10000.0}
            else{9500.0+((i*104729)%5000)as f64},i%5)).collect();
        let unique:std::collections::BTreeSet<_>=states.iter().map(|s|s.gas.eos().unwrap().temperature_k.to_bits()).collect();
        let loops=target.div_ceil(*n);let mut modes=vec![("direct","original"),("direct","shared"),("direct","cached"),
            ("direct","batch1"),("table","shared"),("table","cached"),("table","batch1")];
        if *n>=512{modes.extend([("direct","batch2"),("direct","batch4"),("table","batch2"),("table","batch4")]);}
        for(name,mode)in modes{
            let backend=if name=="direct"{&direct}else{&table};
            if !probe{black_box(run(mode,&states,&c,backend,1));}
            let mut seconds=Vec::new();let mut sums=Vec::new();let mut counts=Vec::new();
            for _ in 0..repeats{let(dt,sum,stats)=run(mode,&states,&c,backend,loops);
                seconds.push(dt);sums.push(sum);counts.push(format!("{{\"evaluations\":{},\"preparations\":{},\"hits\":{}}}",stats.evaluations,stats.preparations,stats.exact_temperature_hits));}
            let mut sorted=seconds.clone();sorted.sort_by(f64::total_cmp);let median=sorted[sorted.len()/2];
            rows.push(format!("{{\"pattern\":\"{pattern}\",\"n\":{n},\"unique_eos_temperature_bits\":{},\"backend\":\"{name}\",\"mode\":\"{mode}\",\"loops\":{loops},\"evaluations_per_repetition\":{},\"seconds\":{:?},\"median_ns_per_rhs\":{:.17e},\"checksums\":{:?},\"stats\":[{}]}}",
                unique.len(),loops*n,seconds,median*1e9/(loops*n)as f64,sums,counts.join(",")));
        }
    }}
    println!("{{\"schema\":\"REI_RUN19_CORE_BENCH_V1\",\"probe\":{probe},\"table_build_seconds\":{construction:.17e},\"table_payload_bytes\":{table_bytes},\"mask\":7,\"repetitions\":{repeats},\"target_evaluations\":{target},\"timing_scope\":\"steady_rhs_with_preallocated_output_includes_scoped_thread_start_and_join\",\"f64_flags\":\"release_default_no_fast_math_no_target_cpu_override\",\"ivps\":0,\"rows\":[{}]}}",rows.join(","));
}
