//! Manufactured, source-free foundation tracer. NOT a physical IGM history,
//! chemistry solver, observed cosmology, REC splice or interval certificate.
use rei_microphysics::coupled_primary::PrimaryPacket;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::igm_state::{
    photon_packet_to_primary, primary_to_photon_packet, IgmGasState,
};
use rei_microphysics::RadiationState;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let bg = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: 2e-18,
        omega_r: 0.01,
        omega_m: 0.29,
        omega_b: 0.04,
        omega_lambda: 0.70,
        helium_mass_fraction: 0.24,
        tcmb0_k: 3.0,
        ln_a_min: 0.125_f64.ln(),
        ln_a_max: 0.0,
        parameter_source: "manufactured-foundation-v1; not observationally calibrated".into(),
    })?;
    let first = bg.at_redshift(7.0)?;
    let gas =
        IgmGasState::from_temperature([0.001, 0.0, 0.0], first.n_h_cm3, first.n_he_cm3, 17.0)?;
    let radiation = RadiationState::new(
        first.geometry,
        vec![primary_to_photon_packet(
            &PrimaryPacket {
                energy_ev: 70.0,
                per_h: 0.1,
            },
            bg.n_h_comoving_cm3(),
            [0.0, 0.6, 0.8],
        )?],
    )?;
    eprintln!("model=manufactured-foundation-v1; fixed fractions; no sources/absorption/cooling; mHe=4mp; no cosmic-time integration");
    println!("ln_a,a,z,H_per_s,dt_dln_a_s,dt_dz_s,nH_cm3,nHe_cm3,Tcmb_K,xHII,xHeII,xHeIII,ne_cm3,w_erg_per_H,u_erg_cm3,T_K,photon_E_eV,photons_per_H,photon_comoving_cm3,photon_proper_cm3");
    for i in 0..=8 {
        let ln_a = first.a.ln() + (0.5_f64.ln() - first.a.ln()) * f64::from(i) / 8.0;
        let p = bg.at_ln_a(ln_a)?;
        let s = gas.adiabatic_to(first.a, p.a)?;
        let eos = s.eos(p.n_h_cm3, p.n_he_cm3)?;
        let rad = radiation.transport(p.geometry)?;
        let packet = photon_packet_to_primary(&rad.packets[0], bg.n_h_comoving_cm3())?;
        println!("{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            ln_a,p.a,p.redshift,p.hubble_per_s,p.dt_dln_a_s,p.dt_dz_s,p.n_h_cm3,p.n_he_cm3,p.tcmb_k,
            s.fractions[0],s.fractions[1],s.fractions[2],eos.electron_density_cm3,s.w_erg_per_h,eos.u_erg_cm3,eos.temperature_k,
            packet.energy_ev,packet.per_h,rad.comoving_photon_count()?,rad.proper_photon_density_cm3()?);
    }
    Ok(())
}
