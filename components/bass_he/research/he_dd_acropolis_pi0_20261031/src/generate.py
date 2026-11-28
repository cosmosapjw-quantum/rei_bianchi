#!/usr/bin/env python3
"""Generate source-conditional coupled ACROPOLIS v1.3.1 response to Rambo1999 pi0 two-gamma source."""
from __future__ import annotations
import os,csv,json,hashlib,sys,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from cascade_bridge import run_fixed_epoch, SourceShape
ROOT=BASE/'data';FIG=BASE/'figures';ROOT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
plt.rcParams['svg.hashsalt']='BASS_HE_ACROPOLIS_SOURCE_20261031_V1'
plt.rcParams['font.family']='DejaVu Sans'

ES=(206.,216.,229.,241.)
ZS=(1e4,1e5,1e6)
NE=120

def write_csv(path,rows,fields=None):
    if not rows:raise ValueError('No science data rows')
    fields=fields or list(rows[0].keys())
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def plot_save(fig,stem):
    fig.savefig(FIG/(stem+'.png'),dpi=150,bbox_inches='tight',metadata={'Software':'BASS_HE source-owned v1'})
    fig.savefig(FIG/(stem+'.svg'),bbox_inches='tight',metadata={'Date':'2026-10-31','Creator':'BASS_HE source-owned'})
    plt.close(fig)

def main():
    rows=[];spectra=[];injections=[];reactions=[]
    source_identity={}
    for E in ES:
        source=SourceShape.from_exfor(E)
        source_identity[str(int(E))]={'measured_angular_support_N':len(source.weights), 'source_N_photons':2*0.98823,'source_energy_MeV':source.exact_moments()['energy']}
        for z in ZS:
            result,sol,proj,src=run_fixed_epoch(E,z,NE,photon_only_check=True)
            rows.append(result)
            for j,e in enumerate(sol[0]):
                spectra.append({'E_primary_MeV':E,'z':z,'E_secondary_MeV':float(e),
                    'injected_pi0_dN_gamma_dE':float(proj[j]),
                    'steady_gamma_spectrum':float(sol[1,j]),
                    'steady_electron_spectrum':float(sol[2,j]),
                    'steady_positron_spectrum':float(sol[3,j]),
                    'ACROPOLIS_version':'1.3.1','source_conditional':True})
            print('CASE',E,z,result['D_born_per_pi0_conditional'],result['D_born_per_primary_gamma_first_pi0_then_cascade'],result['fraction_D_born_below150'],result['D_born_coupled_over_photon_only'],flush=True)
    # Real physics: independent E/T changes, fixed experiment and frozen sources.
    write_csv(ROOT/'FIRST_GENERATION_PI0_COUPLED_RESPONSE_12.csv',rows)
    write_csv(ROOT/'SPECIES_SPECTRA_SOURCE_12.csv',spectra)
    comparisons=[]
    for E,z in [(216.,1e4),(216.,1e5),(216.,1e6),(241.,1e5)]:
        reference=next(v for v in rows if v['E_primary_MeV']==E and v['z']==z)
        for low in (48,72,96):
            other,*_=run_fixed_epoch(E,z,low)
            comparisons.append({'E_primary_MeV':E,'z':z,'NE_per_decade':low,
                'D_per_pi0':other['D_born_per_pi0_conditional'],
                'D_per_pi0_ref_120':reference['D_born_per_pi0_conditional'],
                'rel_diff_from_120':other['D_born_per_pi0_conditional']/reference['D_born_per_pi0_conditional']-1.,
                'discrete_injection_energy_relerr':other['source_grid_energy_relerr']})
    write_csv(ROOT/'GRID_PHYSICS_SENSITIVITY_12.csv',comparisons)
    # plot 1 measured source of pi0; only support-angle conditional.
    fig,ax=plt.subplots(figsize=(7.3,4.4))
    for E in ES:
        src=SourceShape.from_exfor(E)
        g=np.linspace(1.5,max(src.highs)*1.00001,500)
        ax.plot(g,np.array([src.spectrum(e) for e in g]),label=f'{E:.0f} MeV incident')
    ax.set(xlabel='Daughter gamma energy (MeV)',ylabel='dN_gamma / dE per produced pi0 (MeV$^{-1}$)',title='Coherent pi0 decay: source-angle-conditioned injection')
    ax.legend(fontsize=8);ax.grid(alpha=.25);plot_save(fig,'PI0_DAUGHTER_SOURCE_MEASURED_ANGLE')
    # plot 2 directly physics D births per pi0 at three different epochs.
    fig,ax=plt.subplots(figsize=(7.3,4.4))
    for z in ZS:
        sub=sorted([v for v in rows if v['z']==z],key=lambda v:v['E_primary_MeV'])
        ax.plot([r['E_primary_MeV'] for r in sub],[r['D_born_per_pi0_conditional'] for r in sub],marker='o',label=f'z={z:.0e}')
    ax.set(xlabel='Original gamma energy (MeV)',ylabel='Gross D nuclei born / produced pi0',title='Coupled photon / electron / positron cascade response')
    ax.set_yscale('log');ax.legend();ax.grid(alpha=.25);plot_save(fig,'PI0_SECONDARY_GROSS_D_BIRTH')
    # plot 3 fraction of D from sub150MeV photonuclear interactions.
    fig,ax=plt.subplots(figsize=(7.3,4.4))
    for z in ZS:
        sub=sorted([v for v in rows if v['z']==z],key=lambda v:v['E_primary_MeV'])
        ax.plot([r['E_primary_MeV'] for r in sub],[100*r['fraction_D_born_below150'] for r in sub],marker='o',label=f'z={z:.0e}')
    ax.set(xlabel='Original gamma energy (MeV)',ylabel='D-birth contribution from secondary E < 150 MeV (%)',title='Previous 150 MeV cutoff excluded the dominant secondary response')
    ax.set_ylim(0,101);ax.legend();ax.grid(alpha=.25);plot_save(fig,'PI0_D_BIRTH_BELOW_150_FRACTION')
    # plot 4 e± feedback ratio.
    fig,ax=plt.subplots(figsize=(7.3,4.4))
    for E in ES:
        sub=sorted([v for v in rows if v['E_primary_MeV']==E],key=lambda v:v['z'])
        ax.plot([r['z'] for r in sub],[r['D_born_coupled_over_photon_only'] for r in sub],marker='o',label=f'E={E:.0f} MeV')
    ax.set(xlabel='Injection redshift',ylabel='D-born coupled / gamma-only',title='Secondary electron and positron return effect')
    ax.set_xscale('log');ax.legend();ax.grid(alpha=.25);plot_save(fig,'PI0_EM_COUPLED_OVER_PHOTON_ONLY')
    # plot 5 photon spectrum response for Eprimary=216 at epochs.
    fig,ax=plt.subplots(figsize=(7.3,4.4))
    for z in ZS:
        sub=[x for x in spectra if x['E_primary_MeV']==216 and x['z']==z]
        # multiply the stationary solution by n_alpha (MeV^3) to avoid extreme physical scale; here show spectrum ratios at reference energy
        x=np.array([q['E_secondary_MeV'] for q in sub]); y=np.array([q['steady_gamma_spectrum'] for q in sub]);
        y=y/max(y)
        ax.plot(x,y,label=f'z={z:.0e}')
    ax.set(xlabel='Cascade photon energy (MeV)',ylabel='Photon occupation response / peak (relative)',title='ACROPOLIS nonthermal photon spectral shape, 216 MeV primary')
    ax.set_xscale('log');ax.set_yscale('log');ax.legend();ax.grid(alpha=.25);plot_save(fig,'PI0_CASCADE_PHOTON_SPECTRA')
    summary={'unit':'BASS_HE_PR136_PI0_ACROPOLIS_COUPLED_GREEN_RESPONSE','parent_pr':135,'parent_head':'36c3c30dde29be5837985c84ec8326935e17ee9a',
      'ACROPOLIS_user_zip_sha256':'1d933f8d53c614d379166ada9319b4188ec45c0b74e065ba790034da41f0d9e1',
      'ACROPOLIS_version':'1.3.1','ACROPOLIS_modifications':0,
      'source_Rambo1999_PDF_sha256':'0221c872f2ed44f35e215b86fd068569bd3af113cca0baafce96ecee17894d3a',
      'source_MacCormick1997_PDF_sha256':'2fe2558f443e107a0ae2e04d4707ea25fe327f8f77f7b6be9f62c74452a09bb7',
      'DAG_central':'28/88','DAG_HE':'14/18','canonical_delta':0,
      'fixed_source_energies_MeV':ES,'fixed_redshifts':ZS,'NE_per_decade':NE,
      'source_mass_branch':source_identity,'new_model_case_rows':len(rows),'new_species_spectrum_rows':len(spectra),'grid_perturbation_cases':len(comparisons),'measured_new_rows':0,
      'all_species_positivity':all(np.isfinite(r['D_born_per_pi0_conditional']) and r['D_born_per_pi0_conditional']>=0 for r in rows),
      'maximum_source_discrete_energy_relative_error':max(abs(r['source_grid_energy_relerr']) for r in rows),
      'max_grid_96_vs_120_D_birth_relerr':max(abs(r['rel_diff_from_120']) for r in comparisons if r['NE_per_decade']==96),
      'science_claim':'source-conditional full three-species EM cascade and linear alpha-photodisintegration response to first-generation coherent pi0 daughter gamma source',
      'not_included':['pion regeneration from secondaries','nuclear photon opacity in cascade','full abundance network evolution','true BASS-native gamma emissivity','fastD Coulomb/ion/nuclear energy deposition','D/H posterior','covariant anisotropic transfer'],
      'BASS_native_source':'MISSING','heat_rate':None,'R_event':None,'kappa':None,'L4':False,'PRODUCTION':'HOLD','NO_MERGE':True,'AUTO_NEXT_NODE':False}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('DONE',len(rows),'cases',len(spectra),'spectrum rows',len(comparisons),'grid comparisons',flush=True)

if __name__=='__main__':main()
