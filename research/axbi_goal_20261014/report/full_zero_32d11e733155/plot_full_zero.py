#!/usr/bin/env python3
"""Conditional ZERO full represented interval; no scientific admission or solver."""
import csv,datetime,hashlib,importlib.util,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
SOURCE=ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001'
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
LABELS=['H I','H II','He I','He II','He III',r'$e^-$ (charge census; not nucleus)']
COLORS=['#176b50','#0e88a9','#a26816','#de7625','#9250b4','#313a49']
MYR=365.25*86400*1e6

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def main():
 if (BASE/'FIGURE_MANIFEST.json').exists():raise ValueError('Existing plots; no overwrite')
 receipt=json.loads((SOURCE/'COMPOSITION_RECEIPT.json').read_text());case=json.loads((SOURCE/'COMPLETED_CASE_INPUT.json').read_text())
 if receipt['status']!='COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION' or case['id']!='ZERO' or receipt['row_counts']['history.csv']['composed_rows']!=312238 or receipt['cumulative_terminal']['accepted']!='312237':raise ValueError('HOLD composition scope/count')
 if receipt['original_binary_sha256']!='32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca' or receipt['execution_wrapper_identity']['new_binary_sha256']!='a7e3f1d98bd8a9b852357c95bb65bca4aabe13f45a9e679651d352af7dfe3b2b':raise ValueError('HOLD binary identity')
 bound={n:sha(SOURCE/n) for n in ['COMPOSITION_RECEIPT.json','COMPLETED_CASE_INPUT.json','history.csv','abundances.csv','config.cfg','source_identity.txt','checkpoint.txt','RETURN.txt','ORIGINAL_RETURN.txt','SEGMENT_RETURN.txt']}
 for n,digest in bound.items():
  if n!='COMPOSITION_RECEIPT.json' and digest!=receipt['output_sha256'][n]:raise ValueError('HOLD composition output identity '+n)
 for role in ['history','abundances','config','source_identity','terminal']:
  # Explicit descriptor paths must refer to this composed dataset, not another case.
  if (ROOT/Path(case[role]['path'])).resolve().parent!=SOURCE:raise ValueError('HOLD completed input path')
  case[role]['path']=str(ROOT/case[role]['path'])
 original=ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO/source_identity.txt'
 segment=ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_continuation_001/source_identity.txt'
 for p in [original,segment]:
  if sha(p)!=receipt['input_sha256'][str(p.relative_to(ROOT))] or sha(p)!=bound['source_identity.txt']:raise ValueError('HOLD original/segment library identity')
 readerpath=ROOT/'research/axbi_goal_20261014/convergence/compare_histories.py'
 spec=importlib.util.spec_from_file_location('completed_history_reader',readerpath);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
 loaded=reader.load_case(case)  # Entire joined interval: finite, ordered, species,
 # nuclei/charge/baryon normalization and history alignment at inherited 1e-12.
 s=loaded['series'];data={'time_s':np.asarray(s['time_s']),'Tgas_K':np.asarray(s['Tgas_K']),**{k:np.asarray(s['Y_'+k]) for k in SPECIES}}
 if len(data['time_s'])!=312238 or float(np.exp(s['L'][-1]))!=0.2:raise ValueError('HOLD selected endpoint/count')
 for n,digest in bound.items():
  if sha(SOURCE/n)!=digest:raise ValueError('HOLD changed completed input '+n)
 selected={0,len(data['time_s'])-1}
 for lo in range(0,len(data['time_s']),100):
  hi=min(len(data['time_s']),lo+100);selected.update((lo,hi-1))
  for k in ['Tgas_K',*SPECIES]:
   selected.add(lo+int(np.argmin(data[k][lo:hi])));selected.add(lo+int(np.argmax(data[k][lo:hi])))
 # Retain first positive point/global minimum even when a block minimum is zero.
 for k in SPECIES:
  pos=np.flatnonzero(data[k]>0)
  if len(pos):selected.update((int(pos[0]),int(pos[np.argmin(data[k][pos])])) )
 selected=np.array(sorted(selected));display={k:v[selected] for k,v in data.items()}
 with (BASE/'ZERO_display_samples.csv').open('x',newline='') as f:
  w=csv.writer(f);w.writerow(['global_accepted_row',*data]);w.writerows([[int(i),*[data[k][i] for k in data]] for i in selected])
 ymin=min(float(v[v>0].min()) for k,v in data.items() if k in SPECIES);ymax=max(float(v.max()) for k,v in data.items() if k in SPECIES)
 outputs={};plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'savefig.dpi':180})
 for axis,name in [('time','abundance_vs_elapsed_time.png'),('temperature','abundance_vs_Tgas_time_ordered.png')]:
  fig,ax=plt.subplots(figsize=(11.8,7.2));x=display['time_s']/MYR if axis=='time' else display['Tgas_K']
  for k,label,color in zip(SPECIES,LABELS,COLORS):
   ax.plot(x,np.ma.masked_where(display[k]==0,display[k]),label=label,color=color,lw=1.7,ls=':' if k=='electron' else '-')
   if axis=='temperature':
    for fraction in [.25,.55,.8]:
     i=int(fraction*(len(x)-1));j=min(len(x)-1,i+max(1,len(x)//24))
     if display[k][i]>0 and display[k][j]>0:ax.annotate('',xy=(x[j],display[k][j]),xytext=(x[i],display[k][i]),arrowprops={'arrowstyle':'->','color':color,'lw':1.2})
  ax.set_yscale('log');ax.set_ylim(ymin/2,max(1.2,2*ymax));ax.grid(alpha=.2)
  ax.set_xlabel('Elapsed proper time since z̄ = 20 [Myr]' if axis=='time' else 'Gas temperature [K] (arrows: increasing time)');ax.set_ylabel(r'$Y_i=n_i/(n_H+4n_{He})$')
  ax.set_title(f'ZERO (q_ref=0): z̄ 20 → 4; elapsed {data["time_s"][-1]/MYR:.6f} Myr\nConditional source/IC model; independent full-history science review pending',fontsize=13)
  ax.legend(loc='lower right',ncol=2,framealpha=.9)
  fig.text(.5,.024,'Exact zeros masked only for log display; retained positive values have no floor or clipping. Extrema-preserving sampling.\nChronological Tgas path; no convergence, resolved shear, absolute-age, observer-tail, or tiny-trace precision claim.',ha='center',fontsize=10)
  fig.subplots_adjust(left=.10,right=.98,top=.85,bottom=.18);fig.savefig(BASE/name);plt.close(fig);outputs[name]={'sha256':sha(BASE/name),'bytes':(BASE/name).stat().st_size}
 manifest={'status':'CONDITIONAL_FULL_INTERVAL_ZERO_FIGURES_PENDING_SCIENCE_REVIEW','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),'validation_reader_sha256':sha(readerpath),'source_path':str(SOURCE.relative_to(ROOT)),'input_sha256':bound,'original_binary_sha256':receipt['original_binary_sha256'],'execution_wrapper_identity':receipt['execution_wrapper_identity'],'original_segment_source_identity_sha256':bound['source_identity.txt'],'endpoint':{'a':0.2,'zbar':4,'accepted':312237,'time_s':float(data['time_s'][-1]),'elapsed_Myr':float(data['time_s'][-1]/MYR),'Tgas_K':float(data['Tgas_K'][-1]),'x_HII':s['x_HII'][-1],'x_HeII':s['x_HeII'][-1],'x_HeIII':s['x_HeIII'][-1]},'full_rows_validated':312238,'display_rows':len(selected),'display_csv_sha256':sha(BASE/'ZERO_display_samples.csv'),'selection':'Each chronological 100-row block first/last and min/max of T and six species; full endpoints and first positive/global positive minima also retained','positive_minimum':{k:float(data[k][data[k]>0].min()) for k in SPECIES},'zero_count':{k:int(np.count_nonzero(data[k]==0)) for k in SPECIES},'normalization':'Y_i=n_i/(nH+4nHe); electrons labelled charge census, not nucleus','clock':'Elapsed proper seconds since zbar20, not absolute cosmic age','temperature_order':'Saved chronology; never sorted by temperature','full_history_feedback':receipt['full_history_feedback'],'full_history_tau':receipt['full_history_tau'],'figures':outputs,'scientific_admission':'NOT_ISSUED','solver_runs':0,'source_mutations':0,'versions':{'matplotlib':matplotlib.__version__,'numpy':np.__version__}}
 (BASE/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
