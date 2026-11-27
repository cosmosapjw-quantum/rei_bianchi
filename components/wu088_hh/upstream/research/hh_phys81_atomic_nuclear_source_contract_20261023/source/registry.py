"""Bind literal source bytes to admitted finite operators; no hidden defaults."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
from finite_ci import FiniteWindowCI, A0_M

ROOT=Path(__file__).resolve().parents[1]

def load_rates():
    meta=json.loads((ROOT/'source_data/ADMITTED_FINITE_CI_REGISTRY.json').read_text())
    path=ROOT/'source_data'/meta['literal_csv'];blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=meta['literal_csv_sha256']:raise ValueError('LITERAL_CSV_PIN_MISMATCH')
    if meta['status']!='ADMITTED_EXPLICIT_FINITE_MODEL_ONLY':raise ValueError('FINITE_ADMISSION_REQUIRED')
    rows=list(csv.DictReader(blob.decode('utf-8').splitlines()));models=[]
    for item in meta['source_curves']:
        name=item['project_label'];rr=[r for r in rows if r['project_nuclide_label']==name]
        units={r['cross_section_unit'] for r in rr}
        if units=={'cm^2'}:factor=1.
        elif name=='H1' and units=={'a0^2'}:factor=(100*A0_M)**2
        else:raise ValueError('SOURCE_UNIT_MISMATCH:'+name)
        e=np.array([float(r['incident_energy_eV_literal']) for r in rr]);s=np.array([float(r['cross_section_literal'])*factor for r in rr])
        lower,upper=map(float,item['allowed_window_eV'])
        identity='literal-csv:'+meta['literal_csv_sha256']+';target:'+name+';chemical:'+item['chemical_source_sha256']
        models.append(FiniteWindowCI(name,e,s,identity,float(item['chemical_I_eV']),lower,upper))
    if tuple(m.species for m in models)!=('H1','He4','Li7'):raise ValueError('SOURCE_SPECIES_ORDER_MISMATCH')
    return tuple(models)
