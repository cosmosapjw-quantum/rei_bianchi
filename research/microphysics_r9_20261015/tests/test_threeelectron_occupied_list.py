"""Compare unpenalized RDM-spin backend to ordinary spin-penalized FCI."""
from pathlib import Path
import sys,os,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import microphysics_driver_v6 as m
import numpy as np
from pyscf import lib
lib.num_threads(2)
try:lib.current_memory()
except FileNotFoundError:
    def mem():
        v,r=map(int,Path('/proc/self/statm').read_text().split()[:2]);p=os.sysconf('SC_PAGE_SIZE');return r*p/1e6,v*p/1e6
    lib.current_memory=mem
class OccupiedListBackendChecks(unittest.TestCase):
    def test_real_small_Li_Be_union(self):
        case=dict(kind='quench',basis='cc-pvdz',basis_elements=['Li','Be'],initial_symbol='Li',final_symbol='Be',initial_charge=0,final_charge=1,spin=1,memory_gib=8,threads=2,fci_tol=1e-13,residual_tol=1e-10)
        ordinary,_=m.quench(case)
        unpenalized,_=m.quench(case|dict(validate_occupied_list_backend=True))
        for name in ['parent','daughter']:
            self.assertLess(abs(ordinary[name]['E_BO_Eh']-unpenalized[name]['E_BO_Eh']),1e-9)
            self.assertLess(abs(unpenalized[name]['spin_squared']-.75),1e-6)
            self.assertLess(unpenalized[name]['checks']['original_H_residual_Eh'],1e-7)
            self.assertEqual(unpenalized[name]['solver_backend'],'unpenalized_direct_spin1_occupied_list_capable_RDM_spin')
        self.assertLess(abs(ordinary['P_ground']-unpenalized['P_ground']),1e-8)
        self.assertLess(unpenalized['checks']['closure_error'],1e-10)
if __name__=='__main__':unittest.main(verbosity=2)
