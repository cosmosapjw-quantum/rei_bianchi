//! Read-only ON06G checkpoint intake. No source/root/paired_trial call.
use rei_microphysics::paired_runtime::{energy_nodes,hh_checkpoint_decode,hh_checkpoint_encode,HhRunConfig,PairedConfig};
use rei_microphysics::coupled_primary::HhMode;
use std::path::Path;

// Compile the actual public ENERGY05 boundary without inventing a proof decoder.
// A linked Chain remains explicitly unable to authorize a whole owner macro.
#[allow(dead_code)]
fn require_linked_macro(chain: &hh_energy05::tangent_api::Chain,
                        request: &hh_energy05::return_api::Request,
                        time: f64) -> Result<(), hh_energy05::ForwardError> {
    chain.verify_for(request,time)?;
    chain.require_full_macro()
}

fn config(member: usize) -> HhRunConfig {
    HhRunConfig::new(PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16},
        if member < 2 {[1e-14;3]} else {[1.01e-14,0.99e-14,1e-14]},
        if member % 2 == 0 {HhMode::Off} else {HhMode::Lcs91}).unwrap()
}
fn inspect(input: &Path, out: &Path, time: f64) -> Result<(),Box<dyn std::error::Error>> {
    // Input-validation refusal creates no output. I/O failure can leave .pending;
    // A complete directory plus this process exit0 is required for durable success;
    // a directory alone does not prove that post-rename sync succeeded.
    let mut verified=Vec::new();
    for member in 0..4 {
        let bytes=std::fs::read(input.join(format!("member{member}.bin")))?;
        let c=config(member);
        let state=hh_checkpoint_decode(&c,&bytes)?;
        if state.base().time_s.to_bits()!=time.to_bits(){return Err("checkpoint clock mismatch".into());}
        let encoded=hh_checkpoint_encode(&c,&state)?;
        if bytes!=encoded {return Err("checkpoint roundtrip mismatch".into());}
        let np=energy_nodes(c.grid())?.len();
        if state.base().photons.len()!=np*128{return Err("direction shape mismatch".into());}
        verified.push((member,bytes,state));
    }
    std::fs::create_dir(out)?; // Exclusive reservation; never replace an existing output.
    let pending=out.join(".pending");std::fs::create_dir(&pending)?;
    use std::io::Write;
    for (member,bytes,_) in &verified {
        let mut f=std::fs::OpenOptions::new().write(true).create_new(true).open(pending.join(format!("member{member}.bin")))?;
        f.write_all(bytes)?;f.sync_all()?;
    }
    std::fs::File::open(&pending)?.sync_all()?;
    std::fs::rename(&pending,out.join("complete"))?;
    std::fs::File::open(out)?.sync_all()?;
    let parent=out.parent().filter(|p|!p.as_os_str().is_empty()).unwrap_or(Path::new("."));
    std::fs::File::open(parent)?.sync_all()?;
    for (member,bytes,state) in verified {
        println!("{{\"member\":{},\"time\":{:?},\"bytes\":{},\"directions\":128,\"nodes\":33,\"photons\":{},\"gas\":{:?},\"gas_box\":{:?},\"ledger_comp\":{:?},\"energy_comp\":{:?},\"hh_events\":{:?},\"hh_heat\":{:?},\"hh_comp\":{:?},\"byte_identity\":true,\"source_calls\":0}}",
            member,state.base().time_s,bytes.len(),state.base().photons.len(),
            [state.base().gas.fractions[0],state.base().gas.fractions[1],state.base().gas.fractions[2],state.base().gas.w_ev_per_h],
            state.base().gas_box.map(|v|[v.lo,v.hi]),state.base().ledger_comp,state.base().energy_comp,
            state.hh_events_per_h(),state.hh_heat_ev_per_h(),state.hh_compensation());
    }
    Ok(())
}
fn main() -> Result<(),Box<dyn std::error::Error>> {
    let args=std::env::args().collect::<Vec<_>>();
    if args.len()!=4{return Err("usage: checkpoint_probe INPUT NEW_OUTPUT EXPECTED_TIME".into());}
    inspect(Path::new(&args[1]),Path::new(&args[2]),args[3].parse()?)
}
#[cfg(test)]mod tests {
    use super::*;
    fn seed()->std::path::PathBuf{std::env::var("HH_SEED").unwrap().into()}
    #[test]fn real_seed_roundtrip_retains_all_intervals_and_compensations(){
        for member in 0..4{let bytes=std::fs::read(seed().join(format!("member{member}.bin"))).unwrap();
            let c=config(member);let s=hh_checkpoint_decode(&c,&bytes).unwrap();
            assert_eq!(s.base().time_s,1.6e11);assert_eq!(hh_checkpoint_encode(&c,&s).unwrap(),bytes);}
    }
    #[test]fn corrupt_checkpoint_refused_before_mutation(){
        let bytes=std::fs::read(seed().join("member1.bin")).unwrap();let mut bad=bytes.clone();bad[100]^=1;
        assert!(hh_checkpoint_decode(&config(1),&bad).is_err());
        let s=hh_checkpoint_decode(&config(1),&bytes).unwrap();assert_eq!(hh_checkpoint_encode(&config(1),&s).unwrap(),bytes);
    }
    #[test]fn off_and_lcs_are_separate_checkpoint_identities(){
        let bytes=std::fs::read(seed().join("member1.bin")).unwrap();assert!(hh_checkpoint_decode(&config(0),&bytes).is_err());
    }
    #[test]fn flrw_cannot_be_restored_as_bianchi(){
        let bytes=std::fs::read(seed().join("member1.bin")).unwrap();assert!(hh_checkpoint_decode(&config(3),&bytes).is_err());
    }
    #[test]fn aggregate_grid_cannot_substitute_for_128_directions(){
        let bytes=std::fs::read(seed().join("member1.bin")).unwrap();
        let wrong=HhRunConfig::new(PairedConfig{spectral_subdivisions:8,n_mu:1,n_phi:1},[1e-14;3],HhMode::Lcs91).unwrap();
        assert!(hh_checkpoint_decode(&wrong,&bytes).is_err());
    }
    fn scratch(label:&str)->std::path::PathBuf {
        std::env::temp_dir().join(format!("hh_energy06_{label}_{}_{}",std::process::id(),std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()))
    }
    #[test]fn restore_publication_is_complete_generation(){
        let out=scratch("complete");inspect(&seed(),&out,1.6e11).unwrap();
        assert!(out.join("complete").is_dir(),"no atomic complete generation was published");
        for i in 0..4{let n=format!("member{i}.bin");assert_eq!(std::fs::read(seed().join(&n)).unwrap(),std::fs::read(out.join("complete").join(&n)).unwrap());}
        assert!(!out.join(".pending").exists());std::fs::remove_dir_all(out).unwrap();
    }
    #[test]fn invalid_fourth_member_leaves_destination_absent(){
        let input=scratch("bad_input");let out=scratch("no_output");std::fs::create_dir(&input).unwrap();
        for i in 0..4{let n=format!("member{i}.bin");std::fs::copy(seed().join(&n),input.join(&n)).unwrap();}
        std::fs::write(input.join("member3.bin"),b"truncated").unwrap();
        assert!(inspect(&input,&out,1.6e11).is_err());assert!(!out.exists());std::fs::remove_dir_all(input).unwrap();
    }
    #[test]fn existing_destination_is_never_replaced(){
        let out=scratch("existing");std::fs::create_dir(&out).unwrap();std::fs::write(out.join("sentinel"),b"retain").unwrap();
        assert!(inspect(&seed(),&out,1.6e11).is_err());assert_eq!(std::fs::read(out.join("sentinel")).unwrap(),b"retain");std::fs::remove_dir_all(out).unwrap();
    }

    #[test]fn bare_relative_destination_uses_current_directory_for_sync(){
        let unique=scratch("relative");let out=std::path::PathBuf::from(unique.file_name().unwrap());
        let result=inspect(&seed(),&out,1.6e11);
        if out.exists(){std::fs::remove_dir_all(&out).unwrap();}
        assert!(result.is_ok(),"relative parent synchronization failed: {result:?}");
    }

}
