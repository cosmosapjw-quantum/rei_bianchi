#!/usr/bin/env python3
"""Recompose saved unchanged geometry after a transport-only numerical fix."""
from pathlib import Path
import os,sys,json,hashlib
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from bass_he.geometry import unjsonable,atomic_json
from run_research import assembly
rows=[]
for name in ('pilot','quadrature_q1','quadrature_q2'):
    p=ROOT/'evidence'/name
    eps={r['branch']:r['ep'] for r in unjsonable(json.loads((p/'EP_CERTIFICATES.json').read_text()))}
    geom={(r['branch'],r['rho']):r['result'] for r in unjsonable(json.loads((p/'GEOMETRY_RESULTS.json').read_text()))}
    old=json.loads((p/'INITIAL_COLUMN_OUTPUTS.json').read_text());new=assembly(eps,geom,old['energies_keV_u'],old['rhos'])
    diff=max(float(np.max(abs(new[f]-np.array(old['lanes'][f]['probabilities'])))) for f in ('1','2'))
    assert diff<2e-14
    rows.append(dict(stage=name,max_abs_difference=diff,action_geometry_reused_unchanged=True,
        minimum_probability=min(float(x.min()) for x in new.values()),
        maximum_column_sum_defect=max(float(np.max(abs(x.sum(-1)-1))) for x in new.values())))
atomic_json(ROOT/'evidence/ASSEMBLY_RECHECK.json',dict(rows=rows,transport_sha256=hashlib.sha256((ROOT/'src/bass_he/transport.py').read_bytes()).hexdigest(),scope='transport-only convex-update fix; unchanged geometry and rotor reused'))
print(json.dumps(rows,indent=2))
