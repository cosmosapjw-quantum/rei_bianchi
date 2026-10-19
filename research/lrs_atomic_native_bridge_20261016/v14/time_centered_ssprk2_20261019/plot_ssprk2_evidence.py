#!/usr/bin/env python3
"""Plot actual raw refinement differences. Reference slopes are guides, not fits."""
from pathlib import Path
import csv,json,hashlib,argparse,os,gzip,io
os.environ.setdefault("MPLCONFIGDIR",str(Path("/tmp")/"rei_ssprk_matplotlib"))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 p=argparse.ArgumentParser();p.add_argument('--work-root',type=Path,default=Path(__file__).resolve().parent.parent);a=p.parse_args();w=a.work_root;out=Path(__file__).resolve().parent/'figures';out.mkdir(exist_ok=True)
 base=w if(w/'execution_transport').exists()else w/'evidence'
 paths=[base/'execution_transport/ssprk_transport.csv',base/'execution_coupled/fixed_geometry.csv',base/'execution_coupled/birth_histories.csv'];raw=lambda p:p.read_bytes()if p.is_file()else gzip.decompress(Path(str(p)+'.gz').read_bytes())
 ar=list(csv.DictReader(io.StringIO(raw(paths[0]).decode())));br=list(csv.DictReader(io.StringIO(raw(paths[1]).decode())));cr=list(csv.DictReader(io.StringIO(raw(paths[2]).decode())));points={}
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'legend.fontsize':8,'pdf.fonttype':42})
 fig,axs=plt.subplots(2,2,figsize=(12,9));colors=['#1d5e91','#c45a24','#527d39','#8b5fa3']
 def curve(ax,label,x,y,color,marker='o'):
  ax.loglog(x,y,marker=marker,ms=4,lw=1.3,color=color,label=label);points[label]={'x':x,'y':y}
 def guide(ax,x0,y0,power):
  x=[x0/2,x0,x0*2];y=[y0*(v/x0)**power for v in x];ax.loglog(x,y,'--',color='#777777',lw=1,label=f'slope {power} guide')
 ax=axs[0,0]
 for j,cells in enumerate([8,16,32,64]):
  rs=[r for r in ar if r['kind']=='pair'and r['spectrum']=='md14_broad'and int(r['cells'])==cells];x=[float(r['theta'])for r in rs];y=[float(r['cell_N_L1_normalized'])for r in rs];curve(ax,f'A local, cells {cells}',x,y,colors[j])
 guide(ax,x[-2],y[-2]*0.55,3);ax.set(title='A · broad native moments: local pair difference',xlabel=r'$\theta=k_{20}h$',ylabel=r'$\|N_{h/2,h/2}-N_h\|_1/N_0$')
 ax=axs[0,1];rs=[r for r in ar if r['kind']=='history'and r['spectrum']=='md14_broad'];vals=[float(r['result_N'])for r in rs];x=[1/float(r['m'])for r in rs[:-1]];y=[abs(vals[j]-vals[j+1])/float(rs[0]['initial_N'])for j in range(len(vals)-1)];curve(ax,'A global photon N',x,y,colors[0]);guide(ax,x[-2],y[-2]*0.55,2);ax.set(title='A · broad fixed-total-time self differences',xlabel=r'$1/m$',ylabel=r'$|N_m-N_{2m}|/N_0$')
 ax=axs[1,0];rs=[r for r in br if float(r['is_final'])==1]
 for j,(field,label)in enumerate([('final_HII','B fixed HII'),('final_w_eV_H','B fixed thermal w'),('final_T_K','B fixed temperature')]):
  vals=[float(r[field])for r in rs];x=[1/float(r['m'])for r in rs[:-1]];y=[abs(vals[i]-vals[i+1])/abs(vals[-1])for i in range(len(vals)-1)];curve(ax,label,x,y,colors[j])
 guide(ax,x[-2],y[-2]*0.55,2);ax.set(title='B · seeded, evolving gas at fixed geometry',xlabel=r'$1/m$',ylabel='successive difference / finest |observable|')
 ax=axs[1,1];rs=[r for r in cr if r['kind']=='physical_gl2'and float(r['is_final'])==1]
 for j,(field,label)in enumerate([('final_active_N','B GL2 photon N'),('photo_heat','B GL2 photo heat'),('final_w_eV_H','B GL2 thermal w'),('final_T_K','B GL2 temperature')]):
  vals=[float(r[field])for r in rs];x=[1/float(r['m'])for r in rs[:-1]];y=[abs(vals[i]-vals[i+1])/abs(vals[-1])for i in range(len(vals)-1)];curve(ax,label,x,y,colors[j])
 guide(ax,x[-2],y[-2]*0.55,2);ax.set(title='B · source GL2, stable interval clock',xlabel=r'$1/N$',ylabel='successive difference / finest |observable|')
 for ax in axs.flat:ax.grid(True,which='major',alpha=.22);ax.legend(loc='best',frameon=False)
 fig.suptitle('Native SSPRK(2,2) evidence · actual raw refinement differences',fontsize=14,y=.985)
 fig.text(.5,.025,'Guides are not fitted orders. Smooth finite cases only; source-on HeIII changes remain near the numerical floor.\nB uses the corrected stable ln1p clock; no unconditional, stiff, full-EoR, Case-B or signed-Bianchi claim.',ha='center',fontsize=9,color='#444444')
 fig.tight_layout(rect=[0,.075,1,.965]);fig.savefig(out/'ssprk2_refinement.png',dpi=200);fig.savefig(out/'ssprk2_refinement.pdf');plt.close(fig)
 evidence={'schema':'rei.v15.refinement_plot.1','raw_inputs':{str(p.relative_to(w)):{'sha256':hashlib.sha256(raw(p)).hexdigest(),'bytes':len(raw(p))}for p in paths},'points':points,'guides':'slope2/3 reference lines only, no fitted claims','normalization':'A uses initial photonN; B uses absolute finest value of each observable','source_on_tiny_floor':'HeIII excluded from panel because refinements are near numerical floor','new_native_runs':0}
 (out/'PLOT_DATA.json').write_text(json.dumps(evidence,indent=2)+'\n');print(out)
if __name__=='__main__':main()
