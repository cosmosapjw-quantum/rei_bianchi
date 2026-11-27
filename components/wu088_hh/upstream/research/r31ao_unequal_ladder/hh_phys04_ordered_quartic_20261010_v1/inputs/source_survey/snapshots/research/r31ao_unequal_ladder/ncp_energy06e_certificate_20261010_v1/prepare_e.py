from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).parent; C=Path('/root/WU088_HH_ENERGY06C_20261009'); P=W/'repo/research/r31ao_unequal_ladder/ncp_energy06e_certificate_20261010_v1'; R=W/'run'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,x):(R/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((C/'run/FINAL_SOURCE_BINDING_V4.json').read_text()); orig=C/'sealed/WU088_HH_ENERGY06C_NCP_RETURN_20261009_v1/original_owner_dependency'
checks=[]
for n,h in b['original_owner_sources'].items():
 p=orig/'src'/n; assert sha(p)==h;checks.append({'path':str(p),'sha256':h,'bytes':p.stat().st_size})
for n,h in b['candidate_sources'].items():
 p=C/'repo/research/r31ao_unequal_ladder/ncp_energy06c_owner_birth_20261009_v1'/n;assert sha(p)==h;checks.append({'path':str(p),'sha256':h,'bytes':p.stat().st_size})
for x in json.loads((C/'run/PRESERVATION_BEFORE.json').read_text())['files']:
 p=Path(x['path']);assert sha(p)==x['sha256'];checks.append(x)
for n,x in json.loads((C/'run/CHECKPOINT_STATUS.json').read_text())['members'].items():
 p=Path(x['source']);assert sha(p)==x['sha256'];checks.append({'path':str(p),**x})
for p in sorted((C/'run').glob('*')):
 if p.is_file():checks.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
put('INVENTORY_BEFORE.json',{'files':checks,'historical_tests':{'owner':26,'C1':8},'historical_science_reruns':0})
shutil.copytree(orig,W/'original_owner_dependency')
shutil.copytree(C/'c1',W/'c1')
shutil.copytree(W/'inputs',P/'inputs')
shutil.copyfile(C/'run/FINAL_SOURCE_BINDING_V4.json',P/'FINAL_SOURCE_BINDING_V4.json')
for n in ['owner_birth.rs','owner_tests.rs']:shutil.copyfile(C/'repo/research/r31ao_unequal_ladder/ncp_energy06c_owner_birth_20261009_v1/src'/n,P/'src'/n)
# Generated compatibility wrapper bytes are preserved; path relocation is explicit.
G=W/'cargo';G.mkdir()
for n in ['owner_runtime.rs','hh_paired_compat.rs']:
 s=(C/'cargo'/n).read_text();s=s.replace('/root/WU088_HH_MASTER_EXEC_20261008/inputs/on06g/HH_ON06G_20261008_v1/worktree/rust/rei_microphysics',str(W/'original_owner_dependency')).replace(str(C/'cargo'),str(G)).replace(str(C/'repo/research/r31ao_unequal_ladder/ncp_energy06c_owner_birth_20261009_v1/src'),str(P/'src'))
 (G/n).write_text(s)
with (G/'owner_runtime.rs').open('a') as f:f.write('\ninclude!("'+str(P/'src/paired_stage_receipt.rs')+'");\n')
(G/'Cargo.toml').write_text('[package]\nname="hh_energy06e_contract"\nversion="0.1.0"\nedition="2021"\npublish=false\n[workspace]\n[dependencies]\nrei_microphysics={path="'+str(W/'original_owner_dependency')+'"}\n[[bin]]\nname="receipt_contract"\npath="'+str(P/'src/main.rs')+'"\n')
(P/'src/main.rs').write_text('pub use rei_microphysics::*;\n#[path="'+str(G/'owner_runtime.rs')+'"] mod owner;\nfn main(){eprintln!("ENERGY06E_SCIENCE_DISPATCH_BLOCKED certificate=OPEN authorization=null");std::process::exit(77)}\n')
put('DESIGN_AND_DAG.json',{'scope':'typed native predecessor receipt + contract tests + exact algebra + source-bound proof proposal','order':['source inventory','receipt contracts','bounded verification','premise and live identity','return and dual backup'],'original_sources_preserved':True,'new_science_dispatch':0,'production_promotion':False})
