#!/usr/bin/env python3
"""Check clean rerun in a fresh tempdir against SHA256 frozen generated science outputs."""
import sys,subprocess,shutil,tempfile,hashlib,json,os,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parent
expected=['R41_FIRST_V0_MECHANISM_SUMMARY_3500.csv','R41_FIRST_V0_TERMINAL_BRANCHES_126000.csv',
 'R41_SOURCE_CONTRAST_1750.csv','R41_PHOTON_LINE_EVENTS_4704.csv','R41_HALF_RADIATIVE_DENSITY_700.csv',
 'R41_HALF_DENSITY_SOURCE_CONTRAST_350.csv','R41_19LEVEL_RADIATIVE_LINES_63.csv','R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv',
 'R41_OUTSIDE_RADIATIVE_ESCAPE_LINES_124.csv','SUMMARY.json']
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline={n:{'sha256':h(ROOT/'results'/n),'size':(ROOT/'results'/n).stat().st_size} for n in expected}
(ROOT/'verification/OUTPUT_SHA256.json').write_text(json.dumps(baseline,indent=2,sort_keys=True)+'\n')
with tempfile.TemporaryDirectory(prefix='wu_r41_source_clean_') as t:
 t=Path(t)
 for p in ['generate.py','plot_physics.py','plot_external.py','test_science.py']:
  shutil.copy2(ROOT/p,t/p)
 shutil.copytree(ROOT/'source_private',t/'source_private')
 (t/'verification').mkdir()
 runs={}
 for key,cmd in [
  ('generate',[sys.executable,'generate.py']),
  ('test_normal',[sys.executable,'-m','unittest','test_science']),
  ('test_optimized',[sys.executable,'-O','-m','unittest','test_science']),
  ('plots',[sys.executable,'plot_physics.py']),
  ('plots_external',[sys.executable,'plot_external.py'])]:
  z=subprocess.run(cmd,cwd=t,text=True,capture_output=True,timeout=120)
  runs[key]={'command':cmd,'exit':z.returncode,'stdout_tail':z.stdout[-700:],'stderr_tail':z.stderr[-700:]}
  if z.returncode:raise RuntimeError(f'clean {key} failed {runs[key]}')
 observed={n:{'sha256':h(t/'results'/n),'size':(t/'results'/n).stat().st_size} for n in expected}
 identical={n:baseline[n]==observed[n] for n in expected}
 summary={'clean_replay':'PASS' if all(identical.values()) else 'FAIL','files_byte_identical':sum(identical.values()),'files_expected':len(expected),
     'source_only_no_parent_external_zip_required':True,'runs':runs,'output_identity':identical,
     'python':platform.python_version(),
     'numpy':__import__('numpy').__version__,'scipy':__import__('scipy').__version__}
 (ROOT/'verification/CLEAN_REPLAY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
 if not all(identical.values()):raise AssertionError('clean science output hash mismatch: '+str(identical))
 print(json.dumps({'result':'PASS','regenerated_byte_exact':len(expected),'normal':runs['test_normal']['exit'],'opt':runs['test_optimized']['exit'],'source_lanes':'authenticated original'},indent=2))
