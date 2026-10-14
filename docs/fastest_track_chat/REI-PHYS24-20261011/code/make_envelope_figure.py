#!/usr/bin/env python3
"""Render PHYS24's proved envelope; sampling is for display only."""
from __future__ import annotations

import argparse
from decimal import Decimal as D
import hashlib
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError('Choose a fresh figure output directory.')
    spec = importlib.util.spec_from_file_location(
        'phys24_display_kernel', ROOT / 'contributions/numerics/moment_envelope.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result_path = ROOT / 'contributions/numerics/MOMENT_ENVELOPE.json'
    result = json.loads(result_path.read_text())
    jx = D(result['constants']['J_h2_x_s-1'])
    jw = D(result['constants']['J_h2_w_H_eV-1_s-1'])
    a, b = D('13.61'), D('24.58')
    ka = D(result['endpoint_values']['left']['k_s-4'])
    kb = D(result['endpoint_values']['right']['k_s-4'])
    emin = float(result['mono_zero_inherited']['midpoint_eV'])
    eplus = float(result['endpoint_chord_zero']['mean_eV'])
    grid = [a + (b-a)*D(i)/D(240) for i in range(241)]
    lower = [module.response(m, jx, jw)['k_s-4'] for m in grid]
    upper = [((b-m)*ka+(m-a)*kb)/(b-a) for m in grid]
    xx = np.array([float(m) for m in grid])
    yy = np.array([float(v/D('1e-64')) for v in lower])
    zz = np.array([float(v/D('1e-64')) for v in upper])
    sample19 = next(x for x in result['envelope_samples'] if x['label']=='mean_19')
    low19, high19 = [float(D(sample19[k])/D('1e-64')) for k in
                     ['lower_candidate_k_s-4','upper_candidate_k_s-4']]

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'pdf.fonttype':42,'axes.titleweight':'bold'})
    fig = plt.figure(figsize=(12.6,8.6), facecolor='white')
    gs = fig.add_gridspec(2,1,height_ratios=[6,1],hspace=0.12,
                          left=.10,right=.96,bottom=.16,top=.82)
    ax = fig.add_subplot(gs[0])
    strip = fig.add_subplot(gs[1],sharex=ax)
    navy, orange = '#205b8c','#b96d25'
    ax.fill_between(xx,yy,zz,color='#afcce0',alpha=.55,
                    label='All attainable responses')
    ax.plot(xx,zz,color=orange,lw=2.8,label='Maximum: 13.61 / 24.58 eV endpoint mixture')
    ax.plot(xx,yy,color=navy,lw=2.8,label='Minimum: monoenergetic spectrum at the mean')
    ax.axhline(0,color='#263442',lw=1.1)
    for value in [emin,eplus]:
        ax.axvline(value,color='#7d858d',ls=(0,(3,3)),lw=1.1,zorder=0)
    ax.scatter([emin,eplus],[0,0],s=44,c=[navy,orange],edgecolors='white',zorder=5)
    ax.annotate(r'$E_-\simeq15.43367$',xy=(emin,0),xytext=(14.02,-.55),
                color=navy,arrowprops={'arrowstyle':'-','color':navy},fontsize=11)
    ax.annotate(r'$E_+\simeq19.55655$',xy=(eplus,0),xytext=(20.2,.42),
                color=orange,arrowprops={'arrowstyle':'-','color':orange},fontsize=11)
    ax.annotate('',xy=(19,high19),xytext=(19,low19),
                arrowprops={'arrowstyle':'<->','lw':1.5,'color':'#333d48'})
    ax.text(19.22,-.75,'At mean 19 eV\n'+r'$[-1.40473,\ +0.18212]\times10^{-64}\;\mathrm{s}^{-4}$',
            fontsize=10.4,color='#333d48',ha='left',va='center',
            bbox={'facecolor':'white','edgecolor':'none','alpha':.82,'pad':4})
    ax.set_xlim(float(a),float(b));ax.set_ylim(-1.98,2.22)
    ax.set_ylabel(r'HeIII coefficient $a_{4,h_2}$  [$10^{-64}\;\mathrm{s}^{-4}$]',labelpad=12)
    ax.grid(axis='y',color='#e2e6ea',lw=.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis='x',labelbottom=False)
    ax.legend(loc='upper right',frameon=False,fontsize=10.4,
              borderaxespad=1,labelspacing=.75)
    bands=[(float(a),emin,'All positive','#d9eee7','#195642'),
           (emin,eplus,'Negative, zero or positive','#f7e8ca','#725218'),
           (eplus,float(b),'All negative','#e7e3f1','#554077')]
    for lo,hi,label,color,ink in bands:
        strip.axvspan(lo,hi,0,1,color=color,lw=0)
        strip.text((lo+hi)/2,.50,label,ha='center',va='center',fontsize=10.5,color=ink)
    strip.set_ylim(0,1);strip.set_yticks([])
    for spine in strip.spines.values():spine.set_visible(False)
    strip.set_xticks([13.61,15,17,19,21,23,24.58])
    strip.set_xticklabels(['13.61','15','17','19','21','23','24.58'])
    strip.set_xlabel(r'Fixed mean photon energy $\bar E$ [eV]',labelpad=10)
    fig.text(.10,.94,'PHYS24  |  The full HeIII response range at fixed moments',
             fontsize=18,fontweight='bold',color='#172c40')
    fig.text(.10,.891,r'Initial $\epsilon^2t^4$ coefficient · $N_0\simeq0.05$ photon/H · fixed numerical $J_{\mathrm{np},*}$',
             fontsize=12,color='#52616d')
    fig.text(.10,.07,
             r'At $E_-$: zero only for the mono spectrum.  At $E_+$: zero only for the endpoint mixture.',
             fontsize=10.2,color='#465563')
    fig.text(.10,.034,
             'Curvature and extrema: exact conditional theorem. Boundary values: numerical. Finite-time / physical admission: HOLD.',
             fontsize=9.5,color='#52616d')
    args.output_dir.mkdir(parents=True)
    png=args.output_dir/'PHYS24_fixed_moment_envelope.png'
    pdf=args.output_dir/'PHYS24_fixed_moment_envelope.pdf'
    fig.savefig(png,dpi=190)
    fig.savefig(pdf,metadata={'Title':'PHYS24 fixed-moment HeIII envelope','Creator':'Matplotlib'})
    plt.close(fig)
    values={'task':'REI-PHYS24-20261011','purpose':'display only; zero independent validation credit',
            'new_or_old_scientific_main_invocations':0,'display_points':len(grid),
            'source_result_sha256':hashlib.sha256(result_path.read_bytes()).hexdigest(),
            'python_module':'new PHYS24 response helper only; no main invocation',
            'matplotlib_version':matplotlib.__version__,'numpy_version':np.__version__,
            'coefficient_unit':'s^-4','axis_scale':'1e-64',
            'rows':[{'mean_eV':str(m),'minimum_s-4':str(lo),'maximum_s-4':str(hi)}
                    for m,lo,hi in zip(grid,lower,upper)]}
    (args.output_dir/'PHYS24_fixed_moment_envelope.json').write_text(
        json.dumps(values,indent=2)+'\n')
    print(json.dumps({'status':'RENDERED','display_points':len(grid),
                      'png':str(png),'pdf':str(pdf),'science_main_invocations':0}))


if __name__=='__main__':
    main()
