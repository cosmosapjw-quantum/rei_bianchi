"""24 bounded prescribed-opacity controls; no native gas history is certified."""
import argparse,json,math
from pathlib import Path
from scipy.integrate import quad
from paired_response_bound import paired_bound


def sup_survival_difference(k1,k2,last=1.):
    candidates=[0.,last]
    if k1>0 and k2>0 and k1!=k2:
        critical=math.log(k2/k1)/(k2-k1)
        if 0.<critical<last:candidates.append(critical)
    return max(abs(math.exp(-k1*t)-math.exp(-k2*t)) for t in candidates)


def study():
    rows=[]
    for k1,k2 in [(0.,1.),(1.,2.),(5.,20.),(20.,100.)]:
        for n in (8,16,32):
            for scale in (1.,1.1):
                xa=[(i+.5)/n for i in range(n)]
                xb=[(i+.5)/(2*n) for i in range(2*n)]
                wa=[(1.+.3*x)/n for x in xa]
                wb=[scale*(1.+.3*x)/(2*n) for x in xb]
                delta=sup_survival_difference(k1,k2)
                out=paired_bound(xa,wa,xb,wb,
                    left_envelope=dict(response_abs_max=1.,smooth_lipschitz=k1),
                    right_envelope=dict(response_abs_max=1.,smooth_lipschitz=k2),
                    response_sup_difference=delta)
                a=math.fsum(w*math.exp(-k1*x) for x,w in zip(xa,wa))
                b=math.fsum(w*math.exp(-k2*x) for x,w in zip(xb,wb))
                truth=abs(a-b)
                assert truth<=out['absolute_bound']+3.e-15
                ra=quad(lambda x:(1.+.3*x)*math.exp(-k1*x),0.,1.,epsabs=1e-13,epsrel=1e-13)[0]
                rb=quad(lambda x:scale*(1.+.3*x)*math.exp(-k2*x),0.,1.,epsabs=1e-13,epsrel=1e-13)[0]
                rows.append(dict(k_left=k1,k_right=k2,n_left=n,n_right=2*n,
                    source_scale_right=scale,discrete_response_difference=truth,
                    conditional_bound=out['absolute_bound'],response_sup_difference=delta,
                    direct_continuum_controls=[ra,rb],finite_grid_errors=[abs(a-ra),abs(b-rb)],
                    includes_response_change=True))
    return dict(schema='rei.age.two_response.study.v1',cases=rows,case_count=len(rows),
        all_24_inside_conditional_bound=True,native_execution='NOT_RUN',
        scope='Prescribed positive source and constant opacity; no Grackle admission')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();result=study();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(case_count=result['case_count'],all_inside=True,native_execution='NOT_RUN')))
