"""Execute only the previously unreached frozen manufactured fixture."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import numpy as np
import validate as v
from opacity_native import NativeOpacity

class SigmaOnly:
    def __init__(self):
        self.opacity=NativeOpacity();self.counts={'native_processes':1,'SIGMA':0,'SIGMA_energies':0,'CELL_RHS_V1':0}
        sigma=self.opacity.sigma
        def bounded(energy):
            v.need(self.counts['SIGMA']<2 and self.counts['SIGMA_energies']+len(energy)<=192,'CONTINUATION_SIGMA_CAP')
            self.counts['SIGMA']+=1;self.counts['SIGMA_energies']+=len(energy)
            return sigma(energy)
        self.opacity.sigma=bounded

def run():
    pins=json.loads((v.UNIT/'evidence/attempt1/RESULT.json').read_text())['input_sha256'].copy()
    pins.update({str((v.UNIT/'validate.py').relative_to(v.ROOT)):'cc6db64263b6abd251576f74bfd9222196c784cf4c4f2ebcd3c1dbd79d126e7a',str((v.UNIT/'adapter.py').relative_to(v.ROOT)):'c7f1cac3ecbb4a8dc8edfc62f1c7458fff77e9ff6633cadb0cfb1c8e4c15f3c5'})
    v.need(v.digest(v.UNIT/'evidence/attempt1/RESULT.json')=='9b5f1d4190f67207b72df3e59d869c0dd07b86f47793336d38b850201f6731f1','FIRST_FAILURE_IDENTITY')
    v.need(all(v.digest(v.ROOT/p)==s for p,s in pins.items()),'CONTINUATION_SOURCE_IDENTITY')
    v.RESULT['input_sha256']=pins;v.RESULT['continuation']='MANUFACTURED_TAU1_CONTINUATION01'
    original=v.evaluate
    def bounded(*args,**kwargs):
        v.need(v.RESULT['execution']['gas_map_evaluations']<50,'CONTINUATION_MAP_CAP')
        return original(*args,**kwargs)
    v.evaluate=bounded
    caller=SigmaOnly()
    try:
        g={'a_rel':1.3,'b':0.,'H':2e-18,'s':.2*2e-18,'nH':1e-3,'nHe':8e-5,'Tcmb_K':46.}
        gas=v.gas_at_temperature(g,[.2,.3,.1],5000.)
        directions=np.array([[.1,0,0,0],[0,.1,0,0],[0,0,.1,0],[0,0,0,.1*gas[3]],[.1,-.08,.03,.1*gas[3]]])
        v.fixture(caller,'manufactured_tau_order_one',(1e-8,90e-8,1.,60.,120.),g,gas,directions,['central','central','central','thermal','central'])
    finally:v.RESULT['execution'].update(caller.counts);caller.opacity.close()
    v.need(all(v.digest(v.ROOT/p)==s for p,s in pins.items()),'CONTINUATION_SOURCE_CHANGED')
    v.RESULT['outcome']='PASS_MANUFACTURED_TAU1_JVP_SCOPED';v.RESULT['actual_derivative']='HOLD_FD_ORACLE_PRECISION'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();v.RESULT['outcome']='HOLD_MANUFACTURED_CONTINUATION_FIRST_FAILURE';v.RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        v.RESULT['wall_s']=time.monotonic()-t;v.dump(out/'RESULT.json',v.RESULT);print(json.dumps({'outcome':v.RESULT['outcome'],'execution':v.RESULT['execution']}));return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','60s','prlimit','--as=2147483648','--cpu=60','--fsize=8388608','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    v.dump(out/'STARTED.json',{'command':cmd,'cwd':str(v.ROOT),'runner_sha256':v.digest(__file__),'contract':json.loads((v.UNIT/'CONTINUATION_MANUFACTURED01.json').read_text())})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=v.ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'files':{p.name:{'sha256':v.digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(x['bytes'] for x in receipt['files'].values())<=8388608;v.dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode

if __name__=='__main__':raise SystemExit(main())
