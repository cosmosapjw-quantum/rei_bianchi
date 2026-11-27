"""Decode complete one-line transport only; preserve all first failures.
No scientific arithmetic is performed by this transport checker.
"""
from pathlib import Path
import argparse, hashlib, json, re

def decode(raw):
    found=[]
    def visit(x):
        if isinstance(x,dict):
            if set(('p','sha256','bytes')) <= set(x): found.append(x)
            for y in x.values(): visit(y)
        elif isinstance(x,list):
            for y in x: visit(y)
        elif isinstance(x,str):
            candidates=[x.strip()]
            candidates += [x[m.end():].lstrip() for m in re.finditer(r'Out\[\d+\]\s*=\s*',x)]
            for candidate in candidates:
                try: value,end=json.JSONDecoder().raw_decode(candidate)
                except (ValueError,TypeError): continue
                if isinstance(value,(dict,list)): visit(value)
                elif isinstance(value,str) and value != x: visit(value)
    visit(raw)
    unique={json.dumps(x,sort_keys=True):x for x in found}
    if len(unique)!=1: raise ValueError(f'Expected exactly one complete transport; got {len(unique)}')
    envelope=next(iter(unique.values()));p=envelope['p']
    if not isinstance(p,str) or not p.isascii() or '\n' in p or '\r' in p: raise ValueError('Payload must be one-line ASCII')
    if hashlib.sha256(p.encode()).hexdigest()!=envelope['sha256']: raise ValueError('Exact payload SHA mismatch')
    if len(p.encode())!=envelope['bytes']: raise ValueError('Exact payload byte count mismatch')
    encoded=json.dumps(envelope,separators=(',',':'),ensure_ascii=True)
    if len(json.dumps(encoded,ensure_ascii=True,separators=(',',':')).encode())>8000: raise ValueError('Escaped transport exceeds 8000 bytes')
    return envelope,json.loads(p)

def inspect(payload,kind,unit):
    issues=[]
    if payload.get('status')!='PASS': issues.append('runtime_status_not_PASS')
    if payload.get('failures')!=[]: issues.append('nonempty_failures')
    expected=[36,6,23,1017,1017] if kind=='recovery' else [3,10,82,82]
    if payload.get('counts')!=expected: issues.append('unexpected_counts')
    n=1017 if kind=='recovery' else 82
    if payload.get('bits')!='1'*n: issues.append('assertion_bits_incomplete_or_failed')
    if kind=='recovery':
        order=json.loads((unit/'source_data/PHYS85_EXPECTED_ORDER.json').read_text())
        if payload.get('label_sha256')!=order['label_sha256']: issues.append('label_order_sha_mismatch')
        if payload.get('complete') is not True: issues.append('incomplete_certificate')
        for key,length in [('triples',9),('covariances',3),('event_residual_sumabs',36),('ensemble_residual_sumabs',6),('guard_tags',23)]:
            if len(payload.get(key,[]))!=length: issues.append(key+'_length')
        for key in ['event_residual_sumabs','ensemble_residual_sumabs']:
            if any(str(x)!='0' for x in payload.get(key,[])): issues.append(key+'_nonzero')
    else:
        if len(payload.get('rows',[]))!=3: issues.append('moment_row_count')
        if len(payload.get('labels',[]))!=82: issues.append('moment_label_count')
        for row in payload.get('rows',[]):
            if any(str(x)!='0' for x in row.get('residuals',[])): issues.append('moment_residual_nonzero')
            if str(row.get('source_coefficient_residual'))!='0': issues.append('source_residual_nonzero')
        if any(str(x)!='0' for x in payload.get('symbolic_residuals',[])): issues.append('symbolic_residual_nonzero')
    return issues

def main():
    ap=argparse.ArgumentParser();ap.add_argument('kind',choices=['recovery','moments']);ap.add_argument('attempt_dir',type=Path);args=ap.parse_args()
    attempt=args.attempt_dir;unit=Path(__file__).resolve().parents[1]
    try:
        raw=json.loads((attempt/'RAW_WOLFRAM_RESPONSE.json').read_text())
        envelope,payload=decode(raw)
        (attempt/'COMPLETE_CERTIFICATE.json').write_text(json.dumps(payload,indent=2,ensure_ascii=True)+'\n')
        (attempt/'EXACT_PAYLOAD.txt').write_text(envelope['p'])
        issues=inspect(payload,args.kind,unit)
        receipt={'status':'TRANSPORT_COMPLETE_SCOPE_CHECKS_PASS' if not issues else 'TRANSPORT_COMPLETE_SCOPE_CHECKS_FAILED','issues':issues,'sha256':envelope['sha256'],'payload_bytes':envelope['bytes'],'scientific_admission':'PENDING_ASTRA_REVIEW'}
    except Exception as exc:
        receipt={'status':'OUTPUT_PARSE_FAILURE_PRESERVED','exception_type':type(exc).__name__,'message':str(exc),'scientific_admission':'NOT_ISSUED'}
    (attempt/'PARSE_AND_SCOPE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    return 0 if receipt['status']=='TRANSPORT_COMPLETE_SCOPE_CHECKS_PASS' else 1
if __name__=='__main__': raise SystemExit(main())
