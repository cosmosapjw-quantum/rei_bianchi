# Saved-data-only diagnostic render; no scientific modules imported.
import time
WALL_START=time.perf_counter()
import resource,signal
resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
resource.setrlimit(resource.RLIMIT_CPU,(5,5))
signal.setitimer(signal.ITIMER_PROF,max(.001,4-time.process_time()))
signal.setitimer(signal.ITIMER_REAL,7.8)
import os,json,hashlib
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[key]='1'
os.environ['MPLBACKEND']='Agg'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
UNIT=Path(__file__).resolve().parent.parent
OUT=UNIT/'delivery/figures'; SOURCE=UNIT/'implementation/attempt01'

def main():
    raw={n:(SOURCE/n).read_bytes() for n in ('OBSERVATIONS.jsonl','CHECKS.jsonl')}
    obs=[json.loads(x) for x in raw['OBSERVATIONS.jsonl'].splitlines()]
    checks=[json.loads(x) for x in raw['CHECKS.jsonl'].splitlines()]
    if len(obs)!=24 or len({x['canonical_event_id'] for x in obs})!=24: raise ValueError('exact unique24 saved observations required')
    if not all(len(x['FD'])==2 and {v['h'] for v in x['FD']}=={2e-4,1e-4} for x in obs): raise ValueError('two frozen steps required')
    if {x['tolerance'] for x in checks if ':mixed_FD:' in x['check']}!={2e-8}: raise ValueError('saved criterion required')
    zs=sorted({x['z'] for x in obs},key=float); cases=sorted({x['case'] for x in obs}); grids=sorted({x.split('_',1)[1] for x in cases})
    if (len(zs),len(cases),len(grids))!=(3,8,4): raise ValueError('source/case structure')
    colors={'chi1.5':'#0072B2','chi3':'#D55E00'}; markers=dict(zip(grids,('o','s','^','D')))
    offsets={x:(i-3.5)*.043 for i,x in enumerate(cases)}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9.5,'axes.titlesize':10,'legend.fontsize':8,'xtick.labelsize':9,'ytick.labelsize':9,'pdf.fonttype':42})
    fig,axs=plt.subplots(2,1,figsize=(183/25.4,191/25.4),sharex=True)
    fig.subplots_adjust(left=.145,right=.97,top=.865,bottom=.205,hspace=.32)
    values=[]
    for row in obs:
        chi,grid=row['case'].split('_',1); color=colors[chi]; marker=markers[grid]; x=zs.index(row['z'])+offsets[row['case']]
        axs[0].plot(x,row['A_m3'],marker=marker,color=color,linestyle='none',markersize=5.6,markeredgewidth=.85)
        for fd in row['FD']:
            big=fd['h']==2e-4
            axs[1].plot(x+(-.006 if big else .006),fd['max_scaled_error'],marker=marker,color=color,markerfacecolor=color if big else 'white',linestyle='none',markersize=5.4,markeredgewidth=.95)
        values.append({k:row[k] for k in ('canonical_event_id','case','z','A_m3','G_J_m3','FD')})
    for ax in axs:
        ax.set_yscale('log');ax.set_xlim(-.27,2.27);ax.grid(axis='y',which='major',alpha=.22,linewidth=.6)
        ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    axs[0].set_ylabel(r'Integrated capture count $A$ [m$^{-3}$]')
    axs[0].set_title('(a) All 24 integrated capture alternatives',loc='left',pad=8)
    axs[1].set_title('(b) Maximum mixed-JVP FD residual over 27 rows',loc='left',pad=8)
    axs[1].set_ylabel('Scaled FD residual [dimensionless]')
    axs[1].axhline(2e-8,color='#555555',linestyle='--',linewidth=1)
    axs[1].annotate(r'Frozen criterion $2\times10^{-8}$',xy=(.015,2e-8),xycoords=('axes fraction','data'),xytext=(0,4),textcoords='offset points',fontsize=8,ha='left',va='bottom',color='#444444')
    axs[1].set_ylim(top=6e-8);axs[1].set_xticks(range(3),zs)
    axs[1].set_xlabel('Source z alternative (three discrete exports; points offset for readability)')
    fig.suptitle('CR retained-photon return: integrated diagnostics',fontsize=12,y=.975)
    handles=[Line2D([],[],color=colors[k],marker='o',linestyle='none',label=k.replace('chi',r'$\chi=$')) for k in colors]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.945),ncol=2,frameon=False)
    handles=[Line2D([],[],color='#555555',marker=markers[g],linestyle='none',label=g.replace('_',', ')) for g in grids]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.103),ncol=4,frameon=False,columnspacing=1.3)
    handles=[Line2D([],[],color='#333333',marker='o',markerfacecolor=f,linestyle='none',label=lab) for f,lab in (('#333333',r'FD $h=2\times10^{-4}$'),('white',r'FD $h=1\times10^{-4}$'))]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.062),ncol=2,frameon=False)
    fig.text(.5,.033,'Each point is an alternative; no sum, history, rate, spectrum, or uncertainty band.',ha='center',fontsize=8)
    fig.text(.5,.012,r'FD uses saved row-unit normalization and consumer fixture $b=1.4\times10^6$ m$^{-3}$.',ha='center',fontsize=8)
    names=['CR_INTEGRATED_DIAGNOSTICS.png','CR_INTEGRATED_DIAGNOSTICS.pdf']
    fig.savefig(OUT/names[0],dpi=300);fig.savefig(OUT/names[1]);plt.close(fig)
    inputs={'source':'saved attempt01 only; no consumer/checker/producer import or reexecution','files':[{'path':str((SOURCE/n).relative_to(UNIT)),'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for n,v in raw.items()],'actual_alternatives':24,'saved_check_count':len(checks),'source_z':zs,'cases':cases,'FD_steps':[2e-4,1e-4],'FD_frozen_criterion':2e-8,'plotted_saved_values':values,'figure_width_mm':183,'figure_height_mm':191,'connecting_lines':False,'error_bars':False}
    (OUT/'PLOT_INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n')
    (OUT/'CAPTION.md').write_text('''# CR integrated diagnostic return

(a) All24 saved actual integrated capture counts A in proper-volume m^-3, grouped by three discrete source-z alternatives. Color identifies chi1.5 or chi3; marker identifies one of four R/N alternatives. Horizontal offsets expose the alternatives. No connecting lines, sums, histories, rates, error bars, or uncertainty bands are shown.

(b) For each same alternative, the saved maximum mixed-JVP finite-difference residual over27 diagnostic rows appears at both frozen steps h=2e-4 (filled) and1e-4 (open). The normalization is the saved row-specific sum of absolute analytic value/tangent operands, without a universal unit floor. The dashed line is the frozen2e-8 criterion. The consumer fixture b=1.4e6m^-3 applies to these derivative checks; panel(a) uses the exported proper-volume count and needs no b. No donor abundance/state, physical update, expansion trajectory, spectrum, or convergence-order claim is inferred.

Rendered exclusively from saved OBSERVATIONS.jsonl and CHECKS.jsonl. Retained-photon energy, native25 maps, and numerical qualifications remain preserved in raw observations. Scientific admission belongs to root and independent review.
''')
    signal.setitimer(signal.ITIMER_PROF,0);signal.setitimer(signal.ITIMER_REAL,0)
    actual=time.process_time();elapsed=time.perf_counter()-WALL_START
    receipt={'status':'RENDERED_PENDING_VISUAL_REVIEW','budget_owner':'PRESENTATION','actual_CPU_s_before_receipt_tail':actual,'receipt_tail_CPU_s':.05,'charged_CPU_s':actual+.05,'wall_s':elapsed,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limits':{'CPU_s':4,'wall_s':8,'address_space_MiB':512},'within_limits':actual+.05<=4 and elapsed<=8,'scientific_import_or_execution':False,'outputs':[{'path':str((OUT/n).relative_to(UNIT)),'bytes':(OUT/n).stat().st_size} for n in names],'actual_alternatives':24,'plotted_count_values':24,'plotted_FD_values':48,'unknown_remote_LLM_cost':'UNKNOWN_NOT_ZERO'}
    (OUT/'PLOT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)
if __name__=='__main__': main()
