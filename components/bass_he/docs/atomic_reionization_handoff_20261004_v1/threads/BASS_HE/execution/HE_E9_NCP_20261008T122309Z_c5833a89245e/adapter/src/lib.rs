pub fn clock(c:&rei_microphysics::igm_config::HistoryConfig,k:usize)->Result<f64,String>{if k>384{return Err("N384_INDEX".into())}let s=c.start+c.max_dln_a*(k as f64/16.0)/24.0;if !s.is_finite(){return Err("NONFINITE_CLOCK".into())}Ok(s)}
#[cfg(test)] mod tests {
use super::*;
fn cfg()->rei_microphysics::igm_config::HistoryConfig {rei_microphysics::igm_config::parse_config(include_str!("../common_domain.cfg")).unwrap()}
#[test]fn exact_e7_lattice_and_coarse_identity(){let c=cfg();for k in 0..=384{let s=clock(&c,k).unwrap();assert_eq!(s.to_bits(),(c.start+c.max_dln_a*(k as f64/16.0)/24.0).to_bits());if k%2==0{assert_eq!(s.to_bits(),short_hhe_control::radiation::time_at(&c,k/2,192).to_bits());}}}
#[test]fn rejects_out_of_domain(){assert!(clock(&cfg(),385).is_err());}
#[test]fn native_row_readout_does_not_mutate_state(){let c=cfg();let g=short_hhe_control::radiation::Grid::new(&c,512,4).unwrap();let s=short_hhe_control::coupled::State::new(&c,&g).unwrap();let old=s.clone();let p=c.background.at_ln_a(c.start).unwrap();let initial=s.y[3]+short_hhe_control::material::binding(s.y,p.n_he_cm3/p.n_h_cm3);let row=short_hhe_control::output::row(&c,&g,&s,initial).unwrap();assert_eq!(row.len(),41);assert_eq!(s,old);}
}
