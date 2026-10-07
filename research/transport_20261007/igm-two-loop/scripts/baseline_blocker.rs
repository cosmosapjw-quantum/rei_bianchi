#[allow(dead_code)]
#[path = "../../continuous-boundary-prototype-v2/src/primitives.rs"]
mod old;
fn main() {
    let tagged = old::inventory(Some(-750.0), Some(-750.0 + 20.0_f64.ln())).unwrap();
    assert!(matches!(tagged, old::Inventory::LogTail { .. }));
    let result = old::characteristic(20.0_f64.ln(), 0.0, 0.001, 1.0, 0.0, 0.0, 0.0, [1.0e6, 0.0, 0.0]);
    assert!(result.is_err());
    println!("existing_positive_tail_tag={tagged:?}");
    println!("existing_multisegment_evolution={result:?}");
    println!("REPRODUCED: positive underflow tail cannot advance in existing V2 characteristic");
}
