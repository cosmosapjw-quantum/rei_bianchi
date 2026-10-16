"""Analyze only fresh source-locked NCP runs; preserve original PR159 raw separately."""
import csv, gzip, json, math, re, sys
from pathlib import Path
from audit_pr159 import load_raw

root=Path(sys.argv[1])
exits=list(csv.DictReader((root/'exits.csv').open()))
original,_=load_raw()
fields=('temperature_k','x_hii','x_heii','x_heiii','source_n_per_h','source_u_ev_per_h')
rows={}
for e in exits:
    mode,case,n=e['mode'],e['case'],int(e['steps'])
    d=root/f'{mode}_{case}_{n}'
    o=d/'output'
    result=json.loads((o/'result.json').read_text()) if (o/'result.json').exists() else None
    owner=json.loads((o/'owner_rates.json').read_text()) if (o/'owner_rates.json').exists() else None
    trace=list(csv.DictReader((o/'step_trace.csv').open())) if (o/'step_trace.csv').exists() else []
    stderr=(d/'stderr.log').read_text()
    newton=[float(x) for x in re.findall(r'BASS_NEWTON .*? norm=([0-9.eE+-]+)',stderr)]
    cond=[float(x) for x in re.findall(r'BASS_JACOBIAN .*? cond1_est=([0-9.eE+-]+)',stderr)]
    tau={'old':{'min':[math.inf]*3,'max':[0.0]*3,'weighted':[0.0]*3,'weight':0.0},
         'newborn':{'min':[math.inf]*3,'max':[0.0]*3,'weighted':[0.0]*3,'weight':0.0}}
    kernel_bias={'old_be_minus_exponential_number_per_h':0.0,
                 'newborn_be_minus_uniform_number_per_h':0.0,
                 'old_be_minus_exponential_energy_ev_per_h':0.0,
                 'newborn_be_minus_uniform_energy_ev_per_h':0.0}
    optical=o/'optical_nodes.csv.gz'
    accepted_nodes=0
    if optical.exists():
        for t in csv.DictReader(gzip.open(optical,'rt')):
            if t['opacity_phase']!='accepted': continue
            accepted_nodes+=1
            cohort=t['cohort'];w=float(t['number_per_h']);tau[cohort]['weight']+=w
            for j,k in enumerate(('tau_hi','tau_hei','tau_heii')):
                v=float(t[k]);tau[cohort]['min'][j]=min(tau[cohort]['min'][j],v)
                tau[cohort]['max'][j]=max(tau[cohort]['max'][j],v);tau[cohort]['weighted'][j]+=w*v
            total=sum(float(t[k]) for k in ('tau_hi','tau_hei','tau_heii'))
            if total<1e-5:
                phi=1+total*(-0.5+total*(1/6+total*(-1/24+total/120)))
            else:
                phi=-math.expm1(-total)/total
            bias=w*(1/(1+total)-(math.exp(-total) if cohort=='old' else phi))
            label=('old_be_minus_exponential' if cohort=='old' else 'newborn_be_minus_uniform')
            kernel_bias[label+'_number_per_h']+=bias
            kernel_bias[label+'_energy_ev_per_h']+=bias*float(t['energy_physical_ev'])
    else:
        summarized=o/'optical_distribution.json.gz'
        compact_path=o/'optical_compact.json'
        if compact_path.exists() or summarized.exists():
            if compact_path.exists():
                compact=json.loads(compact_path.read_text())
                groups=compact['step_species_distributions']
            else:
                with gzip.open(summarized,'rt') as f: compact=json.load(f)
                groups=compact['groups']
            accepted_nodes=compact.get('accepted_nodes',0)
            for g in groups:
                if g['phase']!='accepted': continue
                data=tau[g['cohort']];j=('hi','hei','heii').index(g['species'])
                weight=g['photon_weight_per_h']
                data['min'][j]=min(data['min'][j],g['tau_min'])
                data['max'][j]=max(data['max'][j],g['tau_max'])
                data['weighted'][j]+=weight*g['tau_weighted_mean'] if g['tau_weighted_mean'] is not None else 0.0
                if j==0: data['weight']+=weight
            kernel_bias=compact.get('frozen_kernel_counterfactual')
    tau_summary={cohort:{'min':[x if x!=math.inf else None for x in data['min']],
                         'max':data['max'],'number_weighted_mean':[x/data['weight'] if data['weight'] else None for x in data['weighted']]}
                 for cohort,data in tau.items()}
    max_source_residual=max((abs(float(t['source_residual_per_h'])) for t in trace),default=None)
    temperature_min=min((float(t['temperature_k']) for t in trace),default=None)
    archived_time=original[f"release_{'cold' if case=='COLD_FLRW' else 'signed'}_long_g481"]['time_s']
    endpoint_ok=(result is not None and result.get('grid_points')==481 and result.get('case')==case
        and math.isfinite(result.get('a',float('nan'))) and abs(result['a']-(1/21)*math.exp(4e-4))<1e-13
        and math.isfinite(result.get('time_s',float('nan'))) and abs(result['time_s']-archived_time)<100.0)
    physics_ok=(result is not None and owner is not None
        and math.isfinite(owner.get('owner_normalized',float('nan')))
        and abs(owner['owner_normalized'])<=1e-12
        and all(math.isfinite(result.get(k,float('nan'))) for k in
        ('temperature_k','photon_normalized','energy_normalized','max_hamiltonian_normalized','max_raychaudhuri_normalized'))
        and abs(result['photon_normalized'])<=1e-8 and abs(result['energy_normalized'])<=1e-8
        and result['max_hamiltonian_normalized']<=3e-12 and result['max_raychaudhuri_normalized']<=1e-9
        and result['temperature_k']>0 and temperature_min is not None and temperature_min>0
        and (max_source_residual is not None and max_source_residual<=1e-10)
        and 0<=result['x_hii']<=1 and result['x_heii']>=0 and result['x_heiii']>=0
        and result['x_heii']+result['x_heiii']<=1)
    execution_complete=(int(e['exit_code'])==0 and result is not None and len(trace)==n
        and result['steps']==n and result['restart_max_abs']==0.0
        and result['adaptive_status']=='ACCEPTED' and result['adaptive_accepted']>0
        and abs(result['dln_a']*n-4e-4)<=1e-15)
    rows[f'{mode}/{case}/{n}']={
        'exit_code':int(e['exit_code']),'result':result,'owner_rates':owner,'trace_rows':len(trace),
        'execution_complete':execution_complete,'endpoint_ok':endpoint_ok,'physics_ok':physics_ok,
        'accepted':execution_complete and endpoint_ok and physics_ok,
        'newton_iteration_residual_max':max(newton,default=None),
        'newton_iteration_count':len(newton),'jacobian_cond1_est_max':max(cond,default=None),
        'optical_tau_by_cohort':tau_summary,
        'frozen_kernel_counterfactual':({**kernel_bias,
             'combined_number_per_h':kernel_bias['old_be_minus_exponential_number_per_h']+kernel_bias['newborn_be_minus_uniform_number_per_h'],
             'combined_energy_ev_per_h':kernel_bias['old_be_minus_exponential_energy_ev_per_h']+kernel_bias['newborn_be_minus_uniform_energy_ev_per_h'],
             'accepted_nodes':accepted_nodes,
             'scope':'separate-cohort quadrature at accepted opacity; counterfactual for merged-moment legacy; not native global error'}
             if accepted_nodes and kernel_bias is not None else
             {'status':'NOT_MEASURED','accepted_nodes':accepted_nodes}),
        'max_step_source_residual_per_h':max_source_residual,
        'min_step_temperature_k':temperature_min,
        'old_photons_first_step':float(trace[0]['old_photons_per_h']) if trace and 'old_photons_per_h' in trace[0] else None,
        'newborn_photons_first_step':float(trace[0]['newborn_photons_per_h']) if trace and 'newborn_photons_per_h' in trace[0] else None,
        'time_record':(d/'time.txt').read_text().strip() if (d/'time.txt').exists() else None,
    }
baseline={}
for case,tag in [('COLD_FLRW','cold'),('SIGNED_MINUS','signed')]:
    for n,name in [(4,'g481'),(8,'t8'),(16,'t16')]:
        old=original[f'release_{tag}_long_{name}']
        row=rows.get(f'original/{case}/{n}',{})
        now=row.get('result') if row.get('accepted') else None
        if now:
            baseline[f'{case}/{n}']={k:now[k]-old[k] for k in fields}
convergence={}
for mode in ('original','legacy_trace','tight_newton','split_be','tight_split_be','uniform_birth','tight_uniform_birth'):
    for case in ('COLD_FLRW','SIGNED_MINUS'):
        seq=[(r.get('result') if r.get('accepted') else None) for n in (4,8,16,32,64,128)
             for r in [rows.get(f'{mode}/{case}/{n}',{})]]
        if all(seq):
            curves={}
            for k in fields:
                values=[x[k] for x in seq]
                diffs=[values[i]-values[i+1] for i in range(5)]
                curves[k]={'values':values,'signed_successive_differences':diffs,
                    'absolute_successive_ratios':[abs(diffs[i]/diffs[i+1]) if diffs[i+1] else None for i in range(4)]}
            convergence[f'{mode}/{case}']=curves
ablation={}
for case in ('COLD_FLRW','SIGNED_MINUS'):
    for n in (4,8,16,32,64,128):
        original_row=rows.get(f'original/{case}/{n}',{})
        base=original_row.get('result') if original_row.get('accepted') else None
        if base:
            for mode in ('legacy_trace','tight_newton','split_be','tight_split_be','uniform_birth','tight_uniform_birth'):
                alt_row=rows.get(f'{mode}/{case}/{n}',{})
                alt=alt_row.get('result') if alt_row.get('accepted') else None
                if alt: ablation[f'{case}/{n}/{mode}']={k:alt[k]-base[k] for k in fields}
checks={}
for key,row in rows.items():
    r=row['result']
    if r and row['accepted']:
        checks[key]={
            'restart_exact':r['restart_max_abs']==0.0,
            'photon_ledger_within_original_1e_8':abs(r['photon_normalized'])<=1e-8,
            'energy_ledger_within_original_1e_8':abs(r['energy_normalized'])<=1e-8,
            'hamiltonian_within_original_3e_12':r['max_hamiltonian_normalized']<=3e-12,
            'positive_temperature':r['temperature_k']>0 and (row['min_step_temperature_k'] or 0)>0,
            'physical_fractions':0<=r['x_hii']<=1 and 0<=r['x_heii'] and 0<=r['x_heiii'] and r['x_heii']+r['x_heiii']<=1,
            'source_midpoint_residual_within_1e_10':(row['max_step_source_residual_per_h'] or 0)<=1e-10,
        }
out={'schema':'rei.bass.longstep.native_causal.v1','source':'PR162 HEAD 6f0864e017e2d1df8cae932263b7eebc917df302 + new opt-in native diff',
     'grid_points':481,'total_dln_a':4e-4,'steps':[4,8,16,32,64,128],
     'units':{'temperature_k':'K','source_n_per_h':'photons/H','optical_tau':'dimensionless','newton_norm':'dimensionless'},
     'original_pr159_replay_difference':baseline,'rows':rows,'checks':checks,
     'convergence':convergence,'ablation_against_original':ablation}
print(json.dumps(out,indent=2,sort_keys=True))
