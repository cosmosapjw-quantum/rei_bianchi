//! Exactly-5000 K raw-provider diagnostic; no history or physical admission.
use rei_microphysics::{AtomicProvider, CoefficientUnits, RawProcess, RecombinationCase};

fn main() {
    let provider = AtomicProvider::reference();
    use RawProcess::*;
    for process in [
        K1, K2, K3, K4, K5, K6, CeHI, CeHeI, CeHeII, CiHeIS, CiHI, CiHeI, CiHeII, ReHII, ReHeII1,
        ReHeII2, ReHeIII, Brem,
    ] {
        let coefficient = provider
            .raw_coefficient(process, 5000.0, RecombinationCase::A)
            .expect("frozen raw diagnostic temperature");
        let record = provider.record(process);
        let unit = match coefficient.unit {
            CoefficientUnits::Cm3PerSecond => "cm3/s",
            CoefficientUnits::ErgCm3PerSecond => "erg*cm3/s",
            CoefficientUnits::ErgCm6PerSecond => "erg*cm6/s",
        };
        println!(
            "{},{:.17e},{},{},{},{}",
            record.source_function,
            coefficient.value,
            unit,
            record.density_prefactor,
            record.consumer_admission,
            record.domain.physical_support_resolved,
        );
    }
}
