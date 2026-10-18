#!/usr/bin/env python3
"""Presentation only: selected actual CSV Ybaryon, preserving saved chronology."""
import argparse,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
LABELS=['H I','H II','He I','He II','He III']
COLORS=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00']
MYR=365.25*86400*1e6
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def require(ok,why):
 if not ok:raise ValueError(why)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();c=json.loads(args.contract.read_text());out=args.output
 require(out.is_dir() and not any(out.iterdir()),'FRESH_EMPTY_OUTPUT_REQUIRED')
 for item in c['bound_small_files']:require(sha(item['path'])==item['sha256'],'BOUND_FILE_CHANGED '+item['path'])
 require(sha(__file__)==c['script_sha256'],'SCRIPT_IDENTITY_CHANGED')
 report={'status':'PRESENTATION_COMPLETE_REVIEW_PENDING','scientific_admission':'NOT_ISSUED','full_convergence':'HOLD','solver_runs':0,'raw_abundance_streams_per_case':1,'normalization':'Yi=ni/nb from actual Ybaryon; nb=nH+4nHe; electron A=0 excluded from nb and Ye=ne/nb shown separately','coordinate_policy':'elapsed proper Myr since z20; Tgas parametric saved chronology, never sorted by temperature','zero_policy':'raw exact zeros preserved in selected CSV; only >0 shown on log ordinate, zeros masked without floors','versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__},'cases':{}}
 for case in c['cases']:
  with Path(case['display_path']).open() as f:selected=list(csv.DictReader(f))
  indices=[int(x['accepted_row']) for x in selected];require(indices==sorted(set(indices)),'DISPLAY_INDICES_NOT_STRICTLY_INCREASING')
  selected_map={int(x['accepted_row']):x for x in selected};actual=[];group=[];groups=0;raw_rows=0
  with Path(case['abundances_path']).open(newline='') as f:
   reader=csv.DictReader(f)
   required=['run_id','time_s','Tgas_K','species_id','A','Ybaryon','normalization_registry'];require(all(k in reader.fieldnames for k in required),'ACTUAL_HEADER_MISSING')
   for row in reader:
    raw_rows+=1;group.append(row)
    if len(group)<6:continue
    if groups in selected_map:
     display=selected_map[groups]
     require([x['species_id'] for x in group]==SPECIES,'SELECTED_SIX_SPECIES_GROUP_MISMATCH')
     require(all(x['run_id']==case['id'] and x['normalization_registry']=='BASELINE_H_HE_CHARGE_AND_BARYON_V1' for x in group),'SELECTED_CASE_OR_REGISTRY_MISMATCH')
     require([int(x['A']) for x in group]==[1,1,4,4,4,0],'SELECTED_MASS_NUMBER_MISMATCH')
     require(all(float(x['time_s'])==float(display['elapsed_time_s']) and float(x['Tgas_K'])==float(display['Tgas_K']) for x in group),'SELECTED_EXACT_CLOCK_TEMPERATURE_MISMATCH')
     ys=[float(x['Ybaryon']) for x in group];require(all(math.isfinite(y) and y>=0 for y in ys),'SELECTED_Y_DOMAIN')
     actual.append([groups,group[0]['time_s'],group[0]['Tgas_K'],*[x['Ybaryon'] for x in group]])
    groups+=1;group=[]
  require(not group and groups==case['expected_history_rows'] and len(actual)==len(selected),'ROW_ALIGNMENT_OR_SELECTION_COUNT_MISMATCH')
  csvpath=out/(case['id']+'_selected_actual_Y.csv')
  with csvpath.open('x',newline='') as f:
   w=csv.writer(f);w.writerow(['accepted_row','elapsed_time_s','Tgas_K',*['Y_'+x for x in SPECIES]]);w.writerows(actual)
  a=np.asarray([[float(v) for v in row] for row in actual]);ys=a[:,3:];zeros={sp:int(np.count_nonzero(ys[:,j]==0)) for j,sp in enumerate(SPECIES)}
  # Sanity within this single execution: plotted Y equals parsed actual Y, with no transform.
  require(len(a)==len(indices) and np.array_equal(a[:,0],indices),'SELECTED_OUTPUT_ALIGNMENT')
  figs=[]
  for coordinate in ['elapsed_time','Tgas_chronological']:
   x=a[:,1]/MYR if coordinate=='elapsed_time' else a[:,2]
   fig,(ion,ele)=plt.subplots(2,1,figsize=(10,7.4),sharex=True,gridspec_kw={'height_ratios':[3,1.4]},layout='constrained')
   for j,label in enumerate(LABELS):ion.plot(x,np.ma.masked_where(ys[:,j]==0,ys[:,j]),label=label,color=COLORS[j],lw=1.3)
   ele.plot(x,np.ma.masked_where(ys[:,5]==0,ys[:,5]),color='#333333',lw=1.4,label='electron')
   for ax in [ion,ele]:ax.set_yscale('log');ax.grid(alpha=.2);ax.legend(loc='best',ncol=3 if ax is ion else 1)
   ion.set_ylabel(r'$Y_i=n_i/n_b$ (H/He ions)');ele.set_ylabel(r'$Y_e=n_e/n_b$')
   ele.set_xlabel('Elapsed proper time since z = 20 [Myr]' if coordinate=='elapsed_time' else 'Gas temperature [K] — saved chronological path')
   fig.suptitle('source005 conditional FLRW z20 → 4 | '+case['id'].replace('FLRW_FULL_',''))
   ion.text(.01,.015,'Full convergence: HOLD; H/He inventory only',transform=ion.transAxes,fontsize=9)
   zero_text='Exact-zero selected points masked: '+', '.join(label+' '+str(zeros[sp]) for label,sp in zip(LABELS,SPECIES[:5]))
   ion.text(.01,1.015,zero_text,transform=ion.transAxes,fontsize=8)
   ele.text(.01,.03,'Electron exact zeros masked: '+str(zeros['electron'])+'; baryons: nH + 4nHe (electron A = 0 excluded)',transform=ele.transAxes,fontsize=8)
   if coordinate=='Tgas_chronological':
    # Arrow positions are chosen by saved row order; coordinates never sorted.
    for j in [0,5]:
     ax=ion if j==0 else ele;positive=np.flatnonzero(ys[:,j]>0)
     for frac in [.2,.5,.8]:
      if len(positive)>1:
       k=int(frac*(len(positive)-1));i=int(positive[k]);n=int(positive[min(k+max(1,len(positive)//80),len(positive)-1)])
       if i!=n:ax.annotate('',xy=(x[n],ys[n,j]),xytext=(x[i],ys[i,j]),arrowprops={'arrowstyle':'->','color':COLORS[j] if j<5 else '#333333','lw':1.4})
   name=case['id']+'_Yi_vs_'+coordinate+'.png';fig.savefig(out/name,dpi=160);plt.close(fig);figs.append(name)
  report['cases'][case['id']]={'selected_rows':len(actual),'first_accepted_row':indices[0],'last_accepted_row':indices[-1],'raw_abundance_rows_streamed':raw_rows,'accepted_state_groups':groups,'selected_exact_time_Tgas_matches':len(actual)*6,'raw_zeros_by_species':zeros,'actual_csv_expected_sha256':case['abundances_sha256'],'actual_csv_sha_recomputed':False,'input_sha_evidence':'reused prior strict completed POSTPROCESS_RECEIPT; no full raw hash replay','selected_csv':csvpath.name,'figures':figs}
 require(len(list(out.glob('*.png')))==4,'EXPECTED_FOUR_PNG')
 write(out/'PRESENTATION_RECEIPT.json',report)
 (out/'README.md').write_text('# Actual baryon-normalized H/He presentation\n\nFour source005 conditional FLRW z20 to4 figures show actual CSV Ybaryon values. The complete modeled baryon inventory is n_b = n_H + 4 n_He. Electron Y_e is separate and contributes zero baryon number. No species fraction is renormalized.\n\nElapsed time is proper time since z20 in Myr, not absolute age. Temperature paths retain accepted-state chronology; arrows show forward time. Exact zeros remain in selected CSVs and are masked without floors on log plots; annotations count selected zeros.\n\nSelections exactly reuse the existing display accepted_row indices and exactly match actual six-species-group time_s and Tgas_K. No physics or ledger validation was replayed. Full convergence remains HOLD; scientific admission remains NOT_ISSUED. These figures contain no D or Bianchi evolution.\n')
 print(json.dumps({'status':report['status'],'figures':4,'selected_rows':{k:v['selected_rows'] for k,v in report['cases'].items()}}))
if __name__=='__main__':main()
