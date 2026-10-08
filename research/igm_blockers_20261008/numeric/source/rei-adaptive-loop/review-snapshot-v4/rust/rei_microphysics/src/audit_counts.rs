use std::sync::atomic::{AtomicUsize,Ordering};
pub static RHS:AtomicUsize=AtomicUsize::new(0);
pub static SIGMA:AtomicUsize=AtomicUsize::new(0);
pub fn read()->(usize,usize){(RHS.load(Ordering::Relaxed),SIGMA.load(Ordering::Relaxed))}
