from pathlib import Path
import argparse,csv,hashlib,json,math,sys,traceback
from decimal import Decimal,localcontext
sys.dont_write_bytecode=True
from shape_innovation import diagnostic

# Independent Decimal60 reference: partial-pivot Gaussian elimination, no Cholesky.
def dec_solve(A,b):
    a=[list(row)+[v] for row,v in zip(A,b)];n=len(b)
    for k in range(n):
        p=max(range(k,n),key=lambda j:abs(a[j][k]));a[k],a[p]=a[p],a[k]
        if not a[k][k]:raise ValueError('SINGULAR_REFERENCE')
        for i in range(k+1,n):
            fac=a[i][k]/a[k][k]
            for j in range(k,n+1):a[i][j]-=fac*a[k][j]
    x=[Decimal(0)]*n
    for i in reversed(range(n)):x[i]=(a[i][n]-sum((a[i][j]*x[j] for j in range(i+1,n)),Decimal(0)))/a[i][i]
    return x

def decimal_reference(C,r):
    with localcontext() as ctx:
        ctx.prec=60
        A=[[Decimal.from_float(float(x)) for x in row] for row in C];v=[Decimal.from_float(float(x)) for x in r];n=len(v);one=[Decimal(1)]*n
        inner=lambda a,b:sum((x*y for x,y in zip(a,b)),Decimal(0))
        w=dec_solve(A,one);h=dec_solve(A,v);beta=inner(one,h)/inner(one,w);rr=[x-beta for x in v];Q=inner(rr,dec_solve(A,rr));out=[]
        for i in range(n):
            ix=[j for j in range(n) if j!=i];B=[[A[j][k] for k in ix] for j in ix];cc=[A[j][i] for j in ix];vj=[v[j] for j in ix];u=[Decimal(1)]*(n-1)
            t=dec_solve(B,u);h=dec_solve(B,vj);g=dec_solve(B,cc);den=inner(u,t);bm=inner(u,h)/den;a=1-inner(cc,t);s0=A[i][i]-inner(cc,g);e=v[i]-inner(cc,h)-a*bm;s=s0+a*a/den;res=[x-bm for x in vj];deleted=inner(res,dec_solve(B,res))
            out.append({'e':e,'s':s,'Z_squared':e*e/s,'beta_minus':bm,'deleted_chi2':deleted,'innovation_chi2':e*e/s,'beta_shift':beta-bm})
        S=[[A[i+1][j+1]-A[i+1][j]-A[i][j+1]+A[i][j] for j in range(n-1)] for i in range(n-1)];d=[v[i+1]-v[i] for i in range(n-1)];cq=inner(d,dec_solve(S,d))
        return {'Q':Q,'contrast_Q':cq,'beta_full':beta,'Delta':d,'leave_one_out':out}

def close(a,b,variance=False):
    a=float(a);b=float(b);tol=1e-10*max(abs(a),abs(b))+(1e-15 if variance else 1e-12)
    if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>tol:raise AssertionError((a,b,tol))

def rejected(C,r):
    try:diagnostic(C,r)
    except ValueError:return True
    raise AssertionError('INVALID_INPUT_ACCEPTED')

def writejson(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False,default=lambda x:str(x) if isinstance(x,Decimal) else x)+'\n')

def main(inp,out):
    out.mkdir(parents=True,exist_ok=False)
    manifest=[]
    expected={'BECKER_BOLTON_2013.json':'893f97497b9aae41f545b17278082602a06b352c86bdeb1db2d9afb5c1c83de4','CALIBRATION_RESULT.json':'8ba2652bcf7358319bbdfc83b499a566890fcf6b449fe12ee759a29a6fcfcc7f'}
    for name,sha in expected.items():
        data=(inp/name).read_bytes();actual=hashlib.sha256(data).hexdigest();assert actual==sha,'INPUT_BYTE_IDENTITY';manifest.append({'name':name,'sha256':actual,'bytes':len(data)})
    obs=json.loads((inp/'BECKER_BOLTON_2013.json').read_text());saved=json.loads((inp/'CALIBRATION_RESULT.json').read_text());C=obs['statistical_covariance_dex2'];d=obs['values'];z=obs['z'];m=saved['template_log10_Gamma12']
    assert len(d)==len(m)==len(z)==7 and z==[2.4,2.8,3.2,3.6,4,4.4,4.75]
    assert d==saved['observed_log10_Gamma12'] and z==saved['observed_z']
    r=[a-b for a,b in zip(d,m)];x=diagnostic(C,r);ref=decimal_reference(C,r);tests={}
    close(x['Q'],19.381736839571925);close(x['Q'],saved['statistical_only']['residual_chi2']);close(x['Q'],x['contrast_Q']);close(x['Q'],ref['Q']);close(x['contrast_Q'],ref['contrast_Q']);close(x['beta_full'],ref['beta_full'])
    for a,b in zip(x['Delta'],ref['Delta']):close(a,b)
    tests['actual_Q_contrast_GLS_Decimal60']=True
    for i,(row,rr) in enumerate(zip(x['leave_one_out'],ref['leave_one_out'])):
        row['z']=z[i];close(row['Q_minus_deleted'],row['innovation_chi2']);close(row['beta_full_minus_beta_minus'],row['block_beta_shift'])
        assert row['Q_minus_deleted']>=-(1e-10*max(abs(x['Q']),abs(row['deleted_chi2']))+1e-12)
        for field in ('e','s','beta_minus','deleted_chi2','innovation_chi2'):close(row[field],rr[field],variance=field=='s')
        close(row['Z']**2,rr['Z_squared']);close(row['beta_full_minus_beta_minus'],rr['beta_shift'])
    tests['all_seven_block_identities_and_Decimal']=True
    for shift in (0.125,-0.25):
        shifted=diagnostic(C,[a+shift for a in r])
        close(shifted['Q'],x['Q'])
        for a,b in zip(shifted['Delta'],x['Delta']):close(a,b)
        for a,b in zip(shifted['leave_one_out'],x['leave_one_out']):close(a['e'],b['e']);close(a['s'],b['s'],True)
    xm=diagnostic(C,[a-(b+0.25) for a,b in zip(d,m)]);close(xm['Q'],x['Q'])
    for a,b in zip(xm['Delta'],x['Delta']):close(a,b)
    assert all(sum(row)==0 for row in x['D'])
    tests['normalization_shift_invariance']=True
    diagonal=[[0.25,0.,0.],[0.,0.5,0.],[0.,0.,1.25]];rv=[0.25,-0.75,0.5];xd=diagnostic(diagonal,rv)
    for i,row in enumerate(xd['leave_one_out']):
        ix=[j for j in range(3) if j!=i];den=sum(1/diagonal[j][j] for j in ix);mean=sum(rv[j]/diagonal[j][j] for j in ix)/den
        close(row['beta_minus'],mean);close(row['predicted_residual'],mean);close(row['s'],diagonal[i][i]+1/den,True);close(row['e'],rv[i]-mean)
    tests['independent_diagonal_weighted_mean_prediction']=True
    synC=[[2.,1.,0.],[1.,2.,1.],[0.,1.,2.]];synr=[0.,1.,-1.];xs=diagnostic(synC,synr);ds=decimal_reference(synC,synr)
    for row,rr in zip(xs['leave_one_out'],ds['leave_one_out']):close(row['s'],rr['s'],True);close(row['e'],rr['e'])
    # c=0 approximation keeps B but replaces the omitted-to-retained covariance.
    def zero_c_approx(C,r,i):
        from shape_innovation import cholesky,solve,dot
        ix=[j for j in range(len(r)) if j!=i];B=[[C[j][k] for k in ix] for j in ix];L=cholesky(B);u=[1.]*len(ix);h=solve(L,[r[j] for j in ix]);t=solve(L,u);den=dot(u,t)
        return r[i]-dot(u,h)/den,C[i][i]+1/den
    assert any(abs(row['s']-zero_c_approx(C,r,i)[1])>1e-8 for i,row in enumerate(x['leave_one_out']))
    assert any(abs(row['e']-zero_c_approx(synC,synr,i)[0])>1e-8 for i,row in enumerate(xs['leave_one_out']))
    tests['actual_and_synthetic_correlation_terms_required']=True
    perm=[6,2,4,0,5,1,3];xp=diagnostic([[C[i][j] for j in perm] for i in perm],[r[i] for i in perm]);close(xp['Q'],x['Q'])
    for k,i in enumerate(perm):
        for field in ('e','s','Z','beta_minus','deleted_chi2','innovation_chi2','beta_full_minus_beta_minus'):close(xp['leave_one_out'][k][field],x['leave_one_out'][i][field],field=='s')
    tests['joint_permutation_labeled_invariance']=True
    assert rejected([[1.,1.],[1.,1.]],[0.,1.]) and rejected([[1.,0.],[0.1,1.]],[0.,1.]) and rejected([[1.]],[0.,1.]) and rejected([[1.,0.],[0.,1.]],[0.,float('nan')])
    tests['rank_deficient_nonsymmetric_dimension_nonfinite_rejection']=True
    p=math.exp(-x['Q']/2)*(1+x['Q']/2+(x['Q']/2)**2/2);assert 0<=p<=1
    contrasts=[]
    for i,delta in enumerate(x['Delta']):
        dd=d[i+1]-d[i];dm=m[i+1]-m[i];sigma=math.sqrt(x['S'][i][i]);close(dd-dm,delta)
        contrasts.append({'z_left':z[i],'z_right':z[i+1],'D_d_dex':dd,'D_m_dex':dm,'Delta_dex':delta,'sigma_dex':sigma,'marginal_Z':delta/sigma,'ratio_discrepancy_10powDelta':10**delta})
    result={'unit':'REI_UVB_SHAPE_INNOVATION_20261028','status':'COMPLETED_SCOPED_CONDITIONAL_DIAGNOSTIC','scientific_admission':'PENDING_FRESH_NONAUTHOR_REVIEW','source_repo':'cosmosapjw-quantum/rei_bianchi','source_commit':'c5ab42c8673db614e7fb16695ad071c65becb81b','input_hashes':manifest,'z':z,'d_dex':d,'m_dex_reused':m,'r_dex':r,**x,'fixed_null_chi2_df':6,'fixed_null_p':p,'descriptive_flag':'CONDITIONAL_STATISTICAL_SHAPE_TENSION' if p<0.01 else 'NO_1PCT_SHAPE_FLAG','fixed_EOS_theta':0,'assumptions':['Gaussian supplied statistical covariance only, already in dex squared','Template fixed for this diagnostic; selected on full data, not independent held-out validation','No Jeans/systematic covariance or parameter selection correction'],'interpretation':['Adjacent marginal Z are correlated; never sum their squares as independent chi-square','Seven leave-one-out innovations are mutually dependent; sum of squares is not Q','No points removed or covariance changed; no EOS-box p-value assigned'],'physical_F4':'PARTIAL_UNCHANGED','full_physical_completion':False,'global_completion_delta':0,'new_IVPs':0,'new_rate_calls':0,'old_tests_rerun':0}
    writejson(out/'RESULT.json',result);writejson(out/'DECIMAL60_REFERENCE.json',ref);writejson(out/'covariance.json',{'C_dex2':C,'D':x['D'],'S_dex2':x['S']});writejson(out/'TEST_RESULT.json',{'status':'PASS','tests':tests,'test_groups':len(tests),'relative_tolerance':1e-10,'absolute_tolerance':1e-12,'variance_absolute_tolerance_dex2':1e-15,'worker_processes':1,'Decimal_precision':60,'production_solver':'binary64 Cholesky solves; no inverse','reference_solver':'Decimal60 partial-pivot Gaussian elimination','failure_clamping':False,'scientific_retries':0})
    for name,rows in [('ADJACENT_CONTRASTS.csv',contrasts),('LEAVE_ONE_OUT.csv',x['leave_one_out'])]:
        with (out/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({'status':'PASS','Q':x['Q'],'p_df6_fixed_null':p,'flag':result['descriptive_flag'],'groups':len(tests)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:main(a.inputs,a.output)
    except Exception as exc:
        if a.output.exists():writejson(a.output/'FAILURE.json',{'status':'FAIL_STOP_FOR_AUTHORITY','type':type(exc).__name__,'error':str(exc)})
        raise
