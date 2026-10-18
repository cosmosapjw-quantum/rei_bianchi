//! New Rust port/coupling controls on synthetic isolated H/D states.
//! Cached Python/Decimal data are inputs; no previous solver/oracle is run.
use rei_microphysics::deuterium_thermal_charge_exchange::*;
use rei_microphysics::deuterium_thermal_coupling::*;
use rei_microphysics::deuterium_charge_exchange::{DhState,DhEnergyDefect};
use rei_microphysics::deuterium_atomic::{DAtomicProvider,DChargeExchange,d_atomic_rhs,DEnergyLedger};
use rei_microphysics::{IsotopeNumberState,IsotopeSpecies};
use std::cell::Cell;

fn initial(n:[f64;4],t:f64) -> ThermalCxState {
    let [h0,hp,d0,dp]=n;
    ThermalCxState {h0,hp,d0,dp,thermal_ev_cm3:1.5*KB_EV_K*(h0+hp+d0+dp+hp+dp)*t}
}
fn defect(value:f64) -> ThermalCxDefect<'static> {
    ThermalCxDefect {delta_chi_ev:value,source:"SYNTHETIC_SIGNED_DEFECT"}
}
fn check_invariants(before:ThermalCxState,answer:&ThermalCxResult,delta:f64) {
    let after=answer.state.unwrap();
    let [a,b,c,d]=before.densities();let [e,f,g,h]=after.densities();
    let mut maximum_ledger_scaled=0.0_f64;
    for (left,right) in [(a+b,e+f),(c+d,g+h),(b+d,f+h),(a+b+2.0*(c+d),e+f+2.0*(g+h))] {
        assert!((left-right).abs()<=128.0*f64::EPSILON*1.0_f64.max(left.abs()).max(right.abs()));
        maximum_ledger_scaled=maximum_ledger_scaled.max((left-right).abs()/1.0_f64.max(left.abs()).max(right.abs()));
    }
    let chemical=delta*answer.extent_cm3.unwrap();
    let energy_scale=1e-30_f64.max(before.thermal_ev_cm3.abs()).max(chemical.abs());
    assert!((after.thermal_ev_cm3+chemical-before.thermal_ev_cm3).abs()<=128.0*f64::EPSILON*energy_scale);
    assert_eq!(answer.thermal_delta_ev_cm3,answer.chemical_delta_ev_cm3.map(|x|-x));
    assert_eq!(answer.electron_delta_cm3,0.0);
    assert!(after.densities().iter().all(|x|x.is_finite()&&*x>=0.0));
    if let (Some(t),Some(ceiling))=(answer.temperature_k,answer.temperature_amplitude_ceiling_k) {
        let t0=before.thermal_ev_cm3/(1.5*KB_EV_K*(a+b+c+d+b+d));
        let amplitude=(t-t0).abs();
        assert!(amplitude<=ceiling+128.0*f64::EPSILON*1.0_f64.max(t0).max(amplitude).max(ceiling));
    }
    assert!(answer.trace.len()<=512);
    assert!(answer.maximum_accepted_local_error_ratio<=1.0);
    println!("THERMAL_CX_METRIC {{\"kind\":\"synthetic_ledger\",\"maximum_scaled_density_residual\":{maximum_ledger_scaled:.17e},\"scaled_energy_residual\":{:.17e}}}",
        (after.thermal_ev_cm3+chemical-before.thermal_ev_cm3).abs()/energy_scale);
}

#[test]
fn cached_manufactured_endpoints_signed_defects_and_partial_boundaries() {
    type Reference=(&'static str,[f64;4],f64,f64,f64,f64,f64,&'static str,f64);
    let references:&[Reference]=include!(concat!(env!("CARGO_MANIFEST_DIR"),
        "/../../research/flrw_thermal_cx_native_20261016/cached_manufactured.rs"));
    for &(id,n,t0,beta,tmin,tmax,time,expected_status,expected_xi) in references {
        let state=initial(n,t0);let input=state;
        let rates=|t:f64| {
            assert!(t>=tmin&&t<=tmax,"invalid provider call {id} {t}");
            Ok((0.2*t/t0,0.2*t/t0))
        };
        let provider=ThermalCxProvider {source:"CACHED_MANUFACTURED_EQUAL_RATES",
            minimum_k:tmin,maximum_k:tmax,rates:&rates};
        let delta=beta*state.thermal_ev_cm3;
        let answer=integrate(state,defect(delta),&provider,time,ThermalCxControls::default());
        assert_eq!(state,input);
        check_invariants(state,&answer,delta);
        if expected_status=="COMPLETE" {
            assert!(answer.full_interval_complete,"{id} {:?}",answer.status);
            let normalized=(answer.extent_cm3.unwrap()-expected_xi).abs()/n.into_iter().fold(0.0,f64::max);
            assert!(normalized<=5e-6,"{id}: {normalized}");
            println!("THERMAL_CX_METRIC {{\"kind\":\"cached_manufactured\",\"id\":\"{id}\",\"normalized_error\":{normalized:.17e},\"extent_cm3\":{:.17e},\"rhs\":{}}}",answer.extent_cm3.unwrap(),answer.counts.rhs_calls);
        } else {
            assert_eq!(answer.status,ThermalCxStatus::DomainBoundaryApproach,"{id}");
            assert!(!answer.full_interval_complete&&answer.t_reached_s<time);
            let boundary=answer.provider_boundary_if_approached.unwrap();
            let scale=n.into_iter().fold(0.0,f64::max);
            assert!((boundary.extent_cm3-expected_xi).abs()<=128.0*f64::EPSILON*1.0_f64.max(scale));
            assert!(answer.distance_to_boundary_cm3.unwrap()/scale<=answer.event_atol_normalized);
            println!("THERMAL_CX_METRIC {{\"kind\":\"boundary_approach\",\"id\":\"{id}\",\"status\":\"{}\",\"achieved_time_s\":{:.17e},\"requested_time_s\":{time:.17e},\"distance_cm3\":{:.17e},\"temperature_K\":{:.17e},\"certified_event_time\":false}}",
                answer.status.as_str(),answer.t_reached_s,answer.distance_to_boundary_cm3.unwrap(),answer.temperature_k.unwrap());
        }
    }
}

#[test]
fn both_euler_stage_guards_precede_invalid_provider_calls() {
    let calls=Cell::new(0);
    let rates=|_:f64| {calls.set(calls.get()+1);Ok((0.2,0.2))};
    let provider=ThermalCxProvider {source:"SYNTHETIC_GUARD",minimum_k:2.7,maximum_k:30.0,rates:&rates};
    let system=ThermalCxSystem::new(initial([1.0,3.0,2.0,1.0],10.0),defect(0.0),&provider).unwrap();
    assert_eq!(system.field(1.0),Err(ThermalCxError::StageOutside));
    assert_eq!(calls.get(),0);
    let mut first_calls=0;
    assert_eq!(heun_step(&system,0.0,1.0,&mut |_| {first_calls+=1;Ok(1.0)}),Err(ThermalCxError::StageOutside));
    assert_eq!(first_calls,1);
    let mut second_calls=0;
    // e=.5 is legal; v=1 is illegal although its convex endpoint=.5 is legal.
    assert_eq!(heun_step(&system,0.0,1.0,&mut |_| {second_calls+=1;Ok(0.5)}),Err(ThermalCxError::StageOutside));
    assert_eq!(second_calls,2);
    assert_eq!(calls.get(),0);
}

#[test]
fn validation_degeneracies_work_caps_and_charged_provider_failures() {
    let state=initial([1.0,3.0,2.0,1.0],10.0);
    let zero=|_:f64|Ok((0.0,0.0));
    let rates=|t:f64|Ok((0.2*t/10.0,0.2*t/10.0));
    let provider=ThermalCxProvider {source:"SYNTHETIC",minimum_k:2.7,maximum_k:30.0,rates:&rates};
    let no_rates=ThermalCxProvider {rates:&zero,..provider};
    let controls=ThermalCxControls::default();
    let dt0=integrate(state,defect(0.0),&provider,0.0,controls);
    assert_eq!(dt0.status,ThermalCxStatus::Complete);assert_eq!(dt0.counts.rhs_calls,0);
    assert_eq!(dt0.state,Some(state));
    let no_d=initial([1.0,3.0,0.0,0.0],10.0);
    assert_eq!(integrate(no_d,defect(0.0037),&provider,2.0,controls).status,ThermalCxStatus::CompleteEquilibrium);
    assert_eq!(integrate(state,defect(0.0),&no_rates,2.0,controls).state,Some(state));
    let empty=ThermalCxState {h0:0.0,hp:0.0,d0:0.0,dp:0.0,thermal_ev_cm3:0.0};
    let result=integrate(empty,defect(-1.0),&provider,2.0,controls);
    assert_eq!(result.status,ThermalCxStatus::CompleteEmpty);
    assert_eq!(result.temperature_k,None);assert_eq!(result.temperature_amplitude_ceiling_k,None);
    assert_eq!(result.counts.rhs_calls,0);
    let invalid_provider=ThermalCxProvider {source:"",..provider};
    assert_eq!(integrate(empty,defect(0.0),&invalid_provider,0.0,controls).status,ThermalCxStatus::InvalidInput);
    for bad in [ThermalCxState {h0:-1.0,..state},ThermalCxState {hp:f64::NAN,..state},
        ThermalCxState {thermal_ev_cm3:1.0,..empty}] {
        assert_eq!(integrate(bad,defect(0.0),&provider,0.0,controls).status,ThermalCxStatus::InvalidInput);
    }
    assert_eq!(integrate(state,defect(0.0),&provider,-1.0,controls).status,ThermalCxStatus::InvalidInput);
    assert_eq!(integrate(state,defect(0.0),&provider,0.0,ThermalCxControls {rtol:f64::NAN,..controls}).status,ThermalCxStatus::InvalidInput);
    let capped=integrate(state,defect(0.0),&provider,2.0,ThermalCxControls {max_attempts:1,..controls});
    assert_eq!(capped.status,ThermalCxStatus::WorkLimit);assert!(!capped.full_interval_complete);
    assert_eq!(capped.counts.attempts,1);assert_eq!(capped.state,Some(state));
    let rhs_capped=integrate(state,defect(0.0),&provider,2.0,ThermalCxControls {max_rhs_calls:1,..controls});
    assert_eq!(rhs_capped.status,ThermalCxStatus::WorkLimit);assert_eq!(rhs_capped.counts.rhs_calls,1);
    let underflow=integrate(state,defect(0.0),&provider,f64::from_bits(1),controls);
    assert_eq!(underflow.status,ThermalCxStatus::StepUnderflow);
    let calls=Cell::new(0usize);
    let failing=|t:f64| {
        calls.set(calls.get()+1);
        if calls.get()==200 {Err(ThermalCxError::FieldFailure("SYNTHETIC_PROVIDER_FAILURE"))}
        else {Ok((0.2*t/10.0,0.2*t/10.0))}
    };
    let failed=integrate(state,defect(0.0),&ThermalCxProvider {rates:&failing,..provider},2.0,controls);
    assert_eq!(failed.status,ThermalCxStatus::ArithmeticFailure);
    assert_eq!(failed.counts.rhs_calls,200);assert!(failed.counts.accepted_steps>0);
    assert!(failed.t_reached_s>0.0&&failed.t_reached_s<2.0);
    check_invariants(state,&failed,0.0);
    let negative=|_:f64|Ok((-1.0,0.0));
    let failed=integrate(state,defect(0.0),&ThermalCxProvider {rates:&negative,..provider},2.0,controls);
    assert_eq!(failed.status,ThermalCxStatus::ArithmeticFailure);
    assert_eq!(failed.counts.rhs_calls,1);assert_eq!(failed.state,Some(state));
}

#[test]
fn si_conversion_and_reused_savin_provider_saved_endpoint_diagnostic() {
    let input=initial([1.0,3.0,2.0,1.0],10.0);let delta=0.1*input.thermal_ev_cm3;
    let rates=|t:f64|Ok((0.2*t/10.0,0.2*t/10.0));
    let provider=ThermalCxProvider {source:"SYNTHETIC_SI_CONVERSION",minimum_k:2.7,maximum_k:30.0,rates:&rates};
    let tiny=DhState {h0_m3:f64::from_bits(1),hp_m3:0.0,d0_m3:0.0,dp_m3:0.0,thermal_j_m3:0.0};
    let original=tiny;
    let rejected=integrate_si(tiny,DhEnergyDefect {delta_chi_j:0.0,source:"SYNTHETIC_CONVERSION_GUARD"},
        &provider,0.0,ThermalCxControls::default());
    assert_eq!(rejected.core.status,ThermalCxStatus::InvalidInput);
    assert!(!rejected.core.full_interval_complete);
    assert_eq!(rejected.core.counts.rhs_calls,0);
    assert!(rejected.state_si.is_none());assert_eq!(tiny,original);
    let core=integrate(input,defect(delta),&provider,2.0,ThermalCxControls::default());
    let si=DhState {h0_m3:input.h0*1e6,hp_m3:input.hp*1e6,d0_m3:input.d0*1e6,
        dp_m3:input.dp*1e6,thermal_j_m3:input.thermal_ev_cm3*(1e6*EV_J)};
    let unexportable=integrate_si(si,DhEnergyDefect {delta_chi_j:f64::from_bits(1),source:"SYNTHETIC_INVERSE_CONVERSION_GUARD"},
        &provider,1e-8,ThermalCxControls::default());
    assert_eq!(unexportable.core.status,ThermalCxStatus::ArithmeticFailure);
    assert!(!unexportable.core.full_interval_complete);
    assert!(unexportable.core.state.is_some()&&unexportable.core.t_reached_s>0.0);
    assert!(unexportable.core.chemical_delta_ev_cm3.unwrap()>0.0);
    assert!(unexportable.state_si.is_none()&&unexportable.extent_m3.is_none());
    assert!(unexportable.integrated_chemical_delta_j_m3.is_none());
    assert!(unexportable.integrated_thermal_delta_j_m3.is_none());
    let native=integrate_si(si,DhEnergyDefect {delta_chi_j:delta*EV_J,source:"SYNTHETIC_SI_CONVERSION"},
        &provider,2.0,ThermalCxControls::default());
    assert_eq!(core.status,native.core.status);
    for (a,b) in [(core.extent_cm3.unwrap(),native.extent_m3.unwrap()/1e6),
        (core.state.unwrap().thermal_ev_cm3,native.state_si.unwrap().thermal_j_m3/(1e6*EV_J))] {
        assert!((a-b).abs()<=128.0*f64::EPSILON*1.0_f64.max(a.abs()).max(b.abs()));
        println!("THERMAL_CX_METRIC {{\"kind\":\"si_conversion\",\"absolute_residual\":{:.17e},\"scaled_residual\":{:.17e}}}",(a-b).abs(),(a-b).abs()/1.0_f64.max(a.abs()).max(b.abs()));
    }
    for t in [2.7,200000.0] {assert!(savin_rates_cm3(t).is_ok());}
    for t in [2.699999,200000.1,f64::NAN] {assert!(savin_rates_cm3(t).is_err());}
    let input=initial([0.9,0.1,2e-5,5e-6],100.0);
    let result=integrate(input,defect(0.0037),&savin_provider(),1e8,ThermalCxControls::default());
    assert!(result.full_interval_complete);check_invariants(input,&result,0.0037);
    assert!(result.temperature_k.unwrap()>=2.7&&result.temperature_k.unwrap()<=200000.0);
    println!("THERMAL_CX_METRIC {{\"kind\":\"savin_saved_endpoint\",\"scope\":\"literature_fit_on_synthetic_isolated_state\",\"extent_cm3\":{:.17e},\"temperature_K\":{:.17e},\"thermal_ev_cm3\":{:.17e},\"extent_difference_cm3\":{:.17e},\"temperature_difference_K\":{:.17e},\"exact_error_claim\":false}}",
        result.extent_cm3.unwrap(),result.temperature_k.unwrap(),result.state.unwrap().thermal_ev_cm3,
        result.extent_cm3.unwrap()-(-4.077787552051901e-7),result.temperature_k.unwrap()-100.00001061103245);
}

#[test]
fn actual_component_owner_api_excludes_double_reaction_and_energy() {
    use IsotopeSpecies::{H1Neutral,H1Ionized,DNeutral,DIonized,He4Neutral};
    let provider=DAtomicProvider::new(13.6,13.6037,"SYNTHETIC_BOUND_THRESHOLDS").unwrap();
    let photo=provider.photo_input(&[],"SYNTHETIC_NO_LIGHT").unwrap();
    let mut values=[0.0;13];
    values[H1Neutral as usize]=0.9e6;values[H1Ionized as usize]=0.1e6;
    values[DNeutral as usize]=2e-5*1e6;values[DIonized as usize]=5e-6*1e6;
    let state=IsotopeNumberState::new(values).unwrap();let original=state;
    let atomic=ThermalCxComponent::new(provider,CxOwnership::AtomicRhs);
    assert_eq!(atomic.rhs(&state,100.0,&photo).unwrap().instantaneous_atomic_rhs,
        d_atomic_rhs(provider,&state,100.0,&photo,DChargeExchange::Savin2002).unwrap());
    assert_eq!(atomic.thermal_substep(&state,f64::NAN,f64::NAN,ThermalCxControls::default()).unwrap_err(),
        ThermalCouplingError::AtomicRhsOwnsCx);
    let thermal=ThermalCxComponent::new(provider,CxOwnership::ThermalSubstep);
    let rhs=thermal.rhs(&state,100.0,&photo).unwrap();
    let disabled=d_atomic_rhs(provider,&state,100.0,&photo,DChargeExchange::Disabled).unwrap();
    assert_eq!(rhs.instantaneous_atomic_rhs,disabled);
    assert_eq!(disabled.cx_forward_events_m3_s,0.0);assert_eq!(disabled.cx_reverse_events_m3_s,0.0);
    assert_eq!(disabled.channel_energy[4],DEnergyLedger::default());
    assert_eq!(disabled.channel_energy[5],DEnergyLedger::default());
    assert_eq!(disabled.species_m3_s[H1Neutral as usize],0.0);
    assert_eq!(disabled.species_m3_s[H1Ionized as usize],0.0);
    let core_input=initial([0.9,0.1,2e-5,5e-6],100.0);
    let u=core_input.thermal_ev_cm3*(1e6*EV_J);
    let result=thermal.thermal_substep(&state,u,1e8,ThermalCxControls::default()).unwrap();
    assert_eq!(result.owner,CxOwnership::ThermalSubstep);
    assert!(result.thermal_map.core.full_interval_complete);
    let energy=result.integrated_cx_energy.unwrap();
    assert_eq!(energy.chemical_delta_j_m3,-energy.thermal_delta_j_m3);
    assert_eq!((energy.photon_input_j_m3,energy.escaped_j_m3),(0.0,0.0));
    let output=result.isotope_state.unwrap();
    let xi=result.thermal_map.extent_m3.unwrap();
    for (species,sign) in [(H1Neutral,1.0),(H1Ionized,-1.0),(DNeutral,-1.0),(DIonized,1.0)] {
        let expected=state.density_m3(species)+sign*xi;
        assert!((output.density_m3(species)-expected).abs()<=128.0*f64::EPSILON*expected.abs().max(1.0));
    }
    let prior=state.moments().unwrap();let after=output.moments().unwrap();
    assert!((prior.neutral_free_electron_density_m3-after.neutral_free_electron_density_m3).abs()<=128.0*f64::EPSILON*prior.neutral_free_electron_density_m3.max(1.0));
    let partial=thermal.thermal_substep(&state,u,1e8,ThermalCxControls {max_rhs_calls:1,..ThermalCxControls::default()}).unwrap();
    assert!(!partial.thermal_map.core.full_interval_complete);
    assert_eq!(partial.thermal_map.core.status,ThermalCxStatus::WorkLimit);
    assert_eq!(state,original);
    values[He4Neutral as usize]=1.0;
    let spectator=IsotopeNumberState::new(values).unwrap();
    assert_eq!(thermal.thermal_substep(&spectator,u,0.0,ThermalCxControls::default()).unwrap_err(),ThermalCouplingError::UnsupportedSpectator);
    assert!(DAtomicProvider::new(13.6,13.5,"INVALID_REVERSED_THRESHOLD").is_err());
}
