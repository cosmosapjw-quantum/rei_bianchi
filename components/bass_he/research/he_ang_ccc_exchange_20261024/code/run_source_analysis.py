"""Printed Table I arithmetic only; manufactured phase control is separate."""
from decimal import Decimal, localcontext
import csv
import hashlib
import json
import math
from pathlib import Path
from ccc_exchange import raw_pair_diagnostics

UNIT=Path(__file__).resolve().parents[1]


def main():
    table=json.loads((UNIT/'source/Stelbovics1999_TableI.json').read_text())
    csv_bytes=(UNIT/'source/stelbovics_table1.csv').read_bytes()
    rows=list(csv.DictReader(csv_bytes.decode().splitlines()))
    if rows != table['rows']:
        raise ValueError('CSV and preserved JSON strings differ')
    if table['normalization'] != {'published_factor_four_already_applied': True,
                                  'additional_factor_applied': '1', 'spin_weight_applied': False}:
        raise ValueError('source normalization metadata differs')
    comparisons=[]
    with localcontext() as ctx:
        ctx.prec=60
        for row in rows:
            ratio=Decimal(row['published_4CCC_pi_a0_squared_per_Ryd'])/Decimal(row['BRM_pi_a0_squared_per_Ryd'])
            comparisons.append({**row, 'published_over_BRM':str(ratio),
                                'relative_deviation':str(ratio-1), 'additional_factor_applied':'1'})
    phase_controls=[]
    for n in range(65):
        phi=n*math.pi/64
        a,b=[1.,0.],[math.cos(phi),math.sin(phi)]
        channels={str(spin):raw_pair_diagnostics(a,b,spin) for spin in (0,1)}
        phase_controls.append({'phase_rad':phi, 'channels':channels,
                               'identity_max_abs_residual':max(abs(2*d['U']['float']-d['C']['float']-d['D']['float']) for d in channels.values())})
    result={'status':'NUMERICALLY_CHECKED_SCOPED', 'table_id':table['table_id'],
            'table_csv_sha256':hashlib.sha256(csv_bytes).hexdigest(),
            'source_rows':len(rows), 'printed_strings_unchanged':True,
            'normalization':table['normalization'], 'comparisons':comparisons,
            'model':'Temkin-Poet singlet S-wave', 'energy_kind':'total_three_body_energy',
            'density_unit':'pi*a0^2/Ry', 'measure':'dE_secondary',
            'comparison_scope':'printed Table I arithmetic, no fresh CCC/BRM solve or convergence bound',
            'manufactured_phase_controls':phase_controls,
            'max_manufactured_identity_abs_residual':max(r['identity_max_abs_residual'] for r in phase_controls),
            'physical_provider_admitted':False, 'parent_status':'SOURCE_INPUT_PENDING',
            'new_IVP':0,'old_suite_runs':0,'source_solver_runs':0}
    (UNIT/'results/source_analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'source_rows':len(rows),'phase_controls':len(phase_controls),
                      'max_identity_abs_residual':result['max_manufactured_identity_abs_residual']}))


if __name__=='__main__':main()
