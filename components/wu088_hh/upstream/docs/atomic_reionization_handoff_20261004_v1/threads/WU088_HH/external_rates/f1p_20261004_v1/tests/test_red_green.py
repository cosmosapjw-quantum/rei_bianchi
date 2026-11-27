from pathlib import Path
import sys, unittest
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hh_pair_reference import paired_reference

def close(base,places):
    return str(base)+'.'+'0'*(places-1)+'1'

class PairContract(unittest.TestCase):
    def test_equal_states_cancel_exactly(self):
        r=paired_reference('LCS91','10000','2','10000','2','3e-18')
        self.assertEqual([D(x) for x in r['delta_event_m3_s']],[D(0),D(0)])
    def test_sub_precision_temperature_difference_keeps_sign(self):
        r=paired_reference('LCS91','10000','2',close(10000,96),'2','3e-18')
        self.assertGreater(D(r['delta_event_m3_s'][0]),0)
    def test_sub_precision_density_difference_keeps_sign(self):
        r=paired_reference('LCS91','10000','2','10000',close(2,100),'3e-18')
        self.assertGreater(D(r['delta_event_m3_s'][0]),0)
    def test_cutoff_records_nonvanishing_jump(self):
        r=paired_reference('LCS91','3000','2',close(3000,20),'2','3e-18')
        self.assertEqual(r['branch_event'],'CROSSES_DISCONTINUOUS_3000K')
        self.assertIsNotNone(r['rate_decomposition']['jump_cm3_s'])
if __name__=='__main__':unittest.main()
