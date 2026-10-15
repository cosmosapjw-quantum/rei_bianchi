#!/usr/bin/env python3
"""Snapshot complete, checkpoint-bounded live CSV prefixes; never edit runs.

Run --capture once for a new immutable snapshot. --render NAME reproduces its
plots from those frozen CSVs, without rereading live simulation files.
"""
import argparse,csv,datetime,hashlib,json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
BASE=pathlib.Path(__file__).resolve().parent
ROOT=BASE.parents[3]
CASES={'ZERO':ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO','SHEAR_PLUS':ROOT/'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_PLUS'}
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
LABELS=['H I','H II','He I','He II','He III',r'$e^-$ (charge census; not nucleus)']
COLORS=['#176b50','#0e88a9','#a26816','#de7625','#9250b4','#313a49']
MYR=365.25*86400*1e6

def sha(data):return hashlib.sha256(data).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def freeze_prefix(source,dest):
    before=source.stat();remaining=before.st_size;h=hashlib.sha256();incomplete=0;rows=0
    with source.open('rb') as src,dest.open('xb') as out:
        while remaining:
            line=src.readline(remaining)
            if not line:raise RuntimeError('SOURCE_SHORTER_THAN_CAPTURED_PREFIX:'+str(source))
            remaining-=len(line);h.update(line)
            if line.endswith(b'\n'):out.write(line);rows+=1
            else:incomplete+=len(line)
    return {'live_path':str(source.relative_to(ROOT)),'read_started_prefix_bytes':before.st_size,'source_mtime_ns_at_start':before.st_mtime_ns,'exact_read_prefix_sha256':h.hexdigest(),'complete_csv_prefix_sha256':sha(dest.read_bytes()),'incomplete_trailing_bytes_excluded':incomplete,'complete_csv_rows_including_header':rows,'copied_complete_bytes':dest.stat().st_size}

def trim_prefix(source,dest,stop_time,species_blocks):
    found=False;groups=[];pending=[];pending_t=None;last_t=None;count=0
    with source.open() as f,dest.open('x') as out:
        header=f.readline();out.write(header)
        columns=next(csv.reader([header]));ti=columns.index('time_s');si=columns.index('species_id') if species_blocks else None
        for line in f:
            row=next(csv.reader([line]));t=float(row[ti])
            if t>stop_time:break
            if not species_blocks:
                if last_t is not None and t<=last_t:raise RuntimeError('NONMONOTONIC_SAVED_TIME')
                out.write(line);count+=1;last_t=t
                if t==stop_time:found=True
            else:
                if pending_t is not None and t!=pending_t:
                    if set(k for k,_ in pending)!=set(SPECIES) or len(pending)!=6:raise RuntimeError('INCOMPLETE_SPECIES_BLOCK_BEFORE_ENDPOINT')
                    out.writelines(l for _,l in pending);count+=len(pending)
                    if pending_t==stop_time:found=True
                    pending=[]
                pending_t=t;pending.append((row[si],line))
        if species_blocks and pending:
            if set(k for k,_ in pending)==set(SPECIES) and len(pending)==6:
                out.writelines(l for _,l in pending);count+=6
                if pending_t==stop_time:found=True
            else:raise RuntimeError('INCOMPLETE_CHECKPOINT_SPECIES_BLOCK')
    if not found:raise RuntimeError('CHECKPOINT_ENDPOINT_NOT_IN_COMPLETE_CSV_PREFIX:'+str(source))
    return {'rows_excluding_header':count,'endpoint_time_s':stop_time,'sha256':sha(dest.read_bytes())}

def capture():
    name=datetime.datetime.now(datetime.timezone.utc).strftime('snapshot_%Y%m%dT%H%M%S%fZ');target=BASE/name;target.mkdir()
    manifest={'scope':'ACTUAL_GROWING_FULL_STAGE_INCOMPLETE','captured_at_utc':utc(),'script_sha256':sha(pathlib.Path(__file__).read_bytes()),'binary_prefix':'32d11e733155','requested_executor_identity':{'model':'gpt-6.1-sol','reasoning_effort':'medium'},'observed_executor_identity_or_null':None,'case_snapshots':{},'scientific_admission':'NOT_ISSUED_FOR_FULL_OR_PARTIAL_FULL_STAGE_HISTORY','live_data_mutations':0,'solver_runs':0}
    for case,source in CASES.items():
        out=target/case;out.mkdir();start=utc()
        cp=(source/'checkpoint.txt').read_bytes();(out/'checkpoint.txt').write_bytes(cp);lines=cp.decode().splitlines();a,time_s=map(float,lines[1].split()[:2]);counts=list(map(int,lines[2].split()))
        record={'capture_started_utc':start,'checkpoint_source':str((source/'checkpoint.txt').relative_to(ROOT)),'checkpoint_sha256':sha(cp),'checkpoint_format':lines[0],'a':a,'time_s':time_s,'start_zbar':20.0,'endpoint_zbar':1/a-1,'selected_target_zbar':4.0,'status':'INCOMPLETE_GROWING_INTERVAL','accepted_at_checkpoint':counts[0],'tentative_at_checkpoint':counts[1],'RHS_at_checkpoint':counts[4],'prefixes':{},'selected_csvs':{},'config_source_identity':{}}
        for filename in ['config.cfg','source_identity.txt']:
            data=(source/filename).read_bytes();(out/filename).write_bytes(data);record['config_source_identity'][filename]=sha(data)
        for filename,blocks in [('history.csv',False),('abundances.csv',True)]:
            prefix=out/(filename+'.complete_prefix');record['prefixes'][filename]=freeze_prefix(source/filename,prefix);record['selected_csvs'][filename]=trim_prefix(prefix,out/filename,time_s,blocks)
        record['capture_finished_utc']=utc();manifest['case_snapshots'][case]=record
    (target/'SNAPSHOT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');return target

def load(path):
    samples=[];block=None
    with (path/'abundances.csv').open() as f:
        for row in csv.DictReader(f):
            t=float(row['time_s'])
            if block is None or t!=block['t']:
                if block is not None:samples.append(block)
                block={'t':t,'T':float(row['Tgas_K']),'species':{}}
            block['species'][row['species_id']]={'Y':float(row['Ybaryon']),'n':float(row['nproper'])}
    samples.append(block);t=np.array([s['t'] for s in samples]);T=np.array([s['T'] for s in samples]);values={k:[] for k in SPECIES}
    if not np.all(np.diff(t)>0):raise RuntimeError('SNAPSHOT_TIME_ORDER')
    for s in samples:
        if set(s['species'])!=set(SPECIES):raise RuntimeError('SPECIES_REGISTRY')
        q=s['species'];nb=q['H_I']['n']+q['H_II']['n']+4*sum(q[k]['n'] for k in ['He_I','He_II','He_III'])
        for k in SPECIES:
            y=q[k]['Y']
            if not np.isfinite(y) or y<0 or abs(y-q[k]['n']/nb)>1e-12:raise RuntimeError('SNAPSHOT_Y_DOMAIN_OR_DENOMINATOR')
            values[k].append(y)
    return t,T,{k:np.array(v) for k,v in values.items()}

def render(target):
    manifest=json.loads((target/'SNAPSHOT_MANIFEST.json').read_text());data={c:load(target/c) for c in CASES};outputs={}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelsize':12,'figure.dpi':160,'savefig.dpi':180})
    for axis,name in [('time','progress_abundance_vs_elapsed_time.png'),('temperature','progress_abundance_vs_Tgas_time_ordered.png')]:
        fig,axs=plt.subplots(1,2,figsize=(13.6,6.4),sharey=True)
        for ax,case in zip(axs,CASES):
            t,T,ys=data[case];x=t/MYR if axis=='time' else T;info=manifest['case_snapshots'][case]
            for k,label,color in zip(SPECIES,LABELS,COLORS):
                ax.plot(x,np.ma.masked_where(ys[k]==0,ys[k]),label=label,color=color,ls=':' if k=='electron' else '-',lw=1.7)
                if axis=='temperature':
                    for fraction in [.35,.7]:
                        i=int((len(t)-1)*fraction);j=min(len(t)-1,i+max(4,len(t)//24))
                        if ys[k][i]>0 and ys[k][j]>0:ax.annotate('',xy=(x[j],ys[k][j]),xytext=(x[i],ys[k][i]),arrowprops={'arrowstyle':'->','color':color,'lw':1.2})
            ymin=min(float(v[v>0].min()) for v in ys.values() if np.any(v>0));ax.set_yscale('log');ax.set_ylim(ymin/2,1.2);ax.grid(True,alpha=.23)
            q='0' if case=='ZERO' else '+0.01';ax.set_title(f'{case}: q_ref={q}\nCheckpointed z̄ 20 → {info["endpoint_zbar"]:.5f}')
            ax.set_xlabel('Elapsed proper time since z̄ = 20 [Myr]' if axis=='time' else 'Gas temperature [K] (arrows: increasing time)');ax.margins(x=.03)
        axs[0].set_ylabel(r'$Y_i=n_i/n_b$, with $n_b=n_H+4n_{He}$');h,l=axs[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.085))
        fig.suptitle('ACTUAL FULL-STAGE PROGRESS | INCOMPLETE | target z̄ = 4 not reached',fontsize=16,y=.985)
        fig.text(.5,.022,'Exact zeros omitted only on log display; no floor, clipping, or temperature sorting.\nDifferent checkpoint cutoffs: no matched-response, trace-accuracy, convergence, or full-history claim.',ha='center',fontsize=10)
        fig.subplots_adjust(left=.085,right=.99,bottom=.24,top=.84,wspace=.09);fig.savefig(target/name);plt.close(fig);outputs[name]=sha((target/name).read_bytes())
    result={'snapshot_manifest_sha256':sha((target/'SNAPSHOT_MANIFEST.json').read_bytes()),'script_sha256':sha(pathlib.Path(__file__).read_bytes()),'figures':outputs,'normalization':'Saved n_i/(nH+4nHe); electronne/nb labellednotnuclear','temperature_order':'Originalstrictsavedtimeorder; arrows; nosort','zeros':'Originalzeros retainedinCSV; maskedonlylogdisplay','tiny_traces':'Displayedassaved; no34digitprecision orglobalconvergenceclaim','versions':{'matplotlib':matplotlib.__version__,'numpy':np.__version__},'classification':'DIAGNOSTIC_INCOMPLETE_ACTUAL_GROWING_HISTORY'}
    (target/'FIGURE_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    text='# Actual full-stage progress snapshot — incomplete\n\nCaptured UTC: '+manifest['captured_at_utc']+'\n\n'
    for c,r in manifest['case_snapshots'].items():text+=f'- {c}: checkpointed z̄20 → {r["endpoint_zbar"]:.8f}; elapsed {r["time_s"]/MYR:.8f} Myr; {r["accepted_at_checkpoint"]} accepted, {r["tentative_at_checkpoint"]} tentative, {r["RHS_at_checkpoint"]} RHS.\n'
    text+='\nThe target z̄4 is not reached. Snapshots are exact complete CSV prefixes bounded by the captured atomic checkpoint; source identities, capture timestamps, prefix sizes/hashes and excluded incomplete tails are in SNAPSHOT_MANIFEST.json. Different case cutoffs are not a matched comparison. No full AX14 completion, global numerical refinement, resolved shear response or validated tiny-trace precision is claimed. Electrons are labelled charge census and excluded from nuclear baryon inventory. Time/Tgas plots preserve original time order; exact zeros are masked only on the log display.\n\n![Elapsed-time progress](progress_abundance_vs_elapsed_time.png)\n\n![Time-ordered Tgas progress](progress_abundance_vs_Tgas_time_ordered.png)\n\nReproduce figures with `python3 snapshot_progress.py --render '+target.name+'` from this postprocessor directory; no live source is reread. Continue the existing supervisor and checkpoint identities; do not relaunch completed or running cases.\n'
    (target/'PROGRESS_ADDENDUM.md').write_text(text);print(json.dumps({'snapshot':str(target),'coverage':{c:r['endpoint_zbar'] for c,r in manifest['case_snapshots'].items()},'figures':outputs},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--capture',action='store_true');parser.add_argument('--render');args=parser.parse_args()
    if args.capture:render(capture())
    elif args.render:render(BASE/args.render)
    else:parser.error('Choose --capture fornewimmutabledata or--render NAME forfrozenreproduction')
