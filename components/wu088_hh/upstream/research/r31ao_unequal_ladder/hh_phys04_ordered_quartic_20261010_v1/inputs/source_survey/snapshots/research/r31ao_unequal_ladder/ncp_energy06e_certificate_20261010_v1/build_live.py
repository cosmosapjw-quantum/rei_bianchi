from pathlib import Path
import subprocess,json,hashlib
W=Path(__file__).parent;R=W/'run';src=W/'c1/source/wide_domain_20261001_v1/log_native_driver/primitive_worker.cpp'
s=src.read_text();s=s.replace('int main(int argc,char **argv) {','int main(int argc,char **argv) {\n if(argc==2 && std::string(argv[1])=="--identity-live") {\n  std::cout << "ENERGY06E_C1_IDENTITY_ONLY precision=128 radius=2^-57 science_dispatch=0" << std::endl;\n  std::string release; std::getline(std::cin,release); return release=="RELEASE_IDENTITY_ONLY"?0:77;\n }')
src.write_text(s)
lines=[json.loads(l) for l in Path('/root/WU088_HH_ENERGY06C_20261009/c1/COMMANDS.jsonl').read_text().splitlines()]
a=[x for x in lines if x['label']=='build' and x['exit_code']==0][-1]['argv'];a=[v.replace('/root/WU088_HH_ENERGY06C_20261009',str(W)) for v in a];a[-1]=str(W/'c1/energy06e_c1_identity_candidate')
r=subprocess.run(a,capture_output=True);(R/'C1_BUILD.stdout').write_bytes(r.stdout);(R/'C1_BUILD.stderr').write_bytes(r.stderr)
(R/'C1_BUILD.json').write_text(json.dumps({'argv':a,'exit':r.returncode,'compiler_sha256':hashlib.sha256(Path(a[0]).read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'promotion':False},indent=2)+'\n');raise SystemExit(r.returncode)
