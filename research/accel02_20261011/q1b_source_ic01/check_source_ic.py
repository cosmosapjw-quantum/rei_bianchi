"""Q1B_SOURCE_IC01: prescribed local moments, no history integration."""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

EV = 1.602176634e-12
PINS = {
    'research/physical_provider_20261010/hm12_data.py': 'ede512206bd6f5acc85b1c6b90fda4edc256b4dd8a70c42f9726932b6bff5121',
    'research/physical_provider_20261010/sources/emissivity.out': '88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
    'research/physical_provider_20261010/sources/UVB.out': 'a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc',
    'research/physical_provider_20261010/sources/acquisition.json': 'd9f3ce2a9174587124489d17542350cf01386eec8cdd5026be0399052f2e7b2b',
    'research/accel02_20261011/recovery/Q0_SOURCE_ATTRIBUTION.json': '91959c5e09073ae89afcfe14937e6bc2dc4478692143873471934f542fc1ad6d',
    'research/accel02_20261011/q1a/GRID_G1.json': '13bdcc466891d0edd18cd2c645f388cc13f89a88f13a0af44a9c0b6cd7136efd',
    'research/accel02_20261011/q1a/NEXT_DESIGN.md': '296421ea8846c7f137a5094fcc4745b35608efbc0e082aa02b89acd80b4d4815',
    'research/accel02_20261011/q1a/review/Q1B_PROPOSAL_REVIEW.json': '9cf208e79b5f6d426d4ad820dd5fe62c9f9f2800e9a6e476d51121c6307884bc',
}
BANDS = {'full': 10., 'HI_ionizing': 13.60, 'HeI_ionizing': 24.59, 'HeII_ionizing': 54.42}


def cell_moments(table, qlo, qhi, z, R, weight, threshold=10.):
    if not all(math.isfinite(x) for x in (qlo, qhi, z, R, weight, threshold)) or qlo <= 0 or qhi <= qlo or R <= 0 or weight < 0 or threshold < 10:
        raise ValueError('INVALID_CELL_INPUT')
    lo, hi = max(R*qlo, 10., threshold), min(R*qhi, 50000.)
    if hi <= lo:
        return (0., 0., 0.)
    m0 = table.moment(lo, hi, z, power=0, reference_eV=1, proper_photons=True)
    m1 = table.moment(lo, hi, z, power=1, reference_eV=1, proper_photons=True)
    sn, sq = weight*R**-3*m0, weight*R**-4*m1
    su = R*sq
    if not all(math.isfinite(x) and x >= 0 for x in (sn, sq, su)):
        raise ValueError('INVALID_CELL_MOMENT')
    assert su == R*sq
    return sn, sq, su


def aggregate(table, edges, z, R):
    result = {}
    for band, threshold in BANDS.items():
        cells = [cell_moments(table, float(a), float(b), z, R, .5, threshold)
                 for a,b in zip(edges[:-1], edges[1:])]
        # The two frozen angles have the same FLRW R and weight 1/2.
        n = math.fsum(x[0] for x in cells for _ in range(2))
        u = math.fsum(x[2] for x in cells for _ in range(2))
        result[band+'_number_ref'] = n
        result[band+'_number_proper'] = n*R**3
        result[band+'_energy_ref'] = u*EV
        result[band+'_energy_proper'] = u*EV*R**3
    return result


def compare(new, saved):
    n,s = np.asarray(new),np.asarray(saved)
    scale = float(np.max(np.abs(s)))
    error = float(np.max(np.abs(n-s)))
    return {'max_absolute_difference': error, 'saved_max_absolute': scale,
            'scaled_difference': error/scale if scale else None,
            'pass': bool(error/scale <= 1e-12) if scale else bool(np.all(n == 0))}


def run(root):
    observed = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in PINS}
    if observed != PINS:
        raise ValueError('HOLD_INPUT_FILE_IDENTITY')
    spec = importlib.util.spec_from_file_location('q1b_pinned_hm12_data', root/'research/physical_provider_20261010/hm12_data.py')
    hm = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = hm
    spec.loader.exec_module(hm)
    tables = hm.load_hm12()
    q0 = json.loads((root/'research/accel02_20261011/recovery/Q0_SOURCE_ATTRIBUTION.json').read_text())
    epochs = q0['exact_source_history']
    assert len(epochs) == 129
    uv = tables['uvb'].energies_eV
    jumps = uv[:-1][uv[:-1] == uv[1:]]
    qmax = 168999.99999999997
    base = np.exp(np.linspace(math.log(10.), math.log(qmax),65))
    base[0],base[-1] = 10.,qmax
    edges = np.unique(np.concatenate((base,jumps[(jumps>10)&(jumps<qmax)], [13.60,24.59,54.42,50000.])))
    enriched = np.sort(np.concatenate((edges,np.sqrt(edges[:-1]*edges[1:]))))
    assert np.all(np.diff(edges)>0) and np.all(np.diff(enriched)>0)
    assert np.all(np.isin(edges,enriched)) and edges[0]==10 and edges[-1]==qmax
    assert all(float(v) in edges for v in (13.60,24.59,54.42,50000.))
    grids = {'candidate':edges,'enriched':enriched}
    checks, data = {},{}
    for name, grid in grids.items():
        print('BEGIN '+name,flush=True)
        rows=[]
        for i,e in enumerate(epochs):
            R=1./e['a_rel']
            if not math.isfinite(R) or R<=0:
                raise ValueError('HOLD_GEOMETRY_DOMAIN')
            rows.append({k:e[k] for k in ('time_s','z','a_rel')} | aggregate(tables['emissivity'],grid,e['z'],R))
            if i%32==0: print(name+' epoch '+str(i),flush=True)
        source = {}
        for setname,indices in [('epochs129',range(129)),('original65',range(0,129,2))]:
            source[setname]={k:compare([rows[i][k] for i in indices],[epochs[i][k] for i in indices]) for k in rows[0] if k not in ('time_s','z','a_rel')}
        ic=aggregate(tables['uvb'],grid,15.9,1.)
        saved=q0['runs']['EVENT_COUPLED002']['initial_UVB_moment_comparison']
        iccheck={k:compare([ic[k+'_ref']],[v['exact_declared_interpolation']]) for k,v in saved.items()}
        highcells=[cell_moments(tables['uvb'],float(a),float(b),15.9,1.,.5) for a,b in zip(grid[:-1],grid[1:]) if a>=50000.]
        assert highcells and all(x==(0.,0.,0.) for x in highcells)
        checks[name]={'source':source,'IC':iccheck,'high_q_IC_exact_zero':True,'cells':len(grid)-1}
        data[name]={'edges_eV':grid.tolist(),'source_history':rows,'initial_UVB_moments':ic}
    # Analytic constant ordinate fixture is local and does not replace pinned source.
    fixture=hm.HM12Table('uvb',np.array([0.,1.]),np.array([hm.HC_EV_ANGSTROM/100000.,hm.HC_EV_ANGSTROM/1.]),np.ones((2,2)))
    factor=fixture.proper_photon_factor(.5)
    fixtures=[]
    for lo,hi,R in [(40000.,80000.,1.),(25000.,50000.,2.),(60000.,70000.,1.),(8.,12.,1.)]:
        actual=cell_moments(fixture,lo,hi,.5,R,.5)
        left,right=max(R*lo,10.),min(R*hi,50000.)
        expected=(0.,0.,0.) if right<=left else (.5*R**-3*factor*math.log(right/left),.5*R**-4*factor*(right-left),.5*R**-3*factor*(right-left))
        comparison=[compare([a],[b]) for a,b in zip(actual,expected)]
        fixtures.append({'cell':[lo,hi],'R':R,'actual':actual,'expected':expected,'comparisons':comparison})
    rejected=0
    for args in [(0.,1.,.5,1.,.5),(2.,1.,.5,1.,.5),(1.,2.,.5,0.,.5),(1.,2.,.5,1.,-1.),(1.,2.,float('nan'),1.,.5)]:
        try: cell_moments(fixture,*args)
        except ValueError: rejected+=1
    assert rejected==5
    passed=all(v['pass'] for c in checks.values() for s in c['source'].values() for v in s.values()) and all(v['pass'] for c in checks.values() for v in c['IC'].values()) and all(v['pass'] for f in fixtures for v in f['comparisons'])
    return {'schema':'q1b_source_ic01.v1','outcome':'PASS_SOURCE_IC_MOMENT_COMPONENT_PENDING_INDEPENDENT_REVIEW' if passed else 'HOLD_SOURCE_IC_MOMENT_COMPARISON', 'input_sha256':observed,'tolerance':1e-12,'checks':checks,'fixtures':fixtures,'invalid_inputs_rejected':rejected,'data':data,'geometry':{'R':'1/a_rel','mu':[-1/math.sqrt(3),1/math.sqrt(3)],'weights':[.5,.5],'qmax_eV':qmax},'execution':dict.fromkeys(['native','SIGMA','RHS','JAC','ODE','build','history_replay'],0),'claim':'Source/IC local moments only; numerical output of declared HM12 interpolation.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    started=time.monotonic()
    try:
        result=run(args.root)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        result={'outcome':'HOLD_SOURCE_IC_EXECUTION','error_type':type(exc).__name__,'error':str(exc),'execution':dict.fromkeys(['native','SIGMA','RHS','JAC','ODE','build','history_replay'],0)}
    result['wall_s']=time.monotonic()-started
    result['implementation_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f: json.dump(result,f,indent=2,allow_nan=False)
    print(result['outcome'],flush=True)
    sys.exit(0 if result['outcome'].startswith('PASS_') else 1)
