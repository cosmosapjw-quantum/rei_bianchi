#!/usr/bin/env python3
"""Four completed-family abundance diagnostics; absent completion => no PNGs.

Five explicit immutable case descriptors use convergence/compare_histories.py.
No solver, final admission, resolved response inference or temperature sorting.
"""
import argparse,csv,hashlib,importlib.util,json,math,pathlib,sys,tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
BASE=pathlib.Path(__file__).resolve().parent;ROOT=BASE.parents[3]
REDUCER_PATH=ROOT/'research/axbi_goal_20261014/convergence/compare_histories.py'
spec=importlib.util.spec_from_file_location('completed_history_reader',REDUCER_PATH);reducer=importlib.util.module_from_spec(spec);spec.loader.exec_module(reducer)
QS={'ZERO':0.0,'SHEAR_PLUS':.01,'SHEAR_MINUS':-.01,'SHEAR_HALF_PLUS':.005,'SHEAR_HALF_MINUS':-.005}
SPECIES=list(reducer.SPECIES);LABELS=['H I','H II','He I','He II','He III',r'$e^-$ (charge census; not nucleus)']
SPECIES_COLORS=['#176b50','#0e88a9','#a26816','#de7625','#9250b4','#313a49']
CASE_COLORS={'ZERO':'#202124','SHEAR_PLUS':'#bc4427','SHEAR_MINUS':'#2159a7','SHEAR_HALF_PLUS':'#bd882b','SHEAR_HALF_MINUS':'#218c88'}
MYR=365.25*86400*1e6

def load_family(manifest):
    loaded={};issues=[];declared=manifest.get('cases',{})
    for case,q in QS.items():
        if case not in declared:issues.append({'case':case,'status':'NOT_READY_MISSING_CASE_DESCRIPTOR'});continue
        try:
            if declared[case].get('id')!=case:raise reducer.InputHold('HOLD_CASE_ID',case)
            current=reducer.load_case(declared[case])
            if float(current['config'].get('q_ref','nan'))!=q:raise reducer.InputHold('HOLD_SIGNED_Q_MAPPING',case)
            if current['config'].get('same_h')!='false':raise reducer.InputHold('HOLD_PRIMARY_PHYSICAL_FAMILY',case)
            loaded[case]=current
        except (reducer.InputHold,KeyError,ValueError) as e:issues.append({'case':case,'status':getattr(e,'status','NOT_READY_INPUT_SCHEMA'),'field':getattr(e,'field',str(e))})
    if not issues:
        ref=loaded['ZERO'];resource={'max_steps','max_attempts','max_rhs','max_wall_s','output_budget_mib','spectra_every_accepted'}
        def value(v):
            try:return float(v)
            except (TypeError,ValueError):return v
        for case,current in loaded.items():
            differences={k for k in ref['config'].keys()|current['config'].keys() if value(ref['config'].get(k))!=value(current['config'].get(k))}
            if not differences<={'q_ref'}|resource:issues.append({'case':case,'status':'NOT_READY_UNMATCHED_PHYSICAL_NUMERICAL_CONFIG','field':sorted(differences)})
            if max(abs(a-b) for a,b in zip(ref['factors'],current['factors']))>1e-12:issues.append({'case':case,'status':'NOT_READY_UNMATCHED_BARYON_INVENTORY'})
    return loaded,issues

def read_ledger(desc):
    if not desc:return [],'NOT_MEASURED'
    p=reducer.bound({'id':'convergence','ledger':desc},'ledger');rows=[]
    with p.open() as f:
        for row in csv.DictReader(f):
            if row.get('comparison_coordinate')!='ZBAR':raise reducer.InputHold('HOLD_LEDGER_COORDINATE',str(p))
            if row.get('case_id') not in QS or row.get('reference_case')!='ZERO':raise reducer.InputHold('HOLD_LEDGER_CASE',str(p))
            if not row.get('observable','').startswith('Y_'):continue
            z=float(row['candidate_zbar'])
            if z!=float(row['reference_zbar']) or not 4<=z<=20:raise reducer.InputHold('HOLD_LEDGER_SUPPORTED_MATCHED_ZBAR',str(p))
            if row.get('numerical_error_estimate') not in [None,'','UNKNOWN']:
                err=float(row['numerical_error_estimate'])
                if not math.isfinite(err) or err<0:raise reducer.InputHold('HOLD_LEDGER_ERROR_ESTIMATE',str(p))
                row=dict(row,numerical_error_estimate=err)
            else:row=dict(row,numerical_error_estimate=None)
            rows.append(row)
    if reducer.hashfile(p)!=desc['sha256']:raise reducer.InputHold('HOLD_LEDGER_CHANGED_DURING_READ',str(p))
    return rows,'PROVIDED_ROWS_ONLY_NO_INFERRED_RESOLUTION'

def style(ax):ax.grid(True,alpha=.22);ax.margins(x=.025)
def abundance_axis(ax,values):
    positive=[np.min(v[v>0]) for v in values if np.any(v>0)]
    ax.set_yscale('log');ax.set_ylim(min(positive)/2,1.2)
def footer(fig):fig.text(.5,.014,'Exact zeros omitted only on log display; no floor or state clipping. Electrons are not nuclei.\nTiny traces do not imply validated precision. Global/refinement/model admission is separate.',ha='center',fontsize=9)

def render(cases,out,ledger,synthetic=False):
    prefix='SYNTHETIC SMOKE — NOT PHYSICAL' if synthetic else 'COMPLETED CONDITIONAL INTERVAL z̄ 20 → 4'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'savefig.dpi':170})
    ref=cases['ZERO'];s=ref['series'];times=np.asarray(s['time_s'])/MYR;temperatures=np.asarray(s['Tgas_K']);files=[]
    for mode,name in [('time','abundance_vs_time.png'),('temperature','abundance_vs_Tgas.png')]:
        fig,ax=plt.subplots(figsize=(10.2,6.5));x=times if mode=='time' else temperatures;ys=[]
        for k,label,color in zip(SPECIES,LABELS,SPECIES_COLORS):
            y=np.asarray(s['Y_'+k]);ys.append(y);ax.plot(x,np.ma.masked_where(y==0,y),label=label,color=color,ls=':' if k=='electron' else '-')
            if mode=='temperature':
                for f in [.25,.5,.75]:
                    i=int((len(x)-1)*f);j=min(len(x)-1,i+max(1,len(x)//30))
                    if y[i]>0 and y[j]>0:ax.annotate('',xy=(x[j],y[j]),xytext=(x[i],y[i]),arrowprops={'arrowstyle':'->','color':color})
        abundance_axis(ax,ys);style(ax);ax.set_ylabel(r'$Y_i=n_i/n_b$; $n_b=n_H+4n_{He}$');ax.set_xlabel('Elapsed proper time since z̄20 [Myr]' if mode=='time' else 'Gas temperature [K]; arrows follow saved chronological order');ax.set_title(prefix+'\nZERO baseline');ax.legend(ncol=3,loc='lower right',fontsize=8);footer(fig);fig.subplots_adjust(bottom=.16,top=.87,left=.1,right=.98);fig.savefig(out/name);plt.close(fig);files.append(name)
    fig,axs=plt.subplots(3,2,figsize=(13,10),sharex=True)
    for ax,k,label in zip(axs.flat,SPECIES,LABELS):
        values=[]
        for case,data in cases.items():
            y=np.asarray(data['series']['Y_'+k]);values.append(y);ax.plot(np.asarray(data['series']['time_s'])/MYR,np.ma.masked_where(y==0,y),color=CASE_COLORS[case],label=f'{case} q={QS[case]:+.3g}',lw=1.2)
        abundance_axis(ax,values);style(ax);ax.set_title(label);ax.set_ylabel(r'$Y_i$');ax.set_xlabel('Elapsed proper time [Myr]')
    h,l=axs.flat[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,bbox_to_anchor=(.5,.064),fontsize=8);fig.suptitle(prefix+'\nIndependent solved clocks; time overlays do not also match z̄',fontsize=14);footer(fig);fig.subplots_adjust(bottom=.17,top=.88,hspace=.32,wspace=.2);name='flrw_bianchi_abundance_comparison.png';fig.savefig(out/name);plt.close(fig);files.append(name)
    grid=reducer.grid();zs=np.array([20 if i==0 else 4 if i==1000 else math.exp(-L)-1 for i,L in enumerate(grid)]);fig,axs=plt.subplots(3,2,figsize=(13,10),sharex=True)
    for ax,k,label in zip(axs.flat,SPECIES,LABELS):
        name='Y_'+k;baseline=np.array([reducer.interp(s['L'],s[name],L) for L in grid])
        for case,data in cases.items():
            if case=='ZERO':continue
            candidate=np.array([reducer.interp(data['series']['L'],data['series'][name],L) for L in grid]);ax.plot(zs,candidate-baseline,color=CASE_COLORS[case],label=case,lw=1.15)
            supplied=[r for r in ledger if r['case_id']==case and r['observable']==name and r['numerical_error_estimate'] is not None]
            if supplied:
                # Show only actually supplied per-case numerical estimates;
                # never transfer signs/levels, interpolate gaps or resolve a claim.
                ax.scatter([float(r['candidate_zbar']) for r in supplied],[r['numerical_error_estimate'] for r in supplied],s=8,marker='x',color=CASE_COLORS[case],alpha=.6)
        floor=reducer.floor(name,ref);ax.axhline(0,color='black',lw=.6);ax.axhline(floor,color='#888888',ls='--',lw=.7);ax.axhline(-floor,color='#888888',ls='--',lw=.7);style(ax);ax.set_xlim(20,4);ax.set_ylabel(r'$\Delta Y_i=Y_i(q)-Y_i(0)$');ax.set_title(label);ax.set_xlabel('Matched mean redshift z̄')
    h,l=axs.flat[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=4,bbox_to_anchor=(.5,.066),fontsize=8)
    text='Resolution NOT_MEASURED; no error band invented' if not ledger else 'x markers: supplied numerical estimates only; interpolation uncertainty not absorbed'
    fig.suptitle(prefix+'\nSigned deltas on frozen 1001 ln(a) grid | '+text,fontsize=13);fig.text(.5,.019,'Dashed ±Y floors are diagnostic thresholds, not uncertainty bounds. No resolved effect or null inferred.\nSampled linear interpolation; unknown global/refinement/model accuracy remains separate.',ha='center',fontsize=9);fig.subplots_adjust(bottom=.15,top=.88,hspace=.32,wspace=.2);name='delta_abundance_resolution.png';fig.savefig(out/name);plt.close(fig);files.append(name)
    return files

def run(manifest_path,output):
    output=pathlib.Path(output)
    if output.exists():raise RuntimeError('Existing output directory preserved; choose a new directory')
    output.mkdir(parents=True);result={'status':'NOT_READY','figures':None,'solver_runs':0,'scientific_admission':'NOT_ISSUED','plot_source_sha256':reducer.hashfile(__file__),'reader_source_sha256':reducer.hashfile(REDUCER_PATH),'input_manifest':str(manifest_path)}
    try:
        result['input_manifest_sha256']=reducer.hashfile(manifest_path);manifest=json.loads(pathlib.Path(manifest_path).read_text());cases,issues=load_family(manifest)
        if issues:result['exact_wait_inputs']=issues
        else:
            ledger,status=read_ledger(manifest.get('convergence_ledger'));names=render(cases,output,ledger);result.update(status='COMPLETED_BASELINE_FAMILY_DIAGNOSTIC_FIGURES_NO_FINAL_ADMISSION',figures={n:reducer.hashfile(output/n) for n in names},convergence_ledger_status=status,case_descriptors=manifest['cases'],interpolation_uncertainty='UNKNOWN',claim_scope='Fullcompletedfivecasebaseline only; no C11/C12/AX15 PASS inferred')
    except (reducer.InputHold,KeyError,ValueError,OSError) as e:result['exact_wait_inputs']=[{'status':getattr(e,'status','NOT_READY_INPUT'),'field':getattr(e,'field',str(e))}]
    (output/'FIGURE_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);return result

def smoke():
    raw=BASE/'raw';raw.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=raw) as name:
        p=pathlib.Path(name);m=p/'missing.json';m.write_text(json.dumps({'cases':{}}));r=run(m,p/'missing')
        assert r['status']=='NOT_READY' and len(r['exact_wait_inputs'])==5 and not list((p/'missing').glob('*.png'))
    # Small numeric falsifier for matched-z deltas; T order never enters matching.
    L=reducer.grid();ref=[0,.5,1];q=[0,.6,1];native=[L[0],L[500],L[-1]]
    delta=[reducer.interp(native,q,u)-reducer.interp(native,ref,u) for u in L]
    assert abs(delta[500]-.1)<1e-14 and delta[0]==0 and delta[-1]==0
    print('SYNTHETIC_SMOKE_PASS: missingfivecasesproducesnoPNGs; matchedzdelta;0solver0actualfinalfigures')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest');p.add_argument('--output');p.add_argument('--smoke-test',action='store_true');a=p.parse_args()
    if a.smoke_test:smoke()
    elif a.manifest and a.output:run(a.manifest,a.output)
    else:p.error('Use --smoke-test or--manifest JSON --output NEW_DIRECTORY')
