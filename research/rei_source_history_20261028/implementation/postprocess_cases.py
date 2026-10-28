"""Future three-case validation and all17 population figure; not yet executed.

Reads only the prepared case files and immutable baseline. No IVP calls.
"""
import csv
import json
from pathlib import Path
import numpy as np
from history import UNIT,old,baseline

CASES=('OFF_base','ON_base','ON_refined')


def read_case(out,name):
    with np.load(out/(name+'.npz'),allow_pickle=False) as d:
        result={key:d[key].copy() for key in ('t','physical','baryon_residual','charge_residual','scales')}
    metadata=json.loads((out/(name+'.json')).read_text())
    t,p,s=result['t'],result['physical'],result['scales']
    if t.ndim!=1 or p.shape!=(23,len(t)) or s.shape!=(23,):
        raise ValueError(name+': incompatible saved case schema; expected physical23xN, scales23')
    if result['baryon_residual'].shape!=t.shape or result['charge_residual'].shape!=t.shape:
        raise ValueError(name+': ledger output shape mismatch')
    if not all(np.isfinite(value).all() for value in result.values()) or np.any(s<=0) or np.any(np.diff(t)<=0):
        raise ValueError(name+': nonfinite/unordered saved values or nonpositive scales')
    result['metadata']=metadata
    return result


def validate(cases,data):
    reference=cases['ON_refined'];t=reference['t']
    if any(not np.array_equal(cases[name]['t'],t) for name in CASES):
        raise ValueError('three cases do not share the exact prepared output times; no interpolation substituted')
    if t[0]!=0 or t[-1]!=data['t'][-1]:
        raise ValueError('pilot interval does not match the finite background interval')
    matched_epochs=bool(np.isin(data['t'],t).all())
    transient_samples=bool(np.any((t>0)&(t<data['t'][1])))
    # This is a stricter sufficient test than dividing by max(initial stock,
    # absolute boundary throughput). No absolute-throughput measurement exists
    # in the saved schema, and none is inferred from the net boundary ledger.
    denominator=float(data['y'][0].sum()+data['hidden'][0].sum())
    if denominator<=0:raise ValueError('nonpositive initial heavy-particle stock')
    threshold=1e-8*max(denominator,1e-30)
    reports={}
    for name,d in cases.items():
        minimum=float((d['physical'][:21]/d['scales'][:21,None]).min())
        bad_energy=int(np.count_nonzero((d['physical'][17:19]==0)&(d['physical'][19:21]!=0)))
        b=float(abs(d['baryon_residual']).max());q=float(abs(d['charge_residual']).max())
        checks={'solver_completed':d['metadata'].get('status')=='COMPLETED',
                'finite_saved_values':True,'scaled_nonnegativity':minimum>=-1e-9,
                'baryon_balance_strict_initial_stock':b<=threshold,
                'charge_balance_strict_initial_stock':q<=threshold,
                'zero_fast_stock_energy_consistent':bad_energy==0}
        reports[name]={'checks':checks,'accepted':all(checks.values()),'minimum_scaled_stock':minimum,
                      'max_baryon_residual':b,'max_charge_residual':q,
                      'zero_B_nonzero_U_samples':bad_energy}
    base,ref=cases['ON_base'],cases['ON_refined']
    if not np.array_equal(base['scales'],ref['scales']):
        raise ValueError('ON base/refined scales differ; no unapproved normalization substituted')
    differences=np.max(abs(base['physical'][:21]-ref['physical'][:21])/ref['scales'][:21,None],axis=1)
    per_isotope={}
    for family,indices in [('n',[0]),('H1',[1,2]),('D',[3,4]),('T',[5,6]),('He3',[7,8,9]),
                           ('He4',[10,11,12]),('Li7',[13,14,15,16])]:
        per_isotope[family]=float(differences[indices].max())
    refinement=all(value<=1e-5 for value in per_isotope.values())
    return {'status':'PASS_SCOPED_NUMERICAL_CHECKS' if refinement and matched_epochs and transient_samples and all(x['accepted'] for x in reports.values()) else 'HOLD',
            'scientific_admission':'PENDING_ROOT_ASTRA_DECISION','cases':reports,
            'refinement_pass':refinement,'per_isotope_normalized_max_difference':per_isotope,
            'fast_stock_energy_normalized_differences':dict(zip(('Bn','BT','Un','UT'),differences[17:21].tolist())),
            'balance_denominator_initial_particles_per_Href':denominator,'balance_absolute_threshold':threshold,
            'balance_test':'STRICT_SUFFICIENT_INITIAL_STOCK_BOUND',
            'absolute_boundary_throughput':'NOT_MEASURED; net ledger is not absolute throughput',
            'sample_times':len(t),'contains_all201_matched_epochs':matched_epochs,
            'contains_initial_transient_samples':transient_samples,
            'scope':'Illustrative prescribed-bath pilot; saved donor is reference, not exact OFF target'},differences


def write_tables(out,cases,data,differences):
    t=cases['ON_refined']['t'];hidden=np.array([np.interp(t,data['t'],data['hidden'][:,j]) for j in range(4)])
    with (out/'pilot17_populations.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['case','elapsed_proper_s','eta','z_mean',*['per_Href__'+x for x in old.LABELS],
                         'Bn_per_Href','BT_per_Href','Un_eV_per_Href','UT_eV_per_Href',
                         'hidden_Li6_baryons_per_Href','total_baryons_per_Href',
                         'open_baryon_residual','heavy_free_electron_residual'])
        for name,d in cases.items():
            eta=np.interp(t,data['t'],data['eta']);z=21*np.exp(-eta)-1
            p=d['physical'];baryon=old.A[:17]@p[:17]+p[17]+3*p[18]+6*hidden.sum(axis=0)
            for k in range(len(t)):
                writer.writerow([name,t[k],eta[k],z[k],*p[:21,k],6*hidden[:,k].sum(),baryon[k],d['baryon_residual'][k],d['charge_residual'][k]])
    with (out/'pilot17_refinement.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['state','maximum_normalized_base_refined_difference','criterion'])
        writer.writerows((label,differences[j],1e-5) for j,label in enumerate(old.LABELS))


def plot(out,cases,data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    families=[('n',[0]),('H1',[1,2]),('D',[3,4]),('T',[5,6]),('He3',[7,8,9]),('He4',[10,11,12]),('Li7',[13,14,15,16])]
    fig,axes=plt.subplots(7,1,figsize=(10,17),sharex=True)
    t=cases['ON_refined']['t'];eta=np.interp(t,data['t'],data['eta']);z=21*np.exp(-eta)-1
    for ax,(family,indices) in zip(axes,families):
        any_positive=False;has_negative=False
        for j,index in enumerate(indices):
            color=plt.get_cmap('tab10')(j)
            label='n' if index==0 else family+' '+('I','II','III','IV')[int(old.Q[index])]
            for name,style,lw in [('OFF_base','--',1.),('ON_base',':',1.),('ON_refined','-',1.7)]:
                values=cases[name]['physical'][index]
                has_negative=has_negative or bool(np.any(values<0))
                any_positive=any_positive or bool(np.any(values>0))
                # Retain raw exact zeros and signed values in CSV. Only values
                # outside the log plot domain are masked; no floor is inserted.
                ax.plot(z,np.ma.masked_less_equal(values,0),style,color=color,lw=lw,
                        label=label if name=='ON_refined' else None)
            ax.plot(data['z'],np.ma.masked_less_equal(data['y'][:,index],0),'-.',color=color,lw=.7,alpha=.5)
        if any_positive:ax.set_yscale('log')
        else:ax.set_ylim(0,1);ax.text(.5,.5,'No positive samples on log domain' if has_negative else 'All plotted populations exactly zero',ha='center',transform=ax.transAxes)
        if has_negative:ax.text(.99,.03,'Signed numerical samples retained in CSV; omitted on log axis',ha='right',fontsize=7,transform=ax.transAxes)
        ax.set_ylabel(family+'\nparticles / Href');ax.grid(alpha=.2);ax.legend(fontsize=8,ncol=4)
    axes[-1].set(xlim=(20,2),xlabel='Mean redshift z from the finite matched clock')
    handles=[Line2D([0],[0],color='black',ls=style,label=label) for label,style in
             [('OFF base','--'),('ON base',':'),('ON refined','-'),('Saved donor reference','-.')]]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.975),ncol=4,fontsize=9)
    fig.suptitle('All17 visible populations — illustrative prescribed-bath pilot',y=.995)
    fig.text(.5,.012,'Li7 IV included. Hidden Li6 is prescribed; total-baryon CSV includes Li6 and Bn+3BT.\nSaved donor is a reference curve; OFF uses a fixed reconstructed electron/photon/temperature bath.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,.955));fig.savefig(out/'pilot17_populations.png',dpi=150);plt.close(fig)


def main():
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    try:
        data=baseline();cases={name:read_case(out,name) for name in CASES}
        report,differences=validate(cases,data)
        write_tables(out,cases,data,differences);plot(out,cases,data)
    except Exception as exc:
        report={'status':'POSTPROCESS_INPUT_OR_RENDER_HOLD','error':str(exc),
                'scientific_admission':'NOT_ADMITTED','IVP_execution':'NO_SOLVER_CALLED_BY_POSTPROCESSOR'}
    (out/'PILOT_VALIDATION.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2,allow_nan=False))
    if report['status']!='PASS_SCOPED_NUMERICAL_CHECKS':raise SystemExit(1)


if __name__=='__main__':main()
