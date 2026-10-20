#!/usr/bin/env python3
"""Generate a standard scientific PNG/SVG from the completed R1 comparisons.

This script performs no physics integration and changes no admission. Points
show measured absolute relative errors against one independent reference.
"""
from __future__ import annotations
import argparse
import datetime
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from independent_birth_reference import sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--comparison',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    data=json.loads(args.comparison.read_text())
    runs={r['label']:r for r in data['runs']}
    names=['fitted_r4_m4_o8_e16','fitted_r8_m4_o8_e16','gauss_r1_d8_m4_o8_e16','gauss_r1_d16_m4_o8_e16']
    for name in [*names,'gauss_r1_d8_m8_o8_e16']:
        if name not in runs:raise ValueError('completed original-spectrum case required: '+name)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.labelsize':11,
        'axes.titlesize':12,'legend.fontsize':9,'svg.fonttype':'none','savefig.facecolor':'white'})
    fig,(ax,work_ax)=plt.subplots(1,2,figsize=(11.8,5.1),gridspec_kw={'width_ratios':[1.6,1]})
    fig.subplots_adjust(left=.083,right=.983,bottom=.21,top=.80,wspace=.32)
    x=np.arange(4,dtype=float)
    quantities=[('survivor_com3','Survivor count','#0072B2','o'),
                ('age_sum_com_s','Raw age moment 1','#D55E00','s'),
                ('age2_sum_com_s2','Raw age moment 2','#009E73','^')]
    plotted=[]
    for shift,(key,label,color,marker) in zip((-.19,0.,.19),quantities):
        values=np.array([abs(runs[n]['continuous_comparison'][key]['relative']) for n in names])
        if np.any(values<=0):raise ValueError('log plot requires nonzero measured errors; do not fabricate a floor')
        ax.plot(x+shift,values,linestyle='none',marker=marker,color=color,markersize=7.5,label=label)
        plotted.extend({'case':n,'quantity':key,'absolute_relative_error':float(v)} for n,v in zip(names,values))
    ax.axhline(1e-8,color='#0072B2',lw=1,ls='--',alpha=.85)
    ax.axhline(1e-7,color='#777777',lw=1,ls=':',alpha=.95)
    ax.text(3.55,1e-8,'count target',color='#0072B2',fontsize=8.5,ha='right',va='top')
    ax.text(3.55,1e-7,'age targets',color='#555555',fontsize=8.5,ha='right',va='bottom')
    ax.set_xticks(x,['Fitted r4','Fitted r8','Gauss 8','Gauss 16'])
    ax.set_yscale('log');ax.set_ylim(5e-15,5e-4);ax.set_xlim(-.55,3.65)
    ax.set_ylabel('Absolute relative error')
    ax.set_title('(a) Count and birth-age moments',loc='left',pad=14)
    ax.grid(axis='y',which='major',color='#E4E7EB',lw=.7);ax.set_axisbelow(True)
    ax.legend(loc='lower left',frameon=True,framealpha=.96,edgecolor='#D3D7DD')
    work_names=['gauss_r1_d8_m4_o8_e16','gauss_r1_d8_m8_o8_e16']
    wx=np.arange(2,dtype=float)
    for shift,key,label,color,marker in ((-.12,'work_independent_j','Direct integral','#0072B2','o'),
                                        (.12,'work_ledger_j','Energy subtraction','#D55E00','s')):
        values=np.array([abs(runs[n]['continuous_comparison'][key]['relative']) for n in work_names])
        work_ax.plot(wx+shift,values,linestyle='none',marker=marker,color=color,markersize=8,label=label)
        plotted.extend({'case':n,'quantity':key,'absolute_relative_error':float(v)} for n,v in zip(work_names,values))
    work_ax.set_xticks(wx,['4 path slabs','8 path slabs'])
    work_ax.set_yscale('log');work_ax.set_ylim(1e-12,3e-3);work_ax.set_xlim(-.55,1.6)
    work_ax.set_ylabel(r'Error divided by $|W_{\rm ref}|$')
    work_ax.set_title('(b) Photon geometry work',loc='left',pad=14)
    work_ax.grid(axis='y',which='major',color='#E4E7EB',lw=.7);work_ax.set_axisbelow(True)
    work_ax.legend(loc='lower left',frameon=True,framealpha=.96,edgecolor='#D3D7DD')
    for axis in (ax,work_ax):
        axis.spines[['top','right']].set_visible(False)
        axis.tick_params(axis='both',which='major',length=4,color='#6B7280')
    source=runs[work_names[0]]['continuous_comparison']['source_j']['reference']
    wref=runs[work_names[0]]['continuous_comparison']['work_independent_j']['reference']
    condition=abs(source/wref)
    fig.text(.083,.94,'BR06 recovery R1: one frozen recorded-gas operator',fontsize=15,weight='bold')
    fig.text(.083,.88,'384 original source labels; variable BASS geometry; independent continuous-birth comparison',fontsize=10.8,color='#4B5563')
    fig.text(.083,.085,'Left: fixed path controls (4 slabs, opacity 8, event 16).  Right: Gauss 8 births; only path slabs change.',fontsize=9.2,color='#4B5563')
    fig.text(.083,.042,f'Work normalization: source energy / |W reference| = {condition:.3g}. Small ledger residuals do not establish work accuracy.',fontsize=9.2,color='#4B5563')
    png=args.output/'BR06_BIRTH_AGE_AND_WORK_R1.png';svg=args.output/'BR06_BIRTH_AGE_AND_WORK_R1.svg'
    description='Fresh R1 finite-error comparison. Targets: count1e-8, raw age1/2=1e-7. This is not a convergence proof for a nonlinear history or an interval whole-operator bound.'
    fig.savefig(png,dpi=190,metadata={'Description':description,'SourceComparisonSHA256':sha(args.comparison)})
    fig.savefig(svg,metadata={'Title':'BR06 birth age and geometry work errors','Description':description})
    plt.close(fig)
    caption=('고정된 기록 기체와 원 384 source label에서 출생 적분만 바꾼 오차 비교이다. '
        '왼쪽 점은 생존수와 생존 광자의 raw age 1·2차 moment를 연속 출생 기준해와 비교한 절대 상대오차이며, '
        '점선은 각각 1e-8과 1e-7의 bounded 진단 목표이다. 오른쪽은 같은 Gauss8 출생표에서 path slab만4→8로 바꾸고 '
        '광자 geometry work를 직접 적분한 값과 에너지 차감으로 얻은 값을 각각 |W_ref|로 정규화했다. '
        'source energy가 |W_ref|보다 약6.42e5배 커서, source-energy-normalized ledger 잔차와 W 자체의 상대 정확도를 구분한다. '
        '1e-13 부근의 일치는 독립 기준해의 부동소수점·차수 변경 규모에서 읽어야 하며 엄밀한 구간 오차한계가 아니다.')
    receipt={'version':'BR06_THEORY_RECOVERY_R1','status':'GENERATED_FROM_FRESH_COMPLETED_MATRIX','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'script_sha256':sha(__file__),'source_comparison':str(args.comparison),'source_comparison_sha256':sha(args.comparison),
       'matplotlib':matplotlib.__version__,'no_new_physics_execution':True,
       'targets':{'count_relative':1e-8,'raw_age_moments_relative':1e-7},'source_energy_over_abs_W':condition,
       'caption_ko':caption,'plotted_data':plotted,'artifacts':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in (png,svg)],
       'visual_review':'PENDING_ROOT_INSPECTION'}
    out=args.output/'FIGURE_RECEIPT_R1.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'png':str(png),'svg':str(svg),'receipt':str(out)}))


if __name__=='__main__':main()
