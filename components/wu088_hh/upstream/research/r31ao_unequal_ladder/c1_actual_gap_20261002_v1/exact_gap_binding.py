"""C1: frozen predictions and historical B192 values to exact represented gaps.

No HH kernel, predictor, historical comparator or SVD is executed. This module
cannot accept epsilon or promote continuous-target/physical admission.
"""
from pathlib import Path
from fractions import Fraction as Q
import io, json, re, zipfile
from c1_support import BindingError, LOCK_SHA, loads, read_bytes, sha, verify_sources, vendor
from machine_predicate_bridge import E, LIMITS, audit_tokens, token_bits

D = vendor('decoder')
MODELS = ('R31AK','R31Z','R31AD')
FIELDS = {'Dcol':'D_col','Drow':'D_row','K':'K'}
OD_SHA = '7e7b5782cc698a364aeac608620e56c7bfdc64035ffe5dfee501608dae7970df'
JVP_SHA = '53569e92875254e897a7e23b55620cca9c5acf9f86124dc0a73198ad41d1df87'

def document(root,name,*,tokens=False):
    return loads(read_bytes(root,'authority/'+name),tokens=tokens)

def _raw(root, label, shape):
    doc = loads(read_bytes(root,'inputs/'+label+'.exact_dyadic.json'))
    provenance = document(root,label+'.provenance.json')
    if doc.get('schema')!='EXACT_DYADIC_ARRAY_V1' or doc.get('shape')!=list(shape) or len(doc.get('values',[]))!=94:
        raise BindingError('raw canonical shape/schema mismatch')
    canonical = json.dumps(doc,sort_keys=True,separators=(',',':')).encode('ascii')
    if sha(canonical)!=provenance['canonical_sha256'] or provenance['authority_scope']!='HISTORICAL_PRODUCER_LAYOUT_REVIEWED':
        raise BindingError('raw decoded authority mismatch')
    values=[]
    for z in doc['values']:
        if type(z) is not list or len(z)!=2:
            raise BindingError('invalid complex pair')
        parts=[]
        for term in z:
            if type(term) is not list or len(term)!=2:
                raise BindingError('invalid dyadic')
            s,p=term
            if type(s) is not str or len(s)>32 or re.fullmatch(r'-?[0-9a-f]+',s) is None or type(p) is not int or abs(p)>2048:
                raise BindingError('noncanonical or oversized dyadic')
            n=int(s,16)
            if (n==0 and (s!='0' or p!=0)) or (n!=0 and n%2==0):
                raise BindingError('unnormalized dyadic')
            parts.append(Q(n << p) if p>=0 else Q(n,1<<-p))
        values.append(tuple(parts))
    return [values[i*shape[1]:(i+1)*shape[1]] for i in range(shape[0])], provenance

def _payload_c_order(blob,header):
    payload=blob[header.payload_offset:]
    if not header.fortran_order:
        return payload
    m,n=header.shape; size=header.item_bytes
    return b''.join(payload[(i+j*m)*size:(i+j*m+1)*size] for i in range(m) for j in range(n))

def load_inputs(root):
    root=Path(root)
    lock=verify_sources(root)
    primary=document(root,'NEXT_VALIDATION_PREREGISTRATION.json',tokens=True)
    secondary=document(root,'SECONDARY_REFINEMENT_PREREGISTRATION.json',tokens=True)
    if primary['selected_z_decimal']!='0.75' or primary['prediction_key']!='z0p75' or primary['radial_order']!=192 or secondary['radial_order']!=192:
        raise BindingError('geometry/order binding failed')
    if any(Q(str(z))==Q(3,4) for z in primary['training_nodes_z_a0']):
        raise BindingError('holdout appears in training list')
    for k,file in [('comparator_sha256','compare_future_holdout.py'),('decision_rule_sha256','FROZEN_HOLDOUT_DECISION_RULE.json'),('eight_node_manifest_sha256','EIGHT_NODE_INPUT_MANIFEST.json')]:
        if sha(read_bytes(root,'authority/'+file)) != primary[k]:
            raise BindingError('primary preregistration identity failed: '+file)
    if sha(read_bytes(root,'authority/NEXT_VALIDATION_PREREGISTRATION.json'))!=secondary['primary_parent_prereg_sha256']:
        raise BindingError('secondary-parent mismatch')
    for item in secondary['locked_files'].values():
        leaf=Path(item['path']).name
        prefix='inputs/' if leaf.endswith('.npz') else 'authority/'
        if (root/prefix/leaf).exists() and sha(read_bytes(root,prefix+leaf))!=item['sha256']:
            raise BindingError('secondary locked file mismatch: '+leaf)
    c,cp=_raw(root,'C',(47,2)); r,rp=_raw(root,'R',(2,47))
    models={}; members=[]; aggregated={}; checks={}
    for model in MODELS:
        name='Z075_COARSE_PREDICTION.npz' if model=='R31AD' else 'FROZEN_HOLDOUT_PREDICTIONS.npz'
        archive=read_bytes(root,'inputs/'+name)
        expected_archive=(secondary['locked_files']['R31AD_coarse_npz']['sha256'] if model=='R31AD' else primary['frozen_predictions_sha256'])
        if sha(archive)!=expected_archive:
            raise BindingError('prediction archive not pre-output bound')
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            names=z.namelist()
            if len(names)>1000 or len(set(names))!=len(names):
                raise BindingError('duplicate or over-budget ZIP members')
            selected=[]; values={}
            for field in ('O','dotO','Dcol','Drow','K'):
                member='z0p75_'+model+'_'+field+'.npy'
                info=z.getinfo(member)
                if info.file_size>65536:
                    raise BindingError('NPY member too large')
                raw=z.read(member)
                h=D.inspect_npy_header(raw,max_elements=94)
                expected=(2,47) if field=='Drow' else (47,2)
                if h.shape!=expected or h.descr!='<c16':
                    raise BindingError('prediction field shape/type mismatch')
                selected.append(_payload_c_order(raw,h))
                if field in FIELDS:
                    decoded=D.decode_npy_bytes(raw,max_elements=94)
                    values[FIELDS[field]]=E.from_decoded(decoded,limits=LIMITS)
                    members.append({'model':model,'field':FIELDS[field],'member':member,'archive':name,
                                    'npy_sha256':decoded.raw_npy_sha256,'canonical_sha256':decoded.canonical_sha256,
                                    'shape':list(h.shape),'dtype':h.descr,'fortran_order':h.fortran_order,
                                    'stored_independently':field=='K'})
            aggregate=sha(b''.join(selected));aggregated[model]=aggregate
            expected=(secondary['R31AD_coarse_arrays_sha256'] if model=='R31AD' else primary['selected_'+model+'_prediction_arrays_sha256'])
            if aggregate!=expected:
                raise BindingError('pre-output selected arrays hash mismatch: '+model)
            checks[model]=True;models[model]=values
    return {'raw_col':c,'raw_row':r,'models':models,'bindings':{
        'schema':'WU088_C1_ACTUAL_MODEL_GAP_INPUTS_V1','source_lock_sha256':LOCK_SHA,
        'source_head':lock['base_commit'],'source_tree':lock['base_tree'],
        'geometry_z_au':'3/4','cosmological_redshift':None,'source_radial_order':192,
        'raw_C_provenance':cp,'raw_R_provenance':rp,'OD_archive_sha256':OD_SHA,'JVP_archive_sha256':JVP_SHA,
        'raw_values_reused_not_redecoded':True,'prediction_members':members,
        'selected_array_hashes':aggregated,'selected_array_hashes_verified':checks,
        'raw_K_definition':'EXACT (C - adjoint(R))/2',
        'prediction_K_definition':'INDEPENDENT_STORED_K_NO_RECONSTRUCTION',
        'holdout_not_used_for_training':True}}

def evaluate(root):
    x=load_inputs(root)
    out=E.represented_gaps(x['models'],x['raw_col'],x['raw_row'],precision=128,limits=LIMITS)
    gaps={c:{k:v.to_json() for k,v in out[c].items()} for c in ('PRIMARY','SECONDARY')}
    p=document(root,'PRIMARY_COMPARISON_RAW.json',tokens=True)
    s=document(root,'SECONDARY_REFINEMENT_COMPARISON.json',tokens=True)
    for d in (p,s):
        if d['OD_sha256']!=OD_SHA or d['JVP_sha256']!=JVP_SHA or token_bits(d['comparison_tolerance_per_ta'])!=E.TOLERANCE_BITS:
            raise BindingError('historical scalar source/tolerance drift')
    if p['R31AK_errors']!=s['refined_R31AK_errors']:
        raise BindingError('PRIMARY/SECONDARY local scalars differ')
    bridge={}; legacy={}
    specs=[('PRIMARY',p['R31AK_errors'],p['R31Z_errors'],p['verdict'],'PARETO_SUPPORTED_AT_SELECTED_HOLDOUT'),
           ('SECONDARY',s['refined_R31AK_errors'],s['coarse_R31AD_errors'],s['secondary_verdict'],'REFINED_PARETO_SUPPORTED_AT_Z075')]
    for comparison,local,other,archived,expected in specs:
        lt=[local['E_'+k+'_per_ta'] for k in ('K','Dmax')]
        ot=[other['E_'+k+'_per_ta'] for k in ('K','Dmax')]
        trace=audit_tokens(lt,ot,comparison)
        trace['input_provenance_admitted']=True
        trace['archived_verdict']=archived
        trace['archived_verdict_matches']=archived==expected and trace['rne']['frozen_binary64_supported']
        bridge[comparison]=trace;legacy[comparison]={}
        for index,metric in enumerate(('K','Dmax')):
            bits=int(trace['rne']['other_minus_local_bits'][index],16)
            g=E.binary64_value(bits)
            legacy[comparison][metric]={'reconstructed_rne_gap':str(g),'reconstructed_rne_gap_bits':f'{bits:016x}',
                 'eta_upper':str(E.legacy_eta(g,out[comparison][metric],limits=LIMITS)),
                 'scope':'A posteriori bound for this archived scalar and exact represented interval; not a generic SVD error theorem'}
    threshold=min((v.lo-E.TOLERANCE)/2 for c in ('PRIMARY','SECONDARY') for v in out[c].values())
    result = {'schema':'WU088_C1_RESULT_V1','status':'C1_REPRESENTED_GAPS_VERIFIED__CONTINUOUS_TARGET_UNRESOLVED',
      'final_verdict':'UNRESOLVED_INPUTS','epsilon':None,
      'input_bindings':x['bindings'],
      'represented_errors':{name:{k:v.to_json() for k,v in met.items()} for name,met in out['model_errors'].items()},
      'represented_gaps':gaps,'machine_bridge':bridge,'legacy_comparison':legacy,
      'sufficient_future_common_epsilon':{'strict_upper':str(threshold),'unit':'1/t_a',
        'condition':'If separately proven max(epsilon_C,epsilon_R) is strictly below this bound, all four exact-real gap inequalities are strict.',
        'actual_epsilon_computed':False,'admission':False},
      'arithmetic':{'backend':'PINNED_EXACT_RATIONAL_GRAM_WITH_INTEGER_SQRT',
        'radical_absolute_grid_bits':128,'relative_128bit_accuracy_claim':False,
        'eta_added_to_direct_route':False,'source_error_terms_double_counted':False},
      'admission':{'represented_gap_arithmetic':True,'continuous_target_certificate':False,
        'physical_model_validated':False,'scientific_admission':False,'production_admission':False,
        'independent_scientific_review':False},
      'preserved':{'coverage':20,'total':289,'missing_unbounded':269,'B22':'OPEN_UNDETERMINED','C0_application_authority':'BLOCKED'},
      'execution':{'new_HH_integrations':0,'producer_calls':0,'model_evaluations':0,'historical_SVD_reruns':0},
      'next':'C2_PORTABLE_CERTIFICATE_JOIN_AND_RETURN_INGEST'}
    result['polynomial_certificate']=check_all_norms(x,result['represented_errors'])
    return result


def verify_norm_bracket(matrix, interval):
    """Independent rational characteristic-polynomial certificate, no sqrt/SVD.

    For Hermitian Gram G, x >= lambda_max iff x >= max(a,d) and
    det(x I-G)>=0. Below lambda_max follows from x<=max(a,d), or from
    det(x I-G)<=0. Here x is the square of a nonnegative norm endpoint.
    """
    if not isinstance(matrix,(list,tuple)) or not matrix or not matrix[0]:
        raise BindingError('nonempty exact matrix required')
    m,n=len(matrix),len(matrix[0])
    if min(m,n)!=2 or m*n>94 or any(len(row)!=n for row in matrix):
        raise BindingError('bounded rank-two matrix required')
    for row in matrix:
        for z in row:
            if not isinstance(z,tuple) or len(z)!=2 or any(not isinstance(v,Q) or max(v.numerator.bit_length(),v.denominator.bit_length())>8192 for v in z):
                raise BindingError('bounded exact complex components required')
    a=matrix if n==2 else [[(matrix[j][i][0],-matrix[j][i][1]) for j in range(2)] for i in range(n)]
    aa=sum((z[0][0]**2+z[0][1]**2 for z in a),Q(0))
    dd=sum((z[1][0]**2+z[1][1]**2 for z in a),Q(0))
    br=sum((z[0][0]*z[1][0]+z[0][1]*z[1][1] for z in a),Q(0))
    bi=sum((z[0][0]*z[1][1]-z[0][1]*z[1][0] for z in a),Q(0))
    lo,hi=Q(interval['lo']),Q(interval['hi'])
    if lo<0 or hi<lo:
        return False
    det=lambda x:(x-aa)*(x-dd)-br*br-bi*bi
    return hi*hi>=max(aa,dd) and det(hi*hi)>=0 and (lo*lo<=max(aa,dd) or det(lo*lo)<=0)

def check_all_norms(x, errors):
    c,r=x['raw_col'],x['raw_row']
    raw_k=[[( (c[i][j][0]-r[j][i][0])/2,(c[i][j][1]+r[j][i][1])/2 ) for j in range(2)] for i in range(47)]
    raw={'D_col':c,'D_row':r,'K':raw_k}
    records=[]
    for model in MODELS:
        for field in ('D_col','D_row','K'):
            a=x['models'][model][field];ref=raw[field]
            diff=[[tuple(z-w for z,w in zip(v,u)) for v,u in zip(ar,rr)] for ar,rr in zip(a,ref)]
            ok=verify_norm_bracket(diff,errors[model][field])
            records.append({'model':model,'field':field,'pass':ok})
    if not all(d['pass'] for d in records):
        raise BindingError('exact characteristic-polynomial verification failed')
    return {'method':'Independent exact rational characteristic-polynomial inequalities; no square-root evaluator',
            'checked_norms':len(records),'all_pass':True,'records':records,
            'independent_algorithm':True,'independent_scientific_reviewer':False}

def _write_new(path, doc):
    import os
    data=(json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    with open(path,'xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())

def main():
    import argparse, os, resource, signal, sys, time
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--require-continuous',action='store_true')
    args=ap.parse_args()
    try:
        args.output.mkdir(parents=True,exist_ok=False)
    except OSError as exc:
        print('OUTPUT_NOT_CREATE_ONLY: '+str(exc),file=sys.stderr);return 4
    root=Path(__file__).resolve().parent
    _write_new(args.output/'STARTED.json',{'node':'C1','scientific_dispatch':False,'automatic_retry':False})
    start=time.perf_counter()
    try:
        cap=1073741824
        oldsoft,oldhard=resource.getrlimit(resource.RLIMIT_AS)
        cap=min(cap,oldhard) if oldhard>=0 else cap
        cap=min(cap,oldsoft) if oldsoft>=0 else cap
        resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
        def timeout(signum,frame):
            raise TimeoutError('30 second C1 deadline')
        signal.signal(signal.SIGALRM,timeout);signal.alarm(30)
        result=evaluate(root)
        _write_new(args.output/'RESULT.json',result)
        _write_new(args.output/'ACTUAL_MODEL_GAP_INPUTS.json',result['input_bindings'])
        _write_new(args.output/'PREDICATE_BRIDGE.json',result['machine_bridge'])
        _write_new(args.output/'ACTUAL_REPRESENTED_GAPS.json',result['represented_gaps'])
        ret={'status':'UNRESOLVED_INPUTS' if args.require_continuous else result['status'],
             'continuous_target_certificate':False,'HH_integrations':0,'result_sha256':sha((args.output/'RESULT.json').read_bytes()),
             'elapsed_seconds':time.perf_counter()-start,'address_space_limit_bytes':cap,
             'max_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'source_lock_sha256':LOCK_SHA,'next':result['next']}
        _write_new(args.output/'RETURN.json',ret)
        print(ret['status'])
        return 3 if args.require_continuous else 0
    except (ValueError,OSError,KeyError,TypeError,TimeoutError,MemoryError,zipfile.BadZipFile) as exc:
        _write_new(args.output/'FAILURE.json',{'status':'BLOCKED','failure_type':type(exc).__name__,
                    'reason':str(exc),'HH_integrations':0,'automatic_retry':False})
        print(type(exc).__name__+': '+str(exc),file=sys.stderr);return 2
    finally:
        signal.alarm(0)

if __name__=='__main__':
    raise SystemExit(main())
