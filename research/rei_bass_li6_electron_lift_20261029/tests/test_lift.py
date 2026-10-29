import importlib.util, json, random, unittest
from fractions import Fraction as Q
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lift',ROOT/'code/lift.py')
l=importlib.util.module_from_spec(spec); spec.loader.exec_module(l)

class TestLiLift(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model,cls.saved=l.load_inputs()
        cls.norm,cls.nu,cls.gamma=l.owner_scales(cls.model)
        cls.p={ (Z,q):Q(Z+q+2,13) for Z in (1,2,3) for q in range(Z)}
        cls.r={ (Z,q):Q(Z+2*q+1,17) for Z in (1,2,3) for q in range(1,Z+1)}
        cls.A,cls.R=l.operator_blocks(cls.p,cls.r,neutron=Q(1,8784),tritium=Q(1,1232))
        cls.y=[Q(1+i%3,57) for i in range(17)]
        cls.y[13:17]=[cls.nu['Li7']*Q(i+1,10) for i in range(4)]
        cls.nb=Q(2,7)

    def test_01_source_checks(self):
        for name in l.SOURCE_LOCK: self.assertGreater(len(l.source_bytes(name)),1000)
    def test_02_correct_source_order(self):
        self.assertEqual(len(l.RETAIN),17);self.assertEqual(l.RETAIN[-4:],(17,18,19,20))
    def test_03_model_positive_inventory(self):
        self.assertGreater(self.nu['Li6'],0);self.assertGreater(self.nu['Li7'],0)
    def test_04_source_initial_li6_li7_charge_equals(self):
        self.assertEqual(self.model['initial_lithium_charge'],1)
    def test_05_gamma_owner_exact_repr(self):
        self.assertEqual(self.gamma,self.nu['Li6']/self.nu['Li7'])
        self.assertNotEqual(self.gamma,Q(1,50000))  # owner float64 represented-real identity
    def test_06_lift_projection_identity(self):
        self.assertEqual(l.select21(l.lift17(self.y,self.gamma)),self.y)
    def test_07_charge_covector_identity(self):
        yy=l.lift17(self.y,self.gamma)
        self.assertEqual(l.dot(l.Q21,yy),l.dot(l.effective_charge17(self.gamma),self.y))
    def test_08_delta_ion_charge_positive(self):
        d=sum((self.gamma*k*self.y[13+k] for k in range(4)),Q(0))
        self.assertGreater(d,0)
    def test_09_photo_recomb_matrix_conserves_nuclei(self):
        mass=[l.MASS[k] for k,indices in l.GROUPS.items() for _ in indices]
        for operator in (self.A,self.R):
            for j in range(21):self.assertEqual(sum(mass[i]*operator[i][j] for i in range(21)),0)
    def test_10_recombined_F_exact(self):
        self.assertEqual(l.source_intertwining(self.A,self.R,self.y,self.nb,self.gamma)[0],0)
    def test_11_recombined_J_exact(self):
        self.assertEqual(l.source_intertwining(self.A,self.R,self.y,self.nb,self.gamma)[1],0)
    def test_12_true_21_reduced_17_source_equivalent(self):
        ff=l.full_rhs(self.A,self.R,l.lift17(self.y,self.gamma),self.nb)
        self.assertEqual(ff,l.lift17(l.select21(ff),self.gamma))
    def test_13_random_21_state_intertwining(self):
        rng=random.Random(291029)
        for k in range(22):
            y=[Q(rng.randrange(1,101),rng.randrange(101,401)) for _ in range(17)]
            y[13:17]=[self.nu['Li7']*Q(i,10) for i in (1,2,3,4)]
            b=Q(rng.randrange(1,10),rng.randrange(11,40))
            self.assertEqual(l.source_intertwining(self.A,self.R,y,b,self.gamma),(0,0))
    def test_14_reduced_F_delta_effective_electron(self):
        eta,df,dj=l.delta_chemistry(self.A,self.R,self.y,self.nb,self.gamma)
        x=l.lift17(self.y,self.gamma)
        no_li_charge=l.dot(l.Q17,self.y)
        self.assertEqual(l.dot(l.Q21,x)-no_li_charge,eta)
        ry=l.matvec([[self.R[i][j] for j in l.RETAIN] for i in l.RETAIN],self.y)
        self.assertEqual(df,[self.nb*eta*v for v in ry])
    def test_15_delta_J_two_terms(self):
        eta,df,dj=l.delta_chemistry(self.A,self.R,self.y,self.nb,self.gamma)
        h=Q(1,999)
        moved=self.y.copy();moved[15]+=h
        eta2,df2,_=l.delta_chemistry(self.A,self.R,moved,self.nb,self.gamma)
        for i in range(17):
            # quadratic source: finite difference equals Jacobian plus O(h)
            self.assertEqual((df2[i]-df[i])/h-dj[i][15],
             self.nb*(self.gamma*2)*self.R[l.RETAIN[i]][l.RETAIN[15]]*h)
    def test_16_delta_J_not_just_outer_rankone(self):
        _,_,dj=l.delta_chemistry(self.A,self.R,self.y,self.nb,self.gamma)
        self.assertGreaterEqual(sp.Matrix(dj).rank(),2)
    def test_17_gamma_source_rate_mismatch_reject(self):
        perturbed,_=l.operator_blocks(self.p,self.r,Q(1,8784),Q(1,1232),li6_photo_override=self.p[(3,0)]+Q(1,11))
        self.assertGreater(l.source_intertwining(perturbed,self.R,self.y,self.nb,self.gamma)[0],0)
    def test_18_neutron_T_positive_break_helium_equality(self):
        # T0 beta->He3+ but never directly He4+: imbalance source=λT*T0.
        y21=l.lift17(self.y,self.gamma)
        self.assertEqual(self.A[8][5],Q(1,1232));self.assertEqual(self.A[11][5],0)
        self.assertGreater(self.A[8][5]*y21[5],0)
    def test_19_Li6_t_tau_source_positive(self):
        d=sum(self.gamma*k*self.y[13+k] for k in range(4))
        self.assertGreater(d,0)
        self.assertLessEqual(d,3*self.nu['Li6'])
    def test_20_sharp_li_bounds(self):
        for q in range(4):
            r=[Q(0)]*17;r[13+q]=self.nu['Li7']
            s=sum(l.effective_charge17(self.gamma)[j]*r[j] for j in range(13,17))
            self.assertEqual(s,self.nu['Li7']*q+self.nu['Li6']*q)
    def test_21_fixed_initial_electron(self):
        self.assertGreater(Q(l.diagnostics()['initial_Li6_fraction_of_total_electrons']),0)
    def test_22_seven_REI_snapshots_counterfactual_only(self):
        obj=l.diagnostics()
        self.assertEqual(len(obj['source_only_REI_seven_counterfactual']),7)
        self.assertFalse(obj['actual_rei_source_rates_equal'])
    def test_23_no_physical_tau(self):
        self.assertFalse(l.diagnostics()['full_BASS_native_network_evaluated'])
    def test_24_variable_clock_pullback(self):
        # x=1, Y= (1+x)^3; rho=1+x; y= (1+x)^2, y'=2(1+x)=4
        self.assertEqual(l.rho_pullback([Q(8)],[Q(12)],Q(2),Q(1)),[Q(4)])
    def test_25_nonpositive_rho_refuse(self):
        with self.assertRaises(ValueError): l.rho_pullback([1],[1],0,1)
    def test_26_nonpositive_gamma_refuse(self):
        with self.assertRaises(ValueError): l.lift17(self.y,0)
    def test_27_float_disallowed_for_exact_contract(self):
        with self.assertRaises(TypeError): l.lift17([0.5]*17,self.gamma)
    def test_28_source_hash_negative(self):
        original=l.SOURCE_LOCK['BASS_ATOMIC_MODEL.json']
        try:
            l.SOURCE_LOCK['BASS_ATOMIC_MODEL.json']='0'*64
            with self.assertRaisesRegex(ValueError,'SOURCE_SHA256_MISMATCH'):l.load_inputs()
        finally:l.SOURCE_LOCK['BASS_ATOMIC_MODEL.json']=original
    def test_29_identical_lithium_source_blocks(self):
        # Actual source uses the same Z,q electronic rates for Li6 and Li7.
        for j in range(4):
            for i in range(4):
                self.assertEqual(self.A[13+i][13+j],self.A[17+i][17+j])
                self.assertEqual(self.R[13+i][13+j],self.R[17+i][17+j])
    def test_30_red_J_dimension(self):
        J=l.reduced_jacobian(self.A,self.R,self.y,self.nb,self.gamma)
        self.assertEqual((len(J),len(J[0])),(17,17))

if __name__=='__main__':unittest.main()
