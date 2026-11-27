"""Plot saved validation JSON only; no scientific imports or solver calls."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--saved-json',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    source=Path(args.saved_json);raw=source.read_bytes();data=json.loads(raw)
    if not data['validation']['success']:raise SystemExit('failed validation cannot be plotted')
    num=lambda x:float(Fraction(x))
    mid=lambda item:(num(item['lower'])+num(item['upper']))/2
    plt.rcParams.update({'font.size':9,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,2,figsize=(9,6))
    rows=data['rotation_scan'];x=[num(row['offset']) for row in rows]
    axes[0,0].plot(x,[num(row['expected']) for row in rows],color='black',label='Exact triangular oracle')
    axes[0,0].scatter(x,[mid(row['coincidence']) for row in rows],s=15,label='Certified C')
    axes[0,0].set(xlabel='B sector start [turn]',ylabel='Coincidence event measure',title='Quarter sectors: shared-event azimuth')
    axes[0,0].legend(fontsize=7)
    rows=data['controls'];idx=list(range(len(rows)));w=.34
    axes[0,1].bar([i-w/2 for i in idx],[num(row['actual']) for row in rows],w,label='Actual C')
    axes[0,1].bar([i+w/2 for i in idx],[num(row['counterfactual']) for row in rows],w,label='Counterfactual')
    axes[0,1].set_xticks(idx,['No halfturn','Independent','Sum Q1+Q2','Both hits'],rotation=15,fontsize=7)
    axes[0,1].set(ylabel='Manufactured event/count measure',title='Four diagnostic controls')
    axes[0,1].legend(fontsize=7)
    rows=data['native_rows'];x=[row['energy_MeV'] for row in rows]
    for key,label in [('coincidence','Distinct-daughter C'),('hit_a','Hit A'),('hit_b','Hit B')]:
        axes[1,0].plot(x,[mid(row[key]) for row in rows],'o-',markersize=3,label=label)
    axes[1,0].set(xlabel='Incident photon energy [MeV]',ylabel='Declared manufactured measure',title='NIST scalar masses; finite sectors')
    axes[1,0].legend(fontsize=7)
    rows=data['bounds_comparison'];x=list(range(len(rows)))
    widths=[num(row['hit_a']['width']) for row in rows];bounds=[num(row['hit_a']['width_bound']) for row in rows]
    axes[1,1].bar([i-.17 for i in x],widths,.34,label='Actual width')
    axes[1,1].bar([i+.17 for i in x],bounds,.34,label='Area-based bound')
    axes[1,1].axhline(2**-40,color='black',linestyle='--',linewidth=.8,label='Default sigma / 2^40')
    axes[1,1].set_xticks(x,['Default delta','Manual delta = 1/16'])
    axes[1,1].set(yscale='log',ylabel='Hit-A enclosure width',title='Exact bounds; no epsilon claim for ratios')
    axes[1,1].legend(fontsize=7)
    for ax in axes.flat:ax.grid(alpha=.2)
    fig.suptitle('AZIMUTH09: uniform azimuth declared; continuous paired measure',fontsize=12)
    fig.text(.5,.015,'Saved validation data only. Energy closure: pair = G C; each label = G C / 2. No empirical normalization or heating claim.',ha='center',fontsize=7)
    fig.subplots_adjust(left=.09,right=.98,bottom=.13,top=.88,wspace=.34,hspace=.56)
    output=Path(args.output)
    for ext in ('svg','png'):
        path=output/f'AZIMUTH09.{ext}'
        if path.exists():raise FileExistsError(path)
        fig.savefig(path,dpi=110)
    plt.close(fig)
    receipt={'input':str(source),'input_sha256':hashlib.sha256(raw).hexdigest(),'scientific_function_calls':0,'scientific_imports':0,'outputs':['AZIMUTH09.svg','AZIMUTH09.png'],'scope':'Display values read from exact rational bounds saved in the one validation run'}
    with (output/'PLOT_RECEIPT.json').open('x') as stream:json.dump(receipt,stream,indent=2)
