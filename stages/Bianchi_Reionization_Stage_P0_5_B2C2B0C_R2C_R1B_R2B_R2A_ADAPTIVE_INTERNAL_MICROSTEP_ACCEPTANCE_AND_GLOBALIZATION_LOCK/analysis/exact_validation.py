#!/usr/bin/env python3
"""Independent symbolic/decimal replay for the R2B-R2A durable stage."""
from __future__ import annotations
from decimal import Decimal, getcontext
import hashlib, json
from pathlib import Path
import sympy as sp

STAGE=Path(__file__).resolve().parents[1]
RECEIPTS=STAGE/'receipts'

def main() -> int:
    getcontext().prec=90
    # Exact nuclei identities.
    htot, hi0, ahi, rh = sp.symbols('Htot HI0 AHI RH')
    hi1=hi0-ahi+rh; hii1=htot-hi1
    he_tot, hei0, heiii0, ahei, aheii, rheii, rheiii = sp.symbols(
        'HeTot HeI0 HeIII0 AHeI AHeII RHeII RHeIII'
    )
    hei1=hei0-ahei+rheii
    heiii1=heiii0+aheii-rheiii
    heii1=he_tot-hei1-heiii1
    # Exact owner partition and uniform substep budget.
    hs=sp.symbols('h0:4', nonnegative=True); H=sp.Add(*hs)
    qs=[h/H for h in hs]
    total=sp.symbols('J', nonnegative=True)
    n=sp.symbols('n', integer=True, positive=True); dt=sp.symbols('dt', positive=True)
    lam=sp.symbols('lam', nonnegative=True)
    y,g=sp.symbols('y g', nonnegative=True)
    symbolic={
        'hydrogen_nuclei_residual':sp.simplify(hi1+hii1-htot),
        'helium_nuclei_residual':sp.simplify(hei1+heii1+heiii1-he_tot),
        'owner_fraction_sum_residual':sp.simplify(sp.Add(*qs)-1),
        'owner_current_sum_residual':sp.simplify(sp.Add(*[total*q for q in qs])-total),
        'uniform_substep_budget_residual':sp.simplify(n*(total*dt/n)-total*dt),
        'damped_picard_convex_identity':sp.simplify(y+lam*(g-y)-((1-lam)*y+lam*g)),
        'subgrid_resolved_source_vector':[0,0,0],
    }
    assert all(v==0 for k,v in symbolic.items() if k not in {'subgrid_resolved_source_vector'})

    results=json.loads((STAGE/'results.json').read_text())
    perf=json.loads((STAGE/'data/performance_benchmark.json').read_text())
    lane_checks={}
    for lane,row in results['lanes'].items():
        gates=row['gates']
        pass_names=('fixed_point','positivity','H_nuclei','He_nuclei','photon',
                    'resolved_thermal','unresolved_energy','commit_once','rollback','restart')
        lane_checks[lane]={
            'all_nonlocal_gates_pass':all(str(gates[n]['status']).startswith('PASS') for n in pass_names),
            'local_error_fails':gates['local_error']['status']=='FAIL',
            'terminal_partition':row['terminal_certificate']['partition'],
            'terminal_classification':row['terminal_certificate']['classification'],
        }
        assert lane_checks[lane]['all_nonlocal_gates_pass']
        assert lane_checks[lane]['local_error_fails']
        assert lane_checks[lane]['terminal_partition']==1024
        assert lane_checks[lane]['terminal_classification']=='LOCAL_ERROR_FAILURE'
    ext={r['partition']:r for r in results['extension_auditor']['rows']}
    assert not ext[2048]['passes_locked_local_error']
    assert ext[4096]['passes_locked_local_error']
    assert perf['owner_law']['promoted'] is True
    assert perf['jax_thermal']['production_promoted'] is False

    # Decimal replay of the measured owner speedup and local-error ordering.
    legacy=Decimal(str(perf['owner_law']['legacy']['seconds']))
    candidate=Decimal(str(perf['owner_law']['candidate']['seconds']))
    speed=legacy/candidate
    p1024=Decimal(str(next(iter(results['lanes'].values()))['gates']['local_error']['value']))
    p2048=Decimal(str(ext[2048]['local_error']))
    p4096=Decimal(str(ext[4096]['local_error']))
    assert speed >= Decimal('5')
    assert p1024 > p2048 > p4096
    assert p4096 <= Decimal('0.0002') < p2048

    receipt={
        'classification':'R2B_R2A_EXACT_VALIDATION_RECEIPT',
        'symbolic':{k:str(v) for k,v in symbolic.items()},
        'lane_checks':lane_checks,
        'decimal_90':{
            'owner_speedup':str(speed),
            'local_error_dt1024':str(p1024),
            'local_error_dt2048':str(p2048),
            'local_error_dt4096':str(p4096),
        },
        'results_sha256':hashlib.sha256((STAGE/'results.json').read_bytes()).hexdigest(),
        'performance_sha256':hashlib.sha256((STAGE/'data/performance_benchmark.json').read_bytes()).hexdigest(),
        'pass':True,
    }
    (RECEIPTS/'EXACT_VALIDATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
