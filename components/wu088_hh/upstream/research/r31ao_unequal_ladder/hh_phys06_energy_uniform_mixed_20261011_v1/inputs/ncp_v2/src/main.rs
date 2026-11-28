mod family;
mod probe;
mod observables;
mod certificate;
fn main(){ if std::env::args().nth(1).as_deref()==Some("--identity-lease"){assert_eq!(hh_phys04_candidate::paired_runtime::phys04_native_counts(),[0;4]);println!("PHYS04_IDENTITY_ONLY science=0 pid={}",std::process::id());std::thread::sleep(std::time::Duration::from_secs(20));return;} if std::env::args().nth(1).as_deref()==Some("--derivative-probe"){probe::derivative_probe();return;} eprintln!("PHYS04_NATIVE_AUTHORIZATION_NULL_BUDGET_ZERO"); assert!(hh_phys04_candidate::paired_runtime::phys04_native_dispatch_requested().is_err()); assert_eq!(hh_phys04_candidate::paired_runtime::phys04_native_counts(),[0;4]); std::process::exit(77) }
