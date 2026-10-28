"""Compact rendering of evaluated frozen-epoch response only."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import model as m


def main():
    out=m.UNIT/'outputs'
    with (out/'external_source_response.csv').open() as f:rows=list(csv.DictReader(f))
    values={k:np.array([float(r[k]) for r in rows]) for k in rows[0]}
    z=values['z_mean'];fig,axs=plt.subplots(2,2,figsize=(12,8),sharex=True)
    ax=axs[0,0]
    for prefix,label in [('photo_atom_','atomic photons'),('photo_nuc_','nuclear photons'),('cr_','CR nuclear'),('inject_','thermal/fast injection')]:
        y=sum((v for k,v in values.items() if k.startswith('event_per_Href_s__'+prefix)),np.zeros_like(z))
        ax.plot(z,np.ma.masked_equal(y,0),label=label)
    ax.set_yscale('log');ax.set_ylabel('Events / Href / proper second');ax.set_title('Prescribed source families')
    ax=axs[0,1]
    colors={'n':'C0','T_0':'C1','T_1':'C2'}
    for label in ('n','T_0','T_1'):
        for alpha,ls in [(1,'-'),(10,'--')]:
            v=values[f'qss_alpha{alpha}_per_Href__{label}']
            ax.plot(z,np.ma.masked_equal(v,0),color=colors[label],ls=ls,label=f'{label}, α={alpha}')
    ax.set_yscale('log');ax.set_ylabel('Particles / Href');ax.set_title('Thermal QSS (α=0: exact zero)')
    ax=axs[1,0]
    for kind,ls in [('n','-'),('T','--')]:
        for branch,color in [('slowing','C0'),('escape','C1'),('beta','C2')]:
            ax.plot(z,values['fast_fraction_'+branch+'__'+kind],ls=ls,color=color,label=f'{kind}: {branch}')
    ax.set_ylim(0,1);ax.set_ylabel('Fast-particle branch fraction');ax.set_title('Finite slowing, escape, decay')
    ax=axs[1,1]
    for key,label in [('heat','heat'),('fast_electron','fast electrons'),('neutrino','antineutrinos'),('escaping_radiation','escaping radiation'),('escaped_kinetic','escaped kinetic')]:
        v=values['power_eV_per_Href_s__'+key]
        ax.plot(z,np.ma.masked_equal(v,0),label=label)
    ax.set_yscale('log');ax.set_ylabel('Energy / Href / proper second [eV]');ax.set_title('Positive energy outputs; signed books in CSV')
    for ax in axs.flat:
        ax.grid(alpha=.25);ax.legend(fontsize=7,ncol=2);ax.set_xlim(z[0],z[-1])
    for ax in axs[1]:ax.set_xlabel('Mean-scale-factor redshift z')
    fig.suptitle('Illustrative, uncalibrated external sources + n/T response',fontsize=15)
    fig.text(.5,.015,'Frozen-epoch QSS; not a time-evolution solution. Baseline targets prescribed; no new IVP.\n'
             'α=1 nominal and α=10 sensitivity; finite-bin toy cross sections and transport hazards. Exact zeros retained in CSV.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,.95));fig.savefig(out/'external_source_response.png',dpi=135);plt.close(fig)
    print(str(out/'external_source_response.png'))


if __name__=='__main__':main()
