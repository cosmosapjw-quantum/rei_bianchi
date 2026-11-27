"""Source-only reproducible bitwise/operator and validation-cost comparison."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=Path('/root/BASS_HE_HE27_SOURCECUT_20261016')
sys.path.insert(0,str(ROOT/'research/he27_sourcecut_native_20261016/src'))
from sourcecut_v3 import SourceCutModel as V3
from sourcecut_fast import SourceCutModel as Fast

class NoOwner:pass

def main():
    records=[]
    for q in (-.005,0.,.005):
        v3=V3(NoOwner(),4,4,q)
        fast=Fast(NoOwner(),4,4,q)
        assert v3.source_table_sha256==fast.source_table_sha256
        assert v3.K==fast.K and np.array_equal(v3.Eref,fast.Eref)
        times=[float(f*v3.t_end) for f in np.linspace(0,1,11)]
        times.extend(float(f*v3.t_end) for f in
                     (.0001273786026739819,.0009449402471520216,
                      .0694303,.3300042,.6699852,.9305666))
        short=[i for i in range(len(v3._cut_bounds)-1)
               if i not in v3._source_tables]
        times.extend(float((v3._cut_bounds[i]+v3._cut_bounds[i+1])/2)
                     for i in (short[0],short[len(short)//2],short[-1]))
        maxdonor=0.;maxlocal=0
        for t in times:
            index=v3._locate(t)
            left,right=(float(v3._cut_bounds[index]),
                        float(v3._cut_bounds[index+1]))
            v3.set_interval(left,right);fast.set_interval(left,right)
            a=v3.source(t);b=fast.source(t)
            assert np.array_equal(a,b)
            r3=np.array(v3.source_diagnostics['donor_raw'])
            rf=np.array(fast.source_diagnostics['donor_raw'])
            maxdonor=max(maxdonor,float(np.max(abs(r3-rf)/np.maximum(abs(r3),1e-30))))
            maxlocal=max(maxlocal,fast.source_diagnostics['max_angle_band_relative_error'])
        record={'q':q,'m':4,'angles':4,'sampled_flux_vectors':len(times),
                'bitwise_flux_equal':True,'source_table_sha256':fast.source_table_sha256,
                'max_fast_v3_donor_relative_difference':maxdonor,
                'max_fast_angle_band_relative_defect':maxlocal,
                'physical_GL64_GL128_relative_difference':fast.physical_birth_quadrature_relative}
        if q==0.:
            queries=np.linspace(.001,.999,201)*v3.t_end
            v3.set_interval(0.,v3.t_end/100)
            fast.set_interval(0.,fast.t_end/100)
            start=time.perf_counter()
            for t in queries:v3.source_moments(float(t))
            slow=time.perf_counter()-start
            start=time.perf_counter()
            for t in queries:fast.source_moments(float(t))
            quick=time.perf_counter()-start
            record.update(validation_queries=len(queries),v3_validation_seconds=slow,
                          fast_validation_seconds=quick,speed_ratio=slow/quick)
        records.append(record)
    result={'schema':'bass_he.he27.source_fast_validation.v1',
            'scope':'SOURCE_ONLY_NO_NATIVE_CHEMISTRY',
            'v3_source_sha256':hashlib.sha256((ROOT/'research/he27_sourcecut_native_20261016/src/sourcecut_v3.py').read_bytes()).hexdigest(),
            'fast_source_sha256':hashlib.sha256((ROOT/'research/he27_sourcecut_native_20261016/src/sourcecut_fast.py').read_bytes()).hexdigest(),
            'unchanged_eight_moment_gate_relative':3e-13,
            'cases':records}
    temp=HERE/'SOURCE_FAST_VALIDATION.json.tmp';final=HERE/'SOURCE_FAST_VALIDATION.json'
    with temp.open('x') as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.flush();os.fsync(stream.fileno())
    temp.replace(final)
    fd=os.open(HERE,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
