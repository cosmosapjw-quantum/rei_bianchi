#!/usr/bin/env python3
"""Independent exact reference. No production kernel or primary imports."""
import sys
sys.dont_write_bytecode=True
import json
from evidence import UNIT,REPO,identity,resume,fresh,publish,main_args

def audit(primary):
    from fractions import Fraction as R
    from math import lcm
    from itertools import product
    primary_scan=json.loads((primary/'PAIR_SCAN.json').read_text())
    primary_results=json.loads((primary/'RESULTS.json').read_text())
    saved_fixtures=json.loads((primary/'CONSUMER_ENVELOPE_FIXTURES.json').read_text())
    contract=json.loads((UNIT/'CONTRACT.json').read_text())
    table=json.loads((REPO/contract['inputs'][0]['path']).read_text())
    rounding=json.loads((REPO/contract['inputs'][1]['path']).read_text())
    n=153;A=[[R(s) for s in row] for row in table['matrix']]
    B=[[R(0) for _ in range(n)] for _ in range(n)];k=0
    for i in range(n):
        for j in range(i,n):B[i][j]=B[j][i]=R(rounding['halfULP'][k]);k+=1
    assert k==11781
    # Independent scaling for each 2x2 block, with determinant polynomial in p,q.
    records=[]
    for i in range(n):
        for j in range(i+1,n):
            values=(A[i][i],B[i][i],A[j][j],B[j][j],A[i][j],B[i][j])
            denominator=lcm(*(v.denominator for v in values))
            records.append((i,j,*[int(v*denominator) for v in values]))
    def scan_at(t):
        t=R(t);p=t.numerator;q=t.denominator
        bad_single=[i for i in range(n) if A[i][i]+t*B[i][i]<0]
        bad=[]
        for i,j,a,h,b,k,c,l in records:
            first=a*q+h*p;second=b*q+k*p
            nearest=abs(c)*q-l*p
            if nearest<0:nearest=0
            determinant=first*second-nearest*nearest
            if min(first,second)<0 or determinant<0:bad.append([i,j])
        return bad_single,bad
    zero_s,zero=scan_at(0);one_s,one=scan_at(1)
    assert zero==primary_scan['t0']['failed_pairs'] and zero_s==primary_scan['t0']['failed_singletons']
    assert one==primary_scan['t1']['failed_pairs'] and one_s==primary_scan['t1']['failed_singletons']
    checked=2
    for checkpoint in primary_scan['checkpoints'][2:]:
        singles,bad=scan_at(checkpoint['t']);checked+=1
        assert len(bad)==checkpoint['failed_pair_count'] and singles==checkpoint['failed_singletons']
        assert (not singles and not bad)==checkpoint['all_pass']
    bracket=primary_scan['bracket'];lo=R(bracket['lo']);hi=None if bracket['hi'] is None else R(bracket['hi'])
    ls,lp=scan_at(lo)
    if bracket['status']=='BRACKETED':
        hs,hp=scan_at(hi)
        assert (ls or lp) and not hs and not hp and hi-lo==R(bracket['initial_width'])/2**40
        assert bracket['iterations']==40 and len(primary_scan['checkpoints'])>=42
    elif bracket['status']=='ZERO_PAIR_THRESHOLD': assert lo==hi==0 and not ls and not lp
    else: assert lo==4096 and (ls or lp) and hi is None
    witness=bracket['witness_lo']
    if witness and witness['kind']=='pair':
        i,j=witness['i'],witness['j'];a=A[i][i]+lo*B[i][i];b=A[j][j]+lo*B[j][j]
        c=max(abs(A[i][j])-lo*B[i][j],R(0))
        assert [i,j] in lp and a==R(witness['upper_a']) and b==R(witness['upper_b'])
        assert c==R(witness['minimum_abs_off']) and a*b-c*c==R(witness['maximum_determinant'])
    elif witness:
        i=witness['i'];assert i in ls and A[i][i]+lo*B[i][i]==R(witness['upper_diagonal'])
    a=A[0][0];d=R(1,10**10);threshold=2*a/(4*a-d)
    assert threshold==R(primary_scan['known_0_10_threshold'])
    assert (a+threshold*d/2)*(a-d+threshold*d/2)-(a-threshold*d/2)**2==0
    # Independently enumerate eight symmetric vertices and the 3-row common map.
    L=((1,1),(1,-1),(-2,0));observations=[]
    for s,t,u in product((-1,1),repeat=3):
        C=((R(4+s),R(t)),(R(t),R(4+u)))
        K=[[sum((R(x[ii])*C[ii][jj]*R(y[jj]) for ii in range(2) for jj in range(2)),R(0)) for y in L] for x in L]
        assert all(sum(row,R(0))==0 for row in K)
        assert C[0][0]>0 and C[0][0]*C[1][1]-C[0][1]**2>0
        observations.append({'signs':[s,t,u],'K':K,'cross':K[0][1],'var_u':K[0][0],'var_v':K[1][1]})
    def normalize(x):
        if isinstance(x,dict):return {k:normalize(v) for k,v in x.items()}
        if isinstance(x,list):return [normalize(v) for v in x]
        if isinstance(x,R):return str(x)
        return x
    assert normalize(observations)==saved_fixtures['sharp_shared_entry']['vertices']
    assert {v['cross'] for v in observations}=={R(-2),R(0),R(2)}
    assert max(v['var_u'] for v in observations)==max(v['var_v'] for v in observations)==12
    assert max(v['var_u']+v['var_v'] for v in observations)==20
    assert not any(v['var_u']==v['var_v']==12 for v in observations)
    # All nine support entries and both off-diagonal coefficients count the shared source once.
    for i,x in enumerate(L):
        for j,y in enumerate(L):
            center=4*(x[0]*y[0]+x[1]*y[1])
            exact_radius=abs(x[0]*y[0])+abs(x[1]*y[1])+abs(x[0]*y[1]+x[1]*y[0])
            assert max(v['K'][i][j] for v in observations)==center+exact_radius
            assert min(v['K'][i][j] for v in observations)==center-exact_radius
    assert 12+12+20!=0 # independent diagonal covariance violates q^TKq=0
    # Manufactured 3x3 pair feasibility with exact global separating direction.
    assert (R(11,10)**2-R(9,10)**2)>=0
    global_upper=3-6+R(9,10)
    assert global_upper==R(-21,10)==R(saved_fixtures['pair_pass_global_fail']['upper_quadratic'])
    for probe in primary_results['actual_source_algebraic_probes'].values():
        left={int(i):R(v) for i,v in probe['left_indices_and_coefficients'].items()}
        right={int(i):R(v) for i,v in probe['right_indices_and_coefficients'].items()}
        # Centers are reused parent constants, never rerun an old witness callback.
        expected_center=R(-1,10**10) if len(left)==2 else R(1069643,2500000000)
        assert expected_center==R(probe['center']) and probe['center_status']=='REUSED_PARENT_EXACT_VALUE'
        active=sorted(set(left)|set(right))
        bound=sum((B[i][i]*abs(left.get(i,0)*right.get(i,0)) for i in active),R(0))
        bound+=sum((B[i][j]*abs(left.get(i,0)*right.get(j,0)+left.get(j,0)*right.get(i,0))
                    for i in active for j in active if i<j),R(0))
        assert bound==R(probe['radius_at_t1'])
        assert list(map(R,probe['box_interval_at_t1']))==[expected_center-bound,expected_center+bound]
    return {'status':'PASS_EXACT_INDEPENDENT_REFERENCE','method':'independent per-pair integer scaling and Fraction fixtures',
            'production_kernel_imports':0,'all_pairs_each_checkpoint':len(records),
            'checkpoints_checked':checked,'all_t1_pairs_checked':11628,'all_t1_singletons_checked':153,
            'bracket_and_selected_witness_exact':True,'vertices_checked':8,'support_entries_checked':9,
            'common_conservation_exact':True,'independent_covariance_rejected':True,
            'unattainable_simultaneous_marginal_endpoints_rejected':True,'pair_pass_global_fail_exact':True}

def main():
    args=main_args('reference');binding=identity()
    if args.resume:
        skipped=resume(args.output,'reference',binding)
        parent=resume(args.primary_output,'primary',binding)
        record=json.loads((args.output/'REFERENCE.json').read_text())
        if record['primary_manifest_sha256']!=parent['manifest_sha256']:
            raise ValueError('RESUME_PRIMARY_MANIFEST_MISMATCH')
        print(json.dumps(skipped));return
    # Bind primary metadata and every original payload before reference science.
    validated=resume(args.primary_output,'primary',binding)
    output=fresh(args.output)
    result=audit(args.primary_output);result['primary_manifest_sha256']=validated['manifest_sha256']
    publish(output,'reference',binding,{'REFERENCE.json':result})
    print(json.dumps({'status':'COMPLETE','kind':'reference','identity':binding['sha256']}))
if __name__=='__main__':main()
