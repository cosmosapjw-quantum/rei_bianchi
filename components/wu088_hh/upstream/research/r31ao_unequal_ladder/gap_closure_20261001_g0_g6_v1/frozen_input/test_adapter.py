from fractions import Fraction
from pathlib import Path
import hashlib,io,json,struct,unittest,zipfile
from .adapter import decode_npz,generate_cpp,AdapterError,SPEC,FROZEN107_ARCHIVE_SHA256


def npy(name,*,shape=None,descr='<f8',order=None,nan=False):
    wanted=SPEC[name]
    shape=wanted['shape'] if shape is None else shape
    order=wanted['fortran_order'] if order is None else order
    count=1
    for n in shape:count*=n
    header=repr({'descr':descr,'fortran_order':order,'shape':tuple(shape)}).encode()
    header+=b' '*((-(10+len(header)+1))%64)+b'\n'
    values=list(range(count))
    if order and len(shape)==2:
        values=[i*shape[1]+j for j in range(shape[1]) for i in range(shape[0])]
    payload=b''.join(struct.pack('<d',float(x+1)) for x in values)
    if nan:payload=bytes.fromhex('000000000000f87f')+payload[8:]
    return b'\x93NUMPY\x01\x00'+len(header).to_bytes(2,'little')+header+payload


def fixture(changes=None,extra=None,missing=None,compression=zipfile.ZIP_DEFLATED):
    f=io.BytesIO()
    with zipfile.ZipFile(f,'w',compression=compression) as z:
        for name in SPEC:
            if name!=missing:z.writestr(name,(changes or {}).get(name,npy(name)))
        if extra:z.writestr(*extra)
    return f.getvalue()


def run(data,**kwargs):
    return decode_npz(data,expected_archive_sha256=hashlib.sha256(data).hexdigest(),scope='SYNTHETIC_ONLY',**kwargs)


class AdapterTests(unittest.TestCase):
    def test_exact_semantic_fortran_and_native_bridge(self):
        record=run(fixture())
        self.assertEqual(record['fields']['s_C']['values'][12],'13')
        self.assertEqual(record['fields']['s_C']['values'][1],'2')
        self.assertEqual(record['fields']['pref']['values'],['1'])
        text=generate_cpp(record)
        self.assertIn('out.s_C[12].set("13");',text)
        self.assertIn('out.donor_C[728].set("729");',text)
        self.assertIn('out.z.set("3/4");',text)
        self.assertIn('load_synthetic_rational_record',text)
        self.assertEqual(text,generate_cpp(record))

    def test_expected_hash_required_and_mismatch(self):
        with self.assertRaises(TypeError): decode_npz(fixture(),scope='SYNTHETIC_ONLY')
        with self.assertRaises(AdapterError):decode_npz(fixture(),expected_archive_sha256='0'*64,scope='SYNTHETIC_ONLY')

    def test_fixture_never_admitted_as_pinned_original(self):
        data=fixture()
        with self.assertRaises(AdapterError):decode_npz(data,expected_archive_sha256=hashlib.sha256(data).hexdigest(),scope='FROZEN107_PINNED')

    def test_missing_and_unknown_member(self):
        for data in (fixture(missing='v.npy'),fixture(extra=('extra.npy',b'bad'))):
            with self.assertRaises(AdapterError):run(data)

    def test_duplicate_and_path(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            duplicate=fixture(extra=('pref.npy',npy('pref.npy')))
        for data in (duplicate,fixture(extra=('../escape.npy',b'bad'))):
            with self.assertRaises(AdapterError):run(data)

    def test_null_truncated_zip_path(self):
        data=fixture(missing='pref.npy',extra=('pref.npyJUNK',npy('pref.npy')))
        data=data.replace(b'pref.npyJUNK',b'pref.npy\0UNK')
        with self.assertRaisesRegex(AdapterError,'original ZIP member path'):run(data)

    def test_shape_and_order(self):
        for data in (fixture({'s_C.npy':npy('s_C.npy',shape=(144,))}),fixture({'s_C.npy':npy('s_C.npy',order=False)})):
            with self.assertRaises(AdapterError):run(data)

    def test_dtype_and_nonfinite(self):
        for data in (fixture({'v.npy':npy('v.npy',descr='<c16')}),fixture({'pref.npy':npy('pref.npy',nan=True)})):
            with self.assertRaises(AdapterError):run(data)

    def test_archive_and_member_size_caps(self):
        with self.assertRaises(AdapterError):run(b'x'*(1024*1024+1))
        with self.assertRaises(AdapterError):run(fixture({'pref.npy':b'x'*70000}))

    def test_unsupported_compression(self):
        with self.assertRaises(AdapterError):run(fixture(compression=zipfile.ZIP_BZIP2))

    def test_compression_bomb_ratio(self):
        with self.assertRaisesRegex(AdapterError,'compression ratio'):
            run(fixture({'pref.npy':b'\0'*64000}))

    def test_symlink_entry_rejected(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            for name in SPEC:
                info=zipfile.ZipInfo(name)
                if name=='pref.npy':info.external_attr=(0o120777<<16)
                z.writestr(info,npy(name))
        with self.assertRaisesRegex(AdapterError,'nonregular'):run(stream.getvalue())

    def test_generated_code_rejects_tampered_record(self):
        r=run(fixture());r['fields']['pref']['values'][0]='1\");system(\"evil'
        with self.assertRaises(AdapterError):generate_cpp(r)
        body={k:v for k,v in r.items() if k!='canonical_record_sha256'}
        r['canonical_record_sha256']=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()
        with self.assertRaises(AdapterError):generate_cpp(r)

    def test_rational_token_and_signed_zero_provenance(self):
        pref=npy('pref.npy')
        r=run(fixture({'pref.npy':pref[:-8]+bytes.fromhex('000000000000c03f')}))
        self.assertEqual(r['fields']['pref']['values'],['1/8'])
        self.assertIn('out.pref.set("1/8");',generate_cpp(r))
        r=run(fixture({'pref.npy':pref[:-8]+bytes.fromhex('0000000000000080')}))
        self.assertEqual(r['fields']['pref']['values'],['0'])
        self.assertEqual(r['fields']['pref']['negative_zero_c_order'],[True])

    def test_no_new_donor_count_authority(self):
        record=run(fixture())
        self.assertEqual(record['donor_nonzero_count'],729)
        self.assertFalse(record['scientific_authority'])
        self.assertFalse(record['execution_authorized'])

    def test_pinned_codegen_rejects_self_asserted_scope(self):
        data=fixture();r=run(data)
        r['scope']='FROZEN107_PINNED';r['archive_sha256']=FROZEN107_ARCHIVE_SHA256
        r['input_byte_pin_verified']=True
        body={k:v for k,v in r.items() if k!='canonical_record_sha256'}
        r['canonical_record_sha256']=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()
        with self.assertRaisesRegex(AdapterError,'original archive bytes'):generate_cpp(r)
        with self.assertRaises(AdapterError):generate_cpp(r,source_archive_bytes=data)


if __name__=='__main__':unittest.main(verbosity=2)
