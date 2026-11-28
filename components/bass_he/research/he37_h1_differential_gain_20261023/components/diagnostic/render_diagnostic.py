"""Render only the saved HE37 rows; no model import or scientific recompute."""
from pathlib import Path
import datetime,hashlib,json,os,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    with t.open('rb') as f:os.fsync(f.fileno())
    t.replace(p)
def render():
    receipt=P/'plots/RENDER_RECEIPT.json'
    if receipt.exists():raise RuntimeError('Saved render exists; inspect/cache reuse, not unchanged rerender')
    start=time.perf_counter();data=np.genfromtxt(P/'outputs/h1_gain_moments.csv',names=True,delimiter=',');T=data['temperature_K']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,'axes.titlesize':11,
                          'figure.dpi':160,'savefig.dpi':180,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,2,figsize=(11.6,8.0))
    fig.subplots_adjust(left=.09,right=.97,bottom=.20,top=.86,wspace=.28,hspace=.45)
    navy='#143d63';orange='#c66a1b';teal='#118477';grey='#536575'
    ax=axs[0,0];ax.loglog(T,data['alpha_native_m3_s'],color=navy,lw=2.2,label='Le–Cambier source model')
    ax.loglog(T,data['alpha_CCC_reused_finite_m3_s'],color=orange,lw=1.8,ls='--',label='CCC finite table · saved HE36')
    ax.set_title('(a) Two separately defined event-rate kernels',loc='left');ax.set_ylabel(r'$\alpha\;[\mathrm{m^3\,s^{-1}}]$');ax.legend(loc='lower right',frameon=False,fontsize=9)
    ax=axs[0,1];ax.semilogx(T,data['native_over_CCC_rate'],color=navy,lw=2.2)
    ax.axhline(1,color=grey,lw=1,ls=':');ax.set_title('(b) Source-model dependence',loc='left');ax.set_ylabel(r'$\alpha_{\rm LC}/\alpha_{\rm CCC,finite}$')
    ax.text(.04,.08,'Different thresholds and energy support;\ncomparison is not a calibration error bar.',transform=ax.transAxes,va='bottom',fontsize=8.6,color=grey)
    ax=axs[1,0];ax.semilogx(T,data['incoming_mean_energy_eV'],color=navy,lw=2.2,label='Incoming removal ⟨E⟩')
    ax.semilogx(T,data['outgoing_returned_energy_eV'],color=teal,lw=2,label='Returned by two electrons ⟨E⟩ − I')
    ax.semilogx(T,data['net_cooling_energy_eV'],color=orange,lw=1.8,ls='--',label='Net cooling I = 13.6 eV')
    ax.set_title('(c) Energy per ionization event',loc='left');ax.set_ylabel('Energy [eV]');ax.legend(loc='upper left',frameon=False,fontsize=8.5)
    ax=axs[1,1];ax.fill_between(T,data['nu_lower_over_nH_alpha'],data['nu_upper_over_nH_alpha'],color=teal,alpha=.18,label='Positive-angular model envelope')
    ax.loglog(T,data['kappa2_over_alpha'],color=navy,lw=2.2,label='Isotropic source model')
    ax.set_title('(d) Electron STF damping per event rate',loc='left');ax.set_ylabel(r'$\nu/(n_H\alpha)$');ax.legend(loc='upper right',frameon=False,fontsize=8.5)
    for ax in axs.flat:
        ax.set_xlabel('Electron temperature [K]');ax.set_xlim(2000,200000);ax.grid(True,which='major',color='#d8e1e8',lw=.6);ax.set_axisbelow(True)
        ax.set_xticks([2000,20000,200000],labels=['2,000','20,000','200,000'])
    fig.suptitle('H1 ionization: differential gain closes the net pressure source',x=.09,ha='left',y=.965,fontsize=16,weight='bold')
    fig.text(.09,.91,'Le–Cambier Eq.85 + isotropic outgoing directions  •  heavy-target limit  •  infinitesimal electron Grad STF',fontsize=10,color=grey)
    fig.text(.09,.05,'129 saved temperatures. New source-native model moments; CCC values are reused without recomputation.\nThe angular envelope spans positive recoil-free models at fixed LC cross section; it is not a measured H1 uncertainty.',fontsize=9,color=grey,linespacing=1.5)
    paths=[]
    for ext in ('png','svg'):
        path=P/'plots'/('h1_gain_diagnostic.'+ext);fig.savefig(path,facecolor='white',metadata={'Creator':'HE37 source-model diagnostic'} if ext=='svg' else {'Software':'HE37 source-model diagnostic'});paths.append(path)
    plt.close(fig)
    result={'schema':'he37.saved_rows_render.v1','status':'RENDERED','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'command':'MPLCONFIGDIR=/tmp/he37_diagnostic/mplcache python render_diagnostic.py','exit_code':0,'model_evaluations':0,'render_attempt':2,
        'affected_change':'Only margins/footer/annotation placement; prior render preserved at plots/attempts/render_001',
        'input_csv_sha256':sha(P/'outputs/h1_gain_moments.csv'),'script_sha256':sha(__file__),'matplotlib':matplotlib.__version__,
        'elapsed_seconds':time.perf_counter()-start,'payloads':[{'path':str(p.relative_to(P)),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths]}
    save(receipt,result);print(json.dumps(result))
if __name__=='__main__':render()
