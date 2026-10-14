use axbi_atomic_vector_component::{validation,POINTS,CELLS};
use std::sync::atomic::Ordering;
#[test]
fn exact_components(){let result=std::panic::catch_unwind(validation);println!("OBSERVED_COUNTERS point_calls={} photon_cells={}",POINTS.load(Ordering::SeqCst),CELLS.load(Ordering::SeqCst));let (p,c,res)=result.unwrap();println!("validation_point_calls={p} photon_cells={c} residuals={res:?}");}
