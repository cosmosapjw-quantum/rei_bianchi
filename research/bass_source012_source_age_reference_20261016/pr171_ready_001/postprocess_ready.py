"""Present saved states only; no provider, helper, solver or rate calls."""
import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

KB_ERG_K = 1.380649e-16
EV_ERG = 1.602176634e-12
MYR_S = 365.25 * 86400 * 1e6
SPECIES = ['H_I', 'H_II', 'He_I', 'He_II', 'He_III', 'electron']
LABELS = ['H I', 'H II', 'He I', 'He II', 'He III', 'electron']
COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#333333']

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def gas_decode(z):
    # Same positive_native.rs::gas_decode inverse map. These are accepted
    # coordinates, never proposed/rejected Runge-Kutta states.
    if z[0] >= 0:
        h = 1 / (1 + math.exp(-z[0]))
    else:
        e = math.exp(z[0])
        h = e / (1 + e)
    maximum = max(float(z[1]), float(z[2]), 0.0)
    neutral, y, zz = (math.exp(-maximum), math.exp(z[1]-maximum),
                       math.exp(z[2]-maximum))
    norm = neutral + y + zz
    return h, y/norm, zz/norm, math.exp(z[3])

def saved_rows(root):
    setup = read(root/'setup.json')
    count = setup['birth_count']
    he = setup['he_h']
    denominator = 1 + 4*he
    result = read(root/'solver_return.json') if (root/'solver_return.json').exists() else None
    endpoint = read(root/'endpoint.json') if (root/'endpoint.json').exists() else None
    observations = read(root/'observations.json') if (root/'observations.json').exists() else []
    source_files = sorted(root.glob('accepted_coordinates_event*.npy'),
                          key=lambda p: int(re.search(r'event(\d+)',p.name)[1]))
    rows = []
    last_time = -math.inf
    for path in source_files:
        event = int(re.search(r'event(\d+)',path.name)[1])
        z = np.load(path, allow_pickle=False)
        h, y, zz, w = gas_decode(z[:4])
        electron_per_h = h + he*(y+2*zz)
        # IgmGasState::eos / HHeModel::temperature, after cancelling n_H.
        # No atomic coefficient evaluation or ODE reconstruction occurs here.
        temperature = 2*(w*EV_ERG)/(3*KB_ERG_K*(1+he+electron_per_h))
        if event < count:
            x, time_s = setup['births'][event], setup['birth_times_s'][event]
            side = 'accepted_pre_birth'
        else:
            if event != count or endpoint is None:
                raise ValueError('Final accepted event lacks serialized native endpoint clock')
            x, time_s = setup['x1'], endpoint['proper_time_s']
            side = 'accepted_terminal'
        assert all(math.isfinite(v) for v in [h,y,zz,w,x,time_s,temperature])
        assert 0 <= h <= 1 and y >= 0 and zz >= 0 and y+zz <= 1
        assert time_s >= last_time and temperature > 0
        last_time = time_s
        abundance = [(1-h)/denominator, h/denominator,
                     he*(1-y-zz)/denominator, he*y/denominator,
                     he*zz/denominator, electron_per_h/denominator]
        assert all(math.isfinite(v) and v >= 0 for v in abundance)
        row = {'accepted_event':event,'side':side,'active_cohorts':min(event,count),
               'ln_a':x,'elapsed_proper_time_s':time_s,
               'elapsed_proper_time_Myr':time_s/MYR_S,
               'temperature_K_from_saved_coordinates':temperature,
               'x_HII':h,'x_HeII':y,'x_HeIII':zz,'w_eV_per_H':w,
               'he_h':he}
        row.update(zip(SPECIES,abundance))
        rows.append(row)
    validation = {'method':'No new helper call: original gas_decode + algebraic H/He EOS; times from serialized native birth_times_s and terminal clock',
                  'EOS_constants':{'kb_erg_K':KB_ERG_K,'ev_erg':EV_ERG},
                  'accepted_rows':len(rows),'birth_count':count,
                  'source_files':[p.name for p in source_files],
                  'solver_return':result,'serialized_observation_rows':len(observations),
                  'baryon_denominator':'n_H+4n_He; H/He-only nuclear inventory',
                  'Gamma_heat_at_decoded_accepted_rows':'NOT_SERIALIZED; not reconstructed',
                  'last_represented_ln_a_fraction':((rows[-1]['ln_a']-setup['x0'])/(setup['x1']-setup['x0'])) if rows else None,
                  'target_interval_complete':bool(result and result['status']=='SCOPED_NUMERICAL_EXECUTION_COMPLETE' and endpoint is not None),
                  'max_baryon_identity_roundoff':max((abs(r['H_I']+r['H_II']+4*(r['He_I']+r['He_II']+r['He_III'])-1) for r in rows),default=None),
                  'max_initial_encoding_roundtrip_abs':max(abs(a-b) for a,b in zip(gas_decode(setup['initial']),setup['initial_physical'][:4]))}
    return rows, validation

def existing_comparison(repo, raw, output):
    result={'reference_to_reference':[], 'native_to_matched_reference':[],
            'not_evaluable':[], 'science_admission':'NOT_ISSUED'}
    task=repo/'research/rei_source_age_positive_native_intake_20261016'
    source=task/'compare_matrix.py'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    expected=read(task/'FINAL_SOURCE_IDENTITY.json')['task_files'][str(source.relative_to(repo))]['sha256']
    assert digest==expected, 'Frozen comparison source differs'
    module=ast.parse(source.read_text())
    threshold=next(ast.literal_eval(n.value) for n in module.body
                   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='THRESHOLD' for t in n.targets))
    inputs=output/'comparison_inputs';inputs.mkdir()
    env={'np':np,'json':json,'root':inputs,'THRESHOLD':threshold}
    functions=ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
    exec(compile(functions,str(source),'exec'),env)
    for new,old in [('age64','age32'),('transport128','transport64')]:
        target=raw/new
        returned=target/'solver_return.json'
        complete=returned.exists() and read(returned)['status']=='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
        if not complete:
            result['not_evaluable'].append({'case':new,'reason':'New reference did not complete; no endpoint target claim'})
            continue
        (inputs/old).symlink_to(task/'evidence/matrix'/old,target_is_directory=True)
        (inputs/new).symlink_to(target.resolve(),target_is_directory=True)
        result['reference_to_reference'].append(env['compare'](old,new,'reference_to_reference'))
        native=raw/(new+'_native')
        if (native/'endpoint.json').exists():
            (inputs/(new+'_native')).symlink_to(native.resolve(),target_is_directory=True)
            result['native_to_matched_reference'].append(env['compare'](new+'_native',new,'native_to_matched_reference'))
        else:
            result['not_evaluable'].append({'case':new+'_native','reason':'Native endpoint absent; paired native/reference accuracy NOT_EVALUABLE'})
    result['unchanged_comparison_source_SHA256']=digest
    result['inherited_finest_neighbor_target']=threshold
    write(output/'COMPARISON.json',result)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw',type=Path,required=True)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir()
    plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans'})
    summaries={};figures=[]
    for name in ['age64','transport128']:
        root=args.raw/name
        if not(root/'setup.json').exists():
            summaries[name]={'state':'NOT_STARTED_OR_SETUP_NOT_SAVED'};continue
        rows,summary=saved_rows(root);summaries[name]=summary
        if not rows:
            continue
        with (args.output/(name+'_accepted_Y.csv')).open('x',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        values=np.array([[r[k] for k in SPECIES] for r in rows])
        scope='completed short reference' if summary['target_interval_complete'] else 'accepted prefix; target interval incomplete'
        for coordinate in ['time','Tgas_chronological']:
            xs=np.array([r['elapsed_proper_time_Myr'] if coordinate=='time' else r['temperature_K_from_saved_coordinates'] for r in rows])
            fig,(gas,electrons)=plt.subplots(2,1,sharex=True,figsize=(9.8,7.1),layout='constrained',gridspec_kw={'height_ratios':[3,1]})
            for j in range(5):
                gas.plot(xs,np.ma.masked_where(values[:,j]==0,values[:,j]),label=LABELS[j],color=COLORS[j],marker='.',markersize=3)
            electrons.plot(xs,np.ma.masked_where(values[:,5]==0,values[:,5]),label='electron',color=COLORS[5],marker='.',markersize=3)
            for ax in [gas,electrons]:ax.set_yscale('log');ax.grid(alpha=.2);ax.legend(ncol=3 if ax is gas else 1)
            gas.set_ylabel(r'$Y_i=n_i/(n_H+4n_{He})$');electrons.set_ylabel(r'$Y_e$')
            if coordinate=='time':electrons.set_xlabel('Elapsed proper time since native a0 = 1/21 [Myr]');electrons.set_xlim(left=0)
            else:
                electrons.set_xlabel('Gas temperature [K]; chronological saved-state path')
                for ax,j in [(gas,0),(electrons,5)]:
                    for k in [len(rows)//3,2*len(rows)//3]:
                        if 0<k<len(rows) and values[k-1,j]>0 and values[k,j]>0:
                            ax.annotate('',xy=(xs[k],values[k,j]),xytext=(xs[k-1],values[k-1,j]),arrowprops={'arrowstyle':'->','color':COLORS[j]})
            gas.set_title(name+' | '+scope+'\nWarm analytic MD14 H/He; accuracy HOLD; no full EoR admission')
            gas.text(.01,.015,f'{len(rows)} saved accepted states; exact zeros masked; no invented t=0 state',transform=gas.transAxes,fontsize=8)
            electrons.text(.01,.03,'T: original coordinate inverse + algebraic native EOS; no new provider/RHS',transform=electrons.transAxes,fontsize=8)
            for extension in ['png','pdf']:
                file=args.output/(name+'_Y_vs_'+coordinate+'.'+extension);fig.savefig(file,dpi=160);figures.append(file.name)
            plt.close(fig)
    comparison=existing_comparison(args.repo,args.raw,args.output)
    write(args.output/'PRESENTATION_RECEIPT.json',{'cases':summaries,'figures':figures,
         'new_physical_or_helper_calls':0,'decoded_saved_coordinates':True,
         'T_sorted':False,'zero_population_floors':False,'synthetic_initial_states':False,
         'unimplemented_isotope_zeros_added':False,'science_admission':'NOT_ISSUED',
         'comparison_mechanical_labels_only':True,'versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__}})
    print(json.dumps({'figures':figures,'case_accepted_rows':{k:v.get('accepted_rows') for k,v in summaries.items()},'comparison_pairs':len(comparison['reference_to_reference'])}))

if __name__=='__main__':main()
