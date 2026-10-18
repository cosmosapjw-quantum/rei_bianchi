#!/usr/bin/env python3
"""Presentation consumer only; every saved native state, actual Ybaryon."""
import argparse,csv,hashlib,json,math
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
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();c=json.loads(args.contract.read_text())
 require(c.get('execution_authorized_after_raw_review') is True,'RAW_RESULT_REVIEW_PASS_AND_FROZEN_CONTRACT_REQUIRED');require(sha(__file__)==c['script_sha256'],'SCRIPT_CHANGED');require(len(c['cases'])==2 and all(x['coverage_complete'] is True for x in c['cases']),'FOUR_FIGURES_REQUIRE_BOTH_TRUE_COMPLETE')
 require(not args.output.exists(),'FRESH_OUTPUT_REQUIRED');args.output.mkdir(parents=True)
 for item in c['bound_small_files']:require(sha(item['path'])==item['sha256'],'SMALL_INPUT_BINDING_CHANGED')
 loaded=[];observations={}
 for case in c['cases']:
  arrays=[];group=[];count=0;digest=hashlib.sha256();raw=Path(case['abundances_path'])
  with raw.open('rb') as f:
   def decoded_lines():
    for line in f:digest.update(line);yield line.decode('utf-8')
   reader=csv.DictReader(decoded_lines())
   for row in reader:
    group.append(row)
    if len(group)!=6:continue
    require([x['species_id'] for x in group]==SPECIES,'SIX_SPECIES_GROUP');require([(x['A'],x['Z'],x['charge']) for x in group]==[('1','1','0'),('1','1','1'),('4','2','0'),('4','2','1'),('4','2','2'),('0','','-1')],'SPECIES_METADATA');require(all(all(x[k]==group[0][k] for k in ['time_s','Tgas_K','zbar','background_Tref_K']) for x in group),'EXACT_GROUP_METADATA');require(all(x['run_id']==case['case'] and x['normalization_registry']=='BASELINE_H_HE_CHARGE_AND_BARYON_V1' for x in group),'CASE_OR_NORMALIZATION_REGISTRY')
    t=float(group[0]['time_s']);temp=float(group[0]['Tgas_K']);require(all(float(x['time_s'])==t and float(x['Tgas_K'])==temp for x in group),'GROUP_CLOCK_TEMPERATURE');ys=[float(x['Ybaryon']) for x in group];require(math.isfinite(t) and math.isfinite(temp) and all(math.isfinite(y) and y>=0 for y in ys),'FINITE_ACTUAL_Y_DOMAIN');arrays.append([t,temp,*ys]);count+=1;group=[]
  require(not group and count==case['expected_saved_states'],'ALL_NATIVE_SAVED_STATES_REQUIRED');require(digest.hexdigest()==case['abundances_sha256'],'ACTUAL_CSV_SHA_MISMATCH');a=np.asarray(arrays);require(a[0,0]==0.0 and np.all(np.diff(a[:,0])>0),'ELAPSED_TIME_OR_CHRONOLOGY');zero={sp:int(np.count_nonzero(a[:,2+j]==0)) for j,sp in enumerate(SPECIES)};loaded.append((case,a));observations[case['case']]={'saved_states':count,'input_sha256_actual_stream':digest.hexdigest(),'exact_zero_counts':zero,'initial_time_s':float(a[0,0]),'initial_Tgas_K':float(a[0,1]),'final_time_s':float(a[-1,0]),'final_Tgas_K':float(a[-1,1]),'first_last_ionic_Y':[a[0,2:7].tolist(),a[-1,2:7].tolist()],'first_last_electron_Ye':[float(a[0,7]),float(a[-1,7])],'downsampled':False}
 # All actual input consumers finished before publishing this four-figure set.
 figures=[]
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
 for case,a in loaded:
  ys=a[:,2:];zero=observations[case['case']]['exact_zero_counts']
  for coordinate in ['elapsed_time','Tgas_chronological']:
   x=a[:,0]/MYR if coordinate=='elapsed_time' else a[:,1];fig,(ion,ele)=plt.subplots(2,1,figsize=(10,7.4),sharex=True,gridspec_kw={'height_ratios':[3,1.4]},layout='constrained')
   for j,label in enumerate(LABELS):ion.plot(x,np.ma.masked_where(ys[:,j]==0,ys[:,j]),label=label,color=COLORS[j],lw=1.4)
   ele.plot(x,np.ma.masked_where(ys[:,5]==0,ys[:,5]),color='#333333',label='electron',lw=1.4)
   for ax in [ion,ele]:ax.set_yscale('log');ax.grid(alpha=.2);ax.legend(loc='best',ncol=3 if ax is ion else 1)
   ion.set_ylabel(r'$Y_i=n_i/(n_H+4n_{He})$');ele.set_ylabel(r'$Y_e=n_e/(n_H+4n_{He})$')
   ele.set_xlabel('Elapsed proper time since z = 20 [Myr]' if coordinate=='elapsed_time' else 'Gas temperature [K] — saved chronological path')
   fig.suptitle(case['case']+' | conditional BASS source009 short z20 → 19.8')
   ion.text(.01,1.015,'Exact zeros masked: '+', '.join(label+' '+str(zero[sp]) for label,sp in zip(LABELS,SPECIES)),transform=ion.transAxes,fontsize=8)
   ion.text(.01,.015,'All saved states; initial T ≈ 8.098 K differs from full005 REC IC',transform=ion.transAxes,fontsize=8)
   ele.text(.01,.03,'Electron A = 0 excluded from baryons; exact zeros masked: '+str(zero['electron']),transform=ele.transAxes,fontsize=8)
   if coordinate=='Tgas_chronological':
    for j in [0,5]:
     ax=ion if j==0 else ele;valid=np.flatnonzero(ys[:,j]>0)
     for frac in [.2,.5,.8]:
      if len(valid)>1:
       k=int(frac*(len(valid)-1));i=int(valid[k]);n=int(valid[min(k+max(1,len(valid)//70),len(valid)-1)])
       if i!=n:ax.annotate('',xy=(x[n],ys[n,j]),xytext=(x[i],ys[i,j]),arrowprops={'arrowstyle':'->','color':COLORS[0] if j==0 else '#333333','lw':1.3})
   name=case['case']+'_Y_vs_'+coordinate+'.png';fig.savefig(args.output/name,dpi=160);plt.close(fig);figures.append({'path':name,'sha256':sha(args.output/name),'bytes':(args.output/name).stat().st_size})
 receipt={'status':'CONDITIONAL_BASS_SOURCE009_SHORT_Z20_19P8_PRESENTATION_ONLY_REVIEW_PENDING','scope':'actual saved Ybaryon, all native saved states, no Tsort/downsampling/floors; proper elapsed time not absoluteage','normalization':'ni/(nH+4nHe), HHe modeled baryon inventory; electron separate and A0excluded','cases':observations,'figures':figures,'scientific_admission':'NOT_ISSUED','full_time_angular_accuracy':'HOLD','D_activation':'ABSENT','versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__},'solver_ledger_checkpoint_replays':0};write(args.output/'PRESENTATION_RECEIPT.json',receipt);(args.output/'README.md').write_text('# Conditional source009 short-history presentation\n\nFour figures consume every saved native abundance state as actual Ybaryon=ni/(nH+4nHe), with ionic Y and electron Ye in separate logarithmic panels. Time is linear elapsed proper Myr since z20 including t0; temperature plots retain chronology and show time-direction arrows. Zeros are counted and masked, never floored. No solver, ledger or checkpoint was replayed.\n\nThis conditional short interval uses initial T8.098K distinct from full005 REC IC; it is not an absolute-age, D, full-history or accuracy admission. Source008 mode sensitivity and time/angular convergence HOLD remain.\n');print(json.dumps({'status':receipt['status'],'figures':len(figures),'states':{k:v['saved_states'] for k,v in observations.items()}}))
if __name__=='__main__':main()
