#!/usr/bin/env python3
"""Isolated original-source replay and deterministic output identity verification."""
from pathlib import Path
import subprocess,tempfile,shutil,hashlib,json,sys,platform
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results';VER=ROOT/'verification';VER.mkdir(exist_ok=True)
science=['R43_CASES_324.csv','R43_POPULATIONS_16848.csv','R43_SIGNED_PHOTONS_119232.csv','R43_GRACKLE_REFERENCE_15.csv','SUMMARY.json']
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base={n:{'bytes':(OUT/n).stat().st_size,'sha256':H(OUT/n)} for n in science}
(VER/'OUTPUT_SHA256.json').write_text(json.dumps(base,indent=2,sort_keys=True)+'\n')
with tempfile.TemporaryDirectory(prefix='wu_r43_restore_clean_') as v:
 t=Path(v)
 for n in ['generate.py','test_science.py','plot_science.py']:shutil.copy2(ROOT/n,t/n)
 shutil.copytree(ROOT/'source_private',t/'source_private')
 runs={}
 for name,cmd in [('generate',[sys.executable,'generate.py']),('normal',[sys.executable,'-m','unittest','test_science','-q']),('opt',[sys.executable,'-O','-m','unittest','test_science','-q']),('plots',[sys.executable,'plot_science.py'])]:
  p=subprocess.run(cmd,cwd=t,capture_output=True,text=True,timeout=150,env={**__import__('os').environ,'OPENBLAS_NUM_THREADS':'1'})
  runs[name]={'command':cmd,'exit_code':p.returncode,'stdout_tail':p.stdout[-900:],'stderr_tail':p.stderr[-900:]}
  if p.returncode:raise RuntimeError(f'{name} failed: {runs[name]}')
 verify={n:(OUT/n).stat().st_size==(t/'results'/n).stat().st_size and H(OUT/n)==H(t/'results'/n) for n in science}
 result={'clean_replay':'PASS' if all(verify.values()) else 'FAIL','bytes_equal':sum(verify.values()),'expected':len(science),'files':verify,'runs':runs,'python_version':platform.python_version(),'numpy_version':__import__('numpy').__version__,'scipy_version':__import__('scipy').__version__}
 (VER/'CLEAN_REPLAY.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 if not all(verify.values()):raise AssertionError(result)
 print(json.dumps({'clean_replay':result['clean_replay'],'identical_outputs':len(science),'normal':runs['normal']['stderr_tail'],'opt':runs['opt']['stderr_tail'],'plots':runs['plots']['stdout_tail']},indent=2))
