#!/usr/bin/env python3
"""Scientific diagnostic figures; source snapshots, NOT an original RT history."""
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
plt.rcParams['svg.hashsalt']='REI_IGM_SOURCE_SECANT_20261101'

def plot():
    ROOT.joinpath('figures').mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(ROOT/'results/TEMP_DECILE_10.csv')
    fig,ax=plt.subplots(figsize=(7,4.5))
    center=.5*(d['min_temperature_K']+d['max_temperature_K'])
    ax.semilogy(center,d['mean_abs_source_snapshot_gap_HII'],'o-',label='H II representative-source difference')
    ax.set_xlabel('Source representative gas temperature T [K]')
    ax.set_ylabel('Equal-node mean absolute discrepancy in H II fraction')
    ax.set_title('Source-rate midpoint proxy vs accepted endpoint, by T decile')
    ax.grid(True,alpha=.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(ROOT/'figures'/('TEMP_DECILE_HII_SOURCE_GAP.'+ext),dpi=160,metadata={'Creator':'REI IGM source-authentic diagnostic','Date':'2026-11-01'} if ext=='svg' else {'Software':'REI IGM source-authentic diagnostic'})
    plt.close(fig)
    df=pd.read_csv(ROOT/'results/NODEWISE_SOURCE_SECANT_46080.csv.gz',compression='gzip',float_precision='round_trip')
    fig,ax=plt.subplots(figsize=(7,4.5))
    sample=df.iloc[::8]
    ax.loglog(sample['original_logT_parent_width'],np.maximum(abs(sample['HII_dx_difference']),1e-18),'.',markersize=2,alpha=.45)
    ax.set_xlabel('Original tick160 parent enclosure width: ln(T_hi/T_lo)')
    ax.set_ylabel('|Representative H II displacement − two-source proxy|')
    ax.set_title('Different diagnostics: original width vs independent source proxy')
    ax.grid(True,alpha=.25)
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(ROOT/'figures'/('HII_SOURCE_PROXY_VS_PARENT_WIDTH.'+ext),dpi=160,metadata={'Creator':'REI IGM source-authentic diagnostic','Date':'2026-11-01'} if ext=='svg' else {'Software':'REI IGM source-authentic diagnostic'})
    plt.close(fig)

if __name__=='__main__':plot()
