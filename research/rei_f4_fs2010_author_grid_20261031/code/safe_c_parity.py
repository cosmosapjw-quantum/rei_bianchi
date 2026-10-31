#!/usr/bin/env python3
"""Bounded-label buffer repair solely for C/Python scientific interpolation parity."""
from pathlib import Path
import os,ctypes,tempfile,subprocess,json
import numpy as np
from compute import ROOT,FS2010
SRC=(ROOT/'source_tar'/'elec_interp.c').read_text()
assert SRC.count('char label[] = " ";')==1
assert SRC.count('fscanf(input_file,"%s", label);')==2
FS=FS2010(); gen=np.random.default_rng(7001)
with tempfile.TemporaryDirectory(prefix='fs2010_c_parity_') as p:
 path=Path(p)
 copied=SRC.replace('char label[] = " ";','char label[64] = {0};').replace('fscanf(input_file,"%s", label);','fscanf(input_file,"%63s", label);')
 (path/'elec_interp_safe.c').write_text(copied)
 so=path/'libelec_safe.so'
 cmd=['gcc','-O2','-shared','-fPIC','-Wall','-Wextra', '-I',str(ROOT/'source_tar'),'-o',str(so),str(path/'elec_interp_safe.c'),'-lm']
 c=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if c.returncode: raise RuntimeError(f'SAFE_C_COMPILATION_FAILED: {c.stderr}')
 lib=ctypes.CDLL(str(so)); wd=os.getcwd()
 try:
  os.chdir(ROOT/'source_tar');lib.initialize_interp_arrays()
 finally:os.chdir(wd)
 diffs={}; seed=7001
 for key,j in [('interp_fheat',1),('interp_n_Lya',3),('interp_nion_HI',4),('interp_nion_HeI',5),('interp_nion_HeII',6)]:
  fun=getattr(lib,key);fun.argtypes=[ctypes.c_float,ctypes.c_float];fun.restype=ctypes.c_float
  ds=[]
  for i in range(200):
   e=float(gen.uniform(10.2,1000));x=float(gen.uniform(0.0002,0.997))
   cval=float(fun(e,x));pyval=float(FS.interp(e,x)[j]);ds.append(abs(cval-pyval)/max(1.0,abs(pyval)))
  diffs[key]=max(ds)
 assert max(diffs.values())<4e-7,diffs
 out={'reference':'author elec_interp.c only label buffer repair, scientific code otherwise unchanged',
      'compiler_cmd':cmd,'exit_code':c.returncode,'points_per_method':200,
      'test_seed':seed,'max_normalized_error_by_method':diffs,'worst_normalized_error':max(diffs.values()),
      'pass_limit':4e-7,'status':'PASS'}
 (ROOT/'evidence'/'SAFE_C_PARITY.json').write_text(json.dumps(out,indent=2)+'\n')
 print('SAFE_C_PARITY 5x200 PASS; max_normalized_error='+str(max(diffs.values())))
