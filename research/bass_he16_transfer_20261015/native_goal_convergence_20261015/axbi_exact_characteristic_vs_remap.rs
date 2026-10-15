//! Source-bound exact CovariantPhoton vs frozen-grid repeated remapper, signed q.
//! Explicitly not a replacement of any production collision/chemistry source.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
use std::fmt::Write as _;

fn main() {
    let mut buf=String::new();
    writeln!(&mut buf,"q_ref,remap_steps,initial_E_eV,exact_end_E_eV,reprojected_surviving_mean_E_eV,relative_energy_bias,number_surviving,number_boundary,number_ledger_residual,energy_ledger_residual").unwrap();
    for q in [-0.005_f64,0.0,0.005] {
        let mut config=DriverConfig::baseline();
        config.q_ref=q;
        config.end_zbar=19.8;
        config.background_panels=4096;
        let (driver,initial)=Driver::new(config).expect("frozen native Driver::new");
        let a_ref=initial.a;
        let a_end=1./20.8;
        let gi=driver.background.point_at_scale(a_ref).unwrap().geometry().unwrap();
        let go=driver.background.point_at_scale(a_end).unwrap().geometry().unwrap();
        let kray=driver.source.angular_cells.len()/2;
        let mu=driver.source.angular_cells[kray].mu;
        let direction=[(1.-mu*mu).sqrt(),0.,mu];
        let index=5_usize;
        let E=driver.energies[index];
        let exact=CovariantPhoton::from_local(&gi,E,direction,1.).unwrap().energy_at(&go).unwrap();
        assert!(exact>driver.energies[0], "exact photon remains above minimum energy node");
        for steps in [1_usize,4096_usize] {
            let mut state=initial.clone();
            state.photons[kray*driver.energies.len()+index]=1.;
            state.ledgers.source_n=1.;
            state.ledgers.source_u=E;
            let l=(a_end/a_ref).ln();
            for i in 1..=steps {
                let next=if i==steps {a_end} else {a_ref*(l*(i as f64)/(steps as f64)).exp()};
                driver.geometry_map(&mut state,next).unwrap();
            }
            let (n,energy)=driver.photon_inventory(&state);
            let (rn,re)=driver.residuals(&state).unwrap();
            assert!(rn.abs()<1e-11 && re.abs()<1e-11,"Native source photon ledgers failed");
            assert!((n+state.ledgers.boundary_n-1.).abs()<1e-11);
            let mean=energy/n;
            writeln!(&mut buf,"{q:.6},{steps},{E:.17e},{exact:.17e},{mean:.17e},{:.17e},{n:.17e},{:.17e},{rn:.17e},{re:.17e}",
                (mean-exact)/exact,state.ledgers.boundary_n).unwrap();
        }
    }
    print!("{buf}");
}
