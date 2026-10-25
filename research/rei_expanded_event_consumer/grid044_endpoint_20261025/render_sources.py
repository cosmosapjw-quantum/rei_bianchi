"""Render only saved endpoint outputs; no scientific provider calls."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent

def render(result,contributions):
    folder=ROOT/'figures';folder.mkdir(exist_ok=True)
    columns=['event_id','source','target_abundance_per_ref','event_rate_per_ref_s','event_rate_m3_s',
             'radiation_loss_eV_per_ref_s','binding_gain_eV_per_ref_s','primary_gain_eV_per_ref_s']
    with (folder/'source_contributions.csv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=columns);writer.writeheader()
        for row in contributions:
            writer.writerow({**{k:row[k] for k in columns[:5]},**dict(zip(columns[5:],row['energy_eV_per_ref_s']))})
    rates=np.asarray([row['event_rate_per_ref_s'] for row in contributions]).reshape(13,2)
    labels=[contributions[2*i]['lower']+'→'+contributions[2*i]['upper'] for i in range(13)]
    powers=np.asarray([row['energy_eV_per_ref_s'] for row in contributions]).reshape(13,2,3).sum(axis=0)
    plt.rcParams.update({'font.size':10,'axes.spines.right':False,'axes.spines.top':False})
    fig,axes=plt.subplots(3,1,figsize=(12,13),gridspec_kw={'height_ratios':[1.6,1.0,1.0]},constrained_layout=True)
    colors=['#2b6a99','#d17828'];pos=np.arange(13);width=.36
    positive=rates[rates>0];minimum=float(positive.min())
    for si,name in enumerate(['stellar','external IGM']):
        axes[0].bar(pos+(si-.5)*width,rates[:,si],width,label=name,color=colors[si])
    axes[0].set_yscale('log');axes[0].set_ylim(minimum*.2,float(rates.max())*15)
    axes[0].set_xticks(pos,labels,rotation=45,ha='right');axes[0].set_ylabel('events per reference nucleus per proper s')
    axes[0].set_title('Actual GRID044 target at z = 2 with independently prescribed continua')
    axes[0].legend(ncol=2)
    for i,row in enumerate(rates):
        if np.all(row==0):axes[0].text(i,minimum*.35,'exact 0',ha='center',rotation=90,color='#555555')
    power_scale=float(np.max(np.abs(powers)))
    for si,name in enumerate(['stellar','external IGM']):
        axes[1].bar(np.arange(3)+(si-.5)*width,powers[si]/power_scale,width,color=colors[si],label=name)
    axes[1].axhline(0,color='#444444',lw=.8)
    axes[1].set_xticks(np.arange(3),['radiation loss (signed)','binding gain','primary electron kinetic gain'])
    axes[1].set_ylabel(f'sector source / {power_scale:.3e} eV ref⁻¹ s⁻¹')
    axes[1].set_title('Collision energy transfer; primary kinetic energy is not thermal heating')
    m=result['metrics'];n=result['normalization_controls']
    values=[m['REC_Jacobian_complex_step_row_scaled'],n['changed_reference_directional_row_scaled'],
            n['fixed_comoving_a_directional_row_scaled'],m['energy_component_row_scaled'],
            n['omitted_quotient_term_mutation_max_abs']]
    names=['REC J / complex step','varying reference derivative','comoving a derivative','energy balance',
           'quotient omitted\nabsolute mutation error']
    ax=axes[2]
    for i,value in enumerate(values):
        if value>0:ax.scatter(i,value,s=70,color='#b93636' if i==4 else '#2b6a99')
        else:ax.text(i,1e-18,'exact 0',ha='center')
    ax.set_yscale('log');ax.set_ylim(3e-19,1);ax.set_xticks(range(5),names,rotation=18,ha='right')
    ax.axhline(3e-12,lw=1,ls='--',color='#555555',label='derivative / energy tolerance')
    ax.set_ylabel('row-scaled residual; mutation uses absolute units')
    ax.set_title('Changed binding checks and a manufactured normalization mutation');ax.legend(loc='center left')
    fig.suptitle('Instantaneous photo-only source operator • 13 events × 2 source components\nSaved neutron and tritium zeros retained • no new trajectory, stopping or geometry feedback',fontsize=13)
    fig.savefig(folder/'GRID044_ACTUAL_ENDPOINT_SOURCES.png',dpi=150)
    fig.savefig(folder/'GRID044_ACTUAL_ENDPOINT_SOURCES.svg')
    plt.close(fig)
