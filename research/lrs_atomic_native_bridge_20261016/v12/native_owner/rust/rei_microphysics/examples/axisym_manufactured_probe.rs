//! Manufactured prescribed-background probe; no chemistry or source evolution.
use rei_microphysics::{
    AxisymmetricPoint, CharacteristicRay, ConstantAxisymmetricBackground, GeometryBackground,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("scope,MANUFACTURED_PRESCRIBED_COMPONENT_PAIR");
    println!("claim,chemistry_and_radiation_matter_feedback_not_evolved");
    println!("t_proper_s,case,ray,E_over_E0");
    for (case, shear) in [("flrw", 0.0), ("axisym", 0.05)] {
        let point = AxisymmetricPoint::new(1.0, 0.0, 0.1, shear)?;
        let background = ConstantAxisymmetricBackground::new(0.0, point, [0.0, 1.0])?;
        let g0 = background.snapshot(0.0)?;
        let g1 = background.snapshot(1.0)?;
        for (name, direction) in [
            ("axis", [0.0, 0.0, 1.0]),
            ("equator", [1.0, 0.0, 0.0]),
            ("oblique", [0.6, 0.0, 0.8]),
        ] {
            let ray = CharacteristicRay::new(20.0, direction, 1.0)?;
            println!(
                "1,{case},{name},{:.17e}",
                ray.pullback(&g0, &g1)?.energy_ev / ray.energy_ev
            );
        }
    }
    Ok(())
}
