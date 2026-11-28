#!/usr/bin/env python3
"""Review only the newly supplied first-half inverse readiness certificate."""
import argparse,datetime,hashlib,json,pathlib,struct,time
from fractions import Fraction as F
def main(a):
    t=time.perf_counter();p=a.parent15/'inputs/phys14/inputs/ncp07/results/first_half/SOURCE_BOX.json'
    blob=p.read_bytes();src=json.loads(blob);rec=json.loads(a.preflight.read_text())
    q=lambda x:F(*map(int,x));bit=lambda x:F(struct.unpack('>d',bytes.fromhex(x))[0])
    scales=[F(1),F(1),F(1),F(27,2)];B=[]
    for i in range(4):
        row=[]
        for j in range(4):
            z=src['A_Gg'][i][j];v=F(i==j)
            row.append(max(abs(v-bit(z['lo_bits'])),abs(v-bit(z['hi_bits']))))
        B.append(row)
    bounds=[sum(B[i][j]*scales[j]/scales[i] for j in range(4)) for i in range(4)]
    assert [q(x) for x in rec['S1_exact']]==scales
    assert [[q(x) for x in row] for row in rec['B1_exact']]==B
    assert [q(x) for x in rec['weighted_row_bounds_exact']]==bounds
    assert q(rec['q1_exact'])==max(bounds)<F(rec['outward_decimal_q1_upper'])<1
    assert rec['input']['sha256']==hashlib.sha256(blob).hexdigest()
    assert rec['pure_response_application']=='not_run'
    result={'schema':'WU088_HH_PHYS18_INDEPENDENT_CURVATURE_PREFLIGHT_V1','status':'PASS',
            'readiness':'first-half linear inverse only; pure response remains not_run',
            'original_input_sha256':hashlib.sha256(blob).hexdigest(),'checked_B_entries':16,
            'checked_weighted_rows':4,'q1_exact':str(max(bounds)),'q1_display':float(max(bounds)),
            'preflight_sha256':hashlib.sha256(a.preflight.read_bytes()).hexdigest(),
            'elapsed_seconds':time.perf_counter()-t,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_calls':0,'root_solves':0,'history_replays':0}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ('parent15','preflight','output'):p.add_argument('--'+k,type=pathlib.Path,required=True)
    main(p.parse_args())
