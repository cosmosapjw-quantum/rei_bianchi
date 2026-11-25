use rei_microphysics::axbi_covariant_driver::{Driver,DriverConfig};
#[test]
fn original_fixed_q_driver_live_cold_source_has_no_redshift_remap(){
 let mut c=DriverConfig::read("initial_x_hii=0.00021014665671400957\ninitial_temperature_k=9.304371943681256\nend_zbar=19.98\ntransport_cells=32\nbackground_panels=64\nlocal_target=0.00008\ninactive_hi_split=true\ninitial_state_id=REC_HMLA_TEST\n").unwrap();
 c.max_steps=10000;
 let(d,mut s)=Driver::new(c).unwrap();
 let a0=s.a;
 for i in 0..d.source.angular_cells.len(){ d.seed_delta(&mut s,i,13.6,1e-8*d.source.angular_cells[i].count_fraction).unwrap(); }
 s.ledgers.source_n=1e-8;s.ledgers.source_u=13.6e-8;
 d.geometry_map(&mut s,a0*1.0001).unwrap();
 let p=d.photon_pool_inventory(&s).unwrap();
 assert_eq!(p[0],0.);
 assert!((p[2]-1e-8).abs()<1e-20);
 let mut rhs=0;
 d.chemical_stage(&mut s,1e5,&mut rhs).unwrap();
 assert_eq!(s.ledgers.photo_events,[0.;3]);
 assert!(d.config.initial_state_id.starts_with("REC_HMLA_"));
 d.validate(&s,1e-8).unwrap();
}
