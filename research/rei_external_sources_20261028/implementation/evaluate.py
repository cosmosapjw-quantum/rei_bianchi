"""One 201-epoch pointwise algebraic evaluation; does not solve an IVP."""
import csv
import json
from pathlib import Path
import numpy as np
import model as m


def main():
    eta,z,base,hidden,nref=m.load_baseline();c=m.config(); rows=[]
    maxima={'relative_baryon_balance':0.,'relative_charge_balance':0.,'relative_energy_balance':0.,'relative_qss_residual':0.}
    for i in range(201):
        r=m.reservoirs(base[i],1,c);q=m.qss(base[i],nref[i],1,c,r)
        ys=base[i].copy();ys[[0,5,6]]=q['stocks']
        baseline=m.evaluate_operator(base[i],nref[i],1,c,res=r)
        out=m.evaluate_operator(ys,nref[i],1,c,res=r)
        row={'epoch':i,'eta_ln_a_over_ai':float(eta[i]),'z_mean':float(z[i]),'nHref_cm3':float(nref[i])}
        for state_index,label in enumerate(m.LABELS):
            row['baseline_per_Href__'+label]=float(base[i,state_index])
            row['source_baseline_per_Href_s__'+label]=float(baseline['dy'][state_index])
            row['source_at_qss_per_Href_s__'+label]=float(out['dy'][state_index])
        for j,label in enumerate(m.HIDDEN):
            row['baseline_per_Href__'+label]=float(hidden[i,j]);row['new_source_per_Href_s__'+label]=0.
        for alpha in c['alphas']:
            qa=m.qss(base[i],nref[i],alpha,c)
            for j,label in enumerate(('n','T_0','T_1')):row[f'qss_alpha{alpha}_per_Href__{label}']=float(qa['stocks'][j])
        for j,kind in enumerate(('n','T')):
            row['fast_stock_per_Href__'+kind]=float(r['B'][j])
            row['fast_kinetic_stock_eV_per_Href__'+kind]=float(r['U'][j])
            row['fast_source_per_Href_s__'+kind]=float(r['S'][j])
            row['tau_fast_s__'+kind]=float(1/r['L'][j])
            for b,branch in enumerate(('slowing','escape','beta')):
                row['fast_fraction_'+branch+'__'+kind]=float(r['fractions'][j,b])
        row['tau_thermal_n_s']=float(q['tau_s'][0]);row['tau_thermal_T_s']=float(q['tau_s'][1])
        row['T_photoionization_s']=q['Gamma'];row['n_capture_hazard_s']=q['kcap']
        for name,value in out['rates'].items():row['event_per_Href_s__'+name]=value
        for name,value in out['power'].items():row['power_eV_per_Href_s__'+name]=float(value)
        for key in ('electron_rate','external_baryon_rate','external_charge_rate','baryon_residual','charge_residual','energy_residual','absorbed_photon_rate','escaped_particle_rate'):row[key]=float(out[key])
        row['photon_absorption_drain_cm3_s']=nref[i]*out['absorbed_photon_rate']
        scaleA=max(float(np.sum(np.abs(m.A*out['dy']))),abs(out['external_baryon_rate']),1e-300)
        scaleQ=max(float(np.sum(np.abs(m.Q*out['dy']))),abs(out['electron_rate']),1e-300)
        scaleE=max(sum(abs(v) for v in out['power'].values()),1e-300)
        scaleS=max(float(np.max(q['sources'])),1e-300)
        checks={'relative_baryon_balance':abs(out['baryon_residual'])/scaleA,'relative_charge_balance':abs(out['charge_residual'])/scaleQ,
                'relative_energy_balance':abs(out['energy_residual'])/scaleE,'relative_qss_residual':float(np.max(np.abs(out['dy'][[0,5,6]])))/scaleS}
        for key,value in checks.items():maxima[key]=max(maxima[key],value)
        if not np.isfinite(list(row.values())).all():raise ValueError('nonfinite output row')
        rows.append(row)
    if any(v>1e-12 for v in maxima.values()):raise ValueError('contractual balance/QSS residual exceeded')
    outdir=m.UNIT/'outputs';outdir.mkdir(exist_ok=True)
    table=outdir/'external_source_response.csv'
    with table.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'schema':'REI_EXTERNAL_POINTWISE_V1','status':'EVALUATED_PENDING_INDEPENDENT_ADMISSION','epoch_count':201,
             'scope':'Illustrative, uncalibrated; frozen-epoch QSS, not a time-evolution solution',
             'units':{'stocks':'particles/Href','event_rates':'events/Href/proper-second','powers':'eV/Href/proper-second','nHref':'cm^-3'},
             'input_identity':{'baseline_csv_sha256':m.digest(m.CSV_PATH),'baseline_npz_sha256':m.digest(m.NPZ_PATH),'contract_sha256':m.digest(m.UNIT/'theory/FROZEN_CONTRACT.md'),'config_sha256':m.digest(Path(__file__).with_name('config.json'))},
             'density':{'source':'matching ANGTHERM01 grid044_M4_nominal NPZ nHref','shape':list(nref.shape),'eta_serialization_alignment_pass':True,'eta_atol':5e-15,'cm3_endpoints':[float(nref[0]),float(nref[-1])]},
             'state_order':list(m.LABELS),'hidden_Li6':'copied numerically unchanged; all new-source derivatives exact zero',
             'maxima':maxima,'alphas':c['alphas'],'tau_fast_s':{kind:float(1/r['L'][j]) for j,kind in enumerate(('n','T'))},
             'tau_thermal_n_s_range':[min(x['tau_thermal_n_s'] for x in rows),max(x['tau_thermal_n_s'] for x in rows)],
             'tau_thermal_T_s':float(q['tau_s'][1]),'parameter_conventions':c,
             'limits':['No time integration or accumulated events; targets outside n/T held at baseline.','QSS timescale validity needs source history/background comparison; not inferred here.','Inverse weak bath NOT_INCLUDED_BY_MODEL.','Finite photon/CR bins and toy cross sections are uncalibrated.','Injection/escape matter rest mass is outside excess-energy ledger; effective Q-value bookkeeping only.','Beta T atomic shifts, recoil, transport, inverse channels, and directional observables omitted.'],
             'selected_rows':[rows[i] for i in (0,100,200)],'output_csv_sha256':m.digest(table)}
    (outdir/'external_source_response.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'epochs':201,'maxima':maxima,'density':summary['density'],'csv_columns':len(rows[0])}))


if __name__=='__main__':main()
