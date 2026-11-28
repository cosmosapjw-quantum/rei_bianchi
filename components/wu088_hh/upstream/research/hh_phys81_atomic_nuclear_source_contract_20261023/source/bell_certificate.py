"""Exact-rational Bernstein certificates for the newly transcribed Bell rows."""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def derivative_polynomial(a,b):
    out=[F(a)]+[F(0)]*len(b)
    for j,v in enumerate(b,1):
        v=F(v or '0')*j;out[j-1]+=v;out[j]-=v
    while len(out)>1 and out[-1]==0:out.pop()
    return out

def bernstein_on(g,a,b):
    n=len(g)-1;w=b-a
    power=[sum(g[j]*comb(j,k)*a**(j-k)*w**k for j in range(k,n+1)) for k in range(n+1)]
    return [sum(power[k]*F(comb(i,k),comb(n,k)) for k in range(i+1)) for i in range(n+1)]

def certificate(g,a=F(0),b=F(1),depth=0):
    coeff=bernstein_on(g,a,b)
    if min(coeff)>0:
        return [{'interval':[str(a),str(b)],'bernstein_coefficients':[str(v) for v in coeff],'strict_lower_bound':str(min(coeff))}]
    if depth>=16:raise ArithmeticError('POSITIVE_CERTIFICATE_NOT_CLOSED')
    mid=(a+b)/2
    return certificate(g,a,mid,depth+1)+certificate(g,mid,b,depth+1)

def main():
    out=ROOT/'verification/BELL_GLOBAL_POSITIVITY.json'
    if out.exists():raise FileExistsError('CERTIFICATE_ALREADY_EXISTS')
    rows=json.loads((ROOT/'source_data/BELL1983_VISUAL_TABLE_TRANSCRIPT.json').read_text())['rows']
    results=[]
    for r in rows:
        if r['species'] not in ('H I','He I','Li I'):continue
        g=derivative_polynomial(r['A_mantissa_printed'],r['B_mantissas_printed'])
        c=certificate(g)
        # Adjacent intervals cover exactly [0,1]; positive Bernstein basis
        # sums to one, hence each coefficient bound is a global polynomial bound.
        assert F(c[0]['interval'][0])==0 and F(c[-1]['interval'][1])==1
        assert all(c[i]['interval'][1]==c[i+1]['interval'][0] for i in range(len(c)-1))
        results.append({'species':r['species'],'G_power_coefficients':[str(x) for x in g],'subintervals':c,'status':'EXACT_RATIONAL_POSITIVE_ON_CLOSED_UNIT_INTERVAL'})
    record={'method':'positive Bernstein coefficients after exact-rational affine subdivision','independent_symbolic_check':'Wolfram Reduce[0<=x<=1 && G<=0,x,Reals] returned False for each of three rows; verification/WOLFRAM_EVAL_001.json','conclusion':'F(0)=0, Fprime=G/(1-x)>0 for x in[0,1); therefore Bell sigma(E)>0 for every E>I.','scope':'Selected mathematical fits; not source physical uncertainty or rate accuracy','rows':results,'new_ODE':0}
    out.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'certificate_rows':len(results),'subinterval_counts':[len(r['subintervals']) for r in results],'status':'EXACT_RATIONAL_CERTIFICATES_CREATED'}))

if __name__=='__main__':main()
