"""Validate exact original author data, cross-check independent source files, emit Rust.

No coefficients are fitted here. Fixed-width ASCII parsing follows the original
description files; cfit.f and phfit2.f are independently parsed for identity checks.
"""
from pathlib import Path
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
SELECTED = {3, 6, 7, 8}
SHA = {
    'photo.dat':'a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389',
    'cfit.dat':'470ea3078c64159eece6a469314dde2356e2d6ccaf618f4eaecb46649d61a5cd',
    'phfit2.f':'8df982535a4a2b952e33ca2ffb6d81600e156d7373fbf547a0c0170c1cecc296',
    'cfit.f':'7fe7d78c25166084041bea58bb55c2fcc6ad724fba8432c167cf044e6eb1bcc1',
    'rec_table1.dat':'2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091',
}

def ci_rows(text):
    out = {}
    for line in text.splitlines():
        key = int(line[6:8]), int(line[9:11])
        values = [float(line[a:b]) for a,b in [(12,19),(20,21),(22,31),(32,38),(39,43),(44,48),(49,53)]]
        assert key not in out and 1 <= key[1] <= key[0] <= 28
        de,p,a,x,k,lo,hi = values
        assert all(math.isfinite(v) for v in values)
        assert de>0 and p in (0,1) and a>0 and x>0 and k>=0 and lo>0 and hi*1000>lo
        out[key] = values
    assert len(out)==406
    return out

def parse():
    for name, sha in SHA.items():
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==sha, name
    photo = {}
    for line in (DATA/'photo.dat').read_text().splitlines():
        pieces=line.split()
        key=tuple(map(int,pieces[:2]))
        values=list(map(float,pieces[2:]))
        assert len(values)==9 and key not in photo
        eth,emax,e0,s0,ya,p,yw,y0,y1=values
        assert all(math.isfinite(v) and v>=0 for v in values)
        assert emax>eth>0 and e0>0 and s0>0 and ya>0 and p>0
        photo[key]=values
    assert len(photo)==185
    ci=ci_rows((DATA/'cfit.dat').read_text())
    ci_fortran={}
    for z,n,vs in re.findall(r'DATA\(CF\(I,\s*(\d+),\s*(\d+)\),I=1,5\)/([^/]+)/', (DATA/'cfit.f').read_text(), re.I):
        ci_fortran[int(z),int(n)]=list(map(float,vs.split(',')))
    assert len(ci_fortran)==406
    assert all(ci[key][:5]==vals for key,vals in ci_fortran.items())
    ftext='\n'.join(line[6:] for line in (DATA/'phfit2.f').read_text().splitlines() if not line.startswith('*'))
    photo_fortran={}
    for z,n,vs in re.findall(r'DATA\s*\(PH2\(I,\s*(\d+),\s*(\d+)\),I=1,7\)\s*/([^/]+)/',ftext,re.I):
        photo_fortran[int(z),int(n)]=[float(x) for x in vs.replace('\n','').split(',')]
    for key,values in photo.items():
        assert key in photo_fortran and values[2:]==photo_fortran[key], key
    rr={}
    for line in (DATA/'rec_table1.dat').read_text().splitlines():
        key=int(line[9:11]),int(line[12:14])
        values=[float(line[a:b]) for a,b in [(16,25),(27,33),(35,44),(46,55)]]
        if key[0] in SELECTED:
            assert key not in rr
            a,b,t0,t1=values
            assert a>0 and 0<=b<=1 and t0>0 and t1>0
            rr[key]=values
    assert len(rr)==12
    return photo,ci,rr

def literal(x):
    return repr(float(x))

def main():
    photo,ci,rr=parse()
    keys=sorted((z,n) for z in SELECTED for n in range(z,0,-1))
    assert len(keys)==24
    out=['// Generated from exact pinned original data by generate_catalog.py; do not hand edit.',
         'use super::{CiFit, Ion, IonFit, PhotoFit, RrFit};',
         'pub static IONS: [IonFit; 24] = [']
    records=[]
    for z,n in keys:
        fields=['IonFit {', f'    ion: Ion {{ atomic_number: {z}, electrons: {n} }},',
                '    photo: PhotoFit { coeff: ['+', '.join(map(literal,photo[z,n]))+'] },',
                '    ci: CiFit { coeff: ['+', '.join(map(literal,ci[z,n]))+'] },']
        r=rr.get((z,n))
        fields.append('    rr_toward: '+('Some(RrFit { coeff: ['+', '.join(map(literal,r))+'] })' if r else 'None')+',')
        fields.append('},')
        out.extend(fields)
        records.append({'atomic_number':z,'electrons':n,'charge':z-n,'photo':photo[z,n],'ci':ci[z,n],'rr_toward':r})
    out.append('];')
    src=ROOT/'catalog'/'src'
    src.mkdir(parents=True,exist_ok=True)
    (src/'generated.rs').write_text('\n'.join(out)+'\n')
    (DATA/'selected_coefficients.json').write_text(json.dumps(records,indent=2)+'\n')
    evidence=ROOT/'evidence'
    evidence.mkdir(exist_ok=True)
    result={'status':'PASS','photo_ascii_records':len(photo),'ci_ascii_records':len(ci),
            'ci_fortran_identity_matches':406,'photo_fortran_identity_matches':185,
            'selected_elements':[3,6,7,8],'selected_pi_ci_ion_stages':24,'selected_rr_toward_stages':12,
            'source_sha256':SHA,
            'recombination_label_semantics':'N is the electron count AFTER capture; coefficient is for parent N-1 electrons -> N.'}
    (evidence/'PARSER_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
