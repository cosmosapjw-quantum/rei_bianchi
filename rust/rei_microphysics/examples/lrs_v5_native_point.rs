//! Read-only PR150 native point comparison at the V5 cgs boundary.
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::{igm_point_rhs, IgmPhotoInput};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<f64> = std::env::args().skip(1).map(|s| s.parse()).collect::<Result<_,_>>()?;
    if args.len() != 10 { return Err("expected nh nhe H T gamma[3] heat[3]".into()); }
    let [nh,nhe,h,t,g0,g1,g2,q0,q1,q2] = <[f64;10]>::try_from(args)
        .map_err(|_| "expected ten values")?;
    // Fractions of the matching V4 stock fixture: HII/(HI+HII),
    // HeII/(HeI+HeII+HeIII), HeIII/(HeI+HeII+HeIII).
    let state = IgmGasState::from_temperature([0.03/0.4,0.012/0.1,0.003/0.1],nh,nhe,t)?;
    let point = igm_point_rhs(&state,nh,nhe,h,2.725,
        IgmPhotoInput {gamma_s:[g0,g1,g2],heat_erg_per_absorber_s:[q0,q1,q2]})?;
    let ci=point.ci_thermal_sink_erg_cm3_s.iter().sum::<f64>();
    let ce=point.ce_thermal_sink_erg_cm3_s.iter().sum::<f64>();
    for (name,values) in [
        ("photo",point.photo_events_cm3_s.to_vec()),
        ("rr",point.rr_events_cm3_s.to_vec()),
        ("dr",vec![point.dr_events_cm3_s]),
        ("rr_cool",point.rr_thermal_sink_erg_cm3_s.to_vec()),
        ("dr_cool",vec![point.dr_thermal_sink_erg_cm3_s]),
        ("photo_input",vec![point.photo_input_erg_cm3_s]),
        ("selected_thermal",vec![point.thermal_micro_erg_cm3_s+ci+ce+
            point.freefree_thermal_sink_erg_cm3_s-point.cmb_to_gas_erg_cm3_s]),
        ("selected_binding",vec![point.binding_micro_erg_cm3_s-ci]),
        ("selected_escape",vec![point.escape_erg_cm3_s-ce-
            point.freefree_thermal_sink_erg_cm3_s]),
    ] {
        print!("{name}");
        for v in values {print!(",{v:.17e}");}
        println!();
    }
    Ok(())
}
