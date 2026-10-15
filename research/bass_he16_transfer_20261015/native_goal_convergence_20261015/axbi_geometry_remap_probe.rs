//! Exploratory isolated pure collisionless AXBI geometry remap semigroup probe.
//! Original rei_microphysics crate is linked; native solver/source not modified.
//! A monoenergetic packet has exact zero energy variance under free streaming;
//! grid deposition broadens it while conserving count and first energy moment.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use std::fmt::Write as _;

fn main() {
    let mut output=String::new();
    writeln!(&mut output, "z_end,steps,energy_index,start_energy_eV,exact_end_eV,mean_end_eV,relative_mean_error,variance_eV2,occupied_bins,photon_number,boundary_loss,number_ledger_residual,energy_ledger_residual").unwrap();
    for end_zbar in [19.99_f64, 19.8_f64] {
        let mut config=DriverConfig::baseline();
        config.end_zbar=end_zbar;
        config.q_ref=0.0;
        config.background_panels=4096;
        let (driver, initial)=Driver::new(config).expect("Original AXBI Driver::new");
        let a_ref=initial.a;
        let a_end=1.0/(1.0+end_zbar);
        let ne=driver.energies.len();
        for eindex in [5_usize,15,25] {
            let e0=driver.energies[eindex];
            let exact=e0*a_ref/a_end;
            for steps in [1_usize,2,4,16,64,256,1024,4096] {
                let mut state=initial.clone();
                // One photon in one mid-angle ray; use no source or chemistry.
                let ray=driver.source.angular_cells.len()/2;
                state.photons[ray*ne+eindex]=1.0;
                state.ledgers.source_n=1.0;
                state.ledgers.source_u=e0;
                let logarithmic=(a_end/a_ref).ln();
                for i in 1..=steps {
                    let next=if i==steps {a_end} else {
                        a_ref*(logarithmic*(i as f64)/(steps as f64)).exp()
                    };
                    driver.geometry_map(&mut state,next).expect("geometry_map");
                }
                let mut count=0_f64;let mut energy=0_f64;
                let mut energy2=0_f64;let mut occupied=0_usize;
                for k in 0..driver.source.angular_cells.len() {
                    for j in 0..ne {
                        let v=state.photons[k*ne+j];
                        if v!=0.0 {occupied+=1;}
                        count+=v;
                        energy+=v*driver.energies[j];
                        energy2+=v*driver.energies[j]*driver.energies[j];
                    }
                }
                let mean=energy/count;
                let variance=(energy2/count-mean*mean).max(0.0);
                let (number_residual,energy_residual)=driver.residuals(&state).expect("native number-energy ledger");
                if number_residual.abs()>1e-8 || energy_residual.abs()>1e-8 {
                    panic!("Native number-energy ledger failed: {number_residual}, {energy_residual}");
                }
                writeln!(&mut output, "{end_zbar},{steps},{eindex},{e0:.17e},{exact:.17e},{mean:.17e},{:.17e},{variance:.17e},{occupied},{count:.17e},{:.17e},{number_residual:.17e},{energy_residual:.17e}",
                    (mean-exact)/exact,state.ledgers.boundary_n
                ).unwrap();
            }
        }
    }
    print!("{output}");
}
