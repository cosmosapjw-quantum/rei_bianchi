#!/usr/bin/env python3
"""Stage the source-matched HE18 C3 runtime from immutable archives.

Creates a NEW private runtime directory; source and only required data are copied.
Never writes private P01/AXBI original inputs into the Git checkout. Only two
archived warm P01 RHS evaluations are used to freeze second-cell endpoint slopes.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ARCHIVES={
 'c1':'fedc88bf43812b3cf2ea0ae227c3e1ed0a94a1e284e3a71452290dc3372497f0',
 'r5':'2f29435ea39adb4aa136075a201a2904767798b4ef2a966bae452a134462ae08',
 'r8':'b58f6e26ffdd4688efe32758bcee67b95c91786d1ec36c1d4eb8a4cdbe3f9ab9'}
INPUT_SHA={'P01_STATE.npz':'3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be',
 'emissivity.out':'88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
 'ENDPOINT_MEMORY_R7.json':'aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39',
 'FIXED_REFERENCE.npz':'3572256db4cc17f45f76cf9bcb14434c158066ddcf54d93db26279d688f4b26e',
 'ADOPTION_RESULT_R8.json':'3a57883e0640f7e7b7be29dfd0c3adabc168533e91e77bd2027c2ff91a6e0173'}
SOURCE_SHA='8c434debdcb66ee499d61f7822980c73c75469bd426839a1597687042b8c78f3'
def sha(b):return hashlib.sha256(b).hexdigest()
def stage(c1,r5,r8,destination):
 c1,r5,r8,dst=map(Path,(c1,r5,r8,destination))
 if dst.exists():raise ValueError('REFUSE_EXISTING_PRIVATE_RUNTIME')
 for key,path in [('c1',c1),('r5',r5),('r8',r8)]:
  if sha(path.read_bytes())!=ARCHIVES[key]:raise ValueError('ARCHIVE_IDENTITY_MISMATCH:'+key)
  with zipfile.ZipFile(path) as z:
   if z.testzip() is not None:raise ValueError('ARCHIVE_ZIP_CRC:'+key)
 tmp=dst.with_name(dst.name+'.partial')
 if tmp.exists():raise ValueError('REFUSE_EXISTING_PARTIAL_RUNTIME')
 try:
  for folder in ['src','checks','results','evidence','inputs','_c1_private/src','_c1_private/inputs']:(tmp/folder).mkdir(parents=True,exist_ok=True)
  for name in ['warm_interval.py','interval_jet.py','run_evaluations.py','assemble_certificate.py']:
   shutil.copy2(ROOT/'src'/name,tmp/'src'/name)
  for name in ['verify_c3.py','propagate_endpoint.py','test_c3.py']:
   shutil.copy2(ROOT/'checks'/name,tmp/'checks'/name)
  with zipfile.ZipFile(c1) as z:
   for name in ('P01_STATE.npz','emissivity.out','ENDPOINT_MEMORY_R7.json'):
    raw=z.read('HE18_C1_20261014/inputs/'+name)
    if sha(raw)!=INPUT_SHA[name]:raise ValueError('C1_INPUT_IDENTITY:'+name)
    (tmp/'inputs'/name).write_bytes(raw)
    (tmp/'_c1_private/inputs'/name).write_bytes(raw)
   source=z.read('HE18_C1_20261014/src/warm_source_reference.py')
   if sha(source)!=SOURCE_SHA:raise ValueError('C1_SOURCE_REFERENCE_IDENTITY')
   (tmp/'_c1_private/src/warm_source_reference.py').write_bytes(source)
  with zipfile.ZipFile(r5) as z:
   for name in ['HH_P01_COMPARISON.json','P01_INTERVAL.json']:
    raw=z.read('BASS_HE_HE17_R5_20261014/inputs/'+name)
    (tmp/'inputs'/name).write_bytes(raw)
  with zipfile.ZipFile(r8) as z:
   raw=z.read('HE17_R8_20261014/results/ADOPTION_RESULT.json')
   if sha(raw)!=INPUT_SHA['ADOPTION_RESULT_R8.json']:raise ValueError('R8_FIRST_CELL_RECORD_WRONG')
   (tmp/'inputs/ADOPTION_RESULT_R8.json').write_bytes(raw)
  module=tmp/'_c1_private/src/warm_source_reference.py'
  spec=importlib.util.spec_from_file_location('private_c1_warm_reference',module)
  srcmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(srcmod)
  source=srcmod.Source();i=1
  t0,t1=source.times[i:i+2]
  assert t0==srcmod.L(6250000000) and t1==srcmod.L(12500000000)
  left=np.asarray(source.y[:,i],dtype=np.float64);right=np.asarray(source.y[:,i+1],dtype=np.float64)
  m0=source.rhs(t0,source.y[:,i])[0].astype(np.float64)
  m1=source.rhs(t1,source.y[:,i+1])[0].astype(np.float64)
  target=tmp/'inputs/FIXED_REFERENCE.npz'
  np.savez_compressed(target,left=left,right=right,slope_left=m0,slope_right=m1,h=float(t1-t0))
  if sha(target.read_bytes())!=INPUT_SHA['FIXED_REFERENCE.npz']:
   raise ValueError('SECOND_REFERENCE_BYTESTREAM_DIFFERENT_FROM_C3_PRODUCER')
  info={'stage':'HE18_C3','input_archive_sha256':ARCHIVES,'input_sha256':INPUT_SHA,
        'left_s':str(t0),'right_s':str(t1),'source_rhs_endpoint_calls':2,'source_ivp_ode_calls':0,
        'private_runtime_directory':str(dst),'source_repository_mutated':False}
  (tmp/'inputs/STAGED_SOURCE_IDENTITY.json').write_text(json.dumps(info,indent=2)+'\n')
  tmp.rename(dst)
  return info
 except BaseException:
  if tmp.exists():shutil.rmtree(tmp)
  raise
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ('c1','r5','r8'):p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--output',required=True,type=Path)
 a=p.parse_args();print(json.dumps(stage(a.c1,a.r5,a.r8,a.output),indent=2))
