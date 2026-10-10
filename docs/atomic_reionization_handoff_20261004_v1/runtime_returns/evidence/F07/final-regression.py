import copy, importlib.util, json
from pathlib import Path
from fractions import Fraction
base=Path.cwd(); path=base/'docs/atomic_reionization_handoff_20261004_v1/tools/verify_science_scenario.py'
spec=importlib.util.spec_from_file_location('screen',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=json.loads((base/'configs/rei_fastest_v1/science_scenario_v1.json').read_text())
s=json.loads((base/'configs/rei_fastest_v1/science_scenario_v1.schema.json').read_text())
m.validate(c,s);result=m.screen(c);assert result['status']=='PASS'
checks=1
for name in ['wrong_cutoff','outside_real_guard','zero_grid','fractional_grid','negative_kB','source_below_cutoff']:
 x=copy.deepcopy(c)
 if name=='wrong_cutoff':x['constants']['cross_section_cutoff_ev']=x['constants']['binding_threshold_ev'][:]
 if name=='outside_real_guard':
  x['atomic_model']['fit_implementation_temperature_guard_K']=[1000.,200000.];x['atomic_model']['scenario_temperature_guard_K']=[1000.,160000.];x['initial_state']['temperature_K']=120000.
 if name=='zero_grid':x['spectral']['angular_quadrature']['n_mu'][0]=0
 if name=='fractional_grid':x['spectral']['angular_quadrature']['n_phi'][0]=8.5
 if name=='negative_kB':x['constants']['k_B_erg_K']=-1.380649e-16
 if name=='source_below_cutoff':x['source']['energy_at_birth_ev']=x['initial_state']['photon_energy_ev']=13.599
 try:m.validate(x,s);m.screen(x)
 except ValueError as e:print('REJECT',name,str(e));checks+=1
 else:raise AssertionError('Invalid candidate accepted: '+name)
for n,p in zip(c['spectral']['angular_quadrature']['n_mu'],c['spectral']['angular_quadrature']['n_phi']):
 w=Fraction(1,n*p);assert w>0 and n*p*w==1;checks+=1;print('GRID',n,p,'weight',str(w),'sum1')
for row in result['geometry_screen']:
 assert float(row['HI_Verner_cutoff_crossing_first_possible_s']) < float(row['HI_binding_crossing_first_possible_s']);checks+=1
print('PASS',checks,'preregistration/regression assertions; no histories or physical admission')
