//! Unit B integration checks, independent of historical IVP/test suites.
use rei_iso_couple_reference::{
    HHeModel,cubic_igm::{CubicIgmTable,source_id,DEFAULT_NODES},
    deuterium_atomic::{DAtomicProvider,DAtomicError,DChargeExchange,d_atomic_rhs_from_prepared},
    full_network::{FullState,NetworkConfig},
    gas_reference_rhs::{gas_rates_with_backend,gas_rates_batch_into,GasRates},
    igm_rates::igm_rates,isotope_state::{IsotopeNumberState,IsotopeSpecies as S},
    mixture_eos::{MixtureState,KB_J_K},rate_table::{IgmRateBackend,igm_flat,igm_branch_knots,IGM_CUBIC_EVALUATOR},
};
use std::{sync::Arc,path::PathBuf};
fn fixture(t:f64)->(FullState,NetworkConfig){
    let n=[0.0,180.0,20.0,0.0045,0.0005,0.0,0.0,0.0,0.0,0.0,12.0,3.0,1.0];
    let nuclei=IsotopeNumberState::new(n).unwrap();
    let u=1.5*KB_J_K*nuclei.thermal_particle_density_all_thermal_m3().unwrap()*t;
    let h=HHeModel::controlled_fixture().threshold_ev[0];
    let mut c=NetworkConfig::source_bound(DAtomicProvider::new(h,h+0.0037,"RUN19_TEST_THRESHOLD").unwrap(),"RUN19_TEST_SOURCE");
    c.use_photo=false;c.cmb_temperature_k=29.0;
    (FullState{gas:MixtureState{nuclei,thermal_j_m3:u},photon_bins:Vec::new(),escaped_j_m3:0.0,cmb_reservoir_j_m3:0.0,elapsed_s:0.0},c)
}
fn bits(q:GasRates)->[u64;28]{let mut a=[0;28];a[..27].copy_from_slice(&q.vector().map(f64::to_bits));a[27]=q.chemical.to_bits();a}
struct Temp(PathBuf);
impl Temp{fn new()->Self{let p=std::env::temp_dir().join(format!("rei_unit_b_{}_{}",std::process::id(),std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));std::fs::create_dir(&p).unwrap();Self(p)}}
impl Drop for Temp{fn drop(&mut self){std::fs::remove_dir_all(&self.0).unwrap();}}

#[test]
fn cubic_prepared_hhe_d_uses_one_bound_bundle_and_same_ledgers(){
    let backend=IgmRateBackend::Cubic(Arc::new(CubicIgmTable::build_default().unwrap()));
    assert_eq!(backend.evaluator_id(),IGM_CUBIC_EVALUATOR);
    for t in [100.0,9284.0,10000.0,13817.0,100000.0]{
        let(s,c)=fixture(t);let eos=s.gas.eos().unwrap();let p=backend.prepare(eos.temperature_k).unwrap();
        let photo=c.deuterium.photo_input_from_bound_rates(0.0,0.0,c.photon_source).unwrap();
        let d=d_atomic_rhs_from_prepared(c.deuterium,&s.gas.nuclei,eos.temperature_k,&photo,DChargeExchange::Savin2002,&p,&backend).unwrap();
        let q=gas_rates_with_backend(&s,&c,7,&backend).unwrap();
        assert_eq!(q.ci[3].to_bits(),d.ci_events_m3_s.to_bits());assert_eq!(q.rr[3].to_bits(),d.rr_events_m3_s.to_bits());
        assert_eq!(q.ci[0].to_bits(),(eos.free_electrons_m3*1e-6*s.gas.nuclei.density_m3(S::H1Neutral)*p.rates().ci_cm3_s[0]).to_bits());
        let scale=q.heat.abs()+q.chemical.abs()+q.escape.abs()+q.cmb.abs();
        assert!(q.residual().abs()<=3e-14*scale);
        assert_eq!(d_atomic_rhs_from_prepared(c.deuterium,&s.gas.nuclei,eos.temperature_k,&photo,DChargeExchange::Disabled,&p,&IgmRateBackend::Direct),Err(DAtomicError::PreparedEvaluatorMismatch));
    }
}

#[test]
fn cubic_retains_direct_boundary_floor_diagnostics_and_domain(){
    let table=CubicIgmTable::build_default().unwrap();
    for t in igm_branch_knots().into_iter().flat_map(|x|[x.next_down(),x,x.next_up()]).chain([1.0,1e6]){
        let direct=igm_rates(t).unwrap();let actual=table.rates(t).unwrap();
        assert_eq!(igm_flat(direct).map(f64::to_bits),igm_flat(actual).map(f64::to_bits),"T={t}");
        assert_eq!(direct.diagnostics.ci_floor_cm3_s.map(f64::to_bits),actual.diagnostics.ci_floor_cm3_s.map(f64::to_bits));
        assert_eq!(direct.diagnostics.ce_cap_erg.map(f64::to_bits),actual.diagnostics.ce_cap_erg.map(f64::to_bits));
        assert_eq!(direct.diagnostics.dr_low_branch,actual.diagnostics.dr_low_branch);
    }
    for t in [2.0,300.0,9000.0,10000.0,900000.0]{
        let direct=igm_rates(t).unwrap();let actual=table.rates(t).unwrap();
        for j in 0..3{assert_eq!(direct.diagnostics.ci_floor_cm3_s[j]!=0.0,actual.diagnostics.ci_floor_cm3_s[j]!=0.0);
            if direct.diagnostics.ci_floor_cm3_s[j]!=0.0{assert_eq!(actual.ci_cm3_s[j].to_bits(),1e-20_f64.to_bits());}
            assert_eq!(direct.diagnostics.ce_cap_erg[j]!=0.0,actual.diagnostics.ce_cap_erg[j]!=0.0);}
        assert_eq!(actual.diagnostics.dr_low_branch,direct.diagnostics.dr_low_branch);
        if actual.diagnostics.dr_low_branch{assert_eq!(actual.dr_cooling_erg_cm3_s,0.0);assert_eq!(actual.diagnostics.dr_excluded_erg_cm3_s.to_bits(),actual.dr_raw_cooling_erg_cm3_s.to_bits());}
    }
    for t in [0.0,0.5,1e6_f64.next_up(),f64::NAN,f64::INFINITY]{assert_eq!(table.rates(t).err(),igm_rates(t).err());}
}

#[test]
fn exact_source_cache_roundtrip_and_wrong_identity_or_size_are_rejected(){
    let dir=Temp::new();let file=dir.0.join("good.bin");let table=CubicIgmTable::build_default().unwrap();
    assert_eq!(table.grid().source_id(),source_id());assert_eq!(table.grid().nodes(),DEFAULT_NODES);
    table.save_new(&file).unwrap();assert!(table.save_new(&file).is_err());
    let loaded=CubicIgmTable::load_default(&file).unwrap();
    for t in [3.0,9284.0,10001.5,50000.0,1e6]{assert_eq!(igm_flat(table.rates(t).unwrap()).map(f64::to_bits),igm_flat(loaded.rates(t).unwrap()).map(f64::to_bits));}
    let mut bytes=std::fs::read(&file).unwrap();bytes[24]^=1;let len=bytes.len();
    let digest=rei_rate_cubic::source_digest(&bytes[..len-32]);bytes[len-32..].copy_from_slice(&digest);
    let wrong=dir.0.join("wrong_source.bin");std::fs::write(&wrong,bytes).unwrap();
    assert!(matches!(CubicIgmTable::load_default(&wrong),Err(rei_rate_cubic::Error::Invalid("CUBIC_CACHE_IDENTITY"))));
    let small=dir.0.join("wrong_nodes.bin");CubicIgmTable::new(257).unwrap().save_new(&small).unwrap();
    assert!(matches!(CubicIgmTable::load_default(&small),Err(rei_rate_cubic::Error::Invalid("IGM_CUBIC_CACHE_DOMAIN_OR_NODES"))));
}

#[test]
fn cubic_typed_batch_preserves_scalar_bits_all_masks_workers(){
    let backend=IgmRateBackend::Cubic(Arc::new(CubicIgmTable::build_default().unwrap()));
    let(s,c)=fixture(10000.0);let mut states=vec![s;97];
    for(i,s)in states.iter_mut().enumerate().skip(48){*s=fixture(9500.0+i as f64*19.0).0;}
    for mask in [0,1,2,4,7]{for workers in [1,2,4]{
        let mut output=vec![GasRates::default();states.len()];
        let stats=gas_rates_batch_into(&states,&c,mask,&backend,&mut output,workers).unwrap();
        assert_eq!(stats.evaluations,states.len());
        for(s,q)in states.iter().zip(output){assert_eq!(bits(q),bits(gas_rates_with_backend(s,&c,mask,&backend).unwrap()));}
    }}
}
