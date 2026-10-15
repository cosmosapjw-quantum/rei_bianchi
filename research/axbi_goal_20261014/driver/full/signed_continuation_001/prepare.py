from pathlib import Path
import hashlib,json
root=Path('.')
prep=root/'research/axbi_goal_20261014/driver/full/signed_continuation_001'
decision_path=root/'research/axbi_goal_20261014/driver/full/SIGNED_CONTINUATION_MECHANISM_DECISION.json'
d=json.loads(decision_path.read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=(root/'rust/rei_microphysics/examples/axbi_plus_resource_continuation.rs').read_text()
a=s.index('pub struct Expected'); b=s.index('pub fn resource_cap')
s=s[:a]+s[b:]
s=s.replace('if case != "SHEAR_PLUS" {','if !CASES.contains(&case) {')
s=s.replace('"SHEAR_PLUS_RESOURCE_CONTINUATION_001",','format!("{case}_RESOURCE_CONTINUATION_001"),')
s=s.replace('"{\\\"max_steps\\\":500000,\\\"max_attempts\\\":1550054,\\\"max_wall_s\\\":16976.389416854}\\n",','format!("{{\\\"max_steps\\\":{},\\\"max_attempts\\\":{},\\\"max_rhs\\\":{},\\\"max_wall_s\\\":{},\\\"output_budget_mib\\\":{}}}\\n",driver.config.max_steps,driver.config.max_attempts,driver.config.max_rhs,driver.config.max_wall_s,driver.config.output_budget_mib),')
s=s.replace('segment_id=SHEAR_PLUS_RESOURCE_CONTINUATION_001','segment_id={case}_RESOURCE_CONTINUATION_001')
a=s.index('fn cli()'); b=s.index('fn check_resources',a)
s=s[:a]+'''const CASES: [&str; 3] = ["SHEAR_MINUS", "SHEAR_HALF_PLUS", "SHEAR_HALF_MINUS"];
pub const OLD: &str = "d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185";
pub const NEW: &str = "4de69c1e68ebd395fe2d0b5580d901b9a82bde86cadbd11bdd07e5ad2042b4a1";
const KEYS: &[&str] = &["execution_authorized","start_authorized","case","segment","config","config_sha256","q_ref","predecessor","output","raw_output","checkpoint_sha256","terminal_sha256","old_source_sha256","current_source","current_source_sha256","decision","decision_sha256","review","review_sha256","example","example_sha256","binary_sha256","authority","authority_sha256","starting_state_debug","additional_steps","additional_attempts","additional_wall_s","additional_output_mib","effective_max_steps","effective_max_attempts","effective_max_rhs","effective_max_wall_s","effective_output_budget_mib"];
pub type Binding = std::collections::BTreeMap<String,String>;
pub fn parse_binding(text: &str) -> Result<Binding, ForwardError> {
    let mut values=Binding::new();
    for line in text.lines() {
        if line.is_empty() || line.starts_with('#') { continue; }
        let (k,v)=line.split_once('=').ok_or(err("AXBI_BINDING_FORMAT"))?;
        if !KEYS.contains(&k) || v.is_empty() || values.insert(k.into(),v.into()).is_some() { return Err(err("AXBI_BINDING_KEY")); }
    }
    Ok(values)
}
fn get<'a>(b: &'a Binding,k: &str)->Result<&'a str,ForwardError>{b.get(k).map(String::as_str).ok_or(err("AXBI_BINDING_MISSING"))}
pub fn execution_gate(b: &Binding)->Result<(),ForwardError>{
    if get(b,"execution_authorized")? != "true" || get(b,"start_authorized")? != "true" {return Err(err("AXBI_EXECUTION_NOT_AUTHORIZED"));}
    let case=get(b,"case")?;
    if !CASES.contains(&case) || get(b,"segment")? != format!("{case}_RESOURCE_CONTINUATION_001") {return Err(err("AXBI_RESUME_CASE"));}
    if get(b,"old_source_sha256")? != OLD || get(b,"current_source_sha256")? != NEW {return Err(err("AXBI_SOURCE_EPOCH"));}
    for k in KEYS {get(b,k)?;}
    Ok(())
}
fn hash_check(path: &str,digest: &str)->Result<(),ForwardError>{if sha256(Path::new(path))? != digest {Err(err("AXBI_PREDECESSOR_IDENTITY"))} else {Ok(())}}
pub fn verify_authority(b: &Binding)->Result<(),ForwardError>{
    hash_check(get(b,"authority")?,get(b,"authority_sha256")?)?;
    let authority=parse_binding(&fs::read_to_string(get(b,"authority")?).map_err(ioerr)?)?;
    for (k,v) in b {if !["authority","authority_sha256"].contains(&k.as_str()) && authority.get(k) != Some(v) {return Err(err("AXBI_AUTHORITY_BINDING"));}}
    Ok(())
}
pub fn apply_caps(cfg: &mut DriverConfig,b: &Binding)->Result<(),ForwardError>{
    let n=|k| -> Result<usize,ForwardError>{get(b,k)?.parse().map_err(|_|err("AXBI_RESOURCE_VALUE"))};
    let f=|k| -> Result<f64,ForwardError>{let x:f64=get(b,k)?.parse().map_err(|_|err("AXBI_RESOURCE_VALUE"))?;if !x.is_finite() || x<=0. {return Err(err("AXBI_RESOURCE_VALUE"));} Ok(x)};
    let ds=n("additional_steps")?; let da=n("additional_attempts")?; let dw=f("additional_wall_s")?;let dout=n("additional_output_mib")?;
    let steps=n("effective_max_steps")?;let attempts=n("effective_max_attempts")?;let wall=f("effective_max_wall_s")?;let output=n("effective_output_budget_mib")?;
    if ds==0 || da==0 || dout==0 || cfg.max_steps.checked_add(ds)!=Some(steps) || cfg.max_attempts.checked_add(da)!=Some(attempts) || cfg.output_budget_mib.checked_add(dout)!=Some(output) || cfg.max_wall_s+dw != wall || wall<=cfg.max_wall_s || n("effective_max_rhs")? != cfg.max_rhs {return Err(err("AXBI_RESOURCE_ARITHMETIC"));}
    cfg.max_steps=steps; cfg.max_attempts=attempts;cfg.max_wall_s=wall;cfg.output_budget_mib=output; Ok(())
}
fn cli() -> Result<(), ForwardError> {
    let args=std::env::args().skip(1).collect::<Vec<_>>();
    if args.len()!=4 {return Err(err("AXBI_CONTINUATION_USAGE"));}
    let mut a=Binding::new();
    for p in args.chunks_exact(2) {if !["--binding","--binding-sha256"].contains(&p[0].as_str()) || a.insert(p[0].clone(),p[1].clone()).is_some(){return Err(err("AXBI_CONTINUATION_USAGE"));}}
    let binding_path=get(&a,"--binding")?;let binding_sha=get(&a,"--binding-sha256")?;
    hash_check(binding_path,binding_sha)?;
    let b=parse_binding(&fs::read_to_string(binding_path).map_err(ioerr)?)?;
    execution_gate(&b)?; // Before any output creation or Driver construction.
    verify_authority(&b)?;
    let case=get(&b,"case")?;let config=get(&b,"config")?;
    let expected_config=match case {"SHEAR_MINUS"=>"d5227c1925d27a89e71bf59e1e5abd0557061f910172ea5fa9baacaece46c677","SHEAR_HALF_PLUS"=>"a5af5c6e61b2bca228baa8bf71e33e12ebbebb3638425704178badcba6135b81",_=>"d0c4d48fdcec402d4e2108d5ac205be00428846156f3613ff6e2e842e168bef2"};
    if get(&b,"config_sha256")?!=expected_config || config!=format!("research/axbi_goal_20261014/driver/full/{case}.cfg") {return Err(err("AXBI_CONFIG_BINDING"));}
    let predecessor=Path::new(get(&b,"predecessor")?);let out=Path::new(get(&b,"output")?);
    if out.exists() || Path::new(get(&b,"raw_output")?).exists(){return Err(err("AXBI_OUTPUT_EXISTS"));}
    if fs::read_to_string(predecessor.join("case_id.txt")).map_err(ioerr)?!=case {return Err(err("AXBI_RESUME_CASE"));}
    hash_check(config,expected_config)?;
    for (name,key) in [("config.cfg","config_sha256"),("checkpoint.txt","checkpoint_sha256"),("RETURN.txt","terminal_sha256"),("source_identity.txt","old_source_sha256")] {hash_check(predecessor.join(name).to_str().ok_or(err("AXBI_PATH"))?,get(&b,key)?)?;}
    for (path,key) in [("current_source","current_source_sha256"),("decision","decision_sha256"),("review","review_sha256"),("example","example_sha256")] {hash_check(get(&b,path)?,get(&b,key)?)?;}
    if get(&b,"decision_sha256")? != DECISION_SHA || get(&b,"review_sha256")? != REVIEW_SHA || fs::read_to_string(get(&b,"current_source")?).map_err(ioerr)? != compiled_identity(){return Err(err("AXBI_SOURCE_COMPATIBILITY"));}
    let binary=sha256(&std::env::current_exe().map_err(ioerr)?)?;
    if binary!=get(&b,"binary_sha256")? {return Err(err("AXBI_BINARY_IDENTITY"));}
    let text=fs::read_to_string(config).map_err(ioerr)?; let mut cfg=DriverConfig::read(&text)?;
    let q=match case {"SHEAR_MINUS"=>-0.01,"SHEAR_HALF_PLUS"=>0.005,_=>-0.005};
    if cfg.q_ref!=q || get(&b,"q_ref")?.parse::<f64>().map_err(|_|err("AXBI_Q_REF"))? != q {return Err(err("AXBI_Q_REF"));}
    let old=cfg.clone();apply_caps(&mut cfg,&b)?;
    let (driver,_)=Driver::new(cfg)?;let state=driver.read_checkpoint(&predecessor.join("checkpoint.txt"))?;
    if format!("{state:?}")!=get(&b,"starting_state_debug")? || state.photons.len()!=392 {return Err(err("AXBI_PREDECESSOR_STATE"));}
    driver.validate(&state,1e-8)?;
    let result=run_segment(driver,state,&text,out,case);
    if out.exists(){
        fs::copy(predecessor.join("source_identity.txt"),out.join("predecessor_source_identity.txt")).map_err(ioerr)?;
        fs::write(out.join("source_compatibility.json"),format!("{{\\"old_source_sha256\\":\\"{OLD}\\",\\"current_source_sha256\\":\\"{NEW}\\",\\"decision_sha256\\":\\"{DECISION_SHA}\\",\\"review_sha256\\":\\"{REVIEW_SHA}\\",\\"binding_sha256\\":\\"{binding_sha}\\",\\"authority_sha256\\":\\"{}\\",\\"checkpoint_sha256\\":\\"{}\\",\\"terminal_sha256\\":\\"{}\\",\\"new_binary_sha256\\":\\"{binary}\\",\\"original_binary_sha256\\":\\"32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca\\",\\"relation\\":\\"REVIEWED_RESOURCE_ONLY\\"}}\\n",get(&b,"authority_sha256")?,get(&b,"checkpoint_sha256")?,get(&b,"terminal_sha256")?)).map_err(ioerr)?;
        if out.join("RETURN.txt").exists(){let mut f=fs::OpenOptions::new().append(true).open(out.join("RETURN.txt")).map_err(ioerr)?;writeln!(f,"original_resource_config={old:?}\\nexecution_binding_path={binding_path}\\nexecution_binding_sha256={binding_sha}\\nold_source_sha256={OLD}\\ncurrent_source_sha256={NEW}\\nnew_binary_sha256={binary}\\nexternal_exit=PENDING_CONTROLLER_OBSERVATION\\nadditional_steps={}\\nadditional_attempts={}\\nadditional_wall_s={}\\nadditional_output_mib={}",get(&b,"additional_steps")?,get(&b,"additional_attempts")?,get(&b,"additional_wall_s")?,get(&b,"additional_output_mib")?).map_err(ioerr)?;}
    }
    result
}
''' +s[b:]
s+=f'\nconst DECISION_SHA: &str = "{sha(decision_path)}";\nconst REVIEW_SHA: &str = "{d["reviewed_input_sha256"]["research/axbi_goal_20261014/reviews/AX11_OUTPUT_ALLOCATION_REVIEW.json"]}";\n'
(root/'rust/rei_microphysics/examples/axbi_signed_resource_continuation.rs').write_text(s)
for case,c in d['actual_snapshot']['cases'].items():
    v={'execution_authorized':'false','start_authorized':'false','case':case,'segment':case+'_RESOURCE_CONTINUATION_001','config':c['original_config_path'],'config_sha256':c['original_config_sha256'],'q_ref':c['q_ref'],'old_source_sha256':d['original_compiled_identity_sha256'],'current_source_sha256':d['current_compiled_identity_sha256'],'current_source':'research/axbi_goal_20261014/convergence/output_allocation_repair/compiled_source_identity.txt','decision':str(decision_path),'decision_sha256':sha(decision_path),'review':'research/axbi_goal_20261014/reviews/AX11_OUTPUT_ALLOCATION_REVIEW.json','review_sha256':d['reviewed_input_sha256']['research/axbi_goal_20261014/reviews/AX11_OUTPUT_ALLOCATION_REVIEW.json']}
    (prep/(case+'.binding.template')).write_text(''.join(k+'='+val+'\n' for k,val in v.items()))
