"""Fresh offline additive build and one bounded fixed-export observable execution."""
import argparse, hashlib, json, os, pathlib, resource, shutil, subprocess, time
HERE=pathlib.Path(__file__).resolve().parent
UP=HERE.parent/'vigilode_age_transport_20261019'
IDENTITIES={'model.json':'d5ba5169a291996e31de3d0b8b4c4c6c75081f06e183bee571498eb5d4d3de0d','nodes.csv':'b83f5c07d83d9a6a04ca8120e8fcbe11dab67efb41cbcdd000e4f7eb6a25c17a'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def call(cmd,cwd,env,timeout,name,out=None):
 out=out or HERE/'results'
 start=time.monotonic();r0=resource.getrusage(resource.RUSAGE_CHILDREN)
 try:
  r=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
  stdout,stderr,code=r.stdout,r.stderr,r.returncode
 except subprocess.TimeoutExpired as e:
  stdout=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else (e.stdout or '')
  stderr=(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else (e.stderr or '')
  code=124
 elapsed=time.monotonic()-start;r1=resource.getrusage(resource.RUSAGE_CHILDREN)
 (out/f'{name}.stdout').write_text(stdout);(out/f'{name}.stderr').write_text(stderr)
 receipt={'command':cmd,'cwd':str(cwd),'exit_code':code,'wall_seconds':elapsed,'cpu_seconds':r1.ru_utime+r1.ru_stime-r0.ru_utime-r0.ru_stime,'children_peak_rss_kb_so_far':r1.ru_maxrss,'resource_method':'RUSAGE_CHILDREN deltas for CPU; peak RSS is cumulative wrapper child maximum, not per-command isolated peak','timeout_seconds':timeout}
 (out/f'{name}.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt),flush=True)
 assert code==0,stderr
 return receipt

def prepare_output(out):
 assert not out.exists() or not any(out.iterdir()),'result directory must be absent or empty; choose a fresh --out'
 out.mkdir(parents=True,exist_ok=True)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',type=pathlib.Path,required=True);ap.add_argument('--rust-prefix',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,help='fresh result directory; default RUNTIME/results');a=ap.parse_args()
 a.runtime=a.runtime.resolve();a.rust_prefix=a.rust_prefix.resolve()
 assert not a.runtime.exists(),'fresh runtime required';a.runtime.mkdir(parents=True)
 out=(a.out or a.runtime/'results').resolve();prepare_output(out)
 for name,digest in IDENTITIES.items():assert sha(UP/'inputs'/name)==digest,name
 assert sha(UP/'rust/Cargo.lock')=='a6f430016c83354842b8ba3616aaa87b0c87b762bdd8544eb30ac0bb0a21c056'
 crate=a.runtime/'crate';shutil.copytree(UP/'rust/src',crate/'src');shutil.copytree(UP/'rust/.cargo',crate/'.cargo');(crate/'vendor').symlink_to((UP/'rust/vendor').resolve(),target_is_directory=True)
 shutil.copyfile(UP/'rust/Cargo.lock',crate/'Cargo.lock');shutil.copyfile(UP/'rust/Cargo.toml',crate/'Cargo.toml');(crate/'src/bin').mkdir();shutil.copyfile(HERE/'observable.rs',crate/'src/bin/observable.rs')
 shutil.copyfile(HERE/'fixture_parity.rs',crate/'src/bin/fixture_parity.rs')
 with (crate/'src/bin/observable.rs').open('a') as f:f.write('\n#[cfg(test)] include!("fixture_parity.rs");\n')
 env=dict(os.environ,PATH=str(a.rust_prefix/'bin')+os.pathsep+os.environ['PATH'],CARGO_HOME=str(a.runtime/'cargo_home'),CARGO_TARGET_DIR=str(a.runtime/'target'),RAYON_NUM_THREADS='2')
 cargo=str(a.rust_prefix/'bin/cargo');versions={tool:subprocess.check_output([str(a.rust_prefix/'bin'/tool),'--version'],text=True).strip() for tool in ['rustc','cargo']}
 build=call([cargo,'build','--release','--offline','--locked','--bin','observable','-j','2'],crate,env,240,'BUILD',out)
 tests=call([cargo,'test','--release','--offline','--locked','--bin','observable','-j','2'],crate,env,120,'FIXTURE_TESTS',out)
 binary=a.runtime/'target/release/observable';run=call([str(binary),str(UP/'inputs'),str(out/'STUDY.json')],crate,env,120,'RUN',out)
 receipt={'base_pr199_head':'cf00684741eb612e35f987713c28937513d44d57','versions':versions,'binary_sha256':sha(binary),'source_sha256':sha(HERE/'observable.rs'),'fixture_source_sha256':sha(HERE/'fixture_parity.rs'),'inputs':IDENTITIES,'lock_sha256':sha(UP/'rust/Cargo.lock'),'build':build,'fixtures':tests,'analysis_wall_consumed_seconds':run['wall_seconds'],'analysis_cumulative_cap_seconds':240,'run':run,'execution_identity':{'requested_role':'lower-tier coding executor per controller task','observed_runtime_model':'not independently observed'},'PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED'}
 (out/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
