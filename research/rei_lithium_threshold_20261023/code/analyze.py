"""Saved comparisons and exactly three plots. No IVP."""
import time
CPU0,WALL0=time.process_time(),time.monotonic()
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from trace_model import *
import importlib.util
_case_spec=importlib.util.spec_from_file_location('angtherm02_case_table',BASE/'code/run_cases.py')
_case_module=importlib.util.module_from_spec(_case_spec);_case_spec.loader.exec_module(_case_module)
CASES=_case_module.CASES
R=BASE/'results';F=BASE/'figures'
def difference(a,b):
    if not np.array_equal(a['eta'],b['eta']):raise RuntimeError('TIME_MISMATCH')
    d=a['fractions']-b['fractions'];q,t=np.unravel_index(abs(d).argmax(),d.shape)
    return {'max_absolute_fraction_difference':float(abs(d).max()),'eta_at_max':float(a['eta'][t]),'charge_state_at_max':['LiI','LiII','LiIII','LiIV'][q],'per_charge_max_abs':abs(d).max(axis=1).tolist(),'endpoint_signed_fraction_difference':d[:,-1].tolist()}
def main():
    F.mkdir(exist_ok=True);hs={i:np.load(R/(s['name']+'.npz'),allow_pickle=False) for i,s in CASES.items()};metas={i:json.loads((R/(s['name']+'.json')).read_text()) for i,s in CASES.items()}
    if not all(m['status']=='COMPLETED' for m in metas.values()):raise RuntimeError('CASE_INCOMPLETE')
    out={'scope':'conditional trace lithium, prescribed thermal/electron bath','native_fraction_normalization':'per total Li nuclei','comparisons':{},'gates':{},'admission':'controller and independent reviewer decision pending'}
    pairs=[(6,7,'split16_minus_split32'),(5,6,'split8_minus_split16'),(4,1,'fixed16_thin_minus_attenuated'),(6,8,'primary_minus_secondary_split16'),(2,7,'fixed4_minus_split32'),(3,7,'fixed8_minus_split32'),(4,7,'fixed16_minus_split32')]
    for a,b,key in pairs:out['comparisons'][key]=difference(hs[a],hs[b])
    with np.load(DONOR/'results/grid044_M16_tight.npz',allow_pickle=False) as old:
        t=old['eta'][11:];ind=np.searchsorted(hs[1]['eta'],t)
        if not np.array_equal(hs[1]['eta'][ind],t):raise RuntimeError('SAVED_TIME_NOT_EXACT')
        for i,key in [(1,'fixed16_attenuated_minus_saved_M16'),(6,'split16_minus_saved_M16')]:
            d=hs[i]['fractions'][:,ind]-old['fractions'][5:9,11:];q,j=np.unravel_index(abs(d).argmax(),d.shape)
            out['comparisons'][key]={'matching_report_count':len(t),'max_absolute_fraction_difference':float(abs(d).max()),'per_charge_max_abs':abs(d).max(axis=1).tolist(),'eta_at_max':float(t[j]),'charge_state_at_max':['LiI','LiII','LiIII','LiIV'][q]}
    bath=Bath();bs=[]
    for i in [9,10]:
        j=int(np.flatnonzero(hs[i]['eta']==bath.star)[0])
        bs.append({'case':i,'B_last':float(hs[i]['B'][-1]),'B_star':float(hs[i]['B'][j]),'F_star':float(hs[i]['F'][j]),'initial_LiI':float(bath.initial[0]),'initial_tau_max':float(bath.tau.max()),'seeded_LiI_below_F':bool(bath.initial[0]<=hs[i]['F'][j]),'saved_tau_below_Bstar':bool(bath.tau.max()<=hs[i]['B'][j]),'B_min_accepted_increment':float(np.diff(hs[i]['accepted_Y'][1]).min())})
    bd=abs(bs[0]['B_last']-bs[1]['B_last']);bm=max(x['B_last'] for x in bs);cmp=out['comparisons']
    out['attenuation_bootstrap']={'delta':DELTA,'declared_numerical_margin':1e-10,'last_B_difference':bd,'max_last_B_plus_margin':bm+1e-10,'cases':bs,'analytic_uniform_component_implication_if_bootstrap_holds':float(np.expm1(DELTA)),'numerical_component_allowance':2e-9,'interpretation':'same bath and seeded state; initial optical profile bounded by Bstar; numerical robustness margin is not interval arithmetic'}
    out['gates']={'all_case_invariants':all(m['validation']['all_pass'] for m in metas.values()),'same_fixed_M16_reconstruction':cmp['fixed16_attenuated_minus_saved_M16']['max_absolute_fraction_difference']<=2e-7,'selected_split16_vs_split32':cmp['split16_minus_split32']['max_absolute_fraction_difference']<=2e-8,'fixed16_attenuation_consistent':cmp['fixed16_thin_minus_attenuated']['max_absolute_fraction_difference']<=np.expm1(DELTA)+2e-9,'bath_transfer_at_2e-7':cmp['primary_minus_secondary_split16']['max_absolute_fraction_difference']<=2e-7,'bootstrap_below_delta_with_margin':bm+1e-10<DELTA,'bootstrap_standard_tight_difference':bd<1e-11,'seeded_LiI_below_F':all(x['seeded_LiI_below_F'] for x in bs),'saved_initial_optical_depths_below_Bstar':all(x['saved_tau_below_Bstar'] for x in bs),'bootstrap_nonnegative_F_B':all(metas[i]['validation']['all_pass'] for i in [9,10])}
    out['gates']={k:bool(v) for k,v in out['gates'].items()};out['all_numerical_gates_pass']=all(out['gates'].values())
    out['all_case_validation_maxima']={k:max(m['validation'].get('maxima',{}).get(k,0) for m in metas.values()) for k in ['mass_residual','charge_residual','event_energy_residual_eV_per_Li']}
    rate=Rates();ts=hs[6]['eta'];co={str(m):np.array([rate.coefficients(float(t),'split',m)[:2] for t in ts]).T for m in [8,16,32]};fixed={str(m):np.array([rate.coefficients(float(t),'fixed',m)[:2] for t in ts]).T for m in [4,8,16]};width=np.array([np.diff(support(float(t),rate.bg.fields(float(t))[2]))[0] for t in ts])
    np.savez_compressed(R/'rate_curves.npz',eta=ts,support_width=width,**{'split'+k:v for k,v in co.items()},**{'fixed'+k:v for k,v in fixed.items()})
    plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.22})
    colors={2:'#8c564b',3:'#ff7f0e',4:'#d62728',5:'#9467bd',6:'#1f77b4',7:'#2ca02c',8:'#7f7f7f',1:'#e377c2'}
    fig,ax=plt.subplots(2,2,figsize=(12.2,8.2),layout='constrained')
    for m in ['4','8','16']:ax[0,0].plot(ts,fixed[m][0],label='fixed GL'+m)
    ax[0,0].plot(ts,co['32'][0],color='black',label='support split GL32');ax[0,0].set(ylabel=r'Lambda per unit eta',title='Li I photoionization coefficient');ax[0,0].legend(fontsize=8)
    ax[0,1].plot(ts,width,color='black');ax[0,1].set(ylabel='Active width in covariant mu0',title='Physical integration measure')
    for i in [2,3,4,6,7]:
        ax[1,0].plot(ts,hs[i]['fractions'][0],label=CASES[i]['name'],color=colors[i]);ax[1,1].plot(ts,hs[i]['fractions'][1],color=colors[i])
    ax[1,0].set(ylabel='Li I fraction per Li nucleus',title='Neutral lithium threshold response');ax[1,1].set(ylabel='Li II fraction per Li nucleus',title='Singly ionized lithium');ax[1,0].legend(fontsize=8)
    for a in ax.flat:
        a.set(xlim=(.44,.78),xlabel='eta = ln(a/a0)')
        for root in rate.endpoint_roots:a.axvline(root,color='#777777',ls=':',lw=.8)
    fig.suptitle('Conditional trace lithium — prescribed primary thermal/electron bath');fig.savefig(F/'01_rates_support_li.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(2,2,figsize=(12.2,8.2),layout='constrained')
    for q,a in enumerate(ax.flat):
        for i in [2,3,4,5,6,8]:a.plot(ts,hs[i]['fractions'][q]-hs[7]['fractions'][q],label=CASES[i]['name'],color=colors[i],lw=1.1)
        a.set(xlim=(.44,.80),xlabel='eta = ln(a/a0)',ylabel='Signed native Li-fraction difference',title=['Li I','Li II','Li III','Li IV'][q]);a.ticklabel_format(axis='y',style='sci',scilimits=(0,0));a.axhline(0,color='black',lw=.6)
    ax[0,0].legend(fontsize=8);fig.suptitle('Errors relative to split GL32 — conditional prescribed bath');fig.savefig(F/'02_signed_fraction_errors.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(2,2,figsize=(12.2,8.2),layout='constrained')
    for i in [9,10]:ax[0,0].plot(hs[i]['eta'],hs[i]['F'],label=CASES[i]['name']);ax[0,1].plot(hs[i]['eta'],hs[i]['B'],label=CASES[i]['name'])
    ax[0,0].scatter([bath.star],[bath.initial[0]],color='black',s=25,label='saved seeded Li I');ax[0,0].set(ylabel='Upper Li I fraction F',title='Global comparison');ax[0,0].legend(fontsize=8)
    ax[0,1].axhline(DELTA,color='black',ls='--',label='delta = 2e-8');ax[0,1].set(ylabel='Optical-depth envelope B',title='Numerical bootstrap');ax[0,1].legend(fontsize=8)
    for i in [1,6,7]:
        ax[1,0].plot(ts,hs[i]['event_energy_residual_eV_per_Li'],label=CASES[i]['name']);ax[1,1].plot(ts,hs[i]['charge_residual'],label=CASES[i]['name']+' charge');ax[1,1].plot(ts,hs[i]['mass_residual'],ls=':',label=CASES[i]['name']+' mass')
    ax[1,0].set(ylabel='Event energy residual [eV per Li]',title='Prescribed-bath transfer identity');ax[1,1].set(ylabel='Residual per Li nucleus',title='Charge and fraction sum')
    for a in ax.flat:a.set_xlabel('eta = ln(a/a0)');a.ticklabel_format(axis='y',style='sci',scilimits=(0,0));a.legend(fontsize=7)
    fig.suptitle('Conditional trace model — opacity and event ledgers');fig.savefig(F/'03_bootstrap_ledgers.png',dpi=170);plt.close(fig)
    out['execution']={'CPU_s':time.process_time()-CPU0,'wall_s':time.monotonic()-WALL0,'new_IVPs':0};(R/'comparisons.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
    return 0 if out['all_numerical_gates_pass'] else 2
if __name__=='__main__':raise SystemExit(main())

