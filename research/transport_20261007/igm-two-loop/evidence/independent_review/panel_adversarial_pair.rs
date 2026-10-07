#[path = "../repo/research/transport_20261007/igm-two-loop/src/panel.rs"]
mod panel;
use panel::{Family, Panel};
fn main() {
    println!("log_parent,log_fraction,log_restricted,log_restricted_low,normalized_mean,node_admitted");
    for ln_n in [-750.0, -1000.0, -10000.0, -100000.0, -1.0e12] {
        let p = Panel {l: 0.0, r: 1.0, beta: 0.0, family: Family::Ordinary, ln_n};
        match p.restrict(0.0, 0.5) {
            Ok(Some(r)) => println!("{ln_n:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{}", r.ln_fraction,r.ln_n,r.ln_n_lo,r.normalized_mean,r.quadrature_node().is_ok()),
            other => println!("{ln_n:.17e},REJECT,{other:?}"),
        }
    }
    let p=Panel {l:-1.0, r:1.0, beta:0.0, family:Family::Ordinary,ln_n:-750.0};
    let r=p.restrict(-1.0,1.0).unwrap().unwrap();
    assert!(r.quadrature_node().is_ok());
    assert_eq!(r.ln_fraction,0.0);
    assert!(p.restrict(f64::NAN,1.0).is_err());
    let p=Panel {l:0.0,r:1.0,beta:128.0,family:Family::RightFront,ln_n:-750.0};
    let r=p.restrict(f64::from_bits(1.0f64.to_bits()-1),1.0).unwrap().unwrap();
    assert!(r.quadrature_node().is_err());
}
