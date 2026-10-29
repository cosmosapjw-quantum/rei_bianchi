#!/usr/bin/env python3
"""Saved-array-only log-log presentation. Execute only through bounded wrapper."""
import argparse,bisect,csv,json,math,subprocess,resource,signal
from pathlib import Path
from vector_plot import Canvas,panel,COLORS,save_bundle
MYR=31557600000000.
CASES=['OFF_base','ON_base','ON_refined']
STYLES={'OFF_base':[5,2],'ON_base':[1.2,2],'ON_refined':[]}
LABELS=['n','H I','H II','D I','D II','T I','T II','3He I','3He II','3He III','4He I','4He II','4He III','7Li I','7Li II','7Li III','7Li IV']

def limits(series,x,xlim=None):
    vals=[v for s in series for t,v in zip(x,s['y']) if t>0 and v>0 and (xlim is None or xlim[0]<=t<=xlim[1])]
    if not vals:raise ValueError('No positive saved samples')
    lo=10**math.floor(math.log10(min(vals)));hi=10**math.ceil(math.log10(max(vals)))
    return lo,hi if hi>lo else lo*10

def top_ticks(x,eta,xlim):
    candidates=[(x[1],'~20')]
    for z in [19,15,10,5,2]:
        e=math.log(21/(1+z));j=bisect.bisect_left(eta,e)
        if 0<j<len(x):
            u=(e-eta[j-1])/(eta[j]-eta[j-1]);candidates.append((x[j-1]+u*(x[j]-x[j-1]),str(z)))
    selected=[];last=-1e99
    for t,label in sorted(candidates):
        if xlim[0]<=t<=xlim[1]:
            pos=math.log10(t/xlim[0])/math.log10(xlim[1]/xlim[0])*426
            if pos-last>=32:selected.append((t,label));last=pos
    return selected

def main():
    ap=argparse.ArgumentParser();ap.add_argument('data');ap.add_argument('out');a=ap.parse_args()
    d=json.loads(Path(a.data).read_text());o=Path(a.out);o.mkdir(parents=True,exist_ok=True)
    x=d['t_myr'];cases=d['cases'];ref=cases['ON_refined']['physical'];meta=[];canvases=[]
    assert len(x)==361 and all(len(v)==361 for c in cases.values() for v in c['physical'])
    def ser(ids,values):return [dict(label=LABELS[i],y=values[i],color=COLORS[i],dash=[]) for i in ids]
    common=['t = 0, z = 20 omitted on log axes; initial values in initial_values.csv.','Saved samples joined directly; no floor, smoothing, resampling or new IVP.']
    def render(stem,ss,title,ylabel,notes=(),xlim=None,signed=False):
        xlim=xlim or (x[1],x[-1]);lim=limits([dict(y=[abs(v) for v in s['y']]) for s in ss] if signed else ss,x,xlim)
        rows=math.ceil(len(ss)/4); height=(665 if signed else 365)+rows*14+12*(len(notes)+len(common))
        c=Canvas(183/25.4*72,height);panels=[]
        if signed:
            for sign,top in [(1,64),(-1,350)]:
                transformed=[dict(s,y=[v*sign if v*sign>0 else 0 for v in s['y']]) for s in ss]
                panels.append(panel(c,(69,top,426,200),x,transformed,title+(' | positive values' if sign==1 else ' | negative values: magnitude'),ylabel+' (magnitude)','log','log',lim,top_ticks(x,d['eta'],xlim),xlim,sign==-1))
            yy=350+200+49+rows*14
        else:
            panels.append(panel(c,(69,64,426,220),x,ss,title,ylabel,'log','log',lim,top_ticks(x,d['eta'],xlim),xlim));yy=284+49+rows*14
        for note in list(notes)+common:c.text(69,yy,note,8);yy+=12
        c.save(o/stem);canvases.append(c)
        counts=[dict(label=s['label'],zero_indices=[i for i,v in enumerate(s['y']) if v==0],positive_count=sum(v>0 for v in s['y']),negative_count=sum(v<0 for v in s['y'])) for s in ss]
        meta.append(dict(stem=stem,panels=panels,sign_policy='positive upper; negative magnitude lower; shared y limits' if signed else 'positive saved quantities',raw_counts=counts))
    mult=[1e22,1,1,1e4,1e4,1e18,1e18,1e4,1e4,1e4,10,10,10,1e9,1e9,1e9,1e9]
    overview=ser(range(17),[[v*mult[i] for v in ref[i]] for i in range(17)])
    for i,s in enumerate(overview):s['label']+=' x%g'%mult[i]
    render('01_all17_ON_refined',overview,'All 17 states: ON_refined','Number abundance / Href x multiplier',['Fixed isotope multipliers in legend; all positive saved t > 0 values included.'])
    for j,g in enumerate(d['groups'],1):
        ss=[dict(label=LABELS[i]+' '+case.replace('_base','').replace('_refined',' ref'),y=cases[case]['physical'][i],color=COLORS[i],dash=STYLES[case]) for i in g['indices'] for case in CASES]
        render('02_group_%d'%j,ss,'Abundance band: '+g['name'].replace('≥','>=').replace('≤','<='),'Number abundance / Href',['OFF dashed; ON_base dotted; ON_refined solid. Full saved positive range.'])
    scales=cases['ON_refined']['scales'];response=[[v/scales[i] for v in d['delta_on_off'][i]] for i in range(17)]
    render('03_source_response',ser(range(17),response),'Source response: ON_base - OFF_base','Abundance difference / frozen scale',['Panel sign retains signed response; zeros listed in metadata.'],signed=True)
    render('04_refinement',ser(range(17),d['signed_refinement']),'Refinement: ON_base - ON_refined','Abundance difference / frozen scale',['Two resolutions only; acceptance max magnitude / scale <= 1e-5.'],signed=True)
    early=(x[1],max(t for t in x if 0<t<=1e-3))
    for stem,ids,title in [('05_initial_transient',[0,5,6],'Initial n and T transient'),('07_initial_helium',[7,8,9,10,11,12],'Initial helium charge states'),('08_initial_lithium',[13,14,15,16],'Initial lithium charge states')]:
        render(stem,ser(ids,ref),title+': ON_refined','Number abundance / Href',['Early saved evolution at mean z approximately 20.'],xlim=early)
    threshold=1.0820350005000101e-8
    ss=[dict(label=case+' '+tag,y=[v/threshold for v in cases[case][key]],color=color,dash=STYLES[case]) for case in CASES for key,tag,color in [('baryon_residual','baryon',COLORS[1]),('charge_residual','charge',COLORS[2])]]
    render('06_conservation',ss,'Open-system conservation residuals','Residual / absolute threshold',['Baryon plus external ledger; heavy charge minus electron ledger.','Threshold = 1.0820350005000101e-8 particles / Href; initial values removed.'],signed=True)
    with (o/'initial_values.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['case','state','t_s','z','initial_abundance_per_Href'])
        for case in CASES:
            for i,label in enumerate(LABELS):w.writerow([case,label,d['t_s'][0],21*math.exp(-d['eta'][0])-1,cases[case]['physical'][i][0]])
    # Preserve all signed values, including t=0 and exact zero positions.
    with (o/'signed_values.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['quantity','state_or_case','index','t_s','signed_value'])
        for quantity,values in [('source_response_scaled',response),('refinement_scaled',d['signed_refinement'])]:
            for i,arr in enumerate(values):
                for j,v in enumerate(arr):w.writerow([quantity,LABELS[i],j,d['t_s'][j],v])
        for s in ss:
            for j,v in enumerate(s['y']):w.writerow(['conservation_threshold_units',s['label'],j,d['t_s'][j],v])
    (o/'FIGURE_METADATA.json').write_text(json.dumps(dict(figures=meta,state_colors=dict(zip(LABELS,COLORS)),case_styles=STYLES,sample_policy='All saved points; t=0 separate; nonpositive values not placed on log axes; signed magnitudes in paired panels; raw zeros retained.',clock='Myr = 31557600000000 s; z = 21 exp(-eta)-1; top ticks invert saved eta(t)',page_count=len(meta)),indent=2)+'\n')
    save_bundle(canvases,o/'scientific_loglog_figure_set.pdf')
    used=resource.getrusage(resource.RUSAGE_SELF); remaining=3.40-used.ru_utime-used.ru_stime
    if remaining<=0:raise TimeoutError('No remaining raster CPU allowance')
    def raster_limit():
        signal.signal(signal.SIGPROF,signal.SIG_DFL);signal.setitimer(signal.ITIMER_PROF,remaining)
    subprocess.run(['/usr/bin/pdftocairo','-png','-r','90',str(o/'scientific_loglog_figure_set.pdf'),str(o/'preview')],check=True,timeout=45,preexec_fn=raster_limit)
    u=resource.getrusage(resource.RUSAGE_SELF);ch=resource.getrusage(resource.RUSAGE_CHILDREN)
    remaining=3.45-u.ru_utime-u.ru_stime-ch.ru_utime-ch.ru_stime
    if remaining<=0:raise TimeoutError("Combined rendering allowance exhausted")
    signal.setitimer(signal.ITIMER_PROF,remaining)
    for i,f in enumerate(meta,1):
        p=o/('preview-%02d.png'%i)
        if not p.exists():p=o/('preview-%d.png'%i)
        p.rename(o/(f['stem']+'.png'))
    assert len(meta)==12
if __name__=='__main__':main()
