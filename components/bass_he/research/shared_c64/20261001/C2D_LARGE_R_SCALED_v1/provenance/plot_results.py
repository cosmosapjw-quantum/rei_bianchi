"""Plot archived final scalar data only; no physical computations."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
a=json.loads((ROOT/'evidence/FINAL_AUDIT.json').read_bytes())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
fig,axes=plt.subplots(1,2,figsize=(10,4.7))
fig.subplots_adjust(left=.11,right=.98,top=.83,bottom=.19,wspace=.36)
for ax,key,color,title in zip(axes,['Q_O','Q_B'],['#1f5c9e','#b55325'],[r'$Q_O=\bar L_O/x$',r'$Q_B=-x^2\bar L_B$']):
 rows=a['sequence'];xs=[r['R'] for r in rows];ys=[100*r[key+'_relative_difference_from_C'] for r in rows]
 ax.plot(xs,ys,color=color,alpha=.6,lw=1.5)
 for new,label in [(False,'Inherited scalars'),(True,'New endpoint audit')]:
  select=[r for r in rows if r['new_point']==new]
  ax.scatter([r['R'] for r in select],[100*r[key+'_relative_difference_from_C'] for r in select],facecolors=color if new else 'white',edgecolors=color,s=54,zorder=3,label=label)
 ax.axhline(0,color='#444444',lw=.8,ls='--');ax.set_xscale('log',base=2);ax.set_yscale('symlog',linthresh=1e-4)
 ax.set_ylim(min(ys)*2 if min(ys)<0 else -1e-4,max(ys)*2)
 ax.set_xticks(xs,labels=[str(x) for x in xs]);ax.grid(alpha=.18,which='both');ax.set_xlabel(r'$x=R/a_A$');ax.set_title(title)
 ax.set_ylabel('Difference from asymptotic coefficient (%)')
axes[0].legend(loc='best',frameon=False,fontsize=9)
fig.suptitle('BASS_HE: large-R scaled coupling sequence',fontsize=15)
fig.text(.5,.025,'Finite-R differences, not numerical error bars. No continuum or asymptotic-radius certificate.',ha='center',fontsize=9,color='#444444')
out=ROOT/'figures/C2D_LARGE_R_SCALED.png'
if out.exists():raise FileExistsError(out)
fig.savefig(out,bbox_inches='tight');plt.close(fig)
print(out)
