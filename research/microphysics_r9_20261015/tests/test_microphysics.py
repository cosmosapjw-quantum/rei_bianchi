"""Small numerical checks; STO-3G is a fixture basis, not production input."""
import json
from pathlib import Path
import sys,unittest,os
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import microphysics_driver_v3 as m
from pyscf import gto,ao2mo,lib
lib.num_threads(2)
try:lib.current_memory()
except FileNotFoundError:
    def mem():
        v,r=map(int,Path('/proc/self/statm').read_text().split()[:2]);p=os.sysconf('SC_PAGE_SIZE');return r*p/1e6,v*p/1e6
    lib.current_memory=mem
class NumericalChecks(unittest.TestCase):
    def test_common_rotation_preserves_quench(self):
        c=dict(memory_gib=4,threads=2,basis='sto-3g',fci_tol=1e-13,residual_tol=1e-10)
        info,a=m.quench(c);X=a['common_orbital_matrix'];Q=np.linalg.qr(np.random.default_rng(417).normal(size=(X.shape[1],X.shape[1])))[0];Xr=X@Q
        b=gto.basis.load('sto-3g','Li');ci=[];energies=[]
        for atom,charge in [('He',0),('Li',1)]:
            mol=m.mol_build([(atom,(0,0,0))],{atom:b},charge,0,4)
            h=Xr.T@(mol.intor('int1e_kin')+mol.intor('int1e_nuc'))@Xr;eri=ao2mo.kernel(mol,Xr)
            ii,aa,_=m.solve_integrals(mol,Xr,h,eri,c);ci.append(aa['CI']);energies.append(ii['E_BO_Eh'])
        self.assertLess(abs(abs(np.vdot(*ci))**2-info['P_ground']),1e-8)
        self.assertAlmostEqual(energies[0],info['parent']['E_BO_Eh'],places=10)
        self.assertAlmostEqual(energies[1],info['daughter']['E_BO_Eh'],places=10)
    def test_projected_response_moments(self):
        info,a=m.response(dict(memory_gib=4,threads=2,basis='sto-3g',lengths=[8,16]))
        self.assertTrue(info['response_internal_numerics_passed'])
        for L in [8,16]:
            omega=a[f'ritz_omega_L{L}_Eh'];weights=a[f'ritz_weights_L{L}']
            np.testing.assert_allclose([sum(weights*omega**k) for k in range(3)],info['direct_moments_au'],atol=1e-10,rtol=1e-10)
        self.assertEqual(info['physical_continuum_status'],'missing_provider_or_boundary_validation')
    def test_tighter_energy(self):
        c=dict(memory_gib=4,threads=2,basis='sto-3g',species='Li')
        first,_=m.atomic(c);tight,_=m.atomic(c|dict(fci_tol=1e-13,residual_tol=5e-8))
        self.assertLess(abs(first['E_BO_Eh']-tight['E_BO_Eh']),1e-9)
    def test_resource_refusal(self):
        with self.assertRaises(m.Deferred):m.estimate(100,(3,2),16)
if __name__=='__main__':unittest.main(verbosity=2)
