use axbi_temperature_rate_integration::{candidate_driver::{Driver,DriverConfig,DriverState},provider::Provider};
use rei_microphysics::{axbi_driver as canonical,igm_state::IgmGasState,igm_thermal::IgmPhotoInput};
use std::path::Path;
use axbi_temperature_rate_table_benchmark::validation::{compare_rate_bundle,compare_rhs_pair,mixed_fixture};
fn config(q:f64)->DriverConfig{
    let mut c=DriverConfig::baseline();c.q_ref=q;c.end_zbar=19.8;c.initial_temperature_k=8.098143045064857;c.max_wall_s=600.0;c
}
fn canonical_config(q:f64)->canonical::DriverConfig{
    let mut c=canonical::DriverConfig::baseline();c.q_ref=q;c.end_zbar=19.8;c.initial_temperature_k=8.098143045064857;c.max_wall_s=600.0;c
}
fn state_bytes(s:&DriverState)->Vec<u64>{
    let mut v=vec![s.a,s.gas.w_erg_per_h,s.next_dln_a,s.max_newton_residual,s.last_error];
    v.extend(s.gas.fractions);v.extend(&s.photons);
    let l=&s.ledgers;
    v.extend([l.source_n,l.source_u,l.absorbed_n,l.escaped_u,l.boundary_n,l.boundary_u,l.thermal_work,l.photon_work,l.cmb_input,l.dr_events,l.ce_cap_ev,l.excluded_dr_ev]);
    for a in [l.rr_events,l.ci_events,l.photo_events,l.ci_floor_events]{v.extend(a)}
    v.into_iter().map(f64::to_bits).collect()
}
fn canonical_bytes(s:&canonical::DriverState)->Vec<u64>{
    let mut v=vec![s.a,s.gas.w_erg_per_h,s.next_dln_a,s.max_newton_residual,s.last_error];
    v.extend(s.gas.fractions);v.extend(&s.photons);
    let l=&s.ledgers;
    v.extend([l.source_n,l.source_u,l.absorbed_n,l.escaped_u,l.boundary_n,l.boundary_u,l.thermal_work,l.photon_work,l.cmb_input,l.dr_events,l.ce_cap_ev,l.excluded_dr_ev]);
    for a in [l.rr_events,l.ci_events,l.photo_events,l.ci_floor_events]{v.extend(a)}
    v.into_iter().map(f64::to_bits).collect()
}
#[test]
fn direct_attempt_binary64_parity(){
    for q in [0.0,0.01]{
        let (d,mut s)=Driver::new(config(q)).unwrap();let (c,mut t)=canonical::Driver::new(canonical_config(q)).unwrap();
        assert_eq!(d.adaptive_step(&mut s).map_err(|e|format!("{e:?}")),c.adaptive_step(&mut t).map_err(|e|format!("{e:?}")));
        assert_eq!(state_bytes(&s),canonical_bytes(&t),"q={q}");
        assert_eq!((s.accepted,s.attempts,s.comparisons,s.rejects,s.rhs_evaluations),(t.accepted,t.attempts,t.comparisons,t.rejects,t.rhs_evaluations));
        println!("direct q={q} accepted={} attempts={} rhs={}",s.accepted,s.attempts,s.rhs_evaluations);
    }
}
#[test]
fn table_point_fixtures(){
    let table=Provider::load(Path::new("../temperature_rate_table_001/data/rates.bin")).unwrap();
    let direct=Provider::direct();
    let mut valid=0u64;
    for t in [8.098143045064857,5500.0,9300.0,20000.0,9284.0]{
        for mixed in [false,true]{
            let (gas,nh,nhe,h,photo)=if mixed{
                mixed_fixture(t).unwrap()
            }else{
                (IgmGasState::from_temperature([2e-4,0.0,0.0],1e-3,8e-5,t).unwrap(),
                    1e-3,8e-5,0.0,IgmPhotoInput::default())
            };
            let a=direct.point(&gas,nh,nhe,h,57.2355,photo).unwrap();
            let b=table.point(&gas,nh,nhe,h,57.2355,photo).unwrap();
            assert_eq!(a.temperature_k.to_bits(),b.temperature_k.to_bits(),"T={t} mixed={mixed}");
            compare_rate_bundle(&a.rates,&b.rates,t).unwrap_or_else(|e|panic!("T={t} mixed={mixed} {e}"));
            compare_rhs_pair(&a.rhs,&b.rhs,&gas,nh,nhe,t,photo).unwrap_or_else(|e|panic!("T={t} mixed={mixed} {e}"));
            for rates in [&a.rates,&b.rates]{
                let d=&rates.diagnostics;
                assert_eq!(d.dr_low_branch,rates.dr_cooling_erg_cm3_s==0.0,"T={t}");
                if d.dr_low_branch{
                    assert_eq!(rates.dr_cooling_erg_cm3_s.to_bits(),0);
                    assert_eq!(d.dr_excluded_erg_cm3_s.to_bits(),rates.dr_raw_cooling_erg_cm3_s.to_bits());
                }else{
                    assert_eq!(d.dr_excluded_erg_cm3_s.to_bits(),0);
                    assert_eq!(rates.dr_cooling_erg_cm3_s.to_bits(),rates.dr_raw_cooling_erg_cm3_s.to_bits());
                }
                for k in 0..3{
                    if d.ci_floor_cm3_s[k]!=0.0{assert_eq!(d.ci_floor_cm3_s[k].to_bits(),rates.ci_cm3_s[k].to_bits())}
                    else {assert_eq!(d.ci_floor_cm3_s[k].to_bits(),0)}
                    if d.ce_cap_erg[k]!=0.0{assert_eq!(d.ce_cap_erg[k].to_bits(),rates.ce_erg[k].to_bits())}
                    else {assert_eq!(d.ce_cap_erg[k].to_bits(),0)}
                }
            }
            valid+=1;
        }
    }
    assert_eq!(valid,10);
    let (base,nh,nhe,h,photo)=mixed_fixture(10000.0).unwrap();
    let mut cases:Vec<(&str,IgmGasState,f64,f64,f64,IgmPhotoInput)>=Vec::new();
    let mut p=photo;p.gamma_s[0]=-1e-14;cases.push(("negative_gamma",base,nh,h,2.7255,p));
    let mut p=photo;p.gamma_s[0]=f64::NAN;cases.push(("nan_gamma",base,nh,h,2.7255,p));
    let mut p=photo;p.heat_erg_per_absorber_s[0]=-1e-26;cases.push(("negative_heat",base,nh,h,2.7255,p));
    let mut p=photo;p.heat_erg_per_absorber_s[0]=f64::NAN;cases.push(("nan_heat",base,nh,h,2.7255,p));
    let mut p=photo;p.gamma_s[0]=0.0;cases.push(("heat_without_gamma",base,nh,h,2.7255,p));
    cases.push(("negative_h",base,nh,-1e-17,2.7255,photo));
    cases.push(("nan_h",base,nh,f64::NAN,2.7255,photo));
    cases.push(("zero_tcmb",base,nh,h,0.0,photo));
    cases.push(("nan_tcmb",base,nh,h,f64::NAN,photo));
    cases.push(("zero_nh",base,0.0,h,2.7255,photo));
    let mut bad=base;bad.fractions[0]=1.01;cases.push(("forged_h_fraction",bad,nh,h,2.7255,photo));
    let mut bad=base;bad.w_erg_per_h=-base.w_erg_per_h;cases.push(("negative_thermal_energy",bad,nh,h,2.7255,photo));
    cases.push(("negative_h_and_zero_tcmb",base,nh,-1e-17,0.0,photo));
    assert_eq!(cases.len(),13);
    for (id,gas,case_nh,case_h,tcmb,p) in cases{
        let a=direct.point(&gas,case_nh,nhe,case_h,tcmb,p);
        let b=table.point(&gas,case_nh,nhe,case_h,tcmb,p);
        assert!(a.is_err()&&b.is_err(),"{id}: {a:?} {b:?}");
        assert_eq!(format!("{:?}",a.unwrap_err()),format!("{:?}",b.unwrap_err()),"{id}");
        println!("invalid_rhs {id} matched");
    }
    for t in [0.0,0.5,1_000_001.0,f64::NAN,f64::INFINITY]{
        let a=direct.rates(t);let b=table.rates(t);
        assert!(a.is_err()&&b.is_err(),"invalid T={t:?}");
        assert_eq!(format!("{:?}",a.unwrap_err()),format!("{:?}",b.unwrap_err()),"invalid T={t:?}");
    }
    println!("validator_repair valid_points={valid} invalid_rhs=13 invalid_rates=5 table_counts={:?} direct_counts={:?}",table.counts(),direct.counts());
}

fn rhs_bits(x:&rei_microphysics::igm_thermal::IgmPointRhs)->Vec<u64>{
    let mut v=Vec::new();
    v.extend(x.fraction_dt);
    v.extend(x.species_chemical_cm3_s);
    v.extend([x.w_dt_erg_per_h_s,x.temperature_dt_k_s]);
    for a in [x.photo_events_cm3_s,x.ci_events_cm3_s,x.rr_events_cm3_s,
        x.ci_thermal_sink_erg_cm3_s,x.rr_thermal_sink_erg_cm3_s,x.ce_thermal_sink_erg_cm3_s,
        x.ci_floor_events_cm3_s,x.ce_cap_cooling_erg_cm3_s]{v.extend(a)}
    v.extend([x.dr_events_cm3_s,x.dr_thermal_sink_erg_cm3_s,x.freefree_thermal_sink_erg_cm3_s,
        x.thermal_micro_erg_cm3_s,x.binding_micro_erg_cm3_s,x.escape_erg_cm3_s,
        x.cmb_to_gas_erg_cm3_s,x.photo_input_erg_cm3_s,x.expansion_work_erg_cm3_s,
        x.excluded_dr_cooling_erg_cm3_s]);
    assert_eq!(v.len(),45);
    v.into_iter().map(f64::to_bits).collect()
}
fn rate_bits(x:&rei_microphysics::igm_rates::IgmRates)->Vec<u64>{
    let mut v=axbi_temperature_rate_table_benchmark::columns(x).into_iter().map(f64::to_bits).collect::<Vec<_>>();
    v.push(x.dr_cooling_erg_cm3_s.to_bits());
    v.extend(x.diagnostics.ci_floor_cm3_s.map(f64::to_bits));
    v.extend(x.diagnostics.ce_cap_erg.map(f64::to_bits));
    v.push(x.diagnostics.dr_excluded_erg_cm3_s.to_bits());
    v.push(x.diagnostics.dr_low_branch as u64);
    v
}
#[test]
fn direct_point_all_fields_binary64_parity(){
    let provider=Provider::direct();
    for t in [8.098143045064857,5500.0,9300.0,20000.0,9284.0]{
        for mixed in [false,true]{
            let (gas,nh,nhe,h,photo)=if mixed{mixed_fixture(t).unwrap()}else{
                (IgmGasState::from_temperature([2e-4,0.0,0.0],1e-3,8e-5,t).unwrap(),1e-3,8e-5,0.0,IgmPhotoInput::default())};
            let a=rei_microphysics::axbi_rates::AxbiProvider.point(&gas,nh,nhe,h,57.2355,photo).unwrap();
            let b=provider.point(&gas,nh,nhe,h,57.2355,photo).unwrap();
            assert_eq!(a.provider_id,b.provider_id);
            assert_eq!(a.temperature_k.to_bits(),b.temperature_k.to_bits());
            assert_eq!(rhs_bits(&a.rhs),rhs_bits(&b.rhs),"T={t} mixed={mixed} RHS");
            assert_eq!(rate_bits(&a.rates),rate_bits(&b.rates),"T={t} mixed={mixed} rates");
        }
    }
    assert_eq!(provider.counts().0,20);
}
#[test]
fn failed_point_accounting(){
    let nh=1e-4;let nhe=0.08*nh;
    let cold=IgmGasState::from_temperature([0.5,0.25,0.25],nh,nhe,0.5).unwrap();
    for provider in [Provider::direct(),Provider::load(Path::new("../temperature_rate_table_001/data/rates.bin")).unwrap()]{
        let err=provider.point(&cold,nh,nhe,0.0,2.7255,IgmPhotoInput::default()).unwrap_err();
        assert_eq!(format!("{err:?}"),"InvalidInput(\"IGM_TEMPERATURE_DOMAIN\")");
        assert_eq!(provider.counts().0,1,"failed rate-domain attempt must be charged");
        let mut photo=IgmPhotoInput::default();photo.gamma_s[0]=-1e-14;
        let warm=IgmGasState::from_temperature([0.5,0.25,0.25],nh,nhe,10000.0).unwrap();
        assert!(provider.point(&warm,nh,nhe,0.0,2.7255,photo).is_err());
        assert_eq!(provider.counts().0,1,"pre-rate validation must not charge");
        println!("failed_point backend={:?} counts={:?}",provider.backend(),provider.counts());
    }
}
