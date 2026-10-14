#!/usr/bin/env python3
"""Render immutable, matched-a resource-capped ZERO/PLUS histories. No solver."""
import array,csv,datetime,hashlib,itertools,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
CASES={'ZERO':ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO','SHEAR_PLUS':ROOT/'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_PLUS'}
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
LABELS=['H I','H II','He I','He II','He III',r'$e^-$ (charge census; not nucleus)']
COLORS=['#176b50','#0e88a9','#a26816','#de7625','#9250b4','#313a49']
MYR=365.25*86400*1e6
END=0.08873654701704167

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def finite(v):
 v=float(v)
 if not math.isfinite(v):raise ValueError('Nonfinite saved value')
 return v

def load(case,path):
 identities={n:sha(path/n) for n in ['history.csv','abundances.csv','config.cfg','source_identity.txt','checkpoint.txt','RETURN.txt']}
 terminal=dict(l.split('=',1) for l in (path/'RETURN.txt').read_text().splitlines() if '=' in l)
 cp=(path/'checkpoint.txt').read_text().splitlines();state=list(map(float,cp[1].split()));counts=list(map(int,cp[2].split()))
 if cp[0]!='AXBI_CHECKPOINT_V2' or terminal['status']!='STOPPED_CHECKPOINTED' or 'AXBI_RUNTIME_CAP' not in terminal['result'] or float(terminal['a'])!=END or state[0]!=END or counts[0]!=200000:raise ValueError('Wrong frozen terminal scope')
 data={k:array.array('d') for k in ['t','T','a','x_HII','x_HeII','x_HeIII',*SPECIES]};last_h=None;index=0
 with (path/'history.csv').open() as hf,(path/'abundances.csv').open() as af:
  history=iter(csv.DictReader(hf))
  for t,rows in itertools.groupby(csv.DictReader(af),lambda r:finite(r['time_s'])):
   h=next(history,None);block={}
   if h is None or h['case_id']!=case or finite(h['time_s'])!=t:raise ValueError('History/abundance alignment')
   for row in rows:
    k=row['species_id']
    if k in block or row['run_id']!=case or row['normalization_registry']!='BASELINE_H_HE_CHARGE_AND_BARYON_V1':raise ValueError('Species registry')
    block[k]=row
   if set(block)!=set(SPECIES):raise ValueError('Incomplete species block')
   T=finite(h['temperature_K']);a=finite(h['a'])
   if T<=0 or not 1/21<=a<=END or (data['t'] and (t<=data['t'][-1] or a<=data['a'][-1])):raise ValueError('Chronology/domain')
   n={k:finite(block[k]['nproper']) for k in SPECIES};nh=n['H_I']+n['H_II'];he=sum(n[k] for k in ['He_I','He_II','He_III']);nb=nh+4*he
   if min(n.values())<0 or nh<=0 or he<=0:raise ValueError('Density domain')
   if abs(nh/finite(h['nH_proper_cm3'])-1)>1e-12 or abs(n['electron']-n['H_II']-n['He_II']-2*n['He_III'])/nh>1e-12:raise ValueError('Nuclei/charge alignment')
   ys={k:finite(block[k]['Ybaryon']) for k in SPECIES}
   for k in SPECIES:
    if ys[k]<0 or abs(ys[k]-n[k]/nb)>1e-12 or finite(block[k]['Tgas_K'])!=T or finite(block[k]['zbar'])!=finite(h['zbar']):raise ValueError('Saved abundance normalization/state')
    data[k].append(ys[k])
   if abs(sum(int(block[k]['A'])*ys[k] for k in SPECIES)-1)>1e-12:raise ValueError('Baryon inventory')
   for k,den in [('H_I',nh),('H_II',nh),('He_I',he),('He_II',he),('He_III',he)]:
    if abs(n[k]/den-finite(h['x_'+k.replace('_','')]))>1e-12:raise ValueError('Fraction alignment')
   for k,v in [('t',t),('T',T),('a',a),*[(k,finite(h[k])) for k in ['x_HII','x_HeII','x_HeIII']]]:data[k].append(v)
   last_h=h;index+=1
  if next(history,None) is not None:raise ValueError('Extra history rows')
 if index!=200001 or data['t'][0]!=0 or data['a'][0]!=1/21 or data['a'][-1]!=END or data['t'][-1]!=state[1]:raise ValueError('Endpoint/accepted count')
 for k,i in [('x_HII',3),('x_HeII',4),('x_HeIII',5)]:
  if data[k][-1]!=state[i]:raise ValueError('Checkpoint species endpoint')
 if any(sha(path/n)!=h for n,h in identities.items()):raise ValueError('Frozen input changed')
 data={k:np.asarray(v) for k,v in data.items()}
 # Decimate only the plotted samples. Retain extrema of every displayed species
 # and T, per chronological 100-row block, plus endpoints; no value clipping.
 selected={0,index-1}
 for lo in range(0,index,100):
  hi=min(index,lo+100);selected.update((lo,hi-1))
  for k in ['T',*SPECIES]:selected.add(lo+int(np.argmin(data[k][lo:hi])));selected.add(lo+int(np.argmax(data[k][lo:hi])))
 selected=np.array(sorted(selected),dtype=int)
 target=BASE/(case+'_display_samples.csv')
 with target.open('x',newline='') as f:
  w=csv.writer(f);w.writerow(['original_accepted_row',*data]);w.writerows([[int(i),*[data[k][i] for k in data]] for i in selected])
 info={'source_path':str(path.relative_to(ROOT)),'input_sha256':identities,'status':'TERMINAL_RESOURCE_CAPPED_PARTIAL','a_endpoint':END,'zbar_endpoint':1/END-1,'time_s_endpoint':data['t'][-1],'time_Myr_endpoint':data['t'][-1]/MYR,'accepted':200000,'full_rows_checked':index,'display_rows':len(selected),'display_csv_sha256':sha(target),'selection':'chronological 100-row blocks, first/last and min/max of each species and T; endpoints retained','positive_minimum':{k:float(data[k][data[k]>0].min()) for k in SPECIES},'zero_count':{k:int(np.count_nonzero(data[k]==0)) for k in SPECIES},'endpoint':{k:float(data[k][-1]) for k in ['T','x_HII','x_HeII','x_HeIII',*SPECIES]}}
 return {k:v[selected] for k,v in data.items()},info

def main():
 if (BASE/'FIGURE_MANIFEST.json').exists():raise ValueError('Existing figures; no overwrite')
 loaded={c:load(c,p) for c,p in CASES.items()}
 if loaded['ZERO'][1]['input_sha256']['source_identity.txt']!=loaded['SHEAR_PLUS'][1]['input_sha256']['source_identity.txt']:raise ValueError('Different library identities')
 outputs={};plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'savefig.dpi':180})
 for axis,name in [('time','abundance_vs_elapsed_time.png'),('temperature','abundance_vs_Tgas_time_ordered.png')]:
  fig,axs=plt.subplots(1,2,figsize=(14,6.8),sharey=True)
  for ax,c in zip(axs,CASES):
   d,info=loaded[c];x=d['t']/MYR if axis=='time' else d['T']
   for k,label,color in zip(SPECIES,LABELS,COLORS):
    ax.plot(x,np.ma.masked_where(d[k]==0,d[k]),label=label,color=color,lw=1.5,ls=':' if k=='electron' else '-')
    if axis=='temperature':
     for f in [.3,.65]:
      i=int(f*(len(x)-1));j=min(len(x)-1,i+max(1,len(x)//24))
      if d[k][i]>0 and d[k][j]>0:ax.annotate('',xy=(x[j],d[k][j]),xytext=(x[i],d[k][i]),arrowprops={'arrowstyle':'->','color':color,'lw':1})
   ymin=min(info['positive_minimum'].values());ax.set_yscale('log');ax.set_ylim(ymin/2,1.2);ax.grid(alpha=.2)
   ax.set_title(f'{c}: q_ref={"0" if c=="ZERO" else "+0.01"}\n20 → z̄ {info["zbar_endpoint"]:.8f}; {info["time_Myr_endpoint"]:.6f} Myr')
   ax.set_xlabel('Elapsed proper time since z̄ = 20 [Myr]' if axis=='time' else 'Gas temperature [K] (arrows: increasing time)')
  axs[0].set_ylabel(r'$Y_i=n_i/(n_H+4n_{He})$');h,l=axs[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.10))
  fig.suptitle('MATCHED SCALE FACTOR | TERMINAL PARTIAL HISTORIES | z̄ = 4 NOT REACHED',fontsize=15)
  fig.text(.5,.025,'Same terminal a; unequal elapsed proper time. No resolved shear, convergence, or trace-precision claim.\nExact zeros masked only on log display; all positive values retained without clipping. Chronological extrema-preserving display sampling.',ha='center',fontsize=10)
  fig.subplots_adjust(left=.08,right=.99,top=.83,bottom=.25,wspace=.12);fig.savefig(BASE/name);plt.close(fig);outputs[name]={'sha256':sha(BASE/name),'bytes':(BASE/name).stat().st_size}
 manifest={'scope':'MATCHED_A_TERMINAL_PARTIAL_ZERO_PLUS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),'cases':{c:i for c,(_,i) in loaded.items()},'figures':outputs,'normalization':'Y_i=n_i/(nH+4nHe); electron is charge census, not nucleus','proper_time_note':'Matched a/zbar does not imply matched elapsed proper time. Endpoint species differences are not claimed numerically resolved.','full_target_zbar':4,'full_target_reached':False,'scientific_admission':'NOT_ISSUED','solver_runs':0,'input_mutations':0,'versions':{'matplotlib':matplotlib.__version__,'numpy':np.__version__}}
 (BASE/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
