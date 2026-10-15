from pathlib import Path
import hashlib,json
r=Path('.'); prep=r/'research/axbi_goal_20261014/driver/full/signed_continuation_001'
s=(r/'rust/rei_microphysics/tests/axbi_plus_resource_continuation.rs').read_text().replace('axbi_plus_resource_continuation.rs','axbi_signed_resource_continuation.rs').replace('post_plus_001/rust/fixtures','signed_continuation_001/fixtures')
a=s.index('#[test]\nfn identity_checks'); b=s.index('#[test]\nfn cumulative_caps',a)
s=s[:a]+'''#[test]
fn strict_templates_and_authority_reject_without_output() {
    for case in ["SHEAR_MINUS","SHEAR_HALF_PLUS","SHEAR_HALF_MINUS"] {
        let path=PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../research/axbi_goal_20261014/driver/full/signed_continuation_001").join(format!("{case}.binding.template"));
        let text=fs::read_to_string(path).unwrap();
        let b=wrapper::parse_binding(&text).unwrap();
        assert!(wrapper::execution_gate(&b).is_err());
        assert!(wrapper::parse_binding(&(text.clone()+"case=ZERO\\n")).is_err());
        assert!(wrapper::parse_binding(&(text+"unknown=value\\n")).is_err());
        let mut changed=b.clone();changed.insert("case".into(),"ZERO".into());assert!(wrapper::execution_gate(&changed).is_err());
        changed.insert("execution_authorized".into(),"true".into());changed.insert("start_authorized".into(),"true".into());assert!(wrapper::execution_gate(&changed).is_err());
        changed=b;changed.insert("current_source_sha256".into(),wrapper::OLD.into());assert!(wrapper::execution_gate(&changed).is_err());
    }
    let root=workspace("authority");let authority=root.join("authority.binding");
    fs::write(&authority,"execution_authorized=true\\ncase=SHEAR_MINUS\\n").unwrap();
    let mut b=wrapper::parse_binding("execution_authorized=true\\ncase=SHEAR_HALF_PLUS\\n").unwrap();
    b.insert("authority".into(),authority.to_str().unwrap().into());b.insert("authority_sha256".into(),wrapper::sha256(&authority).unwrap());assert!(wrapper::verify_authority(&b).is_err());
    b.insert("authority_sha256".into(),"0".repeat(64));assert!(wrapper::verify_authority(&b).is_err());
}
#[test]
fn resource_changes_are_checked_and_rhs_ceiling_retained() {
    let mut cfg=DriverConfig::baseline();
    let text=format!("additional_steps=1\\nadditional_attempts=3\\nadditional_wall_s=10\\nadditional_output_mib=1792\\neffective_max_steps={}\\neffective_max_attempts={}\\neffective_max_wall_s={}\\neffective_output_budget_mib=2048\\neffective_max_rhs={}\\n",cfg.max_steps+1,cfg.max_attempts+3,cfg.max_wall_s+10.,cfg.max_rhs);
    let b=wrapper::parse_binding(&text).unwrap();wrapper::apply_caps(&mut cfg,&b).unwrap();
    let mut bad=b.clone();bad.insert("effective_max_rhs".into(),"99999999".into());assert!(wrapper::apply_caps(&mut DriverConfig::baseline(),&bad).is_err());
    bad=b;bad.insert("additional_wall_s".into(),"NaN".into());assert!(wrapper::apply_caps(&mut DriverConfig::baseline(),&bad).is_err());
}
''' + s[b:]
# Run exact parity test independently for all approved signs.
s=s.replace('fn component() -> (Driver, DriverState) {','fn component() -> (Driver, DriverState) { component_q(-0.01) }\nfn component_q(q: f64) -> (Driver, DriverState) {').replace('cfg.q_ref = 0.01;','cfg.q_ref = q;')
s=s.replace('fn exact_resume_matches_uninterrupted_kernel_and_preserves_prefix() {','fn exact_resume_matches_uninterrupted_kernel_and_preserves_prefix() {\n for (case,q) in [("SHEAR_MINUS",-0.01),("SHEAR_HALF_PLUS",0.005),("SHEAR_HALF_MINUS",-0.005)] {')
s=s.replace('workspace("equivalence")','workspace(case)').replace('let (driver, mut prefix) = component();','let (driver, mut prefix) = component_q(q);')
a=s.index('fn exact_resume'); b=s.index('#[test]',a)
part=s[a:b].replace('"SHEAR_PLUS"','case').replace('terminal.contains("segment_id=SHEAR_PLUS_RESOURCE_CONTINUATION_001")','terminal.contains(&format!("segment_id={case}_RESOURCE_CONTINUATION_001"))')
part=part.rstrip()+'\n}\n'
s=s[:a]+part+s[b:]
s=s.replace('"SHEAR_PLUS"','"SHEAR_MINUS"')
(r/'rust/rei_microphysics/tests/axbi_signed_resource_continuation.rs').write_text(s)
# Preserve streaming join and scientific CSV checks from reviewed composer.
s=(r/'research/axbi_goal_20261014/driver/full/post_cap_001/compose_zero_history.py').read_text()
s=s.replace('ROOT = Path(__file__).resolve().parents[5]','ROOT = Path(__file__).resolve().parents[4]')
s=s.replace("def groups(path):","def groups(path, case='SHEAR_MINUS'):")
s=s.replace("row.get('case_id', 'ZERO') != 'ZERO' or row.get('run_id', 'ZERO') != 'ZERO'","row.get('case_id', case) != case or row.get('run_id', case) != case")
s=s.replace('def join_csv(original, segment, target, boundary):','def join_csv(original, segment, target, boundary, case):').replace('groups(original)','groups(original, case)').replace('groups(segment)','groups(segment, case)')
a=s.index('    binding = json.loads(binding_path.read_text())');b=s.index('    roles = list(FILES)',a)
s=s[:a]+'''    binding = parse_binding(binding_path)
    case = binding['case']
    if case not in CASES or binding['execution_authorized'] != 'true' or binding['start_authorized'] != 'true':
        raise NotReady('HOLD_BINDING_AUTHORITY')
    prefix, segment = Path(binding['predecessor']), Path(binding['output'])
    prior = terminal(prefix / 'RETURN.txt'); end = terminal(segment / 'RETURN.txt')
    if end.get('status') != 'COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' or end.get('result') != 'Ok(())':
        raise NotReady('NOT_READY_CONTINUATION_INCOMPLETE')
    if sha(segment / 'RETURN.txt') != segment_terminal_sha256:
        raise NotReady('HOLD_TERMINAL_IDENTITY')
    for path,key in [(Path(binding['config']),'config_sha256'),(prefix/'config.cfg','config_sha256'),(prefix/'checkpoint.txt','checkpoint_sha256'),(prefix/'RETURN.txt','terminal_sha256'),(Path(binding['decision']),'decision_sha256'),(Path(binding['review']),'review_sha256'),(Path(binding['authority']),'authority_sha256')]:
        if sha(path) != binding[key]: raise NotReady('HOLD_FROZEN_INPUT_IDENTITY:'+key)
    authority = parse_binding(binding['authority'])
    for key,value in binding.items():
        if key not in ('authority','authority_sha256') and authority.get(key) != value:
            raise NotReady('HOLD_AUTHORITY_BINDING:'+key)
    compatibility = json.loads((segment/'source_compatibility.json').read_text())
    verify_epochs(sha(prefix/'source_identity.txt'), sha(segment/'source_identity.txt'), compatibility)
    if (segment/'predecessor_source_identity.txt').read_bytes() != (prefix/'source_identity.txt').read_bytes(): raise NotReady('HOLD_PREDECESSOR_SOURCE')
    for name in ('config.cfg','case_id.txt'):
        if (prefix/name).read_bytes() != (segment/name).read_bytes(): raise NotReady('HOLD_SEGMENT_COMPATIBILITY:'+name)
    if (prefix/'case_id.txt').read_text() != case or (segment/'segment_id.txt').read_text() != binding['segment']:
        raise NotReady('HOLD_CASE_OR_SEGMENT_IDENTITY')
    for key in ('decision_sha256','review_sha256','authority_sha256','checkpoint_sha256','terminal_sha256'):
        if compatibility[key] != binding[key]: raise NotReady('HOLD_COMPATIBILITY_BINDING:'+key)
    if compatibility['binding_sha256'] != sha(binding_path) or compatibility['new_binary_sha256'] != binding['binary_sha256']:
        raise NotReady('HOLD_EXECUTION_BINDING')
    cp = (prefix/'checkpoint.txt').read_text().splitlines()
    segment_cp = (segment/'checkpoint.txt').read_text().splitlines()
    config = terminal(prefix/'config.cfg'); endpoint=1/(1+float(config['end_zbar']))
    if cp[0] != 'AXBI_CHECKPOINT_V2' or segment_cp[0] != 'AXBI_CHECKPOINT_V2' or float(segment_cp[1].split()[0]) != endpoint or float(end['a']) != endpoint:
        raise NotReady('HOLD_CHECKPOINT_SCHEMA_OR_ENDPOINT')
    for data,record in [(cp,prior),(segment_cp,end)]:
        for key,index in [('accepted',0),('attempts',1),('rejections',2),('rhs_evaluations',4),('comparisons',5)]:
            if int(data[2].split()[index]) != int(record[key]): raise NotReady('HOLD_CHECKPOINT_COUNTER:'+key)
        if float(data[1].split()[10]) != float(record['wall_s']): raise NotReady('HOLD_CHECKPOINT_WALL')
    state=list(map(float,cp[1].split()))
    if state[0]!=float(prior['a']): raise NotReady('HOLD_CHECKPOINT_TERMINAL_ALIGNMENT')
    wrapper=compatibility
''' +s[b:]
s=s.replace("for name in ('execution_wrapper_identity.json', 'effective_resource_overrides.json', 'segment_id.txt'):","for name in ('source_compatibility.json', 'predecessor_source_identity.txt', 'effective_resource_overrides.json', 'segment_id.txt'):")
s=s.replace("binding['original_binary_sha256']","compatibility['original_binary_sha256']")
s=s.replace('output / name, state[1])','output / name, state[1], case)')
s=s.replace("groups(prefix / 'history.csv')","groups(prefix / 'history.csv', case)")
s=s.replace("for name in ('config.cfg', 'source_identity.txt', 'case_id.txt'):","for name in ('config.cfg', 'case_id.txt'):")
s=s.replace("shutil.copyfile(segment / 'checkpoint.txt', output / 'checkpoint.txt')","shutil.copyfile(segment / 'checkpoint.txt', output / 'checkpoint.txt')\n        shutil.copyfile(prefix/'source_identity.txt',output/'predecessor_source_identity.txt')\n        shutil.copyfile(segment/'source_identity.txt',output/'source_identity.txt')\n        shutil.copyfile(segment/'source_compatibility.json',output/'source_compatibility.json')")
s=s.replace("case = {'id': 'ZERO', 'clock_origin': reader.CLOCK}","case = {'id': binding['case'], 'clock_origin': reader.CLOCK, 'source_epochs': {'predecessor': OLD, 'current': NEW, 'compatibility': compatibility}}")
s=s.replace("'solver_runs': 0}","'solver_runs': 0, 'source_epochs': {'predecessor': OLD, 'current': NEW}, 'source_compatibility': compatibility}")
pos=s.index('def compose(')
d=json.loads((prep.parent/'SIGNED_CONTINUATION_MECHANISM_DECISION.json').read_text())
extra=f'''CASES = ('SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS')
OLD = '{d['original_compiled_identity_sha256']}'
NEW = '{d['current_compiled_identity_sha256']}'
DECISION = '{hashlib.sha256((prep.parent/'SIGNED_CONTINUATION_MECHANISM_DECISION.json').read_bytes()).hexdigest()}'
REVIEW = '{d['reviewed_input_sha256']['research/axbi_goal_20261014/reviews/AX11_OUTPUT_ALLOCATION_REVIEW.json']}'
def parse_binding(path):
    result={{}}
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith('#'): continue
        key, value=line.split('=',1)
        if key in result or not value: raise NotReady('HOLD_BINDING_DUPLICATE_OR_EMPTY')
        result[key]=value
    return result

def verify_epochs(old, new, c):
    if old != OLD or new != NEW or c.get('old_source_sha256') != OLD or c.get('current_source_sha256') != NEW or c.get('decision_sha256') != DECISION or c.get('review_sha256') != REVIEW or c.get('relation') != 'REVIEWED_RESOURCE_ONLY':
        raise NotReady('HOLD_SOURCE_EPOCH_COMPATIBILITY')

'''
s=s[:pos]+extra+s[pos:]
s=s.replace('Join the frozen ZERO prefix','Join a frozen signed prefix')
(r/'research/axbi_goal_20261014/driver/full/compose_signed_history.py').write_text(s)
