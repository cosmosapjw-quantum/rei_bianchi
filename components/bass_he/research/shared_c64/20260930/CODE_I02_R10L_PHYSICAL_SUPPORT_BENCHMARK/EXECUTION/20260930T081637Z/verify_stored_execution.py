"""Arithmetic-only readback; no contour or rotation integration is executed."""
import hashlib, json
import numpy as np
from execute_real_support import HERE, atomic, canonical, sha, BRANCH_NAMES
from endpoint_quadrature import nodes, reduce
from bass_he.geometry import _gk15_reduce


def main():
    query=json.loads((HERE/'QUERY_CONTRACT.json').read_text())
    result=json.loads((HERE/'C_RESULT.json').read_text())
    values={}
    for path in sorted((HERE/'integrands').glob('*.json')):
        item=json.loads(path.read_text())
        for h,row in zip(item['rho_hex'],item['components']):
            if h in values and values[h]!=row:raise ValueError('conflicting query values')
            values[h]=row
    cuts=[float.fromhex(x) for x in query['cutpoints_hex']]
    rhos=[float.fromhex(x) for x in query['tail_rho_hex']]
    tail=np.zeros(18);errors=np.zeros(18)
    for i,(a,b) in enumerate(zip(cuts[1:-1],cuts[2:])):
        f=np.array([values[h] for h in query['tail_rho_hex'][15*i:15*i+15]])
        estimate=_gk15_reduce(a*a,b*b,f)
        tail+=estimate['high'];errors+=estimate['error']
    scale=float.fromhex(query['endpoint_q_scale_hex'])
    for aa,bb in result['q_intervals']:
        a,b=float.fromhex(aa),float.fromhex(bb);q=nodes(a,b);r=scale*np.sinh(q)
        f=np.array([values[float(x).hex()] for x in r])
        transformed=(np.pi*scale*scale*np.sinh(2*q))[:,None]*f
        hi,err=reduce(a,b,transformed);tail+=hi;errors+=err
    difference=float(np.max(abs(tail-np.array(result['integral']))))
    error_difference=float(np.max(abs(errors-np.array(result['error_estimate']))))
    if difference>5e-14 or error_difference>1e-14:raise ValueError('stored integral mismatch')
    cache=[]
    for path in sorted((HERE/'geometry_cache').glob('*.json')):
        item=json.loads(path.read_text());key,record=item['key'],item['record']
        if path.stem!=hashlib.sha256(canonical(key)).hexdigest():raise ValueError('cache keyhash')
        if item['record_sha256']!=hashlib.sha256(canonical(record)).hexdigest():raise ValueError('payloadhash')
        if key['branch']!=record['branch'] or key['rho_hex']!=record['rho_hex']:raise ValueError('pairidentity')
        k=BRANCH_NAMES.index(key['branch']);rho=float.fromhex(key['rho_hex'])
        if rho>=float.fromhex(query['real_support_hex'][k]) or rho>=float.fromhex(query['extended_support_hex'][k]):
            raise ValueError('outside domain')
        cache.append({'file':path.name,'sha256':sha(path)})
    if len(cache)!=result['counts']['new_delta_calls']:raise ValueError('call count/cache cardinality')
    check={'status':'STORED_EXECUTION_READBACK_PASS','new_contour_calls_for_verification':0,
           'new_rotation_integrations_for_verification':0,'integral_max_absolute_difference':difference,
           'error_estimate_max_absolute_difference':error_difference,'new_cache_records_verified':len(cache),
           'unique_rho_hex_consumed':len(values),'new_cache_inventory':cache,
           'not_claimed':'independent physics/contour validation; this is saved-record arithmetic and content integrity only'}
    atomic(HERE/'STORED_EXECUTION_VERIFICATION.json',check)
    print(json.dumps({k:v for k,v in check.items() if k!='new_cache_inventory'}))


if __name__=='__main__':main()
