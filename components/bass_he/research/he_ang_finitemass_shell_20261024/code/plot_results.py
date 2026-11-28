"""Render saved analysis only; no shell, reference or quadrature import."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]


def main():
    source=UNIT/'results/ANALYSIS.json';raw=source.read_bytes();data=json.loads(raw)
    if data['status']!='PASS':raise RuntimeError('plot requires preserved passing analysis')
    out=UNIT/'results/figures';out.mkdir(parents=True,exist_ok=True)
    if (out/'FINITEMASS_SHELL.png').exists():raise RuntimeError('preserve existing figure; no automatic rerender')
    plt.rcParams.update({'font.size':9,'axes.titlesize':11})
    fig,axes=plt.subplots(1,2,figsize=(11,4.9))
    grid=data['fold']['plot_grid'];theta=[r['theta_deg'] for r in grid]
    axes[0].plot(theta,[r['p_minus'] for r in grid],label=r'$p_-$',color='#157f88',linewidth=2)
    axes[0].plot(theta,[r['p_plus'] for r in grid],label=r'$p_+$',color='#a43e62',linewidth=2)
    axes[0].axvline(data['fold']['theta_critical_deg'],color='0.3',linestyle=':',label='fold boundary')
    axes[0].set(title='Synthetic conditional sphere: both radial branches',
                xlabel=r'Lab ray angle $\theta_B$ (degrees)',ylabel='Positive radial momentum (electron a.u.)',xlim=(0,70))
    axes[0].legend(frameon=False,loc='upper right');axes[0].grid(alpha=.2)
    colors={20:'#157f88',54.4:'#a43e62',413.6:'#7060a8'}
    for curve in data['volume_ratio_curves']:
        label=f"{curve['nominal_eV']:g} eV, "+('B=0.5' if curve['binding_mode']=='fixed0.5' else r'$B=\mu/2$')
        axes[1].semilogx([r['M'] for r in curve['rows']],
                         [r['ratio_to_Bhalf_infinite_mass'] for r in curve['rows']],
                         color=colors[curve['nominal_eV']],linestyle='-' if curve['binding_mode']=='fixed0.5' else '--',label=label)
    axes[1].axhline(1,color='0.5',linewidth=.8,linestyle=':')
    axes[1].set(title='Labelled kinematic phase-space volume',xlabel=r'Nucleus/electron mass ratio $M$',
                ylabel=r'$\Phi_M/\Phi_{\infty,B=0.5}$')
    axes[1].legend(frameon=False,fontsize=8,loc='lower right');axes[1].grid(alpha=.2)
    fig.subplots_adjust(left=.075,right=.985,top=.88,bottom=.27,wspace=.28)
    fig.suptitle('Finite-mass breakup shell: projection fold and volume limit',y=.98,fontsize=13)
    fig.text(.075,.16,'Left: M=1, E0=1, B=0.5, pA=P/4 is a synthetic stress fixture; both positive roots are retained.',fontsize=9)
    fig.text(.075,.115,'Right: nominal U=27.2 eV; fixed B=0.5 and reduced-mass binding are separate model inputs.',fontsize=9)
    fig.text(.075,.07,'Constant weight W=1: kinematic measure only. No amplitude, flux, spin/count factors or event cross section.',fontsize=9)
    outputs={}
    for ext in ('png','svg'):
        path=out/('FINITEMASS_SHELL.'+ext);fig.savefig(path,dpi=160)
        b=path.read_bytes();outputs[path.name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    plt.close(fig)
    (out/'PLOT_RECEIPT.json').write_text(json.dumps({'source':'results/ANALYSIS.json',
        'source_sha256':hashlib.sha256(raw).hexdigest(),'saved_output_only':True,
        'science_recomputation':0,'outputs':outputs},indent=2)+'\n')
    print(json.dumps({'status':'RENDERED_PENDING_INDEPENDENT_VISUAL_REVIEW','outputs':outputs}))


if __name__=='__main__':main()
