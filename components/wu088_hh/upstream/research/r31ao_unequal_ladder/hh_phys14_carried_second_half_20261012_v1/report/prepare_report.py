#!/usr/bin/env python3
"""Tables and exact-data plots for the PHYS14 LaTeX report, not a science rerun."""
import argparse
import json
import pathlib
import shutil
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fontTools import subset

R = pathlib.Path(__file__).resolve().parent
d = json.loads((R.parent/'results/advance01/ADVANCE_RESULTS.json').read_text())

def qpair(x):
    return [Q(*map(int, x['exact'][k])) for k in ('lo','hi')]

def digits(x, exponent=0, places=6):
    ret=[]
    for v, rnd in zip(qpair(x), (ROUND_FLOOR, ROUND_CEILING)):
        v *= Q(10)**(-exponent)
        with localcontext() as c:
            c.prec=90
            z=Decimal(v.numerator)/Decimal(v.denominator)
            z=z.quantize(Decimal(1).scaleb(-places),rounding=rnd)
            ret.append(format(z, 'f'))
    return ret

def texpair(x, exponent=0, places=6, suffix=True):
    a,b=digits(x,exponent,places)
    return r'$['+a+', '+b+']'+(r'\,10^{'+str(exponent)+'}' if exponent and suffix else '')+'$'

def write_table(name, caption, label, header, rows, spec):
    text=[r'\begin{table}[H]\centering\footnotesize',r'\caption{'+caption+'}',r'\label{'+label+'}',
          r'\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{@{}'+spec+r'@{}}\toprule',header+r'\\\midrule']
    text += [' & '.join(row)+r'\\' for row in rows]
    text += [r'\bottomrule\end{tabular}',r'\end{table}']
    (R/name).write_text('\n'.join(text)+'\n')

root=d['root_certificate']['root_image']
write_table('root_table.tex','기체 domain과 PHYS14 두 번째 half의 근 포함. 새 근은 원 $X$ 내부다.', 'tab:root',
            r'좌표 & 원 $X$의 간단 표기 & 새 $g_2$ 포함',
            [[n,x,texpair(v,0,10)] for n,x,v in zip([r'$x$',r'$y_1$',r'$y_2$',r'$w$'],
                                                  [r'$[0.90,0.93]$',r'$[0.29,0.31]$',r'$[0.59,0.61]$',r'$[13,14]$'],root)],'lll')
rows=[]
for key, label, exps in [('electron_per_H',r'$e$ [electrons/H]',(-10,-9,-17)),
                         ('electron_density_cm3',r'$n_e$ [cm$^{-3}$]',(-14,-13,-21)),
                         ('thermal_eV_per_H',r'$w$ [eV/H]',(-9,-10,-16)),
                         ('temperature_K',r'$T$ [K]',(-5,-4,-12))]:
    rows.append([label]+[texpair(d['readouts'][s][key],e,6) for s,e in zip(('U','V','W'),exps)])
write_table('response_tables.tex','새 두-half endpoint의 일차·혼합 응답. 각 칸의 거듭제곱과 행 단위를 함께 읽는다. 전체 parameter rectangle에서 균일하며 같은 finite 차이에도 적용된다.',
            'tab:response',r'관측량 & $U=\partial_\lambda$ & $V=\partial_b$ & $W=\partial_\lambda\partial_b$',rows,'llll')
rows=[]
for name,label,e,unit in [('inherited_gas','전달 기체',-6,r'$\mu\mathrm K$'),
                           ('direct_second_half_HH','두 번째 half 직접 HH',-6,r'$\mu\mathrm K$'),
                           ('inherited_photon_memory','전달 광자 기억',-12,r'$\mathrm{pK}$')]:
    rows.append([label,texpair(d['HH_U_decomposition'][name]['temperature_U_K'],e,8,False),unit])
write_table('memory_table.tex','같은 HH 첫 미분의 세 전달 기여. 각 항에 같은 implicit gas feedback을 적용했다.',
            'tab:memory','온도 응답 기여 & 포함 & 단위',rows,'lll')
rows=[]
for j in (10,16,17,24):
    c=next(x for x in d['remap_split_defect']['columns_j_ge_2'] if x['input_node']==j)
    rows.append([str(j),texpair(c['a_j'],0,9),texpair(c['L1'],0,9)])
write_table('remap_table.tex','원 비균일 node에서의 선택된 column 분할 크기. 두 moment는 정확히 0이다.',
            'tab:remap',r'입력 node $j$ & $\alpha_j$ & column $\ell^1$',rows,'lll')

(R/'figures').mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'pdf.fonttype':42})
fig,axs=plt.subplots(1,2,figsize=(8.1,3.5),gridspec_kw={'width_ratios':[1.65,1]},layout='constrained')
for y,s,label,col in [(1,'U','HH switch','#16486D'),(0,'V','Birth switch','#A15E21')]:
    lo,hi=[float(q*10**6) for q in qpair(d['readouts'][s]['temperature_K'])]
    axs[0].plot([lo,hi],[y,y],lw=7,color=col,solid_capstyle='butt')
    axs[0].scatter([lo,hi],[y,y],marker='|',s=100,color=col)
axs[0].axvline(0,color='0.55',lw=.8)
axs[0].set(yticks=[0,1],yticklabels=['Birth switch','HH switch'],xlabel='Temperature response (microkelvin)',ylim=(-.6,1.6),xlim=(-245,10))
axs[0].set_title('Finite first response',loc='left')
for y,x,label,col in [(1,d['readouts']['W']['temperature_K'],'HH x birth','#187F9B'),
                       (0,d['HH_U_decomposition']['inherited_photon_memory']['temperature_U_K'],'Photon memory','#70469A')]:
    lo,hi=[float(q*10**12) for q in qpair(x)]
    axs[1].plot([lo,hi],[y,y],lw=7,color=col,solid_capstyle='butt')
    axs[1].scatter([lo,hi],[y,y],marker='|',s=100,color=col)
axs[1].axvline(0,color='0.55',lw=.8)
axs[1].set(yticks=[0,1],yticklabels=['Photon memory','HH x birth'],xlabel='Temperature response (picokelvin)',ylim=(-.6,1.6),xlim=(-2,4))
axs[1].set_title('Mixed and memory response',loc='left')
for ax in axs:
    ax.spines[['top','right','left']].set_visible(False)
    ax.grid(axis='x',alpha=.18)
    ax.tick_params(axis='y',length=0)
fig.savefig(R/'figures/temperature_response.pdf')
fig.savefig(R/'figures/temperature_response.png',dpi=180)
plt.close(fig)

cols=d['remap_split_defect']['columns_j_ge_2']
c=next(x for x in cols if x['input_node']==16)
fig,axs=plt.subplots(1,2,figsize=(8.1,3.65),layout='constrained')
values=[sum(map(float,qpair(x)))/2 for x in c['coefficients']]
axs[0].bar(c['affected_nodes'],values,width=.58,color=['#187F9B','#B96B2F','#187F9B'])
axs[0].axhline(0,color='0.45',lw=.8)
axs[0].set(xticks=c['affected_nodes'],xlabel='Output node',ylabel='Signed photons per input photon',ylim=(-.45,.26))
axs[0].set_title('Input node 16: exact split stencil',loc='left')
axs[1].plot([x['input_node'] for x in cols],[sum(map(float,qpair(x['L1'])))/2 for x in cols],'-o',color='#16486D',ms=3,lw=1.1)
axs[1].set(xlabel='Input energy node',ylabel='Column L1 difference',ylim=(-.025,.85),xlim=(1,33))
axs[1].set_title('Original nonuniform grid',loc='left')
axs[1].axvspan(9.5,16.5,color='#187F9B',alpha=.08)
for ax in axs:
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.15)
fig.savefig(R/'figures/remap_split.pdf')
fig.savefig(R/'figures/remap_split.png',dpi=180)
plt.close(fig)

parser=argparse.ArgumentParser();parser.add_argument('--font-source',required=True);args=parser.parse_args()
font_source=pathlib.Path(args.font_source)
(R/'fonts').mkdir(exist_ok=True)
text=''.join(f.read_text() for f in R.glob('*.tex'))+''.join(chr(x) for x in range(32,256))+''.join(chr(x) for x in range(0x2000,0x2070))+'그림표원문근거목차독립검토조건부승격판정완료'
for name in ('NotoSerifCJKkr-Regular.otf','NotoSerifCJKkr-Bold.otf'):
    opt=subset.Options();opt.name_IDs=['*'];opt.name_legacy=True;opt.name_languages=['*']
    font=subset.load_font(str(font_source/name),opt)
    s=subset.Subsetter(options=opt);s.populate(text=text);s.subset(font)
    subset.save_font(font,str(R/'fonts'/name),opt)
for f in font_source.iterdir():
    if f.suffix.lower() in ('.txt','.md'):shutil.copy2(f,R/'fonts'/f.name)
print('Prepared four exact-endpoint tables, two data figures, and subset fonts.')
