"""Independent high-precision (mpmath) photo-rate & energy ledger oracle.

References only original pinned JSON data, no source17 function/rate_response.
This verifies formulas and 7 saved populations at fixed snapshot, no IVP.
"""
import csv
import json
from pathlib import Path
import mpmath as mp
from physical_data import source_hashes, ROOT


def run():
    source_hashes()
    p=json.loads((ROOT/'research/rei_uvb_six_moment_response_20261029/source/PUCHWEIN2019_13_ROW_PROJECTION.json').read_text())
    s=json.loads((ROOT/'research/rei_uvb_saved_state_source_tangent_20261029/source/ON_REFINED_7_SAVED_ROWS.json').read_text())
    bb=json.loads((ROOT/'research/rei_uvb_six_moment_response_20261029/source/FROZEN_BB13_SUPPORT_INPUT.json').read_text())
    import numpy as np
    from physical_data import s as pr262
    port,d,_,rows,g=pr262.load_parent()
    a0=g['a0']
    with (ROOT/'results/REI_FROZEN_7_EPOCH_PHYSICAL_SOURCE.csv').open() as f: out=list(csv.DictReader(f))
    mp.mp.dps=85
    table=[[mp.mpf(str(v)) for v in row] for row in p['rows']]
    I=[1,3,5,7,8,10,11]
    ch=[0,0,0,1,2,1,2]
    threshold=[mp.mpf(t) for t in ('13.6','13.6','13.6','24.6','54.4','24.6','54.4')]
    worst=mp.mpf('0');worst_abs=mp.mpf('0');cases=0
    for idx,rec in enumerate(s['rows']):
        z=mp.mpf(str(rec['z']))
        j=next(k for k in range(len(table)-1) if table[k][0]<=z<=table[k+1][0])
        frac=(z-table[j][0])/(table[j+1][0]-table[j][0])
        moments=[mp.exp((1-frac)*mp.log(table[j][i])+frac*mp.log(table[j+1][i])) for i in range(1,7)]
        pop=[mp.mpf(str(rec['y'][i])) for i in I]
        for scenario in ('P19_D1_fiducial','P19_D1_BB13_GLs_nominal'):
            factor=mp.mpf(1) if scenario=='P19_D1_fiducial' else mp.power(10,mp.mpf(str(a0[0]))+mp.mpf(str(a0[1]))*(z-mp.mpf('3.6')))
            events=sum(pop[k]*moments[2*ch[k]]*factor for k in range(7))
            heating=sum(pop[k]*moments[2*ch[k]+1]*factor for k in range(7))
            storage=sum(pop[k]*moments[2*ch[k]]*factor*threshold[k] for k in range(7))
            absorbed=heating+storage
            obs=next(v for v in out if v['scenario']==scenario and int(v['saved_index'])==idx)
            for calc,key in [(events,'photoelectrons_created_per_Href_s'),(heating,'photoheat_eV_per_Href_s'),(storage,'ionization_storage_eV_per_Href_s'),(absorbed,'absorbed_photon_eV_per_Href_s')]:
                reported=mp.mpf(obs[key]);abs_err=abs(calc-reported);rel=abs_err/(abs(calc)+mp.mpf('1e-100'))
                worst=max(worst,rel);worst_abs=max(worst_abs,abs_err);cases+=1
    o={'oracle':'independent mpmath85 raw projected P19 source knots and saved REI 7 rows',
       'cases':cases,'max_relative_error':mp.nstr(worst,22),
       'max_absolute_error':mp.nstr(worst_abs,22),
       'dps':85,'new_ivps':0,'pass_under_3e-14':bool(worst<mp.mpf('3e-14'))}
    (ROOT/'results/INDEPENDENT_REFERENCE.json').write_text(json.dumps(o,indent=2)+'\n')
    if not o['pass_under_3e-14']:raise AssertionError(o)
    print(json.dumps(o,indent=2));return o

if __name__=='__main__':run()
