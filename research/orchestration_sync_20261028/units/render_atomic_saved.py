"""Diagnostics from saved exact results only; no scientific subprocess rerun."""
import json,pathlib,time,resource
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=pathlib.Path(__file__).resolve().parent
plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
start=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_SELF)
u=ROOT/'WU_CUBIC_RATIONAL_DOUBLE_ROOT_PREPROCESS_V1';p=json.loads((u/'PRIMARY.json').read_text());r=json.loads((u/'REFERENCE.json').read_text())
fig,axs=plt.subplots(1,2,figsize=(12,4.8));xs=[i/400 for i in range(401)]
for c in p['cases']:
    power=list(map(lambda x:float(F(x)),c['power_x']));ys=[sum(a*x**k for k,a in enumerate(power)) for x in xs];axs[0].plot(xs,ys,label=c['id'])
axs[0].set(xlabel='Normalized clock x',ylabel='Forcing p(x) [s⁻¹]',title='Saved power coefficients: frozen double-root family');axs[0].axhline(0,color='black',lw=.6);axs[0].legend(fontsize=8)
v=p['cases'][0];orig=list(map(lambda x:float(F(x)),r['checks'][0]['unsplit_B3']));left=list(map(lambda x:float(F(x)),v['cells'][0]['B3']));right=list(map(lambda x:float(F(x)),v['cells'][1]['B3']))
for offset,cs,label in [(-.23,orig,'Original cell'),(0,left,'Left split cell'),(.23,right,'Right split cell')]:axs[1].bar([i+offset for i in range(4)],cs,width=.22,label=label)
axs[1].axhline(0,color='black',lw=.7);axs[1].set(xticks=range(4),xlabel='Bernstein B3 coefficient index',ylabel='Coefficient [s⁻¹]',title='cubic_plus: original negative coefficient → two positive cells');axs[1].legend(fontsize=8)
fig.suptitle('Exact rational preprocessing • 7/7 coefficient and integral identities passed',fontsize=13);fig.text(.5,.01,'Plot uses saved exact coefficients; time mapping t∈[2,5] s, split keeps original memory origin. Frozen family only.',ha='center',fontsize=9);fig.tight_layout(rect=(0,.04,1,.94));fig.savefig(u/'DIAGNOSTIC.svg');fig.savefig(u/'DIAGNOSTIC.png',dpi=130);plt.close(fig)

def hull(points):
    pts=sorted(set(points))
    if len(pts)<=2:return pts
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];hi=[]
    for v in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],v)<=0:lo.pop()
        lo.append(v)
    for v in reversed(pts):
        while len(hi)>=2 and cross(hi[-2],hi[-1],v)<=0:hi.pop()
        hi.append(v)
    return lo[:-1]+hi[:-1]

u=ROOT/'CR_SAME_BIN_HL_CORRECTED_JOINT_FACET_V1';p=json.loads((u/'PRIMARY.json').read_text());r=json.loads((u/'REFERENCE.json').read_text());fig,axes=plt.subplots(3,3,figsize=(12,10))
for ax,pr,ref in zip(axes.flat,p['cases'],r['cases']):
    points=[(float(F(v['C'])),float(F(v['d']))) for v in ref['vertices']];poly=hull(points);N,L,S,D=[float(F(pr[k])) for k in ('N','L','S','D')];hi=max(1.,D*1.12);cs=[i*hi/100 for i in range(101)]
    if len(poly)>=3:ax.fill([x for x,y in poly],[y for x,y in poly],color='#badce9',alpha=.8)
    elif len(poly)==2:ax.plot([x for x,y in poly],[y for x,y in poly],color='#6ca8be',lw=5,alpha=.8)
    ax.scatter([x for x,y in points],[y for x,y in points],s=15,c='#134b64',zorder=4,label='Full-system projected vertices')
    ax.plot(cs,[min(D,(L+c)/2) for c in cs],'--',color='#c55246',label='Old S=0 bound')
    ax.plot(cs,[min(D,(L+S+c)/2) for c in cs],color='#187a4b',label='Corrected upper bound')
    ax.set(xlim=(-.04*hi,hi),ylim=(-.04*hi,hi),xlabel='Cross-bin pair mass C',ylabel='Total pair mass d',title=f"{pr['id']}: S={pr['S']}, {ref['accepted_vertices']} full vertices")
    ax.grid(alpha=.15)
handles,labels=axes.flat[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=9);fig.suptitle('Same-bin HL correction: exact feasible projections and necessary upper bounds',fontsize=14);fig.text(.5,.047,'Axes: m⁻³ s⁻². All polygons use saved full marginal-system vertices; upper bound does not assert generic sufficiency.',ha='center',fontsize=9);fig.tight_layout(rect=(0,.07,1,.96));fig.savefig(u/'DIAGNOSTIC.svg');fig.savefig(u/'DIAGNOSTIC.png',dpi=130);plt.close(fig)
end=resource.getrusage(resource.RUSAGE_SELF);(ROOT/'ATOMIC_RENDER_RESOURCE.json').write_text(json.dumps({'purpose':'render saved exact results only','cpu_seconds':end.ru_utime+end.ru_stime-cpu.ru_utime-cpu.ru_stime,'wall_seconds':time.monotonic()-start,'science_children_rerun':False,'host_overhead':'UNKNOWN_NOT_MEASURED'},indent=2)+'\n')
