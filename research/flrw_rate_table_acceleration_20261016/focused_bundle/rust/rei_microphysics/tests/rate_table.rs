use std::{hint::black_box, sync::{Arc, OnceLock}, time::Instant};
pub use rei_microphysics::{igm_rates, igm_state, ForwardError, HHeModel};
use rei_microphysics::{axbi_rates::AxbiProvider, deuterium_atomic::DAtomicProvider,
    igm_state::IgmGasState, igm_thermal::{igm_point_rhs, igm_point_rhs_with_prepared, IgmPhotoInput, IgmPointRhs},
    rate_table::*};
#[path="../../../research/flrw_rate_table_acceleration_20261016/probe/baseline_igm_thermal.rs"]
mod baseline;

static TABLE: OnceLock<Arc<IgmRateTable>> = OnceLock::new();
fn table() -> &'static Arc<IgmRateTable> {
    TABLE.get_or_init(|| Arc::new(IgmRateTable::build_default().unwrap()))
}
fn neighbors(t:f64)->[f64;3]{[f64::from_bits(t.to_bits()-1),t,f64::from_bits(t.to_bits()+1)]}
fn direct(t:f64)->igm_rates::IgmRates{igm_rates::igm_rates(t).unwrap()}
fn baseline_photo(p:IgmPhotoInput)->baseline::IgmPhotoInput{
    baseline::IgmPhotoInput{gamma_s:p.gamma_s,heat_erg_per_absorber_s:p.heat_erg_per_absorber_s}
}
fn event_scale(r:&IgmPointRhs)->f64 {
    r.photo_events_cm3_s.iter().chain(&r.ci_events_cm3_s).chain(&r.rr_events_cm3_s).sum::<f64>()+r.dr_events_cm3_s
}
fn power_scale(r:&IgmPointRhs)->f64 {
    r.escape_erg_cm3_s+r.photo_input_erg_cm3_s+r.cmb_to_gas_erg_cm3_s.abs()
        +r.ci_thermal_sink_erg_cm3_s.iter().sum::<f64>()
}
fn assert_ledger(r:&IgmPointRhs) {
    let eps=64.0*f64::EPSILON;
    assert!((r.species_chemical_cm3_s[0]+r.species_chemical_cm3_s[1]).abs()<=eps*event_scale(r));
    assert!(r.species_chemical_cm3_s[2..5].iter().sum::<f64>().abs()<=eps*event_scale(r));
    assert!((r.species_chemical_cm3_s[1]+r.species_chemical_cm3_s[3]+2.0*r.species_chemical_cm3_s[4]-r.species_chemical_cm3_s[5]).abs()<=eps*event_scale(r));
    let residual=r.thermal_micro_erg_cm3_s+r.binding_micro_erg_cm3_s+r.escape_erg_cm3_s-r.photo_input_erg_cm3_s-r.cmb_to_gas_erg_cm3_s;
    assert!(residual.abs()<=eps*power_scale(r));
}

#[test]
fn a_generic_grid_keeps_uncertified_zero_sign_and_outside_domain_direct() {
    let f=|t:f64|if !t.is_finite()||!(1.0..=1000.0).contains(&t){Err(ForwardError::InvalidInput("PROVIDER_DOMAIN"))}else{Ok([(t.ln()-10f64.ln())*(100f64.ln()-t.ln())])};
    let grid=LogRateGrid::build(10.0,100.0,2,f,|_,_|false,|_,_,_|false).unwrap();
    assert_eq!(grid.evaluate(30.0,f).unwrap(),f(30.0).unwrap());
    assert_eq!(grid.evaluate(1.0,f).unwrap(),f(1.0).unwrap());
    assert!(grid.evaluate(f64::NAN,f).is_err());
    let zero=LogRateGrid::build(1.0,100.0,4,|_|Ok([0.0]),|_,_|false,|_,_,_|true).unwrap();
    assert_eq!(zero.evaluate(20.0,|_|panic!("certified zero should not invoke source")).unwrap(),[0.0]);
    let sign=|t:f64|Ok([t-10.0]);
    let signed=LogRateGrid::build(1.0,100.0,2,sign,|_,_|false,|_,_,_|false).unwrap();
    assert_eq!(signed.evaluate(3.0,sign).unwrap(),[-7.0]);
    let tiny=LogRateGrid::build(1.0,100.0,2,|_|Ok([f64::from_bits(1)]),|_,_|false,|_,_,_|false).unwrap();
    assert_eq!(tiny.evaluate(5.0,|_|Ok([f64::from_bits(1)])).unwrap(),[f64::from_bits(1)]);
    assert!(LogRateGrid::<1>::build(1e6,f64::from_bits(1e6f64.to_bits()+1),100,|_|Ok([1.0]),|_,_|false,|_,_,_|false).is_err());
}

#[test]
fn b_scalar_soa_parallel_and_exact_floor_neighbors_agree() {
    let table=table(); let mut ts=vec![1.0,10.0,100.0,1e4,1e5,1e6];
    for t in igm_branch_knots(){ts.extend(neighbors(t));}
    let(mut lo,mut hi)=(1.0f64,9284.0f64);
    assert!(direct(lo).diagnostics.ci_floor_cm3_s[0]!=0.0);
    assert!(direct(hi).diagnostics.ci_floor_cm3_s[0]==0.0);
    while hi.to_bits()-lo.to_bits()>1 {
        let mid=f64::from_bits((lo.to_bits()+hi.to_bits())/2);
        if direct(mid).diagnostics.ci_floor_cm3_s[0]!=0.0{lo=mid}else{hi=mid}
    }
    ts.extend(neighbors(lo));ts.extend(neighbors(hi));
    println!("CI_FLOOR_BRACKET lower={lo:.17e} upper={hi:.17e}");
    let serial=table.batch_soa(&ts).unwrap();
    for workers in [1,2,4]{assert_eq!(serial,table.batch_parallel(&ts,workers).unwrap());}
    for(q,&t)in ts.iter().enumerate(){
        let got=table.rates(t).unwrap();let reference=direct(t);
        assert_eq!(igm_flat(got),std::array::from_fn(|j|serial[j][q]));
        for j in 0..3{
            assert_eq!(got.diagnostics.ci_floor_cm3_s[j]!=0.0,reference.diagnostics.ci_floor_cm3_s[j]!=0.0);
            assert_eq!(got.diagnostics.ce_cap_erg[j]!=0.0,reference.diagnostics.ce_cap_erg[j]!=0.0);
            if reference.diagnostics.ci_floor_cm3_s[j]!=0.0{assert_eq!(got.ci_cm3_s[j],1e-20);}
        }
        assert_eq!(got.diagnostics.dr_low_branch,reference.diagnostics.dr_low_branch);
        if reference.dr_cm3_s==0.0{assert_eq!(got.dr_cm3_s,0.0);assert_eq!(got.dr_cooling_erg_cm3_s,0.0);}
    }
    assert!(table.batch_parallel(&ts,0).is_err());assert!(table.batch_parallel(&ts,5).is_err());
    assert!(table.batch_soa(&[10.0,f64::NAN]).is_err());
    assert!(table.batch_parallel(&[10.0,f64::NAN],2).is_err());
    for t in [0.0,0.99999,1e6+1.0,f64::NAN,f64::INFINITY]{assert!(table.rates(t).is_err());}
}

#[test]
fn c_prepared_direct_matches_frozen_ledger_and_table_preserves_event_scales() {
    let(nh,nhe)=(1.5e-3,1.2e-4);let photo=IgmPhotoInput{gamma_s:[1e-13,2e-14,3e-15],heat_erg_per_absorber_s:[1e-24,2e-25,3e-26]};
    let backend=IgmRateBackend::Table(table().clone());
    for fractions in [[2e-4,1e-5,1e-8],[0.3,0.2,0.1],[1.0,0.0,1.0]]{
      for t in [6.137,20.0,100.0,5500.0,9284.0,1e4,1e5]{
        let gas=IgmGasState::from_temperature(fractions,nh,nhe,t).unwrap();
        let reference=baseline::igm_point_rhs(&gas,nh,nhe,1e-16,57.2355,baseline_photo(photo)).unwrap();
        let exact=AxbiProvider.point(&gas,nh,nhe,1e-16,57.2355,photo).unwrap();
        assert_eq!(format!("{:?}",exact.rhs),format!("{reference:?}"));
        assert_eq!(format!("{:?}",exact.rates),format!("{:?}",direct(exact.temperature_k)));
        let reference = exact.rhs; // Same every-field output as the frozen oracle above.
        assert_eq!(format!("{:?}",igm_point_rhs(&gas,nh,nhe,1e-16,57.2355,photo).unwrap()),format!("{reference:?}"));
        let approximate=AxbiProvider.point_with_backend(&backend,&gas,nh,nhe,1e-16,57.2355,photo).unwrap();let r=approximate.rhs;
        assert_ledger(&reference);assert_ledger(&r);
        let es=event_scale(&reference);let ps=power_scale(&reference);
        for(a,b)in r.species_chemical_cm3_s.iter().zip(reference.species_chemical_cm3_s){assert!((a-b).abs()<=1e-5*es);}
        for(a,b)in [r.thermal_micro_erg_cm3_s,r.binding_micro_erg_cm3_s,r.escape_erg_cm3_s].into_iter().zip([reference.thermal_micro_erg_cm3_s,reference.binding_micro_erg_cm3_s,reference.escape_erg_cm3_s]){assert!((a-b).abs()<=1e-5*ps);}
        assert!((r.w_dt_erg_per_h_s-reference.w_dt_erg_per_h_s).abs()<=1e-5*ps/nh);
        let particles=nh+nhe+gas.eos(nh,nhe).unwrap().electron_density_cm3;
        let temperature_scale=2.0*ps/(3.0*HHeModel::controlled_fixture().kb_erg_k*particles)+exact.temperature_k*es/particles;
        assert!((r.temperature_dt_k_s-reference.temperature_dt_k_s).abs()<=1e-5*temperature_scale);
        assert_eq!(r.expansion_work_erg_cm3_s,reference.expansion_work_erg_cm3_s);
        assert_eq!(r.cmb_to_gas_erg_cm3_s,reference.cmb_to_gas_erg_cm3_s);
      }
    }
}

#[test]
fn d_prepared_temperature_identity_and_deuterium_projection_are_explicit() {
    let(nh,nhe)=(1e-3,8e-5);let gas=IgmGasState::from_temperature([0.1,0.1,0.1],nh,nhe,10000.0).unwrap();
    let t=gas.eos(nh,nhe).unwrap().temperature_k;
    let p=IgmRateBackend::Direct.prepare(t).unwrap();
    assert_eq!(p.evaluator_id(),IGM_DIRECT_EVALUATOR);
    let d=DAtomicProvider::new(13.598434599702,13.602134599702,"explicit test threshold").unwrap();
    assert_eq!(d.rates(t).unwrap(),d.rates_from_prepared(&p));
    let tab=IgmRateBackend::Table(table().clone()).prepare(t).unwrap();
    assert_eq!(tab.evaluator_id(),IGM_TABLE_EVALUATOR);
    let selected=d.rates_from_prepared(&tab);let h=tab.rates();
    assert_eq!(selected.ci_m3_s,h.ci_cm3_s[0]*1e-6);assert_eq!(selected.ce_j_m3_s,h.ce_erg[0]*1e-13);
    let wrong=IgmRateBackend::Direct.prepare(t+1.0).unwrap();
    let e=igm_point_rhs_with_prepared(&gas,nh,nhe,0.0,50.0,IgmPhotoInput::default(),&wrong).unwrap_err();
    assert_eq!(e.code(),"IGM_PREPARED_TEMPERATURE_MISMATCH");
    assert!(IgmRateBackend::Direct.prepare(f64::NAN).is_err());
}

fn checksum(values: impl IntoIterator<Item=[f64;15]>, scales:&[f64;15])->f64{
    values.into_iter().map(|v|v.iter().zip(scales).map(|(a,b)|a/b).sum::<f64>()).sum()
}
fn temperatures(n:usize,random:bool)->Vec<f64>{
    let mut seed=0x172942a3d8c56f01u64;
    (0..n).map(|i|{let u=if random{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);(seed>>11)as f64/(1u64<<53)as f64}else{(i as f64+0.371)/n as f64};(1e6f64.ln()*u).exp()}).collect()
}
#[test]
fn z_benchmark_same_inputs_three_samples_and_shared_table() {
    let table=table();let scales=igm_flat(direct(1e4));
    println!("BENCH_META {{\"compiler\":\"rustc1.85.1\",\"threads\":4,\"available_parallelism\":{},\"nodes\":{},\"grid_payload_bytes\":{},\"table_payload_bytes\":{}}}",std::thread::available_parallelism().unwrap().get(),table.grid().nodes(),table.grid().storage_bytes(),table.storage_bytes());
    for random in [false,true]{let distribution=if random{"random_logT"}else{"ordered_logT"};
      for n in [256,8192]{let ts=temperatures(n,random);
        for sample in 0..3{let mut checks=[0.0;4];
          for (m,method)in ["direct","table_scalar","table_soa","table_parallel4"].into_iter().enumerate(){
            let start=Instant::now();
            let sum=match m{
                0=>checksum(ts.iter().map(|&t|igm_flat(black_box(direct(black_box(t))))),&scales),
                1=>checksum(ts.iter().map(|&t|igm_flat(black_box(table.rates(black_box(t)).unwrap()))),&scales),
                _=>{let rows=if m==2{table.batch_soa(black_box(&ts)).unwrap()}else{table.batch_parallel(black_box(&ts),4).unwrap()};let rows=black_box(rows);checksum((0..n).map(|q|std::array::from_fn(|j|rows[j][q])),&scales)}
            };
            let seconds=start.elapsed().as_secs_f64();black_box(sum);checks[m]=sum;
            println!("BENCH {{\"distribution\":\"{distribution}\",\"n\":{n},\"sample\":{sample},\"method\":\"{method}\",\"seconds\":{seconds:.12},\"checksum\":{sum:.17e}}}");
          }
          for sum in &checks[1..]{assert!((sum/checks[0]-1.0).abs()<=1e-5);}
        }
      }
    }
    let(nh,nhe)=(1.5e-3,1.2e-4);let photo=IgmPhotoInput::default();
    let states:Vec<_>=(0..1024).map(|i|IgmGasState::from_temperature([2e-4,1e-5,1e-8],nh,nhe,(10f64.ln()+1e4f64.ln()*(i as f64+0.371)/1024.0).exp()).unwrap()).collect();
    let backend=IgmRateBackend::Table(table.clone());
    for sample in 0..3{for(method,m)in [("legacy_double_direct",0),("prepared_direct_point",1),("table_point",2)]{
      let start=Instant::now();let mut sum=0.0;
      for gas in &states{let value=if m==0{let t=gas.eos(nh,nhe).unwrap().temperature_k;let rhs=baseline::igm_point_rhs(black_box(gas),nh,nhe,1e-16,57.2355,baseline_photo(photo)).unwrap();black_box(direct(t));black_box(rhs).temperature_dt_k_s}else if m==1{black_box(AxbiProvider.point(black_box(gas),nh,nhe,1e-16,57.2355,photo).unwrap()).rhs.temperature_dt_k_s}else{black_box(AxbiProvider.point_with_backend(&backend,black_box(gas),nh,nhe,1e-16,57.2355,photo).unwrap()).rhs.temperature_dt_k_s};sum+=value;}
      let seconds=start.elapsed().as_secs_f64();black_box(sum);
      println!("POINT_BENCH {{\"n\":1024,\"sample\":{sample},\"method\":\"{method}\",\"seconds\":{seconds:.12},\"checksum\":{sum:.17e}}}");
    }}
}
