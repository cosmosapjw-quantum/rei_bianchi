"""Independent Decimal70 source oracle, separate from REC/REI implementations."""
from decimal import Decimal as D, getcontext
from pathlib import Path
import argparse, itertools, json, subprocess, hashlib
getcontext().prec=70
TOL=D('3e-12')
def source(t,n,h,x,y):
    one=D(1); t4=t/D(10000); tev=D('8.617343e-5')*t
    alpha=D('4.309e-19')*t4**D('-.6166')/(one+D('.6703')*t4**D('.5300'))
    beta=alpha*D('3.016103031869581e27')*tev**D('1.5')*(-D('13.598286071938324')/4/tev).exp()
    bol=(-D('10.198714553953742')/tev).exp(); x1=one-x-y
    ra=D('4.662899067555897e21')*h/n/x1; bg=beta/4; dg=(D('8.2206')+3*ra)/4; c=dg/(dg+bg)
    v=dict(x1=x1,alpha_b_m3_s=alpha,beta_p_s=beta,beta_shell_s=bg,r_alpha_s=ra,d_ground_s=dg,boltzmann_lya=bol,c_factor=c)
    rec=n*alpha*x*x; inv=beta*(one-x)*bol; peebles=-c*(rec-inv)
    continuum=rec-bg*y; ground=dg*(y-4*x1*bol)
    rhs=dict(dxp_dt=-continuum,dx2_dt=continuum-ground,dx1_dt=ground,continuum_flux=continuum,ground_flux=ground)
    return v,peebles,rhs,max(abs(rec),abs(inv),abs(bg*y),abs(ground),D('1e-300'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
    lines=[];cases=[]
    for t,n,h,(x,y),mode in itertools.product(['1000','3000','6000'],['1e3','1e8'],['1e-15','1e-13'],[('.05','0'),('.5','1e-10'),('.95','.001')],['point_si','point_cgs']):
        nn=D(n) if mode=='point_si' else D(n)/D('1e6');lines.append(f'{mode} {t} {t} {nn} {h} {x} {y}');cases.append((t,n,h,x,y))
    invalid=['point_si 3000 3001 1e8 1e-13 .5 0','point_si 3000 3000 1e8 0 .5 0','point_si 3000 3000 0 1e-13 .5 0','point_si 3000 3000 1e8 1e-13 1 0','point_si 3000 3000 1e8 1e-13 .5 .6','point_cgs 3000 3000 1e308 1e-13 .5 0','point_si NaN 3000 1e8 1e-13 .5 0','point_si 3000 3000 1e8 1e-13 -.1 0']
    (out/'POINT_ORACLE_INPUT.txt').write_text('\n'.join(lines+invalid)+'\n')
    run=subprocess.run([a.native],input='\n'.join(lines+invalid)+'\n',text=True,capture_output=True,timeout=30)
    (out/'POINT_ORACLE_NATIVE.jsonl').write_text(run.stdout);(out/'POINT_ORACLE_NATIVE.stderr').write_text(run.stderr)
    rows=[json.loads(s,parse_float=D) for s in run.stdout.splitlines()];fail=[];checks=0;maxima={}
    def check(ok,label,idx):
        nonlocal checks
        checks+=1
        if not ok:fail.append(dict(case=idx,check=label))
    def close(g,w,s,label,idx):
        e=abs(D(g)-w)/max(abs(s),D('1e-300'));maxima[label]=max(maxima.get(label,D(0)),e);check(e<=TOL,label,idx)
    check(run.returncode==0,'native_exit',-1);check(len(rows)==len(lines)+len(invalid),'row_count',-1)
    for i,(row,case) in enumerate(zip(rows,cases)):
        check(row.get('ok') is True,'valid_admitted',i)
        if not row.get('ok'):continue
        t,n,h,x,y=map(D,case);sc,pc,_,scale=source(t,n,h,x,D(0));sr,pr,rr,rscale=source(t,n,h,x,y)
        for mode,wanted in [('collapsed',sc),('retained',sr)]:
            for k,v in wanted.items():close(row[mode]['source'][k],v,v,'source.'+k,i)
        close(row['collapsed']['dxp_dt'],pc,scale,'collapsed_rhs',i)
        close(row['retained']['same_rates_peebles_dt'],pr,rscale,'same_rates_rhs',i)
        for k,v in rr.items():close(row['retained']['rhs'][k],v,rscale,'retained.'+k,i)
        d=row['retained']['closure_defect'];direct=rr['dxp_dt']-pr;lag=-(1-sr['c_factor'])*rr['dx2_dt'];depletion=-sr['c_factor']*sr['beta_p_s']*sr['boltzmann_lya']*y
        for k,v in [('direct',direct),('shell_lag',lag),('ground_depletion',depletion),('reconstructed',lag+depletion)]:close(d[k],v,rscale,'defect.'+k,i)
        close(row['retained_minus_standard_collapsed'],rr['dxp_dt']-pc,rscale,'total_difference',i)
        check(row['physical_admission'] is False,'claim_ceiling',i)
    for j,row in enumerate(rows[len(cases):]):check(row.get('ok') is False,'invalid_rejected',j)
    result=dict(status='PASS' if not fail else 'FAIL',checks=checks,valid_cases=len(cases),invalid_cases=len(invalid),tolerance=str(TOL),precision_digits=70,max_scaled_errors={k:str(v) for k,v in maxima.items()},failures=fail,oracle_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_sha256=hashlib.sha256(Path(a.native).read_bytes()).hexdigest(),independence='separate high-precision formulas; same source-profile constants are shared deliberately',scope='finite pointwise consumer validation, not physical-error or history certificate')
    (out/'POINT_ORACLE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(bool(fail))
if __name__=='__main__':main()
