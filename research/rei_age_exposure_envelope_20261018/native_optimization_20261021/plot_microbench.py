"""Plot the twenty preserved timing samples; never perform a new measurement."""
from pathlib import Path
import hashlib,json,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent

def main():
 source=HERE/'verification/MICROBENCH.json';data=json.loads(source.read_text());rows=data['raw'];assert len(rows)==20
 keys=[('original_serial',1),('ordered_pool',1),('ordered_pool',2),('ordered_pool',4)]
 groups=[[1000*r['wall_seconds'] for r in rows if (r['mode'],r['workers'])==key] for key in keys]
 assert all(len(g)==5 for g in groups)
 labels=['Original serial','Ordered pool 1','Ordered pool 2','Ordered pool 4'];colors=['#63738a','#8798ad','#3a8a92','#295e76']
 fig,(ax,table)=plt.subplots(1,2,figsize=(11,5),gridspec_kw={'width_ratios':[2.1,1.3]},layout='constrained')
 box=ax.boxplot(groups,tick_labels=labels,patch_artist=True,widths=.5,showfliers=False)
 for patch,color in zip(box['boxes'],colors):patch.set_facecolor(color);patch.set_alpha(.22)
 for i,(values,color) in enumerate(zip(groups,colors),1):
  ax.scatter([i+x for x in [-.1,-.05,0,.05,.1]],values,c=color,s=36,zorder=3)
  ax.text(i,max(values)+.22,f'median {statistics.median(values):.3f}',ha='center',fontsize=9,color=color)
 ax.set_ylabel('Milliseconds per sample (20 × 32 cohort evaluations)');ax.set_ylim(0,max(map(max,groups))*1.18);ax.grid(axis='y',alpha=.2);ax.tick_params(axis='x',rotation=15)
 table.axis('off');cells=[[f'{v:.3f}' for v in g]+[f'{statistics.median(g):.3f}'] for g in groups]
 t=table.table(cellText=cells,rowLabels=labels,colLabels=['1','2','3','4','5','Median'],loc='center',cellLoc='center');t.auto_set_font_size(False);t.set_fontsize(8);t.scale(1.0,1.7)
 table.set_title('All 20 measured samples, ms',fontsize=11,pad=20)
 fig.suptitle('Native prepared-absorption kernel: preserved local timing samples',fontsize=14)
 fig.text(.5,-.025,'5 repeats/mode · identical fixture and iteration count · all scientific fields bitwise equal\nNo gas RHS/history; no 64-core campaign speedup claim',ha='center',fontsize=9)
 dest=HERE/'verification/KERNEL_TIMINGS.png';fig.savefig(dest,dpi=170,bbox_inches='tight');plt.close(fig)
 refs=dict(source=str(source.relative_to(HERE)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=20,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),output=str(dest.relative_to(HERE)),scope='DISPLAY_OF_EXISTING_MEASUREMENTS_ONLY')
 (HERE/'verification/KERNEL_TIMINGS_REFERENCES.json').write_text(json.dumps(refs,indent=2)+'\n');print(json.dumps(refs))
if __name__=='__main__':main()
