"""Exact finite binary64-input reductions and decomposition, not true-error bounds."""
import math
from fractions import Fraction as F
SPECIES=('HI','HeI','HeII')
def finite_nonnegative(v):
    if not isinstance(v,(float,int)) or not math.isfinite(v) or v<0:raise ValueError('FINITE_NONNEGATIVE_REQUIRED')
    return F.from_float(float(v))
def checked_rows(rows):
    for i,r in enumerate(rows):
        if int(r['index'])!=i:raise ValueError('SAMPLE_IDENTITY')
        for k in ('weight','density','energy_eV',*('sigma_'+s for s in SPECIES)):finite_nonnegative(r[k])
        if r['weight']<=0 or r['energy_eV']<=0 or not math.isfinite(r['eta']):raise ValueError('INVALID_SPECTRAL_GEOMETRY')
def exact_rates(meta,rows):
    checked_rows(rows);pre=finite_nonnegative(meta['c_cm_s'])*finite_nonnegative(meta['nH']);out=[F(0)]*3
    for r in rows:
        weight=finite_nonnegative(r['weight'])*finite_nonnegative(r['density'])
        for i,s in enumerate(SPECIES):out[i]+=weight*finite_nonnegative(r['sigma_'+s])
    return [pre*x for x in out]
def decompose(g22,g24,g42,g44):
    if not all(isinstance(x,F) for x in (g22,g24,g42,g44)):raise ValueError('EXACT_INPUTS_REQUIRED')
    out={'total':g44-g22,'fixed_parent_rule':g44-g42,'fixed_grid_history':g42-g22,'reverse_rule':g24-g22,'reverse_history':g44-g24,'interaction':g44-g42-g24+g22}
    assert out['total']==out['fixed_parent_rule']+out['fixed_grid_history']==out['reverse_rule']+out['reverse_history']
    return out
def same_grid_stock_bound(meta,left,right):
    checked_rows(left);checked_rows(right)
    if len(left)!=len(right):raise ValueError('MEASURE_LENGTH')
    for a,b in zip(left,right):
        if any(a[k]!=b[k] for k in ('eta','weight','energy_eV',*('sigma_'+s for s in SPECIES))):raise ValueError('FIXED_GRID_REQUIRED')
    pre=finite_nonnegative(meta['c_cm_s'])*finite_nonnegative(meta['nH']);out=[F(0)]*3
    for a,b in zip(left,right):
        delta=abs(finite_nonnegative(a['density'])-finite_nonnegative(b['density']))*finite_nonnegative(a['weight'])
        for i,s in enumerate(SPECIES):out[i]+=delta*finite_nonnegative(a['sigma_'+s])
    return [pre*x for x in out]
