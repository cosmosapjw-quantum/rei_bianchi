import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('resume', ROOT/'code/t4_resume.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
b = r.b
OBSERVED = {}


def fixture(d=96, complex_=False):
    rng = np.random.default_rng(418)
    A = rng.normal(size=(d-1,d-1))
    if complex_: A = A+1j*rng.normal(size=A.shape)
    Q, _ = np.linalg.qr(A)
    K = np.zeros((d,d), dtype=Q.dtype)
    K[1:,1:] = (Q*np.linspace(.1, 400., d-1))@Q.conj().T
    g = np.zeros(d, dtype=Q.dtype); g[0] = 1
    u = rng.normal(size=d)
    if complex_: u = u+1j*rng.normal(size=d)
    u[0] = 0; u /= np.linalg.norm(u)
    return K, g, u


def budget(maximum=256, seconds=20):
    return b.ActionBudget(time.monotonic()+seconds, maximum=maximum, headroom_gib=0)


def legacy(out, K, g, u, length):
    out.mkdir(); bu = budget()
    result, spectral = b.krylov_chain(lambda v: bu.apply(lambda x: K@x,v), g,u,.7,
         out=out, budget=bu, identities={**r.identities(),'runner':r.LEGACY_SHA},max_length=length)
    return result, spectral, bu


def mutate(source, target, fn):
    with np.load(source,allow_pickle=False) as f: arrays = {k:f[k].copy() for k in f.files}
    md = json.loads(str(arrays['metadata_json'].item()))
    fn(arrays,md); arrays['metadata_json'] = np.asarray(json.dumps(md))
    np.savez(target, **arrays)


class ResumeTests(unittest.TestCase):
    def test_serialized_64_to_cap128_and_complex_32_to64(self):
        summary = []
        for complex_, stop, cap in [(False,64,128),(True,32,64)]:
            K,g,u = fixture(complex_=complex_)
            with tempfile.TemporaryDirectory() as td:
                td=Path(td)
                old,_,before = legacy(td/'old',K,g,u,stop)
                state = r.load_checkpoint(td/'old/checkpoint.npz',g,u,.7)
                self.assertEqual(before.actions,stop)
                self.assertEqual(state['validation']['recompression_H_actions'],0)
                self.assertTrue(all(x is None for x in state['corrections']))
                fresh=budget(); samples=r.cache_seam_checks(lambda v:fresh.apply(lambda x:K@x,v),state)
                self.assertTrue(samples['passed']); self.assertEqual(fresh.actions,3)
                bu=budget(); (td/'new').mkdir()
                result,sp,V,KV=r.resume_chain(lambda v:bu.apply(lambda x:K@x,v),state,g,u,.7,cap,bu,td/'new')
                full,fullsp,fullbudget=legacy(td/'full',K,g,u,cap)
                with np.load(td/'full/checkpoint.npz',allow_pickle=False) as f: Vf=f['V']
                self.assertEqual(result['last_length'],full['last_length'])
                self.assertEqual(bu.actions,result['last_length']-stop)
                self.assertEqual(fullbudget.actions,result['last_length'])
                self.assertLess(np.linalg.norm(V@V.conj().T-Vf@Vf.conj().T),1e-8)
                self.assertTrue(np.allclose(result['direct_moments'],full['direct_moments'],rtol=1e-8,atol=1e-8))
                self.assertTrue(np.allclose(sp['spectra'],fullsp['spectra'],rtol=1e-8,atol=1e-8))
                for z in (.3+.05j,3+.1j,230+.2j):
                    def compressed(s): return np.sum(s['weights']/(z-s['nodes']))/.7
                    self.assertLess(abs(compressed(sp)-compressed(fullsp)),1e-8*max(1,abs(compressed(fullsp))))
                correction=json.loads(str(np.load(td/'new/checkpoint.npz',allow_pickle=False)['metadata_json'].item()))['reorthogonalization_correction_norms_Eh']
                self.assertEqual(correction[:stop],[None]*stop)
                self.assertTrue(all(isinstance(x,float) for x in correction[stop:]))
                reloaded=r.load_checkpoint(td/'new/checkpoint.npz',g,u,.7)
                self.assertEqual(reloaded['validation']['semantic_mapping'],'same resume implementation')
                summary.append({'complex':complex_,'restored':stop,'requested_cap':cap,'achieved':result['last_length'],
                    'before_actions':before.actions,'recompression_actions':0,'seam_actions':fresh.actions,
                    'extension_actions':bu.actions,'full_actions':fullbudget.actions,'termination':result['termination'],
                    'max_spectrum_difference':float(np.max(abs(sp['spectra']-fullsp['spectra'])))})
        OBSERVED['continuations']=summary

    def test_rejections_mapping_and_corrections(self):
        K,g,u=fixture(d=40)
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); legacy(td/'old',K,g,u,16); cp=td/'old/checkpoint.npz'
            state=r.load_checkpoint(cp,g,u,.7,milestone=td/'old/milestone_016.json')
            self.assertEqual(state['correction_origin'],'matching_milestone')
            self.assertNotEqual(state['validation']['legacy_runner_sha256'],state['validation']['resume_runner_sha256'])
            mutations = [
                ('shape',lambda a,m:a.update(V=a['V'][:,:-1])),
                ('nonfinite',lambda a,m:a['KV'].__setitem__((1,1),np.nan)),
                ('length',lambda a,m:m.update(length=16.0)),
                ('beta',lambda a,m:m.update(next_beta=-1)),
                ('hash',lambda a,m:m['identities'].update(data='wrong')),
                ('runner',lambda a,m:m['identities'].update(runner='unknown')),
                ('operator',lambda a,m:m.update(operator='unsymmetrized')),
                ('last_cache',lambda a,m:a['KV'].__setitem__((1,-1),a['KV'][1,-1]+1)),
                ('direct',lambda a,m:m.update(direct_moments=[.7,0,0])),
                ('next',lambda a,m:a['next_vector'].__setitem__(1,2)),
                ('g',lambda a,m:a['ground'].__setitem__(1,.1)),
                ('current_missing_operator',lambda a,m:m['identities'].update(runner=b.sha(r.__file__))),
            ]
            for name,fn in mutations:
                target=td/(name+'.npz');mutate(cp,target,fn)
                with self.subTest(name=name),self.assertRaises((ValueError,TypeError)):
                    r.load_checkpoint(target,g,u,.7)
            corrupt={**state,'KV':state['KV'].copy()}; corrupt['KV'][:,0]+=.01
            bu=budget();bad=r.cache_seam_checks(lambda v:bu.apply(lambda x:K@x,v),corrupt)
            self.assertFalse(bad['passed']);self.assertEqual(bu.actions,3)
            mutate(cp,td/'unknown.npz',lambda a,m:m.update(reorthogonalization_correction_norms_Eh=[None]*16))
            self.assertEqual(r.load_checkpoint(td/'unknown.npz',g,u,.7)['corrections'],[None]*16)

    def test_budget_and_deadline_before_and_after_actions(self):
        v=np.ones(2); calls=[]
        bu=budget(maximum=0)
        with self.assertRaises(b.Deferred):bu.apply(lambda x:calls.append(1) or x,v)
        self.assertEqual(calls,[]);self.assertEqual(bu.actions,0)
        bu=budget(seconds=-1)
        with self.assertRaises(b.Deferred):bu.apply(lambda x:calls.append(1) or x,v)
        self.assertEqual(calls,[])
        bu=budget()
        def crosses_deadline(x):bu.deadline=time.monotonic()-1;return x
        with self.assertRaises(b.Deferred):bu.apply(crosses_deadline,v)
        self.assertEqual(bu.actions,1)
        K,g,u=fixture(d=40)
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);legacy(td/'old',K,g,u,16)
            state=r.load_checkpoint(td/'old/checkpoint.npz',g,u,.7)
            bu=budget(maximum=0)
            with self.assertRaises(b.Deferred):r.resume_chain(lambda x:bu.apply(lambda y:K@y,x),state,g,u,.7,32,bu)
            self.assertEqual(bu.actions,0)

    def test_happy_breakdown_no_actions(self):
        g=np.array([1.,0.,0.]);u=np.array([0.,1.,0.]);K=np.diag([0.,2.,3.])
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);legacy(td/'old',K,g,u,16)
            state=r.load_checkpoint(td/'old/checkpoint.npz',g,u,.7)
            self.assertEqual(state['stop'],'certified_invariant_subspace')
            bu=budget();result,_,_,_=r.resume_chain(lambda x:bu.apply(lambda y:K@y,x),state,g,u,.7,128,bu)
            self.assertEqual(bu.actions,0);self.assertEqual(result['last_length'],1)

    def test_residual_bound_independent_dense_coordinate_defect_and_J(self):
        K,g,u=fixture(d=24,complex_=True)
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);legacy(td/'old',K,g,u,16)
            with np.load(td/'old/checkpoint.npz',allow_pickle=False) as f:V=f['V']; KV=f['KV']
            # Exercise both a coordinate defect and a small cache rounding perturbation.
            # The perturbation is within inherited scaled cache/anti-Hermitian limits.
            V=V.copy();V[:,1]+=2e-8*V[:,0];KV=K@V;KV[:,1]+=2e-9*V[:,0]
            u2=u+1e-3*V[:,2];u2/=np.linalg.norm(u2)
            C=V.conj().T@KV
            self.assertGreater(np.linalg.norm(C-C.conj().T),1e-9)
            diag=r.residual_diagnostic(V,KV,u2,.7,grid=np.array([.1,2.,100.,220.,399.]),etas=(.05,.1,.2))
            w,Y=np.linalg.eigh(K)
            measured=[]
            for ei,eta in enumerate(diag['etas']):
                for wi,omega in enumerate(diag['grid']):
                    reference=np.sum(abs(Y.conj().T@u2)**2/(omega+1j*eta-w))
                    error=abs(reference-diag['scalar_resolvent'][ei,wi])
                    self.assertLessEqual(error,diag['scalar_bound'][ei,wi]+1e-10*max(1,abs(reference)))
                    J=(C+C.conj().T)/2;t=np.linalg.solve((omega+1j*eta)*np.eye(16)-J,np.eye(16)[:,0])
                    direct=float(np.linalg.norm(u2))*np.linalg.norm(u2-V[:,0]+(KV-V@J)@t)/eta+abs((u2.conj()@V-np.eye(16)[0])@t)
                    self.assertAlmostEqual(diag['scalar_bound'][ei,wi],direct,places=8)
                    measured.append({'eta':float(eta),'omega':float(omega),'error':float(error),'bound':float(diag['scalar_bound'][ei,wi])})
            self.assertGreater(np.max(diag['coordinate_delta']),0)
            OBSERVED['residual_bound']=measured

    def test_J_residual_uses_symmetrized_matrix(self):
        V=np.eye(3)[:,1:];K=np.diag([0.,2.,5.]);KV=K@V;KV[:,1]+=1e-10*V[:,0]
        u=V[:,0].copy();diag=r.residual_diagnostic(V,KV,u,.7,grid=np.array([2.]),etas=(.05,))
        C=V.T@KV;J=(C+C.T)/2;t=np.linalg.solve((2+.05j)*np.eye(2)-J,np.array([1.,0.]))
        expected=np.linalg.norm((KV-V@J)@t)/.05
        self.assertGreater(diag['scalar_bound'][0,0],1e-9)
        self.assertAlmostEqual(diag['scalar_bound'][0,0],expected,places=14)
        OBSERVED['J_vs_C']={'antihermitian_inf':float(np.linalg.norm(C-C.T,np.inf)),
            'bound_using_J':float(diag['scalar_bound'][0,0]),'incorrect_bound_using_C':0.}

    def test_nine_reconstruction_gates_plus_cache_actions(self):
        K,g,u=fixture(d=40);E0=-2.;H=K+E0*np.eye(40);i=np.sqrt(.3)*g+np.sqrt(.7)*u
        bu=budget();checks=b.reconstruction_checks(lambda v:bu.apply(lambda x:H@x,v),i,g,u,E0,np.vdot(i,H@i).real,np.vdot(H@i,H@i).real,0.)
        self.assertTrue(checks['passed']);self.assertEqual(len(checks['gates']),9);self.assertEqual(bu.actions,3)
        OBSERVED['reconstruction']={'gates':checks['gates'],'actions':bu.actions}

    def test_cli_prepare_allocation_denial_and_supervision(self):
        now=time.time()
        allocation={'authorized':True,'allocation_id':'synthetic-test','issued_utc':r.dt.datetime.fromtimestamp(now-1,r.dt.timezone.utc).isoformat(),
            'absolute_deadline_utc':r.dt.datetime.fromtimestamp(now+100,r.dt.timezone.utc).isoformat(),'wall_s':7200,'memory_gib':24,'omp_threads':12,'blas_threads':1,'maximum_new_Hamiltonian_actions':70}
        self.assertGreater(r.validate_allocation(allocation),0)
        for bad in [{**allocation,'authorized':False},{**allocation,'maximum_new_Hamiltonian_actions':160},{**allocation,'absolute_deadline_utc':r.HISTORY['absolute_deadline_utc']}]:
            with self.assertRaises(ValueError):r.validate_allocation(bad)
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            command=[sys.executable,str(ROOT/'code/t4_resume.py'),'prepare','--out',str(td/'prepared')]
            proc=subprocess.run(command,capture_output=True,text=True,timeout=10)
            self.assertEqual(proc.returncode,0,proc.stderr)
            prepared=json.loads((td/'prepared/allocation_template.json').read_text());self.assertFalse(prepared['authorized'])
            proc=subprocess.run(command,capture_output=True,text=True,timeout=10);self.assertEqual(proc.returncode,1)
            (td/'supervised').mkdir()
            result=b.supervise([sys.executable,'-c','import time; time.sleep(2)'],td/'supervised',.1,1.,headroom_gib=0)
            self.assertEqual(result['supervisor_stop_reason'],'wall_limit')
            self.assertLess(result['supervisor_exit_code'],0)
            OBSERVED['supervisor']={'reason':result['supervisor_stop_reason'],'exit_code':result['supervisor_exit_code'],'wall_s':result['supervisor_wall_s']}


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ResumeTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    output=os.environ.get('UNIT5_OBSERVATIONS')
    if output:Path(output).write_text(json.dumps({'fixture_kind':'synthetic NumPy dense; not actual physical H','observations':OBSERVED},indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
