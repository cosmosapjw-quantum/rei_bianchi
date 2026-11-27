#!/usr/bin/env python3
"""Render frozen PHYS18 exact interval results; no scientific recomputation."""
from pathlib import Path
from fractions import Fraction
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
CORE=HERE.parent
sources={
 'main':CORE/'checks/application/run02/results/MIXED_RESPONSE_RESULTS.json',
 'readout':CORE/'checks/application/readout01/results/FINITE_MIXED_READOUT.json',
 'readout_summary':CORE/'checks/application/readout01/results/SUMMARY.json'}
r=json.loads(sources['main'].read_text())
rs=json.loads(sources['readout_summary'].read_text())
def number(s):
 s=str(s)
 if 'E' in s.upper():
  mant,exp=s.upper().split('E')
  return mant+r'\times10^{'+str(int(exp))+'}'
 return s
def interval(z):
 a=z['outward_decimal'] if isinstance(z,dict) else z
 return r'$['+number(a[0])+r',\ '+number(a[1])+']$'
rows=[('$W_{d,x_{\\rm HII}}$', '1'),('$W_{d,y_{\\rm HeII}}$', '1'),('$W_{d,y_{\\rm HeIII}}$','1'),('$W_{d,w}$',r'$\mathrm{eV/H}$')]
t=[r'\begin{table}[H]',r'\centering\small',r'\caption{최종 mixed gas defect 포함. 두 매개변수는 무차원이다.}',r'\label{tab:mixed-gas}',r'\begin{tabular}{lll}\toprule',r'좌표 & 구간 & 단위 \\\midrule']
for (name,unit),z in zip(rows,r['d_mixed_intersection']):t.append(name+' & '+interval(z)+' & '+unit+r' \\')
t += [r'\bottomrule\end{tabular}',r'\end{table}']
(HERE/'numeric_table.tex').write_text('\n'.join(t)+'\n')
groups=rs['grouped_attribution_K']
group_rows=[('HH 기울기 묶음',groups['HH_gradient_terms']),('일곱 광자 항',groups['photon_seven_sectors']),('나머지 기체와 endpoint 항',groups['remaining_gas_and_endpoint_terms']),('온도 분모와 기하 항',rs['thermal_geometry_K'])]
t=[r'\begin{table}[H]',r'\centering\small',r'\caption{Full 역연산자로 전달한 강제항 묶음과 유한 온도 분모의 별도 기여. 단위 K.}',r'\label{tab:groups}',r'\begin{tabular}{ll}\toprule',r'묶음 & 온도 혼합 기여 \\\midrule']
for name,z in group_rows:t.append(name+' & '+interval(z)+r' \\')
t += [r'\bottomrule\end{tabular}',r'\end{table}']
(HERE/'contribution_table.tex').write_text('\n'.join(t)+'\n')

plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'figure.dpi':150})
fig,ax=plt.subplots(figsize=(7.8,2.85),layout='constrained')
keys=['DeltaT_mixed_original_subtraction_K','DeltaT_mixed_direct_K','DeltaT_mixed_correlated_K']
names=['Original response subtraction','Direct mixed implicit equation','Correlated mixed defect']
colors=['#6b7280','#1d5b8f','#8d2439']
for i,(k,c) in enumerate(zip(keys,colors)):
 lo,hi=[float(s)/1e-12 for s in r[k]['outward_decimal']];y=2-i
 ax.hlines(y,lo,hi,color=c,lw=6,alpha=.9);ax.plot([lo,hi],[y,y],'|',color=c,ms=13)
 ax.text((lo+hi)/2,y+.13,f'[{lo:.4f}, {hi:.4f}]',ha='center',va='bottom',fontsize=9,color=c)
ax.axvline(0,color='#aa3333',linestyle='--',lw=1)
ax.set_yticks([2,1,0],names);ax.set_ylim(-.45,2.65)
ax.set_xlabel(r'Mixed temperature defect $\partial_{\lambda b} F$ [$10^{-12}$ K]')
ax.grid(axis='x',alpha=.2);ax.tick_params(axis='y',length=0)
fig.savefig(HERE/'figures/mixed_enclosure_comparison.pdf');fig.savefig(HERE/'figures/mixed_enclosure_comparison.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.8,3.25),layout='constrained')
items=[('HH: stage birth increment','HH_gradient_birth_increment'),('HH: endpoint birth defect','endpoint_HH_birth_defect'),('Birth backward Euler','birth_backward_euler'),('Opacity change','opacity_change')]
for i,(name,k) in enumerate(items):
 lo,hi=[float(s)/1e-12 for s in r['contributions'][k]['temperature_K']['outward_decimal']]
 ax.hlines(4-i,lo,hi,lw=6,color='#235e83');ax.plot([lo,hi],[4-i,4-i],'|',color='#235e83',ms=13)
lo,hi=[float(s)/1e-12 for s in r['temperature_geometry_K']['outward_decimal']]
ax.hlines(0,lo,hi,lw=6,color='#8d2439');ax.plot([lo,hi],[0,0],'|',color='#8d2439',ms=13)
ax.axvline(0,color='#777777',linestyle='--',lw=1)
ax.set_yticks([4,3,2,1,0],[z[0] for z in items]+['Temperature geometry'])
ax.set_xlabel(r'Mixed temperature contribution [$10^{-12}$ K]');ax.set_ylim(-.5,4.5)
ax.grid(axis='x',alpha=.2);ax.tick_params(axis='y',length=0)
fig.savefig(HERE/'figures/mixed_mechanism.pdf');fig.savefig(HERE/'figures/mixed_mechanism.png',dpi=180);plt.close(fig)

def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
made=[HERE/'numeric_table.tex',HERE/'contribution_table.tex',*sorted((HERE/'figures').glob('*'))]
provenance={'purpose':'Tables use outward decimal displays from frozen exact rational results; plots display these enclosures, not simulated trajectories.','sources':[{'path':str(p.relative_to(CORE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources.values()],'outputs':[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in made],'scientific_rerun':False}
(HERE/'DATA_AND_FIGURE_PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'generated':len(made),'source_identity_count':len(sources),'scientific_rerun':False}))
