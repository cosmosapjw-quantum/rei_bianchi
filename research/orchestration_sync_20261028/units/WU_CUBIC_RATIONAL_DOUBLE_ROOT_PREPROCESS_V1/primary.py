"""Exact factor-product Bernstein subdivision on the frozen rational family."""
import argparse,json,re
from fractions import Fraction as F

def rat(s):
    if not isinstance(s,str) or not re.fullmatch(r'[+-]?\d+(?:/[1-9]\d*)?',s): raise ValueError('exact rational string required')
    n=F(s)
    if max(abs(n.numerator).bit_length(),n.denominator.bit_length())>64: raise ValueError('input bit limit')
    return n

def calc(z):
    r,a,b,t0,t1=[rat(z[k]) for k in ('r','a','b','t0','t1')]
    if not 0<r<1 or b<0 or a+b<0 or t1<=t0: raise ValueError('outside frozen domain')
    powers=[b*r*r,a*r*r-2*b*r,b-2*a*r,a]
    cells=[]
    for u,v in [(F(0),r),(r,F(1))]:
        q0,q1=u-r,v-r;l0,l1=a*u+b,a*v+b
        c=[q0*q0*l0,(q0*q0*l1+2*q0*q1*l0)/3,(2*q0*q1*l1+q1*q1*l0)/3,q1*q1*l1]
        if not all(x>=0 for x in c): raise AssertionError('negative split coefficient')
        cells.append({'interval':[str(u),str(v)],'B3':list(map(str,c)),'integral_x':str((v-u)*sum(c)/4)})
    ix=sum(F(c['integral_x']) for c in cells)
    allv=powers+[ix,ix*(t1-t0)]+[F(s) for c in cells for s in c['B3']]
    if any(max(abs(v.numerator).bit_length(),v.denominator.bit_length())>4096 for v in allv):raise ValueError('derived bit limit')
    return {'id':z['id'],'original_time_interval':[str(t0),str(t1)],'memory_origin':str(t0),'normalized_knots':['0',str(r),'1'],'power_x':list(map(str,powers)),'cells':cells,'integral_x':str(ix),'integrated_forcing':str(ix*(t1-t0)),'units':{'coefficient':'s^-1','time':'s','integrated_forcing':'1'}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output');args=p.parse_args();data=json.load(open(args.input))
    if len(data['cases'])>16:raise ValueError('case limit')
    rows=[calc(c) for c in data['cases']]; controls=[]
    for c in data['rejections']:
        try: calc(c)
        except (ValueError,ZeroDivisionError) as e:controls.append({'id':c['id'],'rejected':True,'reason':str(e)})
        else:raise AssertionError('rejection accepted: '+c['id'])
    json.dump({'cases':rows,'rejection_controls':controls,'accepted_count':len(rows),'rejected_count':len(controls)},open(args.output,'w'),indent=2)
if __name__=='__main__':main()
