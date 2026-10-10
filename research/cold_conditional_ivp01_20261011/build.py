import pathlib,hashlib,json,subprocess,time,tempfile
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parents[1];E=P/'evidence';E.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
c=json.loads((P/'CONTRACT.json').read_text());assert git('rev-parse','HEAD')==c['base_commit'];assert git('rev-parse','HEAD^{tree}')==c['base_tree']
paths={'baseline':'research/rec_rei_cold_intake01_20261011/inputs/baseline.json','refined':'research/rec_rei_cold_intake01_20261011/inputs/refined.json','REC_CONTRACT':'research/rec_rei_cold_intake01_20261011/inputs/REC_CONTRACT.json','history.c':'research/cold_compton_component01_20261011/source/history.c','composition':'rust/rei_microphysics/src/cold_stage_composition.rs','HG97_PDF':'research/cold_hii_rr_component01_20261011/source/HG97_astro-ph_9612232v1.pdf','RR':'rust/rei_microphysics/src/cold_hii_rr.rs','Compton':'rust/rei_microphysics/src/cold_compton.rs','axisym':'rust/rei_microphysics/src/axisym_coupling.rs'}
for k,p in paths.items():
 data=subprocess.check_output(['git','show',c['base_commit']+':'+p],cwd=ROOT) if k=='composition' else (ROOT/p).read_bytes()
 assert hashlib.sha256(data).hexdigest()==c['source_sha256'][k],k
subprocess.run(['cargo','generate-lockfile','--offline','--manifest-path',str(P/'native/Cargo.toml')],cwd=ROOT,check=True)
allowed=['rust/rei_microphysics/src/cold_conditional_ivp.rs','rust/rei_microphysics/src/lib.rs','rust/rei_microphysics/src/cold_stage_composition.rs',str(P.relative_to(ROOT))]
subprocess.run(['git','add','--',*allowed],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').splitlines();subprocess.run(['git','commit','-m','Pin source for bounded cold conditional FLRW IVP01'],cwd=ROOT,check=True)
commit=git('rev-parse','HEAD');tree=git('rev-parse','HEAD^{tree}');sourcefiles=git('ls-files','rust/rei_microphysics',str(P.relative_to(ROOT))).splitlines();sources={p:sha(ROOT/p) for p in sourcefiles if '/evidence/' not in p}
target=pathlib.Path(tempfile.mkdtemp(prefix='rei-cold-ivp-build-'));start=time.monotonic()
with (E/'FIRST_BUILD.stdout').open('w') as out,(E/'FIRST_BUILD.stderr').open('w') as err:
 p=subprocess.run(['cargo','build','--offline','--locked','--release','--manifest-path',str(P/'native/Cargo.toml'),'--target-dir',str(target)],cwd=ROOT,stdout=out,stderr=err,timeout=300)
binary=target/'release/cold_conditional_ivp01';receipt={'returncode':p.returncode,'elapsed_s':time.monotonic()-start,'build_attempts':1,'base_commit':c['base_commit'],'base_tree':c['base_tree'],'source_commit':commit,'source_tree':tree,'staged_paths':staged,'sources':sources,'target':str(target),'binary':str(binary),'binary_sha256':sha(binary) if binary.exists() else None}
(E/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');assert p.returncode==0,'BUILD_FAILURE'
