"""Full fixed-node numerical gate for the research-only Coulomb rotator."""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
import numpy as np
from bass_he.eq54 import support_cutoffs
from bass_he.geometry import _gk15_nodes,atomic_json
from arseny_reimpl.rotational import s_sigma_boundary
from coulomb_rotation import author_cutoff,coulomb_rotation_batch

TABLE_SHA='21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49'
SOURCE_SHA='496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba'


def fixed_rhos(table_path):
    p=Path(table_path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=TABLE_SHA:
        raise ValueError('R10D_TABLE_IDENTITY_MISMATCH')
    table=json.loads(p.read_text())
    if table['source_sha256']!=SOURCE_SHA or table['status']!='COMPLETE_VALID_EXACT_NODE_TABLE' or len(table['rows'])!=360:
        raise ValueError('R10D_TABLE_IDENTITY_MISMATCH')
    found={x['rho_hex'] for x in table['rows']}
    cuts=support_cutoffs()
    nodes=np.concatenate([np.sqrt(_gk15_nodes(a*a,b*b)) for a,b in zip(cuts[:-1],cuts[1:])])
    if len(found)!=105 or len(nodes)!=105 or set(float(x).hex() for x in nodes)!=found or np.any(nodes<=0):
        raise ValueError('R10D_FIXED_NODE_IDENTITY_MISMATCH')
    return nodes


def run(table_path,out_path):
    nodes=fixed_rhos(table_path)
    gate=json.loads((Path(__file__).parent/'NUMERICAL_GATE_PRECOMMITTED.json').read_text())
    records=[]
    for N,l in [(2,1),(3,1),(3,2)]:
        for cutoff_label,cut in [('CPC',s_sigma_boundary(l)),('AUTHOR',author_cutoff(l))]:
            for E in (0.5,5.0):
                results={}
                for steps in gate['steps']:
                    r=coulomb_rotation_batch(N,l,np.full(105,E),nodes,steps=steps,R_cut=cut)
                    U=r['U_z'];P=r['P_abs']
                    unit=float(np.max(np.abs(U.conj().swapaxes(-2,-1)@U-np.eye(2*l+1))))
                    stochastic=float(np.max(np.abs(P.sum(axis=1)-1)))
                    results[steps]=r
                    records.append({'N':N,'l':l,'cutoff':cutoff_label,'energy_keV_u':E,
                                    'steps':steps,'entered_count':int(np.count_nonzero(r['entered'])),
                                    'max_unitarity_defect':unit,
                                    'max_collapsed_column_stochastic_defect':stochastic,
                                    'minimum_probability':float(P.min()),
                                    'coulomb_a':float(r['coulomb_a'][0])})
                p64=results[64]['P_abs'];p128=results[128]['P_abs'];p256=results[256]['P_abs']
                e1=float(np.max(abs(p64-p128)));e2=float(np.max(abs(p128-p256)))
                records.append({'N':N,'l':l,'cutoff':cutoff_label,'energy_keV_u':E,
                                'comparison':'64_to_128_and_128_to_256',
                                'max_probability_difference_64_128':e1,
                                'max_probability_difference_128_256':e2,
                                'step_doubling_decreases':bool(e2<=e1),
                                'gate_pass':bool(e2<=gate['max_probability_difference_128_to_256'])})
    unitarity=max(x['max_unitarity_defect'] for x in records if 'steps' in x)
    stochastic=max(x['max_collapsed_column_stochastic_defect'] for x in records if 'steps' in x)
    pairs=[x for x in records if 'comparison' in x]
    mx=max(x['max_probability_difference_128_256'] for x in pairs)
    passed=(mx<=gate['max_probability_difference_128_to_256'] and
            unitarity<=gate['max_unitarity_defect'] and
            stochastic<=gate['max_collapsed_column_stochastic_defect'] and
            all(x['step_doubling_decreases'] for x in pairs))
    result={'status':'R10D_ROTATION_NUMERICS_PASS' if passed else 'R10D_ROTATION_NUMERICS_UNRESOLVED',
            'table_sha256':TABLE_SHA,'source_sha256':SOURCE_SHA,'nodes':105,
            'max_probability_difference_128_256':mx,'max_unitarity_defect':unitarity,
            'max_collapsed_column_stochastic_defect':stochastic,'records':records,
            'gate':gate,'new_contour_solves':0}
    atomic_json(out_path,result)
    return result
