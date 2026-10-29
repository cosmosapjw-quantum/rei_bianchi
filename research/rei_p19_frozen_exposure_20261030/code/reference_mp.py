"""Independent 90-digit mpmath check against source-LF frozen PR271 event CSVs.

Only checks the *chosen* loglinear interpolation integral, not the unknowable
physical between-knot trajectory. No inherited float64 logmean helper imported.
"""
from __future__ import annotations
from pathlib import Path
import csv, io, json, zipfile, hashlib, mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'source_archive/PR271_SOURCE_FULL.zip'
P_SHA='c20b7a776e407c35dff99c32595f394ce0c9426c3469358a8b5d7f2750c68165'
E='results/REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv'
mp.mp.dps=90

def logmean_mp(a,b):
    a=mp.mpf(a);b=mp.mpf(b)
    if a<=0 or b<=0:raise ValueError('nonpositive')
    if a==b:return a
    return (b-a)/(mp.log(b)-mp.log(a))

def run():
    if hashlib.sha256(PARENT.read_bytes()).hexdigest()!=P_SHA:raise ValueError('SOURCE_SHA_MISMATCH')
    with zipfile.ZipFile(PARENT) as z: parent=list(csv.DictReader(io.StringIO(z.read(E).decode('utf8'))))
    data=list(csv.DictReader((ROOT/'results/INTERVAL_84_EVENT_EXPOSURE.csv').open()))
    src={(r['scenario'],int(r['event_index']),r['saved_index']):r for r in parent}
    errors=[]
    for row in data:
        k=int(row['event_index']);i=int(row['interval_index']);scenario=row['scenario'];
        t0=mp.mpf(src[(scenario,k,str(6-i))]['elapsed_proper_s'])
        t1=mp.mpf(src[(scenario,k,str(5-i))]['elapsed_proper_s'])
        dt=t1-t0
        for old,new in [('photoelectrons_created_per_Href_s','loglinear_photoelectrons_per_Href'),('photoheat_eV_per_Href_s','loglinear_photoheat_eV_per_Href')]:
            a=src[(scenario,k,str(6-i))][old];b=src[(scenario,k,str(5-i))][old]
            reference=dt*logmean_mp(a,b)
            actual=mp.mpf(row[new]);rel=abs(actual/reference-1)
            errors.append(rel)
    result={'schema':'REI_P19_EXPOSURE_MP90_INDEPENDENT','cases':len(errors),'mp_dps':90,
            'max_relative_error':str(max(errors)),'pass_lt_3e-14':max(errors)<mp.mpf('3e-14'),
            'authority':'independent mp.mpf positive log-mean from source CSV; not physical integration'}
    (ROOT/'results/MP90_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
