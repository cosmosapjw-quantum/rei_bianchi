#!/usr/bin/env python3
"""Compute original ACROPOLIS v1.3.1 17-reaction + measured inclusive / pi0 feedback data."""
from __future__ import annotations
import os,sys,csv,json,math,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from pion_feedback import _physical_model,GEOM,RATES,CONVERSION,ALPHA_REACTIONS
from pi0_physics import interpolated_absorption

ES=[206,216,229,241]
ZS=[1e4,1e5,1e6]
NE=int(os.environ.get('BASS_HE_GRID_PD','120'))
SCENARIOS={'em_only':(False,False),'nuclear_loss':(False,True),'measured_pi_gain':(True,True)}
ROOT=BASE/'data';FIG=BASE/'figures';ROOT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'BASS_HE_PR137_PHYSICAL_SOURCE_20261031'})

def write_csv(path,rows):
    if not rows:raise RuntimeError('No science rows')
    keys=list(rows[0].keys());
    with path.open('w',encoding='utf-8',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def plot(ax,stem):
    ax.grid(alpha=.24)
    fig=ax.get_figure();fig.tight_layout();fig.savefig(FIG/(stem+'.png'),dpi=150,metadata={'Software':'BASS_HE PR137 measured-source model'});fig.savefig(FIG/(stem+'.svg'),metadata={'Date':'2026-10-31','Creator':'BASS_HE source-owned'});plt.close(fig)

def create():
    import acropolis
    from acropolis.input import InputInterface,locate_sm_file
    from acropolis.nucl import NuclearReactor
    ii=InputInterface(locate_sm_file())
    nu=NuclearReactor([lambda t:0.]*3,[lambda e,t:0.]*3,(1e-5,1e-5),250,ii)
    anchors=[]
    for E in ES:
        phi=interpolated_absorption(E)
        si=sum(nu.get_cross_section(rid,E)/CONVERSION*1000 for rid in ALPHA_REACTIONS)
        rr=RATES[E]
        # Non-overlapping physical process partition only; no claim residual is one channel.
        remaining=phi['sigma_micro_b']-rr-si
        if remaining<=0:raise RuntimeError('Source model positivity: residual nuclear absorption <=0')
        anchors.append({'E_lab_MeV':E,'absorption_inclusive_micro_b':phi['sigma_micro_b'],
            'absorption_interpolated_from_low_MeV':phi['low_MeV'],
            'absorption_interpolated_from_high_MeV':phi['high_MeV'],
            'sigma_coherent_pi0_micro_b':rr,
            'sigma_alpha_four_acropolis_micro_b':si,
            'measured_minus_pi0_minus_four_alpha_model_micro_b':remaining,
            'pion_fraction_inclusive':rr/phi['sigma_micro_b'],
            'common_pion_norm_sys_fraction':0.07,
            'source_pi0':'Rambo1999_EXFOR_M0752019',
            'source_inclusive':'MacCormick1997_EXFOR_M0520002',
            'model_alpha':'ACROPOLIS_v1.3.1_17_nuclear_reactions',
            'residual_is_not_one_physical_exclusive_channel':True})
    write_csv(ROOT/'SOURCE_MEASURED_INCLUSIVE_OPACITY_ANCHORS_4.csv',anchors)
    if os.environ.get('BASS_HE_RESUME_DATA')=='1':
        def _read_csv(name):
            with (ROOT/name).open(newline='',encoding='utf-8') as file:return list(csv.DictReader(file))
        rows=_read_csv('COUPLED_NUCLEAR_PI0_GREEN_RESPONSE_36.csv')
        events=_read_csv('REACTION_17_RESPONSES_612.csv')
        isotopes=_read_csv('NUCLIDE_9_SIGNED_RESPONSE_324.csv')
        spectra=_read_csv('THREE_SPECIES_NUCLEAR_OPACITY_SPECTRA.csv')
        for r in rows:
            for key in ('E_primary_MeV','z','D_net_per_initial_pi0','D_born_per_initial_pi0','D_destroy_per_initial_pi0','known_channels_baryon_residual','known_channels_charge_residual'):
                r[key]=float(r[key])
        for r in events:r['E_primary_MeV']=float(r['E_primary_MeV']);r['z']=float(r['z']);r['event_response_per_pi0']=float(r['event_response_per_pi0'])
        for r in isotopes:r['E_primary_MeV']=float(r['E_primary_MeV']);r['z']=float(r['z']);r['signed_delta_Y_per_pi0']=float(r['signed_delta_Y_per_pi0'])
    else:
        rows=[];events=[];isotopes=[];spectra=[]
        for E in ES:
            for z in ZS:
                for scenario,(gain,sink) in SCENARIOS.items():
                    out,sol,rabs,rpi,Eg=_physical_model(E,z,NE,do_gain=gain,do_sink=sink)
                    data={k:v for k,v in out.items() if k not in ('channel_events','isotope_delta_0to8')}
                    data['scenario_id']=scenario
                    rows.append(data)
                    for rid,val in out['channel_events'].items():
                        events.append({'E_primary_MeV':E,'z':z,'scenario':scenario,'reaction_id':rid,'event_response_per_pi0':val,
                                      'model_source':'ACROPOLIS_v1.3.1_NuclearReactor'} )
                    for i,val in out['isotope_delta_0to8'].items():
                        isotopes.append({'E_primary_MeV':E,'z':z,'scenario':scenario,'nuclide_index':i,'signed_delta_Y_per_pi0':val,
                                        'source':'ACROPOLIS_17_reactions_excluding_Li6_unknown_X'} )
                    if scenario=='measured_pi_gain':
                        for j,eg in enumerate(Eg):
                            spectra.append({'E_primary_MeV':E,'z':z,'E_secondary_MeV':float(eg),
                                            'gamma_spectrum':float(sol[1,j]),'electron_spectrum':float(sol[2,j]),
                                            'positron_spectrum':float(sol[3,j]),
                                            'photonuclear_absorption_rate_natural_MeV':float(rabs[j]),
                                            'coherent_pi0_regen_rate_natural_MeV':float(rpi[j]),
                                            'scenario':'measured_pi_gain'})
                    print('SCE',E,z,scenario,'Dnet',f"{out['D_net_per_initial_pi0']:.11g}",
                          'pi',f"{out['pion_regen_events_measured_support']:.4e}",flush=True)
        write_csv(ROOT/'COUPLED_NUCLEAR_PI0_GREEN_RESPONSE_36.csv',rows)
        write_csv(ROOT/'REACTION_17_RESPONSES_612.csv',events)
        write_csv(ROOT/'NUCLIDE_9_SIGNED_RESPONSE_324.csv',isotopes)
        write_csv(ROOT/'THREE_SPECIES_NUCLEAR_OPACITY_SPECTRA.csv',spectra)
    # Conditions at 241 only, same fixed sources, compare corrections on same mesh
    checks=[]
    for z,res in ((1e4,96),(1e5,96),(1e5,144),(1e5,192),(1e6,96)):
        for res in (res,):
            lo,*_=_physical_model(241,z,res,do_gain=False,do_sink=True)
            hi,*_=_physical_model(241,z,res,do_gain=True,do_sink=True)
            delta=hi['D_net_per_initial_pi0']-lo['D_net_per_initial_pi0']
            checks.append({'E_primary_MeV':241,'z':z,'NE_pd':res,'pion_feedback_D_net_increment':delta,
                           'pion_feedback_relative_increment':delta/lo['D_net_per_initial_pi0'],
                           'mean_pi0_return_photons':hi['pion_regen_photon_count_actually_injected'],
                           'pion_support_grid_points':hi['n_measured_pion_grid_points'],
                           'pi_kernel_energy_relative_error':hi['max_pi_kernel_energy_model_relative_error']})
    write_csv(ROOT/'PI0_RETURN_GRID_SENSITIVITY_5.csv',checks)
    # Source-only visuals, grouped by redshift
    def get(e,z,k):return next(r for r in rows if r['E_primary_MeV']==e and r['z']==z and r['scenario_id']==k)
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    for z in ZS:
        v=[get(e,z,'measured_pi_gain')['D_net_per_initial_pi0'] for e in ES]
        ax.plot(ES,v,marker='o',label='z='+format(z,'.0e'))
    ax.set(xlabel='Primary gamma energy (MeV)',ylabel='Signed net D nuclei / produced pi0',title='17-channel BBN nuclear network: signed deuterium response');ax.set_yscale('log');ax.legend();plot(ax,'NET_D_RESPONSE_BY_REDSHIFT')
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    for z in ZS:
        v=[100*(get(e,z,'nuclear_loss')['D_net_per_initial_pi0']/get(e,z,'em_only')['D_net_per_initial_pi0']-1) for e in ES]
        ax.plot(ES,v,marker='o',label='z='+format(z,'.0e'))
    ax.set(xlabel='Primary gamma energy (MeV)',ylabel='Signed net D change from photonuclear loss (%)',title='Nuclear photon opacity changes the coupled EM cascade');ax.legend();plot(ax,'NUCLEAR_OPACITY_EFFECT_ON_NET_D')
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    for z in ZS:
        v=[(get(e,z,'measured_pi_gain')['D_net_per_initial_pi0']-get(e,z,'nuclear_loss')['D_net_per_initial_pi0']) for e in ES]
        ax.plot(ES,v,marker='o',label='z='+format(z,'.0e'))
    ax.set(xlabel='Primary gamma energy (MeV)',ylabel='Pion regeneration net-D increment / pion',title='Measured-support coherent pi0 feedback: not full subthreshold physics');ax.legend();plot(ax,'PI0_MEASURED_SUPPORT_FEEDBACK')
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    xx=np.arange(17); rmap={int(r['reaction_id']):r['event_response_per_pi0'] for r in events if r['E_primary_MeV']==241 and r['z']==1e5 and r['scenario']=='measured_pi_gain'}
    ax.bar(xx+1,[rmap[i] for i in range(1,18)])
    ax.set(xlabel='ACROPOLIS reaction ID',ylabel='Events / produced pi0',title='Original ACROPOLIS 17-channel nuclear response at E=241 MeV,z=1e5');ax.set_yscale('log');plot(ax,'SEVENTEEN_NUCLEAR_CHANNELS')
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    iso={int(r['nuclide_index']):r['signed_delta_Y_per_pi0'] for r in isotopes if r['E_primary_MeV']==241 and r['z']==1e5 and r['scenario']=='measured_pi_gain'}
    labels=['n','p','D','T','He3','He4','Li6','Li7','Be7']
    ax.bar(np.arange(9),[iso[i] for i in range(9)]);ax.set_xticks(np.arange(9),labels)
    ax.set(xlabel='Nuclear isotope',ylabel='Signed delta Y / produced pi0',title='Known-product 16-channel nuclei: baryon & charge closure');plot(ax,'SIGNED_NUCLEAR_ISOTOPE_CHANGES')
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    ax.plot(ES,[v['absorption_inclusive_micro_b'] for v in anchors],marker='o',label='MacCormick total absorption')
    ax.plot(ES,[v['sigma_coherent_pi0_micro_b'] for v in anchors],marker='o',label='Rambo coherent pi0 included')
    ax.plot(ES,[v['sigma_alpha_four_acropolis_micro_b'] for v in anchors],marker='o',label='ACROPOLIS four He4 models')
    ax.set(xlabel='Photon energy (MeV)',ylabel='Cross section (microbarn)',title='Measured inclusive is the alpha absorption TOTAL, not an extra loss');ax.legend();plot(ax,'INCLUSIVE_REPLACES_NOT_ADDS')
    worst=max(abs(r['known_channels_baryon_residual']) for r in rows)
    max_charge=max(abs(r['known_channels_charge_residual']) for r in rows)
    high_z_g=next(r for r in checks if r['z']==1e6 and r['NE_pd']==96)
    summary={'project':'BASS_HE','unit':'SOURCE_AUTHORITY_PI0_NUCLEAR_OPACITY_FEEDBACK_PR137','source_owner':'ACROPOLIS v1.3.1 + original Cyburt2003 + Jedamzik2006 + Rambo1999 + MacCormick1997',
         'source_ACROPOLIS_zip_SHA256':'1d933f8d53c614d379166ada9319b4188ec45c0b74e065ba790034da41f0d9e1',
         'source_ACROPOLIS_version':'1.3.1','original_acropolis_unmodified':True,
         'parent_head':'5c24f0fa2c0de0f0e80edd8bde7266c60b264fde',
         'central_DAG':'28/88','he_physical_DAG':'14/18','canonical_delta':0,
         'n_cases':len(rows),'n_reaction_rows':len(events),'n_signed_species_rows':len(isotopes),'n_spectral_rows':len(spectra),'n_grid_checks':len(checks),'n_new_measured_rows':0,
         'grid_pd':NE,'physics_cross_section_kind':'standard published modeled nuclear 17 channels; measured inclusive above 204 replacing alpha sum, pion 206-241 gain interpolated',
         'nuclide_conservation_max_baryon_residual':worst,'nuclide_conservation_max_charge_residual':max_charge,
         'most_important_conflict':'pi0 included in MacCormick total, no double count',
         'limitations':['pion production below 206 MeV unmodeled; no extrapolation','Rambo angle shape limited measured bins','time-local fixed FLRW and original AlterBBN 2.2 failsafe12','no pion or nuclear feedback above input 250 MeV','unknown Li6 gamma X excluded from signed isotope balance','other nuclear channels at high E are Cyburt source extrapolations','no BASS source amplitude','no FastD deposition','no observational likelihood'],
         'kappa':None,'R_event':None,'heat_rate':None,'L4':False,'PRODUCTION':'HOLD','NO_MERGE':True,'AUTO_NEXT_NODE':False}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print('DONE',len(rows),len(events),len(isotopes),len(spectra),len(checks),flush=True)

if __name__=='__main__':create()
