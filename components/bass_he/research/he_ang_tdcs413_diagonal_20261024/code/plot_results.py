"""Two saved-output panels; no kernel import/model evaluation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]


def main():
    r=json.loads((UNIT/'results/ANALYSIS.json').read_text());rows=r['rows'];angles=[float(x['theta_deg']) for x in rows]
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'HEANG_TDCS413_DIAGONAL'})
    fig,axes=plt.subplots(2,1,figsize=(9.5,7),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    ax=axes[0];ax.errorbar(angles,[x['y'] for x in rows],yerr=[x['s'] for x in rows],fmt='o',color='#0072B2',capsize=3,label='13 clear source points and printed one-sigma')
    ax.plot(r['plot_grid']['theta_deg'],r['plot_grid']['predicted'],color='#D55E00',label='Nominal PWBE, minimax common scale')
    ax.set(ylabel='Relative source units',title='H(1s) coplanar equal-energy diagonal: 413.6 eV, 200 + 200 eV')
    ax.legend(loc='upper right',frameon=False,fontsize=9)
    ax.text(.02,.95,f"kappa = {r['fit']['kappa']:.6g}\na = {r['fit']['a']:.6g}\nModel peak = {r['peak']['theta_deg']:.5f} deg",transform=ax.transAxes,va='top',fontsize=9)
    ax=axes[1];ax.axhline(0,color='.4',lw=.8);ax.axhline(r['fit']['kappa'],color='.5',ls='--');ax.axhline(-r['fit']['kappa'],color='.5',ls='--')
    ax.plot(angles,[x['weighted_residual'] for x in rows],'o',color='#009E73')
    ax.set(xlabel='theta_A = theta_B [degree]',ylabel='(a f - y) / s',xlim=(31,61))
    for ax in axes:ax.grid(alpha=.2)
    fig.text(.5,.025,'FIAS-R-39 (June 1978), Table 1: 13 selected points; 45/46/48 deg excluded before model evaluation.\n'
             'Relative azimuth = pi; nominal U = 27.2 eV. The measured 60 deg zero is retained.\n'
             'Printed one-sigma values are numerical weights; covariance is unknown. Relative shape benchmark.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.11,right=.97,bottom=.16,top=.92,hspace=.16)
    out=UNIT/'results/figures';out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/'TDCS413_DIAGONAL.png',dpi=160);fig.savefig(out/'TDCS413_DIAGONAL.svg',metadata={'Creator':'HEANG_TDCS413_DIAGONAL'});plt.close(fig)
    (out/'PLOT_RECEIPT.json').write_text(json.dumps({'source':'results/ANALYSIS.json','scientific_recalculation':False,'Matplotlib':matplotlib.__version__,'visual_review':'PENDING_ACTUAL_VIEW'},indent=2)+'\n')
    print('Saved TDCS413_DIAGONAL.png and.svg; actual visual review pending')


if __name__=='__main__':main()
