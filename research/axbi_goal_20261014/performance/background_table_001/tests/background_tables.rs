use axbi_background_table_benchmark::*;
use rei_microphysics::axbi_background::BackgroundFamily;
#[test]
fn exact_cache_errors_fifo_and_identity(){
 let counts=Counts::default();let m=Model::new(0.01,BackgroundFamily::PhysicalDensityFixed,counts.clone()).unwrap();let mut c=ExactCache::new(m.clone());
 for a in [AR,AE,scale(1,8192)]{assert_eq!(point_bits(c.query(a).unwrap()),point_bits(m.direct(a).unwrap()));assert_eq!(point_bits(c.query(a).unwrap()),point_bits(m.direct(a).unwrap()));}
 for j in 1..=257 {c.query(scale(j,8192)).unwrap();} let before=c.misses;c.query(AR).unwrap();assert_eq!(c.misses,before+1);
 for a in [f64::NAN,f64::INFINITY,0.0,-1.0,AR*0.999,AE*1.001]{let direct=m.direct(a).unwrap_err();let cache=c.query(a).unwrap_err();assert_eq!(format!("{direct:?}"),format!("{cache:?}"));}
 std::fs::write(concat!(env!("CARGO_MANIFEST_DIR"),"/raw/local_test_counts.json"),format!("{{\"direct\":{},\"candidate\":{},\"integrand\":{}}}",counts.direct.get(),counts.candidate.get(),counts.integrand.get())).unwrap();
}
