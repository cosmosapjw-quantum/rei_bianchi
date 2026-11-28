
#[cfg(test)]mod energy06c_tests {
 use super::*;
 #[test]fn wrong_clock_rejected(){assert!(!contract_valid(0.0,1.0,"ON06G","original","128x33"));}
 #[test]fn wrong_origin_rejected(){assert!(!contract_valid(1.6e11,1.0,"ENERGY05","original","128x33"));}
 #[test]fn wrong_birth_law_rejected(){assert!(!contract_valid(1.6e11,1.0,"ON06G","forced_same_measure","128x33"));}
 #[test]fn unsupported_lambda_rejected(){assert!(!contract_valid(1.6e11,0.5,"ON06G","original","128x33"));}
 #[test]fn wrong_angle_rejected(){assert!(!contract_valid(1.6e11,1.0,"ON06G","original","aggregate"));}
 #[test]fn full_diagnostic_never_added_to_accepted_events(){assert_eq!(accepted_events(100.0,2.0,3.0),5.0);}
 #[test]fn incoming_tangent_is_not_reset(){assert_eq!(carry_rhs(11.0,2.0,3.0,5.0),21.0);}
}
#[cfg(test)]mod actual_input_tests {
 use super::*;
 fn original(member:usize)->(HhRunConfig,HhPairedState){let c=cfg(member).unwrap();let b=std::fs::read(std::path::Path::new(&std::env::var("HH_SEED").unwrap()).join(format!("member{member}.bin"))).unwrap();let s=hh_checkpoint_decode(&c,&b).unwrap();(c,s)}
 #[test]fn original_direction_state_prebirth_boxes_contain_points(){for m in 0..4{let(c,s)=original(m);let n=energy_nodes(c.grid()).unwrap();let b=prepare_actual_birth(c.grid(),c.hubble(),s.base(),1.25e9,&n).unwrap();assert_eq!(b.photons.len(),4224);assert!(b.photons.iter().zip(b.boxes).all(|(x,i)|contains(i,*x)));assert!(b.groups.iter().zip(b.group_boxes).all(|(x,i)|contains(i,*x)));}}
 #[test]fn real_schedule_distinct_birth_nodes_same_binary64_total(){let sc=schemes(1.6e11,1.25e9).unwrap();assert_ne!(sc[0].times[0],sc[1].times[0]);assert_eq!((sc[0].steps[0]*SOURCE).to_bits(),(2.0*(sc[1].steps[0]*SOURCE)).to_bits());}
 #[test]fn source_weights_at_half_nodes_keep_actual_direction_identity(){let(c,s)=original(3);let(a,_)=source_weights(c.grid(),c.hubble(),s.base.time_s+6.25e8).unwrap();let(b,_)=source_weights(c.grid(),c.hubble(),s.base.time_s+1.25e9).unwrap();assert_eq!(a.len(),128);assert_ne!(a,b);assert!((a.iter().sum::<f64>()-1.0).abs()<1e-14);}
 #[test]fn birth_added_before_be_in_source_only_transformed_fixture(){let(c,s)=original(1);let mut b=s.base.clone();b.photons.fill(0.0);b.photon_boxes.fill(p(0.0).unwrap());b.lower_guard_n.fill(0.0);b.lower_guard_u.fill(0.0);b.lower_guard_n_box.fill(p(0.0).unwrap());b.lower_guard_u_box.fill(p(0.0).unwrap());let n=energy_nodes(c.grid()).unwrap();let out=prepare_actual_birth(c.grid(),c.hubble(),&b,1.25e9,&n).unwrap();assert_eq!(out.transport_n,0.0);assert!(out.photons.iter().enumerate().all(|(i,x)|if i%33==24{*x==out.source_n*out.weights[i/33]}else{*x==0.0}));}
 #[test]fn unsupported_parameter_family_cannot_dispatch_or_retry(){assert!(scientific_dispatch_requested().is_err());assert!(scientific_dispatch_requested().is_err());}
 #[test]fn native_point_is_not_promoted_to_root_family_defect(){let d=enclosing_defect(&[Interval::new(1.0,2.0).unwrap()],&[Interval::new(3.0,4.0).unwrap()]).unwrap();assert!(d[0].lo<=1.0&&d[0].hi>=3.0);assert!(enclosing_defect(&[],&[]).is_err());}
 #[test]fn photon_tangent_energy_angle_correspondence_required(){let nodes=energy_nodes(&PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16}).unwrap();assert!(validate_tangent(&[0.0;4],&[0.0;4224],&nodes,128).is_ok());assert!(validate_tangent(&[0.0;4],&[0.0;33],&[0.0;33],1).is_err());assert!(validate_tangent(&[0.0;4],&[f64::NAN;4224],&[0.0;33],128).is_err());}
 #[test]fn no_new_owner_nuclei_or_hh_thermal_factor(){assert_eq!(CHI[0].to_bits(),13.598434599702_f64.to_bits());let _nuclei=FHE;assert_eq!(source_law().energy_bits,13.7_f64.to_bits());}
 #[test]fn nonfinite_prepare_dt_refused(){let(c,s)=original(1);let n=energy_nodes(c.grid()).unwrap();assert!(prepare_actual_birth(c.grid(),c.hubble(),s.base(),f64::NAN,&n).is_err());}
 #[test]fn threshold_singleton_and_one_sided_hat_preserve_owner_rules(){let n=energy_nodes(&PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16}).unwrap();let x=p(n[24]).unwrap();assert!(contains(hat_box(x,&n,24).unwrap(),1.0));let left=Interval::new(n[23],n[24]).unwrap();let b=hat_box(left,&n,24).unwrap();assert!(b.lo<=0.0&&b.hi>=1.0);}
}
#[cfg(test)]mod contraction_rounding_test {
 use super::*;
 #[test]fn row_norm_cannot_round_down_into_false_contraction(){let tiny=2.0_f64.powi(-55)*1.5;assert!(norm_upper([1.0-2.0_f64.powi(-53),tiny,tiny,tiny]).unwrap()>=1.0);}
}
#[cfg(test)]mod independent_review_regressions {
 use super::*;
 #[test]fn wrong_energy_bits_are_not_canonical_labels(){assert!(validate_tangent(&[0.0;4],&[0.0;4224],&[0.0;33],128).is_err());}
 #[test]fn swapped_prebe_nodes_rejected_before_source_preparation(){let c=cfg(1).unwrap();let bytes=std::fs::read(std::path::Path::new(&std::env::var("HH_SEED").unwrap()).join("member1.bin")).unwrap();let s=hh_checkpoint_decode(&c,&bytes).unwrap();let mut n=energy_nodes(c.grid()).unwrap();n.swap(0,1);assert!(prepare_actual_birth(c.grid(),c.hubble(),s.base(),1.25e9,&n).is_err());}
 #[test]fn canonical_zero_tangent_remap_is_supported(){let c=cfg(1).unwrap();let n=energy_nodes(c.grid()).unwrap();assert!(remap_lambda_fixed_theta(c.grid(),c.hubble(),1.6e11,1.25e9,&n,&[p(0.0).unwrap();4224],&[p(0.0).unwrap();128],&[p(0.0).unwrap();128]).is_ok());}
}
#[cfg(test)]mod guard_tangent_checks {
 use super::*;
 #[test]fn nonzero_incoming_guard_tangents_are_carried(){let c=cfg(3).unwrap();let n=energy_nodes(c.grid()).unwrap();let t=remap_lambda_fixed_theta(c.grid(),c.hubble(),1.6e11,1.25e9,&n,&[p(0.0).unwrap();4224],&[p(2.0).unwrap();128],&[p(3.0).unwrap();128]).unwrap();for d in 0..128{let q=qhat(c.grid(),d);let r=g_point(q,c.hubble(),1.6125e11)/g_point(q,c.hubble(),1.6e11);assert!(contains(t.guard_n[d],2.0));assert!(contains(t.guard_u[d],3.0*r));}}
 #[test]fn below_threshold_stock_derivative_exports_to_owned_guard(){let c=cfg(1).unwrap();let n=energy_nodes(c.grid()).unwrap();let mut incoming=vec![p(0.0).unwrap();4224];incoming[0]=p(1.0).unwrap();let t=remap_lambda_fixed_theta(c.grid(),c.hubble(),1.6e11,1.25e9,&n,&incoming,&[p(0.0).unwrap();128],&[p(0.0).unwrap();128]).unwrap();let q=qhat(c.grid(),0);let r=g_point(q,c.hubble(),1.6125e11)/g_point(q,c.hubble(),1.6e11);assert!(contains(t.guard_n[0],1.0));assert!(contains(t.guard_u[0],10.0*r));assert!(t.photons.iter().all(|x|contains(*x,0.0)));}
}
#[cfg(test)]mod signed_guard_review_checks {
 use super::*;
 #[test]fn invalid_incoming_guard_interval_refused(){let c=cfg(1).unwrap();let n=energy_nodes(c.grid()).unwrap();let mut gn=vec![p(0.0).unwrap();128];gn[0]=Interval{lo:2.0,hi:1.0};assert!(remap_lambda_fixed_theta(c.grid(),c.hubble(),1.6e11,1.25e9,&n,&[p(0.0).unwrap();4224],&gn,&[p(0.0).unwrap();128]).is_err());}
 #[test]fn negative_lower_export_preserves_signed_derivative(){let c=cfg(1).unwrap();let n=energy_nodes(c.grid()).unwrap();let mut incoming=vec![p(0.0).unwrap();4224];incoming[0]=p(-1.0).unwrap();let t=remap_lambda_fixed_theta(c.grid(),c.hubble(),1.6e11,1.25e9,&n,&incoming,&[p(0.0).unwrap();128],&[p(0.0).unwrap();128]).unwrap();let q=qhat(c.grid(),0);let r=g_point(q,c.hubble(),1.6125e11)/g_point(q,c.hubble(),1.6e11);assert!(contains(t.guard_n[0],-1.0));assert!(contains(t.guard_u[0],-10.0*r));}
 #[test]fn lower_threshold_straddling_hull_contains_both_signed_paths(){let c=PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16};let n=energy_nodes(&c).unwrap();let mut incoming=vec![p(0.0).unwrap();4224];incoming[0]=Interval::new(-2.0,3.0).unwrap();let t=remap_lambda_fixed_theta(&c,[0.0;3],1.6e11,1.25e9,&n,&incoming,&[p(0.0).unwrap();128],&[p(0.0).unwrap();128]).unwrap();assert!(contains(t.guard_n[0],-2.0)&&contains(t.guard_n[0],3.0));assert!(contains(t.guard_u[0],-20.0)&&contains(t.guard_u[0],30.0));assert!(contains(t.photons[0],-2.0)&&contains(t.photons[0],3.0));}
}
