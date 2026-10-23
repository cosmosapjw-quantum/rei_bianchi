"""One saved-data-only LiI figure; no scientific model imports or IVPs."""
from pathlib import Path
import json
import os
os.environ['MPLCONFIGDIR']='/tmp/angtherm01_mpl_cache'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parents[1]
R=BASE/'results'


def main():
    paths={4:'grid044_M4_tight',8:'grid044_M8_tight',16:'grid044_M16_tight',0:'grid044_M4_mean_tight'}
    h={n:np.load(R/(name+'.npz'),allow_pickle=False) for n,name in paths.items()}
    spans={}
    for n in [4,16]:
        meta=json.loads((R/(paths[n]+'.json')).read_text())
        times=[c['eta'] for c in meta['crossings'] if c['initial_energy_eV']==10 and c['threshold_eV']==5.392]
        spans[n]=[min(times),max(times)]
    mean_meta=json.loads((R/(paths[0]+'.json')).read_text())
    mean_times=[c['eta'] for c in mean_meta['crossings'] if c['initial_energy_eV']==10 and c['threshold_eV']==5.392]
    mean_cross=mean_times[0]
    eta=h[16]['eta'];li_index=5
    plt.rcParams.update({'font.size':10,'axes.labelsize':10,'legend.fontsize':8.5,'axes.grid':True,'grid.alpha':.22,'savefig.dpi':180})
    fig,ax=plt.subplots(2,1,figsize=(3.6,6.6),sharex=True,layout='constrained')
    ax[0].plot(eta,h[16]['fractions'][li_index],label='Directional M16, tight')
    ax[0].plot(eta,h[0]['fractions'][li_index],label='Matched mean-redshift, tight')
    ax[0].axvspan(*spans[16],color='0.85',alpha=.6)
    ax[0].axvline(mean_cross,color='k',ls='--',lw=.8)
    ax[0].text(.02,.97,'10 eV → Li I threshold\nM16 rays:0.4568–0.7280\nmean:0.6177',transform=ax[0].transAxes,va='top',fontsize=8.5,
               bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=2))
    ax[0].legend(loc='lower center',bbox_to_anchor=(.5,1.03))
    ax[0].set_ylabel('Neutral Li fraction')
    for a,b in [(4,8),(8,16)]:
        difference=abs(h[a]['fractions'][li_index]-h[b]['fractions'][li_index])
        ax[1].plot(eta,np.ma.masked_equal(difference,0),label=f'|M{a} − M{b}|')
    ax[1].set(yscale='log',ylabel='Li I angular fraction difference',xlabel=r'$\eta=\ln(a/a_i)$')
    ax[1].legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=2)
    fig.suptitle('Li I threshold signal, grid044\nSame H/nHref; prescribed geometry\nFinite signal and angular error separated')
    fig.savefig(BASE/'figures/07_lithium_threshold.png',bbox_inches='tight')
    plt.close(fig)
    caption={'figure':'07_lithium_threshold.png','new_IVPs':0,'LiI_fraction_row_index':li_index,
       'source_arrays':paths,'directional_threshold_spans_eta':spans,'mean_threshold_eta':mean_cross,
       'caption':'Top: saved-report-grid LiI fractions, directional M16 versus a matched same-grid044 H/nHref mean-redshift counterfactual. Gray span marks the M16 10eV cohort LiI5.392eV crossing range; dashed line marks the mean crossing. Bottom: native LiI fraction angular-refinement differences at common reporting times; exact zeros are omitted only on this log display. No Li angular convergence to the finite-oracle agreement tolerance is claimed. The mean case is prescribed counterfactual geometry, not a physical FLRW solution.'}
    (R/'lithium_figure_caption.json').write_text(json.dumps(caption,indent=2)+'\n')


if __name__=='__main__':
    main()
