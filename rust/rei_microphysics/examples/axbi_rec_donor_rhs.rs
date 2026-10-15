//! Independent native point-RHS factorial split for HyRec x_e and T_m.
 //! Source is original REI Grackle-CaseA H/He plus Thomson, no stellar
 //! photons in the *initial* source-free state. This does not evolve an IVP.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::axbi_rates::AxbiProvider;
use rei_microphysics::igm_thermal::IgmPhotoInput;
use rei_microphysics::igm_state::IgmGasState;

fn run()->Result<(),String> {
    let x0=2e-4_f64;
    let x1=0.000210349192936_f64;
    let t0=2.7255*21.0_f64.powi(2)/(150.0*(0.0224_f64/0.023).powf(0.4));
    let t1=9.306042400380866_f64;
    println!("q_ref,combination,x_HII,Tgas_K,H_s_inv,n_H_cm3,n_e_cm3,stellar_source_per_H_s,dxHII_dt_s_inv,dTgas_dt_K_s_inv,rr_HI_cm3_s,ci_HI_cm3_s,CMB_heat_erg_cm3_s,energy_local_residual_erg_cm3_s");
    for q in [0.0_f64,-0.01,0.01] {
        let mut conf=DriverConfig::baseline();
        conf.q_ref=q;
        conf.end_zbar=19.95;
        conf.background_panels=64;
        let (d,s)=Driver::new(conf).map_err(|e|format!("{e:?}"))?;
        let bg=d.background.point_at_scale(s.a).map_err(|e|format!("{e:?}"))?;
        let nH=d.n_h0_cm3/s.a.powi(3);
        let nHe=d.n_he0_cm3/s.a.powi(3);
        let emission=d.source.at_redshift(20.0).map_err(|e|format!("{e:?}"))?;
        for (tag,x,t) in [
            ("baseline",x0,t0),
            ("x_only",x1,t0),
            ("T_only",x0,t1),
            ("full_donor",x1,t1),
        ] {
            let gas=IgmGasState::from_temperature([x,0.0,0.0],nH,nHe,t)
                .map_err(|e|format!("{e:?}"))?;
            let eo=gas.eos(nH,nHe).map_err(|e|format!("{e:?}"))?;
            let rhs=AxbiProvider.point(&gas,nH,nHe,bg.h_per_s,
                2.7255/s.a,IgmPhotoInput::default())
                .map_err(|e|format!("{e:?}"))?.rhs;
            if rhs.photo_events_cm3_s.iter().any(|&v|v!=0.0) {
                return Err("photo input does not start at zero".into());
            }
            let balance=rhs.thermal_micro_erg_cm3_s
                +rhs.binding_micro_erg_cm3_s+rhs.escape_erg_cm3_s
                -rhs.photo_input_erg_cm3_s-rhs.cmb_to_gas_erg_cm3_s;
            println!("{q:.17e},{tag},{x:.17e},{t:.17e},{h:.17e},{nH:.17e},{ne:.17e},{src:.17e},{dx:.17e},{dt:.17e},{rr:.17e},{ci:.17e},{cmb:.17e},{balance:.17e}",
                h=bg.h_per_s,ne=eo.electron_density_cm3,
                src=emission.per_h_s,dx=rhs.fraction_dt[0],
                dt=rhs.temperature_dt_k_s,
                rr=rhs.rr_events_cm3_s[0],ci=rhs.ci_events_cm3_s[0],
                cmb=rhs.cmb_to_gas_erg_cm3_s);
        }
    }
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("FAIL {e}");std::process::exit(1)}}
