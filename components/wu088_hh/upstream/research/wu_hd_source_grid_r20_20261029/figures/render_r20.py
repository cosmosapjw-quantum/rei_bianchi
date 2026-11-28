import os
"""Reproducible static R20 figures; no observational interpretation."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import _extent_and_remainders

ROOT=Path(__file__).resolve().parents[1]
PDF=Path(os.environ.get('WU_R20_SOURCE_PDF', str(ROOT/'parent/ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf')))
OUT=ROOT/'figures'

def save(fig,name):
    for ext in ('png','svg'):
        fig.savefig(OUT/f'{name}.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)

def run():
    grid=load_native_grid(PDF)
    k105=float(grid.lookup(105).nominal_m3_s)
    k255=float(grid.lookup(255).nominal_m3_s)
    ts=np.linspace(0,1e10,501)
    exp=np.minimum(ts,5e9)*k105+np.maximum(ts-5e9,0)*k255
    ext=np.array([_extent_and_remainders(1e6,1e6,1.,float(x))[0] for x in exp])
    fig,ax=plt.subplots(figsize=(7.8,4.5))
    ax.plot(ts/1e9,1e6-ext,label=r'$n_{H^+}=n_{HD(0,2)}$')
    ax.plot(ts/1e9,ext,label=r'$n_{D^+}=n_{H_2(0,1)}$')
    ax.axvline(5.,linestyle='--',color='0.4',linewidth=1.0)
    ax.text(1.0,9e5,'105 K',fontsize=9)
    ax.text(7.,9e5,'255 K',fontsize=9)
    ax.set(xlabel='Proper time (10$^9$ s)',ylabel='Physical number density (m$^{-3}$)',
           title='Source-grid two-temperature nominal reaction (prescribed V/V0=1)')
    ax.legend(loc='center right');ax.grid(alpha=.25);fig.tight_layout()
    save(fig,'SOURCE_GRID_POPULATIONS')
    r=json.loads((ROOT/'results/NUMERICAL_BENCHMARK.json').read_text())
    nodes=[x['nodes'] for x in r['clock_quadrature']]
    errors=[x['relative_error'] for x in r['clock_quadrature']]
    fig,ax=plt.subplots(figsize=(7.6,4.5))
    ax.semilogy(nodes,errors,marker='o')
    ax.set(xlabel='Gauss-Legendre nodes in ln(a)',ylabel='Relative exposure error',
           title='Synthetic constant-H, V∝a³ clock quadrature (not a certificate)')
    ax.set_xticks(nodes);ax.grid(alpha=.3);fig.tight_layout()
    save(fig,'OWNER_CLOCK_QUADRATURE')
    fig,ax=plt.subplots(figsize=(7.6,4.5))
    cases=r['cases']
    ax.plot([x['segments'] for x in cases],[x['wall_speed_ratio'] for x in cases],marker='o')
    ax.set(xlabel='Source-grid segments',ylabel='DOP853 wall time / exact-flow wall time',
           title='Local matched-accuracy timing, source PDF parsing excluded')
    ax.grid(alpha=.25);fig.tight_layout()
    save(fig,'MATCHED_ACCURACY_TIMING')
    return {'plots':['SOURCE_GRID_POPULATIONS','OWNER_CLOCK_QUADRATURE','MATCHED_ACCURACY_TIMING'],
            'model':'synthetic density, prescribed source-grid T and clock',
            'uncertainty':'source true uncertainty not supplied',
            'no_temperature_interpolation':True}

if __name__=='__main__':
    r=run();(ROOT/'results/FIGURES.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
