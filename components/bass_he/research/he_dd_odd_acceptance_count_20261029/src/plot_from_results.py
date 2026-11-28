"""Replot conditional odd-acceptance envelopes from pinned exact RESULTS.json.

Figures display illustrative response ratios, NOT experimental calibration.
"""
import argparse
import json
from pathlib import Path
from fractions import Fraction as F
from odd_acceptance_count import odd_leakage_envelope


def render(result_file, output_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data=json.loads(Path(result_file).read_text())
    d2=F(data['contract']['Delta2_MeV2']) if 'contract' in data else F(data['Delta2_MeV2'])
    root=Path(output_dir);root.mkdir(parents=True,exist_ok=True)
    curves={}
    for L,row in data['cases'].items():
        a,u=map(F,row['source_b_outer'])
        ds=[F(i,200) for i in range(41)]
        vals=[odd_leakage_envelope(a,u,(1+d)/(1-d),d2) for d in ds]
        curves[L]={'x':[float(x)*100 for x in ds],
                   'mean':[float(z['mean_energy_offset_squared_max_MeV2'])**.5 for z in vals],
                   'lo':[float(z['conditional_var_lower_MeV2']) for z in vals],
                   'hi':[float(z['conditional_var_upper_MeV2']) for z in vals]}
    fig,ax=plt.subplots(figsize=(7.5,4.6))
    for L,c in curves.items():ax.plot(c['x'],c['mean'],label='L='+L)
    ax.set(xlabel='Hypothetical response-shape delta (%)',
           ylabel='Upper bound on labelled mean energy offset (MeV)',
           title='Arm-labelled selection leakage (not intrinsic birth asymmetry)')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(root/'mean_leakage.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,4.6))
    for L,c in curves.items():
        line=ax.plot(c['x'],c['lo'],label='L='+L+' lower')[0]
        ax.plot(c['x'],c['hi'],ls='--',color=line.get_color(),label='L='+L+' upper')
    ax.set(xlabel='Hypothetical response-shape delta (%)',
           ylabel='Labelled daughter Var(K) (MeV²)',
           title='Conditional detected-sample variance, not physical heat')
    ax.grid(alpha=.2);ax.legend(ncol=2,fontsize=7);fig.tight_layout()
    fig.savefig(root/'variance_bounds.png',dpi=170);plt.close(fig)
    return list(curves)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    root=Path(__file__).resolve().parents[1]
    p.add_argument('--results',default=str(root/'RESULTS.json'))
    p.add_argument('--out-dir',default=str(root/'figures'))
    a=p.parse_args()
    print('rendered cases:',render(a.results,a.out_dir))
