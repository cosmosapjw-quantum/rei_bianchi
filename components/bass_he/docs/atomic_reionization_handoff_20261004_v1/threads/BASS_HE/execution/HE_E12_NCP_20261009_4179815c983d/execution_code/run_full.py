import pathlib,json,hashlib,sys
from execute import run,write
R=pathlib.Path(__file__).parent
S=R/'shadow';C=S/'research/transport_20261007/short-hhe-midpoint'
identity=json.loads((R/'SOURCE_IDENTITY.json').read_text())
def check_identity():
 for name,sha in identity['base_shadow_files_sha256'].items():
  assert hashlib.sha256((S/name).read_bytes()).hexdigest()==sha,name
 assert hashlib.sha256((C/'examples/e11_native_telemetry.rs').read_bytes()).hexdigest()==identity['telemetry_sha256']
 assert hashlib.sha256((C/'target/release/examples/e11_native_telemetry').read_bytes()).hexdigest()==identity['binary_sha256']
 for name,d in identity['compiler'].items():assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()==d['sha256']
check_identity();(R/'full').mkdir(exist_ok=False)
for mode in ('OFF','KF','GM'):
 check_identity()
 code=run('FULL_'+mode,['/usr/bin/time','-v',str(C/'target/release/examples/e11_native_telemetry'),str(C/'e9_common_domain.cfg'),mode,str(R/'full'/mode),'384','--authorized-full'],C)
 if code:sys.exit(code)
 check_identity()
write('POST_FULL_SOURCE_IDENTITY.json',{'all_base_source_compiler_binary_hashes':'PASS','mode_boundaries':'before and after each mode','scientific_changes':0})
sys.exit(run('VERIFY_FULL', ['python3',str(R/'verify_run.py'),'full'],R))
