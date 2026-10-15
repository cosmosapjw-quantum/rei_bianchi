#!/usr/bin/env python3
"""Read-only, completion-gated FLRW plots and diagnostic grid-pair reduction."""
import argparse,csv,hashlib,json,math,sys,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
import compare_histories as reader
from source_pair_guard import require_source_relation
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
MYR=365.25*86400*1e6
COLORS={'x_HI':'#1d567b','x_HII':'#d38418','x_HeI':'#1d567b','x_HeII':'#d38418','x_HeIII':'#96517c'}
LABELS={'x_HI':'H I','x_HII':'H II','x_HeI':'He I','x_HeII':'He II','x_HeIII':'He III'}
ROLES={'history':'history.csv','abundances':'abundances.csv','config':'config.cfg','source_identity':'source_identity.txt','terminal':'RETURN.txt','ledger':'ledgers.csv','checkpoint':'checkpoint.txt'}
class Hold(ValueError):pass
def sha(p):return reader.hashfile(p)
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def parse(p):return dict(line.split('=',1) for line in p.read_text().splitlines() if '=' in line)
def frozen_full005_guard(case,binding):
    base=Path(__file__).resolve().parent
    plan=json.loads((base/'FULL005_RESOURCE_PLAN.json').read_text())
    expected=json.loads((base/'FULL005_EXPECTED_BINDINGS.json').read_text())['bindings']
    cases={c['case']:c for c in plan['cases']}
    if case not in cases or case not in expected:raise Hold('UNEXPECTED_FROZEN_FULL005_CASE')
    frozen=expected[case]
    if frozen['source_identity_sha256']!=plan['source_identity_sha256'] or frozen['binary_sha256']!=plan['binary_sha256'] or frozen['base_config_sha256']!=cases[case]['config_sha256']:raise Hold('FROZEN_FULL005_PLAN_BINDING_DISAGREEMENT')
    if binding.get('case')!=case:raise Hold('FROZEN_FULL005_CASE_BINDING_MISMATCH')
    for key in ['source_identity_sha256','binary_sha256','base_config_sha256','runtime_config_sha256']:
        if binding.get(key)!=frozen[key]:raise Hold('FROZEN_FULL005_BINDING_MISMATCH '+key)
    return {'status':'FROZEN_ACTUAL_FULL005_SOURCE_BINARY_BASE_AND_RUNTIME_CONFIG_MATCH','expected_bindings_sha256':sha(base/'FULL005_EXPECTED_BINDINGS.json'),'resource_plan_sha256':sha(base/'FULL005_RESOURCE_PLAN.json')}
def bind(case,run,binding):
    run=Path(run);binding=Path(binding);b=json.loads(binding.read_text())
    if b.get('case')!=case:raise Hold('CASE_BINDING_MISMATCH')
    terminal=parse(run/'RETURN.txt')
    if terminal.get('status')!='COMPLETE_REPRESENTED_INTERVAL':raise Hold('INCOMPLETE_NATIVE_TERMINAL_NO_PLOTS')
    cfg=parse(run/'config.cfg')
    expected_source=b.get('source_identity_sha256');expected_cfg=b.get('runtime_config_sha256',b.get('config_sha256'))
    if not expected_source or not expected_cfg:raise Hold('MISSING_CONTROLLER_SOURCE_CONFIG_BINDING')
    if sha(run/'source_identity.txt')!=expected_source or sha(run/'config.cfg')!=expected_cfg:raise Hold('CONTROLLER_SOURCE_CONFIG_READBACK_MISMATCH')
    out={'id':case,'clock_origin':reader.CLOCK,'binding':{'path':str(binding.resolve()),'sha256':sha(binding)},'expected_source_sha256':expected_source,'expected_config_sha256':expected_cfg}
    for role,name in ROLES.items():
        p=(run/name).resolve()
        if not p.is_file():raise Hold('MISSING_REQUIRED_OUTPUT '+str(p))
        out[role]={'path':str(p),'sha256':sha(p)}
    return out
def validate_extra(case):
    spec=case['spec'];binding=Path(spec['binding']['path'])
    if sha(binding)!=spec['binding']['sha256']:raise Hold('BINDING_CHANGED')
    b=json.loads(binding.read_text())
    if b.get('case')!=spec['id'] or spec['source_identity']['sha256']!=b.get('source_identity_sha256') or spec['config']['sha256']!=b.get('runtime_config_sha256',b.get('config_sha256')):raise Hold('SOURCE_CONFIG_BINDING_NOT_MATCHED')
    chk=reader.bound(spec,'checkpoint');lines=chk.read_text().splitlines()
    if len(lines)!=11 or lines[0]!='AXBI_CHECKPOINT_V4':raise Hold('CHECKPOINT_V4_REQUIRED')
    values=list(map(float,lines[1].split()));counts=list(map(int,lines[2].split()))
    expected=int(case['config']['transport_cells'])*int(case['config']['n_mu'])
    arrays=[list(map(float,lines[i].split())) for i in range(4,10)]
    if any(len(a)!=expected or any(not math.isfinite(v) or v<0 for v in a) for a in arrays):raise Hold('CHECKPOINT_SIX_ARRAY_SHAPE_OR_DOMAIN')
    s=case['series'];term=parse(Path(spec['terminal']['path']))
    history_path=Path(spec['history']['path'])
    with history_path.open('rb') as f:
        header=f.readline().decode();f.seek(max(0,history_path.stat().st_size-65536));lastline=f.read().decode().splitlines()[-1]
    endpoint=next(csv.DictReader([header,lastline]))
    total_n=sum(arrays[0])+sum(arrays[4]);total_u=(sum(arrays[1])+sum(arrays[5]))*(1/21)/values[0]
    for actual,saved in [(total_n,float(endpoint['photon_n_per_H'])),(total_u,float(endpoint['photon_u_eV_per_H']))]:
        if abs(actual-saved)>1e-12*max(abs(actual),abs(saved),1e-300):raise Hold('CHECKPOINT_HISTORY_PHOTON_MOMENTS')
    if counts[0]!=int(term['accepted']) or values[0]!=float(term['a']) or values[1]!=s['time_s'][-1]:raise Hold('CHECKPOINT_TERMINAL_HISTORY_MISMATCH')
    p=reader.bound(spec,'ledger');statuses={};last_values={};maxima={};required={'photon_count','augmented_energy_eV_per_H','J1_eV_per_H'}
    rows=0
    with p.open() as f:
        for row in csv.DictReader(f):
            rows+=1
            if row['case_id']!=spec['id']:raise Hold('LEDGER_CASE_MISMATCH')
            status=row['status'];statuses[status]=statuses.get(status,0)+1
            value=float(row['residual'])
            if not math.isfinite(value):raise Hold('NONFINITE_LEDGER')
            if status=='FAIL':raise Hold('SAVED_LEDGER_FAIL')
            if status=='PASS':
                tol=float(row['tolerance'])
                if not math.isfinite(tol) or tol<0 or abs(value)>tol:raise Hold('PASS_LEDGER_OUTSIDE_OWN_RECORDED_TOLERANCE')
                maxima[row['ledger_name']]=max(maxima.get(row['ledger_name'],0),abs(value))
            elif status=='VALUE':last_values[row['ledger_name']]=value
            else:raise Hold('UNKNOWN_LEDGER_STATUS '+status)
    if not required.issubset(maxima):raise Hold('MISSING_REQUIRED_LEDGER_CHECKS')
    if sha(p)!=spec['ledger']['sha256'] or sha(chk)!=spec['checkpoint']['sha256']:raise Hold('INPUT_CHANGED_DURING_READ')
    return {'status':'STRICT_COMPLETENESS_SOURCE_CONFIG_CHARGE_BARYON_LEDGER_CHECKS_PASS','history_rows':len(s['L']),'accepted':counts[0],'six_array_lengths':[len(a) for a in arrays],'ledger_rows':rows,'ledger_status_counts':statuses,'max_abs_saved_residuals':maxima,'final_VALUE_ledgers':last_values,'endpoint_photon_N_per_H':total_n,'endpoint_photon_U_eV_per_H':total_u,'elapsed_time_s':float(s['time_s'][-1]),'end_Tgas_K':float(s['Tgas_K'][-1]),'source_identity_sha256':spec['source_identity']['sha256'],'config_sha256':spec['config']['sha256'],'binding_sha256':spec['binding']['sha256'],'D_cosmological_activation':'NOT_ACTIVATED_NOT_PLOTTED'}
def display_indices(s):
    selected={0,len(s['L'])-1};block=max(1,len(s['L'])//6000)
    for lo in range(0,len(s['L']),block):
        hi=min(len(s['L']),lo+block);selected.update([lo,hi-1])
        for k in ['Tgas_K',*LABELS]:
            vals=s[k][lo:hi]
            selected.add(lo+min(range(len(vals)),key=vals.__getitem__));selected.add(lo+max(range(len(vals)),key=vals.__getitem__))
    return np.asarray(sorted(selected),dtype=int)
def render(cases,out,scope):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'savefig.dpi':160})
    files=[]
    for case in cases:
        s=case['series'];idx=display_indices(s);times=np.asarray(s['time_s'])[idx]/MYR;temp=np.asarray(s['Tgas_K'])[idx]
        with (out/(case['id']+'_display.csv')).open('x',newline='') as f:
            w=csv.writer(f);w.writerow(['accepted_row','elapsed_time_s','Tgas_K',*LABELS]);w.writerows([[int(i),s['time_s'][i],s['Tgas_K'][i],*[s[k][i] for k in LABELS]] for i in idx])
        for coordinate,name in [('time','ion_fractions_vs_elapsed_time'),('temperature','ion_fractions_vs_Tgas_chronological')]:
            fig,axes=plt.subplots(2,1,figsize=(11,8),sharex=True)
            x=times if coordinate=='time' else temp
            for ax,keys in zip(axes,[['x_HI','x_HII'],['x_HeI','x_HeII','x_HeIII']]):
                for k in keys:
                    y=np.asarray(s[k])[idx];ax.plot(x,y,label=LABELS[k],color=COLORS[k],lw=1.6)
                    if coordinate=='temperature':
                        for frac in [.25,.5,.75]:
                            i=int(frac*(len(idx)-1));j=min(len(idx)-1,i+max(1,len(idx)//30));ax.annotate('',xy=(x[j],y[j]),xytext=(x[i],y[i]),arrowprops={'arrowstyle':'->','color':COLORS[k],'lw':1.1})
                ax.set_ylim(-.015,1.015);ax.set_ylabel('Fraction within the element');ax.grid(alpha=.2);ax.legend(loc='best',ncol=len(keys))
            axes[-1].set_xlabel('Elapsed proper time since z20 [Myr]' if coordinate=='time' else 'Actual gas temperature [K]; arrows follow saved time order')
            fig.suptitle(scope+' | '+case['id']+'\nActual H/He ionic fractions; no D activation or full-convergence claim',fontsize=12)
            fig.text(.5,.015,'All saved rows validated; chronological extrema-preserving display selection. No temperature sorting or state clipping.',ha='center',fontsize=9)
            fig.tight_layout(rect=[0,.035,1,.92]);path=out/(case['id']+'_'+name+'.png');fig.savefig(path);plt.close(fig);files.append(path.name)
    fig,ax=plt.subplots(figsize=(11,5.5))
    for i,case in enumerate(cases):
        s=case['series'];idx=display_indices(s);ax.plot(np.asarray(s['time_s'])[idx]/MYR,np.asarray(s['Tgas_K'])[idx],label=case['id'],color=['#1d567b','#d38418'][i],ls=['-','--'][i])
    ax.set_xlabel('Elapsed proper time since z20 [Myr]');ax.set_ylabel('Actual gas temperature [K]');ax.set_title(scope+' | Saved gas-temperature history');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(out/'Tgas_vs_elapsed_time.png');plt.close(fig);files.append('Tgas_vs_elapsed_time.png')
    return files
def run(manifest_path,out):
    if out.exists():raise Hold('FRESH_OUTPUT_REQUIRED')
    out.mkdir(parents=True)
    receipt={'status':'NOT_READY_NO_FIGURES','solver_runs':0,'scientific_admission':'NOT_ISSUED','D_cosmological_activation':'NOT_ACTIVATED_NOT_PLOTTED','temperature_order':'SAVED_CHRONOLOGY_NEVER_SORT_BY_T','clock':'Elapsed proper seconds sincez20, not absolute cosmic age','manifest_sha256':sha(manifest_path),'script_sha256':sha(Path(__file__)),'pair_convergence_criterion':'NONE_INVENTED; diagnostics await independent review'}
    try:
        m=json.loads(manifest_path.read_text());mode=m['mode'];end=float(m['end_zbar'])
        if mode=='FULL_PAIR':
            if end!=4 or len(m['cases'])!=2:raise Hold('FULL_PAIR_REQUIRES_2_COMPLETED_Z20_TO4_CASES')
            scope='CONDITIONAL_FULL_INTERVAL_DIAGNOSTIC_REVIEW_PENDING'
            receipt['frozen_full005_checks']={spec['id']:frozen_full005_guard(spec['id'],json.loads(Path(spec['binding']['path']).read_text())) for spec in m['cases']}
        elif mode=='SHORT_SCREEN_PREVIEW':
            if not 4<end<20 or len(m['cases'])!=1:raise Hold('SHORT_PREVIEW_SCOPE')
            scope='SHORT_SCREEN_PREVIEW'
        else:raise Hold('EXPLICIT_MODE_REQUIRED')
        reader.EXPECTED_END_ZBAR=end;reader.A1=1/(1+end);reader.L1=math.log(reader.A1)
        cases=[reader.load_case(spec) for spec in m['cases']]
        checks={case['id']:validate_extra(case) for case in cases}
        if any(float(c['config'].get('q_ref','nan'))!=0 for c in cases):raise Hold('FLRW_ONLY_POSTPROCESSOR')
        if mode=='FULL_PAIR':
            if sorted(int(c['config']['transport_cells']) for c in cases)!=[512,1024]:raise Hold('EXPECTED_Q512_Q1024')
            relation=require_source_relation(cases[0],cases[1],m)
            def value(x):
                try:return float(x)
                except (TypeError,ValueError):return x
            cfg=[c['config'] for c in cases];differences={k for k in cfg[0].keys()|cfg[1].keys() if value(cfg[0].get(k))!=value(cfg[1].get(k))}
            allowed={'transport_cells','transport_threads','max_steps','max_attempts','max_rhs','max_wall_s','output_budget_mib','spectra_every_accepted'}
            if not differences<=allowed:raise Hold('UNMATCHED_PHYSICAL_NUMERICAL_CONFIG '+str(sorted(differences)))
            rows,summary,milestones=reader.compare(cases[0],cases[1])
            for row in rows:row.pop('absolute_resolution_floor',None)
            for row in summary:row.pop('absolute_resolution_floor',None);row['result_class']='DIAGNOSTIC_PAIR_DIFFERENCE_NO_THRESHOLD_OR_ERROR_BOUND'
            reader.write_csv(out/'full_pair_sampled_diagnostics.csv',rows);reader.write_csv(out/'full_pair_summary.csv',summary)
            write(out/'full_pair_milestones.json',milestones);receipt['pair_source_relation']=relation;receipt['pair_grid']='1001sampledln(a), linearinterpolation, not continuoussupremum';receipt['pair_metrics']=summary
        if mode=='FULL_PAIR':
            pair_endpoints={}
            for key in ['endpoint_photon_N_per_H','endpoint_photon_U_eV_per_H']:
                a=checks[cases[0]['id']][key];b=checks[cases[1]['id']][key];pair_endpoints[key]={'reference':a,'candidate':b,'difference':b-a,'classification':'DIAGNOSTIC_NO_ACCEPTANCE_THRESHOLD'}
            for key in ['photo_events_0_per_H','photo_events_1_per_H','photo_events_2_per_H']:
                a=checks[cases[0]['id']]['final_VALUE_ledgers'].get(key);b=checks[cases[1]['id']]['final_VALUE_ledgers'].get(key)
                if a is None or b is None:raise Hold('MISSING_FINAL_PHOTO_EVENT_VALUE_LEDGER '+key)
                pair_endpoints[key]={'reference':a,'candidate':b,'difference':b-a,'classification':'DIAGNOSTIC_NO_ACCEPTANCE_THRESHOLD'}
            receipt['pair_endpoint_event_and_photon_diagnostics']=pair_endpoints
            write(out/'full_pair_endpoint_event_diagnostics.json',pair_endpoints)
        names=render(cases,out,scope)
        for spec in m['cases']:
            for role in ROLES:
                if sha(Path(spec[role]['path']))!=spec[role]['sha256']:raise Hold('COMPLETED_INPUT_CHANGED '+role)
        receipt.update(status=scope,case_checks=checks,figures={name:{'sha256':sha(out/name),'bytes':(out/name).stat().st_size} for name in names},validated_complete_inputs=m['cases'],fullpair_uncertainty='UNKNOWN; no numerical/model convergence admission',versions={'matplotlib':matplotlib.__version__,'numpy':np.__version__})
    except (Hold,reader.InputHold,KeyError,ValueError,OSError) as e:
        for f in out.glob('*.png'):f.unlink()
        receipt.update(status='NOT_READY_NO_FIGURES',wait_reason=str(e),figures=None)
    report=['# FLRW postprocessing: '+receipt['status'],'','Solver runs:0. D cosmological activation: absent; no D curve is fabricated.','Temperature plots follow saved chronology; no sorting byT.','Full pair differences are diagnostic; no convergence threshold or error bound is invented.','']
    for name,check in receipt.get('case_checks',{}).items():
        report.extend(['## '+name,'','Validated '+str(check['history_rows'])+' complete accepted-state rows; '+str(check['ledger_rows'])+' ledger rows.','Elapsed proper time sincez20: '+str(check['elapsed_time_s'])+' s; endpoint gasT: '+str(check['end_Tgas_K'])+' K.','Source SHA256: '+check['source_identity_sha256'],'Config SHA256: '+check['config_sha256'],'Ledger status counts: '+json.dumps(check['ledger_status_counts']), ''])
    if receipt.get('wait_reason'):report.extend(['Wait reason: '+receipt['wait_reason'],'No figures admitted.'])
    (out/'POSTPROCESS_REPORT.md').write_text('\n'.join(report)+'\n')
    write(out/'POSTPROCESS_RECEIPT.json',receipt);print(json.dumps({'status':receipt['status'],'figures':len(receipt.get('figures') or {}),'output':str(out)}))
    return receipt
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    b=sub.add_parser('bind');b.add_argument('--case',action='append',required=True,help='CASE_ID,RUN_DIR,CONTROLLER_BINDING_JSON');b.add_argument('--mode',choices=['FULL_PAIR','SHORT_SCREEN_PREVIEW'],required=True);b.add_argument('--end-zbar',type=float,required=True);b.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('render');r.add_argument('--manifest',type=Path,required=True);r.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.action=='bind':
        if a.output.exists():raise Hold('FRESH_MANIFEST_REQUIRED')
        if a.mode=='FULL_PAIR':
            for v in a.case:
                case,run,binding=v.split(',',2);frozen_full005_guard(case,json.loads(Path(binding).read_text()))
        specs=[bind(*v.split(',',2)) for v in a.case];write(a.output,{'mode':a.mode,'end_zbar':a.end_zbar,'source_relation':'Identicalsourcebyteguard unlessexplicitreviewedrelation supplied','cases':specs});print(str(a.output))
    else:run(a.manifest,a.output)
if __name__=='__main__':main()
