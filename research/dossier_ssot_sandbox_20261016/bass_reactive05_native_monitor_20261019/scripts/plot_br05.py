#!/usr/bin/env python3
"""Render exact finite-grid comparisons and explicitly frozen-reference diagnostics."""
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'rei-br05-mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COLORS = ['#17658a', '#ba4b1e', '#7860a5']


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_final_table(data):
    if {(int(r['N_t']), int(r['r'])) for r in data} != {(n,r) for n in (16,32) for r in (2,4,8)}:
        raise ValueError('finite rectangle axes or completeness changed')
    if any(not np.isfinite(float(r[k])) for r in data for k in ('photons_com3','mean_age_s','q2')):
        raise ValueError('nonfinite figure input')


def canvas(width_mm):
    if width_mm == 182:
        fig, axes = plt.subplots(2, 2, figsize=(width_mm/25.4, 142/25.4), layout='constrained')
    else:
        fig, axes = plt.subplots(4, 1, figsize=(width_mm/25.4, 234/25.4), layout='constrained')
    return fig, list(axes.flat)


def label(ax, letter, title):
    ax.set_title(f'({letter}) {title}', loc='left', fontweight='bold', fontsize=8.5)
    ax.grid(alpha=.18, linewidth=.5)
    ax.spines[['top','right']].set_visible(False)


def save(fig, output, stem, width_mm):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = []
    for ax in fig.axes:
        # Matplotlib creates off-limit ticks that are not actually rendered.
        # Inspect only visible-range ticks, plus every nonempty axes text/title.
        xt = [text for value,text in zip(ax.get_xticks(),ax.get_xticklabels())
              if min(ax.get_xlim()) <= value <= max(ax.get_xlim())]
        yt = [text for value,text in zip(ax.get_yticks(),ax.get_yticklabels())
              if min(ax.get_ylim()) <= value <= max(ax.get_ylim())]
        titles = [x for x in ax.get_children() if isinstance(x, matplotlib.text.Text)]
        for text in [ax.xaxis.label,ax.yaxis.label,*titles,*xt,*yt]:
            if text.get_visible() and text.get_text():
                box = text.get_window_extent(renderer)
                if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width+1 or box.y1 > fig.bbox.height+1:
                    bounds.append(text.get_text())
    if bounds:
        raise ValueError('clipped text: '+repr(bounds))
    base = output/f'{stem}_{width_mm}mm'
    fig.savefig(base.with_suffix('.png'), dpi=220)
    fig.savefig(base.with_suffix('.pdf'), metadata={'Title':stem,'Subject':'BR05 finite-grid/frozen-reference scope'})
    plt.close(fig)
    return {'stem':stem,'width_mm':width_mm,'height_mm':142 if width_mm==182 else 234,
            'minimum_font_pt':7.5,'text_boundary_check':'PASS','human_visual_audit':'separate required gate'}


def main():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,
                         'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,
                         'lines.linewidth':1.35,'lines.markersize':4,'pdf.fonttype':42})
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    sources={
        'finals':ROOT/'evidence/independent/pair/NATIVE_FINALS.csv',
        'interactions':ROOT/'evidence/independent/pair/NATIVE_INTERACTION_COMPARISON.csv',
        'rules':ROOT/'evidence/independent/monitor/RULE_REFERENCE_COMPARISON.csv',
        'newborn':ROOT/'evidence/independent/monitor/NEWBORN_MEASURE_COMPARISON.csv',
        'cohorts':ROOT/'evidence/native/monitor_n16_r8/MONITOR_FINAL_COHORTS.csv'}
    final=rows(sources['finals']);check_final_table(final)
    mix={r['field']:r for r in rows(sources['interactions'])}
    rules=rows(sources['rules']);newborn=rows(sources['newborn'])
    energies=sorted({float(r['energy_ev']) for r in rules})
    envelope=[]
    for e in energies:
        data=[r for r in rules if float(r['energy_ev'])==e]
        assert len(data)==16
        w=[float(r['kernel_W1_s']) for r in data];ks=[float(r['kernel_cdf_sup']) for r in data]
        envelope.append(dict(energy_ev=e,W1_s_min=min(w),W1_s_max=max(w),
                             CDF_sup_min=min(ks),CDF_sup_max=max(ks)))
    cohort=rows(sources['cohorts'])
    age=np.array([float(r['age_s']) for r in cohort]);mass=np.array([float(r['retained_count_com3']) for r in cohort])
    assert np.all(age>0) and np.all(mass>=0) and mass.sum()>0
    edges=np.geomspace(age.min()*.999,age.max()*1.001,33)
    hist,_=np.histogram(age,bins=edges,weights=mass/mass.sum())
    hist_rows=[dict(left_s=edges[i],right_s=edges[i+1],retained_probability=hist[i]) for i in range(32)]
    for name,data in [('MONITOR_ENVELOPE_DATA.csv',envelope),('RETAINED_AGE_HISTOGRAM_DATA.csv',hist_rows)]:
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    manifests=[]
    for width in (182,90):
        fig,axes=canvas(width)
        specs=[('photons_com3',1.0038e-8,1e-13,r'$N_\gamma/(10^{-13}\,\mathrm{m}^{-3})-100380$', 'Photon number'),
               ('mean_age_s',1.511e10,1e6,r'$(\langle A\rangle-1.511\times10^{10}\,\mathrm{s})/(10^6\,\mathrm{s})$','Mean photon age'),
               ('q2',5.20e-8,1e-11,r'$(q_2-5.20\times10^{-8})/10^{-11}$','Energy-weighted quadrupole')]
        for i,(field,offset,scale,ylabel,title) in enumerate(specs):
            ax=axes[i];label(ax,'abcd'[i],title)
            for n,color,marker in ((16,COLORS[0],'o'),(32,COLORS[1],'s')):
                selected=sorted((r for r in final if int(r['N_t'])==n),key=lambda r:int(r['r']))
                ax.plot([int(r['r']) for r in selected],[(float(r[field])-offset)/scale for r in selected],
                        marker=marker,color=color,label=rf'$N_t={n}$')
            ax.set_xscale('log',base=2);ax.set_xticks([2,4,8],['2','4','8']);ax.set_xlabel('Birth refinement r')
            ax.set_ylabel(ylabel);ax.legend(frameon=False)
        ax=axes[3];label(ax,'d','Mixed-term magnitude after refinement')
        fields=['photons_com3','mean_age_s','second_age_s2','q2']
        values=[float(mix[f]['interaction_magnitude_ratio']) for f in fields]
        ax.bar(range(4),values,color=COLORS[0],width=.62)
        for i,value in enumerate(values):ax.text(i,value+.002,f'{value:.3f}',ha='center',fontsize=7.5)
        ax.set_xticks(range(4),[r'$N_\gamma$',r'$\langle A\rangle$',r'$\langle A^2\rangle$',r'$q_2$'])
        ax.set_ylabel(r'$|D_{tr}^{4\to8}|/|D_{tr}^{2\to4}|$');ax.set_ylim(0,.12)
        manifests.append(save(fig,out,'BR05_TIME_BIRTH_RECTANGLE',width))

        fig,axes=canvas(width)
        for i,(lo,hi,ylabel,title) in enumerate([
                ('W1_s_min','W1_s_max',r'$W_1$ of frozen survivor age (s)','Frozen-reference age resolution'),
                ('CDF_sup_min','CDF_sup_max',r'$\sup|F_{\rm atoms}-F_{\rm frozen}|$','Frozen-reference CDF distance')]):
            ax=axes[i];label(ax,'ab'[i],title)
            low=[r[lo] for r in envelope];high=[r[hi] for r in envelope]
            ax.fill_between(energies,low,high,color=COLORS[0],alpha=.3)
            ax.plot(energies,low,color=COLORS[0],label='Range over 16 steps')
            ax.plot(energies,high,color=COLORS[0],linewidth=.7)
            ax.set_xscale('log');ax.set_xlabel('Emitted photon energy (eV)');ax.set_ylabel(ylabel)
            ax.set_xticks([15,25,50,100],['15','25','50','100'])
            ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            if i==0:ax.set_yscale('log')
            ax.legend(frameon=False)
        ax=axes[2];label(ax,'c','Newborn number increments')
        for key,legend,color,marker in [('source_clock_relative_shift','Native source + clock',COLORS[0],'o'),
                ('transport_relative_shift','Actual transport increment',COLORS[1],'s')]:
            ax.plot([int(r['step']) for r in newborn],[1e6*float(r[key]) for r in newborn],
                    label=legend,color=color,marker=marker,markevery=3)
        ax.set_xlabel('Accepted local step');ax.set_ylabel('Change / constant-source reference (ppm)')
        ax.legend(frameon=False,loc='center right');ax.set_xticks([1,4,8,12,16])
        ax=axes[3];label(ax,'d','Actual final cohort age distribution')
        ax.stairs(hist,edges,color=COLORS[0],fill=True,alpha=.65)
        ax.set_xscale('log');ax.set_xlabel('Photon age at final time (s)')
        ax.set_ylabel('Retained probability per log bin')
        manifests.append(save(fig,out,'BR05_NATIVE_BIRTH_MONITOR',width))
    report={'schema':'BR05_FIGURE_DATA_PROVENANCE_V1','figures':manifests,
        'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sources.values()],
        'point_selection':'All 6 finite-grid finals; all 768 frozen rules in 16-step envelopes; all 16 newborn batches; all 314624 final cohorts in 32 log-age bins.',
        'reference_scope':'The plotted offsets are numerical baselines, not exact solutions. W1/CDF refer only to the frozen selector reference. No absolute nonlinear error is plotted.',
        'histogram_scope':'A display histogram only; no cohorts in the solver are merged or deleted.',
        'mixed_term':'Dtr = f(32,2r)-f(16,2r)-f(32,r)+f(16,r), evaluated in Decimal96 upstream.',
        'native_control':'SIGNED_MINUS, grid121, T=8e12 s, source-native H/He/D, opacity GL4; exactly one new N16r8 run.',
        'script_sha256':sha(Path(__file__)),'python':sys.version,'matplotlib':matplotlib.__version__}
    (out/'FIGURE_PROVENANCE.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'RENDERED_REQUIRES_VISUAL_AUDIT','figures':4,'formats':['PNG','PDF']}))


if __name__=='__main__':main()
