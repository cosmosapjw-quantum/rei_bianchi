//! Source-derived native Rust quadrupole oracle for independent Python GL check.
//! Uses the existing unchanged REI source diagnostic. NO driver mutation.
use rei_microphysics::axbi_background::isotropic_initial_radiation_moments;

fn main() {
    let h0=67.4e3/3.0856775814913673e22_f64;
    let g=6.67430e-11_f64;
    let c=299792458.0_f64;
    let kappa=8.0*std::f64::consts::PI*g/(3.0*c*c);
    let aref=1.0_f64/21.0;
    let eps_ref=h0*h0/kappa*9.2e-5/aref.powi(4);
    println!("b,epsilon_J_m3,Pi_J_m3,delta_epsilon_J_m3");
    for b in [0.0_f64,0.00001,-0.00001,0.001,-0.001,0.005,-0.005,0.02,-0.02] {
        let m=isotropic_initial_radiation_moments(
            1.0/5.0,b,aref,0.0,eps_ref,4096
        ).expect("native historical moment evaluator");
        println!("{b:.17e},{:.17e},{:.17e},{:.17e}",
            m.energy_j_m3,
            m.pressure_anisotropy_j_m3,
            m.signed_energy_correction_j_m3
        );
    }
}
