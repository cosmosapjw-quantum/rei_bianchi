#!/usr/bin/env python3
"""Scientific figures from the generated source-qualified CSV products."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
YEAR=31557600.


def main():
    r=HERE/'results';out=HERE/'figures';out.mkdir(exist_ok=True)
    a=pd.read_csv(r/'abundances.csv.gz');z=pd.read_csv(r/'comparison_zbar.csv.gz')
    t=pd.read_csv(r/'comparison_time.csv.gz');m=pd.read_csv(r/'milestones.csv')
    tau=pd.read_csv(r/'thomson_segment.csv.gz');clock=pd.read_csv(r/'clock_check.csv')
    ref=a[a['case']=='ZERO']
    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':11,
        'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','savefig.facecolor':'white'})
    species=[('Y_HI','H I','#244a73'),('Y_HII','H II','#d46a28'),
             ('Y_HeI','He I','#6d538c'),('Y_HeII','He II','#348777'),
             ('Y_HeIII','He III','#b74457'),('Y_e','electron','#222222')]
    cases=[('SHEAR_HALF_PLUS',r'$q=+0.005$','#2b7793','-'),
           ('SHEAR_HALF_MINUS',r'$q=-0.005$','#df8b36','--'),
           ('SHEAR_MINUS',r'$q=-0.01$','#923f69','-')]
    fig,axs=plt.subplots(2,2,figsize=(12,9))
    for field,label,color in species:
        val=ref[field].to_numpy();good=val>0
        axs[0,0].plot(ref.time_s[good]/YEAR/1e6,val[good],label=label,color=color,lw=1.8)
        axs[0,1].plot(ref.temperature_K[good],val[good],color=color,lw=1.6)
    axs[0,0].set(xlabel='Elapsed proper time since mean z = 20 [Myr]',
        ylabel=r'$Y_i=n_i/(n_H+4n_{He})$',yscale='log',ylim=(1e-12,1.3),
        title='A   Complete FLRW abundance trajectory')
    axs[0,0].legend(ncol=3,frameon=False,fontsize=9,loc='lower right')
    axs[0,1].set(xlabel='Gas temperature [K]',ylabel=r'$Y_i$',xscale='log',yscale='log',
        ylim=(1e-12,1.3),title='B   Same trajectory in temperature space')
    for i,j in [(200,220),(760,800)]:
        axs[0,1].annotate('',xy=(ref.temperature_K.iloc[j],ref.Y_HII.iloc[j]),
            xytext=(ref.temperature_K.iloc[i],ref.Y_HII.iloc[i]),
            arrowprops={'arrowstyle':'->','color':'#d46a28','lw':1.7})
    axs[0,1].text(.03,.05,'Time ordered; zeros are masked only for log plotting.',
        transform=axs[0,1].transAxes,fontsize=8,color='#4d4d4d')
    for case,label,color,style in cases:
        f=z[z['case']==case]
        axs[1,0].plot(f.zbar,1e6*f.x_HII_delta_at_fixed_a,label=label,color=color,ls=style,lw=1.8)
    axs[1,0].set(xlabel='Mean redshift',ylabel=r'$10^6\,\Delta x_{HII}$',
        title='C   Matched mean redshift: negative response',xlim=(20,4))
    axs[1,0].legend(frameon=False,fontsize=9)
    f=t[t['case']=='SHEAR_MINUS'];x=f.elapsed_time_s/YEAR/1e6
    for field,label,color,style in [
        ('x_HII_delta_at_fixed_t','Total at equal elapsed time','#923f69','-'),
        ('x_HII_clock_displacement','Reference clock displacement','#d08830','-'),
        ('x_HII_fixed_a_at_candidate_a','Fixed-scale contribution','#2b7793','--')]:
        axs[1,1].plot(x,1e6*f[field],label=label,color=color,ls=style,lw=1.8)
    axs[1,1].set(xlabel='Elapsed proper time [Myr]',ylabel=r'$10^6\,\Delta x_{HII}$',
        title=r'D   Matched elapsed time, $q=-0.01$: decomposition')
    axs[1,1].legend(frameon=False,fontsize=8)
    for ax in axs.flat:ax.grid(alpha=.15)
    fig.suptitle('Original AXBI IGM model: abundance evolution and the comparison clock',fontsize=15,y=.99)
    fig.text(.5,.01,'Conditional saved model, mean z = 20 to 4. Four actual histories; +0.01 incomplete. Evolution refinement errors remain unknown.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.035,1,.96))
    for ext in ['png','svg']:fig.savefig(out/f'abundance_coordinate_response.{ext}',dpi=180)
    plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(12,8.6))
    levels=np.arange(3);width=.23
    for j,(case,label,color,style) in enumerate(cases):
        f=m[m['case']==case].sort_values('x_HII_level')
        axs[0,0].bar(levels+(j-1)*width,-f.delta_time_years_from_ZERO/1e3,width,
                     label=label,color=color,alpha=.9)
    axs[0,0].set(xticks=levels,xticklabels=['0.1','0.5','0.9'],xlabel=r'Local $x_{HII}$ milestone',
        ylabel='Earlier elapsed-time crossing [kyr]',title='A   Milestone shifts from native saved rows')
    axs[0,0].legend(frameon=False,fontsize=9)
    for case,label,color,style in cases:
        f=z[z['case']==case]
        axs[0,1].plot(f.zbar,(f.candidate_time_s-f.reference_time_s)/YEAR/1e3,
                       color=color,ls=style,label=label,lw=1.8)
    cc=clock[clock['case']=='SHEAR_MINUS']
    axs[0,1].plot(cc.zbar,cc.independent_offset_s/YEAR/1e3,'o',ms=4,mfc='white',mec='#923f69',label='Independent integral')
    axs[0,1].set(xlabel='Mean redshift',ylabel=r'$(t_q-t_0)$ at fixed scale [kyr]',
        title='B   Clock offset: saved history and background integral',xlim=(20,4))
    axs[0,1].legend(frameon=False,fontsize=8)
    for field,label,color in [('x_HII',r'$x_{HII}$','#d46a28'),('x_HeII',r'$x_{HeII}$','#348777'),
                             ('x_HeIII',r'$x_{HeIII}$','#b74457')]:
        f=z[z['case']=='SHEAR_MINUS']
        axs[1,0].plot(f.zbar,f[field+'_delta_at_fixed_a']*1e6,label=label,color=color,lw=1.8)
    axs[1,0].set(xlabel='Mean redshift',ylabel=r'$10^6\,\Delta x_i$',xlim=(20,4),
        title=r'C   Hydrogen and helium at matched scale, $q=-0.01$')
    axs[1,0].legend(frameon=False)
    for case,label,color,style in [('ZERO','FLRW','#222222','-')]+cases:
        f=tau[tau['case']==case]
        axs[1,1].plot(f.zbar,f.tau_to_conditional_z4_receiver,color=color,ls=style,label=label,lw=1.5)
    axs[1,1].set(xlabel='Mean redshift of emission',ylabel=r'$\tau(t,t_{\bar z=4})$',xlim=(20,4),
        title='D   REC collision law on actual proper electron histories')
    axs[1,1].text(.04,.83,'Curves overlap at this scale.\nUnknown observer tail is not set to zero.',transform=axs[1,1].transAxes,fontsize=9)
    for ax in axs.flat:ax.grid(alpha=.15)
    fig.suptitle('Original high-z IGM: milestone, clock, species and segment-electron results',fontsize=15,y=.99)
    fig.text(.5,.01,'Shifts are conditional model outputs, not a converged detection. Native milestone brackets are wider than some paired shifts.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.035,1,.96))
    for ext in ['png','svg']:fig.savefig(out/f'milestones_clock_electrons.{ext}',dpi=180)
    plt.close(fig)
    (out/'FIGURE_SCOPE.json').write_text(json.dumps({'source':'../results/*.csv[.gz]',
        'temperature_trajectory_sorted_by_temperature':False,'source_state_clipped':False,
        'log_plot_exact_zero_policy':'mask for display only',
        'all_four_histories_in_tables':True,'upper_abundance_panels':'FLRW; paired responses shown separately',
        'evolution_uncertainty':'UNKNOWN_AX11'},indent=2)+'\n')
    print('Rendered two figures in PNG and SVG from actual generated data.')


if __name__=='__main__':main()
