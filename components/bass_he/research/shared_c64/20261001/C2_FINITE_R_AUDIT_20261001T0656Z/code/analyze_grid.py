"""Evaluate registered finite-grid criteria without re-solving any states."""
import json,sys,hashlib,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes

def main():
 c=json.loads((ROOT/'CONTRACT.json').read_text());t=c['criteria'];base=ROOT/'evidence/PROLATE_MPI';rows=[];inputs={}
 def read(R,kind):
  p=base/(f'R{R:g}_{kind}'.replace('.','p'))/'RESULT.json';inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
 for R in c['scientific_grid']:
  vals={kind:read(R,kind) for kind in ('base','h','p','tail')};a=vals['base'];o=a['operators'];d=o['direct']['24'];row={'R':R,'energies':a['energies'],'direct':d,'invariants':o['invariants'],'refinements':{},'configuration_checks':{}};gates={}
  for kind,v in vals.items():
   op=v['operators'];inv=op['invariants'];di=op['direct'];to=op['torque']
   e=max(abs(x-y) for x,y in zip(a['energies'],v['energies']));lo=abs(d['L_O_bar']-di['24']['L_O_bar']);lb=abs(d['L_B_bar']-di['24']['L_B_bar'])
   row['refinements'][kind]={'energy_delta_max_abs':e,'L_O_delta_abs':lo,'L_B_delta_abs':lb}
   gates[kind+'_spatial']=e<=t['energy_refinement_abs'] and max(lo,lb)<=t['L_O_refinement_abs']
   qd=max(abs(di['24'][k]-di['16'][k]) for k in ('L_O_bar','L_B_bar','p_x_bar','dipole_x','norm_g','norm_b'))
   qt=max(abs(to['28'][k]-to['20'][k]) for k in ('L_O_bar','L_B_bar','T_A','T_B'))
   residual=max(s['residuals'][k] for s in v['states'] for k in ('radial_discrete_relative','angular_discrete_relative'))
   matching=max(s['residuals']['matching_absolute']/max(1.,abs(s['separation_radial'])+abs(s['separation_angular'])) for s in v['states'])
   dark=max(abs(z['L_dark_O_bar']) for z in op['dark'].values())
   checks={'direct_quadrature_max_abs':qd,'force_quadrature_max_abs':qt,'algebraic_residual_max':residual,'scaled_matching_residual_max':matching,'dark_max_abs':dark,**inv}
   row['configuration_checks'][kind]=checks
   gates[kind+'_operators']=(max(inv['direct_torque_O_abs'],inv['direct_torque_B_abs'])<=t['direct_torque_abs'] and inv['momentum_commutator_abs']<=t['momentum_gap_dipole_abs'] and inv['origin_identity_abs']<=t['origin_identity_abs'])
   gates[kind+'_quadrature']=max(qd,qt)<=t['operator_quadrature_abs']
   gates[kind+'_norm_residual']=inv['norm_error_abs']<=t['norm_error_abs'] and residual<=t['algebraic_residual_relative']
   gates[kind+'_dark']=dark<=t['dark_abs']
  if not np.array_equal(vals['base']['states'][0]['actual_radial_edges'],vals['tail']['states'][0]['actual_radial_edges'][:65]):raise AssertionError('tail inner knots changed')
  gates['bright_nonzero']=abs(d['L_O_bar'])>t['L_O_refinement_abs']*10
  row['gates']=gates;row['pass']=all(gates.values());row['failed_gates']=[k for k,v in gates.items() if not v]
  row['scaled_diagnostics']={'small_L_O_over_R3':d['L_O_bar']/R**3,'small_limit':4*math.sqrt(2)/15,'large_L_O_over_R':d['L_O_bar']/R,'large_limit':32*math.sqrt(2)/243,'large_minus_L_B_times_R2':-d['L_B_bar']*R*R,'large_B_limit':128*math.sqrt(2)/729,'asymptotic_closure':'NOT_CLAIMED'}
  rows.append(row)
 out={'scope':'seven registered points only','rows':rows,'all_pointwise_gates_pass':all(x['pass'] for x in rows),'input_sha256':inputs,'contract_sha256':hashlib.sha256((ROOT/'CONTRACT.json').read_bytes()).hexdigest(),'continuum_certificate':False}
 atomic_create(ROOT/'evidence/GRID_AUDIT.json',json_bytes(out));print(json.dumps({'all_pointwise_gates_pass':out['all_pointwise_gates_pass'],'failed':{str(x['R']):x['failed_gates'] for x in rows if not x['pass']}}))
if __name__=='__main__':main()
