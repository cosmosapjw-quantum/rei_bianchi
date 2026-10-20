//! New integration checks only; no integration of any gas/transport history.
pub use rei_iso_couple_reference::{HHeModel, deuterium_atomic, full_network, igm_rates, isotope_state};
use rei_iso_couple_reference::{
    deuterium_atomic::{DAtomicProvider,DAtomicError,DChargeExchange,d_atomic_rhs,d_atomic_rhs_from_prepared},
    full_network::{FullState,NetworkConfig,NetworkError,PhotonBin},
    gas_reference_rhs::{gas_rates,gas_rates_with_backend,gas_rates_batch_into,GasRateWorkspace,GasRates},
    isotope_state::{IsotopeNumberState,IsotopeSpecies as S},
    mixture_eos::{MixtureState,KB_J_K},
    rate_table::{IgmRateBackend,IgmRateTable},
};
use std::sync::Arc;
// Byte-exact original RUN13 gas assembly, compiled in this same executable.
// Its direct D wrapper shares the unchanged D event/energy implementation.
#[path="../../../run13/recovered/code/rei_bass_coupled/src/gas_reference_rhs.rs"]
mod original_gas;

fn fixture(t:f64, variant:usize)->(FullState,NetworkConfig){
    let mut n=[0.0;13];
    for (s,v) in [(S::H1Neutral,180.0),(S::H1Ionized,20.0),(S::DNeutral,0.0045),
        (S::DIonized,0.0005),(S::He4Neutral,12.0),(S::He4SinglyIonized,3.0),(S::He4DoublyIonized,1.0)]{
        n[s as usize]=v;
    }
    // Same total particles and electrons, but a different density-dependent RHS.
    n[S::H1Neutral as usize]-=variant as f64;
    n[S::He4Neutral as usize]+=variant as f64;
    let nuclei=IsotopeNumberState::new(n).unwrap();
    let u=1.5*KB_J_K*nuclei.thermal_particle_density_all_thermal_m3().unwrap()*t;
    let h=HHeModel::controlled_fixture().threshold_ev[0];
    let mut c=NetworkConfig::source_bound(DAtomicProvider::new(h,h+0.0037,"RUN19_TEST_THRESHOLD").unwrap(),"RUN19_TEST_SOURCE");
    c.use_photo=false;c.cmb_temperature_k=29.0;
    (FullState{gas:MixtureState{nuclei,thermal_j_m3:u},photon_bins:Vec::new(),escaped_j_m3:0.0,cmb_reservoir_j_m3:0.0,elapsed_s:0.0},c)
}
fn bits(q:GasRates)->[u64;28]{
    let mut out=[0;28];out[..27].copy_from_slice(&q.vector().map(f64::to_bits));out[27]=q.chemical.to_bits();out
}
#[test]
fn direct_shared_bundle_preserves_original_all_channels_and_masks(){
    let ts=[3.0,100.0,5500.0_f64.next_down(),5500.0,5500.0_f64.next_up(),
        9284.0_f64.next_down(),9284.0,9284.0_f64.next_up(),10000.0,50000.0,190000.0];
    for t in ts {for variant in [0,1,4] {let(s,c)=fixture(t,variant);for mask in 0..8 {
        let old=original_gas::gas_rates(&s,&c,mask).unwrap();
        let new=gas_rates(&s,&c,mask).unwrap();
        assert_eq!(old.vector().map(f64::to_bits),new.vector().map(f64::to_bits),"T={t},variant={variant},mask={mask}");
        assert_eq!(old.chemical.to_bits(),new.chemical.to_bits());
        let scale=new.heat.abs()+new.chemical.abs()+new.escape.abs()+new.cmb.abs();
        assert!(new.residual().abs()<=2e-14*scale.max(f64::MIN_POSITIVE));
    }}}
}
#[test]
fn prepared_d_preserves_direct_event_and_thermal_ledger(){
    let backend=IgmRateBackend::Direct;
    for t in [3.0,100.0,9284.0,10000.0,50000.0,190000.0]{
        let(s,c)=fixture(t,0);let p=backend.prepare(t).unwrap();
        let photo=c.deuterium.photo_input_from_bound_rates(3e-14,1e-33,"BOUND_TEST").unwrap();
        for cx in [DChargeExchange::Disabled,DChargeExchange::Savin2002]{
            let a=d_atomic_rhs(c.deuterium,&s.gas.nuclei,t,&photo,cx).unwrap();
            let b=d_atomic_rhs_from_prepared(c.deuterium,&s.gas.nuclei,t,&photo,cx,&p,&backend).unwrap();
            assert_eq!(a,b);
        }
    }
}
#[test]
fn prepared_temperature_evaluator_and_photo_threshold_fail_closed(){
    let(s,c)=fixture(1e4,0);let direct=IgmRateBackend::Direct;
    let table=IgmRateBackend::Table(Arc::new(IgmRateTable::new(257).unwrap()));
    let p=direct.prepare(1e4).unwrap();
    let photo=c.deuterium.photo_input_from_bound_rates(0.0,0.0,"TEST").unwrap();
    let call=|t,ph:&deuterium_atomic::DPhotoInput,b:&IgmRateBackend|
        d_atomic_rhs_from_prepared(c.deuterium,&s.gas.nuclei,t,ph,DChargeExchange::Disabled,&p,b);
    assert_eq!(call(10000.0_f64.next_up(),&photo,&direct),Err(DAtomicError::PreparedTemperatureMismatch));
    assert_eq!(call(1e4,&photo,&table),Err(DAtomicError::PreparedEvaluatorMismatch));
    assert_eq!(call(f64::NAN,&photo,&direct),Err(DAtomicError::NonFiniteInput));
    let other=DAtomicProvider::new(c.deuterium.chi_h_ev(),c.deuterium.chi_d_ev()+0.001,"OTHER").unwrap();
    let wrong=other.photo_input_from_bound_rates(0.0,0.0,"TEST").unwrap();
    assert_eq!(call(1e4,&wrong,&direct),Err(DAtomicError::PhotoThresholdMismatch));
}
#[test]
fn exact_temperature_workspace_never_caches_density_dependent_powers(){
    let backend=IgmRateBackend::Direct;let mut ws=GasRateWorkspace::new(&backend);
    let(s,c)=fixture(1e4,0);let(s2,_)=fixture(1e4,4);
    assert_eq!(s.gas.eos().unwrap().temperature_k.to_bits(),s2.gas.eos().unwrap().temperature_k.to_bits());
    let first=ws.evaluate(&s,&c,7).unwrap();let second=ws.evaluate(&s2,&c,7).unwrap();
    assert_eq!(bits(first),bits(gas_rates(&s,&c,7).unwrap()));
    assert_eq!(bits(second),bits(gas_rates(&s2,&c,7).unwrap()));
    assert_ne!(bits(first),bits(second));
    assert_eq!(ws.stats.preparations,1);assert_eq!(ws.stats.exact_temperature_hits,1);
    let(mut s3,_)=fixture(1e4,0);s3.gas.thermal_j_m3=s3.gas.thermal_j_m3.next_up();
    assert_ne!(s3.gas.eos().unwrap().temperature_k.to_bits(),s.gas.eos().unwrap().temperature_k.to_bits());
    ws.evaluate(&s3,&c,7).unwrap();assert_eq!(ws.stats.preparations,2);
}
#[test]
fn typed_batch_workers_match_scalar_for_direct_and_optin_table(){
    let(_,c)=fixture(1e4,0);
    let states:Vec<_>=(0..97).map(|i|fixture(if i<48{1e4}else{2e4},i%5).0).collect();
    let backends=[IgmRateBackend::Direct,IgmRateBackend::Table(Arc::new(IgmRateTable::new(1025).unwrap()))];
    for backend in backends {for workers in [1,2,4] {for mask in [0,1,2,4,7]{
        let mut out=vec![GasRates::default();states.len()];
        let stats=gas_rates_batch_into(&states,&c,mask,&backend,&mut out,workers).unwrap();
        assert_eq!(stats.evaluations,states.len());
        for(s,q)in states.iter().zip(out){assert_eq!(bits(q),bits(gas_rates_with_backend(s,&c,mask,&backend).unwrap()));}
        if mask&3==0{assert_eq!(stats.preparations,0);}
        else{assert_eq!(stats.preparations+stats.exact_temperature_hits,states.len());}
    }}}
}
#[test]
fn input_errors_and_mask2_contract_match_original(){
    let(s,c)=fixture(1e4,0);
    for mask in [0,2,7,8] {for case in 0..5{
        let mut ss=s.clone();let mut cc=c;
        match case{0=>{},1=>ss.gas.thermal_j_m3*=100.0,2=>cc.use_photo=true,
            3=>ss.photon_bins.push(PhotonBin{energy_ev:20.0,number_m3:0.0}),4=>cc.cmb_temperature_k=0.0,_=>unreachable!()}
        assert_eq!(original_gas::gas_rates(&ss,&cc,mask).err(),gas_rates(&ss,&cc,mask).err());
    }}
    let mut output=[GasRates::default();1];
    assert_eq!(gas_rates_batch_into(&[],&c,7,&IgmRateBackend::Direct,&mut output,1),Err(NetworkError::InvalidInput));
    assert_eq!(gas_rates_batch_into(&[],&c,7,&IgmRateBackend::Direct,&mut [],0),Err(NetworkError::InvalidInput));
}
