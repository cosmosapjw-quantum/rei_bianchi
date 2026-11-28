"""Exact column-preserving extraction of user-supplied IAEA EXFOR request 10461.

DO NOT infer reaction meaning from source filename. Dataset provenance codes and
column-specific units are authoritative. The numeric catalog includes measurements,
curve digitizations, derived quantities, and repeated publication copies, which are
NOT all independent observations.
"""
from __future__ import annotations
from pathlib import Path
import re, math, csv, hashlib

DATASET_RE = re.compile(r'^#DATASET\s+([^\n]+)\n(.*?)(?=^#DATASET|\Z)',re.M|re.S)
PRIMARY_IDS={
 'M0475003':'exclusive_dd_total', 'M0484003':'exclusive_pT_total',
 'M0520002':'inclusive_total_absorption','M0546002':'duplicate_inclusive_total_absorption',
 'M0384002':'exclusive_2p2n_total','G4081002':'polarization_asymmetry_pT',
 'L0138002':'neutral_pion_production_total', 'M0999002':'three_body_npD_energy_bin',
 'M0999003':'derived_low_energy_absorption',
}

def checksum(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def get_datasets(text:str):
    out={}
    for match in DATASET_RE.finditer(text):
        id=match.group(1).strip(); lines=match.group(2).splitlines()
        meta={}
        for line in lines:
            for key in ('#REACTION','#YEAR','#AUTHOR1','#X4REF1','#REFERENCE1','#STATUS'):
                if line.startswith(key):meta[key[1:].lower()]=line[len(key):].strip()
        h=next((i for i,x in enumerate(lines) if x.startswith('!') and not x.startswith('!Y.')),None)
        d=next((i for i,x in enumerate(lines) if re.match(r'^#DATA\s+\d+',x)),None)
        if h is None or d is None or d<h:raise ValueError(f'{id}: malformed header/data')
        names=lines[h].split()[0:]
        units=lines[h+1].split()
        if not names[0].startswith('!'):raise ValueError('not an EXFOR header')
        names=[names[0].lstrip('!')]+names[1:]
        units=[units[0].lstrip('!')]+units[1:]
        # Data numeric rows start directly after #DATA; comment/legend begins at #ENDDATA
        width=int(lines[d].split()[3]);j=d+1
        numeric=[]
        while j<len(lines) and not lines[j].startswith('#ENDDATA'):
            li=lines[j].strip()
            if li:
                cols=[lines[j][k*width:(k+1)*width].strip() for k in range(len(names))]
                numeric.append([float(x) if x else None for x in cols])
            j+=1
        expected=int(lines[d].split()[1]); expected_cols=int(lines[d].split()[2]);
        if expected!=len(numeric) or expected_cols!=len(names):raise ValueError(f'{id}: count mismatch {expected},{len(numeric)}, {expected_cols},{len(names)}')
        # headers are allowed DATA and ERR-S / ERR-SYS, which are physically distinct
        out[id]={'id':id,'meta':meta,'names':names,'units':units,'rows':[dict(zip(names,n)) for n in numeric], 'source_role':PRIMARY_IDS.get(id,'other_EXFOR_numeric')}
    if len(out)!=84 or sum(len(x['rows']) for x in out.values())!=2270:
        raise ValueError('locked attached EXFOR count changed')
    return out

def raw_source_metadata(std_text:str, id:str):
    match=re.search(r'^SUBENT\s+'+id+r'[^\n]*\n(.*?)(?=^ENDSUBENT)',std_text,re.M|re.S)
    if not match:raise KeyError(id)
    s=match.group(1)
    return {'status_lines':[line.strip() for line in s.splitlines() if line.startswith(('STATUS','           ','HISTORY')) and ('STATUS' in line or 'CURVE' in line or 'TABLE' in line or 'Corrected' in line)],
            'first_360':s[:360]}

def cross_section_rows(ds, source_id, energy_min=150.,energy_max=250.):
    g=ds[source_id]
    if 'SIG' not in g['meta'].get('reaction',''):
        raise ValueError('source does not supply an absolute cross section')
    names=g['names']; units=g['units']; assert names[0]=='DATA'
    mult={'NB':1,'MICRO-B':1e3,'MB':1e6}
    conv=mult.get(units[0]);
    if conv is None:raise ValueError('not a total cross-section unit')
    ans=[]
    for i,row in enumerate(g['rows']):
        E=row.get('EN');
        if E is None or not (energy_min<=E<=energy_max):continue
        stat=row.get('ERR-S')
        systematic=row.get('ERR-SYS',row.get('ERR-1'))
        # for M0484003 constant 5% EXFOR, M0520002 ERR-SYS is an absolute microbarn error
        is_pt=(source_id=='M0484003')
        if is_pt and g['units'][g['names'].index('ERR-SYS')]!='PER-CENT':raise AssertionError('pT systematic incorrect')
        systematic_nb=(row['DATA']*.05*conv if is_pt else (systematic*conv if systematic is not None else None))
        ans.append({'subentry':source_id,'row_index':i+1,'channel':g['source_role'],
           'E_MeV':E,'sigma_nb':row['DATA']*conv,'stat_nb':stat*conv if stat is not None else None,
           'sys_nb':systematic_nb,'sys_is_explicit':systematic is not None,
           'source_measurement_units':units[0], 'original_value':row['DATA'],
           'status':'measured_point' if source_id!='M0384002' else 'measured_multinucleon_point',
           'original_X4REF':g['meta'].get('x4ref1',''), 'notes':'source_sys5pct_correlated_across_E' if is_pt else ('reported_stat_and_sys' if systematic is not None else 'no_reported_sys_do_not_assume_zero')})
    return ans

def write_csv(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:raise ValueError(f'no rows for {path}')
    keys=list(rows[0]);
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)


def normalized_catalog(ds):
    cat=[]
    for id,g in ds.items():
        for i,row in enumerate(g['rows']):
            cat.append({'subentry':id,'row_index':i+1,'reaction':g['meta'].get('reaction',''),
                'role':g['source_role'], 'authors':g['meta'].get('author1',''),
                'source_ref':g['meta'].get('x4ref1',''), 'units_ordered':'|'.join(g['units']),
                'fields_ordered':'|'.join(g['names']),'values_ordered':'|'.join((format(row[k],'.12g') if row[k] is not None else '') for k in g['names']),
                'energy_point_MeV':row.get('EN'), 'energy_min_MeV':row.get('EN-MIN'), 'energy_max_MeV':row.get('EN-MAX'),
                'numeric_kind':'EXFOR_mixed_measurement_model_derived_duplicate_not_independent'})
    return cat
