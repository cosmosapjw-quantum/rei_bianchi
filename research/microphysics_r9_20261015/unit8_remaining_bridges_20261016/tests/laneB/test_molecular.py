import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'code/laneB/molecular.py';s=importlib.util.spec_from_file_location('mol',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class NuclearTests(unittest.TestCase):
    def test_rotational_angular_factor(self):
        self.assertAlmostEqual(m.einstein(.001,1.,0,1)/m.einstein(.001,1.,1,0),3.)
        self.assertEqual(m.einstein(.001,1.,0,0),0)
    def test_global_dipole_sign(self):self.assertEqual(m.einstein(.002,2.,1,2),m.einstein(.002,-2.,1,2))
    def test_mass_convention_is_explicit(self):self.assertLess(m.mu_mass(),m.mu_mass(True))
if __name__=='__main__':unittest.main()
