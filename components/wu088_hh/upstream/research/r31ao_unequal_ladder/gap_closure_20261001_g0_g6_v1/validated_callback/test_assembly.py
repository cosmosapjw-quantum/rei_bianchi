"""Synthetic exact/static checks of S01 registry, contractions and D assembly."""
from fractions import Fraction as Q
from pathlib import Path
import unittest
from assembly_exact import QC, registry, contract_entry, phase_argument, final_blocks


class AssemblyExactTests(unittest.TestCase):
    def test_registry_excludes_only_duplicate_ground(self):
        rows=registry()
        self.assertEqual(len(rows),47)
        self.assertEqual(rows[:24],[(0,j) for j in range(24)])
        self.assertEqual(rows[24:],[(1,j) for j in range(1,24)])
        self.assertNotIn((1,0),rows)

    def test_all_144_signed_coefficient_products_and_order(self):
        left=[Q(i-5,7) for i in range(12)]
        ground=[Q(8-j,11) for j in range(12)]
        raw=[[QC(Q(100*i+j),Q(7*i-3*j)) for j in range(12)] for i in range(12)]
        got=contract_entry(raw,left,ground,orbital=0,field=0,cusp=0)
        expected=QC(Q(0),Q(0))
        for j in range(12):
            for i in range(12): expected+=raw[i][j]*(left[i]*ground[j])
        self.assertEqual(got,expected)
        self.assertNotEqual(got,contract_entry(raw,ground,left,0,0,0))

    def test_every_orbital_field_reflection_sign(self):
        raw=[[QC(Q(0)) for _ in range(12)] for _ in range(12)]
        raw[2][5]=QC(Q(3),Q(-4))
        left=[Q(int(i==2)) for i in range(12)]
        ground=[Q(int(i==5)) for i in range(12)]
        for orbital in range(3):
            for field in range(3):
                for cusp in range(2):
                    p=(-1 if cusp and orbital else 1)*(-1 if cusp and field else 1)
                    self.assertEqual(contract_entry(raw,left,ground,orbital,field,cusp),raw[2][5]*p)

    def test_phase_tau_and_center_signs_exact(self):
        z,v,en,ei=Q(3,4),Q(2,7),Q(-3,5),Q(7,11)
        # 2 kc cz = vz/2 for both cusps; tau is the exact ratio z/v.
        for cusp in (0,1):
            self.assertEqual(phase_argument(z,v,en,ei,cusp),v*z/2+(en-ei)*z/v)
        with self.assertRaises(ValueError): phase_argument(z,Q(0),en,ei,0)

    def test_post_phase_conjugation_and_exact_D(self):
        v,en,ei=Q(2),Q(5),Q(7)
        O,G1,G2=QC(Q(1),Q(2)),QC(Q(3),Q(4)),QC(Q(-2),Q(5))
        for active in (0,1):
            for cusp in (0,1):
                dc,dr=final_blocks(O,G1,G2,v,en,ei,active,cusp)
                kc=Q(1 if cusp==0 else -1)
                ka=Q(1 if active==0 else -1)
                self.assertEqual(dc,(G1+G2)*kc+QC(Q(0),2*kc*kc-ei)*O)
                self.assertEqual(dr,G1.conjugate()*(-ka)+G2.conjugate()*ka-QC(Q(0),en)*O.conjugate())
                self.assertNotEqual(dr,dc.conjugate())

    def test_reject_unbound_shapes_indices(self):
        with self.assertRaises(ValueError): contract_entry([],[],[],0,0,0)
        with self.assertRaises(ValueError): phase_argument(Q(1),Q(2),Q(0),Q(0),2)

    def test_native_stage_and_no_callback_conjugation(self):
        root=Path(__file__).parent
        callback=(root/'callback.cpp').read_text()
        assembly=(root/'assembly.cpp').read_text()
        self.assertNotIn('acb_conj(',callback)
        self.assertIn('acb_conj(',assembly)
        self.assertIn('unnormalized_real_domain_integrals',assembly)
        self.assertIn('normalization_factor',assembly)
        self.assertIn('active ^ cusp',assembly)
        self.assertNotIn('double',assembly)
        self.assertNotIn('radial(',assembly)


if __name__=='__main__': unittest.main(verbosity=2)
