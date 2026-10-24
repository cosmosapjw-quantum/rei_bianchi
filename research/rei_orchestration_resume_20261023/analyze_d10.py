#!/usr/bin/env python3
"""Frozen D10 saved-sample diagnostic; no model, RHS, moment or IVP calls."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[k]='1'
import csv,hashlib,json,pathlib,time,resource,traceback
import numpy as np
from scipy.integrate import cumulative_simpson,cumulative_trapezoid
ROOT=pathlib.Path(__file__).resolve().parent
SIG=[0,.0003,.001,.003,.01,.03,.1]; RAD=[-.001,-.0003,0,.0003,.001]
def require(v,msg):
    if not v: raise ValueError(msg)
def integrate(x,y):
    require(x.ndim==1 and len(x)>=3 and np.isfinite(x).all() and np.all(np.diff(x)>0),'nonmonotone/invalid grid')
    require(y.shape[-1]==len(x) and np.isfinite(y).all(),'invalid integrand')
    return cumulative_simpson(y,x=x,axis=-1,initial=0),cumulative_trapezoid(y,x=x,axis=-1,initial=0)
def select(axes,ids):
    require(axes.shape==(175,3) and len(ids)==175,'population')
    ix=np.flatnonzero(axes[:,1]==0)
    require(len(ix)==35 and len(set(ids[ix]))==35,'35 unique selected histories')
    require(set(map(tuple,axes[ix]))=={(s,0,r) for s in SIG for r in RAD},'selected physical grid')
    return ix
def controls():
    x=np.array([0.,.07,.2,.51,.8,1.]); y=3*x*x+2*x+1
    b,t=integrate(x,y);require(np.max(abs(b-(x**3+x*x+x)))<2e-15,'quadratic analytic primitive')
    b,t=integrate(x,np.zeros_like(x));require(np.all(b==0) and np.all(t==0),'neutral control')
    for bad in (np.array([0.,.1,.1,.3]),np.array([0.,.2,.1,.3])):
        try: integrate(bad,np.ones_like(bad))
        except ValueError: pass
        else: raise AssertionError('corrupt grid accepted')
    ax=np.array([(s,m,r) for s in SIG for m in [-.0003,-.0001,0,.0001,.0003] for r in RAD]); ids=np.array([str(i) for i in range(175)])
    require(len(select(ax,ids))==35,'control valid selection')
    bad=ax.copy();bad[np.flatnonzero(bad[:,1]==0)[0],2]=.002
    for aa,dd in [(bad,ids),(ax,np.array(['same']*175)),(ax[:-1],ids[:-1])]:
        try: select(aa,dd)
        except ValueError: pass
        else: raise AssertionError('invalid selector accepted')
    return {'status':'PASS','controls':['nonuniform quadratic analytic primitive','neutral primitive','duplicate/reversed grid rejection','35 unique physical grid selector and three rejection cases']}
def write(name,obj): (ROOT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def run():
    start=time.perf_counter();cpu=time.process_time();tests=controls();write('CONTROLS.json',tests)
    inp=ROOT/'inputs'; meta=json.loads((inp/'D9_COMPACT_IDENTITY.json').read_bytes()); receipts=json.loads((inp/'github_blobs.json').read_bytes()); recover=[]
    for rec in receipts:
        p=inp/pathlib.Path(rec['path']).name;data=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();require(blob==rec['git_blob'],'git blob '+p.name)
        recover.append({**rec,'local_name':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_verified':True})
    require(hashlib.sha256((inp/'D9_COMPACT_INPUT.npz').read_bytes()).hexdigest()==meta['compact_npz_sha256'],'compact sha')
    a=np.load(inp/'D9_COMPACT_INPUT.npz',allow_pickle=False);bindings=meta['source_input_manifest']['cases']; ids=a['case_ids']; axes=a['physical_axes'];require(np.array_equal(ids,[r['case_id'] for r in bindings]),'identity order')
    require(np.array_equal(axes,[[r[k] for k in ('Sigma_F_i','P_m_i','P_r_i')] for r in bindings]),'identity axes')
    ix=select(axes,ids);x=a['x'];require(len(x)==153,'153 epochs');require(np.allclose(a['a'][:,[0,-1]],[[1/21,1/3]],rtol=0,atol=2e-15),'z endpoints')
    require(all(np.isfinite(a[k]).all() for k in a.files if a[k].dtype.kind=='f'),'finite arrays');require(np.all(a['a']>0) and np.all(np.diff(a['a'],axis=1)>0),'positive monotone a');require(np.allclose(a['a'],a['a'][0],rtol=0,atol=0),'common a grid');require(np.all(a['H']>0),'positive H'); sh=a['s'][ix]/a['H'][ix];b,t=integrate(x,sh); pm=a['Pi_F_signed_matter'][ix];pr=a['Pi_F_signed_gamma'][ix]+a['Pi_F_signed_nu'][ix];sf=np.sqrt(6)*sh
    rows=[]; mapping=[]
    for k,i in enumerate(ix):
        robust=(abs(pm[k])>1e-12)&(abs(b[k])>1e-10); sensitive=robust&(np.sign(t[k])!=np.sign(b[k])); resolved=robust&~sensitive; agree=resolved&(np.sign(pm[k])==-np.sign(b[k])); violate=resolved&~agree;first=np.flatnonzero(abs(pm[k])>1e-12);j=int(first[0]) if len(first) else None;peak=int(np.argmax(abs(pm[k])));s,m,r=axes[i]
        expected=-1 if s>0 else (-int(np.sign(r)) if r else 0)
        rows.append(dict(case_id=str(ids[i]),Sigma_F_i=float(s),P_m_target=0.,P_r_target=float(r),initial_P_m_F=float(pm[k,0]),final_P_m_F=float(pm[k,-1]),peak_signed_P_m_F=float(pm[k,peak]),peak_sample=peak,first_nonzero_sample=j,first_nonzero_x=float(x[j]) if j is not None else None,first_nonzero_z=float(1/a['a'][i,j]-1) if j is not None else None,first_nonzero_P_m_F=float(pm[k,j]) if j is not None else None,expected_local_onset_sign=expected,first_sample_sign_matches_expectation=bool(np.sign(pm[k,j])==expected) if j is not None else None,initial_S_F=float(sf[k,0]),initial_P_r_F=float(pr[k,0]),final_reconstructed_b=float(b[k,-1]),endpoint_trapezoid_minus_Simpson=float(t[k,-1]-b[k,-1]),sign_agreements=int(agree.sum()),sign_violations=int(violate.sum()),nearzero_unresolved=int((~robust).sum()),quadrature_sign_sensitive_samples=int(sensitive.sum())))
        mapping.append({'compact_index':int(i),'binding':bindings[i]})
    with (ROOT/'endpoints35.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write('selected_input_identity.json',mapping);write('SOURCE_RECOVERY.json',{'commit':'cce008b3fc32c298185b30550b2cd909d74fcd87','files':recover});np.savez_compressed(ROOT/'sampled_diagnostics35.npz',x=x,case_ids=ids[ix],reconstructed_b=b,trapezoid_b=t,P_m_F=pm,S_F=sf,P_r_F=pr)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(4,2,figsize=(11,12),sharex=True);axs=axs.ravel()
    for k,s in enumerate(SIG):
        for row,i in enumerate(ix):
            if axes[i,0]==s: axs[k].plot(x,pm[row],label=f'Pr0={axes[i,2]:+.4g}')
        axs[k].axhline(0,color='grey',lw=.5);axs[k].set_title(f'Sigma_F,0 = {s:g}');axs[k].set_yscale('symlog',linthresh=1e-12);axs[k].set_ylabel('signed P_m,F');axs[k].set_xlabel('x = ln(a/a_initial)')
    axs[0].legend(fontsize=7);axs[-1].axis('off');fig.suptitle('35 saved histories; exact metadata P_m,0 = 0');fig.tight_layout();fig.savefig(ROOT/'signed_stress35.png',dpi=150);fig.savefig(ROOT/'signed_stress35.pdf');plt.close(fig)
    result={'status':'MECHANICAL_DIAGNOSTIC_COMPLETE_ASTRA_REVIEW_PENDING','selected_cases':35,'epochs':153,'new_IVP_ODE_RHS_moment_evaluations':0,'b_definition':'reconstructed_b = sampled cumulative Simpson integral(s/H dx), b0=0; not exact stored b','thresholds':{'P_m_F':1e-12,'reconstructed_b':1e-10},'aggregate':{key:sum(r[key] for r in rows) for key in ['sign_agreements','sign_violations','nearzero_unresolved','quadrature_sign_sensitive_samples']},'max_abs_endpoint_trapezoid_minus_Simpson':max(abs(r['endpoint_trapezoid_minus_Simpson']) for r in rows),'first_nonzero_onset_sign_mismatches':[r['case_id'] for r in rows if r['first_sample_sign_matches_expectation'] is False],'neutral_control':[r for r in rows if r['Sigma_F_i']==0 and r['P_r_target']==0],'controls':tests,'claim_boundary':'sample diagnostics and qualitative onset sign only; no exact sample-derived derivatives, Pbar or beta invented, no new tolerance theorem admission','RC_evidence':{'source_recovery':'SOURCE_RECOVERY.json','selector_and_grid':'CONTROLS.json','identities':'selected_input_identity.json','sample_diagnostics':'endpoints35.csv','scientific_admission':'Astra review pending'},'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    write('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
    try: run()
    except Exception:
        (ROOT/'FAILURE.log').write_text(traceback.format_exc());raise
