"""Reduce recorded evidence only; no electronic solve, no fitted limit."""
from pathlib import Path
import json,time
import numpy as np
from numpy.polynomial.legendre import leggauss
from run_centered import load_pair
from evidence_io import atomic_json,sha256
ROOT=Path(__file__).resolve().parents[1]
def read(tag):return json.loads((ROOT/f'evidence/{tag}.json').read_text())
def overlap(a,b):
    q,w=leggauss(max(a.degree,b.degree)+2)
    mesh=np.unique(np.r_[a.boundaries,b.boundaries]);s=0.
    for lo,hi in zip(mesh[:-1],mesh[1:]):
        if lo>=min(a.boundaries[-1],b.boundaries[-1]):continue
        jac=(hi-lo)/2;r=lo+jac*(q+1);ua,ub=a.radial(r),b.radial(r)
        n=min(len(a.ls),len(b.ls));s+=np.sum(ua[:n]*ub[:n]*(w*jac))
    return float(s)
base=read('B_l96');previous=read('B_l72');base_states=load_pair('B_l96')
levels=[read(f'B_l{l}') for l in (8,12,18,24,32,40,72,96)]
rows=[]
for tag,axis in [('B_l72','angular_previous'),('B_l96_h80','radial_h'),('B_l96_p5','radial_p'),('B_l96_q22','Hamiltonian_quadrature'),('B_l96_tail32','outer_radius')]:
    x=read(tag);s=load_pair(tag);ov=[overlap(i,j) for i,j in zip(base_states,s)]
    rows.append({'tag':tag,'axis':axis,'energy_delta':[abs(a['energy']-b['energy']) for a,b in zip(base['states'],x['states'])],
        'L_O_delta':abs(base['direct']['L_O_over_minus_i_hbar']-x['direct']['L_O_over_minus_i_hbar']),
        'physical_L2_overlap':ov,'L2_state_increment':[float(np.sqrt(max(0,2-2*v))) for v in ov],
        'sector_gap_delta':[abs(a['metadata']['discrete_sector_gap']-b['metadata']['discrete_sector_gap']) for a,b in zip(base['states'],x['states'])],
        'vs_prolate':x['vs_C1_prolate'],'invariants':x['invariants']})
allselected=[base]+[read(t) for t in ('B_l96_h80','B_l96_p5','B_l96_q22','B_l96_tail32')]
tail=read('PROLATE_TAIL_ONLY')
criteria={
'independent_energies':max(v for x in allselected for v in x['vs_C1_prolate']['energy_abs'])<1e-5,
'independent_L_O':max(x['vs_C1_prolate']['L_O_abs'] for x in allselected)<1e-5,
'all_refinement_energies':max(v for x in rows for v in x['energy_delta'])<2e-6,
'all_refinement_L_O':max(x['L_O_delta'] for x in rows)<2e-6,
'direct_torque_O':max(x['invariants']['direct_torque_O_abs'] for x in allselected)<1e-7,
'momentum_commutator':max(x['invariants']['momentum_commutator_abs'] for x in allselected)<1e-7,
'force_quadrature':max(x['invariants']['force_q22_to30_abs'] for x in allselected)<1e-8,
'norm':max(abs(s['mass_norm']-1) for x in allselected for s in x['states'])<1e-10,
'algebraic_residual':max(s['residual'] for x in allselected for s in x['states'])<1e-9,
'prolate_tail_energies':max(tail['tail_delta']['energies'])<1e-8,
'prolate_tail_L_O':tail['tail_delta']['L_O_abs']<2e-6,
'inner_prolate_knots_preserved':tail['inner_knots_preserved_exact'],
'inner_reference_knots_preserved':bool(np.array_equal(load_pair('B_l96_tail32')[0].boundaries[:len(base_states[0].boundaries)],base_states[0].boundaries))}
axisexec=read('AXIS_EXECUTION');assert len(axisexec['runs'])==5 and all(x['exit_code']==0 for x in axisexec['runs'])
x={'status':'ALL_SCOPED_CRITERIA_PASS' if all(criteria.values()) else 'NOT_CONVERGED',
   'scope':'R=2 a_A only, empirical independent-discretization energies and specified coupling criteria; no continuum error enclosure',
   'selected_reference':'B_l96','criteria':criteria,'selected_energies':[s['energy'] for s in base['states']],
   'selected_direct':base['direct'],'selected_vs_prolate':base['vs_C1_prolate'],
   'selected_invariants':base['invariants'],'selected_sector_ritz_gaps':[s['metadata']['discrete_sector_gap'] for s in base['states']],
   'axis_comparisons':rows,'prolate_tail_delta':tail['tail_delta'],
   'angular_sequence':[{'lmax':v['config']['lmax'],'energies':[s['energy'] for s in v['states']],'L_O_bar':v['direct']['L_O_over_minus_i_hbar'],'vs_prolate':v['vs_C1_prolate'],'seconds':v['elapsed_seconds'],'max_rss_kib':v['max_rss_kib']} for v in levels],
   'max_rss_kib':max(v['max_rss_kib'] for v in levels+allselected),
   'R2_target_state_solves':28,'R2_pair_count':14,'additional_second_Ritz_roots':24,
   'sum_solver_and_operator_seconds':sum(v['elapsed_seconds'] for v in levels)+sum(read(t)['elapsed_seconds'] for t in ('B_l96_h80','B_l96_p5','B_l96_q22','B_l96_tail32'))+read('O24_DIAGNOSTIC')['elapsed_seconds']+tail['elapsed_seconds'],
   'original_l40_failure_preserved':True,'single_operational_amendment':'OPERATIONAL_AMENDMENT.json',
   'method_spread_is_error_bar':False,'continuum_certificate':False,'C2_broad_grid':'NOT_RUN','reducer_sha256':sha256(__file__)}
atomic_json(ROOT/'evidence/CONVERGENCE_SUMMARY.json',x)
print(json.dumps(x,indent=2))
