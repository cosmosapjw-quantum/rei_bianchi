"""Independent read-only W1 contract checks; never executes HH native code."""
from fractions import Fraction
from pathlib import Path
import copy, hashlib, importlib.util, json, sys

HERE = Path(__file__).resolve().parent
NEW = HERE.parent
LADDER = NEW.parent
WD = LADDER / 'wide_domain_20261001_v1'
EXPECTED = {
 'driver': ('range_native_driver/driver.py', 'e91238a21d5cffc3c513330ceb561f882d44a92f8654b1a0d6fa1117e59949dc'),
 'collector': ('tile_collection/collector.py', '0c8345ccae9a91ab38f2f15619ee5d58317dd22d7eab12268c2c47f91a7c5d94'),
 'build': ('runtime/build_range_cached/BUILD.json', '78ffe9e9489bca5997c103d9a0f9d7048217b6c8cfe4cf7d200ae7f4c8dc4b7d'),
 'binary': ('runtime/build_range_cached/primitive_worker', '7c1984dcca1b19631a91df1de52acea2eaa61db08c8d2ab1af1f9f1a3ebf3ba9'),
 'old_tile0': ('runtime/RANGE_TILE00_COMPLETION.json', '89cef714e9758932036854d218330c775920d6131114df8a236cf7d171bc5c5e'),
 'old_plan0': ('runtime/W1_TILED/plans/00.json', 'e9fb73d94614905c1b4e911c99e7b7af5f6a236753bb92ffad9b8d0a60cdbb19'),
}
LIMITS = {'degree_limit':64,'max_evaluations':200000,'max_integration_calls':1024,'memory_mib':1024,'precision_bits':128,'queued_panels':64,'radius_exp':-52,'relative_goal':128,'wall_seconds':120}
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def read(path): return json.loads(Path(path).read_bytes())
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def baseline():
    checked = {}
    for label,(rel,expected) in EXPECTED.items():
        actual=sha(WD/rel)
        assert actual==expected,(label,actual)
        checked[str((WD/rel).relative_to(LADDER))]=actual
    d=load(WD/EXPECTED['driver'][0],'review_fixed_range_driver')
    m=read(WD/EXPECTED['build'][0]);p=read(WD/EXPECTED['old_plan0'][0]);r=read(WD/EXPECTED['old_tile0'][0]);w=r['wrapper']
    assert m['source']==d.source_identity()
    assert m['source']['sha256']=='de1e32d8a68146a49d269614c2259ec06f10a5294ffa05b15d375239518bcae1'
    assert m['manifest_sha256']=='13965d2210e976f0d7a190fba58f8c3c1bf366521e8dd1bd5e9a28cdae9e9342'
    assert hashlib.sha256(canonical({k:v for k,v in m.items() if k!='manifest_sha256'})).hexdigest()==m['manifest_sha256']
    assert hashlib.sha256(canonical({k:v for k,v in r.items() if k!='result_sha256'})).hexdigest()==r['result_sha256']
    assert w['native_limits']==LIMITS
    assert w['build_manifest_sha256']==m['manifest_sha256'] and w['build_source']==m['source']
    assert w['binary_sha256']==m['binary_sha256']
    d.validate_result({k:v for k,v in r.items() if k not in ('wrapper','result_sha256')},plan=p,task=p['tasks'][0],manifest=m,limits=LIMITS)
    radii={}
    for part in ('real','imag'):
        v=r['rectangle'][part];lower=int(v['lower_mantissa'])*Fraction(2)**int(v['exponent2']);upper=int(v['upper_mantissa'])*Fraction(2)**int(v['exponent2'])
        radius=(upper-lower)/2
        assert 0<=radius<=Fraction(2)**-52
        radii[part]={'lower':str(lower),'upper':str(upper),'radius':str(radius)}
    geometry=[]
    axis=[-4,-1,2,5,8]
    for ti in range(4):
        for ui in range(4):
            window=dict(zip(('l_t','T_t','l_u','T_u'),map(lambda z:str(Fraction(2)**z),(axis[ti],axis[ti+1],axis[ui],axis[ui+1]))))
            local=read(WD/('runtime/W1_TILED/plans/%02d.json'%len(geometry)))
            assert local['window']==window
            assert local['archive_sha256']=='8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
            geometry.append({'tile_id':len(geometry),'window':window,'plan_sha256':local['plan_sha256']})
    assert 16*Fraction(2)**-52==Fraction(2)**-48
    return {'schema':'WU088_W1_BASELINE_INDEPENDENT_REVIEW_V1','status':'PASS_READONLY_BASELINE_AND_GEOMETRY','source_files':checked,'old_tile0_exact_intervals':radii,'limits':LIMITS,'independent_geometry':geometry,'sum_of_tile_caps':'1/281474976710656','new_native_executions':0,'new_runner_or_host_review':'PENDING','full_W1_complete':False,'endpoint_included':False,'scientific_admission':False,'production_admission':False,'review_source_sha256':sha(__file__)}

if __name__=='__main__':
    out=HERE/'BASELINE_REVIEW.json'
    with out.open('x') as f: json.dump(baseline(),f,indent=2,sort_keys=True);f.write('\n')
    print('PASS: immutable range baseline and independent16-tile geometry; noHH execution')
