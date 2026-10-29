#!/usr/bin/env python3
"""Read-only saved-array onset audit. No IVP, rendering, or input mutation."""
import argparse,csv,json,math
from pathlib import Path

def audit(data,old):
    x=data['t_myr']; ts=data['t_s']; z=[21*math.exp(-v)-1 for v in data['eta']]
    assert len(x)==361 and len(ts)==361
    overview=next(f for f in old['figures'] if f['stem']=='01_all17_ON_refined')
    multipliers=[1e22,1,1,1e4,1e4,1e18,1e18,1e4,1e4,1e4,10,10,10,1e9,1e9,1e9,1e9]
    rows=[]
    for case,c in data['cases'].items():
        assert len(c['physical'])==23
        for i,y in enumerate(c['physical'][:17]):
            assert len(y)==len(ts)
            p=next((j for j,v in enumerate(y) if ts[j]>0 and v>0),None)
            visible=next((j for j,v in enumerate(y) if overview['xlim'][0]<=x[j]<=overview['xlim'][1] and overview['ylim'][0]<=v*multipliers[i]<=overview['ylim'][1]),None)
            below=[j for j,v in enumerate(y) if ts[j]>0 and 0<v*multipliers[i]<overview['ylim'][0]]
            rows.append(dict(case=case,state=data['labels'][i],initial_value=y[0],initial_zero=y[0]==0,first_positive_index=p,first_positive_t_s=ts[p] if p is not None else None,first_positive_z=z[p] if p is not None else None,old_first_visible_index=visible,old_first_visible_t_s=ts[visible] if visible is not None else None,positive_below_old_window=len(below),cause=('initial zero; ' if y[0]==0 else 'positive initial value; ')+('positive saved samples below old y window' if below else 'no positive samples below old y window')))
    return {'rows':rows,'clock_samples':len(ts),'ON_refined_initial_zero_count':sum(r['initial_zero'] for r in rows if r['case']=='ON_refined'),'first_positive_saved_time_s':ts[1],'first_positive_saved_redshift':z[1],'raw_arrays_unchanged':True}

def main():
    p=argparse.ArgumentParser();p.add_argument('data');p.add_argument('old_metadata');p.add_argument('out');a=p.parse_args();o=Path(a.out);o.mkdir(parents=True,exist_ok=True)
    result=audit(json.loads(Path(a.data).read_text()),json.loads(Path(a.old_metadata).read_text()))
    (o/'START_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    with (o/'start_audit.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=result['rows'][0]);w.writeheader();w.writerows(result['rows'])
if __name__=='__main__':main()
