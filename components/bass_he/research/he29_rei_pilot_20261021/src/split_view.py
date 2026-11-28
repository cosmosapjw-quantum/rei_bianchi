"""18-point independent initial-stress view: 12 new, six original references."""
import json,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from species_stress import canonical_row
ROOT=Path(__file__).resolve().parents[1]
def build():
 refs=[]
 for p in sorted((ROOT/'data/results/split_cases').glob('split*.json')):refs.append((p,False))
 for si in ['00','02']:
  for suffix in ['p00_zero','p02_minus','p02_plus']:refs.append((ROOT/'data/results/cases'/f's{si}_{suffix}.json',True))
 rows=[];endpoints=[];manifest=[];fig,axes=plt.subplots(2,2,figsize=(11,9))
 for p,reused in refs:
  c=json.loads(p.read_text());assert c['status']=='completed';h=[dict(case_id=c['case_id'],reused=reused,source_path=str(p.relative_to(ROOT)),identity=c['identity_sha256'],saved_index=i,a=d['a'],**canonical_row(d)) for i,d in enumerate(c['diagnostics'])];rows+=h;endpoints.extend([dict(endpoint=k,**r) for k,r in [('initial',h[0]),('final',h[-1])]]);manifest.append(dict(case_id=c['case_id'],reused=reused,path=str(p.relative_to(ROOT)),identity=c['identity_sha256']));plane=0 if c['inputs']['Sigma_F']==0 else 1
  vm,vr=h[0]['v_m'],h[0]['v_r'];color='gray' if reused else ('tab:red' if vm>0 else 'tab:blue');marker='o' if reused else ('^' if vr>1e-12 else ('v' if vr<-1e-12 else 's'))
  axes[plane,0].scatter(h[0]['Pi_m'],h[0]['Pi_r'],marker=marker,facecolors='none',edgecolors=color,s=110)
  axes[plane,1].scatter(vm,vr,marker=marker,facecolors='none',edgecolors=color,s=85)
 for i,sigma in enumerate([0,.03]):
  axes[i,0].set(title=f'Sigma_F0={sigma}: magnitude grid',xlabel='initial Pi_m',ylabel='initial Pi_r',xticks=[0,.0003],yticks=[0,.0006],xlim=(-.00008,.00038),ylim=(-.00012,.00072))
  axes[i,1].set(title=f'Sigma_F0={sigma}: signed initial sectors',xlabel='initial v_m',ylabel='initial v_r',xticks=[-.0003,0,.0003],yticks=[-.0006,0,.0006]);axes[i,1].axhline(0,color='gray',lw=.5);axes[i,1].axvline(0,color='gray',lw=.5)
  for ax in axes[i]:ax.grid(alpha=.25);ax.ticklabel_format(style='sci',axis='both',scilimits=(-3,-3))
 fig.suptitle('Independent matter/radiation finite grid: 18 points, 12 new + 6 reused\nBlue matter −, red matter +, gray reused Pi_m≈0; triangle ↑ radiation +, ↓ −, square zero\nMagnitude panel sign sectors overlap exactly; signed panel resolves all points; no interpolation',fontsize=11);fig.tight_layout(rect=[0,0,1,.89])
 for ext in ['png','svg','pdf']:fig.savefig(ROOT/'plots'/f'split_initial_grid.{ext}',dpi=170)
 for name,data in [('split_view_history',rows),('split_view_endpoints',endpoints)]:
  (ROOT/'data/results'/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
  with (ROOT/'data/results'/f'{name}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 (ROOT/'data/results/split_view_manifest.json').write_text(json.dumps(dict(new=12,reused=6,view=18,total_unique_integrations=40,references=manifest),indent=2)+'\n')
if __name__=='__main__':build()

def response():
    import hashlib
    from matplotlib.colors import Normalize
    rows=json.loads((ROOT/'data/results/split_view_endpoints.json').read_text())
    first={r['case_id']:r for r in rows if r['endpoint']=='initial'}
    final=[r for r in rows if r['endpoint']=='final']
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    for j,key in enumerate(['Sigma_F','Pi_m','Pi_r']):
        norm=Normalize(min(r[key] for r in final),max(r[key] for r in final))
        for i,sigma in enumerate([0,.03]):
            selected=[r for r in final if abs(first[r['case_id']]['Sigma_F']-sigma)<1e-12];ax=axes[i,j]
            sc=ax.scatter([first[r['case_id']]['v_m'] for r in selected],[first[r['case_id']]['v_r'] for r in selected],c=[r[key] for r in selected],norm=norm,cmap='viridis',s=160,edgecolors='black',linewidths=.6)
            ax.set(title=f'Sigma_F0={sigma}: final {key}',xlabel='signed initial v_m',ylabel='signed initial v_r',xticks=[-.0003,0,.0003],yticks=[-.0006,0,.0006]);ax.ticklabel_format(style='sci',axis='both',scilimits=(-3,-3));ax.grid(alpha=.2);fig.colorbar(sc,ax=ax,label=f'final {key}',fraction=.046,pad=.04)
    fig.suptitle('Independent initial matter / radiation stress: actual final responses at a=0.2\n18 discrete initial states (12 new, 6 reused); common color scale within each column; no interpolation',fontsize=12);fig.tight_layout(rect=[0,0,1,.91])
    for ext in ['png','svg','pdf']:fig.savefig(ROOT/'plots'/f'split_final_response.{ext}',dpi=170)
    plt.close(fig)
    used=['data/results/split_view_endpoints.json','data/results/split_view_history.json','src/split_view.py']
    (ROOT/'data/results/split_response_plot_sources.json').write_text(json.dumps({n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in used},indent=2)+'\n')

if __name__=='__main__':response()
