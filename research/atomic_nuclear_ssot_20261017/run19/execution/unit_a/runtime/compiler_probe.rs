fn main() { let x = std::hint::black_box(1.25_f64); println!("{:.17e}", x.exp()); }
