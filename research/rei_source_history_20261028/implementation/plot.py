import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parents[1]/'outputs'


def main():
    with (OUT/'source_history_qss.csv').open() as f:rows=list(csv.DictReader(f))
    with (OUT/'initial_transient_envelope.csv').open() as f:transient=list(csv.DictReader(f))
    col=lambda name:np.array([float(r[name]) for r in rows])
    tr=lambda name:np.array([float(r[name]) for r in transient])
    fig,axes=plt.subplots(2,2,figsize=(11,7))
    for j,fam in enumerate(('neutron','tritium')):
        ax=axes[0,j]
        for key,label in [('QSS_l1','frozen QSS stock'),('total_bound','total error envelope'),('variation_bound','forcing variation')]:
            values=col(fam+'_'+key)
            ax.semilogy(col('z_mean'),np.ma.masked_equal(values,0),label=label)
        ax.set(xlim=(20,2),xlabel='Mean redshift z',ylabel='particles / Href',title=fam+' family')
        ax.legend(fontsize=8);ax.grid(alpha=.25)
        ax=axes[1,j]
        ax.loglog(tr('elapsed_proper_s')[1:],tr(fam+'_relative_bound')[1:],label='analytic total envelope / QSS norm')
        ax.axhline(.01,color='black',ls='--',label='1% certificate criterion')
        ax.set(xlabel='Elapsed proper time after turn-on [s]',ylabel='relative error upper bound',title='Initial '+fam+' relaxation')
        ax.legend(fontsize=8);ax.grid(alpha=.25)
    fig.suptitle('Finite source-history QSS certificate — illustrative, uncalibrated')
    fig.text(.5,.012,'Zero initial n/T stocks: first-epoch relative bound = 1. Analytic bound; no physical IVP.\nSaved-epoch certification only; no interval-wide certificate or astrophysical calibration.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.95));fig.savefig(OUT/'source_history_qss_envelope.png',dpi=150);plt.close(fig)


if __name__=='__main__':main()
