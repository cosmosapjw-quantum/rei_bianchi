"""Independent finite checks, with no IVP."""
import time
CPU0,WALL0=time.process_time(),time.monotonic()
import json,traceback,resource
import numpy as np
from scipy.integrate import quad
from scipy.linalg import expm
from trace_model import *
def scalar(x):
    if isinstance(x,np.generic):return x.item()
    from collections.abc import Mapping
    if isinstance(x,Mapping):return dict(x)
    raise TypeError(type(x).__name__)
def main():
    R=BASE/'results';R.mkdir(parents=True,exist_ok=True)
    out={'stage':'preflight','new_IVPs':0,'checks':{},'diagnostic_tolerances':{
        'jacobian':'max_abs(J-fd)/max(1,max_abs(J))<=2e-7, centered step1e-5, eta.35 away from interfaces',
        'expm':'absolute native fraction difference<=2e-14',
        'algebra':'residual / max(1,sum absolute event terms)<=1e-12',
        'angular':'abs(GL-quad)/max(1,abs(quad))<=1e-10; LambdaE uses1eV reference scale'}}
    try:
        mp=BASE/'inputs/driver_manifest.json'
        if DRIVER_PATH.exists() and mp.exists():out['drivers']=json.loads(mp.read_text());out['driver_construction']='reuse'
        else:out['drivers']=build_drivers();out['driver_construction']='authorized scratch-loss recovery; source RHS only'
        rate=Rates();first,last=rate.endpoint_roots
        out['support_endpoint_eta']=[first,last]
        out['support_endpoint_energy_eV']=[float(energy(first,1.,rate.bg.fields(first)[2])),float(energy(last,0.,rate.bg.fields(last)[2]))]
        ck=out['checks'];ck['endpoint_roots']=max(abs(e-CHI[0]) for e in out['support_endpoint_energy_eV'])<=1e-12
        out['support_sign_tests']=[{'eta':t,'b':b,'interval':support(t,b)} for b in [0.,.1,-.1] for t in [0.,.55,.8]]
        ck['b_zero_full_empty']=support(0.,0.)==(0.,1.) and support(.8,0.)==(0.,0.)
        ck['opposite_sign_support']=support(.55,.1)[0]==0. and support(.55,-.1)[1]==1.
        row=dict(ATOM.provider.rows['LiI']);p2=row['PH2']
        ck['sigma_source_row']=p2[0]==3.107 and p2[2]==15.01 and p2[3]==4.895 and tuple(p2[4:])==(0.,0.,0.)
        roots=np.roots([-7*15.01,(4.895-7)*15.01,11.,11-4.895])
        pos=[float(x.real) for x in roots if abs(x.imag)<1e-14 and x.real>0];em=3.107*15.01*pos[0]**2;sv=sigma(np.array([CHI[0],em,10.]))
        out['sigma_bound']={'LiI_row':row,'positive_root_u':pos,'stationary_energy_eV':em,'sigma_endpoint_stationary_endpoint_cm2':sv.tolist(),'chosen_bound_cm2':SIGMA_MAX}
        ck['sigma_stationary_bound']=len(pos)==1 and abs(em-6.70826323365278)<1e-12 and sv.max()<SIGMA_MAX and sv[1]>max(sv[0],sv[2])
        etas=sorted({*np.linspace(0.,.9,61),first,last,*(p+s*d for p in [first,last] for s in [-1,1] for d in [1e-10,1e-8,1e-6])})
        assert len(etas)<=121
        rows=[];defects={8:[],16:[],32:[]};widths=[]
        for t in etas:
            h,n,b,bp=rate.bg.fields(t);lo,hi=support(t,b)
            def ein(mu):return 10*np.exp(-t)*np.sqrt(np.exp(2*b)*(1-mu*mu)+np.exp(-4*b)*mu*mu)
            def fun(mu):return C*n/h*float(ATOM.provider.sigma('LiI',np.array(ein(mu))))*1e-18*.05
            q,qe=quad(fun,lo,hi,epsabs=1e-11,epsrel=2e-13);qE,qEe=quad(lambda mu:ein(mu)*fun(mu),lo,hi,epsabs=1e-11,epsrel=2e-13)
            item={'eta':float(t),'support':[lo,hi],'Lambda_quad':q,'LambdaE_quad_eV':qE,'quad_error_estimate':[qe,qEe],'rules':{}}
            for m in [8,16,32]:
                lam,le,k,e,wk,w=rate.coefficients(float(t),'split',m);err=[abs(lam-q)/max(1.,abs(q)),abs(le-qE)/max(1.,abs(qE))]
                defects[m].append(err);widths.append((float(w.sum()),hi-lo,float(w.min())))
                item['rules'][str(m)]={'Lambda':lam,'LambdaE_eV':le,'normalized_errors':err}
            item['unsplit_GL4_normalized_error']=abs(rate.coefficients(float(t),'fixed',4)[0]-q)/max(1.,abs(q));rows.append(item)
        out['angular_comparison']=rows;out['angular_check_etas_count']=len(etas)
        out['angular_max_normalized_errors']={str(m):np.max(v,axis=0).tolist() for m,v in defects.items()}
        out['normalization_max_absolute_defect']=max(abs(a-b) for a,b,c in widths);out['minimum_weight']=min(c for a,b,c in widths)
        out['unsplit_GL4_max_normalized_error']=max(x['unsplit_GL4_normalized_error'] for x in rows)
        ck['constant_integrand_normalization']=out['normalization_max_absolute_defect']<1e-14;ck['nonnegative_weights']=out['minimum_weight']>=0
        ck['split_GL8_16_32_vs_quad']=all(np.max(v)<=1e-10 for v in defects.values());ck['unsplit_support_defect']=out['unsplit_GL4_max_normalized_error']>1e-10
        model=Trace();r=np.array([.31,.72,1.13]);lam=.87;a=model.matrix(lam,r);off=a.copy();np.fill_diagonal(off,0.)
        out['generator_column_sum_max_abs']=float(abs(a.sum(axis=0)).max());ck['generator']=out['generator_column_sum_max_abs']<1e-14 and off.min()>=0
        f=np.array([.2,.3,.25,.25]);t=.63;actual=expm(a*t)@f;f3=f[3]*np.exp(-r[2]*t);c3=r[2]*f[3]/(r[1]-r[2]);c2=f[2]-c3
        f2=c2*np.exp(-r[1]*t)+c3*np.exp(-r[2]*t);aa=r[0]+lam
        neutral=f[0]*np.exp(-aa*t)+r[0]*(1-np.exp(-aa*t))/aa
        for c,q in [(c2,r[1]),(c3+f[3],r[2])]:neutral-=r[0]*c*(np.exp(-q*t)-np.exp(-aa*t))/(aa-q)
        out['expm_closed_form_max_abs_defect']=float(abs(actual-np.array([neutral,1-neutral-f2-f3,f2,f3])).max())
        ck['expm_closed_form']=out['expm_closed_form_max_abs_defect']<=2e-14
        jr=[];dr=[]
        for atten in [False,True]:
            m=Trace(kind='fixed' if atten else 'split',M=16,attenuated=atten);y=m.y0.copy();y[:4]=f
            if atten:y[9:]=np.linspace(.001,.02,16)
            tm=.35;J=m.jac(tm,y);step=1e-5;eye=np.eye(m.size)
            fd=np.column_stack([(m.rhs(tm,y+eye[j]*step)-m.rhs(tm,y-eye[j]*step))/(2*step) for j in range(m.size)])
            den=max(1.,float(abs(J).max()));jr.append({'attenuated':atten,'eta':tm,'normalized_defect':float(abs(J-fd).max()/den),'denominator':den,'nearest_support_interface_distance_eta':min(abs(tm-q) for q in m.rates.fixed_crossings(16))})
            dy=m.rhs(tm,y);er=float(BIND@dy[:4]+dy[6]+dy[7]-dy[8]);cr=float(CHARGE@dy[:4]-dy[4]+dy[5]);scale=max(1.,float(abs(BIND*dy[:4]).sum()+abs(dy[6:9]).sum()))
            dr.append({'attenuated':atten,'charge':cr,'energy':er,'scale':scale,'normalized_energy_defect':abs(er)/scale})
        out['jacobian_checks']=jr;out['ledger_derivative_checks']=dr;ck['jacobians']=all(x['normalized_defect']<=2e-7 for x in jr)
        ck['event_derivatives']=all(abs(x['charge'])<=1e-12*x['scale'] and x['normalized_energy_defect']<=1e-12 for x in dr)
        out['all_pass']=all(ck.values())
    except Exception:out['all_pass']=False;out['exception']=traceback.format_exc()
    out['execution']={'CPU_s':time.process_time()-CPU0,'wall_s':time.monotonic()-WALL0,'maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'requested_worker':'gpt-6.1-sol/high','observed_runtime_identity':'not exposed by tools'}
    (R/'preflight.json').write_text(json.dumps(out,indent=2,allow_nan=False,default=scalar)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['angular_comparison','drivers']},indent=2,default=scalar))
    return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())

