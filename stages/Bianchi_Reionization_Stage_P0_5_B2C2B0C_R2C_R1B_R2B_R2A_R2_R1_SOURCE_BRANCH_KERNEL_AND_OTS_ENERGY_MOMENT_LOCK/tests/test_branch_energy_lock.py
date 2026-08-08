from pathlib import Path
import csv, json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def test_source_table_and_domain_counts():
    rows=list(csv.DictReader((ROOT/'data/HUMMER_SEATON_1964_V_TABLE.csv').open()))
    assert np.allclose([float(r['v_equals_X_two_photon_fraction']) for r in rows],[0.285,0.305,0.325,0.35,0.375],rtol=0,atol=1e-15)
    s=json.loads((ROOT/'data/BRANCH_ENERGY_SUMMARY.json').read_text())
    assert s['domain_counts']['below_1e4K']==21600
    assert s['domain_counts']['inside_1e4_to_1e5K']==24480
    assert s['domain_counts']['above_1e5K']==0

def test_branch_envelope_is_nonnegative_and_closes_photon_count():
    s=json.loads((ROOT/'data/BRANCH_ENERGY_SUMMARY.json').read_text())
    assert s['branch_envelope']['negative_multiplicity_count']==0
    assert s['branch_envelope']['corner_count_per_node']==4
    assert s['branch_envelope']['max_photon_count_identity_residual']<1e-14
    with np.load(ROOT/'data/BRANCH_KERNEL_NODE_ENVELOPE.npz') as z:
        assert z['T_K'].shape==(46080,)
        assert np.all(z['v_cell_lower']>=0) and np.all(z['v_cell_upper']<=1)
        assert np.all(z['A_H_lower']>=0) and np.all(z['A_HeI_lower']>=0)

def test_two_photon_moments_are_nonunique_but_counts_match():
    d=json.loads((ROOT/'data/TWO_PHOTON_ENERGY_MOMENT_WITNESS.json').read_text())
    lo=d['constructive_witness_low']; hi=d['constructive_witness_high']
    for q in (lo,hi):
        assert abs(q['count_H_capable']-1.425)<1e-14
        assert abs(q['count_HeI_capable']-0.737)<1e-14
        assert abs(q['total_pair_energy_eV']-d['HeII_Lya_eV'])<1e-13
        assert abs(q['total_photon_count']-2)<1e-14
    assert abs(lo['H_capable_excess_eV']-hi['H_capable_excess_eV'])>7
    assert abs(lo['HeI_capable_excess_eV']-hi['HeI_capable_excess_eV'])>8

def test_energy_owner_matrix_has_one_owner_per_row():
    rows=list(csv.DictReader((ROOT/'data/ENERGY_OWNER_MATRIX.csv').open()))
    assert len(rows)==12
    assert all(r['energy_owner'] for r in rows)
    lya=[r for r in rows if r['event_or_channel'].startswith('HEIII_LYA')]
    assert len(lya)==3 and all(r['first_moment_status']=='MONOENERGETIC_EXACT' for r in lya)
