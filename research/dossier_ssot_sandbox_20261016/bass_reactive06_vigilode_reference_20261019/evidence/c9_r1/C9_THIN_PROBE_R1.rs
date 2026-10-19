//! C9 thin-hazard recovery probe R1.
//! The old probe bytes/grid were lost. This is a new declared 22-case grid
//! exercising the same fixed P1 mechanisms; no old result is inherited.
use rei_br06_reference::{
    Result,
    reference::{PathControls, PathModel, PathSample, integrate_path},
};

struct ConstantHazard {
    rate: f64,
}

impl PathModel for ConstantHazard {
    fn sample(&self, t: f64) -> Result<PathSample> {
        let energy_ev = 100.0 * (-0.05 * t).exp();
        Ok(PathSample {
            energy_ev,
            direction: [0.8, 0.0, 0.6],
            energy_derivative_ev_s: -0.05 * energy_ev,
            rates_per_s: [self.rate, 0.0, 0.0, 0.0],
        })
    }
}

fn main() {
    let rates = [
        0.0,
        f64::from_bits(1),
        1e-320,
        1e-310,
        1e-300,
        1e-200,
        1e-100,
        1e-12,
        1e-9,
        1e-8,
        1e-7,
    ];
    println!(
        "case,rate,slabs,opacity_degree,event_degree,status,survival,optical_depth,\
         HI,HeI,HeII,DI,absorbed_total,absorbed_energy_ev,work_independent_ev,\
         work_ledger_ev,end_energy_ev,number_residual,energy_residual_ev,\
         inverse_residual,thin_time_route,opacity_underflow,absorption_underflow,\
         HI_underflow,HI_heat_underflow,survival_underflow"
    );
    let mut case = 0;
    for rate in rates {
        for slabs in [1, 4] {
            case += 1;
            let controls = PathControls {
                slabs,
                opacity_degree: 8,
                event_degree: 16,
                max_samples: 1_000_000,
            };
            match integrate_path(
                &ConstantHazard { rate },
                &[0.0, 1.0],
                [10.0, 20.0, 30.0, 11.0],
                controls,
            ) {
                Ok(r) => {
                    let total: f64 = r.events.iter().sum();
                    println!(
                        "{case},{rate:.17e},{slabs},8,16,ok,{:.17e},{:.17e},\
                         {:.17e},{:.17e},{:.17e},{:.17e},{total:.17e},{:.17e},\
                         {:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},\
                         {},{},{},{},{},{}",
                        r.survival,
                        r.optical_depth,
                        r.events[0],
                        r.events[1],
                        r.events[2],
                        r.events[3],
                        r.absorbed_energy_ev,
                        r.geometry_work_independent_ev,
                        r.geometry_work_ledger_ev,
                        r.end_energy_ev,
                        r.number_residual,
                        r.energy_residual_ev,
                        r.max_inverse_residual,
                        r.thin_time_route,
                        r.represented_opacity_underflow,
                        r.represented_absorption_underflow,
                        r.represented_species_underflow[0],
                        r.represented_heat_underflow[0],
                        r.represented_survival_underflow,
                    );
                }
                Err(error) => {
                    eprintln!("case={case} rate={rate:.17e} slabs={slabs}: {error}");
                    println!(
                        "{case},{rate:.17e},{slabs},8,16,\"{}\",,,,,,,,,,,,,,,,,,,,",
                        error.to_string().replace('"', "\"\"")
                    );
                }
            }
        }
    }
}
