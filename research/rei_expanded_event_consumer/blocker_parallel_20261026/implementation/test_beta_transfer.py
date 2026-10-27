"""Eight prescribed groups; root authorization is required for execution."""
import math
from beta_transfer import beta_transfer, OUTPUT_ORDER, BETA_STOICHIOMETRY, INVARIANT_ROWS


def _values(result):return tuple(result[name] for name in OUTPUT_ORDER)
def _close(a,b):return abs(a-b) <= 5e-13*max(1.,abs(a)+abs(b))
def _conserved(result,parent,source,h):
    return _close(result['parent']+result['beta_events']+result['competing_removals'],parent+source*h)


def run_tests():
    checks=[]
    r=beta_transfer(2,3,4,5,0)
    checks.append({'name':'zero_duration','pass':_values(r)==(2.,0.,0.,0.)})
    r=beta_transfer(3,5,0,0,2)
    checks.append({'name':'zero_rates_exact_limits','pass':_values(r)==(13.,16.,0.,0.) and r['jacobian_parent_source']==((1.,2.),(2.,2.),(0.,0.),(0.,0.))})
    r=beta_transfer(2,0,1,0,1)
    checks.append({'name':'pure_decay','pass':_close(r['parent'],2/math.e) and _close(r['beta_events'],2*(1-1/math.e)) and r['competing_removals']==0})
    full=beta_transfer(3,5,.2,.3,2)
    first=beta_transfer(3,5,.2,.3,.75);second=beta_transfer(first['parent'],5,.2,.3,1.25)
    composition=_close(full['parent'],second['parent']) and all(_close(full[key],first[key]+second[key]) for key in OUTPUT_ORDER[1:])
    checks.append({'name':'source_competing_and_semigroup','pass':_conserved(full,3,5,2) and _close(full['beta_events']/full['competing_removals'],.2/.3) and composition})
    branches=[]
    for beta,other in ((1e-12,0),(.03,.07),(1,0),(1000,0)):
        r=beta_transfer(1,2,beta,other,1)
        branches.append(all(v>=0 and math.isfinite(v) for v in _values(r)) and _conserved(r,1,2,1))
    checks.append({'name':'small_series_crossover_and_stiff','pass':all(branches),'cases_passed':branches})
    base=beta_transfer(3,5,.2,.3,2);jp=beta_transfer(4,5,.2,.3,2);js=beta_transfer(3,6,.2,.3,2)
    differences=[(jp[key]-base[key],js[key]-base[key]) for key in OUTPUT_ORDER]
    checks.append({'name':'analytic_parent_source_jacobian','pass':all(_close(a,b) for actual,expected in zip(differences,base['jacobian_parent_source']) for a,b in zip(actual,expected))})
    invariant=all(sum(a*b for a,b in zip(row,column))==0 for row in INVARIANT_ROWS for column in BETA_STOICHIOMETRY)
    zeros=beta_transfer(0,0,.2,.3,2);tiny=beta_transfer(1e-300,0,.2,.3,2);driven=beta_transfer(0,5,.2,.3,2)
    checks.append({'name':'stoichiometry_zero_tiny_and_source_driven_parent','pass':invariant and all(v==0 for v in _values(zeros)) and all(v>=0 for v in _values(tiny)) and driven['parent']>0 and driven['beta_events']>0})
    bad=[(1,1,1,None,1),(1,1,None,1,1)]
    for index in range(5):
        for value in (-1.,math.nan,math.inf,-math.inf):
            case=[1.,1.,1.,1.,1.];case[index]=value;bad.append(tuple(case))
    bad.extend([(1.,1.,1e308,1e308,1.),(1.,1.,1e308,0.,1e308),(1e308,1e308,0.,0.,1e308)])
    rejected=[]
    for case in bad:
        try:beta_transfer(*case)
        except ValueError:rejected.append(True)
        else:rejected.append(False)
    try:beta_transfer(1,1,1,h=1)
    except TypeError:rejected.append(True)
    else:rejected.append(False)
    checks.append({'name':'missing_negative_nonfinite_rejected','pass':all(rejected),'rejected_count':sum(rejected),'case_count':len(rejected)})
    return checks
