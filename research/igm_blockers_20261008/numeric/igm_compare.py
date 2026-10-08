"""Frozen numerical-acceptance comparison for manufactured IGM histories."""
import argparse
import csv
import json
import math
from pathlib import Path

FRACTIONS={'x_hii','x_heii','x_heiii','ne_per_h'}
GAMMA={'Gamma_hi','Gamma_hei','Gamma_heii'}
ENERGY={'w','Eactive','emitted_E','out_E','redshift_E','escape_E','work_E','cmb_reservoir_E','ce_cap_HI_E','ce_cap_HeI_E','ce_cap_HeII_E','excluded_dr_E'}
PHOTONS={'Nactive','emitted_N','abs_HI','abs_HeI','abs_HeII','out_N','ci_HI','ci_HeI','ci_HeII','rr_HII','rr_HeII','rr_HeIII','dr_HeII','ci_floor_HI','ci_floor_HeI','ci_floor_HeII'}
REQUIRED={'ln_a','z','T','Tcmb','number_residual','energy_residual',*FRACTIONS,*GAMMA,*ENERGY,*PHOTONS}


def allowance(key,value):
    if key in FRACTIONS: return 1e-6+1e-3*abs(value)
    if key in GAMMA: return 1e-22+1e-3*abs(value)
    if key in ENERGY: return 1e-20+1e-3*abs(value)
    if key in PHOTONS: return 1e-8+1e-3*abs(value)
    if key in ('T','Tcmb'): return 1e-6+1e-3*abs(value)
    raise ValueError(f'no frozen acceptance scale for {key}')


def compare_rows(candidate,reference,allowance_factor=1.0):
    """Report max errors and reject missing, nonfinite, or misaligned rows.

    All cumulative channels/diagnostics are required, not silently dropped by
    intersecting column names. allowance_factor=.1 tests reference tightening.
    """
    if not candidate or len(candidate)!=len(reference):
        raise ValueError('history row count mismatch or empty history')
    fields={key:dict(max_absolute=0.,max_relative_nonzero=0.,max_allowance_ratio=0.,worst_row=0) for key in FRACTIONS|GAMMA|ENERGY|PHOTONS|{'T','Tcmb'}}
    budgets={label:dict(number_max_allowance_ratio=0.,energy_max_allowance_ratio=0.) for label in ('candidate','reference')}
    for i,(actual,expected) in enumerate(zip(candidate,reference)):
        for label,row in (('candidate',actual),('reference',expected)):
            missing=REQUIRED-set(row)
            if missing: raise ValueError(f'{label} row {i} missing fields: {sorted(missing)}')
            if any(not math.isfinite(row[k]) for k in REQUIRED):
                raise ValueError(f'{label} row {i} nonfinite value')
            number_ratio=abs(row['number_residual'])/(1e-10*max(row['emitted_N'],1e-10))
            energy_scale=max(row['emitted_E']+row['work_E']+row['escape_E']+abs(row['cmb_reservoir_E']),1e-20)
            energy_ratio=abs(row['energy_residual'])/(1e-10*energy_scale)
            budgets[label]['number_max_allowance_ratio']=max(budgets[label]['number_max_allowance_ratio'],number_ratio)
            budgets[label]['energy_max_allowance_ratio']=max(budgets[label]['energy_max_allowance_ratio'],energy_ratio)
        if abs(actual['ln_a']-expected['ln_a'])>2e-14:
            raise ValueError(f'output time mismatch at row {i}')
        for key,out in fields.items():
            error=abs(actual[key]-expected[key])
            relative=error/abs(expected[key]) if expected[key] else 0.
            ratio=error/(allowance_factor*allowance(key,expected[key]))
            out['max_absolute']=max(out['max_absolute'],error)
            out['max_relative_nonzero']=max(out['max_relative_nonzero'],relative)
            if ratio>out['max_allowance_ratio']:
                out['max_allowance_ratio']=ratio
                out['worst_row']=i
    return dict(passed=all(out['max_allowance_ratio']<=1 for out in fields.values()) and all(value<=1 for item in budgets.values() for value in item.values()),row_count=len(reference),allowance_factor=allowance_factor,fields=fields,budgets=budgets)


def read_csv(path):
    with open(path) as stream:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]


def plot_history(rows,output_path,other=None,comparison_passed=None,config=None,candidate_label='split BE',reference_label='independent Radau'):
    import os
    os.environ.setdefault('MPLCONFIGDIR','/tmp/igm-matplotlib')
    os.environ.setdefault('XDG_CACHE_HOME','/tmp/igm-cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,2,figsize=(12,11),constrained_layout=True)
    if config is not None:
        from igm_reference import binding
        rows=[dict(row,binding_E=binding([row['x_hii'],row['x_heii'],row['x_heiii'],row['w']],config)) for row in rows]
        if other is not None:
            other=[dict(row,binding_E=binding([row['x_hii'],row['x_heii'],row['x_heiii'],row['w']],config)) for row in other]
    x=[row['z'] for row in rows]
    groups=[(['x_hii','x_heii','x_heiii'],'Homogeneous ion fractions'),(['T','Tcmb'],'Temperature (K)'),(['ne_per_h'],'Electrons per H'),(['Gamma_hi','Gamma_hei','Gamma_heii'],'Photoionization rate (s⁻¹)'),(['emitted_N','Nactive','abs_HI','abs_HeI','abs_HeII','out_N'],'Photon ledger (per H)'),(['emitted_E','w','Eactive','escape_E','work_E','cmb_reservoir_E','redshift_E','out_E'],'Energy ledger (erg/H)')]
    if config is not None: groups[-1][0].insert(2,'binding_E')
    for ax,(keys,label) in zip(axes.flat,groups):
        for key in keys:
            line,=ax.plot(x,[r[key] for r in rows],label=key)
            if other:
                ax.plot([r['z'] for r in other],[r[key] for r in other],ls='--',color=line.get_color(),alpha=.8)
        ax.ticklabel_format(axis='x',style='plain',useOffset=False)
        ax.set_xlabel('Redshift z');ax.set_ylabel(label);ax.invert_xaxis();ax.grid(alpha=.25);ax.legend(fontsize=8)
    status='Numerical convergence targets NOT met\n' if comparison_passed is False else ('This pairwise comparison passes frozen targets\n' if comparison_passed is True else '')
    styles=f'\nSolid: {candidate_label}; dashed: {reference_label}' if other else ''
    fig.suptitle(status+'Manufactured homogeneous FLRW H/He history\nCase A escape, C=1, primary-only; not observed EoR'+styles)
    fig.savefig(output_path,dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,3.5),constrained_layout=True)
    for ax,key in zip(axes,('number_residual','energy_residual')):
        line,=ax.plot(x,[row[key] for row in rows],label=candidate_label)
        if other: ax.plot([row['z'] for row in other],[row[key] for row in other],ls='--',color=line.get_color(),label=reference_label)
        ax.legend(fontsize=8)
        ax.ticklabel_format(axis='x',style='plain',useOffset=False)
        ax.set_xlabel('Redshift z');ax.set_ylabel(key);ax.invert_xaxis();ax.grid(alpha=.25)
    path=Path(output_path)
    fig.savefig(path.with_name(path.stem+'_residuals'+path.suffix),dpi=160);plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--candidate',required=True)
    parser.add_argument('--reference',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--allowance-factor',type=float,default=1.)
    parser.add_argument('--plot')
    parser.add_argument('--config',help='Plot binding energy with this config; defaults to candidate CSV directory/config.cfg')
    parser.add_argument('--candidate-label',default='split BE')
    parser.add_argument('--reference-label',default='independent Radau')
    args=parser.parse_args()
    a,b=read_csv(args.candidate),read_csv(args.reference)
    result=compare_rows(a,b,args.allowance_factor)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    if args.plot:
        from igm_reference import read_config
        path=Path(args.config) if args.config else Path(args.candidate).parent/'config.cfg'
        cfg=read_config(path) if path.exists() else None
        plot_history(a,args.plot,b,result['passed'],cfg,args.candidate_label,args.reference_label)
    print(json.dumps(dict(passed=result['passed'],worst=max(v['max_allowance_ratio'] for v in result['fields'].values()))))
    raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__': main()
