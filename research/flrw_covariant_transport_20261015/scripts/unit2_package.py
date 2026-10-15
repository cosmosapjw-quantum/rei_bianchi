#!/usr/bin/env python3
"""Prepare an explicit safe publication list; build only after document freeze."""
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SCOPE=Path('research/flrw_covariant_transport_20261015')
TASK=ROOT/SCOPE
MANIFEST=TASK/'UNIT2_SELECTION.json'
PATHLIST=TASK/'GITHUB_UNIT2_PATHS.txt'
ALLOWED={'.rs','.py','.md','.json','.jsonl','.cfg','.txt','.log','.diff','.wl','.toml','.lock','.csv','.png','.svg','.pdf'}
GENERATED={str(SCOPE/'UNIT2_SELECTION.json'),str(SCOPE/'GITHUB_UNIT2_PATHS.txt'),str(SCOPE/'UNIT2_PACKAGE_RECEIPT.json')}
def sha(data):return hashlib.sha256(data).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def excluded(path):
 text=str(path)
 if text in GENERATED:return 'generated manifest/list/receipt handled separately'
 if text.startswith(str(SCOPE/'raw/q128_attempt1')+'/'):return 'full first raw run retained in separate archive'
 rel=path.relative_to(SCOPE) if str(path).startswith(str(SCOPE)+'/') else None
 if rel and len(rel.parts)>2 and rel.parts[0]=='raw' and rel.parts[1] not in {'q128_attempt1_terminal_compact','q128_step_diagnostic_001','q128_partition_diagnostic_001'}:return 'nested raw directory outside explicit compact-evidence allowlist'
 if 'target' in path.parts or '__pycache__' in path.parts:return 'build/cache excluded'
 if path.suffix not in ALLOWED:return 'archive/binary/non-allowlisted type excluded'
 if (ROOT/path).stat().st_size>4*1024**2:return 'large per-file payload excluded from compact publication'
 return None
def row(path):
 data=(ROOT/path).read_bytes();return {'path':str(path),'bytes':len(data),'sha256':sha(data)}
def prepare():
 changed=subprocess.check_output(['git','diff','--name-only','--diff-filter=AM'],cwd=ROOT,text=True).splitlines()
 other=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
 safe_code={'rust/rei_microphysics/src/axbi_driver.rs','rust/rei_microphysics/src/axbi_covariant_transport.rs','rust/rei_microphysics/tests/axbi_covariant_driver.rs','rust/rei_microphysics/tests/axbi_covariant_partition.rs','rust/rei_microphysics/tests/axbi_inactive_driver.rs','rust/rei_microphysics/examples/axbi_covariant_step_diagnostic.rs','rust/rei_microphysics/examples/axbi_covariant_partition_diagnostic.rs'}
 candidates={Path(s) for s in changed+other if s in safe_code or s.startswith(str(SCOPE)+'/')}
 publish=[];omitted=[]
 for path in sorted(candidates):
  if not (ROOT/path).is_file():continue
  why=excluded(path)
  if why:omitted.append({'path':str(path),'reason':why})
  else:publish.append(path)
 # A runnable crate uses all library modules and exact compile-time input
 # dependencies, not merely the changed files sent to the GitHub tree API.
 crate=Path('rust/rei_microphysics')
 bundle={p.relative_to(ROOT) for p in (ROOT/crate/'src').rglob('*.rs')}
 bundle.update({Path('AGENTS.md'),Path('CLAUDE.md')})
 bundle.update({crate/'Cargo.toml',crate/'Cargo.lock',crate/'examples/axbi_reionization.rs',crate/'examples/eval_fixture.rs'})
 for name in ['axbi_covariant_transport','axbi_covariant_driver','axbi_covariant_partition','axbi_inactive_driver','deuterium_atomic','deuterium_charge_exchange']:
  f=crate/'tests'/f'{name}.rs'
  if (ROOT/f).exists():bundle.add(f)
 driver=ROOT/crate/'src/axbi_driver.rs';section=driver.read_text().split('pub fn compiled_identity() -> String {',1)[1].split('fn ledger_values',1)[0]
 for rel in re.findall(r'include_str!\(\s*"([^"]+)"',section):bundle.add((driver.parent/rel).resolve().relative_to(ROOT))
 # Retain all compact current task docs/scripts/configs/evidence, including
 # already published compact receipts referenced by the updated handoff.
 for f in TASK.rglob('*'):
  if f.is_file() and excluded(f.relative_to(ROOT)) is None:bundle.add(f.relative_to(ROOT))
 bundle.update(publish)
 result={'schema':'rei.covariant.unit2_selection.v1','status':'DRAFT_REFRESH_AFTER_DOC_FREEZE_BEFORE_BUILD','git_baseline_observed':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'selection_scope':'Unit2 changed code/docs plus compact evidence only; source runnable ZIP additionally includes full Rust library and compile-time dependencies','git_publish_files':[row(p) for p in publish],'git_publish_metadata_extra':[str(SCOPE/'UNIT2_SELECTION.json'),str(SCOPE/'GITHUB_UNIT2_PATHS.txt')],'zip_files':[row(p) for p in sorted(bundle)],'zip_metadata_extra':[str(SCOPE/'UNIT2_SELECTION.json'),str(SCOPE/'GITHUB_UNIT2_PATHS.txt')],'excluded_candidates':omitted,'exclusion_policy':['raw/q128_attempt1/** full189MB excluded; terminal_compact included','target/** and __pycache__/** excluded','archives/binaries excluded; small archive identity receipts retained','max4MiB per compact-publication file'],'zip_uncompressed_bytes':sum((ROOT/p).stat().st_size for p in bundle),'zip_runnable_entry':'README_KO.md','zip_root_readme_source':str(SCOPE/'UNIT2_RUN_KO.md'),'final_archive_built':False,'source_mutations':0,'git_mutations':0,'uploads':0}
 write(MANIFEST,result)
 paths=sorted({str(p) for p in publish}|set(result['git_publish_metadata_extra']))
 PATHLIST.write_text('\n'.join(paths)+'\n')
 print(json.dumps({'manifest':str(MANIFEST),'github_pathlist':str(PATHLIST),'git_publish_files':len(paths),'zip_files':len(bundle)+3,'zip_uncompressed_bytes':result['zip_uncompressed_bytes'],'final_archive_built':False}))
def build(output):
 if output.exists():raise RuntimeError('Fresh destination required; no overwrite')
 data=json.loads(MANIFEST.read_text());entries={}
 for item in data['zip_files']:
  payload=(ROOT/item['path']).read_bytes()
  if len(payload)!=item['bytes'] or sha(payload)!=item['sha256']:raise RuntimeError(f"Packaging input changed since prepare: {item['path']}; refresh prepare after document freeze")
  entries[item['path']]=payload
 for name in data['zip_metadata_extra']:entries[name]=(ROOT/name).read_bytes()
 entries['README_KO.md']=(ROOT/data['zip_root_readme_source']).read_bytes()
 output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,payload in sorted(entries.items()):
   info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,payload,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(output) as z:
  if z.testzip() is not None:raise RuntimeError('ZIP CRC mismatch')
  for name,payload in entries.items():
   if sha(z.read(name))!=sha(payload):raise RuntimeError(f'Member hash mismatch: {name}')
 result={'schema':'rei.covariant.unit2_package_receipt.v1','archive_path':str(output),'archive_bytes':output.stat().st_size,'archive_sha256':sha(output.read_bytes()),'members':len(entries),'uncompressed_bytes':sum(map(len,entries.values())),'selection_manifest_sha256':sha(MANIFEST.read_bytes()),'member_crc_and_sha_readback':'PASS','numerical_runs':0,'build_cache_included':False,'git_mutations':0,'uploads':0}
 write(TASK/'UNIT2_PACKAGE_RECEIPT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','build']);p.add_argument('--output',type=Path,default=ROOT.parents[1]/'REI_FLRW_COVARIANT_UNIT2_20261015.zip');a=p.parse_args();prepare() if a.action=='prepare' else build(a.output.resolve())
