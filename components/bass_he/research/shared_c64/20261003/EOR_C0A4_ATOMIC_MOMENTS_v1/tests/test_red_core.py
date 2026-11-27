from fractions import Fraction as F
import json
import pytest
from bass_he_liu import ContractError,SourceUnavailable,DomainError
from bass_he_atomic_moments import MODEL_ID,coefficients,validate_provider,MomentProvider,basis_weight_interval

@pytest.mark.parametrize('cid,expected',[
 ('NR_CX:1s:1s',F(-3,2)),('NR_CX:1s:2p',F(0)),('NR_CX:1s:3d',F(5,18)),
 ('NR_CX:2s:3d',F(-7,72)),('NR_CX:2s:4f',F(0)),
 ('EXC:1s:2p',F(3,8)),('EXC:2s:3s',F(5,72)),('EXC:2s:4d',F(3,32))])
def test_coefficient_identity(cid,expected):
 out=coefficients(cid,model_id=MODEL_ID)
 assert out is not None and out['internal']==expected
 assert out['chemical']+out['excitation_change']==expected
 assert out['excitation_final']-out['excitation_initial']==out['excitation_change']

@pytest.mark.parametrize('cid',['NR_CX:1s:total','ION:1s:2p','R_CX:1s:2p','EXC:1s:2d','NR_CX:3s:1s'])
def test_undefined_channels_rejected(cid):
 with pytest.raises(ContractError):coefficients(cid,model_id=MODEL_ID)

def test_energy_convention_explicit():
 with pytest.raises(ContractError):coefficients('EXC:1s:2p',model_id=None)

def test_provider_snapshot_actual_binding(root):
 x=validate_provider(root/'raw',root/'provenance/provider_snapshot/ScienceDB_ldjson_0.json')
 assert x is not None and len(x['files'])==4 and all(f['md5_matches'] for f in x['files'])
 assert x['version']=='1.0.0' and x['license_uri'].endswith('/by-nc/4.0/')
 assert x['isotope'] is None and x['per_u_divisor'] is None

def test_modified_snapshot_rejected(root,tmp_path):
 p=root/'provenance/provider_snapshot/ScienceDB_ldjson_0.json'
 q=tmp_path/'bad.json';q.write_text(p.read_text().replace('1.0.0','9.0.0'))
 with pytest.raises(ContractError):validate_provider(root/'raw',q)

def test_native_energy_axis_and_exact_weight(data):
 p=MomentProvider(data,model_id=MODEL_ID)
 x=p.sample('NR_CX:1s:1s','100')
 assert x is not None and x['sigma']['value_token']=='1.15E-17'
 assert F(x['moments']['internal']['exact_fraction'])==-F(3,2)*F('1.15E-17')
 assert x['heat'] is None and not x['physical_certificate']

def test_zero_moment_is_not_missing(data):
 x=MomentProvider(data,model_id=MODEL_ID).sample('NR_CX:1s:2s','100')
 assert x is not None and x['moments']['internal']['exact_fraction']=='0'
 assert x['moments']['internal']['zero_kind']=='EXACT_IN_STATED_ENERGY_MODEL'
 assert x['heat'] is None

def test_no_total_energy_from_total_sigma(data):
 with pytest.raises(SourceUnavailable):MomentProvider(data,model_id=MODEL_ID).sample('NR_CX:1s:total','100')

def test_no_historical_1s_false_node(data):
 with pytest.raises(ContractError):MomentProvider(data,model_id=MODEL_ID).sample('NR_CX:1s:1s','56.25')

def test_contextual_unit_acceptance(data):
 with pytest.raises(ContractError):MomentProvider(data,model_id=MODEL_ID).sample('EXC:1s:2p','100',unit='m2')
 x=MomentProvider(data,model_id=MODEL_ID).sample('EXC:1s:2p','100',unit='m2',accept_contextual_unit=True)
 assert F(x['moments']['internal']['exact_fraction'])==F(3,8)*F('1.77E-20')

@pytest.mark.parametrize('ids',[['NR_CX:1s:n2','NR_CX:1s:2s'],['NR_CX:1s:1s','NR_CX:2s:3s'],['EXC:1s:2p','NR_CX:1s:1s']])
def test_aggregate_refuses_ambiguous_or_overlapping(data,ids):
 with pytest.raises(ContractError):MomentProvider(data,model_id=MODEL_ID).aggregate(ids,'100')

def test_derived_shell_zero_and_count(data):
 x=MomentProvider(data,model_id=MODEL_ID).aggregate(['NR_CX:2s:n4'],'100')
 assert x is not None and len(x['members'])==4 and x['moments']['internal']['exact_fraction']=='0'
 assert not x['inclusive_all_bound']

def test_weighted_finite_functional_reuses_parent(data):
 from bass_he_liu_interp import Interpolator
 x=MomentProvider(data,model_id=MODEL_ID).functional(['EXC:1s:2p'],'25','196',theta_native=30.)
 f=Interpolator(data,method='linear_E').maxwell_functional('EXC:1s:2p','25','196',theta_native=30.)
 assert x is not None and x['moments']['internal']['value']==float(F(3,8))*f['value']
 assert x['heat'] is None and x['full_functional'] is None and x['tail_bound'] is None

def test_basis_averaging_requires_correlation_not_product_of_means():
 # sigma=(1,3,5), q=(2,-1,4): averaged product 19/3 vs product means 5.
 x=basis_weight_interval(F(3),[F(2),F(-1),F(4)])
 assert x is not None and x['lower']==F(-3) and x['upper']==F(12)
 assert x['lower']<=F(19,3)<=x['upper']
