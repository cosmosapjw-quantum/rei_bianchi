"""New integration regression at the real reducer.run seam; no source IVP."""
import csv, hashlib, importlib.util, io, json, math, os, pathlib, sys, tempfile, unittest
from contextlib import redirect_stdout
from fractions import Fraction as Q
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'supplier'))
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
TARGET=pathlib.Path(os.environ.get('REDUCER_PATH',str(ROOT/'supplier/compare_histories.py')))
M=load(TARGET,'tested_reducer')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def fixture(root,name,positions,source='SYNTHETIC_SAME_MODEL_NOT_A_COSMOLOGY',bump=False,extra_config=''):
    p=root/name;p.mkdir();spec={'id':name,'clock_origin':M.CLOCK}
    h=1-.2454;he=.2454/4;f=he/h
    ah=['run_id','time_s','species_id','nproper','Ybaryon','A','normalization_registry']
    hh=['case_id','a','time_s','nH_proper_cm3','ne_proper_cm3',*dict.fromkeys(M.FIELDS.values())]
    hh=list(dict.fromkeys(hh))
    with (p/'history.csv').open('w',newline='') as hf,(p/'abundances.csv').open('w',newline='') as af:
        hw=csv.DictWriter(hf,fieldnames=hh);hw.writeheader();aw=csv.DictWriter(af,fieldnames=ah);aw.writeheader()
        for pos in positions:
            a=M.A0 if pos==0 else M.A1 if pos==1 else math.exp(M.L0+pos*(M.L1-M.L0))
            u=(math.log(a)-M.L0)/(M.L1-M.L0)
            x=.1+.8*u+(.001 if bump and pos==.5003 else 0.)
            t=pos*100;nh=a**-3;nhe=f*nh;nb=nh+4*nhe
            row={'case_id':name,'a':a,'time_s':t,'nH_proper_cm3':nh,'ne_proper_cm3':nh*x,
                 'x_HI':1-x,'x_HII':x,'x_HeI':1.,'x_HeII':0.,'x_HeIII':0.,'temperature_K':10+u,
                 'J0_photon_u_eV_per_H':0.,'J2_photon_u_eV_per_H':0.}
            hw.writerow(row)
            for k,n,A in [('H_I',nh*(1-x),1),('H_II',nh*x,1),('He_I',nhe,4),('He_II',0.,4),('He_III',0.,4),('electron',nh*x,0)]:
                aw.writerow({'run_id':name,'time_s':t,'species_id':k,'nproper':n,'Ybaryon':n/nb,'A':A,
                             'normalization_registry':'BASELINE_H_HE_CHARGE_AND_BARYON_V1'})
    for role,txt in [('config','end_zbar=4\nq_ref=0\nlocal_target=1e-5\n'+extra_config),('source_identity',source),
                     ('terminal',f'status=COMPLETE_REPRESENTED_INTERVAL\na=0.2\naccepted={len(positions)-1}\n')]:
        (p/(role+'.txt')).write_text(txt)
    for role in ('history','abundances','config','source_identity','terminal'):
        path=p/(role+('.csv' if role in ('history','abundances') else '.txt'));spec[role]={'path':str(path),'sha256':sha(path)}
    return spec

def run_pair(root,unequal=False,mode='EXACT_UNION',relation=False,kind='PAIRED'):
    ref=fixture(root,'R',[0,.5,1]);cand=fixture(root,'C',[0,.50025,.5003,.50035,1],
          source='SYNTHETIC_OTHER_IMPLEMENTATION' if unequal else 'SYNTHETIC_SAME_MODEL_NOT_A_COSMOLOGY',bump=True)
    if kind=='REFINEMENT':
        p=pathlib.Path(cand['config']['path']);p.write_text(p.read_text().replace('local_target=1e-5','local_target=2.5e-6'));cand['config']['sha256']=sha(p)
    manifest={'reference':ref,'candidate':cand,'comparison_kind':kind,'reconstruction_norm':mode,
              'fixture_scope':'MANUFACTURED_COMPLETE_DATA_NOT_ACTUAL_TRAJECTORY'}
    if relation:
        manifest['source_relation']={'reference_sha256':ref['source_identity']['sha256'],'candidate_sha256':cand['source_identity']['sha256'],
         'relation':'REVIEWED_SAME_PHYSICAL_MODEL','status':'ACCEPTED_SCOPED','evidence':'MANUFACTURED_TEST_RELATION_ONLY'}
    path=root/'manifest.json';path.write_text(json.dumps(manifest,indent=2))
    with redirect_stdout(io.StringIO()):result=M.run(path,root/'out')
    return result,manifest

class FocusedIntegration(unittest.TestCase):
    def test_electron_floor_commutes_with_normalization(self):
        case={'factors':(.7546,.06135)}
        self.assertAlmostEqual(M.floor('xe',case)*case['factors'][0],M.floor('Y_electron',case),places=22)
    def test_distinct_unbound_sources_stop_before_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);res,_=run_pair(root,unequal=True)
            self.assertEqual(res['status'],'HOLD_SOURCE_RELATION_UNBOUND')
            self.assertFalse((root/'out/sampled_comparisons.csv').exists())
    def test_union_norm_detects_feature_between_grid_points(self):
        with tempfile.TemporaryDirectory() as d:
            res,_=run_pair(pathlib.Path(d))
            self.assertEqual(res['status'],'DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED')
            row=next(x for x in res['metrics'] if x['observable']=='x_HII')
            self.assertIn('reconstruction_sup_exact',row)
            self.assertGreater(Q(row['reconstruction_sup_exact']),Q('0.000999'))
            self.assertLess(row['sampled_sup_absolute_difference'],1e-12)
            self.assertEqual(row['result_class'],'RESOLUTION_LIMITED')

if __name__=='__main__':unittest.main(verbosity=2)
