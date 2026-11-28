#!/usr/bin/env python3
"""Reproducible *published measured near-threshold* pion -> coupled EM nuclear response.
Normal production mode uses the preserved source-author EXFOR 216-row csv.
"""
from __future__ import annotations
import os,sys,csv,json,math,hashlib,contextlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from threshold_transport import *

DATA=BASE/'data'; FIG=BASE/'figures';FIG.mkdir(parents=True,exist_ok=True)
plt.rcParams['font.family']='DejaVu Sans'
plt.rcParams['svg.hashsalt']='BASS_HE_BARNETT_EXFOR_20261031'
ZS=[1e4,1e5,1e6]
MAIN_NE=96


def csvout(path,rows):
    if not rows:raise ValueError('Cannot write empty science output '+str(path))
    keys=list(rows[0].keys())
    with path.open('w',newline='',encoding='utf-8') as h:
        wr=csv.DictWriter(h,fieldnames=keys);wr.writeheader();wr.writerows(rows)


def figure(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=150,bbox_inches='tight',metadata={'Software':'BASS_HE PR138 science'})
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight',metadata={'Date':'2026-10-31','Creator':'BASS_HE PR138 research'})
    plt.close(fig)


def main():
    rows=read_barnett_csv(DATA/'EXFOR_BARNETT_L0138002_216.csv')
    samples=select_source_points(rows)
    midpoint=THRESHOLDS['coherent_alpha'];parent_reproduction=daughter_reproduction_threshold()
    if not (max(x['energy_MeV'] for x in samples)<THRESHOLDS['pT']<parent_reproduction):
        raise AssertionError('Threshold safety domain broken')
    source=[]
    for r in rows:
        q=dict(r)
        E=r['energy_MeV']
        q['strict_coherent_kinematic_domain']=bool(midpoint<E<THRESHOLDS['pT'])
        q['below_coherent_threshold']=bool(E<=midpoint)
        q['breakup_pion_channels_open']=bool(E>=THRESHOLDS['pT'])
        q['measured_raw_sigma_may_be_negative_below_threshold']=True
        source.append(q)
    csvout(DATA/'BARNETT_SOURCE_TYPED_216.csv',source)
    outcomes=[];channel=[];nuclides=[];spectra=[]
    for s in samples:
        for z in ZS:
            rt=solve_epoch(s,z,NE=MAIN_NE,angular_model='pwave',nuclear_sink=True,return_spectrum=True)
            v=rt['case'];outcomes.append(v)
            for rid,val in enumerate(rt['rates'],1):channel.append({'Eprimary_MeV':v['Eprimary_MeV'],'z':z,'rid':rid,'events_per_initial_pi0':float(val),
                        'source':'ACROPOLIS_v1.3.1_published_17_channel_CyburtJedamzik'})
            for j,val in rt['nuclei'].items():nuclides.append({'Eprimary_MeV':v['Eprimary_MeV'],'z':z,'nuclide_index':j,
                    'signed_number_per_initial_pi0':float(val),'Li6_gammaX_unassigned':bool(j==6)})
            ss=rt['spectra']
            for g,e in enumerate(ss['grid']):
                spectra.append({'Eprimary_MeV':v['Eprimary_MeV'],'z':z,'E_secondary_MeV':float(e),
                'source_pi0_daughter_dN_dE':float(ss['injected'][g]),
                'gamma_EM_plus_nuclear_sink':float(ss['gamma'][g]),
                'electron_EM_plus_nuclear_sink':float(ss['electron'][g]),
                'positron_EM_plus_nuclear_sink':float(ss['positron'][g]),
                'nuclear17_photon_absorption_rate_MeV':float(ss['nuclear_loss'][g])})
            # Checkpoint before any optional comparisons / plotting
            csvout(DATA/'MEASURED_NEAR_THRESHOLD_PHYSICS_GREEN_15.csv',outcomes)
            csvout(DATA/'NUCLEAR_17_CHANNEL_EVENTS_255.csv',channel)
            csvout(DATA/'NUCLIDE_SIGNED_RESPONSE_135.csv',nuclides)
            csvout(DATA/'THREE_SPECIES_SPECTRA.csv',spectra)
            print('MODEL',s['energy_MeV'],z,'Dnet/pi=',v['D_net_per_pi0'],'first P=',v['pion_first_hit_P'],
                  'Dnet/primary=',v['D_net_per_primary_first_hit'],flush=True)
    tests=[]
    for e,z in [(144.02,1e4),(152.03,1e5)]:
        sample=next(x for x in samples if abs(x['energy_MeV']-e)<1e-6)
        ref=next(x for x in outcomes if x['Eprimary_MeV']==e and x['z']==z)
        for angle in ('isotropic','pwave'):
            for ne in (64,96):
                if angle=='pwave' and ne==96:
                    value=ref
                else:
                    value=solve_epoch(sample,z,NE=ne,angular_model=angle,nuclear_sink=True)['case']
                tests.append({'Eprimary_MeV':e,'z':z,'angular_model':angle,'NE_per_decade':ne,
                    'D_net_per_pi0':value['D_net_per_pi0'],'D_net_per_primary':value['D_net_per_primary_first_hit'],
                    'relative_to_96_pwave_Dnet':float(value['D_net_per_pi0']/ref['D_net_per_pi0']-1),
                    'daughter_energy_relerr':float(value['daughter_grid_energy_relerr'])})
    csvout(DATA/'ANGULAR_AND_GRID_SENSITIVITY_8.csv',tests)
    # Measured source and exact coherent threshold vs pion production with any fragmentation
    fig,ax=plt.subplots(figsize=(7.7,4.4))
    for q in [r for r in source if r['energy_MeV']>=135]:
        ax.errorbar(q['energy_MeV'],q['sigma_micro_b'],yerr=q['stat_micro_b'],fmt='.',alpha=.26,markersize=3,linewidth=.4)
    ax.axvline(THRESHOLDS['coherent_alpha'],color='grey',ls=':',label='Coherent threshold')
    ax.axvline(THRESHOLDS['pT'],color='black',ls='--',label='First breakup + pion threshold')
    ax.set(xlabel='Incident gamma energy (MeV)',ylabel='Measured gamma+He4 -> pi0+X cross section (microbarn)',
            title='Barnett 2008 EXFOR L0138002: near-threshold source, 216 raw rows')
    ax.legend(fontsize=8);ax.grid(alpha=.25);figure(fig,'BARNETT_EXFOR_MEASURED_PI0_THRESHOLD')
    # Source kinetic no-reproduction proof
    eg=np.linspace(THRESHOLDS['coherent_alpha']+1e-3,200,240)
    fig,ax=plt.subplots(figsize=(7.5,4.4));ax.plot(eg,[max_daughter(E) for E in eg])
    ax.axhline(THRESHOLDS['coherent_alpha'],ls='--',color='black',label='Threshold to make a new pion')
    ax.axvline(parent_reproduction,ls=':',color='grey',label='Secondary-pion reopening = %.3f MeV'%parent_reproduction)
    ax.axvspan(THRESHOLDS['coherent_alpha'],THRESHOLDS['pT'],alpha=.08,label='Provably coherent Barnett domain')
    ax.set(xlabel='Parent gamma energy (MeV)',ylabel='Max daughter gamma energy (MeV)',
            title='Two-body recoil forbids pion feedback below 171.165 MeV')
    ax.legend(fontsize=8);ax.grid(alpha=.25);figure(fig,'EXACT_DAUGHTER_PION_REOPENING')
    # D green response per parent first-hit
    fig,ax=plt.subplots(figsize=(7.5,4.4))
    for z in ZS:
        rr=[x for x in outcomes if x['z']==z]
        ax.plot([x['Eprimary_MeV'] for x in rr],[x['D_net_per_primary_first_hit'] for x in rr],marker='o',label='z=%g'%z)
    ax.set(xlabel='Measured incident gamma energy (MeV)',ylabel='Signed D response / primary gamma (first-pion hit)',
            title='Measured near-threshold pion source x ACROPOLIS 17-channel response')
    ax.set_yscale('log');ax.grid(alpha=.25);ax.legend();figure(fig,'D_NET_GREEN_FIRST_PI0')
    # fast D kinetic source, gross born bounds, not deposited energy
    fig,ax=plt.subplots(figsize=(7.5,4.4))
    for z in (1e4,1e5):
        rr=[x for x in outcomes if x['z']==z]
        xs=np.array([x['Eprimary_MeV'] for x in rr]); low=np.array([x['fastD_from_dd_gross_lower_MeV_per_pi0'] for x in rr]); high=np.array([x['fastD_from_dd_plus_npD_gross_upper_MeV_per_pi0'] for x in rr]);
        ax.plot(xs,low,marker='o',label='Two-body DD kinetic, z=%g'%z)
        ax.fill_between(xs,low,high,alpha=.12,label='Additional npD D kinetic unknown, z=%g'%z)
    ax.set(xlabel='Measured incident gamma energy (MeV)',ylabel='Gross fast-D birth kinetic MeV / pi0',
            title='Source-conditional fast-D kinetic bounds; NOT heat deposition')
    ax.set_yscale('log');ax.legend(fontsize=7);ax.grid(alpha=.25);figure(fig,'FAST_D_GROSS_BIRTH_KINETIC_INTERVAL')
    fig,ax=plt.subplots(figsize=(7.5,4.4))
    for E in [144.02,152.03]:
        rr=[x for x in tests if x['Eprimary_MeV']==E]
        ax.plot([1 if q['angular_model']=='pwave' else 0 for q in rr if q['NE_per_decade']==96],
                [q['relative_to_96_pwave_Dnet']*100 for q in rr if q['NE_per_decade']==96],
                marker='o',label=f'E={E:.2f} MeV')
    ax.set(xticks=[0,1],xticklabels=['Isotropic model','p-wave (reference)'],
            ylabel='D-net difference vs p-wave (%)',title='Unmeasured pion angular-law model sensitivity')
    ax.legend();ax.grid(alpha=.25);figure(fig,'ANGULAR_MODEL_SENSITIVITY')
    # recorded physics lineage summary
    identity=json.loads((DATA/'SOURCE_PROVENANCE.json').read_text())
    summary={'unit':'BASS_HE_BARNETT2008_BELOW_BREAKUP_COHERENT_PI0_WITH_ACROPOLIS','date':'2026-10-31',
    'parent_pr':137,'parent_head':'efadfdea605664a5cfc829a912456a0b7142d12e',
    'gamma_source':SOURCEREF,'source_sha256':identity['input_sha256'],
    'source_raw_rows':len(rows),'selected_exact_energy_source_rows':len(samples),
    'thresholds_MeV':THRESHOLDS,'daughter_reproduction_parent_threshold_MeV':parent_reproduction,
    'model_cases':len(outcomes),'reaction_rows':len(channel),'nuclide_rows':len(nuclides),
    'spectrum_rows':len(spectra),'comparison_rows':len(tests),
    'new_measured_experiments':0,'new_source_rows_imported':len(rows),'new_derived_science_rows':len(outcomes)+len(channel)+len(nuclides)+len(spectra)+len(tests),
    'plots_png':5,'plots_svg':5,'source_branching_pi0_2gamma':B_2G,
    'ACROPOLIS_version':'1.3.1','ACROPOLIS_source_unmodified':True,
    'all_BW_KN_BH_cascade_qed':'ACROPOLIS_1_3_1',
    'nuclear17_reactions':'Cyburt2003_plus_Jedamzik2006_published_ACROPOLIS_implementation',
    'pion_angular_law':'pwave_fully_model_conditional_isotropic_adversarial_alternative',
    'pion_first_hit_only':True,'pion_recursion_zero_on_source_domain':'EXACT_KINEMATIC_NO_REOPENING',
    'gross_fastD_DD_kinetic_exact':'E_gamma-Qdd_energy_ledger',
    'gross_fastD_npD_kinetic':'UPPER_BOUND_ONLY',
    'no_net_heat':True,'no_BASS_gamma_emissivity':True,
    'central_DAG':'28/88','HE_physical_DAG':'14/18','canonical_delta':0,
    'production':'HOLD','no_merge':True,'auto_next_node':False,
    'selected_sample_energies_MeV':[x['energy_MeV'] for x in samples],
    'worst_source_discretization_energy_relerr':max(abs(x['daughter_grid_energy_relerr']) for x in outcomes),
    'max_known_stoichiometry_B_residual':max(abs(x['known_stoichiometry_baryon_residual']) for x in outcomes),
    'max_known_stoichiometry_charge_residual':max(abs(x['known_stoichiometry_charge_residual']) for x in outcomes)}
    (DATA/'SCIENTIFIC_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print('COMPLETE',summary['model_cases'],summary['new_derived_science_rows'],flush=True)

if __name__=='__main__':main()
