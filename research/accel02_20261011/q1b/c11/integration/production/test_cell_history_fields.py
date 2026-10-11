"""Only new P2 binding tests; manufactured kernels are not scientific trajectories."""
import copy
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
import numpy as np
import native_step_v4_diagnostics as v4
import cell_history_fields as fields


class Provider:
    r=0.
    def geometry(self,t):
        return dict(a_rel=2.,b=0.,H=0.,s=0.,nH=2.,nHe=.2,z=7.,Tcmb_K=20.)
    def ray(self,q,mu,t):return np.asarray(q)*.5,np.asarray(mu).copy(),np.full(len(mu),.5)


def fixture():
    p=Provider()
    source=SimpleNamespace(provider=p,mu=np.array([-.5,.5]),weights=np.array([.5,.5]),edges=np.array([20.,80.]))
    state=dict(t_s=0.,gas=np.array([.2,.1,.05,.02]),N=np.array([[2.],[3.]]),U_eV=np.array([[40.],[60.]]),R=np.full((2,1),.5),support=np.array([[[20.,80.]],[[20.,80.]]]),counters={k:0. for k in v4.COUNTER_NAMES},nH_ref=16.,nHe_ref=1.6)
    def integrate(*args,**kwargs):return dict(R1=np.full(2,.5),dN=np.zeros((2,1)),injected_energy_eV=np.zeros((2,1)),diagnostics={})
    def advance(N,U,result):return dict(N=N.copy(),U_eV=U.copy(),radiation_work_eV=np.zeros_like(U),diagnostics={})
    src=SimpleNamespace(provider_event_times=lambda *a:(),integrate_source=integrate,advance_source=advance,
        StableCellSource=lambda source:SimpleNamespace(source=lambda t:{'N':np.array([[4.],[5.]]),'U_eV':np.array([[80.],[100.]])}))
    return source,state,src


class Absorption:
    def __init__(self):self.prepare_calls=0;self.absorb_calls=0
    def prepare_incident(self,N,U,R,a,b,opacity,**kwargs):
        self.prepare_calls+=1
        return SimpleNamespace(N=N,U=U,diagnostics={})
    def absorb(self,cell,lower,h):
        self.absorb_calls+=1;k0=np.array([1.,2.,3.])*cell.N*1e-8
        heat=np.array([2.,3.,4.])*k0
        return dict(N=cell.N,U=cell.U,K0=k0,KE=v4.CHI*k0+heat,photoheat_direct=heat,number_absorbed_species=np.zeros(3))


class Native:
    def __init__(self):self.calls=0;self.inputs=[]
    def rhs(self,t,g,gas,cells):
        self.calls+=1;self.inputs.append((gas.copy(),cells.copy()))
        out=np.zeros(15+2*len(cells));out[0]=1e-4
        for row in cells:out[8:11]+=row[7:10]/g['a_rel']**3
        out[11]=v4.gas_temperature(gas,g)
        return out


class OutputBindingTests(unittest.TestCase):
    def test_transparent_map_final_evaluation_ownership(self):
        source,state,api=fixture();a0,a1=Absorption(),Absorption();n0,n1=Native(),Native()
        old=v4._v3.positive_native_step(copy.deepcopy(state),1.,source,None,n0,source_api=api,absorption_api=a0)
        new=v4.positive_native_step(copy.deepcopy(state),1.,source,None,n1,source_api=api,absorption_api=a1)
        self.assertEqual(n0.calls,n1.calls);self.assertGreater(n1.calls,1)
        self.assertEqual(a0.absorb_calls,a1.absorb_calls)
        for key in ('gas','N','U_eV','R','support'):np.testing.assert_array_equal(old[key],new[key])
        self.assertEqual(old['counters'],new['counters'])
        self.assertEqual(old['diagnostics'],{k:v for k,v in new['diagnostics'].items() if k!='output24_kernel'})
        for left,right in zip(n0.inputs,n1.inputs):
            for x,y in zip(left,right):np.testing.assert_array_equal(x,y)
        kernel=new['diagnostics']['output24_kernel'];self.assertEqual(kernel['native_rhs_evaluations'],n1.calls)
        self.assertEqual(kernel['state_sha256'],fields.physical_state_sha256(new))
        np.testing.assert_array_equal(kernel['gas'],new['gas'])
        row=fields.build_fields24(new,source,source_api=api)
        self.assertEqual(list(row),fields.FIELDS24)
        self.assertEqual(row['GammaHI_s'],new['diagnostics']['gamma'][0])
        with self.assertRaisesRegex(ValueError,'STATE_KERNEL_IDENTITY'):
            altered=copy.deepcopy(new);altered['N'][0,0]+=1.;fields.build_fields24(altered,source,source_api=api)

    def test_initial_h0_units_and_no_physical_state_changes(self):
        source,state,api=fixture();absorption=Absorption()
        new=v4.initial_output_state(state,source,None,absorption_api=absorption)
        self.assertNotIn('diagnostics',state)
        self.assertEqual(fields.physical_state_sha256(new),fields.physical_state_sha256(state))
        self.assertEqual(absorption.prepare_calls,2);self.assertEqual(absorption.absorb_calls,2)
        row=fields.build_fields24(new,source,source_api=api)
        self.assertEqual(row['source_number_ref_cm3_s'],9.)
        self.assertEqual(row['source_number_proper_cm3_s'],9./8.)
        self.assertEqual(row['source_energy_ref_erg_cm3_s'],180.*v4.EV_ERG)
        self.assertEqual(row['radiation_energy_proper_erg_cm3'],100.*v4.EV_ERG/8.)
        self.assertEqual(row['photon_cm3'],5./8.)
        self.assertEqual(row['ne_cm3'],2.*.2+.2*(.1+2.*.05))
        for i,label in enumerate(('HI','HeI','HeII')):
            direct=math.fsum(np.asarray(new['diagnostics']['output24_kernel']['photoheat_direct_eV_per_ref_s'])[:,i])*v4.EV_ERG/8.
            self.assertLess(abs(row[f'photoheat_{label}_per_absorber_erg_s']/direct-1),1e-14)
        self.assertEqual(set(fields.UNITS),set(fields.FIELDS24))
        record=fields.build_record(new,source,source_api=api,epoch_index=0,generation='child-gen0',state_sha256=fields.physical_state_sha256(new),ledger={'energy_scaled':0.,'number_scaled':0.})
        self.assertEqual(record['geometry']['max_error'],0.)
        self.assertEqual(record['kernel_owner'],'ORIGINAL_SAVED_C2_H0_OUTPUT_ONLY')

    def test_native_volume_multiplication_roundoff_is_not_reprojection(self):
        source,state,api=fixture();g=source.provider.geometry(0.);g['a_rel']=1.001
        volume=g['a_rel']*g['a_rel']*g['a_rel'];self.assertNotEqual(volume,g['a_rel']**3)
        cells=np.zeros((2,13));cells[:,7:10]=np.array([[1.,2.,3.],[4.,5.,6.]])*1e-8
        direct=cells[:,7:10]*4.;cells[:,10:13]=cells[:,7:10]*v4.CHI+direct
        gamma=np.zeros(3);heat=np.zeros(3)
        for row in cells:
            gamma+=row[7:10]/volume
            heat+=(row[10:13]-v4.CHI*row[7:10])*v4.EV_ERG/volume
        kernel=v4._capture_kernel(state,g,cells,direct,gamma,owner='MANUFACTURED_NATIVE_ORDER',native_evaluations=1)
        np.testing.assert_array_equal(kernel['gamma_s'],gamma)
        np.testing.assert_array_equal(kernel['photoheat_per_absorber_erg_s'],heat)

    def test_no_evolved_reprojection_or_missing_direct_heat(self):
        source,state,api=fixture();state['t_s']=1.
        with self.assertRaisesRegex(ValueError,'INITIAL_ONLY'):
            v4.initial_output_state(state,source,None,absorption_api=Absorption())
        with self.assertRaisesRegex(ValueError,'MISSING_SAME_MAP_KERNEL'):
            fields.build_fields24(state,source,source_api=api)
        source,state,api=fixture();broken=Absorption();original=broken.absorb
        def bad(*args):
            out=original(*args);out['photoheat_direct']=np.ones(3);return out
        broken.absorb=bad
        with self.assertRaisesRegex(ArithmeticError,'HEAT_ABI_DIRECT'):
            v4.initial_output_state(state,source,None,absorption_api=broken)

if __name__=='__main__':unittest.main(verbosity=2)
