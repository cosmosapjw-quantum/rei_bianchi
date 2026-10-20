"""CSV and plot from preserved Rust output and independent Decimal references."""
import argparse,csv,json,pathlib,os
os.environ.setdefault("MPLCONFIGDIR","/tmp/rei-observable-mplconfig")
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=pathlib.Path(__file__).resolve().parent
R=HERE/'results'
def main():
 global R
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--results',type=pathlib.Path,default=R);R=ap.parse_args().results
 s=json.loads((R/'STUDY.json').read_text());d=json.loads((R/'DECIMAL_REFERENCE.json').read_text())
 with (R/'OBSERVABLE_BOUNDS.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['clock','population','observable','signed_interval_lo','signed_interval_hi','independent_difference_decimal100','label_absolute_upper','chosen_absolute_upper'])
  for i,pair in enumerate(s['pairs']):
   for name,pop in pair['populations'].items():
    for j,obs in enumerate(s['observable_order']):
     bound=pop['moment_chosen_upper'][j-2] if j in [2,3] else pop['label_absolute_upper'][j]
     w.writerow([pair['coarse'],name,obs,*pop['signed_difference'][j],d['pair_references'][i]['populations'][name]['signed_difference'][j],pop['label_absolute_upper'][j],bound])
 with (R/'NORMALIZED_MEAN_BOUNDS.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['clock','population','mean_difference_decimal100_s','forward_upper_s','reverse_upper_s','global_upper_s','chosen_upper_s','global_over_chosen'])
  for i,pair in enumerate(s['pairs']):
   for name,pop in pair['populations'].items():
    b=pop['normalized_mean_bound'];u=b['chosen_upper'];w.writerow([pair['coarse'],name,d['pair_references'][i]['populations'][name]['normalized_mean_difference'],b['forward']['upper'],b['reverse']['upper'],b['global_upper'],u,b['global_upper']/u if u else 'identity'])
 fig,axes=plt.subplots(1,3,figsize=(12,4),sharex=True,constrained_layout=True)
 for ax,name in zip(axes,['all','sensitive','passive']):
  x=[8,16,32];actual=[abs(float(d['pair_references'][i]['populations'][name]['normalized_mean_difference'])) for i in range(3)]
  chosen=[s['pairs'][i]['populations'][name]['normalized_mean_bound']['chosen_upper'] for i in range(3)]
  glob=[s['pairs'][i]['populations'][name]['normalized_mean_bound']['global_upper'] for i in range(3)]
  ax.plot(x,actual,'o-',label='Independent absolute mean difference',color='#222222');ax.plot(x,chosen,'s--',label='Chosen certified upper',color='#0072B2');ax.plot(x,glob,'^:',label='Global fallback upper',color='#D55E00');ax.set_title(name.capitalize());ax.set_xlabel('Coarse birth clock');ax.set_xticks(x);ax.grid(alpha=.2);ax.set_yscale('log')
 axes[0].set_ylabel('Mean-age difference (s; log scale)');handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=8);fig.suptitle('Same exported labels and fixed opacity: mean source-age certificates');fig.savefig(R/'NORMALIZED_MEAN_BOUNDS.png',dpi=180);plt.close(fig)
 print(json.dumps({'csv_rows':84,'normalized_rows':12,'plot':'NORMALIZED_MEAN_BOUNDS.png'}))
if __name__=='__main__':main()
