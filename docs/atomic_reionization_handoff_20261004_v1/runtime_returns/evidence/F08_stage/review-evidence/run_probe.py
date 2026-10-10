from pathlib import Path
import subprocess,hashlib,json,struct
from fractions import Fraction
p=Path(__file__).parent
root=Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi')
lib=root/'rust/rei_microphysics/target/release/deps/librei_microphysics-2db3552c92b16edc.rlib'
identity={'task_id':'REI-F08','run_id':'REI-F08-STAGE-REVIEW-20261005','launch_id':'cl_9081a324967384377e167e21f551af99','head_from_parent':'b553698a114fbff05640ab6ecb95d260410de492','files':{}}
for f in [p/'probe.rs',Path(__file__),lib,root/'rust/rei_microphysics/src/coupled_primary.rs',root/'.cuh/fastest-track/REI-F08-STAGE/review-scope.json']:
 identity['files'][str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
argv=['rustc','--edition','2021','-O',str(p/'probe.rs'),'--extern','rei_microphysics='+str(lib),'-L','dependency='+str(lib.parent),'-o',str(p/'probe')]
identity['argv']=[argv,[str(p/'probe')]]
(p/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
build=subprocess.run(argv,cwd=root,capture_output=True,text=True)
(p/'build.stdout').write_text(build.stdout);(p/'build.stderr').write_text(build.stderr)
print('build_returncode',build.returncode);build.check_returncode()
r=subprocess.run([str(p/'probe')],cwd=root,capture_output=True,text=True)
(p/'probe.stdout').write_text(r.stdout);(p/'probe.stderr').write_text(r.stderr)
print(r.stdout,end='');print(r.stderr,end='');print('probe_returncode',r.returncode)
f=json.loads((root/'.cuh/fastest-track/REI-F08-STAGE/fixture.json').read_text());m=json.loads((root/'runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text())
bits=lambda s:struct.unpack('>d',bytes.fromhex(s))[0]
nh,nhe=map(bits,m['actual_center_and_model_bits']['constants_bits'][:2])
fhe=Fraction(nhe)/Fraction(nh);sf=Fraction(f['stage']['f_he'])
c=bits(m['actual_center_and_model_bits']['constants_bits'][2]);cn_exact=Fraction(c)*Fraction(f['stage']['n_h_cm3']);cn_native=Fraction(c*f['stage']['n_h_cm3'])
audit={'host_fhe_minus_stage_fhe_exact':str(fhe-sf),'host_fhe_minus_stage_fhe_float':float(fhe-sf),'native_cn_minus_exact_cn':str(cn_native-cn_exact),'new_nhe_bits':struct.pack('>d',f['stage']['n_h_cm3']*f['stage']['f_he']).hex(),'manifest_nhe_bits':m['actual_center_and_model_bits']['constants_bits'][1]}
(p/'binding-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
r.check_returncode()
