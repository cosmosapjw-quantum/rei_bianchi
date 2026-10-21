"""Plot measured points and medians; no scientific calculation is executed."""
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/rei_age_matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'results/BENCHMARK.json').read_text())
groups=data['measurements']
fig, axes=plt.subplots(1,2,figsize=(12,5.2),gridspec_kw={'width_ratios':[1.2,1]})
names=['baseline_2','integer_taylor_A_2','preload_B_2','shared_oracle_C_2','shared_oracle_C_8']
labels=['Baseline\n2 threads','A: integer\n2 threads','B: preload\n2 threads','C: shared audit\n2 threads','C: shared audit\n8 threads']
colors=['#475569','#2563eb','#059669','#d97706','#7c3aed']
for i,(name,color) in enumerate(zip(names,colors)):
    r=groups[name];y=r['wall_seconds']
    axes[0].scatter([i-.09,i,i+.09],y,s=45,color=color,zorder=3)
    m=r['median_wall_seconds'];axes[0].plot([i-.22,i+.22],[m,m],color=color,lw=2)
    axes[0].annotate(f'{m:.3f} s',(i,m),xytext=(0,12),textcoords='offset points',ha='center',fontsize=9)
axes[0].set_yscale('log');axes[0].set_ylim(.9,80);axes[0].set_xticks(range(5),labels,fontsize=9)
axes[0].set_ylabel('Warm executable wall time (seconds; log scale)')
axes[0].set_title('Three measured runs per variant',loc='left',fontsize=11)
for key,label,color in [('scaling_B','B: repeated exact oracles','#059669'),('scaling_C','C: shared exact oracle + all-prefix parity','#d97706')]:
    values=data[key];x=[1,2,4,8];y=[values[str(n)] for n in x]
    axes[1].plot(x,y,'o-',color=color,label=label)
axes[1].set_xticks([1,2,4,8]);axes[1].set_xlabel('Cache / independent-oracle task threads')
axes[1].set_ylabel('Warm executable wall time (seconds)');axes[1].set_ylim(0,10)
axes[1].set_title('Measured scaling points (one run each)',loc='left',fontsize=11)
axes[1].legend(loc='upper right',fontsize=8,frameon=False)
for ax in axes:
    ax.grid(axis='y',color='#e2e8f0',lw=.7);ax.spines[['top','right']].set_visible(False);ax.set_axisbelow(True)
fig.suptitle('Exact age-transport optimization: 57,344 nodes, four fixed clock settings',fontsize=13,x=.04,ha='left')
fig.text(.04,.025,'Points are actual runs; horizontal segments mark medians. C shares equivalent oracle work; C at 8 threads uses more task threads.\nAll reported scientific values match baseline bit for bit. Build and compiler setup costs are excluded.',fontsize=9,color='#475569')
fig.subplots_adjust(left=.07,right=.98,top=.84,bottom=.22,wspace=.32)
fig.savefig(HERE/'results/PERFORMANCE.png',dpi=180)
fig.savefig(HERE/'results/PERFORMANCE.svg')
