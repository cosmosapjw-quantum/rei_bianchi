#!/usr/bin/env python3
"""Read the finite native matrix and plot refinement/cost; never run a solver."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipts', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    matrix = json.loads((args.receipts / 'MATRIX_RECEIPT.json').read_text())
    rows = []
    identities = []
    groups = {}
    for case in matrix['cases']:
        if case['status'] != 'COMPLETED':
            raise RuntimeError('Matrix is incomplete; inspect preserved process receipts before accuracy analysis.')
        folder_name = Path(case['receipt']).name if 'receipt' in case else f"{case['mode']}_{case['method']}_n{case['N']}"
        folder = args.receipts / folder_name
        raw = json.loads((folder / 'raw.json').read_text())
        outcome = json.loads((folder / 'outcome.json').read_text())
        assert outcome['exit_code'] == 0 and not outcome['truncated']
        assert raw['completed'] and raw['failure'] is None
        assert len(raw['records']) == raw['N']
        assert raw['config']['q'] == 0
        for stream in ('stdout', 'stderr'):
            assert digest(folder / (stream + '.txt')) == outcome[stream + '_sha256']
        first, last = raw['initial'], raw['records'][-1]['state']
        # q=0 only: proper ray energy factor is a_ref/a; here a_ref=initial a.
        physical_u = math.fsum(last['energy_ref']) * first['a'] / last['a']
        x, y, z = last['fractions']
        row = dict(mode=raw['mode'], method=raw['method'], N=raw['N'],
                   HII=x, HeII=y, HeIII=z, w_eV_H=last['w_ev'], T_K=last['temperature_k'],
                   photon_N_H=math.fsum(last['number']), photon_U_eV_H=physical_u,
                   P_HI=last['ledgers']['photo'][0],
                   source_N_H=last['ledgers']['source_n']-first['ledgers']['source_n'],
                   source_U_eV_H=last['ledgers']['source_u']-first['ledgers']['source_u'],
                   CMB_eV_H=last['ledgers']['cmb_input']-first['ledgers']['cmb_input'],
                   native_rhs=raw['native_rhs_attempts_including_fd_replay'],
                   native_wall_s=raw['wall_s'], process_wall_s=outcome['wall_s'])
        rows.append(row)
        groups.setdefault((row['mode'], row['method']), []).append(row)
        identities.append(dict(case=f"{row['mode']}/{row['method']}/N{row['N']}",
                               raw_sha256=digest(folder/'raw.json'),
                               inputs_sha256=digest(folder/'inputs.json'),
                               outcome_sha256=digest(folder/'outcome.json')))
    channels = ['HII', 'HeII', 'HeIII', 'w_eV_H', 'T_K', 'photon_N_H', 'photon_U_eV_H', 'P_HI']
    refinement = {}
    for key, group in groups.items():
        group.sort(key=lambda r: r['N'])
        report = {'N': [r['N'] for r in group], 'channels': {}}
        for field in channels:
            values = [r[field] for r in group]
            delta = [a-b for a, b in zip(values, values[1:])]
            ratio = [math.log2(abs(a/b)) if a and b else None for a, b in zip(delta, delta[1:])]
            ulps = [abs(d)/math.ulp(max(abs(a), abs(b))) if max(abs(a),abs(b)) else None
                    for d, a, b in zip(delta, values, values[1:])]
            report['channels'][field] = dict(values=values, signed_differences=delta,
                log2_difference_ratios=ratio, differences_in_endpoint_ulps=ulps,
                warning='Finite ratios only; small or irregular differences do not establish order.')
        refinement['/'.join(key)] = report
    empirical = []
    for mode in ('fixed', 'birth', 'disabled'):
        refgroup = groups[(mode, 'radau')]
        ref = refgroup[-1]
        own_difference = {k: abs(refgroup[-2][k]-ref[k]) for k in channels}
        for row in [r for r in rows if r['mode']==mode]:
            empirical.append(dict(mode=mode, method=row['method'], N=row['N'],
                reference=f'Radau N={ref["N"]}; empirical discrete-system comparison, not error bound',
                reference_last_self_difference=own_difference,
                absolute_difference={k: abs(row[k]-ref[k]) for k in channels}))
    output = dict(schema='rei.lrs.native.matrix.analysis.1', unique_cases=len(rows),
        native_runs_performed_by_this_script=0,
        total_native_rhs=sum(r['native_rhs'] for r in rows),
        total_native_wall_s=sum(r['native_wall_s'] for r in rows),
        total_process_wall_s=sum(r['process_wall_s'] for r in rows),
        rows=rows, refinement=refinement, empirical_comparisons=empirical, identities=identities,
        limitations=['q=0, cells=8, n_mu=8, one host and one timed run per setting',
                     'Radau scaled Newton atol=1e-13; unchanged SSPRK coupling tolerance=1e-15',
                     'fixed T=1/k_ref20; birth/disabled Delta ln a=1e-6',
                     'All recorded Radau CMB transfers negative; no positive-CMB or boundary coverage',
                     'GL2 method endpoints differ by at most one ulp; forcing not bitwise identical',
                     'No general nonlinear order, uniform stiff, Case B, full EoR or signed Bianchi admission'])
    (args.out/'MATRIX_ANALYSIS.json').write_text(json.dumps(output, indent=2)+'\n')
    with (args.out/'ENDPOINTS_AND_COST.csv').open('w', newline='') as file:
        writer=csv.DictWriter(file, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10, 'axes.titlesize':11, 'figure.dpi':150,
                         'savefig.dpi':180, 'axes.spines.top':False, 'axes.spines.right':False})
    fig, axes = plt.subplots(2,2,figsize=(11.8,8.2),layout='constrained')
    colors={'radau':'#1f628e', 'ssprk':'#be5935'}
    labels={'radau':'Native Radau IIA3', 'ssprk':'Native SSPRK2'}
    for method in ('radau','ssprk'):
        report=refinement['fixed/'+method]
        axes[0,0].loglog(report['N'][:-1], [abs(x) for x in report['channels']['HII']['signed_differences']],
                         'o-', color=colors[method], label=labels[method])
    axes[0,0].set(title='A  Fixed geometry: HII self differences',xlabel='Macro steps N',
                  ylabel=r'$|x_N-x_{2N}|$')
    axes[0,0].text(.04,.06,'Radau finite ratios: 4.920, 4.945\nSSPRK2 finite ratio: 2.165',
                   transform=axes[0,0].transAxes,fontsize=9)
    axes[0,0].legend(fontsize=9)
    ref=groups[('fixed','radau')][-1]['HII']
    for method in ('radau','ssprk'):
        data=[r for r in groups[('fixed',method)] if abs(r['HII']-ref)>0]
        axes[0,1].loglog([r['native_wall_s'] for r in data],[abs(r['HII']-ref) for r in data],
                        'o-',color=colors[method],label=labels[method])
        for r in data:
            axes[0,1].annotate(f'N={r["N"]}',(r['native_wall_s'],abs(r['HII']-ref)),
                               xytext=(5,4),textcoords='offset points',fontsize=8)
    axes[0,1].set(title='B  Finite fixed-geometry cost comparison',xlabel='Native case wall time [s]',
                  ylabel=r'$|x_N-x_{Radau,16}|$')
    axes[0,1].text(.04,.05,'Empirical reference; one timed run per case\nReference N8→N16 difference: 8.69e−10',
                   transform=axes[0,1].transAxes,fontsize=9)
    for method in ('radau','ssprk'):
        report=refinement['birth/'+method]
        axes[1,0].loglog(report['N'][:-1],[abs(x) for x in report['channels']['photon_N_H']['signed_differences']],
                         'o-',color=colors[method],label=labels[method])
    axes[1,0].set(title='C  Actual GL2 births: photon-number differences',xlabel='Macro steps N',
                  ylabel=r'$|N_{\gamma,N}-N_{\gamma,2N}|$ [photon/H]')
    axes[1,0].text(.04,.06,'Only two differences per method\nRadau ratio 3.486; SSPRK2 ratio 2.138',
                   transform=axes[1,0].transAxes,fontsize=9)
    ulp=math.ulp(groups[('birth','radau')][-1]['HeIII'])
    locations=[0,1,3,4]; values=[]; names=[]; shades=[]
    for method in ('radau','ssprk'):
        values.extend([x/ulp for x in refinement['birth/'+method]['channels']['HeIII']['signed_differences']])
        names.extend(['4→8','8→16']);shades.extend([colors[method]]*2)
    axes[1,1].bar(locations,values,color=shades,width=.7)
    axes[1,1].axhline(0,color='.4',lw=.8);axes[1,1].axhspan(-1,1,color='.85',alpha=.6)
    axes[1,1].set_xticks(locations,names)
    axes[1,1].set(title='D  GL2 HeIII: cancellation prevents order inference',
                  ylabel=r'Signed $(z_N-z_{2N})$/one endpoint ulp',xlabel='Radau pairs                         SSPRK2 pairs')
    axes[1,1].text(.53,.91,f'One ulp = {ulp:.3e}\nNo fitted time order',transform=axes[1,1].transAxes,fontsize=9)
    for ax in axes.flat:ax.grid(True,which='major',alpha=.17)
    fig.suptitle('Independent LRS native comparison — 19 finite settings, q=0, 8 cells × 8 angles',fontsize=13)
    for extension in ('png','pdf','svg'):
        fig.savefig(args.out/('NATIVE_REFINEMENT_AND_COST.'+extension))
    plt.close(fig)
    manifest={p.name: {'bytes':p.stat().st_size,'sha256':digest(p)} for p in args.out.iterdir() if p.is_file() and p.name!='ANALYSIS_FILES.json'}
    (args.out/'ANALYSIS_FILES.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ('unique_cases','total_native_rhs','total_native_wall_s','total_process_wall_s')}))


if __name__=='__main__':main()
