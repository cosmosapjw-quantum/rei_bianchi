use std::{fs,path::PathBuf,time::Instant};
use axbi_temperature_rate_integration::{candidate_driver,provider::{Backend,Provider}};
fn main(){
    let args=std::env::args().skip(1).collect::<Vec<_>>();
    let mut config=None;let mut output=None;let mut case=None;let mut backend=None;let mut table=None;
    let mut i=0;
    while i<args.len(){
        let key=&args[i];
        if !["--config","--output","--case","--backend","--table"].contains(&key.as_str()){
            eprintln!("unknown or disallowed argument {key}");std::process::exit(2)
        }
        i+=1;
        let value=args.get(i).unwrap_or_else(||{eprintln!("missing {key} value");std::process::exit(2)}).clone();
        match key.as_str(){"--config"=>config=Some(value),"--output"=>output=Some(value),"--case"=>case=Some(value),"--backend"=>backend=Some(value),"--table"=>table=Some(value),_=>unreachable!()}
        i+=1;
    }
    let (Some(config),Some(output),Some(case),Some(backend),Some(table))=(config,output,case,backend,table) else {
        eprintln!("usage: axbi_temperature_rate_integration --config PATH --backend DIRECT|TABLE --table PATH --output NEW_DIR --case ID");std::process::exit(2)
    };
    let output=PathBuf::from(output);
    if output.exists(){eprintln!("AXBI_OUTPUT_EXISTS");std::process::exit(2)}
    let load_start=Instant::now();
    let provider=match backend.as_str(){"DIRECT"=>Provider::direct(),"TABLE"=>match Provider::load(&PathBuf::from(&table)){Ok(v)=>v,Err(e)=>{eprintln!("table load: {e}");std::process::exit(1)}},_=>{eprintln!("invalid backend");std::process::exit(2)}};
    let load_s=load_start.elapsed().as_secs_f64();
    let identity=format!("backend={:?}\ntable_path={}\ncanonical_identity_bytes={}\n",provider.backend(),table,rei_microphysics::axbi_driver::compiled_identity().len());
    let text=fs::read_to_string(config).unwrap_or_else(|e|{eprintln!("config: {e}");std::process::exit(1)});
    let run_start=Instant::now();
    let result=candidate_driver::run(&text,&output,&case,false,provider.clone());
    if output.exists(){
        let (coeff,lookups,fallbacks)=provider.counts();
        let _=fs::write(output.join("candidate_identity.txt"),format!("{}candidate_source_bytes={}\nbackend_label={}\n",identity,candidate_driver::compiled_identity().len(),backend));
        let _=fs::write(output.join("provider_counters.txt"),format!("load_s={load_s:.17e}\nrun_s={:.17e}\ncoefficient_calls={coeff}\nlookups={lookups}\nfallbacks={fallbacks}\n",run_start.elapsed().as_secs_f64()));
    }
    if let Err(e)=result{eprintln!("{e:?}");std::process::exit(1)}
    if provider.backend()==Backend::Table && provider.counts().0>5_000_000{eprintln!("coefficient cap exceeded");std::process::exit(1)}
}
