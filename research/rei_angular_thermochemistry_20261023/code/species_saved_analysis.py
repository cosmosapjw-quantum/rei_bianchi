"""Species-resolved differences from saved arrays only; no model import/IVP."""
from pathlib import Path
import json
import os
import numpy as np

BASE=Path(__file__).resolve().parents[1]
R=Path(os.environ.get('ANGTHERM01_RESULTS_DIR',str(BASE/'results'))).resolve()
NAMES={3:'grid044_M4_tight',8:'grid044_M8_tight',9:'grid044_M16_tight',10:'grid044_M4_mean_tight'}
LABELS=['HI','HII','HeI','HeII','HeIII','LiI','LiII','LiIII','LiIV']


def calculate(histories):
    result={'scope':'Saved-array-only native electronic-fraction differences; no IVPs',
            'fraction_labels':LABELS,'comparisons':{}}
    for a,b,name in [(3,10,'directional_M4_minus_mean_M4'),(9,10,'directional_M16_minus_mean_M4'),
                      (3,8,'angular_M4_minus_M8'),(8,9,'angular_M8_minus_M16')]:
        first,second=histories[a],histories[b]
        delta=first['fractions']-second['fractions']
        item={}
        for element,lo,hi in [('H',0,2),('He',2,5),('Li',5,9)]:
            view=delta[lo:hi]
            charge_i,time_i=np.unravel_index(np.argmax(abs(view)),view.shape)
            charge_i+=lo
            item[element]={'max_absolute_fraction_difference':float(np.max(abs(view))),
                 'at_eta':float(first['eta'][time_i]),'at_state':LABELS[charge_i],
                 'first_fraction_at_max':float(first['fractions'][charge_i,time_i]),
                 'second_fraction_at_max':float(second['fractions'][charge_i,time_i]),
                 'per_charge_max_abs':{LABELS[i]:float(np.max(abs(delta[i]))) for i in range(lo,hi)},
                 'first_endpoint_fractions':first['fractions'][lo:hi,-1].tolist(),
                 'second_endpoint_fractions':second['fractions'][lo:hi,-1].tolist(),
                 'endpoint_signed_differences':delta[lo:hi,-1].tolist()}
        result['comparisons'][name]=item
    result['interpretation']={
        'Li_signal':'Li native charge-state fractions show a resolved directional-versus-mean signal although their contribution to total electron count is suppressed by the trace Li abundance5.0001e-10/Href.',
        'angular_boundary':'M4/M8/M16 Li differences do not establish convergence at the2e-7 finite-oracle implementation-agreement tolerance. That tolerance tests representations of the same finite angular system; it is not an angular-continuum error bound.',
        'ratio_boundary':'Successive-difference logarithmic ratios are not demonstrated asymptotic orders; T/ne/tauT differences are at numerical noise level.'}
    return result


def main():
    histories={i:np.load(R/(name+'.npz'),allow_pickle=False) for i,name in NAMES.items()}
    result=calculate(histories)
    (R/'species_analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    path=R/'analysis_summary.json'
    if path.exists():
        summary=json.loads(path.read_text());summary['species_resolved']=result
        path.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':
    main()
