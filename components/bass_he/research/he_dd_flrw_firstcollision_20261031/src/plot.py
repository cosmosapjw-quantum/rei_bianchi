import csv,pathlib,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams["svg.hashsalt"] = "BASS_HE_PR132_SCOPED_FIRST_COLLISION"
R=pathlib.Path(__file__).resolve().parents[1]
def rd(f):
    with (R/'data'/f).open() as h:return [{k:(float(v) if v else None) for k,v in row.items() if k not in ('frame','sigma_dd_kind','BH_kind','KN_kind','source_kind','terminal_reason','BH_model','KN_model','dd_model')} for row in csv.DictReader(h)]
rows=rd('COSMIC_FIRST_COLLISION_18.csv')
for key,name,units in [('P_dd_first','DIRECT_DD_FIRST_EVENT','per injected photon'),('P_BW_first','BREIT_WHEELER_FIRST_EVENT','per injected photon'),('P_KN_first','KLEIN_NISHINA_FIRST_EVENT','per injected photon'),('P_BH_first','BETHE_HEITLER_FIRST_EVENT','per injected photon')]:
    fig,ax=plt.subplots(figsize=(7.2,4.6));
    for E in [170.,220.,249.]:
        vals=sorted((v for v in rows if v['E_inj_MeV']==E),key=lambda d:d['z_inj'])
        ax.plot([p['z_inj'] for p in vals],[max(1e-34,p[key]) for p in vals],marker='o',label=f'E injection {E:g} MeV')
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Injection redshift z_i');ax.set_ylabel(key+' ('+units+')');ax.grid(alpha=0.25);ax.legend(fontsize=8)
    ax.set_title('FLRW model · first collision only · not cosmic source rate');fig.tight_layout()
    for ext in ('.png','.svg'):fig.savefig(R/'figures'/(name+ext),dpi=165,metadata={'Date':None} if ext=='.svg' else None)
    plt.close(fig)
print('plots: 4 PNG and 4 SVG')
