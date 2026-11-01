#!/usr/bin/env python3
"""Second-order exact photon-sharing response of the ORIGINAL REI 26-event source.

This is the fixed-time (tick160), fixed-external-forcing, source-moment submap.
It is NOT a source/parent correlated certificate of the full MPRK/SDIRK D_h map.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,itertools,json,math,sys
from decimal import Decimal,localcontext
from pathlib import Path
import numpy as np

SOURCE_PR=332
BASE_HEAD='2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a'
ORIGINAL_TAR_SHA='a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b'
ORIGINAL_ARRAY_SHA='cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01'
ORIGINAL_KERNEL_SHA='579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644'
NODES=46080
GATE=2e-4
EV_ERG=1.602176634e-12


def shares(a,external):
    a=np.asarray(a,dtype=float)
    if a.shape!=(3,) or np.any(a<0) or external<0: raise ValueError('negative or malformed photon weights')
    den=float(math.fsum([float(external),*map(float,a)]))
    if den<=0 or not math.isfinite(den):raise ValueError('undefined photon denominator')
    return a/den, external/den,den


def jac_hess(p):
    """Exact derivatives of p_s(a exp(l))/D with respect to log neutral moments."""
    p=np.asarray(p,float)
    if p.shape!=(3,) or not np.isfinite(p).all() or np.any(p<0) or np.sum(p)>1+1e-12:
        raise ValueError('invalid photon probability')
    J=np.diag(p)-np.outer(p,p)
    H=np.empty((3,3,3),float)
    for s,t,u in itertools.product(range(3),repeat=3):
        H[s,t,u]=p[s]*((float(s==t)-p[t])*(float(s==u)-p[u])
                  -p[t]*(float(t==u)-p[u]))
    return J,H


def log_fraction_response(a,external,delta):
    delta=np.asarray(delta,float)
    if delta.shape!=(3,) or not np.isfinite(delta).all():raise ValueError('bad source perturbation')
    p,_,den=shares(a,external)
    # Stable exact finite response; avoid subtracting two nearly equal p arrays.
    q=np.expm1(delta)
    B=float(np.dot(p,q))
    if 1+B<=0:raise ValueError('nonpositive perturbed photon denominator')
    after=p*(1+q)/(1+B)
    J,H=jac_hess(p)
    remainder=p*(q-B)/(1+B)-J@delta
    return after,remainder,p,J,H,den


def exact_sum_bounds(arr):
    """Decimal exact sum of the SOURCE FLOAT64 endpoints, rounded outward to f64."""
    x=np.asarray(arr,dtype=float)
    if x.ndim!=1 or np.any(~np.isfinite(x)) or np.any(x<0):raise ValueError('bad original state')
    with localcontext() as ctx:
        ctx.prec=180
        exact=sum((Decimal.from_float(float(v)) for v in x),Decimal(0))
    f=float(exact)
    lo=f if Decimal.from_float(f)<=exact else math.nextafter(f,-math.inf)
    hi=f if Decimal.from_float(f)>=exact else math.nextafter(f,math.inf)
    if not (Decimal.from_float(lo)<=exact<=Decimal.from_float(hi)):raise AssertionError('outward exact sum failed')
    return lo,hi


def finite_corner_report(Slo,Sref,Shi,c,e,obs):
    """Conditional fixed-forcing all-X outer-box photon source curvature certificate.

    Real-arithmetic Taylor theorem: |H_stu| <= 2 p_s, so the second-order
    remainder satisfies |R_s| <= p_s_max * ||delta||_1**2 on the full box.
    Floating point evaluation is checked and outward padded; this alone is
    not a rounding-certified proof of the full 26-event time-step operator.
    """
    slo=np.asarray(Slo,float);s0=np.asarray(Sref,float);shi=np.asarray(Shi,float)
    c=np.asarray(c,float)
    if any(x.shape!=(3,) for x in (slo,s0,shi,c)) or np.any(slo<=0) or np.any(slo>s0) or np.any(s0>shi) or np.any(c<0) or e<0 or obs<0:
        raise ValueError('source moment interval or coefficient invalid')
    a=c*s0
    p,p_external,den=shares(a,e)
    J,H=jac_hess(p)
    dlow=np.log(slo/s0);dhi=np.log(shi/s0)
    delta_max=np.maximum(np.abs(dlow),np.abs(dhi))
    L=float(math.fsum(map(float,delta_max)))
    # P_s maximum occurs at its own high weight and competitors' lower weights.
    alow=c*slo;ahigh=c*shi
    pmax=np.array([ahigh[s]/(e+ahigh[s]+sum(alow[t] for t in range(3) if t!=s))
                   if c[s]!=0 else 0. for s in range(3)])
    # explicit few ulps to cover rounded summaries, not a formally audited FPU.
    rawbound=pmax*L*L
    rbound=np.where(rawbound==0.0,0.0,np.nextafter(np.nextafter(rawbound,np.inf),np.inf))
    allcorners=[];maxcorner=np.zeros(3);maxrest=np.zeros(3)
    for ch in itertools.product((0,1),repeat=3):
        delta=np.array([dhi[i] if ch[i] else dlow[i] for i in range(3)])
        after,resid,_,_,_,_=log_fraction_response(a,e,delta)
        maxcorner=np.maximum(maxcorner,np.abs(resid))
        maxrest=np.maximum(maxrest,after)
        if np.any(np.abs(resid)>rbound+2e-14):
            raise ValueError('theoretical photon-source nonlinear remainder bound violated')
        allcorners.append({'corner':list(ch),'exact_photon_fraction':after.tolist(),'remainder':resid.tolist()})
    return dict(p=p,external_fraction=p_external,den=den,J=J,H=H,
                dlow=dlow,dhi=dhi,L=L,pmax=pmax,rbound=rbound,
                maxcorner=maxcorner,corners=allcorners,
                current_photons_s=obs,
                quadratic_photon_event_remainder_bound=obs*rbound)


def process_real_repo(repo:Path,out:Path,make_plot=True):
    """Run original 46,080 node source math after immutable source input load."""
    source_script=repo/'research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py'
    spec=importlib.util.spec_from_file_location('rei_source_photon_pr332',source_script)
    if spec is None or spec.loader is None:raise FileNotFoundError(source_script)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    source,mod,model,p0,p1,frozen,t=module.context(repo)
    if int(len(p1))!=NODES:raise ValueError('original node count mismatch')
    accepted=[0,2,3]
    low=[];mid=[];high=[]
    for j in accepted:
        lo,_=exact_sum_bounds(frozen['lo'][:,j]);_,hi=exact_sum_bounds(frozen['hi'][:,j]);m0,m1=exact_sum_bounds(p1[:,j]);m=.5*(m0+m1)
        if not (lo<=m<=hi):raise ValueError('nucleus-sourced moment middle not enclosed')
        low.append(lo);mid.append(m);high.append(hi)
    slo=np.array(low);sref=np.array(mid);shi=np.array(high)
    forcing=model.forcing_bounds(t,t)
    z=module.midpoint(forcing.z)
    coeff=module.coefficients(model,mod,z)
    jsource=np.array([module.midpoint(x) for x in forcing.current])
    exts=np.array([module.midpoint(x) for x in forcing.external_subgrid])
    if coeff.shape!=(4,3) or len(exts)!=4:raise ValueError('wrong number original photon groups')
    summaries=[];point=np.zeros((NODES,3));curvature=np.zeros((NODES,3,3));rem=np.zeros((NODES,3))
    heat=0.
    for g in range(4):
        entry=finite_corner_report(slo,sref,shi,coeff[g],exts[g],jsource[g])
        p=entry['p'];D=entry['den'];l1=entry['L']
        evs=float(jsource[g])*p1[:,accepted]*(coeff[g]/D)[None,:]
        point+=evs
        # Fixed-numerator local photoionization source curvature, NOT varying local x.
        for u in range(3):curvature[:,:,u]+=evs*(2*p[u]**2-p[u])
        D_min=exts[g]+float(np.dot(coeff[g],slo))
        if D_min<=0:raise ValueError('nonpositive denominator')
        qmax=evs*(D/D_min)
        rem+=1.5*qmax*l1*l1
        for s in range(3):heat+=float(jsource[g]*p[s])*float(model.excess_eV[s,g])*EV_ERG
        summaries.append({
          'group':g,'z':z,'time_s':float(t),'physical_current_photons_s':float(jsource[g]),
          'source_moment_HI_HeI_HeII_lower':slo.tolist(),
          'source_moment_HI_HeI_HeII_reference':sref.tolist(),
          'source_moment_HI_HeI_HeII_upper':shi.tolist(),
          'photon_fraction':p.tolist(),'external_fraction':entry['external_fraction'],
          'logmom_delta_lower':entry['dlow'].tolist(),'logmom_delta_upper':entry['dhi'].tolist(),
          'logmom_L1_outer_radius':entry['L'],
          'source_jacobian':entry['J'].tolist(),
          'source_hessian':entry['H'].tolist(),
          'exact_corner_max_second_order_remainder':entry['maxcorner'].tolist(),
          'analytic_full_box_second_order_remainder_bound':entry['rbound'].tolist(),
          'source_photon_event_remainder_bound_s':entry['quadratic_photon_event_remainder_bound'].tolist(),
          'source_second_order_to_first_order':('UNDEFINED_AT_ZERO' if entry['L']==0 else float(np.max(entry['rbound'])/max(float(np.max(np.abs(entry['J'])))*entry['L'],1e-300))),
          'source_moment_3x3x3_Hessian_symmetry_residual':float(np.max(np.abs(entry['H']-entry['H'].transpose(0,2,1))))
        })
    # Source owner crosscheck from PR332 on the same fixed physics state and clock.
    old=module.original_source_interval(model,mod,p1,forcing)
    rates=np.sum(point,axis=0)
    for s in range(3):
        lo=float(old[s].lo); hi=float(old[s].hi)
        if not lo-1e-9*max(abs(lo),abs(hi),1e-70)<=rates[s]<=hi+1e-9*max(abs(lo),abs(hi),1e-70):
            raise ValueError('mismatch to original explicit_photo_fields owner')
    if not (float(old[3].lo)-1e-8*max(abs(heat),1e-70)<=heat<=float(old[3].hi)+1e-8*max(abs(heat),1e-70)):
        raise ValueError('original photoheat outside source bound')
    out.mkdir(parents=True,exist_ok=True)
    outfile=out/'ORIGINAL_26EVENT_NODE_PHOTON_SECOND_ORDER_46080.csv.gz'
    cols={}
    for s,name in enumerate(('HI','HeI','HeII')):
        cols[f'physical_photoionization_{name}_events_s']=point[:,s]
        for u,delta_name in enumerate(('HI','HeI','HeII')):
            cols[f'fixed_local_numerator_d2photo_{name}_dlnS{delta_name}_sq_events_s']=curvature[:,s,u]
        cols[f'fixed_local_numerator_nonlinear_all_outer_moments_remainder_bound_{name}_events_s']=rem[:,s]
    with outfile.open('wb') as f, gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=6) as g,io.TextIOWrapper(g,encoding='utf-8',newline='') as dest:
        w=csv.writer(dest);w.writerow(['node',*cols]);
        for i in range(NODES):w.writerow([i,*[format(float(v[i]),'.17g') for v in cols.values()]])
    rows=[]
    for k,v in cols.items():rows.append({'field':k,'min':float(np.min(v)),'median':float(np.median(v)),'max':float(np.max(v)),'sum':float(np.sum(v))})
    result={
       'unit':'REI_IGM_TICK160_ORIGINAL_26EVENT_GLOBAL_SOURCE_SECOND_ORDER',
       'source_head_pr332':BASE_HEAD,'original_source_tar_sha256':ORIGINAL_TAR_SHA,
       'original_state_array_sha256':ORIGINAL_ARRAY_SHA,'original_kernel_sha256':ORIGINAL_KERNEL_SHA,
       'unique_original_nodes':NODES,'original_first_interval_accepted_ticks':'160/131072',
       'original_failed_crossbox_local_error':2.1245050576368385e-4,'locked_limit':GATE,
       'physical_scope':'original 26event photon global source fixed t160, fixed external forcing at representative midpoint; full original parent marginal ranges only for neutral sums; NOT joint original F_h map',
       'new_source_hessian_group_records':12,'nodewise_physical_curvature_rows':NODES,
       'group_physics':summaries,'per_node_field_summaries':rows,
       'source_owned_photoionization_photons_per_s':rates.tolist(),
       'source_owned_photoheating_erg_per_s':heat,
       'original_source_interval_enclosure_pass':True,
       'state_probe_input_correlated':False,
       'float_interval_endpoints_rigorous_to_original_float_inputs':True,
       'full_coupled_discrete_map_Dh_rigorous_enclosure':'NOT_COMPUTED',
       'new_ivp_count':0,'central_dag':'28/88_REPORTED','working_dag':'33/88_REPORTED','physical_fast_dag':'4/7_REPORTED','canonical_delta':0,
       'source_crc_row_sha256':hashlib.sha256(outfile.read_bytes()).hexdigest(),
       'no_merge':True,'no_force_push':True,'production':'HOLD'
    }
    (out/'PHYSICS_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    if make_plot:
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(7.7,4.6))
        n=np.arange(4)
        arr=np.array([q['analytic_full_box_second_order_remainder_bound'] for q in summaries]);
        ax.bar(n-.23,arr[:,0],.22,label='H I');ax.bar(n,arr[:,1],.22,label='He I');ax.bar(n+.23,arr[:,2],.22,label='He II')
        ax.set_xlabel('Original photon group');ax.set_ylabel('Full-neutral-moment-box quadratic remainder upper bound');ax.set_xticks(n);ax.legend();ax.set_yscale('symlog',linthresh=1e-20);fig.tight_layout()
        fig.savefig(out/'FIG1_ORIGINAL_PHOTON_SOURCE_REMAINDER.png',dpi=145);plt.close(fig)
        fig,ax=plt.subplots(figsize=(7.7,4.6))
        vals=np.sum(np.abs(curvature),axis=(1,2));ax.hist(np.log10(np.maximum(vals,1e-120)),bins=68)
        ax.set_xlabel('log10(sum |source second derivatives|) [events s^-1]');ax.set_ylabel('Original distinct source nodes');fig.tight_layout()
        fig.savefig(out/'FIG2_NODEWISE_SECOND_ORDER_SOURCE_RESPONSE.png',dpi=145);plt.close(fig)
    print('REAL_ORIGINAL_26EVENT_GLOBAL_SOURCE_SECOND_ORDER',json.dumps({'nodes':NODES,'groups':len(summaries),'max_group_quad_bound':max(max(x['analytic_full_box_second_order_remainder_bound']) for x in summaries),'original_photoheat_erg_s':heat,'original_source_rates_s':rates.tolist(),'local_node_csv_sha256':result['source_crc_row_sha256'],'central_dag':'28/88'}),flush=True)
    return result


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);a.add_argument('--output',type=Path,required=True);a.add_argument('--no-plot',action='store_true')
    opts=a.parse_args();process_real_repo(opts.repo,opts.output,not opts.no_plot)
