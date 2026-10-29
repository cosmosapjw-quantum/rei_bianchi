"""193-point BASS21 source-owned photoelectric energy ledger. NO IVP.

Runs original, byte-pinned BASS AtomicNetwork from the archived VigilODE owner
against immutable saved Y,T,UV,n_b,H. Splits photon absorption into potential
bound ionization-energy term, primary kinetic term, and Li I unresolved core
term. This is NOT a gas heating/secondary-electron transport model.
"""
from __future__ import annotations
import csv
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_simpson

ROOT = Path(__file__).resolve().parents[1]
DONOR_ARCHIVE = ROOT / 'source/VIGILODE_BASS21_SAVED193_SOURCE_REPLAY_20261030_FULL.zip'
DONOR_SHA = '19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907'
TRAJ_SHA = '37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
EV_J = 1.602176634e-19
LI_EDGE_E = 64.39
LI_VALENCE_E = 5.392
LI_CORE_E = LI_EDGE_E - LI_VALENCE_E
N_EXPECT = 193

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def source_owner(tmp: Path):
    raw = DONOR_ARCHIVE.read_bytes()
    if sha(raw) != DONOR_SHA:
        raise ValueError('DONOR_ZIP_SHA_MISMATCH')
    with zipfile.ZipFile(DONOR_ARCHIVE) as z:
        if z.testzip() is not None:
            raise ValueError('DONOR_ZIP_CRC_FAILED')
        z.extractall(tmp)
    traj = tmp / 'original/trajectory.npz'
    if sha(traj.read_bytes()) != TRAJ_SHA:
        raise ValueError('TRAJECTORY_SHA_MISMATCH')
    sys.path.insert(0, str(tmp / 'rei_pr269/code'))
    try:
        import importlib
        # Source loader is the donor's unchanged source-bounded implementation.
        if 'native_full_rate' in sys.modules:
            del sys.modules['native_full_rate']
        src=importlib.import_module('native_full_rate')
        owner_hashes=src.source_manifest_check()
        net=src.new_native_network()
    finally:
        sys.path.pop(0)
    with np.load(traj,allow_pickle=False) as a:
        owner={name:a[name].copy() for name in a.files}
    with np.load(tmp/'replay/results/ACTUAL_FJ_ALL_193_EPOCHS.npz',allow_pickle=False) as a:
        old={name:a[name].copy() for name in a.files}
    return net,owner,old,owner_hashes

def compute():
    with tempfile.TemporaryDirectory(prefix='bass_photo_energy_') as td:
        net,data,old,hashes=source_owner(Path(td))
        x=data['x'];z=data['z'];Y=data['Y'];diag=data['diagnostics'];names=list(data['diagnostic_names'])
        fields={str(name):diag[:,j] for j,name in enumerate(names)}
        if Y.shape != (N_EXPECT,21) or not np.all(np.diff(x)>0) or len(fields['T_K'])!=N_EXPECT:
            raise ValueError('ORIGINAL_ARRAY_CONTRACT_MISMATCH')
        if not np.array_equal(net.A,data['A']) or not np.array_equal(net.q,data['q']):
            raise ValueError('SPECIES_OR_CHARGE_OWNER_MISMATCH')
        indices=list(map(int,net.photo_indices))
        if len(indices)!=13:
            raise ValueError('EXPECTED_13_ACTIVE_PHOTO_SOURCE_SITES')
        edge=np.asarray(net.photon_energy_eV)
        nbins=edge.size
        if nbins!=71:
            raise ValueError('SOURCE_BIN_COUNT_CHANGED')
        site_sigma=np.asarray(net.photo_sigma_m2)[indices]
        site_inner_sigma=np.asarray(net.li1s_photo_sigma_m2)[indices]
        thresh=np.asarray(net.transition_energy_eV)[indices]
        atom_labels=[str(data['species_names'][idx]) for idx in indices]
        event_rows=[];epoch_rows=[];spectral_rows=[]
        arrays={name:np.zeros((N_EXPECT,len(indices))) for name in ('rate_s','abs_ev_per_baryon_s','ion_ev_per_baryon_s','primary_ev_per_baryon_s','core_ev_per_baryon_s','inner_1s_events_per_baryon_s')}
        max_abs={'abs_W_m3':0.,'primary_W_m3':0.,'core_W_m3':0.,'inner_count_m3_s':0.,'branch_energy_J_m3_s':0.,'source_gamma_s':0.,'event_rate_sum_per_baryon_s':0.}
        max_rel={'abs':0.,'primary':0.,'core':0.}
        spectral={name:np.zeros((N_EXPECT,nbins)) for name in ('event','abs_W','ion_W','primary_W','core_W')}
        sum_epoch={name:np.zeros(N_EXPECT) for name in ('events','abs_eV','ion_eV','primary_eV','core_eV','inner_events')}
        uv0=np.asarray(net.photon_flux_bins_base)
        if np.any(site_sigma<0) or np.any(site_inner_sigma<0):raise ValueError('NEGATIVE_CROSS_SECTION')
        for t in range(N_EXPECT):
            yy=np.asarray(Y[t],float)
            T=float(fields['T_K'][t]); u=float(fields['uv_scale'][t]); n=float(fields['nb_m3'][t]); H=float(fields['H'][t]); ne=float(fields['ne_m3'][t])
            if min(T,n,H)<=0 or u<0 or np.min(yy)<0:raise ValueError('PHYSICAL_SAVED_STATE_DOMAIN')
            # Invoke original AtomicNetwork directly at the saved point; no solver.
            ev=net.evaluate(yy,T,u,n)
            rates=net.rates(T,u)
            flux=np.asarray(rates['photon_flux_bins'])
            if not np.array_equal(flux,uv0*u):raise ValueError('PHOTON_FLUX_SOURCE_MISMATCH')
            pops=yy[indices]
            vol_evt=(n*pops)[:,None]*site_sigma*flux[None,:]
            inner_evt=(n*pops)[:,None]*site_inner_sigma*flux[None,:]
            bin_abs=vol_evt*edge[None,:]*EV_J
            bin_ion=vol_evt*thresh[:,None]*EV_J
            bin_core=inner_evt*LI_CORE_E*EV_J
            bin_primary=bin_abs-bin_ion-bin_core
            # Numerical cancellation at threshold can produce tiny signed residuals;
            # require only the physically scaled lower bound with no clipping.
            if np.min(bin_primary)<-max(1e-70,float(np.max(bin_abs))*2e-14):
                raise ValueError('NEGATIVE_PRIMARY_ENERGY_FOR_SOURCE_GRID')
            tot_evt=np.sum(vol_evt,axis=1)
            site_abs=np.sum(bin_abs,axis=1)
            site_ion=np.sum(bin_ion,axis=1)
            site_primary=np.sum(bin_primary,axis=1)
            site_core=np.sum(bin_core,axis=1)
            site_inner=np.sum(inner_evt,axis=1)
            gamma=np.asarray(rates['photo_s'])[indices]
            max_abs['source_gamma_s']=max(max_abs['source_gamma_s'],float(np.max(np.abs(tot_evt/n/pops.clip(min=1e-200)-gamma)[pops>0])) if np.any(pops>0) else 0.)
            for j,idx in enumerate(indices):
                arrays['rate_s'][t,j]=gamma[j]
                arrays['abs_ev_per_baryon_s'][t,j]=site_abs[j]/(n*EV_J)
                arrays['ion_ev_per_baryon_s'][t,j]=site_ion[j]/(n*EV_J)
                arrays['primary_ev_per_baryon_s'][t,j]=site_primary[j]/(n*EV_J)
                arrays['core_ev_per_baryon_s'][t,j]=site_core[j]/(n*EV_J)
                arrays['inner_1s_events_per_baryon_s'][t,j]=site_inner[j]/n
                event_rows.append(dict(index=t,z=float(z[t]),x=float(x[t]),source_index=idx,species=atom_labels[j],threshold_eV=float(thresh[j]),population_per_baryon=float(yy[idx]),photo_gamma_s=float(gamma[j]),event_per_baryon_s=float(tot_evt[j]/n),absorbed_eV_per_baryon_s=float(site_abs[j]/n/EV_J),ion_threshold_eV_per_baryon_s=float(site_ion[j]/n/EV_J),primary_electron_eV_per_baryon_s=float(site_primary[j]/n/EV_J),unresolved_core_eV_per_baryon_s=float(site_core[j]/n/EV_J),Li_1s_event_per_baryon_s=float(site_inner[j]/n)))
            by_bin={
                'event':np.sum(vol_evt,axis=0),
                'abs_W':np.sum(bin_abs,axis=0),
                'ion_W':np.sum(bin_ion,axis=0),
                'primary_W':np.sum(bin_primary,axis=0),
                'core_W':np.sum(bin_core,axis=0)}
            for name,arr in by_bin.items():spectral[name][t,:]=arr
            for b,e in enumerate(edge):
                spectral_rows.append(dict(index=t,z=float(z[t]),bin_index=b,photon_energy_eV=float(e),photon_flux_m2_s=float(flux[b]),photo_event_m3_s=float(by_bin['event'][b]),absorption_W_m3=float(by_bin['abs_W'][b]),ionization_threshold_W_m3=float(by_bin['ion_W'][b]),primary_electron_W_m3=float(by_bin['primary_W'][b]),unresolved_core_W_m3=float(by_bin['core_W'][b])))
            total_abs=float(np.sum(site_abs));total_ion=float(np.sum(site_ion));total_primary=float(np.sum(site_primary));total_core=float(np.sum(site_core));total_inner=float(np.sum(site_inner))
            expected=dict(abs_W_m3=float(ev['photo_absorbed_power_W_m3']),primary_W_m3=float(ev['primary_kinetic_power_W_m3']),core_W_m3=float(ev['unresolved_core_power_W_m3']),inner_count_m3_s=float(ev['li1s_photo_event_rate_m3_s']))
            found=dict(abs_W_m3=total_abs,primary_W_m3=total_primary,core_W_m3=total_core,inner_count_m3_s=total_inner)
            for key in found:max_abs[key]=max(max_abs[key],abs(found[key]-expected[key]))
            max_abs['branch_energy_J_m3_s']=max(max_abs['branch_energy_J_m3_s'],abs(total_abs-total_ion-total_primary-total_core))
            for key,label in [('abs','abs_W_m3'),('primary','primary_W_m3'),('core','core_W_m3')]:
                max_rel[key]=max(max_rel[key],abs(found[label]-expected[label])/max(1e-100,abs(expected[label])))
            sum_epoch['events'][t]=sum(tot_evt)/n
            for key,val in [('abs_eV',total_abs),('ion_eV',total_ion),('primary_eV',total_primary),('core_eV',total_core)]:sum_epoch[key][t]=val/n/EV_J
            sum_epoch['inner_events'][t]=total_inner/n
            epoch_rows.append(dict(index=t,z=float(z[t]),x=float(x[t]),elapsed_s=float(fields['elapsed_s'][t]),H_s=H,nb_m3=n,ne_m3=ne,T_K=T,UV_scale=u,photo_events_per_baryon_s=sum_epoch['events'][t],absorption_eV_per_baryon_s=sum_epoch['abs_eV'][t],ionization_threshold_eV_per_baryon_s=sum_epoch['ion_eV'][t],primary_electron_eV_per_baryon_s=sum_epoch['primary_eV'][t],unresolved_core_eV_per_baryon_s=sum_epoch['core_eV'][t],Li1s_event_per_baryon_s=sum_epoch['inner_events'][t],unresolved_core_fraction_of_abs=total_core/total_abs if total_abs else 0.,primary_fraction_of_abs=total_primary/total_abs if total_abs else 0.))
        # Original stored x clock: dx/dt=H. A diagnostic exposure, not a new IVP.
        Hs=np.asarray(fields['H'],float)
        exposures={key:float(cumulative_simpson(value/Hs,x=x,initial=0.)[-1]) for key,value in sum_epoch.items()}
        nonnegative=True
        for key in ['abs_eV','ion_eV','core_eV','events','inner_events']:
            if np.min(sum_epoch[key])<0:nonnegative=False
        if not nonnegative:raise ValueError('NEGATIVE_PUBLISHED_ENERGY_OR_EVENT')
        # Independently compare integrated spectral photo event counts against
        # the source-native gamma_i multiplied by saved isotope populations.
        gamma_source_events=np.sum(Y[:,indices]*arrays['rate_s'],axis=1)
        max_abs['event_rate_sum_per_baryon_s']=float(np.max(np.abs(gamma_source_events-sum_epoch['events'])))
        if not np.allclose(gamma_source_events,sum_epoch['events'],rtol=3e-14,atol=2e-36):
            raise AssertionError('SOURCE_GAMMA_SPECTRAL_EVENT_DISAGREEMENT')
        summary={
            'schema':'REI_F4_BASS193_PHOTON_ENERGY_LEDGER_V1',
            'claim':'SOURCE_OWNED_SAVED_HISTORY_SPECTRAL_ENERGY_NOT_HEAT',
            'source':{'donor_archive_sha256':DONOR_SHA,'trajectory_sha256':TRAJ_SHA,'BASS_commit':'cc602e209e7deeb511ab2a1f3b2268d55206c43c','network_sha256':hashes['BASS_ATOMIC_NETWORK.py'],'model_sha256':hashes['BASS_ATOMIC_MODEL.json'],'rate_coefficients':'129/129 numeric projection source-matched; raw original coefficient JSON byte owner not newly proved'},
            'counts':{'epochs':N_EXPECT,'photo_species':len(indices),'spectrum_bins':nbins,'site_event_rows':len(event_rows),'spectral_rows':len(spectral_rows),'new_IVPs':0},
            'identities':{'max_abs_native':max_abs,'max_relative_native':max_rel,'max_branch_abs_W_m3':max_abs['branch_energy_J_m3_s']},
            'exposures':exposures,
            'totals':{'max_absorption_eV_per_baryon_s':float(np.max(sum_epoch['abs_eV'])),'max_unresolved_core_eV_per_baryon_s':float(np.max(sum_epoch['core_eV'])),'core_positive_epoch_count':int(np.sum(sum_epoch['core_eV']>0)), 'total_Li_core_energy_fraction_of_abs_exposure':exposures['core_eV']/exposures['abs_eV'],'max_primary_fraction_of_abs':max(r['primary_fraction_of_abs'] for r in epoch_rows),'min_primary_fraction_of_abs':min(r['primary_fraction_of_abs'] for r in epoch_rows)},
            'normalization':'Species per baryon; photon flux bin integrated m^-2 s^-1, proper n_b m^-3, energy W/m^3 and eV/baryon/s; postprocessing integrated fixed saved x/H only',
            'holds':{'photo_energy_is_gas_heat':False,'actual_Auger_or_fluorescence_cascade':False,'secondary_photoelectron_energy_deposition':False,'radiation_photon_evolution':False,'REI_full_source_equivalence':False,'physical_tau':False,'CMB':False,'F4':'PARTIAL','L4_ready':False,'NO_MORE_IVPs':True,'working_DAG':'33/88','central_DAG':'28/88','physical_fast':'4/7','physical_delta':0}}
        arrays.update({'x':x,'z':z,'Y':Y,'photon_energy_eV':edge,'site_indices':np.asarray(indices),'species_names':np.asarray(atom_labels),'H_s':Hs,'nb_m3':fields['nb_m3'],'temperature_K':fields['T_K'],'uv_scale':fields['uv_scale'],'spectrum_flux_base_m2_s':uv0})
        for k,v in spectral.items():arrays['spectral_'+k]=v
        for k,v in sum_epoch.items():arrays['total_'+k]=v
        return summary,epoch_rows,event_rows,spectral_rows,arrays

def generate():
    summary,epochs,events,spectra,arrays=compute()
    out=ROOT/'results';out.mkdir(parents=True,exist_ok=True)
    for name,records in [('PHOTO_ENERGY_193_EPOCHS.csv',epochs),('PHOTO_SITE_2509_EVENT_ROWS.csv',events),('PHOTO_SPECTRUM_13703_BIN_ROWS.csv',spectra)]:
        with (out/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,list(records[0]));w.writeheader();w.writerows(records)
    np.savez_compressed(out/'PHOTO_ENERGY_ATLAS_193.npz',**arrays)
    site_exposures=[]
    for j,name in enumerate(arrays['species_names']):
        record={'species':str(name),'source_index':int(arrays['site_indices'][j])}
        for key in ('abs_ev_per_baryon_s','ion_ev_per_baryon_s','primary_ev_per_baryon_s','core_ev_per_baryon_s','inner_1s_events_per_baryon_s'):
            record[key.replace('_per_baryon_s','_exposure_per_baryon')]=float(cumulative_simpson(arrays[key][:,j]/arrays['H_s'],x=arrays['x'],initial=0.)[-1])
        site_exposures.append(record)
    (out/'PHOTO_SITE_EXPOSURES_13.json').write_text(json.dumps(site_exposures,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (out/'RESULT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return summary

if __name__=='__main__':
    print(json.dumps(generate(),indent=2))
