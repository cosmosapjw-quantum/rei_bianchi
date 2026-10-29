"""Plot model-source rates and frozen-state per-Href source quantities. No IVPs."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'

def read(name):
    with open(R/name,encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def output():
    p=read('P19_FIDUCIAL_13_KNOT_PHYSICAL_RATES.csv')
    z=np.array([float(r['z']) for r in p]);rates=['Gamma_HI_per_s','Gamma_HeI_per_s','Gamma_HeII_per_s']
    fig,ax=plt.subplots(figsize=(8.2,4.7))
    for name,label in zip(rates,('HI','HeI','HeII')):
        ax.semilogy(z,[float(r[name]) for r in p],marker='o',markersize=3,label=label)
    ax.set_xlabel('Redshift z (P19 selected D1 knots)');ax.set_ylabel('Photoionization rate [s$^{-1}$]')
    ax.set_title('Puchwein 2019 D1: source rates, not a REI trajectory');ax.legend();ax.grid(True,alpha=.2)
    fig.tight_layout();fig.savefig(R/'P19_FIDUCIAL_PHOTO_RATES.png',dpi=180);plt.close(fig)
    f=read('REI_FROZEN_7_EPOCH_PHYSICAL_SOURCE.csv')
    fig,axes=plt.subplots(1,2,figsize=(10.8,4.5))
    metrics=[('photoelectrons_created_per_Href_s','Source photoelectrons / Href / s'),('photoheat_eV_per_Href_s','Photoheat [eV / Href / s]')]
    for ax,(key,title) in zip(axes,metrics):
        for scenario,label in [('P19_D1_fiducial','P19 D1'),('P19_D1_BB13_GLs_nominal','P19 D1 + BB13 GLS')]:
            data=[r for r in f if r['scenario']==scenario]
            ax.semilogy([float(r['saved_z']) for r in data],[float(r[key]) for r in data],'-o',label=label)
        ax.set_xlabel('Saved REI mean redshift');ax.set_ylabel(title);ax.grid(True,alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Frozen-source hybrid: P19 rates × stored REI populations (no IVP)',fontsize=11)
    fig.tight_layout();fig.savefig(R/'REI_FROZEN_PHOTO_ELECTRON_HEAT.png',dpi=180);plt.close(fig)
    ev=read('REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv')
    fid=[r for r in ev if r['scenario']=='P19_D1_fiducial']
    ions=['H1_0','D_0','T_0','He3_0','He3_1','He4_0','He4_1']
    xs=sorted(set(float(r['saved_z']) for r in fid))
    dat=np.array([[float(next(e['photoelectrons_created_per_Href_s'] for e in fid if e['from_state']==ion and float(e['saved_z'])==z)) for ion in ions] for z in xs])
    frac=dat/dat.sum(axis=1,keepdims=True)
    fig,ax=plt.subplots(figsize=(8.5,4.6))
    ax.stackplot(xs,frac.T,labels=ions)
    ax.set_xlabel('Saved mean redshift');ax.set_ylabel('Fraction of photo-electron creation')
    ax.set_ylim(0,1);ax.set_title('Fiducial P19: seven REI event shares at frozen snapshots')
    ax.legend(loc='center left',bbox_to_anchor=(1,0.5),fontsize=8);fig.tight_layout()
    fig.savefig(R/'REI_SEVEN_EVENT_ELECTRON_SHARES.png',dpi=180);plt.close(fig)

if __name__=='__main__':output()
