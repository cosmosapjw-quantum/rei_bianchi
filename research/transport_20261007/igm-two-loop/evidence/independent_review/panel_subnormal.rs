#[path = "../repo/research/transport_20261007/igm-two-loop/src/panel.rs"]
mod panel;
use panel::{Family, Panel};
fn main() {
    let u=f64::from_bits(1);
    let p=Panel {l:-1.0,r:0.0,beta:0.0,family:Family::RightFront,ln_n:-750.0};
    match p.restrict(-2.0*u,-u) {
        Ok(Some(r))=>println!("ACCEPT {:.17e} {:.17e}",r.normalized_mean,4.0/9.0),
        result=>println!("REJECT {result:?}"),
    }
}
