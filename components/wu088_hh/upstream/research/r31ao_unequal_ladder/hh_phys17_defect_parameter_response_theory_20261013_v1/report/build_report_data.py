#!/usr/bin/env python3
"""Create report tables and a finite-change plot from frozen PHYS17 results."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
APP=ROOT/'checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json'
FORCE=ROOT/'checks/application/forcing01/results/FORCING_FEEDBACK_RESULTS.json'
NEUMANN=ROOT/'checks/application/neumann02/results/DERIVATIVE_NEUMANN_RESULTS.json'
a=json.loads(APP.read_text());f=json.loads(FORCE.read_text())

def interval(z,exponent=None):
    lo,hi=map(Decimal,z['outward_decimal'])
    if exponent is None: exponent=max(abs(lo).adjusted(),abs(hi).adjusted())
    l,h=lo.scaleb(-exponent),hi.scaleb(-exponent)
    return rf'$[{l:f},{h:f}]\times10^{{{exponent}}}$'

rows=[('수소 이온화 차이',r'$d_{x,\theta}$','d_theta',0),
      ('He II 차이',r'$d_{y,\theta}$','d_theta',1),
      ('He III 차이',r'$d_{z,\theta}$','d_theta',2),
      ('열에너지 차이 [eV/H]',r'$d_{w,\theta}$','d_theta',3),
      ('전자 수 차이 [H당]',r'$d_{e,\theta}$','d_e_theta_per_H',None),
      ('온도 차이 [K]',r'$\Delta T_\theta$','DeltaT_theta_K',None)]
table=[r'\begin{table}[htbp]\centering\scriptsize',
       r'\caption{같은 전역 매개변수에 대한 실제 endpoint 결함의 1차 응답. 두 열은 각각 단위 무차원 매개변수당 값이다.}\label{tab:responses}',
       r'\setlength{\tabcolsep}{3pt}\begin{tabular}{lll}\toprule',
       r'관측량 & $\partial_\lambda$ 포함 & $\partial_b$ 포함\\\midrule']
for label,symbol,key,i in rows:
    vals=[a['responses'][p][key] if i is None else a['responses'][p][key][i] for p in ['lambda','b']]
    table.append(label+' '+symbol+' & '+interval(vals[0])+' & '+interval(vals[1])+r'\\')
table.append(r'\bottomrule\end{tabular}\end{table}')
(HERE/'numeric_table.tex').write_text('\n'.join(table)+'\n')

forcing=[r'\begin{table}[htbp]\centering\small',r'\caption{같은 $J_F$와 유한 온도 goal을 사용하는 직접 forcing과 feedback의 온도 응답.}\label{tab:forcing}',r'\begin{tabular}{lll}\toprule',r'매개변수 & 직접 forcing [K] & state/opacity feedback [K]\\\midrule']
for p in ['lambda','b']:
    v=f['responses'][p]
    forcing.append(('$\\lambda$' if p=='lambda' else '$b$')+' & '+interval(v['explicit_DeltaT_theta_K'])+' & '+interval(v['feedback_DeltaT_theta_K'])+r'\\')
forcing.append(r'\bottomrule\end{tabular}\end{table}')
(HERE/'forcing_table.tex').write_text('\n'.join(forcing)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(9.2,3.2),layout='constrained')
x=np.linspace(0,1,200)
colors=['#284C8C','#B26820']
for ax,p,scale,unit,color in zip(axes,['lambda','b'],[1e9,1e6],['nK',r'$\mu$K'],colors):
    lo,hi=map(float,a['responses'][p]['DeltaT_theta_K']['outward_decimal'])
    ax.fill_between(x,lo*x*scale,hi*x*scale,color=color,alpha=.24)
    ax.plot(x,lo*x*scale,color=color,lw=1.4)
    ax.plot(x,hi*x*scale,color=color,lw=1.4)
    ax.axhline(0,color='#5D6873',lw=.7)
    ax.set(xlim=(0,1),xlabel=(r'Increase in $\lambda$' if p=='lambda' else r'Increase in $b$'),ylabel='Finite change in '+r'$\Delta T$'+' ['+unit+']')
    ax.set_title('HH source response' if p=='lambda' else 'Photon birth response',loc='left',weight='bold',color=color)
    ax.grid(axis='y',color='#DDE1E6',lw=.6)
fig.savefig(HERE/'finite_parameter_envelopes.pdf',bbox_inches='tight')
fig.savefig(HERE/'finite_parameter_envelopes.png',dpi=200,bbox_inches='tight')
plt.close(fig)

manifest={'schema':'WU088_HH_PHYS17_REPORT_DATA_V1','inputs':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [APP,FORCE,NEUMANN]],'figure_meaning':'Fundamental-theorem-of-calculus outer envelopes from uniform first derivative intervals; each comparison fixes alpha and the other parameter; not independently solved physical trajectories.','outputs':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [HERE/'numeric_table.tex',HERE/'forcing_table.tex',HERE/'finite_parameter_envelopes.pdf',HERE/'finite_parameter_envelopes.png']]}
(HERE/'DATA_AND_FIGURE_PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tables':2,'figures':1,'source':manifest['inputs']},ensure_ascii=False))
