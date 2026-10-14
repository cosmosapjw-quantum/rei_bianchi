#[derive(Debug)] pub enum ForwardError { InvalidInput(&'static str) }
#[path = "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/atomic_provider.rs"] mod atomic_provider;
#[path = "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/ft03_rates.rs"] mod ft03_rates;
fn main() { let p=atomic_provider::AtomicProvider::reference(); for e in [13.5984346,13.599,13.6,13.7] { println!("HI_CROSS_SECTION e={} sigma={:?}",e,p.cross_section(atomic_provider::Absorber::HI,e)); } for t in [50000.0,120000.0] { println!("FT03_RATE t={} result={:?}",t,ft03_rates::ft03_coefficients(t)); } }
