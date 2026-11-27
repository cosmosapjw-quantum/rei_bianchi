"""One saved-only HARMONIC10 four-panel render; no science import or call."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

p=argparse.ArgumentParser();p.add_argument('--saved-json',required=True);p.add_argument('--output',required=True);a=p.parse_args()
start_cpu,start_wall=time.process_time(),time.perf_counter()
source=Path(a.saved_json).resolve();raw=source.read_bytes();data=json.loads(raw)
out=Path(a.output).resolve()
if not out.is_dir():raise SystemExit('bounded runner must create output directory')
if (out/'HARMONIC10.png').exists() or (out/'HARMONIC10.svg').exists():raise SystemExit('one render only; output exists')
cache=Path(os.environ.get('MPLCONFIGDIR',str(Path.home()/'.config/matplotlib')))
font_cache_before=sorted(p.name for p in cache.glob('fontlist-*.json')) if cache.exists() else []
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
fig.suptitle('HARMONIC10 · Declared second-harmonic paired measure',fontsize=16,weight='bold')
ax=axes[0,0];scan=data['rotation_scan']
x=[r['display_a'] for r in scan];y=[r['coincidence']['display_lower'] for r in scan];up=[r['coincidence']['display_upper'] for r in scan]
ax.plot(x,[r['display_oracle'] for r in scan],color='#394867',label='independent closed form')
ax.errorbar(x,[(l+h)/2 for l,h in zip(y,up)],yerr=[(h-l)/2 for l,h in zip(y,up)],fmt='o',ms=4,color='#de7c37',label='certified event enclosure')
ax.set(xlabel='Detector orientation a (turns)',ylabel='Coincidence measure Y',title='A · Beam law fixes the orientation dependence',xlim=(0,1));ax.legend(fontsize=8);ax.grid(alpha=.2)
ax=axes[0,1];case=next(r for r in data['nonseparable'] if r['case']=='forward_backward');actual=case['actual']
vals=[(actual['display_lower']+actual['display_upper'])/2,case['oracle'],case['naive_global_marginal']]
ax.bar(['Certified','Independent\noracle','Global marginal\ndiagnostic'],vals,color=['#de7c37','#394867','#a9b2bd'],width=.62)
ax.errorbar([0],[vals[0]],yerr=[(actual['display_upper']-actual['display_lower'])/2],fmt='none',ecolor='black',capsize=4)
ax.set(ylabel='Coincidence measure Y',title='B · Nonseparable polar–azimuth dependence');ax.grid(axis='y',alpha=.2)
ax=axes[1,0];native=data['native_rows'];energies=[r['energy_MeV'] for r in native]
yields=[(r['coincidence']['display_lower']+r['coincidence']['display_upper'])/2 for r in native]
ax.plot(energies,yields,'o-',color='#394867',label='coincidence measure Y');ax.set(xlabel='Incident photon energy (MeV)',ylabel='Coincidence measure Y',title='C · Native stored masses, manufactured angular law')
right=ax.twinx();right.spines['right'].set_visible(True)
right.plot(energies,[(r['pair_energy_MeV']['display_lower']+r['pair_energy_MeV']['display_upper'])/2 for r in native],'s--',color='#de7c37',label='selected pair total energy')
right.set_ylabel('Selected pair total energy (MeV)');lines=ax.lines+right.lines;ax.legend(lines,[l.get_label() for l in lines],fontsize=8,loc='upper left');ax.grid(alpha=.2)
ax=axes[1,1];widths=data['width_rows'];xx=range(len(widths))
for key,label,marker,color in [('actual_width','actual enclosure width','o','#394867'),('polar_bound','polar bound','s','#de7c37'),('arithmetic_bound','arithmetic contribution','^','#4b997a')]:
 ax.plot(list(xx),[r[key] for r in widths],marker=marker,color=color,label=label)
ax.set_yscale('symlog',linthresh=1e-28);ax.set_xticks(list(xx),[r['case'] for r in widths]);ax.set(ylabel='Absolute measure width (symlog)',title='D · Observed polar and rational arithmetic widths');ax.legend(fontsize=8);ax.grid(alpha=.2)
fig.text(.5,.002,'Rest energy is included. Manufactured law; exact stored masses; measurement uncertainty is outside this declared calculation.',ha='center',fontsize=8,color='#525963')
fig.savefig(out/'HARMONIC10.png',dpi=150)
fig.savefig(out/'HARMONIC10.svg')
plt.close(fig)
receipt={'schema':'HARMONIC10_SAVED_ONLY_PLOT_V1','saved_json':str(source),'saved_json_sha256':hashlib.sha256(raw).hexdigest(),'scientific_imports':[],'scientific_calls':0,'render_attempt':1,'panels':4,'font_cache_before':font_cache_before,'font_cache_state':'warm' if font_cache_before else 'cold','MPLCONFIGDIR':str(cache),'matplotlib_version':matplotlib.__version__,'own_cpu_s':time.process_time()-start_cpu,'own_wall_s':time.perf_counter()-start_wall,'output_files':{name:{'size':(out/name).stat().st_size,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()} for name in ('HARMONIC10.png','HARMONIC10.svg')}}
with (out/'PLOT_RECEIPT.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(receipt))
