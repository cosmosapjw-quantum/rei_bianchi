"""One bounded algebraic history diagnostic; never calls an IVP solver."""
import csv
import json
import numpy as np
from history import UNIT,PREVIOUS,old,baseline,diagnose,five_fixed_point,envelope_step


def main():
    data=baseline();c=old.config();d=diagnose(data,c)
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    header=['eta','z_mean','elapsed_proper_s','H_s-1','nHref_cm-3','Sfast_n','Sfast_T','kcap_s-1',
            'QSS_Bn','QSS_BT','QSS_n','QSS_T0','QSS_T1']
    for fam in ('neutron','tritium'):
        header.extend([fam+'_'+key for key in ('QSS_l1','initial_bound','variation_bound','total_bound','relative_bound','certified_1percent')])
    header.extend(['Lfast_n_s-1','Lfast_T_s-1','Lthermal_n_s-1','Lthermal_T_s-1',
                   'interval_end_elapsed_s','neutron_interval_c_s-1','tritium_interval_c_s-1',
                   'neutron_interval_M_per_Href_s','tritium_interval_M_per_Href_s'])
    lf=[c['ks_'+j+'_s']+c['ke_'+j+'_s']+c['lambda_'+j+'_s']/c['gamma_'+j] for j in ('n','T')]
    with (out/'source_history_qss.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(header)
        for k in range(201):
            row=[data['eta'][k],data['z'][k],data['t'][k],data['H'][k],data['nref'][k],*d['S'][k],d['kcap'][k],*d['fixed'][k]]
            for j in range(2):row.extend([d[key][k,j] for key in ('norms','initial','variation','bound','relative','certified')])
            row.extend([*lf,c['lambda_n_s']+d['kcap'][k]+c['kesc_s'],c['lambda_T_s']+c['kesc_s']])
            row.extend([data['t'][k+1],*d['contraction'][k],*d['M'][k]] if k<200 else ['']*5)
            writer.writerow(row)
    # Analytic envelope inside the first saved interval resolves turn-on even
    # though the next saved epoch is much later than the reservoir lifetimes.
    delta=np.r_[0.,np.geomspace(1e-3,min(data['t'][1],100/min(d['contraction'][0])),240)]
    fraction=delta/data['t'][1]
    fixed=five_fixed_point(d['S'][0]+fraction[:,None]*(d['S'][1]-d['S'][0]),
                          d['kcap'][0]+fraction*(d['kcap'][1]-d['kcap'][0]),c)
    norms=np.column_stack([fixed[:,[0,2]].sum(axis=1),fixed[:,[1,3,4]].sum(axis=1)])
    envelope=envelope_step(d['norms'][0],d['M'][0],d['contraction'][0],delta[:,None])
    relative=envelope/norms
    with (out/'initial_transient_envelope.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['elapsed_proper_s','neutron_relative_bound','tritium_relative_bound'])
        writer.writerows(np.column_stack([delta,relative]))
    identities={str(p.relative_to(UNIT.parent)):old.digest(p) for p in [old.CSV_PATH,old.NPZ_PATH,PREVIOUS/'model.py',PREVIOUS/'config.json',UNIT/'theory/FROZEN_CONTRACT.md']}
    summary={'status':'COMPLETED_NON_IVP','n_saved_epochs':201,'clock':data['clock_check'],
        'elapsed_proper_s_endpoint':float(data['t'][-1]),'input_identities':identities,
        'initial_condition':'All five n/T stocks zero; source turn-on at t=0',
        'family_certificates':d['summary'],'interval_certification':d['interval_certification'],
        'history':'constant replenished external forcing; affine Sfast/kcap in reconstructed proper time',
        'claim':'Analytic history-error envelope for illustrative finite reconstruction, not measured dynamics or astrophysical calibration',
        'IVP_execution':'NOT_RUN','sample_only_certification':True}
    summary['CSV_interval_convention']='At row k<200, c and M apply to [t_k,t_(k+1)]. Final row interval fields empty, not zero.'
    (out/'SOURCE_HISTORY_RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
