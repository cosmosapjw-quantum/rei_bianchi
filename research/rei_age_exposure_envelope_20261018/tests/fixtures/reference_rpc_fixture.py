#!/usr/bin/env python3
"""Deterministic text RPC fixture: prescribed opacity plus one domain retry."""
import json
import math
import os
from pathlib import Path
import sys

births=[.3,.7]
cells=1
extra=14
size=4+2*len(births)+extra
initial=[0.,0.,0.,1.]
setup=dict(birth_count=2,births=births,x0=0.,x1=1.,cells=cells,extra=extra,
           initial=initial,initial_physical=initial,encoded_births=[[math.log(1e-4),0.]]*2,
           active_indices=[[4,5],[6,7]],source_inventory=[[1e-4,.002]]*2,
           he_h=.08,binding_ev=[13.6,24.59,54.42],birth_times_s=births)
print(json.dumps(setup),flush=True)
failed=False
for line in sys.stdin:
    fields=line.split();mode=fields[0];active=int(fields[1]);x=float(fields[2]);y=list(map(float,fields[3:]))
    if mode=='R':
        with Path(os.environ['REI_FIXTURE_RHS_LOG']).open('a') as log:log.write(line)
        if active==1 and not failed and x>.55:
            failed=True
            print('ERR IGM_STATE_OR_UNIT_DOMAIN fixture_once',flush=True)
            continue
        result=[0.]*size
        opacity=50. if x<.4 else 200.
        photo=0.
        for cohort in range(active):
            index=4+2*cohort
            result[index]=-opacity
            photo+=opacity*math.exp(y[index])
        result[-extra]=20.*photo
        result[-extra+4]=photo
        print(' '.join(format(v,'.17e') for v in result),flush=True)
    elif mode=='P':
        number=sum(math.exp(y[4+2*i]) for i in range(active))
        print(json.dumps(dict(N=number,U=20.*number,flat=y[:4],ledgers=y[-extra:],
                              Gamma_s=[0.,0.,0.],heat_erg_per_absorber_s=[0.,0.,0.],
                              temperature_K=1.,cohorts=[],birth_times_s=births[:active])),flush=True)
    else:
        raise RuntimeError(mode)
