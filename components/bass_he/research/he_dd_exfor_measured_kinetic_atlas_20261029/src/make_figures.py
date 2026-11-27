"""Measured EXFOR row markers with fixed-rest-energy kinematic transforms.
No 330 MeV SIG interpolation, no source-model fit, no heat assertion.
"""
from pathlib import Path
from fractions import Fraction
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(results:Path, fig_dir:Path):
    fig_dir.mkdir(parents=True,exist_ok=True)
    with (results/'SIG_ENERGY_WEIGHTED.csv').open() as f: sig=list(csv.DictReader(f))
    with (results/'DA_ENERGY_WEIGHTED.csv').open() as f: da=list(csv.DictReader(f))
    x=[float(Fraction(r['gamma_E_lab_MeV'])) for r in sig]
    y=[float(Fraction(r['SIG_reported_times_pairK_nb_MeV'])) for r in sig]
    e=[float(Fraction(r['ERR_S_times_pairK_nb_MeV'])) for r in sig]
    fig,ax=plt.subplots(figsize=(7,4.5))
    ax.errorbar(x,y,yerr=e,fmt='o',capsize=4,label='EXFOR M0475003: six measured SIG coordinates')
    ax.set(xlabel=r'$E_\gamma$ in stationary $^4$He frame (MeV)',
           ylabel=r'Reported $\sigma(E_\gamma)[E_\gamma-Q]$ (nb MeV)',
           title=r'EXFOR event-kinetic-weighted reported cross section')
    ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(fig_dir/'exfor_SIG_kinetic_weighted.png',dpi=210);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.5))
    for E in (213,258,330):
        sub=[r for r in da if int(Fraction(r['gamma_E_lab_MeV']))==E]
        xs=[float(Fraction(r['theta_d_CM_deg'])) for r in sub]
        ys=[float(Fraction(r['DA_times_pairK_nb_MeV_per_sr'])) for r in sub]
        es=[float(Fraction(r['DA_ERR_S_times_pairK_nb_MeV_per_sr'])) for r in sub]
        ax.errorbar(xs,ys,yerr=es,fmt='o',capsize=3,label=f'M0475002: {E} MeV')
    ax.set(xlabel=r'CM deuteron angle $\theta$ (degrees)',
           ylabel=r'Reported $[d\sigma/d\Omega]_{CM}(E_\gamma-Q)$ (nb MeV / sr)',
           title='Measured angular rows, pair-kinetic weighted')
    ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(fig_dir/'exfor_DA_kinetic_weighted.png',dpi=210);plt.close(fig)
    sub=[r for r in da if int(Fraction(r['gamma_E_lab_MeV']))==330]
    xs=[float(Fraction(r['theta_d_CM_deg'])) for r in sub]
    a=[float(r['Kplus_target_rest_MeV']) for r in sub]
    b=[float(r['Kminus_target_rest_MeV']) for r in sub]
    fig,ax=plt.subplots(figsize=(7,4.5))
    ax.plot(xs,a,'o',label=r'$K_+(\theta_{CM})$ fixed-target')
    ax.plot(xs,b,'s',label=r'$K_-(\theta_{CM})$ fixed-target')
    ax.set(xlabel=r'Measured $\theta_{CM}$ (degrees)',ylabel='One-event daughter kinetic energy (MeV)',
           title=r'Two-body daughter kinematics at source $E_\gamma=330$ MeV')
    ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout()
    fig.savefig(fig_dir/'daughter_330_source_angles.png',dpi=210);plt.close(fig)
    return ['exfor_SIG_kinetic_weighted.png','exfor_DA_kinetic_weighted.png','daughter_330_source_angles.png']

if __name__=='__main__':
    ROOT=Path(__file__).resolve().parents[1]
    print(plot(ROOT/'results',ROOT/'figures'))
