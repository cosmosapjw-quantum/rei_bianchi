"""Observed agreement, refinement and five figures; no scientific IVPs."""
from pathlib import Path
import json
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_cases import BASE, CASES
from angular_model import ATOM, NN, CT, VGRAD
from species_saved_analysis import calculate

R=BASE/'results'
F=BASE/'figures'
LABEL='Prescribed C21O background; conditional trace\nCounts and energies per Href'


def load(i):
    name=CASES[i]['name']
    return np.load(R/f'{name}.npz',allow_pickle=False),json.loads((R/f'{name}.json').read_text())


def comparison(a,b):
    result={}
    limits={'fractions':2e-7,'atomic_scaled':2e-7,'temperature_K':2e-6,'electron_per_Href':2e-7,
            'photon_per_Href':2e-8,'UV_energy':2e-6,'Q':2e-6,'U':2e-6,'Eesc':2e-6,
            'Wgas':2e-6,'Wmean':2e-6,'Wshear':2e-6,'tauT':2e-7}
    for k,limit in limits.items():
        difference=abs(a[k]-b[k])
        if k=='temperature_K':
            difference=difference/abs(b[k])
        maximum=float(np.max(difference))
        result[k]={'maximum':maximum,'limit':limit,'pass':maximum<=limit,
                   'metric':'relative to reference T' if k=='temperature_K' else 'absolute in declared units'}
    return {'all_pass':all(v['pass'] for v in result.values()),'observables':result}


def main():
    started=time.perf_counter()
    F.mkdir(exist_ok=True)
    histories={};meta={}
    for i in CASES:
        histories[i],meta[i]=load(i)
    h=histories[1];eta=h['eta']
    agreements={'nominal_vs_oracle':comparison(h,histories[4]),'nominal_vs_tight':comparison(h,histories[3])}
    refinement={}
    for key in ['temperature_K','electron_per_Href','photon_per_Href','UV_energy','Q','Wshear','tauT']:
        d48=float(np.max(abs(histories[3][key]-histories[8][key])))
        d816=float(np.max(abs(histories[8][key]-histories[9][key])))
        refinement[key]={'M4_M8_max_abs':d48,'M8_M16_max_abs':d816,
                         'log2_successive_difference_ratio':float(np.log2(d48/d816)) if d48>0 and d816>0 else None,
                         'interpretation':'Difference ratio only; no resolved order at numerical noise level' if key in ['temperature_K','electron_per_Href','tauT'] else 'Difference ratio only; asymptotic order not established'}
    summary={'status':'OBSERVED_RESULTS_PENDING_ASTRA_ADMISSION','agreements':agreements,
             'trajectory_checks':{CASES[i]['name']:meta[i]['validation'] for i in CASES},
             'angular_refinement':refinement,'finite_system_exact_equivalence':'tested only M4 full versus folded',
             'cost_interpretation':'One unpaired nominal/oracle observation; no robust speedup claim',
             'case_costs':[{k:meta[i][k] for k in ['name','state_size','child_case_cpu_s','child_case_wall_s',
                                                   'solver_wall_s','accepted_nodes_total','nfev_total','njev_total','nlu_total','rtol','atol']} for i in CASES]}
    summary['cost_comparison_tolerances']={'nominal_primary_rtol':2e-9,'direct_oracle_rtol':2e-10,
          'tight_M4_M8_M16_rtol':2e-11,'caveat':'Different native component atols and state/error norms; observed costs are not a fixed-tolerance or equal-error speedup'}
    summary['accepted_and_reporting_temperature_ranges_K']={}
    summary['same_background_directional_minus_mean']={}
    for key in ['temperature_K','electron_per_Href','UV_energy','Q','Wmean','Wshear','tauT']:
        difference=histories[3][key]-histories[10][key]
        summary['same_background_directional_minus_mean'][key]={
            'max_absolute_difference':float(np.max(abs(difference))),
            'endpoint_signed_difference':float(difference[-1]),
            'directional_endpoint':float(histories[3][key][-1]),'mean_endpoint':float(histories[10][key][-1])}
        if key=='temperature_K':
            summary['same_background_directional_minus_mean'][key]['max_relative_difference']=float(np.max(abs(difference)/histories[10][key]))
    summary['same_background_control_scope']='Same grid044 H/nHref, M4, default IC, rtol2e-11 and same native atols. sign0 counterfactual mean-redshift; not a physical FLRW solution.'
    summary['species_resolved']=calculate(histories)
    for i in CASES:
        d=histories[i];Y=d['accepted_Y'];natom=21 if i==4 else 9
        v=(ATOM.q*ATOM.scales)@Y[:21] if i==4 else VGRAD@Y[:9]
        temps=Y[natom+6*CASES[i]['M']*(8 if i==4 else 1)]/(CT*(NN+v))
        summary['accepted_and_reporting_temperature_ranges_K'][CASES[i]['name']]={
            'accepted_min':float(np.min(temps)),'accepted_max':float(np.max(temps)),
            'reporting_min':float(np.min(d['temperature_K'])),'reporting_max':float(np.max(d['temperature_K']))}
    plt.rcParams.update({'font.size':10,'axes.labelsize':10,'legend.fontsize':8.5,'figure.dpi':150,
                         'savefig.dpi':180,'axes.grid':True,'grid.alpha':.22})
    def save(fig,name):
        fig.savefig(F/name,bbox_inches='tight');plt.close(fig)
    colors={1:'C0',2:'C2',5:'C3',6:'C4',7:'C1'}
    labels={1:'grid044 default',2:'grid022 near FLRW',5:'grid044 reversed b',6:'grid044 zero UV',7:'grid044 ionized IC'}
    fig,ax=plt.subplots(4,1,figsize=(3.6,9),sharex=True,layout='constrained')
    for i in [1,2,5,6,7]:
        d=histories[i]
        ax[0].plot(eta,d['temperature_K'],color=colors[i],label=labels[i])
        ax[1].plot(eta,d['electron_per_Href'],color=colors[i])
        ax[2].plot(eta,d['photon_per_Href'],color=colors[i])
    ax[0].set(yscale='log',ylabel='Common temperature [K]')
    ax[1].set(ylabel='Electrons / Href')
    ax[2].set(ylabel='UV photons / Href')
    ax[3].plot(eta,(histories[3]['temperature_K']-histories[10]['temperature_K'])/histories[10]['temperature_K'],color='C0')
    ax[3].ticklabel_format(style='sci',axis='y',scilimits=(-2,2),useOffset=False,useMathText=True)
    ax[3].set(ylabel='Directional − mean: ΔT/T',xlabel=r'$\eta=\ln(a/a_i)$')
    ax[3].set_title('Same grid044 H/n; both tight, M4',fontsize=8.5)
    ax[0].legend(ncol=1,loc='lower center',bbox_to_anchor=(.5,1.03))
    fig.suptitle('Thermochemistry, M=4\n'+LABEL)
    save(fig,'01_evolution.png')
    fig,ax=plt.subplots(3,1,figsize=(3.6,7.8),sharex=True,layout='constrained')
    for i in [1,2,5]:
        d=histories[i]
        ax[0].plot(eta,d['Q'],label=labels[i],color=colors[i])
        ax[1].plot(eta,d['Wmean'],color=colors[i])
        ax[2].plot(eta,d['Wshear'],color=colors[i])
    for axis in ax:axis.axhline(0,color='k',lw=.6)
    ax[0].set(ylabel='Signed Q [eV / Href]')
    ax[1].set(ylabel='Mean work [eV / Href]')
    ax[2].set(ylabel='Shear work [eV / Href]',xlabel=r'$\eta$')
    ax[0].legend(loc='lower center',bbox_to_anchor=(.5,1.03))
    fig.suptitle('Signed stress and work, M=4\n'+LABEL)
    save(fig,'02_stress_work.png')
    fig,ax=plt.subplots(4,1,figsize=(3.6,8.8),sharex=True,layout='constrained')
    keys=['energy_residual','charge_residual','photon_residual','nucleus_residual']
    for axis,key in zip(ax.flat,keys):
        for i in [1,3,4,8,9]:
            d=histories[i]
            axis.plot(eta,d[key],label=f"M{meta[i]['M']} "+('oracle' if i==4 else 'nominal' if i==1 else 'tight'))
        axis.ticklabel_format(style='sci',axis='y',scilimits=(-2,2),useOffset=False,useMathText=True)
        axis.set_ylabel({'energy_residual':'Energy residual','charge_residual':'Charge residual',
                         'photon_residual':'Photon residual','nucleus_residual':'Nucleus residual'}[key]);axis.set_xlabel(r'$\eta$')
        axis.axhline(0,color='k',lw=.5)
    ax[0].legend(ncol=2,loc='lower center',bbox_to_anchor=(.5,1.15))
    fig.suptitle('grid044 signed conservation residuals\nFixed initial energy/count/element scales\nPrescribed background; conditional trace')
    save(fig,'03_conservation.png')
    fig,ax=plt.subplots(4,1,figsize=(3.6,8.8),sharex=True,layout='constrained')
    for axis,key in zip(ax.flat,['temperature_K','electron_per_Href','UV_energy','Q']):
        for j,lab in [(4,'M4 nominal − full oracle'),(3,'M4 nominal − tight')]:
            delta=h[key]-histories[j][key]
            if key=='temperature_K':delta=delta/histories[j][key]
            axis.plot(eta,delta,label=lab)
        axis.ticklabel_format(style='sci',axis='y',scilimits=(-2,2),useOffset=False,useMathText=True)
        axis.set_ylabel({'temperature_K':'ΔT / T','electron_per_Href':'Δelectrons / Href',
                         'UV_energy':'ΔUV energy [eV/Href]','Q':'ΔQ [eV/Href]'}[key])
        axis.set_xlabel(r'$\eta$')
    ax[0].legend(loc='lower center',bbox_to_anchor=(.5,1.15))
    fig.suptitle('grid044 finite-system agreement\n'+LABEL)
    save(fig,'04_agreement.png')
    fig,ax=plt.subplots(4,1,figsize=(3.6,8.8),sharex=True,layout='constrained')
    for axis,key in zip(ax.flat,['temperature_K','electron_per_Href','Q','Wshear']):
        for a,b,lab in [(3,8,'M4 − M8'),(8,9,'M8 − M16')]:
            axis.plot(eta,histories[a][key]-histories[b][key],label=lab)
        axis.ticklabel_format(style='sci',axis='y',scilimits=(-2,2),useOffset=False,useMathText=True)
        axis.set_ylabel({'temperature_K':'ΔT [K]','electron_per_Href':'Δelectrons / Href',
                         'Q':'ΔQ [eV/Href]','Wshear':'Δshear work [eV/Href]'}[key]);axis.set_xlabel(r'$\eta$')
    ax[0].legend(ncol=2,loc='lower center',bbox_to_anchor=(.5,1.15))
    fig.suptitle('grid044 angular refinement; all tight\nFinite quadrature differences\nConditional prescribed background')
    save(fig,'05_angular_refinement.png')
    fig,ax=plt.subplots(2,1,figsize=(3.6,6.4),layout='constrained')
    selected=[1,4,3,8,9]
    names=['M4\nnominal','M4\ndirect','M4\ntight','M8\ntight','M16\ntight']
    ax[0].bar(names,[meta[i]['state_size'] for i in selected],color=['C0','C1','C4','C2','C3'])
    ax[0].set_ylabel('State dimension');ax[0].tick_params(axis='x',rotation=0)
    ax[1].bar(names,[meta[i]['child_case_wall_s'] for i in selected],color=['C0','C1','C4','C2','C3'])
    ax[1].set_ylabel('Case wall with raw saves [s]');ax[1].tick_params(axis='x',rotation=0)
    agreement=agreements['nominal_vs_oracle']['observables']
    fig.suptitle('grid044 costs on prescribed background\n'+
                 'rtol: nominal 2e−9 / direct 2e−10\n'+
                 'tight 2e−11; native atols/norms differ\n'+
                 f"M4 ΔT/T={agreement['temperature_K']['maximum']:.2g}\nΔQ={agreement['Q']['maximum']:.2g} eV/Href")
    save(fig,'06_sizes_costs.png')
    summary['plotting_wall_s']=time.perf_counter()-started
    (R/'analysis_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'agreements':agreements,'angular_refinement':refinement,'plotting_wall_s':summary['plotting_wall_s']},indent=2))


if __name__=='__main__':
    main()
