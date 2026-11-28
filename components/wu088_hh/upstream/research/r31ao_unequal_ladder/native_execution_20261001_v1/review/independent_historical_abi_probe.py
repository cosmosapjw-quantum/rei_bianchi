"""Read historical bytes/source links; no NumPy casts or numerical decoding."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
WORKSPACE=REPO.parents[1]
BUNDLE=WORKSPACE/'native_execution_intake'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_npy(raw):
    assert raw[:8]==b'\x93NUMPY\x01\x00'
    h=int.from_bytes(raw[8:10],'little')
    return ast.literal_eval(raw[10:10+h].decode('ascii')),raw[10+h:]


def main():
    meta=BUNDLE/'historical_metadata'
    src=BUNDLE/'pinned_sources'
    pre=json.loads((meta/'PRE_OUTPUT_LOCK.json').read_text())
    post=json.loads((meta/'POST_OUTPUT_LOCK_VERIFICATION.json').read_text())
    environment=json.loads((meta/'ENVIRONMENT.json').read_text())
    assert pre['producer_source_sha256']==post['producer_source_sha256']
    assert post['unchanged_after_output'] is True
    assert environment['precision']=={'longdouble_itemsize':16,'longdouble_significand_bits':64,
                                     'clongdouble_itemsize':32}
    assert environment['numpy']=='2.3.5' and 'x86_64' in environment['platform']
    mapping={
        src/'jvp_native.py':'completion/mixed_derivative/native.py',
        src/'jvp_run.py':'completion/mixed_derivative/run.py',
        src/'jvp_cpp.cpp':'completion/mixed_derivative/jvp.cpp',
        src/'od_native.py':'completion/mixed_h/native.py',
        src/'od_run_helpers.py':'completion/mixed_h/run.py',
        REPO/'research/r31an_reference_certification/ncp_preflight_20260930/source_snapshot/completion/mixed_h/od_run.py':
            'completion/mixed_h/od_run.py'}
    sources=[]
    for path,key in mapping.items():
        value=sha(path)
        assert value==pre['producer_source_sha256'][key]
        sources.append({'historical_path':key,'actual_sha256':value,'pre_post_pins_match':True})
    jvp=json.loads((meta/'JVP_RAW_IDENTITY.json').read_text())
    od=json.loads((meta/'OD_RAW_IDENTITY.json').read_text())
    assert jvp['native']==pre['producer_binary_identity']['JVP_NATIVE_PREP']['identity']
    assert od['source_identity']==pre['producer_binary_identity']['OD_NATIVE_PREP']['identity']
    assert jvp['driver']==pre['producer_source_sha256']['completion/mixed_derivative/run.py']
    assert od['driver_sha256']==pre['producer_source_sha256']['completion/mixed_h/od_run.py']
    assert jvp['n']==od['n']==192 and jvp['z']=='0.75'
    bindings=json.loads((BUNDLE/'B192_MEMBER_BINDINGS.json').read_text())
    observations=[]
    for record in bindings['records']:
        path=BUNDLE/'b192_raw'/record['local_basename']
        assert sha(path)==record['sha256'] and path.stat().st_size==record['bytes']
        with zipfile.ZipFile(path) as archive:
            assert set(archive.namelist())=={x['member'] for x in record['npy_members']}
            for member in record['npy_members']:
                raw=archive.read(member['member'])
                header,payload=parse_npy(raw)
                assert hashlib.sha256(raw).hexdigest()==member['sha256']
                assert hashlib.sha256(payload).hexdigest()==member['payload_sha256']
                expected=member['header']
                assert header['descr']==expected['descr'] and list(header['shape'])==expected['shape']
                assert header['fortran_order']==expected['fortran_order']
        observations.append({'archive':record['local_basename'],'archive_sha256':record['sha256'],
                             'npy_members_bound':len(record['npy_members'])})
    with zipfile.ZipFile(BUNDLE/'b192_raw/independent_JVP_ASSEMBLED.npz') as archive:
        header,payload=parse_npy(archive.read('z.npy'))
        assert header=={'descr':'<f16','fortran_order':False,'shape':()}
        x87=((16382<<64)+(3<<62)).to_bytes(10,'little')
        binary128=((16382<<112)+(1<<111)).to_bytes(16,'little')
        assert payload[:10]==x87 and payload!=binary128
    with zipfile.ZipFile(BUNDLE/'b192_raw/OD_ASSEMBLED_OD.npz') as archive:
        oh,op=parse_npy(archive.read('O.npy'))
        rh,rp=parse_npy(archive.read('O_row.npy'))
        assert oh=={'descr':'<c32','fortran_order':False,'shape':(47,2)}
        assert rh=={'descr':'<c32','fortran_order':True,'shape':(2,47)}
        # Transposition and F-order cancel: matching semantic values retain
        # identical physical element positions. Conjugation flips only imag sign.
        for i in range(94):
            original=op[i*32:i*32+32]; conjugate=rp[i*32:i*32+32]
            assert original[:10]==conjugate[:10]
            assert original[16:25]==conjugate[16:25]
            assert original[25]^conjugate[25]==0x80
    sources += [{'historical_numpy_source':p.name,'actual_sha256':sha(p)} for p in sorted(src.glob('numpy*'))]
    result={
        'schema':'WU088_INDEPENDENT_B192_SOURCE_AND_BYTE_ABI_REVIEW_V1',
        'status':'PASS_BOUNDED_HISTORICAL_LAYOUT_INFERENCE',
        'bounded_historical_layout_admitted':True,
        'format_admission_scope':'Only exact two NPZ identities and their enumerated NPY members',
        'evidence_files_sha256':{
            'B192_MEMBER_BINDINGS.json':sha(BUNDLE/'B192_MEMBER_BINDINGS.json'),
            **{'historical_metadata/'+name:sha(meta/name) for name in [
                'PRE_OUTPUT_LOCK.json','POST_OUTPUT_LOCK_VERIFICATION.json','ENVIRONMENT.json',
                'JVP_RAW_IDENTITY.json','OD_RAW_IDENTITY.json','JVP.argv.json','OD.argv.json']},
            'ABI_LAYOUT_EVIDENCE_CHAIN.json':sha(HERE.parent/'intake/ABI_LAYOUT_EVIDENCE_CHAIN.json')},
        'recorded_historical_numpy':'2.3.5','recorded_historical_component_bytes':16,
        'recorded_historical_significand_bits':64,'source_links':sources,
        'npz_member_binding_observations':observations,
        'jvp_native_identity_matches_prepared_binary':True,
        'od_native_identity_matches_prepared_binary':True,
        'producer_sources_unchanged_between_pre_post_locks':True,
        'z_literal_x87_value_offset0_little_match':True,
        'z_literal_binary128_match':False,
        'od_complex_conjugacy_exact_byte_pairs':94,
        'admitted_layout':{'format':'x87_80','component_bytes':16,'value_offset':0,
                           'byte_order':'little','complex_component_order':'real_imag',
                           'padding_policy':'Preserve raw bytes; ignore six padding bytes numerically'},
        'historical_extension_binary_hash_recovered':False,
        'claims_under_recorded_producer_and_version_provenance':True,
        'arbitrary_same_version_installations_admitted':False,
        'current_host_sentinel_used':False,'host_float_casts':0,
        'historical_numeric_values_decoded_by_this_probe':False,
        'mathematical_error_certificate':False,'scientific_admission':False,
        'production_admission':False}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
