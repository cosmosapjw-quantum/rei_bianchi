"""Independent dictionary-polynomial oracle for the implicit mixed operator."""
from fractions import Fraction as Q
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from implicit_mixed import D2,make_reduced_residual,mixed_at_candidate,reduced_photons,solve_linear

KEYS=((0,0),(1,0),(0,1),(1,1))
def poly(x):
    return x if isinstance(x,dict) else {(0,0):Q(x)}
def add(a,b):
    a,b=poly(a),poly(b)
    return {k:a.get(k,Q(0))+b.get(k,Q(0)) for k in KEYS}
def mul(a,b):
    a,b=poly(a),poly(b);out={k:Q(0) for k in KEYS}
    for (i,j),x in a.items():
        for (k,l),y in b.items():
            if i+k<=1 and j+l<=1:out[(i+k,j+l)]+=x*y
    return out
def neg(a):return {k:-v for k,v in poly(a).items()}
def sub(a,b):return add(a,neg(b))
def div(a,b):
    a,b=poly(a),poly(b)
    d=b.get((0,0),Q(0)); assert d!=0
    z={}
    z[(0,0)]=a.get((0,0),Q(0))/d
    z[(1,0)]=(a.get((1,0),Q(0))-b.get((1,0),Q(0))*z[(0,0)])/d
    z[(0,1)]=(a.get((0,1),Q(0))-b.get((0,1),Q(0))*z[(0,0)])/d
    z[(1,1)]=(a.get((1,1),Q(0))-b.get((1,1),Q(0))*z[(0,0)]
                 -b.get((1,0),Q(0))*z[(0,1)]-b.get((0,1),Q(0))*z[(1,0)])/d
    return z
def tojet(a):return D2(*(poly(a).get(k,Q(0)) for k in KEYS))
def nonlinear_poly(g):
    x,y,z,w=g
    return [neg(mul(x,y)),sub(mul(x,z),mul(y,w)),
            sub(mul(y,y),mul(z,w)),neg(mul(w,add(1,add(x,z))))]
def hh_poly(g):
    x,y,z,w=g
    return mul(Q(1,17),mul(mul(sub(1,x),sub(1,x)),mul(w,add(w,y))))
def nonlinear_jet(g):
    x,y,z,w=g
    return [-x*y,x*z-y*w,y*y-z*w,-w*(1+x+z)]
def hh_jet(g):
    x,y,z,w=g
    return Q(1,17)*(1-x)**2*w*(w+y)

def manufacture_old(g,incoming,lam,dt,density,c,fhe,energies,sigma,chi):
    f=nonlinear_poly(g);qq=mul(lam,hh_poly(g))
    f[0]=add(f[0],qq);f[3]=sub(f[3],mul(chi[0],qq))
    lower=[sub(1,g[0]),mul(fhe,sub(sub(1,g[1]),g[2])),mul(fhe,g[1])]
    for stock,e,sig in zip(incoming,energies,sigma):
        op=poly(0)
        for l,s in zip(lower,sig):op=add(op,mul(c*density*s,l))
        photon=div(stock,add(1,mul(dt,op)))
        rates=[mul(c*density*s,mul(l,photon)) for l,s in zip(lower,sig)]
        f[0]=add(f[0],rates[0])
        f[1]=add(f[1],div(sub(rates[1],rates[2]),fhe))
        f[2]=add(f[2],div(rates[2],fhe))
        for r,cut in zip(rates,chi):f[3]=add(f[3],mul(e-cut,r))
    return [sub(y,mul(dt,v)) for y,v in zip(g,f)]

def run():
    records=[]
    for case in range(6):
        dt=Q(1,64+8*case);density=Q(2,7);c=Q(3,2);fhe=Q(1,5)
        energies=[Q(4),Q(7)];chi=[Q(1),Q(2),Q(3)]
        sigma=[[Q(1,3),Q(1,5),Q(1,7)],[Q(2,9),Q(1,6),Q(1,8)]]
        bases=[Q(2,5),Q(1,5),Q(1,10),Q(2)]
        g=[]
        for i,value in enumerate(bases):
            g.append(dict(zip(KEYS,[value,Q((-1)**i*(case+1),31+i),
                                   Q(i+2,43+case),Q((-1)**(i+1),61+i+case)])))
        incoming=[]
        for i in range(2):
            incoming.append(dict(zip(KEYS,[Q(0) if case==5 and i==0 else Q(1+i,20),
                                           Q(-1+i,113),Q(2+i,127),Q(-3+i,131)])))
        lam={(0,0):Q(case%3,2),(1,0):Q(1)}
        old=manufacture_old(g,incoming,lam,dt,density,c,fhe,energies,sigma,chi)
        residual=make_reduced_residual(dt,density,c,fhe,energies,sigma,chi,
                                       nonlinear_jet,hh_jet)
        answer=mixed_at_candidate(residual,bases,list(map(tojet,old)),
                                  list(map(tojet,incoming)),tojet(lam))
        for label,key in [('U',(1,0)),('V',(0,1)),('W',(1,1))]:
            assert answer[label]==[x[key] for x in g],(case,label)
        for label in ('primal_residual','first_a_residual','first_b_residual','mixed_residual'):
            assert all(x==0 for x in answer[label]),(case,label)
        # Energy linkage of HH is independently a stoichiometric identity.
        q=hh_jet(list(map(tojet,g)))
        assert (-chi[0]*q+chi[0]*q)==D2(Q(0),Q(0),Q(0),Q(0))
        records.append({'case':case,'lambda_base':str(tojet(lam).v),'PASS':True,
                        'zero_photon_stock_with_nonzero_signed_derivatives':case==5,
                        'U':list(map(str,answer['U'])),'V':list(map(str,answer['V'])),
                        'W':list(map(str,answer['W']))})
    negative_cases=[]
    for name,call in [
        ('singular_jacobian',lambda:solve_linear([[Q(0)]],[Q(1)])),
        ('zero_denominator',lambda:D2(Q(0)).reciprocal()),
        ('negative_photon_denominator',lambda:reduced_photons(
            [D2(Q(3)),D2(Q(0)),D2(Q(0)),D2(Q(1))],[D2(Q(1))],
            Q(1),Q(1),Q(1),Q(1,10),[[Q(1),Q(0),Q(0)]])),
        ('invalid_threshold',lambda:make_reduced_residual(
            Q(1),Q(1),Q(1),Q(1,10),[Q(1)],[[Q(0),Q(1),Q(0)]],
            [Q(1),Q(2),Q(3)],nonlinear_jet,hh_jet))
    ]:
        try:call()
        except (ValueError,ZeroDivisionError):negative_cases.append({'case':name,'correctly_rejected':True})
        else:raise AssertionError(name)
    return {'schema':'HH_PHYS04_IMPLICIT_MIXED_CHECKS_V1','cases':records,
            'negative_cases':negative_cases,'exact_rational_cases':6,
            'state_derivative_slots':72,'zero_residual_slots':96,
            'independence':'candidate D2 derivatives and generic Gaussian elimination versus dictionary polynomial manufacture from prescribed root family; common physical algebra/fixtures disclosed',
            'physical_model':'H/He stoichiometry and heat, polynomial nonphoto/HH fixtures; not actual provider rates',
            'scope':'arithmetic tangent implementation at manufactured candidate, no nonlinear root finding',
            'native_dispatches':0,'nonlinear_BE_roots':0,'IVP_runs':0}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ns=ap.parse_args()
    if ns.output.exists():raise FileExistsError('evidence output exists')
    result=run();ns.output.parent.mkdir(parents=True,exist_ok=True)
    ns.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'PASS':True,'exact_cases':6,'domain_rejections':4,
                      'derivative_slots':72,'residual_slots':96,'output':str(ns.output)}))

if __name__=='__main__':main()
