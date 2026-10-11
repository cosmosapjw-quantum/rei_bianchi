use rei_microphysics::characteristic_source::{continuous_photon_step, ContinuousPhotonStage};

#[test]
fn continuous_births_do_not_receive_a_full_step_of_absorption() {
    let s = ContinuousPhotonStage {number: 0., source_per_s: 1., opacity_per_s: [1.,0.,0.]};
    let got = continuous_photon_step(s,1.).unwrap();
    let want = 1. - (-1_f64).exp();
    assert!((got.number-want).abs() < 1e-15);
    // Endpoint deposit followed by backward Euler would give0.5, not this.
    assert!((got.number-0.5).abs()>0.1);
    assert!((got.number+got.absorbed_by_species[0]-1.).abs()<1e-15);
}

#[test]
fn stiff_and_transparent_species_ledgers() {
    for tau in [0.,1e-12,1e-5,1.,100.,1e6] {
        let s = ContinuousPhotonStage {number:0.3,source_per_s:0.7,opacity_per_s:[tau*0.1,tau*0.15,tau*0.25]};
        let got=continuous_photon_step(s,2.).unwrap();
        assert!(got.number>=0. && got.absorbed_by_species.iter().all(|x|*x>=0.));
        assert!((got.number+got.absorbed_by_species.iter().sum::<f64>()-1.7).abs()<1e-13);
        if tau>0. {
            let a=got.absorbed_by_species.iter().sum::<f64>();
            for (v,w) in got.absorbed_by_species.iter().zip([0.2,0.3,0.5]) {
                assert!((v/a-w).abs()<1e-14);
            }
        }
    }
}

#[test]
fn bad_inputs_fail_closed() {
    let mut s = ContinuousPhotonStage {number:0.,source_per_s:1.,opacity_per_s:[1.,0.,0.]};
    s.opacity_per_s[0]=-1.;
    assert!(continuous_photon_step(s,1.).is_err());
    s.opacity_per_s[0]=1.;
    assert!(continuous_photon_step(s,-1.).is_err());
}
