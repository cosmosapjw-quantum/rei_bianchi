"""Actual-sample scientific figures and CSV exports; no IVP calls."""
import csv,hashlib,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/rei-hheli-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import atomic as at


def csvwrite(path,rows):
 if not rows:return
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def render(base,manifest):
 out=base/'figures';out.mkdir(exist_ok=True);cases=[];data={};receipts={}
 for case in manifest['cases']:
  p=base/'cases'/case['id'];rp=p/'RESULT.json'
  if not rp.exists():continue
  r=json.loads(rp.read_text())
  if r.get('status') not in ('COMPLETED','COMPUTED_GATE_FAILURE'):continue
  raw=p/'raw.npz'
  if hashlib.sha256(raw.read_bytes()).hexdigest()!=r['raw_sha256']:raise ValueError('PLOT_RAW_IDENTITY')
  with np.load(raw,allow_pickle=False) as z:data[case['id']]={k:np.array(z[k]) for k in z.files}
  cases.append(case);receipts[case['id']]=r
 nominal=[c for c in cases if c['config']['kind']!='combined_refinement'];summary=json.loads((base/'SUMMARY.json').read_text());rows=[]
 for c in cases:
  r=data[c['id']];cfg=c['config'];entry={'case_id':c['id'],'kind':cfg['kind'],'Sigma_F0':cfg['Sigma_F0'],'A_m':cfg['A_m'],'A_r':cfg['A_r'],'orientation':cfg['orientation'],'L':cfg['L'],'P_m0':float(r['P_m'][0]),'P_r0':float(r['P_r'][0]),'S_F0':float(r['signed_Sigma'][0])}
  entry.update({k:float(r[k][-1]) for k in ('signed_Sigma','Sigma_F','P_m','P_gamma','P_nu','P_r','Pi_m','Pi_r','Pi_total','ne_m3','tau_T','U_thermal_J_m3','U_binding_J_m3','U_UV_J_m3','test_fluid_energy_ratio')})
  entry.update({'Y_'+name:float(r['Y_Aq'][i,-1]) for i,name in enumerate(at.NAMES)});entry.update(minimum_fraction=receipts[c['id']]['diagnostics']['minimum_fraction'],minimum_sampled_brightness=receipts[c['id']]['diagnostics']['sampled_brightness_minimum']);rows.append(entry)
 csvwrite(out/'all_computed_endpoints.csv',rows)
 if not nominal:return
 plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'legend.fontsize':8,'xtick.labelsize':9,'ytick.labelsize':9,'savefig.dpi':160,'pdf.fonttype':42})
 plotmap={}
 def save(fig,name,fields):
  fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig);plotmap[name]=fields
 def pick(**conditions):
  return next(c for c in nominal if all(c['config'].get(k)==v for k,v in conditions.items()))
 iso=pick(Sigma_F0=0.,A_m=0.,A_r=0.,kind='grid');strong=pick(Sigma_F0=.6,A_m=1.6,A_r=-.8,orientation=1);negative=pick(Sigma_F0=.6,A_m=1.6,A_r=-.8,orientation=-1)
 cancel=[c for c in nominal if c['config']['kind']=='cancellation']
 selected=[iso,strong,negative]+cancel
 history=[]
 for c in selected:
  raw=data[c['id']]
  for i in range(257):
   row={'case_id':c['id'],'kind':c['config']['kind'],'sample_index':i}
   row.update({k:float(v[i]) for k,v in raw.items() if v.ndim==1 and len(v)==257});row.update({'f_'+name:float(raw['conditional_f'][j,i]) for j,name in enumerate(at.NAMES)});row.update({'Y_'+name:float(raw['Y_Aq'][j,i]) for j,name in enumerate(at.NAMES)});history.append(row)
 csvwrite(out/'selected_histories.csv',history)
 # Realized physical initial axes, actual point colors; no interpolated field.
 values=[float(data[c['id']]['signed_Sigma'][-1]) for c in nominal];bound=max(map(abs,values));norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound)
 fig,axs=plt.subplots(2,3,figsize=(10.8,6.6),layout='constrained')
 for ax,sigma in zip(axs.ravel()[:5],(0.,.01,.05,.2,.6)):
  chosen=[c for c in nominal if c['config']['kind']=='grid' and c['config']['Sigma_F0']==sigma]
  sc=ax.scatter([data[c['id']]['P_m'][0] for c in chosen],[data[c['id']]['P_r'][0] for c in chosen],c=[data[c['id']]['signed_Sigma'][-1] for c in chosen],cmap='RdBu_r',norm=norm,s=70,edgecolors='.3',linewidths=.4)
  ax.set_title(f'Initial Sigma_F = {sigma:g}');ax.set_xlabel('Realized signed P_m at z=20');ax.set_ylabel('Realized signed P_r at z=20');ax.ticklabel_format(style='sci',scilimits=(-2,2));ax.axhline(0,color='.7',lw=.6);ax.axvline(0,color='.7',lw=.6)
 ax=axs.ravel()[5]
 for c in nominal:
  if c['config']['kind']=='grid':continue
  r=data[c['id']];ax.scatter(r['P_m'][0],r['P_r'][0],c=[r['signed_Sigma'][-1]],cmap='RdBu_r',norm=norm,s=90,marker='D' if c['config']['kind']=='cancellation' else 'v',edgecolors='black')
 ax.set_title('Two cancellations + two negative-shear cases');ax.set_xlabel('Realized signed P_m at z=20');ax.set_ylabel('Realized signed P_r at z=20');ax.ticklabel_format(style='sci',scilimits=(-2,2));fig.colorbar(sc,ax=axs.ravel().tolist(),label='Saved final signed S_F at z=2',shrink=.85)
 fig.suptitle('79 actual nominal cases: sampled endpoints on realized physical axes\n75 grid points + 4 explicit additions; no interpolation between cases',fontsize=13);save(fig,'realized_initial_plane_final_signed_shear','all_computed_endpoints.csv')
 colors=['#0072B2','#D55E00','#009E73'];labels=['Isotropic zero-stress seed','Positive shear 0.6, A_m=1.6, A_r=-0.8','Negative shear -0.6, A_m=1.6, A_r=-0.8']
 fig,axs=plt.subplots(2,2,figsize=(8.4,6.5),layout='constrained')
 for ax,key,title in zip(axs.ravel(),('Sigma_F','Pi_m','Pi_r','Pi_total'),('Shear norm','Massive-matter stress norm','Photon + neutrino stress norm','Total signed-sum stress norm')):
  for c,col,label in zip(selected[:3],colors,labels):
   r=data[c['id']];ax.plot(r['z'],r[key],color=col,label=label)
  ax.set_xlim(20,2);ax.set_xlabel('Redshift z');ax.set_ylabel(key+' [dimensionless]');ax.set_title(title)
 axs[0,0].legend(loc='upper right',fontsize=7);fig.suptitle('Separate source norms on three actual coupled trajectories\n257 stored samples; connected lines are visual guides',fontsize=12);save(fig,'shear_and_stress_norm_histories','selected_histories.csv: Sigma_F,Pi_m,Pi_r,Pi_total')
 fig,axs=plt.subplots(2,1,figsize=(7.2,6.1),layout='constrained')
 for ax,c,title in zip(axs,(strong,negative),('Positive initial shear +0.6','Negative initial shear -0.6')):
  r=data[c['id']]
  for key,col in zip(('P_m','P_gamma','P_nu','P_r'),('#0072B2','#D55E00','#009E73','#CC79A7')):ax.plot(r['z'],r[key],label=key,color=col)
  ax.axhline(0,color='.5',lw=.7);ax.set_xlim(20,2);ax.set_xlabel('Redshift z');ax.set_ylabel('Signed stress [dimensionless]');ax.set_title(title);ax.legend(ncol=4)
 fig.suptitle('Photons and neutrinos evolve independently\nDynamic atomic electrons scatter photons only; lines join saved samples',fontsize=12);save(fig,'photon_neutrino_signed_stress','selected_histories.csv: P_m,P_gamma,P_nu,P_r')
 fig,axs=plt.subplots(2,2,figsize=(8.4,6.5),layout='constrained')
 for col,c in enumerate(cancel):
  r=data[c['id']];cfg=c['config'];axs[0,col].plot(r['z'],r['signed_Sigma'],label='signed S_F',color='#762a83');axs[0,col].set_title(f'Initial A_m={cfg["A_m"]:+g}, A_r={cfg["A_r"]:+.6g}')
  for key in ('P_m','P_r') :axs[1,col].plot(r['z'],r[key],label=key)
  axs[1,col].plot(r['z'],r['P_m']+r['P_r'],'--',label='P_m + P_r')
 for ax in axs.ravel():ax.axhline(0,color='.5',lw=.7);ax.set_xlim(20,2);ax.set_xlabel('Redshift z');ax.set_ylabel('Signed dimensionless quantity');ax.legend()
 fig.suptitle('Two actual initially cancelling component sources\nSigma_F,0=0; later cancellation is not imposed',fontsize=12);save(fig,'initially_cancelling_histories','selected_histories.csv: both cancellation cases')
 # Explicit isotope panels, including high-charge Li zeros.
 r=data[strong['id']];fig,axs=plt.subplots(3,2,figsize=(7.2,8.4),layout='constrained')
 for ax,name in zip(axs.ravel(),('H1','D','He3','He4','Li6','Li7')):
  sl=at.SLICES[name]
  for q,i in enumerate(range(sl.start,sl.stop)):ax.plot(r['z'],r['conditional_f'][i],label=f'q={q}',lw=1.4)
  ax.set_xlim(20,2);ax.set_xlabel('Redshift z');ax.set_ylabel('Conditional charge fraction');ax.set_title(f'{name}: Y_nucleus={at.ABUNDANCES[name]:.4g}');ax.legend(ncol=2)
  if name.startswith('Li'):ax.text(.03,.35,'q=2 and q=3 remain exactly zero\nfor this UV support and initial state',transform=ax.transAxes,fontsize=7)
 fig.suptitle('All six populated isotopes: normalized charge histories\nSame-element overlaps follow ElementalElectronicEquality; n and T absent',fontsize=12);save(fig,'isotope_charge_histories','selected_histories.csv: f_H1*,f_D*,f_He3*,f_He4*,f_Li6*,f_Li7*')
 fig,ax=plt.subplots(figsize=(8.4,5.4),layout='constrained');ix=np.arange(21);ax.bar(ix-.18,r['Y_Aq'][:,0],.36,label='z=20');ax.bar(ix+.18,r['Y_Aq'][:,-1],.36,label='z=2');ax.set_yscale('symlog',linthresh=1e-16);ax.set_xticks(ix,at.NAMES,rotation=70,ha='right');ax.set_ylabel('Number abundance per baryon, Y_A f_Aq');ax.set_title('Complete 21-state output census; actual zeros retained\nn/T absent; Li III and Li IV remain zero; linear interval around zero');ax.legend();save(fig,'complete_21_state_abundance_census','selected_histories.csv: Y_*; actual stored zeros, no epsilon replacement')
 fig,axs=plt.subplots(2,2,figsize=(8.4,6.7),layout='constrained')
 for key in ('U_thermal_J_m3','U_binding_J_m3','U_UV_J_m3'):axs[0,0].plot(r['z'],r[key],label=key.replace('_J_m3',''))
 axs[0,0].set_ylabel('Energy density [J m^-3]');axs[0,0].legend();axs[0,0].set_title('Prescribed atomic / UV test-fluid contributions')
 axs[0,1].plot(r['z'],r['test_fluid_energy_ratio']);axs[0,1].set_ylabel('(U_thermal + U_binding + U_UV) / epsilon_bg');axs[0,1].set_title('Approximation diagnostic; not a trajectory error bound')
 for key in ('Q_thermal_required_J_m3_s','Q_binding_J_m3_s','P_photo_J_m3_s'):axs[1,0].plot(r['z'],r[key],label=key.replace('_J_m3_s',''))
 axs[1,0].set_ylabel('Power density [J m^-3 s^-1]');axs[1,0].legend(fontsize=7);axs[1,0].set_title('Required gas powers and absorbed UV power')
 axs[1,1].plot(r['z'],r['bath_minus_escaped_requirement_J_m3_s']);axs[1,1].axhline(0,color='.5',lw=.7);axs[1,1].set_ylabel('Q_gas_required - P_photo [J m^-3 s^-1]');axs[1,1].set_title('Combined bath-minus-escaped requirement')
 for ax in axs.ravel():ax.set_xlim(20,2);ax.set_xlabel('Redshift z');ax.ticklabel_format(axis='y',style='sci',scilimits=(-2,2))
 fig.suptitle('Declared energy ledger: positive ionization binding energy\nNo closed thermal / radiation solution or invented RR cooling is claimed',fontsize=12);save(fig,'prescribed_energy_ledger','selected_histories.csv: U*,Q*,P_photo*,epsilon_background')
 fig,axs=plt.subplots(2,2,figsize=(8.4,6.6),layout='constrained')
 allr=[receipts[c['id']] for c in cases];idx=np.arange(len(allr));axs[0,0].scatter(idx,[v['diagnostics']['sampled_brightness_minimum'] for v in allr],s=12);axs[0,0].axhline(-2e-8,color='black',ls='--');axs[0,0].set_title('257-angle sampled brightness minimum');axs[0,0].set_ylabel('Brightness / initial monopole')
 axs[0,1].scatter(idx,[max(v['diagnostics']['number_relative_drift'].values()) for v in allr],s=12);axs[0,1].axhline(2e-9,color='black',ls='--');axs[0,1].set_yscale('symlog',linthresh=1e-16);axs[0,1].set_title('Maximum conserved-number relative drift')
 axs[1,0].scatter(idx,[v['diagnostics']['isotope_sum_max'] for v in allr],s=12);axs[1,0].axhline(2e-9,color='black',ls='--');axs[1,0].set_yscale('symlog',linthresh=1e-16);axs[1,0].set_title('Conditional isotope sum residual')
 for j,comp in enumerate(summary['refinement']):
  axs[1,1].scatter(range(4),list(comp['max_abs_differences'].values()),label=f'Combined check {j+1}',s=30,marker=('o','s','^')[j])
 axs[1,1].axhline(2e-5,color='black',ls='--',label='Fixed 2e-5 criterion');axs[1,1].set_yscale('symlog',linthresh=1e-15);axs[1,1].set_xticks(range(4),['signed S_F','P_m','P_r','charge f']);axs[1,1].set_title('L16 vs L24 + tighter tolerance');axs[1,1].legend(fontsize=7)
 for ax in axs.ravel()[:3]:ax.set_xlabel('Computed case index')
 fig.suptitle('Finite diagnostics and three selected combined controls\nAlgebraic precision and sampled positivity are separate from convergence claims',fontsize=12);save(fig,'positivity_conservation_refinement','RESULT receipts + SUMMARY.json refinement; no IVPs in plotting')
 diag={name:float(np.max(abs(r['conditional_f'][at.SLICES[a]]-r['conditional_f'][at.SLICES[b]]))) for name,a,b in [('H1_D','H1','D'),('He3_He4','He3','He4'),('Li6_Li7','Li6','Li7')]}
 outputs={'plot_count':len(plotmap),'computed_cases':len(cases),'nominal_cases':len(nominal),'plot_data':plotmap,'example_case':strong['id'],'same_element_fraction_max_abs_differences_example':diag,'zero_abundance_species':['n','T'],'Li_high_charge_nominal':'q2/q3 structurally remain zero for declared source/IC; RR checked separately','data_only_render':True,'line_semantics':'Connected lines are visual guides through stored257samples; scatter planes are actual points only'}
 (out/'PLOT_MANIFEST.json').write_text(json.dumps(outputs,indent=2)+'\n')
