"""Public-only regression tests for the verified 8–16 saved-cell continuation."""
import json,sys,tempfile,unittest
from pathlib import Path
from fractions import Fraction as Q

SRC=Path(__file__).resolve().parents[1]/"src"
sys.path.insert(0,str(SRC))
from stage_cell import WORDS,DASH,new_warm_interval,new_assembler,stage
from admit_cell import collision_lower,collision_upper,directed
from run_remaining import write_atomic

class TestP01Continuation(unittest.TestCase):
    def test_all_saved_cell_names_and_count(self):
        self.assertEqual(set(WORDS),set(range(7,17)))
        self.assertEqual(set(DASH),set(range(7,17)))
        self.assertEqual(WORDS[16],"sixteen")
        self.assertEqual(DASH[16],"SIXTEENTH")

    def test_first_remaining_global_shear_source_clock(self):
        src="""return self.global_volume(z+6)
xq=lo(x)+6
if xq<6 or hi(x)+6>7:raise ValueError('SEVENTH_CELL_SHEAR_DOMAIN')
return bound(0,7*self.h*self.si)
"""
        out=new_warm_interval(src,8)
        for span in ("global_volume(z+7)","xq=lo(x)+7",
                     "hi(x)+7>8","EIGHTH_CELL_SHEAR_DOMAIN",
                     "bound(0,8*self.h*self.si)"):
            self.assertIn(span,out)
        with self.assertRaisesRegex(ValueError,"INHERITED_CODE_ANCHOR"):
            new_warm_interval(out,8)

    def test_last_remaining_global_clock(self):
        src="""return self.global_volume(z+14)
xq=lo(x)+14
if xq<14 or hi(x)+14>15:raise ValueError('FIFTEENTH_CELL_SHEAR_DOMAIN')
return bound(0,15*self.h*self.si)
"""
        out=new_warm_interval(src,16)
        self.assertIn("global_volume(z+15)",out)
        self.assertIn("hi(x)+15>16",out)
        self.assertIn("SIXTEENTH_CELL_SHEAR_DOMAIN",out)
        self.assertIn("bound(0,16*self.h*self.si)",out)

    def test_simultaneous_state_and_electron_indexes(self):
        src="""left=archived_state['states'][:s.n,6]
right=archived_state['states'][:s.n,7]
ne0=rows[6]['ne_cm3']
ne1=rows[7]['ne_cm3']
err='SEVENTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'
stage='HE18_C9'
clock=[str(6*h),str(7*h)]
ref='seventh-cell FIXED_REFERENCE.npz exact dyadic coefficients'
"""
        out=new_assembler(src,8)
        for required in ("left=archived_state['states'][:s.n,7]",
           "right=archived_state['states'][:s.n,8]",
           "ne0=rows[7]['ne_cm3']",
           "ne1=rows[8]['ne_cm3']",
           "EIGHTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH",
           "stage='HE18_C10'",
           "[str(7*h),str(8*h)]",
           "eighth-cell FIXED_REFERENCE.npz exact dyadic coefficients"):
            self.assertIn(required,out)

    def test_bernstein_and_collision_interval_bounds(self):
        for k in (Q(1,100000000),Q(1,1000000),Q(1,100)):
            self.assertTrue(0<collision_lower(k)<collision_upper(k)<k)
        lo=directed(Q(1,3),True)
        hi=directed(Q(1,3),False)
        self.assertLessEqual(Q(lo),Q(1,3))
        self.assertGreaterEqual(Q(hi),Q(1,3))

    def test_stop_on_existing_output_does_not_delete_it(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)
            f=path/"known.json"
            write_atomic(f,{"status":"COMPLETE"})
            with self.assertRaises(ValueError):
                stage(path,path,8)
            self.assertTrue(f.exists())
            self.assertEqual(json.loads(f.read_text())["status"],"COMPLETE")

    def test_durable_checkpoint_overwrite_is_explicit(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/"state.json"
            write_atomic(out,{"completed":[8]})
            write_atomic(out,{"completed":[8,9]})
            self.assertEqual(json.loads(out.read_text())["completed"],[8,9])
            self.assertFalse(out.with_suffix(".partial.json").exists())

if __name__=="__main__":unittest.main()
