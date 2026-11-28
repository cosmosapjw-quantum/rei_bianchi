#!/usr/bin/env python3
"""Render the saved new HE38 finite-mass diagnostic; no model evaluation."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ.setdefault(key,'1')
import argparse, datetime, hashlib, json, pathlib, resource, shutil, sys, time, traceback

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt',type=pathlib.Path,required=True)
    args=parser.parse_args();attempt=args.attempt.resolve()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=attempt/'plots'/('render_'+stamp);out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'render_diagnostic.py')
    begin=time.perf_counter();cpu=time.process_time();code=0
    receipt={'schema':'he38.finite_mass_render.v1','command':[sys.executable,*sys.argv],
      'code_sha256':sha(__file__),'input_csv_sha256':sha(attempt/'finite_mass_moments.csv'),
      'input_metrics_sha256':sha(attempt/'METRICS.json'),'started_utc':stamp,
      'new_api_evaluations':0,'new_scientific_figure_pairs':1,'old_renders_replayed':0,
      'design_width_mm':180,'design_height_mm':150,'raster_dpi':300,'correction_attempt':False}
    dump(out/'START.json',receipt)
    try:
      import numpy as np
      import matplotlib
      matplotlib.use('Agg')
      import matplotlib.pyplot as plt
      from matplotlib.ticker import FixedLocator,FuncFormatter
      data=np.genfromtxt(attempt/'finite_mass_moments.csv',delimiter=',',names=True)
      T=data['temperature_K'];colors={'e':'#0072B2','H':'#D55E00','p':'#009E73'}
      labels={'e':'Electron','H':'Neutral H','p':'Proton'}
      plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9.5,
        'axes.titlesize':10,'legend.fontsize':8,'xtick.labelsize':8,'ytick.labelsize':8,
        'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none',
        'savefig.facecolor':'white','axes.linewidth':0.7,'lines.linewidth':1.65})
      fig,axs=plt.subplots(2,2,figsize=(180/25.4,150/25.4),layout='constrained')
      fig.set_constrained_layout_pads(w_pad=.06,h_pad=.07,wspace=.06,hspace=.07)
      for ax in axs.flat:
        ax.set_xscale('log');ax.set_xlim(T[0],T[-1]);ax.set_xlabel('Temperature (K)')
        ax.xaxis.set_major_locator(FixedLocator([2000,10000,50000,200000]))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v/1000:g}k'))
        ax.tick_params(which='minor',bottom=False)
        ax.grid(True,which='major',color='#d4d9de',linewidth=.55,alpha=.8)
        ax.axhline(0,color='#7e8790',linewidth=.65,zorder=1)
      ax=axs[0,0];ax.set_title('(a) Kinetic energy per event',loc='left',pad=9)
      for name in ['e','H','p']:
        ax.plot(T,data['Q_'+name+'_per_event_eV'],color=colors[name],label=labels[name])
      ax.set_ylabel(r'$Q_s/r$ (eV)');ax.set_ylim(-29,29)
      ax.legend(loc='upper left',frameon=False,handlelength=2)
      ax.text(.96,.06,r'$\sum_s Q_s/r=-13.6$ eV',transform=ax.transAxes,ha='right',fontsize=8.5,
        bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':2})
      ax=axs[0,1];ax.set_title('(b) Finite-mass energy shift',loc='left',pad=9)
      ax.plot(T,1e3*data['electron_shift_from_minus_I_eV'],color=colors['e'],label=r'Electron: $Q_e/r+I$')
      ax.plot(T,1e3*data['Q_heavy_per_event_eV'],color=colors['H'],label=r'Heavy: $(Q_H+Q_p)/r$')
      ax.set_ylabel('Energy shift per event (meV)');ax.set_ylim(-24,24)
      ax.legend(loc='upper left',frameon=False,handlelength=2)
      for j,inp in enumerate(['e','H']):
        ax=axs[1,j];title='electron' if inp=='e' else 'neutral H'
        ax.set_title(f'({"c" if j==0 else "d"}) Incoming {title} stress',loc='left',pad=9)
        for name in ['e','H','p']:
          ax.plot(T,data['STF_'+name+'_from_'+inp+'_over_alpha'],color=colors[name],label=labels[name])
        ax.set_yscale('symlog',linthresh=2e-4,linscale=.7)
        ax.set_ylabel(r'Coefficient $\mathcal{M}_{s,'+inp+r'}/\alpha$')
        ax.legend(loc='lower right',frameon=True,facecolor='white',edgecolor='none',framealpha=.9,handlelength=2)
      axs[1,0].set_ylim(-3000,.003)
      axs[1,1].set_ylim(-2,2)
      fig.suptitle('H1 ionization: finite-mass energy and stress allocation',fontsize=11,y=1.015)
      png=out/'finite_mass_energy_stress.png';svg=out/'finite_mass_energy_stress.svg'
      fig.savefig(png,dpi=300);fig.savefig(svg)
      plt.close(fig)
      receipt.update(status='PASS_SCOPED',matplotlib=matplotlib.__version__,numpy=np.__version__,
        files={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in [png,svg]},
        science_scope='Original LC Jacobi uniform-direction model; common T/bulk infinitesimal independent incoming e/H stress. Signed instantaneous sources; positive proton heat is product birth.',
        normalization='STF coefficients exclude density factors: multiply incoming-e column by nH, incoming-H column by ne. Both axes use symlog, not a dual-axis plot.',
        visual_inspection='PENDING_INDEPENDENT_REVIEW')
    except Exception as exc:
      code=1;receipt.update(status='FAIL',failure={'type':type(exc).__name__,'message':str(exc)})
      (out/'stderr.txt').write_text(traceback.format_exc());traceback.print_exc()
    receipt.update(exit_code=code,wall_seconds=time.perf_counter()-begin,cpu_seconds=time.process_time()-cpu,
      peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    dump(out/'RENDER_RECEIPT.json',receipt)
    dump(attempt/'LATEST_RENDER.json',{'render':str(out.relative_to(attempt)),'receipt_sha256':sha(out/'RENDER_RECEIPT.json'),'status':receipt['status']})
    result=json.dumps({'status':receipt['status'],'plot_directory':str(out),'cpu_seconds':receipt['cpu_seconds'],'peak_RSS_KiB':receipt['peak_RSS_KiB'],'files':receipt.get('files',{})})
    (out/'stdout.txt').write_text(result+'\n')
    if not (out/'stderr.txt').exists():(out/'stderr.txt').write_text('')
    print(result);return code
if __name__=='__main__':sys.exit(main())
