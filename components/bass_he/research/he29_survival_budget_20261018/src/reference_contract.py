"""HE29 reference acceptance: empirical agreement, never a certified error radius."""
from __future__ import annotations
import math
import numpy as np

OWNER='f7830e2f55e7a1938bc3c98f61b60651f8dae474'
JOBS=((2,512),(4,512),(8,512),(4,1024))
THREADS={k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')}
THREADS.update(OMP_DYNAMIC='FALSE',OMP_PLACES='cores',OMP_PROC_BIND='close')


def check_result(r):
    try:
        g=r['gas_final'];s=r['species_defect']
        if len(g)!=4 or len(s)!=3:raise ValueError('HE29_STATE_WIDTH')
        values=[r['number_defect'],r['energy_defect_ev'],r['min_photon'],r['temperature_K'],*s,*g]
        if not all(math.isfinite(float(x)) for x in values):raise ValueError('HE29_NONFINITE_RESULT')
        if (abs(r['number_defect'])>3e-15 or abs(r['energy_defect_ev'])>3e-12
            or max(abs(x) for x in s)>3e-12 or r['min_photon']<0 or r['temperature_K']<=0
            or not isinstance(r['gas_positive'],(bool,np.bool_)) or not r['gas_positive']):
            raise ValueError('HE29_RESULT_LEDGER_OR_POSITIVITY')
    except (KeyError,TypeError) as exc:raise ValueError('HE29_RESULT_SCHEMA') from exc


def admit_pair(a,b):
    check_result(a);check_result(b)
    spread=abs(a['temperature_K']-b['temperature_K'])
    fractions=max(abs(x-y) for x,y in zip(a['gas_final'][:3],b['gas_final'][:3]))
    if spread>1e-9 or fractions>1e-11:raise ValueError('HE29_REFERENCE_UNSTABLE')
    return {'reference_stable':True,'method_temperature_difference_K':spread,
            'absolute_fraction_difference':fractions,'error_radius_certified':False}


def same_model(a,b):
    fields=('m','angles','q','strips','source_table_nodes','table')
    if any(k not in a or k not in b or a[k]!=b[k] for k in fields):
        raise ValueError('HE29_SAME_MODEL_TABLE_REQUIRED')
    if not isinstance(a['table'],str) or not a['table']:raise ValueError('HE29_MISSING_TABLE_HASH')
