#!/usr/bin/env python3
"""Analyze only the prescribed native fixed-gas projection matrix; never runs native code."""
from pathlib import Path
import argparse, csv, hashlib, json, math
CELLS=(8,16,32,64)
SPECTRA=('md14_broad','delta60')
THETA=(.8,.4,.2,.1,.05,.025)
MS=(1,2,4,8,16,32,64)
OBS=('N','U','photo_HI','photo_HeI','photo_HeII','binding','heat')
EXPECTED_NATIVE={
'rust/rei_microphysics/src/axbi_driver.rs':'fd5b040bceb2134dc92c09f4bf49e6b04be2e8115f553c19fe989f472f32c01d',
'rust/rei_microphysics/src/axbi_physical_birth.rs':'3de9ca2dc4a442cb6d4d7fa6eaeb0f993ffc634d6ffdeb2b9410faec38fee0fa',
'rust/rei_microphysics/examples/v14_physical_birth_sweep.rs':'192f68282cf072874c86369ad51e9b71f227e72eff61dbb944051231eed6015c',
'rust/rei_microphysics/tests/v14_physical_birth.rs':'8c368cf35866bd7fe317515a9f1a31bc97cc7340bfd2ed799edf3047cbfd7af7'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ulp_floor(*xs):return 64*max(math.ulp(float(x)) for x in xs)
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--csv',required=True,type=Path)
    a.add_argument('--identity',required=True,type=Path,help='Native V14_RESTORE_RECEIPT.json')
    a.add_argument('--native-root',type=Path)
    a.add_argument('--source',required=True,type=Path)
    a.add_argument('--out',required=True,type=Path)
    a.add_argument('--figures',type=Path,help='Optional PNG and PDF plot directory; requires matplotlib')
    args=a.parse_args()
    receipt=json.loads(args.identity.read_text())
    if receipt.get('schema')!='rei.v14.restore.1' or receipt.get('parent_sha')!='7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e':
        raise ValueError('Unexpected native V14 identity')
    if receipt.get('sha256')!=EXPECTED_NATIVE:raise ValueError('Unexpected native V14 hashes in receipt')
    native=args.native_root or args.identity.parent
    for rel,h in EXPECTED_NATIVE.items():
        if sha(native/rel)!=h:raise ValueError('Native source hash mismatch: '+rel)
    raw=list(csv.DictReader(args.csv.open()))
    rows=[]
    for z in raw:
        r={k:(v if k in ('kind','spectrum') else float(v)) for k,v in z.items()}
        if not all(math.isfinite(v) for v in r.values() if isinstance(v,float)):raise ValueError('Nonfinite CSV')
        if r['cells']!=int(r['cells']) or r['m']!=int(r['m']):raise ValueError('Nonintegral matrix index')
        r['cells']=int(r['cells']);r['m']=int(r['m']);rows.append(r)
    def key(r):return (r['kind'],r['cells'],r['spectrum'],r['theta'],r['m'])
    expected={('pair',c,s,t,2) for c in CELLS for s in SPECTRA for t in THETA}|{('history',16,s,1.,m) for s in SPECTRA for m in MS}
    actual=[key(r) for r in rows]
    if len(rows)!=62 or len(set(actual))!=62 or set(actual)!=expected:
        raise ValueError('Matrix mismatch: '+repr({'rows':len(rows),'missing':sorted(expected-set(actual)),'unexpected':sorted(set(actual)-expected)}))
    pairs=[]
    for c in CELLS:
        for s in SPECTRA:
            rr={r['theta']:r for r in rows if r['kind']=='pair' and r['cells']==c and r['spectrum']==s}
            for obs,field in [('N','cell_N_L1'),('U','cell_U_ref_L1')]:
                for t in THETA[:-1]:
                    r1,r2=rr[t],rr[t/2];v1,v2=r1[field],r2[field]
                    floor1=ulp_floor(r1['initial_'+obs],r1['base_'+obs],r1['result_'+obs])
                    floor2=ulp_floor(r2['initial_'+obs],r2['base_'+obs],r2['result_'+obs])
                    noise=v1<=floor1 or v2<=floor2
                    pairs.append({'cells':c,'spectrum':s,'observable':obs,'theta':t,'theta_half':t/2,
                        'L1':v1,'L1_half':v2,'roundoff_floor':floor1,'roundoff_floor_half':floor2,
                        'roundoff_flag':noise,'local_defect_slope':None if noise else math.log2(v1/v2)})
    histories=[]
    for s in SPECTRA:
        rr={r['m']:r for r in rows if r['kind']=='history' and r['spectrum']==s}
        for obs in OBS:
            for m in MS[:-2]:
                x,y,z=[rr[n]['result_'+obs] for n in (m,2*m,4*m)]
                d1=y-x;d2=z-y;f1=ulp_floor(x,y);f2=ulp_floor(y,z)
                noise=abs(d1)<=f1 or abs(d2)<=f2
                histories.append({'cells':16,'spectrum':s,'observable':obs,'m':m,'m2':2*m,'m4':4*m,
                    'value_m':x,'value_2m':y,'value_4m':z,'signed_difference_m_to_2m':d1,
                    'signed_difference_2m_to_4m':d2,'roundoff_floor_m_to_2m':f1,'roundoff_floor_2m_to_4m':f2,
                    'sign_change':d1*d2<0.,'roundoff_flag':noise,
                    'self_difference_slope':None if noise else math.log2(abs(d1/d2))})
    conservation={}
    for s in SPECTRA:
        rr=[r for r in rows if r['spectrum']==s]
        conservation[s]={obs:{'max_absolute':max(abs(r[p+'_residual_'+obs]) for r in rr for p in ('base','result')),
            'max_normalized_by_initial':max(abs(r[p+'_residual_'+obs])/r['initial_'+obs] for r in rr for p in ('base','result'))} for obs in ('N','U')}
    delta=[r for r in rows if r['spectrum']=='delta60']
    result={'schema':'rei.v14.projection.analysis.1','csv_sha256':sha(args.csv),'diagnostic_source_sha256':sha(args.source),
        'native_identity_receipt_sha256':sha(args.identity),'native_identity':receipt,
        'matrix':{'verified':True,'total_rows':62,'pair_rows':48,'history_rows':14,'all_numeric_finite':True},
        'scope':'Frozen geometry and frozen gas native transport operator only. These are not cosmological histories.',
        'interpretation':'Pair slopes describe a local composition defect. A pair slope approaching 2 is not a claim of global second-order convergence. History slopes describe signed successive native fixed-gas observable differences, not source-on cosmological order.',
        'roundoff_rule':'Null slope if either difference is <=64 times the largest binary64 ulp of its relevant observable endpoints; pair endpoints also include initial inventory. Sign changes are retained independently.',
        'pair_slopes':pairs,'history_self_differences':histories,'native_conservation':conservation,
        'delta_floors':{'max_pair_N_L1_over_initial_N':max(r['cell_N_L1_normalized'] for r in delta if r['kind']=='pair'),
            'max_pair_U_L1_over_initial_U':max(r['cell_U_ref_L1_normalized'] for r in delta if r['kind']=='pair'),
            'max_history_N_L1_over_initial_N':max(r['cell_N_L1_normalized'] for r in delta if r['kind']=='history'),
            'max_history_U_L1_over_initial_U':max(r['cell_U_ref_L1_normalized'] for r in delta if r['kind']=='history')},
        'min_number':min(r[p+'_min_number'] for r in rows for p in ('base','result')),
        'min_normalized_support_slack':min(r[p+'_min_support_slack_normalized'] for r in rows for p in ('base','result')),
        'full_source_on_cosmological_order':'NOT_ESTABLISHED','execution_platform':'NOT_INFERRED_FROM_CSV'}
    if args.figures:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        args.figures.mkdir(parents=True,exist_ok=True)
        fig,ax=plt.subplots(1,2,figsize=(11.4,4.8))
        for c in CELLS:
            rr=sorted((r for r in rows if r['kind']=='pair' and r['spectrum']=='md14_broad' and r['cells']==c),key=lambda r:r['theta'])
            ax[0].loglog([r['theta'] for r in rr],[r['cell_N_L1_normalized'] for r in rr],'o-',label=f'{c} energy cells')
        anchor=next(r['cell_N_L1_normalized'] for r in rows if r['kind']=='pair' and r['cells']==16 and r['spectrum']=='md14_broad' and r['theta']==.025)
        xx=sorted(THETA);ax[0].loglog(xx,[anchor*(x/.025)**2 for x in xx],'k--',label='Slope 2 guide (cells16, θ=.025)')
        ax[0].axhline(result['delta_floors']['max_pair_N_L1_over_initial_N'],color='gray',linestyle=':',label='Maximum delta-control floor')
        ax[0].set(xlabel='θ = k_ref Δt',ylabel='Cell-number L1 difference / initial N',title='One full map versus two half maps')
        hh={r['m']:r for r in rows if r['kind']=='history' and r['spectrum']=='md14_broad'}
        mm=list(MS[:-1]);yy=[abs(hh[2*m]['result_N']-hh[m]['result_N'])/hh[m]['initial_N'] for m in mm]
        ax[1].loglog(mm,yy,'o-',color='#126d70',label='MD14 broad successive difference')
        ax[1].loglog(mm,[yy[-1]*mm[-1]/m for m in mm],'k--',label='Slope −1 guide (last point)')
        dd={r['m']:r for r in rows if r['kind']=='history' and r['spectrum']=='delta60'}
        df=max(abs(dd[2*m]['result_N']-dd[m]['result_N'])/dd[m]['initial_N'] for m in mm)
        ax[1].axhline(df,color='gray',linestyle=':',label='Maximum delta successive floor')
        ax[1].set(xlabel='Number of repeated maps m (total θ = 1)',ylabel='|N(2m) − N(m)| / initial N',title='Frozen broad-spectrum history, 16 cells')
        for x in ax:x.grid(True,which='both',alpha=.2);x.legend(fontsize=7,loc='best')
        fig.text(.5,.015,'Native fixed-gas, fixed-geometry transport operator; not cosmological histories. Dashed lines are labelled slope guides only.',ha='center',fontsize=8)
        fig.tight_layout(rect=(0,.045,1,1))
        for ext in ('png','pdf'):fig.savefig(args.figures/f'projection_diagnostic.{ext}',dpi=180)
        plt.close(fig)
        result['figures']=['projection_diagnostic.png','projection_diagnostic.pdf']
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'ANALYSIS_COMPLETE','rows':len(rows),'output':str(args.out),'delta_floors':result['delta_floors'],'native_conservation':conservation},indent=2))
if __name__=='__main__':main()
