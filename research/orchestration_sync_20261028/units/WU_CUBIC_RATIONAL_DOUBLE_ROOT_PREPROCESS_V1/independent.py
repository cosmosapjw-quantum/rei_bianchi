"""Independent power expansion, affine substitution, and exact integral oracle."""
import argparse,json,math
from fractions import Fraction as F

def multiply(a,b):
    z=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):z[i+j]+=x*y
    return z

def bern_to_power(c):
    out=[F(0)]*4
    for k in range(4):
        for j in range(4-k):out[k+j]+=c[k]*math.comb(3,k)*math.comb(3-k,j)*(-1)**j
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--primary');p.add_argument('--output');args=p.parse_args();data=json.load(open(args.input));primary=json.load(open(args.primary));checks=[]
    assert len(data['cases'])==len(primary['cases'])
    for case,out in zip(data['cases'],primary['cases']):
        r,a,b,t0,t1=[F(case[k]) for k in ('r','a','b','t0','t1')]
        original=multiply(multiply([-r,F(1)],[-r,F(1)]),[b,a]);assert original==list(map(F,out['power_x']))
        sum_integral=F(0);cell_checks=[]
        for cell in out['cells']:
            u,v=map(F,cell['interval']);h=v-u;c=list(map(F,cell['B3']));sub=[sum(original[k]*math.comb(k,j)*u**(k-j)*h**j for k in range(j,4)) for j in range(4)]
            assert sub==bern_to_power(c)
            expected=[sum(sub[j]*F(math.comb(k,j),math.comb(3,j)) for j in range(k+1)) for k in range(4)]
            assert c==expected and min(c)>=0
            integral=sum(original[k]*(v**(k+1)-u**(k+1))/F(k+1) for k in range(4))
            assert integral==F(cell['integral_x']);sum_integral+=integral
            cell_checks.append({'coefficient_identity':True,'nonnegative':True,'integral':str(integral)})
        unsplit=[sum(original[j]*F(math.comb(k,j),math.comb(3,j)) for j in range(k+1)) for k in range(4)]
        nonzero=any(original);assert not nonzero or min(unsplit)<0
        assert F(out['cells'][0]['B3'][-1])==0==F(out['cells'][1]['B3'][0])
        whole=sum(original[k]/F(k+1) for k in range(4));assert sum_integral==whole==F(out['integral_x']);assert whole*(t1-t0)==F(out['integrated_forcing']);assert out['memory_origin']==str(t0)
        checks.append({'id':case['id'],'cells':cell_checks,'unsplit_B3':list(map(str,unsplit)),'unsplit_negative_witness':nonzero and min(unsplit)<0,'nonzero':nonzero,'whole_integral':str(whole),'pass':True})
    assert all(x['rejected'] for x in primary['rejection_controls']) and len(primary['rejection_controls'])==len(data['rejections'])
    json.dump({'checks':checks,'accepted_count':len(checks),'rejection_count':len(primary['rejection_controls']),'exact_checks_pass':True},open(args.output,'w'),indent=2)
if __name__=='__main__':main()
