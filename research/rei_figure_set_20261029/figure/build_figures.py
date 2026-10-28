#!/usr/bin/env python3
"""Render frozen saved-history figure inventory; run only inside CPU wrapper."""
import argparse, bisect, json, math, resource, time, subprocess, signal
from pathlib import Path
from vector_plot import Canvas, panel, COLORS, save_bundle

MYR=31557600000000.
CASES=['OFF_base','ON_base','ON_refined']
STYLES={'OFF_base':[5,2],'ON_base':[1.2,2],'ON_refined':[]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('data');ap.add_argument('out');a=ap.parse_args()
    d=json.loads(Path(a.data).read_text());out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    x=d['t_myr'];eta=d['eta'];labels=['n','H I','H II','D I','D II','T I','T II','3He I','3He II','3He III','4He I','4He II','4He III','7Li I','7Li II','7Li III','7Li IV'];cases=d['cases'];ref=cases['ON_refined']['physical'];meta=[];canvases=[]
    def interp(xx,xs,ys):
        j=max(1,min(len(xs)-1,bisect.bisect_left(xs,xx)));u=(xx-xs[j-1])/(xs[j]-xs[j-1]);return ys[j-1]+u*(ys[j]-ys[j-1])
    def zticks(log=False):
        if log:return [(x[1],'%g'%(21*math.exp(-eta[1])-1)),(x[-1],'%g'%(21*math.exp(-eta[-1])-1))]
        return [(interp(math.log(21/(1+z)),eta,x),str(z)) for z in [20,15,10,5,2] if eta[0]<=math.log(21/(1+z))<=eta[-1]+1e-14]
    def ser(indices,values):return [{'label':labels[i],'y':values[i],'color':COLORS[i],'dash':[]} for i in indices]
    def render(stem,ss,title,ylabel,logy=False,logx=False,ylim=None,xlim=None,notes=(),top=None):
        # 183 mm wide at native scale; 9 pt axes, 8 pt legend.
        notes=list(notes)+['Source: saved pilot17_populations.csv and three-case NPZ arrays.']
        cols=min(4,len(ss));rows=math.ceil(len(ss)/cols);height=350+rows*14+len(notes)*12
        c=Canvas(520,height)
        info=panel(c,(69,64,426,220),x,ss,title,ylabel,'log' if logy else 'linear','log' if logx else 'linear',ylim,zticks(logx) if top is None else [],xlim,True,toplabel=top or 'Mean redshift, z')
        yy=284+49+rows*14
        for text in notes:c.text(69,yy,text,8);yy+=12
        c.save(out/stem);info['stem']=stem;meta.append(info);canvases.append(c)
    multipliers=[1e22,1,1,1e4,1e4,1e18,1e18,1e4,1e4,1e4,10,10,10,1e9,1e9,1e9,1e9]
    overview=ser(range(17),[[v*multipliers[i] for v in ref[i]] for i in range(17)])
    for i,s in enumerate(overview):s['label']+=' x%g'%multipliers[i]
    render('01_all17_ON_refined',overview,'(a) All 17 states: ON_refined','Number abundance / Href x stated isotope multiplier',True,True,ylim=(1e-8,2),notes=['Fixed isotope multipliers appear in legend; y window = 1e-8 to 2.','Positive offscale counts by state are in FIGURE_METADATA.json.','t = 0 and nonpositive samples omitted; unscaled traces in grouped views.'])
    peaks=d['peaks']
    groups=[]
    for j,g in enumerate(d['groups']):
        name=g['name'].replace('\u2265','>=').replace('\u2264','<=');ids=g['indices']
        ss=[]
        for i in ids:
            for case in CASES:ss.append({'label':labels[i]+' '+case.replace('_base','').replace('_refined',' ref'),'y':cases[case]['physical'][i],'color':COLORS[i],'dash':STYLES[case]})
        window=[v for s in ss for tt,v in zip(x,s['y']) if tt>=1 and v>0]
        ywindow=(10**math.floor(math.log10(min(window))),10**math.ceil(math.log10(max(window))))
        render('02_group_%d'%(j+1),ss,'(%s) Abundance band: %s'%(chr(98+j),name),'Number abundance (particles / Href)',True,ylim=ywindow,notes=['OFF dashed; ON_base dotted; ON_refined solid. State colors match overview.','Y limits: positive samples at t >= 1 Myr, rounded outward to decades.','Full time span retained; offscale counts per curve in FIGURE_METADATA.json.','Early source-onset evolution is resolved in figure (i).'])
        groups.append({'band':name,'indices':ids,'labels':[labels[i] for i in ids],'peaks':[peaks[i] for i in ids]})
    # Signed responses use frozen state scales, keeping trace-species response visible.
    scales=cases['ON_refined']['scales']
    response=[[v/scales[i] for v in d['delta_on_off'][i]] for i in range(17)]
    render('03_source_response',ser(range(17),response),'(%s) Source response: ON_base - OFF_base'%chr(98+len(groups)),'Signed abundance difference / frozen scale',notes=['Full configured source switch, including external escape; zero retained.'])
    render('04_refinement',ser(range(17),d['signed_refinement']),'(%s) Refinement: ON_base - ON_refined'%chr(99+len(groups)),'Signed abundance difference / frozen scale',notes=['Two-resolution agreement only; acceptance max |difference / scale| <= 1e-5.'])
    # Saved early transient window: through 1e-3 Myr, with no extra samples.
    early_end=max(v for v in x if 0<v<=1e-3)
    render('05_initial_transient',ser([0,5,6],ref),'(%s) Initial transient: ON_refined'%chr(100+len(groups)),'Number abundance (particles / Href)',True,True,xlim=(x[1],early_end),top='Mean z approximately 20 over this interval',notes=['Source onset is t = 0; n, T I and T II begin at zero.','Positive saved samples only; no time relocation or abundance floor.'])
    threshold=1.0820350005000101e-8
    ss=[]
    for k,case in enumerate(CASES):
        for key,tag,color in [('baryon_residual','baryon',COLORS[1]),('charge_residual','charge',COLORS[2])]:
            ss.append({'label':case+' '+tag,'y':[v/threshold for v in cases[case][key]],'color':color,'dash':STYLES[case]})
    render('06_conservation',ss,'(%s) Signed open-system conservation residuals'%chr(101+len(groups)),'Residual / absolute acceptance threshold',notes=['Baryon + external ledger; heavy charge - electron ledger; initial values removed.','Original absolute threshold = 1.0820350005000101e-8 particles / Href.'])
    (out/'FIGURE_METADATA.json').write_text(json.dumps({'figures':meta,'groups':groups,'case_styles':STYLES,'state_colors':dict(zip(labels,COLORS)),'data_source':'rei_source_history_20261028/outputs/pilot17_populations.csv; saved OFF_base, ON_base, ON_refined NPZ physical arrays and frozen scales; diagnostics export plot_data.json.','sample_policy':'All supplied samples; straight lines only; log axes omit nonpositive points; no floor, smoothing, resampling or new IVP.','clock':'Saved t and eta; Myr=31557600000000 s; z=21 exp(-eta)-1; top ticks invert saved eta(t).'},indent=2)+'\n')
    def checkpoint(stage,previews):
        u=resource.getrusage(resource.RUSAGE_SELF)
        (out/'RENDER_PROGRESS.json').write_text(json.dumps({'stage':stage,'vector_figures':len(meta),'previews':previews,'process_cpu_s':u.ru_utime+u.ru_stime,'monotonic_s':time.monotonic()},indent=2)+'\n')
    checkpoint('VECTORS_COMPLETE_PREVIEWS_PENDING',[])
    # One native vector bundle and one Poppler startup, using identical streams.
    save_bundle(canvases,out/'scientific_figure_set.pdf')
    checkpoint('VECTORS_AND_BUNDLE_COMPLETE_PREVIEWS_PENDING',[])
    u=resource.getrusage(resource.RUSAGE_SELF);child_allowance=max(.001,.30-u.ru_utime-u.ru_stime)
    (out/'RASTER_BUDGET.json').write_text(json.dumps({'child_allowance_s':child_allowance,'combined_ceiling_s':.31,'preview_antialias':'none','vector_streams':'unchanged by rasterization'})+'\n')
    def child_budget():signal.signal(signal.SIGPROF,signal.SIG_DFL);signal.setitimer(signal.ITIMER_PROF,child_allowance)
    result=subprocess.run(['/usr/bin/pdftocairo','-png','-r','72','-antialias','none',str(out/'scientific_figure_set.pdf'),str(out/'preview')],preexec_fn=child_budget,timeout=15)
    u=resource.getrusage(resource.RUSAGE_SELF);cu=resource.getrusage(resource.RUSAGE_CHILDREN);remaining=.31-u.ru_utime-u.ru_stime-cu.ru_utime-cu.ru_stime
    if remaining<=0:raise TimeoutError('Combined 0.31 CPU-second repair ceiling exhausted after raster child')
    signal.setitimer(signal.ITIMER_PROF,remaining)
    if result.returncode:raise RuntimeError('pdftocairo failed or exhausted adaptive child CPU ceiling: '+str(result.returncode))
    previews=[]
    for i,info in enumerate(meta,1):
        source=out/('preview-%02d.png'%i)
        if not source.exists():source=out/('preview-%d.png'%i)
        source.rename(out/(info['stem']+'.png'));previews.append(info['stem']+'.png')
    checkpoint('VECTORS_AND_PREVIEWS_COMPLETE',previews)
    print(json.dumps({'status':'written','figures':len(meta),'formats':['svg','pdf']}))

if __name__=='__main__':main()
