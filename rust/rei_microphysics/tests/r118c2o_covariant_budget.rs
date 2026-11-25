use rei_microphysics::axbi_covariant_driver::{Driver,DriverConfig};
#[test]
fn config_and_direct_chemical_budget(){
    let mut c=DriverConfig::baseline();c.end_zbar=19.8;c.background_panels=64;c.transport_cells=32;
    let (d,mut s)=Driver::new(c).unwrap();
    s.gas=rei_microphysics::igm_state::IgmGasState::from_temperature([0.3,0.28,0.01],d.n_h0_cm3/s.a.powi(3),d.n_he0_cm3/s.a.powi(3),3000.).unwrap();
    for (e,n) in [(20.,0.005),(30.,0.003),(80.,0.0002)]{
        for ray in 0..d.source.angular_cells.len(){
            d.seed_delta(&mut s,ray,e,n*d.source.angular_cells[ray].count_fraction).unwrap();
        }
        s.ledgers.source_n+=n;s.ledgers.source_u+=e*n;
    }
    let mut found=false;
    for dt in [1e4,1e5,1e6,1e7,1e8,1e9,1e10,1e11,1e12] {
        let mut old=s.clone();let mut new=s.clone();let mut n=0;let mut m=0;
        let before=d.total_energy(&s).unwrap();
        d.chemical_stage(&mut old,dt,&mut n).unwrap();
        d.chemical_stage_budgeted(&mut new,dt,&mut m,5e-14).unwrap();
        let a=(d.total_energy(&old).unwrap()-before).abs();
        let b=(d.total_energy(&new).unwrap()-before).abs();
        eprintln!("dt={dt:e}, legacy={a:e}, budget={b:e}, RHS {n}/{m}");
        assert!(b<=5.2e-14,"budget defect {b:e}");
        if a>5.2e-14 {found=true;assert!(m>=n);}
    }
    assert!(found,"fixture must exercise budget");
    assert!(DriverConfig::read("energy_budget_ev_per_h=-1").is_err());
    assert!(DriverConfig::read("energy_budget_ev_per_h=NaN").is_err());
    assert_eq!(DriverConfig::read("energy_budget_ev_per_h=1e-8").unwrap().energy_budget_ev_per_h,1e-8);
}
#[test]
fn impossible_budget_is_transactional(){
    let mut c=DriverConfig::baseline();c.end_zbar=19.8;c.background_panels=64;c.transport_cells=32;
    let (d,mut s)=Driver::new(c).unwrap();
    let old=s.clone();let mut count=0;
    assert!(d.chemical_stage_budgeted(&mut s,1e9,&mut count,1e-40).is_err());
    assert_eq!(s.gas.fractions,old.gas.fractions);
    assert_eq!(s.gas.w_erg_per_h,old.gas.w_erg_per_h);
    assert_eq!(s.photons,old.photons);
}
#[test]
fn mixed_budget_is_bounded_across_fine_paths() {
    let c=DriverConfig::read("energy_budget_ev_per_h=1e-8\nenergy_budget_count_fraction=0.75\nenergy_budget_count_cap=80000\nenergy_budget_chemical_fraction=0.25\nmax_steps=80000").unwrap();
    let (d,_)=Driver::new(c).unwrap();
    let a=1./21_f64;let b=0.2_f64;let n=80000;
    let mut sum=0.;
    for i in 0..n {
        let l=a*(b/a).powf(i as f64/n as f64);
        let r=a*(b/a).powf((i+1) as f64/n as f64);
        let m=(l*r).sqrt();
        sum+=d.tentative_energy_budget(l,m).unwrap().unwrap();
        sum+=d.tentative_energy_budget(m,r).unwrap().unwrap();
    }
    assert!((sum/1e-8-1.).abs()<3e-11);
    assert!(d.tentative_energy_budget(a,a*(1.+1e-10)).unwrap().unwrap()>4e-14);
    assert!(DriverConfig::read("energy_budget_ev_per_h=1e-8\nenergy_budget_count_fraction=0.75\nenergy_budget_count_cap=100\nmax_steps=101").is_err());
    assert!(DriverConfig::read("energy_budget_chemical_fraction=0").is_err());
}
