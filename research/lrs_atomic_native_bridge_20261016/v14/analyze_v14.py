#!/usr/bin/env python3
"""Inspect only actually produced native histories, not assumed successful runs."""
import argparse,csv,json,math
from pathlib import Path
MODES=('be_control','common_combined','physical_midpoint','physical_gl2','source_off','source_off_midpoint','source_off_gl2')

def analyze(path):
    from birth_record_guard import validate_birth_records
    validate_birth_records(path)
    from event_energy_audit import audit_row
    rows=list(csv.DictReader(Path(path).open(newline='')))
    if not rows:raise ValueError('empty history')
    groups={}
    for r in rows:
        for k,v in r.items():
            if k!='mode' and (v is None or not math.isfinite(float(v))):raise ValueError('nonfinite/missing '+k)
        if r['mode'] not in MODES:raise ValueError('unrecognized mode')
        groups.setdefault((r['mode'],int(r['N'])),[]).append(r)
        if abs(float(r['energy_residual_eV_H']))>1e-9:raise ValueError('energy residual')
        if abs(float(r['photon_residual_H']))>1e-16:raise ValueError('photon residual')
        if min(float(r[k]) for k in ['HII','HeII','HeIII','photons_per_H'])<0:raise ValueError('negative physical state')
        if float(r['HII'])>1 or float(r['HeII'])+float(r['HeIII'])>1:raise ValueError('nuclear simplex')
        # Native global event ledgers make each available nuclear/electron
        # equation inspectable in this new binary. Fractions use per-He for He.
        Y=.2454/(4*(1-.2454))
        net=[float(r['photo_'+j])+float(r['CI_'+j])-float(r['RR_'+ion]) for j,ion in zip(['HI','HeI','HeII'],['HII','HeII','HeIII'])]
        net[1]-=float(r['DR_HeII'])
        resid=[float(r['HII'])-.075-net[0],Y*(float(r['HeII'])-.12)-(net[1]-net[2]),Y*(float(r['HeIII'])-.03)-net[2]]
        r['_max_species_residual']=max(map(abs,resid))
        if r['_max_species_residual']>1e-9:raise ValueError('species events')
        r['_independent_ledger']=audit_row(r)
    end={}
    birth_path=Path(str(path)+'.births.csv')
    if not birth_path.exists():raise ValueError('missing actual birth records')
    birth_rows=list(csv.DictReader(birth_path.open(newline='')))
    born={}
    for row in birth_rows:
        key=(row['mode'],int(row['N']))
        if key not in groups:raise ValueError('orphan birth')
        step=int(row['step']); dx=float(groups[key][0]['Xend'])/key[1]
        x=math.log(float(row['a'])*21.)
        if x<(step-1)*dx-1e-14 or x>step*dx+1e-14:raise ValueError('noncausal birth')
        if float(row['added_N'])<0 or float(row['added_U'])<0:raise ValueError('negative birth')
        total=born.setdefault(key,[0.,0.,0]);total[0]+=float(row['added_N']);total[1]+=float(row['added_U']);total[2]+=1
    for key,g in groups.items():
        n=key[1]
        if len(g)!=n or [int(v['step']) for v in g]!=list(range(1,n+1)):raise ValueError('incomplete history '+str(key))
        end[key]=g[-1]
        record=born.get(key,[0.,0.,0]);mode=key[0]
        expected_births=n*(2 if mode in ('common_combined','physical_gl2','source_off_gl2') else (0 if mode=='source_off' else 1))
        if record[2]!=expected_births:raise ValueError('birth record count '+str(key))
        for index,column in enumerate(('source_N','source_U')):
            target=float(g[-1][column]); floor=1e-24 if index==0 else 1e-22
            if abs(record[index]-target)>max(floor,2e-12*abs(target)):raise ValueError('birth ledger mismatch '+column)

    comparisons=[]
    for mode in MODES:
        ns=sorted(n for m,n in end if m==mode)
        if not ns:raise ValueError('missing mode '+mode)
        for n in ns:
            if (mode,2*n) not in end or (mode,4*n) not in end:continue
            for obs in ['T_K','photons_per_H','HII','HeII','HeIII','source_N','source_U']:
                a,b,c=[float(end[mode,m][obs]) for m in (n,2*n,4*n)]
                d1,d2=a-b,b-c;floor=64*math.ulp(max(abs(a),abs(b),abs(c),1e-200))
                p=math.log2(abs(d1/d2)) if min(abs(d1),abs(d2))>floor else None
                comparisons.append({'mode':mode,'N':n,'observable':obs,'delta_N_2N':d1,'delta_2N_4N':d2,
                    'observed_p':p,'sign_change':d1*d2<0,'roundoff_floor':floor})
    return {'file':str(path),'histories':len(groups),'rows':len(rows),'comparisons':comparisons,
            'maximum_energy_residual':max(abs(float(r['energy_residual_eV_H'])) for r in rows),
            'maximum_photon_residual':max(abs(float(r['photon_residual_H'])) for r in rows),
            'maximum_species_event_residual':max(r['_max_species_residual'] for r in rows),
            'independent_ledger_maxima':{k:max(abs(r['_independent_ledger'][k]) for r in rows) for k in rows[0]['_independent_ledger']},
            'claim':'finite native control only; source-on p2 not automatically admitted'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv',nargs='+');p.add_argument('--out',required=True)
    a=p.parse_args();result={'schema':'rei.v14.native.analysis.1','results':[analyze(x) for x in a.csv],
                           'full_source_on_order':'HOLD_REQUIRES_SIGNED_REFINEMENT_AND_INDEPENDENT_REVIEW'}
    Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
