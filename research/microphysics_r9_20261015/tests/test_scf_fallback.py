"""Full-space FCI must remain valid when SCF is only an orbital initializer."""
from pathlib import Path
import sys,unittest,os
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import microphysics_driver_v4 as m
from pyscf import scf,lib
lib.num_threads(2)
try:lib.current_memory()
except FileNotFoundError:
    def mem():
        v,r=map(int,Path('/proc/self/statm').read_text().split()[:2]);p=os.sysconf('SC_PAGE_SIZE');return r*p/1e6,v*p/1e6
    lib.current_memory=mem
class SCFInitializerChecks(unittest.TestCase):
    def test_unconverged_MO_and_canonical_irrep_recovery(self):
        case={'memory_gib':4,'threads':2,'fci_tol':1e-12}
        def molecule():return m.mol_build([('Li',(0,0,-1.6)),('H',(0,0,1.6))],'sto-3g',0,0,4,True)
        reference,_,_=m.stationary(molecule(),case);factory=scf.RHF
        def unconverged(mol):
            mf=factory(mol);original=mf.kernel
            def run(*args,**kwargs):
                e=original(*args,**kwargs);mf.converged=False;return e
            mf.kernel=run;return mf
        with mock.patch('pyscf.scf.RHF',side_effect=unconverged):a,_,_=m.stationary(molecule(),case)
        self.assertFalse(a['scf_converged']);self.assertTrue(a['finite_model_numerics_passed'])
        self.assertEqual(a['orbital_source'],'unconverged_SCF_full_orthonormal_MOs')
        self.assertLess(abs(a['E_BO_Eh']-reference['E_BO_Eh']),1e-9)
        def broken(mol):
            mf=factory(mol)
            def run(*args,**kwargs):raise RuntimeError('forced SCF initializer failure')
            mf.kernel=run;return mf
        with mock.patch('pyscf.scf.RHF',side_effect=broken):b,_,_=m.stationary(molecule(),case)
        self.assertFalse(b['scf_converged']);self.assertTrue(b['finite_model_numerics_passed'])
        self.assertEqual(b['orbital_source'],'canonical_AO_metric_orthogonalization_by_C2v_irrep')
        self.assertLess(abs(b['E_BO_Eh']-reference['E_BO_Eh']),1e-9)
if __name__=='__main__':unittest.main(verbosity=2)
