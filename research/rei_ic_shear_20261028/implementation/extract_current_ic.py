"""Mechanical existing-file extraction only; no RHS/test/IVP/plot execution."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np

UNIT=Path(__file__).resolve().parents[1]
ROOT=UNIT.parent
base=ROOT/'rei_fast_selected_20261028'
csvpath=base/'outputs/grid044_M4_nominal_all21_populations.csv'
src=base/'inputs/angtherm_selected/research/rei_angular_thermochemistry_20261023'
labels=['n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2','He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3']
with csvpath.open() as f:
    first=next(csv.DictReader(f))
values={k:float(first['per_Href__'+k]) for k in labels}
hidden={k:float(first['per_Href__'+k]) for k in ['Li6_0','Li6_1','Li6_2','Li6_3']}
raw={}
for name in ['OFF_base','ON_base','ON_refined']:
    with np.load(ROOT/'rei_source_history_20261028/outputs'/(name+'.npz'),allow_pickle=False) as d:
        raw[name]={'t0_s':float(d['t'][0]),'initial_physical23':d['physical'][:,0].tolist(),
                   'solver_scales23':d['scales'].tolist(),'n_saved_samples':int(len(d['t']))}
with np.load(src/'results/grid044_M4_nominal.npz',allow_pickle=False) as d:
    saved={k:float(d[k][0]) for k in ['eta','H','nHref','temperature_K','electron_per_Href','bprime']}
    saved['photon_groups24_per_Href']=d['photon_groups'][:,0].tolist()
with np.load(src/'inputs/background/grid044_history.npz',allow_pickle=False) as d:
    bg={'initial_raw_background':{k:float(d[k][0]) for k in ['eta','H','s','b','nH_ref_cm3']},
        'schema':list(d.files),'saved_nodes':int(len(d['eta']))}
paths=[csvpath,src/'results/grid044_M4_nominal.npz',src/'inputs/background/grid044_history.npz',
       src/'code/angular_model.py',ROOT/'rei_source_history_20261028/implementation/coupled.py',
       ROOT/'rei_external_sources_20261028/implementation/model.py',ROOT/'rei_external_sources_20261028/implementation/config.json']
report={'schema':'REI_CURRENT_INITIAL_VALUES_EXTRACT_V1','baseline_pr':248,
    'baseline_head':'022f2ed85595364f05834d8eb1573434efce92d0',
    'activity':'Mechanical extraction of existing stored values and definitions only; no RHS, coefficient, test, figure or IVP execution',
    'visible_order':labels,'per_Href_visible':values,'per_Href_hidden_prescribed':hidden,
    'fast_particles_per_Href':{'B_n':0.,'B_T':0.},'fast_kinetic_eV_per_Href':{'U_n':0.,'U_T':0.},
    'initial_accumulated_ledgers':{'external_baryons':0.,'free_electrons':0.},'saved_first_epoch':saved,
    'background_input':bg,'stored_cases':raw,
    'input_sha256':{str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    'new_scientific_execution':'NOT_RUN','runtime_model_identity':'UNKNOWN'}
(UNIT/'implementation/CURRENT_INITIAL_VALUES.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({'visible':values,'hidden':hidden,'saved_first_epoch_scalars':{k:v for k,v in saved.items() if not isinstance(v,list)},
                  'background_initial':bg['initial_raw_background']},indent=2))
