"""Delta-only quotient, count-ledger and independent manufactured-jet checks."""
import math
import sys
from normalized_beta_client import (STATE,PROVIDERS,NU_C,NU_B,BARYON,CHARGE,LEPTON,
                                    check_domain,evaluate,jvp,lifted_oracle)

BOX={'lower':(0.,)*5+(-1.,),'upper':(10.,)*5+(1.,)}
X=(1.,2.,3.,4.,5.,0.)
EPS=128*sys.float_info.epsilon


def close(a,b,tolerance=EPS):return abs(a-b)<=tolerance*max(1.,abs(a)+abs(b))
def constants(S=.6,lc=.2,lb=.03,theta=.04,alpha=-.04,chi=.8):
    return {name:(value,(0.,)*6) for name,value in zip(PROVIDERS,(S,lc,lb,theta,alpha,chi))}
def manufactured(z):
    n,p,H,e,a,ell=z;r=2*math.exp(ell);S=.3*r*(1+.1*p)
    return {'S':(S,(0.,.03*r,0.,0.,0.,S)),
      'lambda_c':(.2*(1+.05*H),(0.,0.,.01,0.,0.,0.)),
      'lambda_b':(.03,(0.,)*6),'theta':(.04+.01*n,(.01,0.,0.,0.,0.,0.)),
      'alpha':(-.04+.005*e,(0.,0.,0.,.005,0.,0.)),
      'chi':(.8*(1+.02*n),(.016,0.,0.,0.,0.,0.))}


def run_tests():
    checks=[]
    checks.append({'name':'two_branch_integer_baryon_charge_lepton_nulls',
      'pass':all(sum(a*b for a,b in zip(row,column))==0 for row in (BARYON,CHARGE,LEPTON) for column in (NU_C,NU_B))})
    lower=[]
    for i in range(5):
        z=list(X);z[i]=0.;v=evaluate(z,constants(theta=-.3,alpha=-.1),2.,BOX)
        lower.append(v['rhs'][i]>=0)
    at_zero=evaluate((0.,2.,3.,4.,5.,0.),constants(),2.,BOX)
    checks.append({'name':'source_driven_zero_parent_and_all_lower_faces','pass':all(lower) and close(at_zero['rhs'][0],.8*.6/2)})
    constant=evaluate(X,constants(),2.,BOX)
    expected=.8*(.3-.23),.8*.2,.8*.03,.8*.2,.8*.23,.8*(-.04)
    checks.append({'name':'fixed_comoving_reference_and_clock_reduction','pass':all(close(a,b) for a,b in zip(constant['rhs'],expected))})
    actual_ell=constant['jacobian'][0][5];expected_ell=-.8*.6/2
    physical=[]
    for i,value in enumerate(constant['rhs'][:5]):
        density_rate=2*value/.8+2*(-.04)*X[i]
        event=(.2*NU_C[i]+.03*NU_B[i])*2*X[0]
        physical.append(close(density_rate,(.6 if i==0 else 0)+event-.04*2*X[i]))
    checks.append({'name':'physical_density_quotient_and_missing_reference_derivative_control',
      'pass':close(actual_ell,expected_ell) and not close(0.,expected_ell) and all(physical)})
    jets=manufactured(X);actual=evaluate(X,jets,2.,BOX);n,p,H,e,a,ell=X
    L=.2*(1+.05*H);K=L+.03;d=.01*n+.005*e;chi=.8*(1+.02*n)
    g=(.3*(1+.1*p)-(K+d)*n,L*n-d*p,.03*n-d*H,L*n-d*e,K*n-d*a)
    # Independent reduced expressions cancel S/r before differentiating.
    dg=((-(K+d)-.01*n,.03,-.01*n,-.005*n,0.,0.),
        (L-.01*p,-d,.01*n,-.005*p,0.,0.),
        (.03-.01*H,0.,-d,-.005*H,0.,0.),
        (L-.01*e,0.,.01*n,-d-.005*e,0.,0.),
        (K-.01*a,0.,.01*n,-.005*a,-d,0.))
    expected_j=tuple(tuple(chi*dg[i][j]+(.016*g[i] if j==0 else 0) for j in range(6)) for i in range(5))
    expected_j+=( (.016*(-.04+.005*e),0.,0.,chi*.005,0.,0.), )
    direction=(1.,-.3,.4,.2,-.1,.7)
    independent_jvp=tuple(sum(a*b for a,b in zip(row,direction)) for row in expected_j)
    checks.append({'name':'nonconstant_provider_full_analytic_jacobian_and_jvp',
      'pass':all(close(a,b) for row,expected in zip(actual['jacobian'],expected_j) for a,b in zip(row,expected)) and all(close(a,b) for a,b in zip(jvp(actual['jacobian'],direction),independent_jvp)),
      'rhs':actual['rhs'],'jacobian':actual['jacobian'],'source_kind':'synthetic_manufactured_analytic_jets'})
    ledger_checks=[];s=actual['source_per_reference']
    for weights in (BARYON,CHARGE,LEPTON):
        stock=sum(w*x for w,x in zip(weights,X));external=weights[0]
        expected_rhs=chi*(external*s-d*stock)
        ledger_checks.append(close(sum(w*f for w,f in zip(weights,actual['rhs'])),expected_rhs))
        for j in range(6):
            ds=jets['S'][1][j]/2-(s if j==5 else 0)
            dd=jets['theta'][1][j]+jets['alpha'][1][j]
            expected_derivative=jets['chi'][1][j]*(external*s-d*stock)+chi*(external*ds-dd*stock-d*(weights[j] if j<5 else 0))
            ledger_checks.append(close(sum(weights[i]*actual['jacobian'][i][j] for i in range(5)),expected_derivative))
    neutral=evaluate((1.,0.,0.,0.,0.,0.),constants(S=0.,lc=.25,lb=.125,theta=.125,alpha=-.125,chi=.5),2.,BOX)
    ledger_checks.extend(sum(w*f for w,f in zip(row,neutral['rhs']))==0 for row in (CHARGE,LEPTON))
    checks.append({'name':'RHS_and_all_Jacobian_columns_count_ledgers','pass':all(ledger_checks)})
    oracle_checks=[];oracle_results=[]
    for lc,lb in ((0.,0.),(0.,.03),(.2,.03)):
        value=lifted_oracle(X[:5],0.,2.,.3,lc,lb,.75,.2,-.1)
        changed=lifted_oracle(tuple(v/5 for v in X[:5]),0.,10.,.3/5,lc,lb,.75,.2,-.1)
        u=value['lifted_counts'];oracle_results.append(value)
        oracle_checks.append(all(v>=0 for v in value['state'][:5]))
        for row,target in ((BARYON,sum(w*x for w,x in zip(BARYON,X))+.3*.75),(CHARGE,sum(w*x for w,x in zip(CHARGE,X))),(LEPTON,sum(w*x for w,x in zip(LEPTON,X)))):
            oracle_checks.append(close(sum(w*x for w,x in zip(row,u)),target,5e-13))
        oracle_checks.extend(close(a,b,5e-13) for a,b in zip(value['physical_densities'],changed['physical_densities']))
    gauge=evaluate(tuple(v/5 for v in X[:5])+(0.,),constants(),10.,BOX)
    oracle_checks.extend(close(a/5,b) for a,b in zip(constant['rhs'][:5],gauge['rhs'][:5]))
    checks.append({'name':'lifted_exact_oracle_and_physical_reference_invariance','pass':all(oracle_checks),'restricted_oracle_results':oracle_results})
    def rejects(fn):
        try:fn()
        except (ValueError,TypeError):return True
        return False
    invalid=[]
    for name in PROVIDERS:
        missing=constants();del missing[name]
        invalid.append(rejects(lambda m=missing:evaluate(X,m,2.,BOX)))
    short=constants();short['S']=(.6,(0.,)*5);invalid.append(rejects(lambda:evaluate(X,short,2.,BOX)))
    for name in ('S','lambda_c','lambda_b','chi'):
        wrong=constants();wrong[name]=(-1.,(0.,)*6)
        invalid.append(rejects(lambda w=wrong:evaluate(X,w,2.,BOX)))
    invalid.extend((rejects(lambda:evaluate(X,constants(chi=0),2.,BOX)),rejects(lambda:evaluate(X,constants(),0.,BOX)),rejects(lambda:check_domain(X,BOX,2.,labels=STATE[:3]+('x_e_th',)+STATE[4:]))))
    wide={'lower':(0.,)*5+(-1000.,),'upper':(10.,)*5+(1000.,)}
    invalid.extend(rejects(lambda ell=ell:check_domain(X[:5]+(ell,),wide,2.)) for ell in (-1000.,1000.))
    prefix=list(X);calls=[]
    def native_wrapper(state):
        check_domain(state,BOX,2.);calls.append('provider_called');return evaluate(state,constants(),2.,BOX)
    invalid.append(rejects(lambda:native_wrapper((11.,)+X[1:])))
    invalid.append(not calls and prefix==list(X))
    checks.append({'name':'missing_jet_domain_clock_reference_pool_and_prefix_guards','pass':all(invalid),'controls_passed':len(invalid)})
    return checks
