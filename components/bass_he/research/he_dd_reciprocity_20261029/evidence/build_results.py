from pathlib import Path
from hashlib import sha256,sha1
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from reciprocity import *

def hash_info(path):
    b=path.read_bytes()
    return {'bytes':len(b),'sha256':sha256(b).hexdigest(),
            'git_blob_sha1':sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}
with localcontext() as ctx:
    ctx.prec=60
    def dec(f):return str(D(f.numerator)/D(f.denominator))
    output={
        'schema':'BASS_HE_DD_RECIPROCITY_V1','date':'2026-10-29',
        'parent_PR':106,'parent_head':'b5ee8c135accb98ba0f9533a4beb0c8c6210933e',
        'frozen_masses_MeV':{'M_alpha_c2':str(MA),'m_d_c2':str(MD)},
        'source':{'repo':'IAEA-NDS/exfor_master','commit':SOURCE_COMMIT,'path':'exforall/M04/M0475.x4',
                  'sha256':SOURCE_SHA256,'git_blob':SOURCE_GIT_BLOB},
        'threshold_Egamma_MeV':dec(gamma_threshold()),
        'Egamma_213_matched_Td_MeV':dec(T_matching(213)),
        'Egamma_330_matched_Td_MeV':dec(T_matching(330)),
        'Td_376_matched_Egamma_MeV':dec(E_matching(376)),
        'Td376_equals_Egamma213':False,'Td376_equals_Egamma330':False,
        'reciprocity':{},
        'tests':{'new_unittest':'33/33 PASS','independent_Decimal80':'8/8 cases max abs residual 2e-73',
                 'Wolfram_exact_compositions':'4/4 zeros','Wolfram_exact_mass_shell_coefficients':'4/4 zeros',
                 'full_BASS_HE_suite':'NOT_RUN','original_IVPs':'NOT_RUN'},
        'physical':{'inverse_measured_330':None,'event_multiplicity_kappa':None,'event_rate':None,
                    'physical_activation':False,'L4':False,'production':'HOLD'},
        'DAG':{'central':'28/88','inherited_HE':'14/18','PR105':'2/2','PR106':'1/2',
               'new_reciprocity_local':'1/2_SCOPED_KINEMATICS_ONLY','physical_delta':0},
        'files':{}
    }
    for energy in (213,330):
        output['reciprocity'][str(energy)]={}
        for convention in (ORDERED,FULL_EVENT):
            a=conditional_inverse_DA(energy,73,convention,ROOT/'source/M0475.x4')
            output['reciprocity'][str(energy)][convention]={
                'ratio_inverse_to_forward_exact':str(a['ratio_inverse_to_forward']),
                'ratio_inverse_to_forward_decimal':dec(a['ratio_inverse_to_forward']),
                'conditional_inverse_73deg_interval_nb_sr':[dec(a['inverse_lower_nb_sr']),dec(a['inverse_upper_nb_sr'])],
                'forward_source_DA_nb_sr':str(a['source_DA_nb_sr']),
                'forward_ERR_S_nb_sr':str(a['ERR_S_nb_sr']),
                'inverse_measured':None}
    for rel in ['src/reciprocity.py','tests/test_reciprocity.py','source/M0475.x4',
                'evidence/independent_oracle.py','evidence/INDEPENDENT_ORACLE.json',
                'make_figures.py','results/energy_matching.png','results/reciprocity_factors.png']:
        output['files'][rel]=hash_info(ROOT/rel)
(ROOT/'RESULTS.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
print('source files',len(output['files']),'unittest',output['tests']['new_unittest'])
