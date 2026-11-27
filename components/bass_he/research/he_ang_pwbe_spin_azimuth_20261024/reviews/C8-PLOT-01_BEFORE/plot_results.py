"""Source-aware saved-output figure only; no scientific kernel import or rerun."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

UNIT=Path(__file__).resolve().parents[1]

def main():
    obj=json.loads((UNIT/'results/AZIMUTH_ANALYSIS.json').read_text());d=obj['diagnostics']
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'svg.hashsalt':'HE-ANG-PWBE-SPIN-AZIMUTH'})
    fig,axes=plt.subplots(1,3,figsize=(15,5.1))
    ax=axes[0];p=np.array(d['G4_phi'])/np.pi
    ax.plot(p,d['G4_pdf'],color='#0072B2',label='Closed PWBE conditional PDF')
    ax.plot(p[::32],np.array(d['G4_raw_source_pdf'])[::32],'.',color='#D55E00',label='Independent source amplitudes')
    ax.set(xlabel=r'Relative azimuth $\phi/\pi$',ylabel=r'$p(\phi\mid G4)$ [rad$^{-1}$]',title='G4: conditional azimuth')
    ax.legend(loc='upper right',fontsize=8,frameon=False)
    # Error evidence is confined to the upper-left inset, away from the pi peak.
    ins=ax.inset_axes([.09,.48,.35,.30]);rows=obj['fixtures'][3]['levels']
    errs=[max(r['Kbar_relative_error'],np.finfo(float).tiny) for r in rows]
    ins.loglog([r['N'] for r in rows],errs,'o-',color='#009E73',markersize=3)
    ins.axhline(1e-10,color='.35',ls='--',lw=.8);ins.set_title('G4 trapezoid error',fontsize=7)
    ins.set_xlabel('N',fontsize=7);ins.tick_params(labelsize=6)
    ax=axes[1];heat=np.array(d['heat_Kbar']);mus=d['heat_mu']
    im=ax.imshow(heat,origin='lower',extent=[mus[0],mus[-1],mus[0],mus[-1]],aspect='auto',
                 cmap='viridis',norm=LogNorm(vmin=float(heat.min()),vmax=float(heat.max())))
    ax.set(xlabel=r'$\mu_A$',ylabel=r'$\mu_B$',title=r'Pointwise $\overline K$: $E_0=100, E_B=40$')
    cb=fig.colorbar(im,ax=ax,fraction=.047,pad=.035);cb.set_label(r'$a_0^2/E_h$ per sr$^2$',fontsize=9)
    ax=axes[2];e=np.array(d['equal_phi'])/np.pi;scale=max(d['equal_K'])
    ax.plot(e,np.array(d['equal_weighted_singlet'])/scale,color='#0072B2',label=r'$\frac14 |D+X|^2$ (scaled TDCS)')
    ax.plot(e,np.array(d['equal_weighted_triplet'])/scale,color='#D55E00',ls='--',label=r'$\frac34 |D-X|^2=0$')
    ax.set(xlabel=r'Relative azimuth $\phi/\pi$',ylabel='Weighted channel / max unpolarized TDCS',title='G5: equal-share triplet node')
    ax.legend(loc='upper right',fontsize=8,frameon=False)
    for ax in axes:ax.grid(alpha=.15)
    fig.suptitle('Exact-swapped fixed-center PWBE model — analytic density and finite azimuth checks',y=.98,fontsize=13)
    fig.text(.5,.035,'Energies in Hartree. Source amplitudes: FIAS-R-39 (1978), Eqs 19–20; unpolarized spin trace independently derived.\n'
             'G4: q=0 at phi=pi. G5: E0=100, EB=49.75, muA=muB=0.5. No source-table fit or global angle/energy integral.',
             ha='center',va='bottom',fontsize=9)
    fig.subplots_adjust(left=.065,right=.965,bottom=.23,top=.84,wspace=.42)
    out=UNIT/'results/figures';out.mkdir(parents=True,exist_ok=True)
    for suffix in ['png','svg']:
        fig.savefig(out/('PWBE_AZIMUTH.'+suffix),dpi=160,metadata={'Creator':'HE-ANG-PWBE-SPIN-AZIMUTH'} if suffix=='svg' else None)
    plt.close(fig)
    (out/'PLOT_RECEIPT.json').write_text(json.dumps({'source':'results/AZIMUTH_ANALYSIS.json','scientific_recalculation':False,
        'Matplotlib':matplotlib.__version__,'NumPy':np.__version__,'panels':3,'visual_review':'PENDING_ACTUAL_VIEW'},indent=2)+'\n')
    print('Saved PWBE_AZIMUTH.png and PWBE_AZIMUTH.svg; visual review pending')


if __name__=='__main__':main()
