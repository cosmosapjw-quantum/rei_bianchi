from pathlib import Path
import json,hashlib,subprocess,shutil,time,os
R=Path.cwd();P=R/'.cuh/fastest-track/REI-F08-PAIRED';C=P/'conservative-candidate';crate=R/'rust/rei_microphysics'
# Canonical packaging waits for every source-bound original producer to close.
for l in ['S2_BI','A0_BI','A2_FLRW','A2_BI']:
 x=json.loads((P/(l+'-production-receipt.json')).read_text());assert x['exit_code']==0,l
for l in ['T2_FLRW','T2_BI']:
 x=json.loads((P/(l+'-producer-resume-execution.json')).read_text());assert x['exit_code']==0,l
old=(crate/'src/coupled_primary.rs').read_bytes();candidate=(C/'coupled_primary.rs').read_bytes();assert candidate.startswith(old)
(crate/'src/coupled_primary.rs').write_bytes(candidate);shutil.copyfile(C/'paired_runtime.rs',crate/'src/paired_runtime.rs')
s=(C/'paired_history.rs').read_text();s=s.replace('#[path="coupled_primary.rs"] pub mod coupled_primary;\n','').replace('use crate::coupled_primary::','use rei_microphysics::coupled_primary::').replace('#[path="paired_runtime.rs"]','#[path="../src/paired_runtime.rs"]')
s=s.replace('include_str!("paired_runtime.rs")','include_str!("../src/paired_runtime.rs")').replace('include_str!("coupled_primary.rs")','include_str!("../src/coupled_primary.rs")')
s=s.replace('include_str!("'+str(R/'configs/rei_fastest_v1/science_scenario_v1.json')+'")','include_str!("../../../configs/rei_fastest_v1/science_scenario_v1.json")')
frozen=(P/'frozen-inputs.json').read_text();assert '"########' not in frozen
s=s.replace('include_str!("'+str(P/'frozen-inputs.json')+'")','r########"'+frozen+'"########')
s=s.replace(str(crate/'src')+'/','../src/')
probe=(P/'energy_comp_recovery_probe.rs').read_text();s+='\n'+probe[probe.index('#[cfg(test)] mod compensation_recovery_test'):]
(crate/'examples/paired_history.rs').write_text(s)
commands=[]
def run(argv,log):
 t=time.monotonic()
 with (P/log).open('wb') as f:p=subprocess.run(['cuhg-telemetry','run','--project',str(R),'--task','REI-F08','--',*argv],cwd=R,env={**os.environ,'CUHG_EXECUTION_MODE':'CODEX_ONLY'},stdout=f,stderr=subprocess.STDOUT)
 commands.append({'argv':argv,'exit_code':p.returncode,'wall_s':time.monotonic()-t,'log':log});assert p.returncode==0,log
run(['cargo','test','--release','--manifest-path',str(crate/'Cargo.toml'),'--lib','--example','paired_history'],'packaging-cargo-tests.log')
run(['cargo','test','--release','--manifest-path',str(crate/'Cargo.toml'),'--tests'],'packaging-integration-tests.log')
run(['cargo','build','--release','--manifest-path',str(crate/'Cargo.toml'),'--example','paired_history'],'packaging-build.log')
lib=max((crate/'target/release/deps').glob('librei_microphysics-*.rlib'),key=lambda p:p.stat().st_mtime)
run(['rustc','--test','--edition','2021','-O',str(P/'native_tests_v2.rs'),'--extern','rei_microphysics='+str(lib),'-L','dependency='+str(crate/'target/release/deps'),'-o',str(P/'packaging-api-tests')],'packaging-api-build.log')
run([str(P/'packaging-api-tests')],'packaging-api-tests.log')
run([str(crate/'target/release/examples/paired_history'),'--scenario',str(R/'configs/rei_fastest_v1/science_scenario_v1.json'),'--output',str(P/'canonical-packaging-pilot'),'--pilot','--only','T2_BI'],'packaging-pilot.log')
run(['sage','-python',str(P/'checker_v5/check_history.py'),str(P/'canonical-packaging-pilot/T2_BI')],'packaging-pilot-independent.log')
result={'task':'REI-F08','status':'PASS','scope':'Canonical source packaging of executed conservative variant; namespace/include paths plus exact frozen input literal; recovery/API/crate and three independent composite pilot trials','commands':commands,'source_files':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [crate/'src/coupled_primary.rs',crate/'src/paired_runtime.rs',crate/'examples/paired_history.rs']},'original_coupled_map_exact_prefix':True,'whole_completed_axes_replayed':False,'whole_campaign_variant_sources_retained':True,'final_source_independently_rereviewed':False,'scientific_admission':'HOLD'};(P/'packaging-qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
