#!/usr/bin/env python3
from pathlib import Path
import csv,math
import matplotlib.pyplot as plt
from rice_response import ROOT,schiff_shape,run

def plots():
  r,rows,spec,legs=run(ROOT)
  p=ROOT/'figures';p.mkdir(exist_ok=True)
  # Each figure is independent, no composite subplots and no user-unrequested colors
  for binid in ('150-190','190-250'):
    sel=[d for d in rows if d['bin_MeV']==binid]
    fig,ax=plt.subplots(figsize=(8,5))
    x=[d['CM_theta_deg'] for d in sel]
    ax.errorbar(x,[d['thesis_1998_nb_sr'] for d in sel],yerr=[d['thesis_stat_sd_nb_sr'] for d in sel],fmt='o',capsize=3,label='1998 thesis preliminary')
    ax.errorbar(x,[d['published_2000_nb_sr'] for d in sel],yerr=[d['published_stat_sd_nb_sr'] for d in sel],fmt='s',capsize=3,label='2000 published final (same SAL experiment)')
    ax.set(xlabel='CM angle (deg)',ylabel=r'$d\sigma/d\Omega$ (nb/sr)',title=f'Source version comparison: Eγ {binid} MeV')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(p/f'SAL_{binid.replace("-","_")}_SOURCE_VERSIONS.png',dpi=160);fig.savefig(p/f'SAL_{binid.replace("-","_")}_SOURCE_VERSIONS.svg');plt.close(fig)
  fig,ax=plt.subplots(figsize=(8,5))
  for binid in ('150-190','190-250'):
    sel=[d for d in rows if d['bin_MeV']==binid]
    ax.plot([d['lab_theta_deg'] for d in sel],[d['J_SR_exact']-d['J_thesis'] for d in sel],marker='o',label=binid+' MeV')
  ax.set(xlabel='Lab angle (deg)',ylabel='J exact SR minus Rice tabulated J',title='Exact two-body laboratory-to-CM response audit')
  ax.axhline(0,linewidth=1);ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(p/'SAL_JACOBIAN_AUDIT.png',dpi=160);fig.savefig(p/'SAL_JACOBIAN_AUDIT.svg');plt.close(fig)
  fig,ax=plt.subplots(figsize=(8,5))
  E=[150+.5*i for i in range(245) if 150+.5*i<273]
  ax.plot(E,[schiff_shape(k) for k in E],label='Schiff source shape (not astrophysical)')
  ax.axvspan(150,190,alpha=.1,label='150-190 MeV original SAL bin')
  ax.axvspan(190,250,alpha=.1,label='190-250 MeV original SAL bin')
  ax.set(xlabel='Incident laboratory photon energy (MeV)',ylabel='Bremsstrahlung spectral shape (arbitrary units)',title='Rice 1998 Appendix A.1 laboratory beam model')
  ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(p/'SCHIFF_LAB_GAMMA_SHAPE.png',dpi=160);fig.savefig(p/'SCHIFF_LAB_GAMMA_SHAPE.svg');plt.close(fig)
  fig,ax=plt.subplots(figsize=(8,5))
  for det in ('NaI14','NaI19'):
    sel=[d for d in legs if d['detector']==det]
    ax.errorbar([d['lab_angle_deg'] for d in sel],[d['flux_corrected_raw_asymmetry'] for d in sel],yerr=[d['Poisson_only_sd'] for d in sel],fmt='o',capsize=3,label=det+' (candidate data only)')
  ax.set(xlabel='Laboratory angle (deg)',ylabel='Flux-normalized raw count asymmetry (not A(theta))',title='LEGS 1993 measured coincidence candidates, npd unremoved')
  ax.axhline(0,linewidth=1);ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(p/'LEGS_INSTRUMENTAL_POLARIZATION_RAW.png',dpi=160);fig.savefig(p/'LEGS_INSTRUMENTAL_POLARIZATION_RAW.svg');plt.close(fig)
  print('PLOTS',len(list(p.glob('*.png'))),'png',len(list(p.glob('*.svg'))),'svg')

if __name__=='__main__':plots()
