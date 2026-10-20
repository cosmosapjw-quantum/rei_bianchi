//! Evaluate retained manufactured point inputs, without integrating a trajectory.
//! The conditioning denominator is an f64 sum of magnitudes of elementary
//! native source terms. It is a point diagnostic, not an interval error bound.
use rei_iso_couple_reference::{HHeModel,
    cubic_igm::{CubicIgmTable,source_id_hex},
    deuterium_atomic::{DAtomicProvider,DChargeExchange,d_atomic_rhs_from_prepared},
    full_network::{FullState,NetworkConfig,EV_J},
    gas_reference_rhs::{GasRates,gas_rates_with_backend},
    isotope_state::{IsotopeNumberState,IsotopeSpecies as S},mixture_eos::MixtureState,
    rate_table::{IgmRateBackend,IgmRateTable}};
use std::{io::{self,BufRead,Write},sync::Arc};
fn vector(q:GasRates)->[f64;28]{let mut a=[0.0;28];a[..27].copy_from_slice(&q.vector());a[27]=q.chemical;a}
fn denominator(s:&FullState,c:&NetworkConfig,q:GasRates)->Result<[f64;28],String>{
    let eos=s.gas.eos().map_err(|e|format!("EOS {e:?}"))?;let t=eos.temperature_k;
    let p=IgmRateBackend::Direct.prepare(t).map_err(|e|format!("prepare {e:?}"))?;
    let rates=p.rates();let n=|sp|s.gas.nuclei.density_m3(sp);let ne=eos.free_electrons_m3*1e-6;
    let photo=c.deuterium.photo_input_from_bound_rates(0.0,0.0,c.photon_source).map_err(|e|format!("photo {e:?}"))?;
    let d=d_atomic_rhs_from_prepared(c.deuterium,&s.gas.nuclei,t,&photo,DChargeExchange::Savin2002,&p,&IgmRateBackend::Direct).map_err(|e|format!("D {e:?}"))?;
    let cx=d.cx_forward_events_m3_s+d.cx_reverse_events_m3_s;
    let mut a=[0.0;28];
    a[S::H1Neutral as usize]=q.ci[0]+q.rr[0]+cx;a[S::H1Ionized as usize]=a[S::H1Neutral as usize];
    a[S::DNeutral as usize]=q.ci[3]+q.rr[3]+cx;a[S::DIonized as usize]=a[S::DNeutral as usize];
    a[S::He4Neutral as usize]=q.ci[1]+q.rr[1]+q.dr;
    a[S::He4SinglyIonized as usize]=q.ci[1]+q.rr[1]+q.ci[2]+q.rr[2]+q.dr;
    a[S::He4DoublyIonized as usize]=q.ci[2]+q.rr[2];
    let chi=HHeModel::controlled_fixture().threshold_ev;
    for(j,ion)in[S::H1Ionized,S::He4SinglyIonized,S::He4DoublyIonized].into_iter().enumerate(){
        let rr_kin=ne*(n(ion)*1e-6)*rates.rr_cooling_erg_cm3_s[j]*0.1;
        a[13]+=chi[j]*EV_J*q.ci[j]+rr_kin;
        a[27]+=chi[j]*EV_J*(q.ci[j]+q.rr[j]);
    }
    let dr_kin=ne*(n(S::He4SinglyIonized)*1e-6)*rates.dr_cooling_erg_cm3_s*0.1;
    let ce=0.1*(ne*n(S::H1Neutral)*1e-6*rates.ce_erg[0]
        +ne*ne*n(S::He4SinglyIonized)*1e-6*rates.ce_erg[1]
        +ne*n(S::He4SinglyIonized)*1e-6*rates.ce_erg[2]);
    a[13]+=dr_kin+ce+q.ff+q.cmb.abs();a[27]+=chi[1]*EV_J*q.dr;
    for channel in &d.channel_energy[1..]{a[13]+=channel.thermal.abs();a[27]+=channel.chemical.abs();}
    a[14]=q.escape.abs();a[15]=q.cmb.abs();
    for j in 0..4{a[16+j]=q.ci[j];a[20+j]=q.rr[j];}
    a[24]=q.dr;a[25]=cx;a[26]=q.ff;
    if a.iter().any(|x|!x.is_finite()||*x<0.0){return Err("invalid denominator".into());}
    Ok(a)
}
fn run()->Result<(),String>{
    let direct=IgmRateBackend::Direct;
    let loglinear=IgmRateBackend::Table(Arc::new(IgmRateTable::build_default().map_err(|e|format!("loglinear {e:?}"))?));
    let cubic=IgmRateBackend::Cubic(Arc::new(CubicIgmTable::build_default().map_err(|e|format!("cubic {e:?}"))?));
    let h=HHeModel::controlled_fixture().threshold_ev[0];
    let mut c=NetworkConfig::source_bound(DAtomicProvider::new(h,h+0.0037,"MANUFACTURED_D_H_DELTA_CHI").map_err(|e|format!("provider {e:?}"))?,"MD14_Z002_FESC_BB50K_13P6_100_V1");
    c.use_photo=false;
    let mut out=io::BufWriter::new(io::stdout().lock());
    writeln!(out,"{{\"schema\":\"REI_RUN19_GAS_CONDITIONING_V1\",\"cubic_source_id\":\"{}\"}}",source_id_hex()).map_err(|e|e.to_string())?;out.flush().map_err(|e|e.to_string())?;
    for(index,line)in io::stdin().lock().lines().enumerate(){
        let line=line.map_err(|e|e.to_string())?;if line=="QUIT"{break;}
        let mut words=line.split_whitespace();if words.next()!=Some("RHS"){return Err("expected RHS".into());}
        let values=words.map(|s|s.parse::<f64>().map_err(|_|"invalid number".to_string())).collect::<Result<Vec<_>,_>>()?;
        if values.len()!=16||values[0]!=7.0||values.iter().any(|v|!v.is_finite()){return Err("expected finite mask7 input".into());}
        c.cmb_temperature_k=values[1];let mut n=[0.0;13];n.copy_from_slice(&values[2..15]);
        let s=FullState{gas:MixtureState{nuclei:IsotopeNumberState::new(n).map_err(|e|format!("state {e:?}"))?,thermal_j_m3:values[15]},photon_bins:Vec::new(),escaped_j_m3:0.0,cmb_reservoir_j_m3:0.0,elapsed_s:0.0};
        let q=gas_rates_with_backend(&s,&c,7,&direct).map_err(|e|format!("Direct {e:?}"))?;
        let l=gas_rates_with_backend(&s,&c,7,&loglinear).map_err(|e|format!("loglinear {e:?}"))?;
        let cu=gas_rates_with_backend(&s,&c,7,&cubic).map_err(|e|format!("cubic {e:?}"))?;
        let sum=denominator(&s,&c,q)?;let t=s.gas.eos().map_err(|e|format!("EOS {e:?}"))?.temperature_k;
        writeln!(out,"{{\"index\":{index},\"temperature_k\":{t:.17e},\"direct\":{:?},\"loglinear\":{:?},\"cubic\":{:?},\"sum_abs_flux\":{:?},\"ledger_residuals\":{:?}}}",vector(q),vector(l),vector(cu),sum,[q.residual(),l.residual(),cu.residual()]).map_err(|e|e.to_string())?;
        out.flush().map_err(|e|e.to_string())?;
    }
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("{e}");std::process::exit(2);}}
