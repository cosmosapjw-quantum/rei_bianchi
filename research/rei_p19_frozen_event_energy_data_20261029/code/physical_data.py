"""Finite source-backed P19 UVB and frozen REI photo-event/energy tables.

No IVP, no full REI chemistry, no BASS physical projection, no tau integration.
Physical units: rate s^-1, populations particles/Href, power eV/Href/s.
The P19 D1 homogeneous UV background and saved REI ON_refined populations
are DIFFERENT source-model histories. Their pointwise product is a HYBRID
conditional diagnostic, not a self-consistent evolution or observed datum.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PR261 = ROOT / 'research/rei_uvb_six_moment_response_20261029'
PR262 = ROOT / 'research/rei_uvb_saved_state_source_tangent_20261029'
sys.path.insert(0, str(PR262 / 'code'))
import source17 as s  # noqa: E402

IMMUTABLE = {
  'p19_numeric_projection': (PR261/'source/PUCHWEIN2019_13_ROW_PROJECTION.json','dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff'),
  'bb13_gls': (PR261/'source/FROZEN_BB13_SUPPORT_INPUT.json','13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b'),
  'rei_7_saved': (PR262/'source/ON_REFINED_7_SAVED_ROWS.json','7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77'),
  'rei_source17_code': (PR262/'code/source17.py','3e8735874b53516dfe2df781598aaf77407fd12e64b72c048f257982cbb2812f'),
  'p19_response_code': (PR261/'code/source_response.py','d594a54d51160e182458dab2c0a524af524784cd3e809493b940f81e788744e4'),
}

def source_hashes():
    out = {}
    for label, (path, expected) in IMMUTABLE.items():
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'SOURCE_IDENTITY_MISMATCH {label}: {actual} != {expected}')
        out[label] = actual
    return out


def save_csv(path, records, fields):
    path.parent.mkdir(exist_ok=True,parents=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='raise')
        writer.writeheader()
        writer.writerows(records)


def calc():
    digests=source_hashes()
    port,bb,p19,rows,geo=s.load_parent()
    saved=s.saved_rows()
    assert s.structural_check()
    # model D1 P19 exactly as archived; not equilibrium D2, not observed data
    p19_table=[]
    for z,gh,hh,gi,hi,gii,hii in p19['rows']:
        if any(v<=0 for v in (gh,hh,gi,hi,gii,hii)):
            raise ValueError('NONPOSITIVE_P19_SOURCE')
        p19_table.append(dict(z=z,Gamma_HI_per_s=gh,Gamma_HeI_per_s=gi,Gamma_HeII_per_s=gii,
                              Heat_HI_eV_per_target_s=hh,Heat_HeI_eV_per_target_s=hi,
                              Heat_HeII_eV_per_target_s=hii,
                              Excess_HI_eV_per_event=hh/gh,
                              Excess_HeI_eV_per_event=hi/gi,
                              Excess_HeII_eV_per_event=hii/gii,
                              t_HI_photo_s=1/gh,t_HeII_photo_s=1/gii))
    # matched epochs: seven saved snapshots, both fiducial P19 and optional BB13 GLS
    event_rows=[];epoch_rows=[];checks=[]
    for j,rec in enumerate(saved):
        y=np.asarray(rec['y'],dtype=float)
        z=float(rec['z'])
        for label,a in (('P19_D1_fiducial',(0.0,0.0)),('P19_D1_BB13_GLs_nominal',geo['a0'])):
            out=s.source17(z,y,a,rows,port)
            rn=np.asarray(out['rate_moments'],dtype=float)
            sum_events=0.0;sum_heat=0.0;sum_ion=0.0;sum_abs=0.0
            for k,(start,stop,rate_id,thr) in enumerate(s.EVENTS):
                idx=int(s.SRC[k]);pop=float(y[idx]);gamma=float(rn[2*rate_id]);heat=float(rn[2*rate_id+1]);events=pop*gamma
                q_heat=pop*heat;q_ion=float(thr)*events;q_abs=q_heat+q_ion
                event_rows.append(dict(scenario=label,saved_index=j,saved_z=z,target_z=rec['target_z'],
                    elapsed_proper_s=rec['elapsed_proper_s'],event_index=k+1,from_state=start,to_state=stop,
                    P19_rate_channel=('HI','HeI','HeII')[rate_id],
                    frozen_rei_population_per_Href=pop,
                    gamma_per_target_s=gamma,heat_per_target_eV_s=heat,
                    excess_energy_eV_per_ionization=heat/gamma,
                    ionization_threshold_eV=float(thr),
                    photoelectrons_created_per_Href_s=events,
                    photoheat_eV_per_Href_s=q_heat,
                    ionization_storage_eV_per_Href_s=q_ion,
                    absorbed_photon_eV_per_Href_s=q_abs))
                sum_events+=events;sum_heat+=q_heat;sum_ion+=q_ion;sum_abs+=q_abs
            QF=float(s.Q@out['F']); AF=float(s.A@out['F'])
            err_e=abs(sum_events-float(out['electron_rate_per_Href_s']))
            err_h=abs(sum_heat-float(out['photoheat_eV_per_Href_s']))
            err_store=abs(sum_ion-float(out['ionization_storage_eV_per_Href_s']))
            err_abs=abs(sum_abs-sum_heat-sum_ion)
            checks.append(dict(scenario=label,saved_index=j,epoch_index=j,charge_difference=abs(QF-sum_events),baryon_residual=abs(AF),
                               event_difference=err_e,heat_difference=err_h,storage_difference=err_store,
                               absorbed_energy_ledger_difference=err_abs))
            epoch_rows.append(dict(scenario=label,saved_index=j,saved_z=z,target_z=rec['target_z'],
                elapsed_proper_s=rec['elapsed_proper_s'],photoelectrons_created_per_Href_s=sum_events,
                photoheat_eV_per_Href_s=sum_heat,ionization_storage_eV_per_Href_s=sum_ion,
                absorbed_photon_eV_per_Href_s=sum_abs,
                mean_photoheat_eV_per_photoionization=sum_heat/sum_events,
                mean_threshold_eV_per_photoionization=sum_ion/sum_events,
                mean_absorbed_photon_eV_per_photoionization=sum_abs/sum_events,
                total_17_state_ionic_charge_per_Href=float(s.Q@y),
                model_rate_scale_factor=float(port.rate_response(z,a,rows)['factor'])))
    prior=s.run_saved()
    ref={row['saved_z']:row for row in prior['entries']}
    for row in epoch_rows:
        if row['scenario'].endswith('nominal'):
            old=ref[row['saved_z']]
            for key,curr in [('electron_creation_per_Href_s','photoelectrons_created_per_Href_s'),
                             ('photoheat_eV_per_Href_s','photoheat_eV_per_Href_s'),
                             ('ionization_storage_eV_per_Href_s','ionization_storage_eV_per_Href_s'),
                             ('absorbed_photon_eV_per_Href_s','absorbed_photon_eV_per_Href_s')]:
                if not math.isclose(float(old[key]),float(row[curr]),rel_tol=5e-14,abs_tol=1e-40):
                    raise AssertionError(f'PREDECESSOR_CROSSCHECK_FAILED z={row["saved_z"]} field={key}')
    for row in checks:
        if row['charge_difference']>5e-29 or row['baryon_residual']>5e-28:
            raise AssertionError('EXACT_EVENT_CONSERVATION_FAILED')
        if any(row[k]>2e-28 for k in ('event_difference','heat_difference','storage_difference','absorbed_energy_ledger_difference')):
            raise AssertionError('PHOTO_EVENT_ENERGY_LEDGER_FAILED')
    return digests,p19_table,epoch_rows,event_rows,checks,{'beta':float(geo['a0'][0]),'kappa':float(geo['a0'][1])}


def run(out_dir=None):
    if out_dir is None:out_dir=ROOT/'results'
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    digests,table,epochs,events,checks,a=calc()
    save_csv(out_dir/'P19_FIDUCIAL_13_KNOT_PHYSICAL_RATES.csv',table,list(table[0]))
    save_csv(out_dir/'REI_FROZEN_7_EPOCH_PHYSICAL_SOURCE.csv',epochs,list(epochs[0]))
    save_csv(out_dir/'REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv',events,list(events[0]))
    save_csv(out_dir/'REI_FROZEN_PHOTO_SOURCE_CHECKS.csv',checks,list(checks[0]))
    obj={'schema':'REI_P19_FROZEN_EVENT_ENERGY_LEDGER_V1','source_hashes':digests,
        'saved_rows':7,'p19_knots':len(table),'physical_scenarios':2,
        'epoch_rows':len(epochs),'event_rows':len(events),'diagnostic_checks':len(checks),
        'units':{'time':'proper s (original saved only)','event':'photoelectrons/Href/s',
          'energy':'eV/Href/s','rate':'s^-1','photons':'conditional absorbed energy eV/Href/s'},
        'invariants':{'event_column_electron':'+1','baryon':'0','energy':'Q_abs=Q_heat+Q_ion',
          'double_counting':'NOT_ALLOWED'},
        'bb13_gls_nominal_beta_kappa':a,
        'pointwise_only':True,'actual_coupled_UVB_trajectory':None,'full_heating_cooling_ODE':None,
        'physical_tau':None,'nHref_H_K_directional_redshift':None,'new_ivps':0,
        'source_scope':'Puchwein 2019 Table D1 13 selected source knots; positive six moments, log-interpolated; 7 ON_refined original saved y from distinct source; isotopic rate-equality REI source assumption; no BASS UV spectrum binding',
        'original_rei_DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','delta':0},
        'max_charge_residual':max(r['charge_difference'] for r in checks),
        'max_baryon_residual':max(r['baryon_residual'] for r in checks),
        'max_energy_ledger_residual':max(r['absorbed_energy_ledger_difference'] for r in checks)}
    (out_dir/'RESULT.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    return obj

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
