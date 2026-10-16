//! One source-on FLRW step against the exact PR150 4e2f owner crate.
//! Copy this into that crate's examples/; this is an exploratory one-step
//! bridge, not the production implicit whole-history solver.
use rei_microphysics::axbi_covariant_transport::CovariantTransport;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::igm_point_rhs;
use rei_microphysics::AxisymmetricPoint;

fn rel(a:f64,b:f64)->f64 { (a-b).abs()/a.abs().max(b.abs()).max(1e-300) }

fn main()->Result<(),Box<dyn std::error::Error>> {
    let (a,h,dt,z)=(0.05,1e-16,1e10,19.0);
    let geom=AxisymmetricPoint::new(a,0.0,h,0.0)?.snapshot()?;
    let nh0=1.898198450714027e-7;
    let nh=nh0/a.powi(3);
    let nhe=nh*0.083;
    let source=AxbiSource::new(nh0,0.2,4,8)?;
    let transport=CovariantTransport::new(&source,geom.clone(),64,13.6,512.0)?;
    let mut photons=transport.empty_state();
    let injected=transport.inject(&mut photons,&geom,z,dt)?;
    let (nin,uin)=transport.inventory(&photons,&geom)?;
    let gas=IgmGasState::from_temperature([0.075,0.12,0.03],nh,nhe,15000.0)?;
    let absorbers=[nh*(1.0-gas.fractions[0]),
                   nhe*(1.0-gas.fractions[1]-gas.fractions[2]),
                   nhe*gas.fractions[1]];
    let prepared=transport.prepare(&photons,&geom)?;
    let absorbed=prepared.evaluate(absorbers,nh,dt)?;
    let (nout,uout)=transport.inventory(&absorbed.state,&geom)?;
    let rhs=igm_point_rhs(&gas,nh,nhe,h,2.725/a,absorbed.photo)?;
    let next=IgmGasState::new(std::array::from_fn(|i| gas.fractions[i]+dt*rhs.fraction_dt[i]),
                              gas.w_erg_per_h+dt*rhs.w_dt_erg_per_h_s)?;
    let next_t=next.eos(nh,nhe)?.temperature_k;
    let count_res=rel(nin-nout,absorbed.absorbed_per_h.iter().sum());
    let photon_energy_res=rel(uin-uout,
       absorbed.binding_ev_per_h+absorbed.heat_ev_per_h);
    let source_count_res=rel(nin,injected.added_photons_per_h);
    let source_energy_res=rel(uin,injected.added_energy_ev_per_h);
    let micro_res=rel(rhs.thermal_micro_erg_cm3_s+
       rhs.binding_micro_erg_cm3_s+rhs.escape_erg_cm3_s,
       rhs.photo_input_erg_cm3_s+rhs.cmb_to_gas_erg_cm3_s);
    let electron_res=rel(rhs.species_chemical_cm3_s[5],
       rhs.photo_events_cm3_s.iter().sum::<f64>()+
       rhs.ci_events_cm3_s.iter().sum::<f64>()-
       rhs.rr_events_cm3_s.iter().sum::<f64>()-rhs.dr_events_cm3_s);
    let junction_event_res=(0..3).map(|j| rel(absorbed.absorbed_per_h[j],
        dt*rhs.photo_events_cm3_s[j]/nh)).fold(0.0_f64,f64::max);
    let junction_energy_res=rel(absorbed.binding_ev_per_h+absorbed.heat_ev_per_h,
        dt*rhs.photo_input_erg_cm3_s/(nh*1.602176634e-12));
    if [count_res,photon_energy_res,source_count_res,source_energy_res,
        micro_res,electron_res,junction_event_res,junction_energy_res].iter()
        .any(|x| *x>1e-10) || next_t<=0.0 {
        return Err("NATIVE_SOURCE_STEP_LEDGER_FAIL".into());
    }
    println!("{{\"source_id\":\"MD14_Z002_FESC_BB50K_13P6_100_V1\",\"a\":{a:.17e},\"z\":{z:.17e},\"dt_s\":{dt:.17e},\"nh_cm3\":{nh:.17e},\"source_photons_per_h\":{nin:.17e},\"absorbed_photons_per_h\":{:.17e},\"T_initial_K\":15000.0,\"T_next_explicit_K\":{next_t:.17e},\"source_count_relative_residual\":{source_count_res:.17e},\"source_energy_relative_residual\":{source_energy_res:.17e},\"photon_count_relative_residual\":{count_res:.17e},\"photon_energy_relative_residual\":{photon_energy_res:.17e},\"electron_relative_residual\":{electron_res:.17e},\"micro_energy_relative_residual\":{micro_res:.17e},\"junction_event_relative_residual\":{junction_event_res:.17e},\"junction_energy_relative_residual\":{junction_energy_res:.17e},\"node_count\":{}}}",absorbed.absorbed_per_h.iter().sum::<f64>(),prepared.node_count());
    Ok(())
}
