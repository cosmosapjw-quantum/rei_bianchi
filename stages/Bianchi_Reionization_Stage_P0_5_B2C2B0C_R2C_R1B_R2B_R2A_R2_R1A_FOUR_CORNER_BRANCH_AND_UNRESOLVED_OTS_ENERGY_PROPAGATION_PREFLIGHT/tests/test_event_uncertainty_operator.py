from __future__ import annotations
import importlib.util,sys,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent
REPO=STAGE.parents[1]
MICRO=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2_OWNER_CORRECT_PHOTON_CONSERVING_NONAUTONOMOUS_FIXED_POINT_HISTORY_RERUN/analysis/microphysics.py'
WITNESS=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1_SOURCE_BRANCH_KERNEL_AND_OTS_ENERGY_MOMENT_LOCK/data/TWO_PHOTON_ENERGY_MOMENT_WITNESS.json'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def sample():
    nh=np.array([1.0e58,2.0e58,4.0e58])
    nhe=0.08*nh
    pop=np.column_stack([
        nh*np.array([0.8,0.5,0.2]), nh*np.array([0.2,0.5,0.8]),
        nhe*np.array([0.7,0.4,0.2]), nhe*np.array([0.25,0.45,0.5]), nhe*np.array([0.05,0.15,0.3]),
    ])
    temp=np.array([8.0e3,2.0e4,6.0e4])
    volume=np.array([1.0e70,1.5e70,2.0e70])
    photo=np.array([[1e46,3e45,2e44],[2e46,4e45,3e44],[3e46,5e45,4e44]])
    return pop,temp,volume,photo

def test_event_operator_matches_legacy_source_rhs_when_given_legacy_branches():
    op=load('event_uncertainty_operator',STAGE/'analysis/event_uncertainty_operator.py')
    micro=load('event_uncertainty_micro_oracle',MICRO)
    pop,temp,volume,photo=sample()
    nh=pop[:,0]+pop[:,1]; nhe=np.sum(pop[:,2:5],axis=1)
    xh=pop[:,1]/nh; he=pop[:,2:5]/nhe[:,None]
    q=np.column_stack([np.log(xh)-np.log1p(-xh),np.log(he[:,1])-np.log(he[:,0]),np.log(he[:,2])-np.log(he[:,0]),np.log(temp)])
    v=1.0/(1.0+np.exp(-(temp-2.0e4)/4.0e3))
    f=1.0-np.exp(-100.0*pop[:,0]/nh)
    result=op.evaluate_event_flux(populations=pop,temperature_K=temp,proper_volume_cm3=volume,
        photo_hi=photo[:,0],photo_hei=photo[:,1],photo_heii=photo[:,2],v=v,f=f,
        energy_policy='ENERGY_LOWER',witness_path=WITNESS)
    expected=np.asarray(micro._batch_rhs(micro.jnp.asarray(q),micro.jnp.asarray(nh),micro.jnp.asarray(nhe),
        micro.jnp.asarray(volume),micro.jnp.asarray(photo[:,0]),micro.jnp.asarray(photo[:,1]),micro.jnp.asarray(photo[:,2])))
    scale=np.maximum(np.max(np.abs(expected),axis=1),1.0)
    assert np.max(np.max(np.abs(result.population_rhs-expected),axis=1)/scale)<3e-13
    assert result.pds_reconstruction_residual<3e-13

def test_event_flux_is_nonnegative_conservative_and_has_no_direct_hei_to_heiii():
    op=load('event_uncertainty_operator2',STAGE/'analysis/event_uncertainty_operator.py')
    pop,temp,volume,photo=sample()
    result=op.evaluate_event_flux(populations=pop,temperature_K=temp,proper_volume_cm3=volume,
        photo_hi=photo[:,0],photo_hei=photo[:,1],photo_heii=photo[:,2],
        v=np.array([0.0,0.33,1.0]),f=np.array([0.1,1.0,0.1]),energy_policy='ENERGY_UPPER',witness_path=WITNESS)
    assert np.min(result.pds_flux)>=0.0
    assert np.all(result.pds_flux[:,4,2]==0.0)
    assert np.max(np.abs(np.sum(result.population_rhs[:,:2],axis=1)))<1e-12*np.max(np.abs(result.population_rhs))+1e-280
    assert np.max(np.abs(np.sum(result.population_rhs[:,2:5],axis=1)))<1e-12*np.max(np.abs(result.population_rhs))+1e-280
    assert result.branch_domain_failure_count==0

def test_augmented_ots_binding_energy_identity_closes_for_both_joint_witnesses():
    op=load('event_uncertainty_operator3',STAGE/'analysis/event_uncertainty_operator.py')
    pop,temp,volume,photo=sample()
    for policy in ('ENERGY_LOWER','ENERGY_UPPER'):
        result=op.evaluate_event_flux(populations=pop,temperature_K=temp,proper_volume_cm3=volume,
            photo_hi=photo[:,0],photo_hei=photo[:,1],photo_heii=photo[:,2],
            v=np.array([0.0,0.5,1.0]),f=np.array([0.1,1.0,0.4]),energy_policy=policy,witness_path=WITNESS)
        assert np.all(result.resolved_ots_heating_erg_s>=0.0)
        assert np.all(result.unresolved_ots_energy_erg_s>=0.0)
        assert np.all(result.escaped_ots_energy_erg_s>=0.0)
        scale=np.maximum.reduce([
            np.abs(result.chemical_ots_energy_rate_erg_s),result.resolved_ots_heating_erg_s,
            result.unresolved_ots_energy_erg_s,result.escaped_ots_energy_erg_s,np.ones(3)])
        residual=(result.chemical_ots_energy_rate_erg_s+result.resolved_ots_heating_erg_s+
                  result.unresolved_ots_energy_erg_s+result.escaped_ots_energy_erg_s)
        assert np.max(np.abs(residual)/scale)<3e-13
        assert result.max_augmented_energy_residual<3e-13

def test_photon_branch_identity_is_exact_to_roundoff():
    op=load('event_uncertainty_operator4',STAGE/'analysis/event_uncertainty_operator.py')
    pop,temp,volume,photo=sample()
    result=op.evaluate_event_flux(populations=pop,temperature_K=temp,proper_volume_cm3=volume,
        photo_hi=photo[:,0],photo_hei=photo[:,1],photo_heii=photo[:,2],
        v=np.array([0.0,0.5,1.0]),f=np.array([0.1,1.0,0.4]),energy_policy='ENERGY_LOWER',witness_path=WITNESS)
    assert result.max_photon_count_identity_residual<3e-15
