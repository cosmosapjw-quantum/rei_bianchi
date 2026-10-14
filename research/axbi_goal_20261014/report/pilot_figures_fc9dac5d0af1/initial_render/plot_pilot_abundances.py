#!/usr/bin/env python3
"""Reproduce actual AX06 abundance diagnostics; no solver or input mutation."""
import csv, hashlib, json, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
OUT=pathlib.Path(__file__).resolve().parent
ROOT=OUT.parents[3]
INPUT=ROOT/'research/axbi_goal_20261014/runs/pilot/fc9dac5d0af1'
MYR_SECONDS=365.25*86400*1e6
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
LABELS=['H I','H II','He I','He II','He III',r'$e^-$ (charge census; not nucleus)']
COLORS=['#176b50','#0e88a9','#a26816','#de7625','#9250b4','#313a49']
CASES=[('FLRW',r'FLRW: $q_{\rm ref}=0$'),('SHEAR_PLUS',r'Axisymmetric BI: $q_{\rm ref}=+0.01$')]

def load(case):
    path=INPUT/case/'abundances.csv';samples=[];current=None
    with path.open() as f:
        for row in csv.DictReader(f):
            t=float(row['time_s'])
            if current is None or t!=current['time_s']:
                if current is not None:samples.append(current)
                current={'time_s':t,'temperature':float(row['Tgas_K']),'zbar':float(row['zbar']),'species':{}}
            if row['species_id'] in current['species']:raise ValueError('duplicate species')
            current['species'][row['species_id']]={'Y':float(row['Ybaryon']),'n':float(row['nproper']),'A':int(row['A'])}
    samples.append(current)
    times=np.array([s['time_s'] for s in samples]);temperatures=np.array([s['temperature'] for s in samples])
    if not np.all(np.diff(times)>0):raise ValueError('saved time must strictly increase')
    values={k:[] for k in SPECIES}
    for s in samples:
        if set(s['species'])!=set(SPECIES):raise ValueError('incomplete species block')
        q=s['species'];nh=q['H_I']['n']+q['H_II']['n'];nhe=sum(q[k]['n'] for k in ['He_I','He_II','He_III']);nb=nh+4*nhe
        for k in SPECIES:
            y=q[k]['Y']
            if not np.isfinite(y) or y<0:raise ValueError('invalid saved abundance')
            if abs(y-q[k]['n']/nb)>1e-12:raise ValueError('savedY violates fullHHebaryon denominator')
            values[k].append(y)
    return times,temperatures,{k:np.array(v) for k,v in values.items()},samples

DATA={case:load(case) for case,_ in CASES}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelsize':12,'axes.titlesize':13,'figure.dpi':160,'savefig.dpi':180})
outputs=[]
for xname,filename in [('time','abundance_vs_elapsed_time.png'),('temperature','abundance_vs_Tgas_time_ordered.png')]:
    fig,axs=plt.subplots(1,2,figsize=(13.6,6.4),sharey=True)
    for ax,(case,title) in zip(axs,CASES):
        t,temp,y,samples=DATA[case];x=t/MYR_SECONDS if xname=='time' else temp
        for species,label,color in zip(SPECIES,LABELS,COLORS):
            yy=np.ma.masked_where(y[species]==0,y[species])
            ax.plot(x,yy,label=label,color=color,lw=2.1 if species=='electron' else 1.65,ls=':' if species=='electron' else '-')
            if xname=='temperature':
                # Time-index arrows; original data order retained even if T turns.
                for fraction in [0.38,0.73]:
                    i=int((len(t)-1)*fraction);j=min(i+max(4,len(t)//24),len(t)-1)
                    if y[species][i]>0 and y[species][j]>0:
                        ax.annotate('',xy=(x[j],y[species][j]),xytext=(x[i],y[species][i]),arrowprops={'arrowstyle':'->','color':color,'lw':1.2,'mutation_scale':12})
        ax.set_yscale('log');ax.set_ylim(1e-15,1.2);ax.grid(True,which='major',alpha=.23);ax.set_title(title)
        ax.set_xlabel('Elapsed proper time since z̄ = 20 [Myr]' if xname=='time' else r'Gas temperature $T_{\rm gas}$ [K] (arrows: increasing time)')
        ax.margins(x=.03)
    axs[0].set_ylabel(r'Number abundance per selected-model baryon, $Y_i=n_i/(n_H+4n_{He})$')
    handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.085))
    fig.suptitle('ACTUAL PILOT DIAGNOSTIC | z̄ = 20 → 19.8 | conditional H/He model',fontsize=16,y=.97)
    fig.text(.5,.024,'Exact zeros are omitted only from the log display; no floor or state clipping.\nShort pilot only: no full EoR, refinement, or resolved shear-effect claim.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.085,right=.99,bottom=.24,top=.86,wspace=.09)
    fig.savefig(OUT/filename);plt.close(fig);outputs.append(filename)
manifest={'classification':'DIAGNOSTIC_ACTUAL_COMPLETED_PILOTS','node_id':'AX13','binary_identity':'fc9dac5d0af16e159af64ed406cc4c2d2f7918362836546ad15eef5d6f836a46','interval_zbar':[20,19.8],'normalization':'Saved Yi checked against n_i/(nHI+nHII+4*(nHeI+nHeII+nHeIII)); electronne/nb excluded fromnuclear inventory','time_unit':'Myr=365.25*86400*1e6 properseconds; origin elapsed sincezbar20','temperature_order':'Strict savedtime order retained; arrowindices38/73percent ofsavedtime sequence, no sortingbyT','log_display':'Exactzeros maskedonly; nofloor/numeric clipping; initialHeII/HeIIIzero retainedininputs','claim_ceiling':'No full20to4history, empiricalrefinement, resolvedsignedsheareffect or nuclearBBNsynthesis','versions':{'matplotlib':matplotlib.__version__,'numpy':np.__version__},'inputs':{str(INPUT/case/name):hashlib.sha256((INPUT/case/name).read_bytes()).hexdigest() for case,_ in CASES for name in ['abundances.csv','history.csv']},'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'figures':{filename:hashlib.sha256((OUT/filename).read_bytes()).hexdigest() for filename in outputs},'samples':{case:{'saved_states':len(DATA[case][0]),'zero_counts':{k:int(np.sum(DATA[case][2][k]==0)) for k in SPECIES},'end_elapsed_Myr':float(DATA[case][0][-1]/MYR_SECONDS),'end_Tgas_K':float(DATA[case][1][-1]),'end_Y':{k:float(DATA[case][2][k][-1]) for k in SPECIES}} for case,_ in CASES}}
(OUT/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'figures':outputs,'samples':manifest['samples']},indent=2))
