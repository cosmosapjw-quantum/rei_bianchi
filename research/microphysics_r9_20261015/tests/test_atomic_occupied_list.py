"""Validate the occupied-list-capable atomic Li route against penalized FCI."""
from pathlib import Path
import sys,os,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import microphysics_driver_v7 as m
from pyscf import lib
lib.num_threads(2)
try:lib.current_memory()
except FileNotFoundError:
    def mem():
        v,r=map(int,Path('/proc/self/statm').read_text().split()[:2]);p=os.sysconf('SC_PAGE_SIZE');return r*p/1e6,v*p/1e6
    lib.current_memory=mem
class AtomicOccupiedListChecks(unittest.TestCase):
    def test_Li_energy_spin(self):
        case=dict(kind='atomic',species='Li',basis='cc-pvdz',memory_gib=8,threads=2,fci_tol=1e-13,residual_tol=1e-10)
        ordinary,_=m.atomic(case)
        unpenalized,_=m.atomic(case|dict(validate_occupied_list_backend=True))
        self.assertLess(abs(ordinary['E_BO_Eh']-unpenalized['E_BO_Eh']),1e-9)
        self.assertLess(abs(unpenalized['spin_squared']-.75),1e-6)
        self.assertLess(unpenalized['checks']['original_H_residual_Eh'],1e-7)
        self.assertEqual(unpenalized['solver_backend'],'unpenalized_direct_spin1_occupied_list_capable_RDM_spin')
if __name__=='__main__':unittest.main(verbosity=2)
