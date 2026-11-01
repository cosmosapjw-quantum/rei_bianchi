#!/usr/bin/env python3
"""Independent stdlib, single-pass verification of original 26-event snapshot proxy.

Does not import the primary NumPy/Pandas implementation. No claim of independent
astrophysical model or validated one-tick state evolution.
"""
import csv,gzip,hashlib,io,json,math,zipfile
from decimal import Decimal,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FIELDS={"HII":('x_HII','dx_HII_dt_mid_per_s','x_HII'),
"HeII":('x_HeII','dx_HeII_dt_mid_per_s','x_HeII'),
"HeIII":('x_HeIII','dx_HeIII_dt_mid_per_s','x_HeIII'),
"electron":('free_electrons_per_H','dxe_dt_mid_per_s','xe_per_H')}
SHA='44b322e2ebbd7b915b6958709136d5dc041e2468b0d71f0eb67da013f6aad535'
SHA_STATE='48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7'
SRC='original_26event_LOCAL_NEUTRAL_HAZARD_PRIMARY_'
ST='NODEWISE_LOCAL_NEUTRAL_HAZARD_PRIMARY_46080_PHYSICAL.csv.gz'
H=Decimal('779495799866.9248')

def stream(zip_,name):
    return csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(zip_.read(name))),encoding='utf-8',newline=''))

def run(source_dir=None,out=None):
    source_dir=Path(source_dir) if source_dir else ROOT/'source'
    a=source_dir/'REI_PR321_VERIFIED_HEAD_26EVENT_SOURCE.zip'
    b=source_dir/'REI_PR320_ORIGINAL_TICK160_NODE_PHYSICS.zip'
    if hashlib.sha256(a.read_bytes()).hexdigest()!=SHA or hashlib.sha256(b.read_bytes()).hexdigest()!=SHA_STATE:
        raise ValueError('INDEPENDENT_SOURCE_HASH_FAILURE')
    with zipfile.ZipFile(a) as z,zipfile.ZipFile(b) as src:
        src0=list(stream(z,SRC+'initial.csv.gz'))
        src1=list(stream(z,SRC+'accepted_tick160.csv.gz'))
        interval=list(stream(src,ST))
    assert len(src0)==len(src1)==len(interval)==46080
    sums={c:[[],[],0] for c in FIELDS}
    samples=[0,1,3,127,1023,2048,2571,4607,4608,8191,12000,20011,30007,38374,40959,46079]
    max_decimal_error=0.0
    for i,(r0,r1,box) in enumerate(zip(src0,src1,interval)):
        if int(r0['node'])!=i or int(r1['node'])!=i or int(box['node'])!=i:raise ValueError('NODE_MISALIGN')
        for c,(col,force,source_col) in FIELDS.items():
            y0=float(r0[col]);y1=float(r1[col])
            src_est=.5*float(H)*(float(r0[force])+float(r1[force]))
            gap=y1-y0-src_est
            interval_low=float(box[source_col+'_lo'])-y0
            interval_high=float(box[source_col+'_hi'])-y0
            outside=src_est<interval_low or src_est>interval_high
            sums[c][0].append(abs(gap));sums[c][1].append(abs(y1-y0));sums[c][2]+=int(outside)
            if i in samples:
                with localcontext() as ctx:
                    ctx.prec=65
                    dy=Decimal(r1[col])-Decimal(r0[col]); f0=Decimal(r0[force]); f1=Decimal(r1[force]); d=dy-H*(f0+f1)/2
                    max_decimal_error=max(max_decimal_error,abs(float(d)-gap))
    summary=json.loads((ROOT/'results/SUMMARY.json').read_text())
    results={}
    for c,(res,dx,count) in sums.items():
        # Independent precise arithmetic aggregation over all original rows.
        ratio=math.fsum(res)/math.fsum(dx)
        expected=summary['channel_diagnostics'][c]
        assert count==expected['nominal_outside_original_accepted_interval_count'],(c,count,expected)
        assert math.isclose(ratio,expected['sum_abs_residual_over_sum_abs_state_change'],rel_tol=7e-11,abs_tol=2e-15),(c,ratio)
        results[c]={'total_abs_gap_ratio':ratio,'outside':count,'fraction':count/46080}
    obj={'schema':'REI_26EVENT_SOURCE_SECANT_INDEPENDENT_AUDIT_V1',
      'source_verified_sha256':SHA,'source_state_verified_sha256':SHA_STATE,
      'source_endpoints_checked':46080,'selected_decimal_65digit_nodes':len(samples),'decimal_max_abs_gap_discrepancy':max_decimal_error,
      'check':'PASS','per_channel':results,'constraint':'diagnostic only; no accepted joint 26-event trajectory'}
    path=Path(out) if out else ROOT/'results/INDEPENDENT_AUDIT.json'
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print(json.dumps(obj,indent=2))
    return obj
if __name__=='__main__':run()
