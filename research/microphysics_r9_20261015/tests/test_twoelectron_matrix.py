"""Validate the exact 2e matrix backend against independent PySCF action/FCI."""
from pathlib import Path
import sys,unittest,os
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import microphysics_driver_v3 as m
import numpy as np
from pyscf import gto,ao2mo,lib
lib.num_threads(2)
try:lib.current_memory()
except FileNotFoundError:
    def mem():
        v,r=map(int,Path('/proc/self/statm').read_text().split()[:2]);p=os.sysconf('SC_PAGE_SIZE');return r*p/1e6,v*p/1e6
    lib.current_memory=mem
class ExactMatrixChecks(unittest.TestCase):
    def test_native_action_energy_and_projection(self):
        b=gto.basis.load('sto-3g','Li');a=m.mol_build([('He',(0,0,0))],{'He':b},0,0,4)
        S=a.intor('int1e_ovlp');ss,U=np.linalg.eigh(S);X=U/np.sqrt(ss)
        eri=ao2mo.kernel(a,X);native=[];matrix=[]
        case={'memory_gib':4,'fci_tol':1e-13,'residual_tol':1e-10}
        for symbol,charge in [('He',0),('Li',1)]:
            mol=m.mol_build([(symbol,(0,0,0))],{symbol:b},charge,0,4);h=X.T@(mol.intor('int1e_kin')+mol.intor('int1e_nuc'))@X
            ni,na,nh=m.solve_integrals(mol,X,h,eri,case)
            mi,ma,mh=m.solve_twoelectron_matrix(mol,X,h,eri,case)
            trial=np.random.default_rng(347).normal(size=(X.shape[1],X.shape[1]));trial=(trial+trial.T)/2;trial/=np.linalg.norm(trial)
            np.testing.assert_allclose(nh(trial),mh(trial),atol=1e-11,rtol=1e-11)
            self.assertLess(abs(ni['E_BO_Eh']-mi['E_BO_Eh']),1e-9)
            self.assertLess(mi['checks']['original_H_residual_Eh'],1e-9)
            native.append(na['CI']);matrix.append(ma['CI'])
        self.assertLess(abs(abs(np.vdot(*native))**2-abs(np.vdot(*matrix))**2),1e-8)
if __name__=='__main__':unittest.main(verbosity=2)
