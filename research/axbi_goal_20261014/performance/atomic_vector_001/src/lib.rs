pub mod candidate_igm_thermal;
pub mod candidate_axbi_rates;
pub mod photon_kernel;
use rei_microphysics::{axbi_rates::{AxbiPoint,AxbiProvider},igm_state::IgmGasState,igm_thermal::IgmPhotoInput,AtomicProvider,Absorber,axbi_sources::AxbiSource};
use std::{sync::atomic::{AtomicU64,Ordering},hint::black_box,time::Instant};
pub static POINTS:AtomicU64=AtomicU64::new(0);pub static CELLS:AtomicU64=AtomicU64::new(0);
fn reserve(counter:&AtomicU64,n:u64,max:u64){counter.fetch_update(Ordering::SeqCst,Ordering::SeqCst,|v|v.checked_add(n).filter(|&w|w<=max)).expect("cumulative quota exceeded before call");}
pub fn bits(p:&AxbiPoint)->Vec<(&'static str,u64)>{let mut b=vec![("temperature_k",p.temperature_k.to_bits())];
for v in p.rates.ci_cm3_s{b.push(("rates.ci_cm3_s",v.to_bits()));}
for v in p.rates.rr_cm3_s{b.push(("rates.rr_cm3_s",v.to_bits()));}
b.push(("rates.dr_cm3_s",p.rates.dr_cm3_s.to_bits()));
for v in p.rates.ce_erg{b.push(("rates.ce_erg",v.to_bits()));}
for v in p.rates.rr_cooling_erg_cm3_s{b.push(("rates.rr_cooling_erg_cm3_s",v.to_bits()));}
b.push(("rates.dr_cooling_erg_cm3_s",p.rates.dr_cooling_erg_cm3_s.to_bits()));
b.push(("rates.dr_raw_cooling_erg_cm3_s",p.rates.dr_raw_cooling_erg_cm3_s.to_bits()));
b.push(("rates.freefree_erg_cm3_s",p.rates.freefree_erg_cm3_s.to_bits()));
for v in p.rates.diagnostics.ci_floor_cm3_s{b.push(("rates.diagnostics.ci_floor_cm3_s",v.to_bits()));}
for v in p.rates.diagnostics.ce_cap_erg{b.push(("rates.diagnostics.ce_cap_erg",v.to_bits()));}
b.push(("rates.diagnostics.dr_excluded_erg_cm3_s",p.rates.diagnostics.dr_excluded_erg_cm3_s.to_bits()));
b.push(("rates.diagnostics.dr_low_branch",p.rates.diagnostics.dr_low_branch as u64));
for v in p.rhs.fraction_dt{b.push(("rhs.fraction_dt",v.to_bits()));}
for v in p.rhs.species_chemical_cm3_s{b.push(("rhs.species_chemical_cm3_s",v.to_bits()));}
b.push(("rhs.w_dt_erg_per_h_s",p.rhs.w_dt_erg_per_h_s.to_bits()));
b.push(("rhs.temperature_dt_k_s",p.rhs.temperature_dt_k_s.to_bits()));
for v in p.rhs.photo_events_cm3_s{b.push(("rhs.photo_events_cm3_s",v.to_bits()));}
for v in p.rhs.ci_events_cm3_s{b.push(("rhs.ci_events_cm3_s",v.to_bits()));}
for v in p.rhs.rr_events_cm3_s{b.push(("rhs.rr_events_cm3_s",v.to_bits()));}
b.push(("rhs.dr_events_cm3_s",p.rhs.dr_events_cm3_s.to_bits()));
for v in p.rhs.ci_thermal_sink_erg_cm3_s{b.push(("rhs.ci_thermal_sink_erg_cm3_s",v.to_bits()));}
for v in p.rhs.rr_thermal_sink_erg_cm3_s{b.push(("rhs.rr_thermal_sink_erg_cm3_s",v.to_bits()));}
b.push(("rhs.dr_thermal_sink_erg_cm3_s",p.rhs.dr_thermal_sink_erg_cm3_s.to_bits()));
for v in p.rhs.ce_thermal_sink_erg_cm3_s{b.push(("rhs.ce_thermal_sink_erg_cm3_s",v.to_bits()));}
b.push(("rhs.freefree_thermal_sink_erg_cm3_s",p.rhs.freefree_thermal_sink_erg_cm3_s.to_bits()));
b.push(("rhs.thermal_micro_erg_cm3_s",p.rhs.thermal_micro_erg_cm3_s.to_bits()));
b.push(("rhs.binding_micro_erg_cm3_s",p.rhs.binding_micro_erg_cm3_s.to_bits()));
b.push(("rhs.escape_erg_cm3_s",p.rhs.escape_erg_cm3_s.to_bits()));
b.push(("rhs.cmb_to_gas_erg_cm3_s",p.rhs.cmb_to_gas_erg_cm3_s.to_bits()));
b.push(("rhs.photo_input_erg_cm3_s",p.rhs.photo_input_erg_cm3_s.to_bits()));
b.push(("rhs.expansion_work_erg_cm3_s",p.rhs.expansion_work_erg_cm3_s.to_bits()));
for v in p.rhs.ci_floor_events_cm3_s{b.push(("rhs.ci_floor_events_cm3_s",v.to_bits()));}
for v in p.rhs.ce_cap_cooling_erg_cm3_s{b.push(("rhs.ce_cap_cooling_erg_cm3_s",v.to_bits()));}
b.push(("rhs.excluded_dr_cooling_erg_cm3_s",p.rhs.excluded_dr_cooling_erg_cm3_s.to_bits()));
b}
#[derive(Clone,Copy,Debug)]
pub struct PointInput{pub gas:IgmGasState,pub nh:f64,pub nhe:f64,pub h:f64,pub tcmb:f64,pub photo:IgmPhotoInput}
pub fn eval(a:&PointInput,candidate:bool)->Result<AxbiPoint,rei_microphysics::ForwardError>{reserve(&POINTS,1,250000);if candidate{candidate_axbi_rates::point(&a.gas,a.nh,a.nhe,a.h,a.tcmb,a.photo)}else{AxbiProvider.point(&a.gas,a.nh,a.nhe,a.h,a.tcmb,a.photo)}}
pub fn point_parity(a:&PointInput){let before=format!("{:?}",a);let x=eval(a,false);let y=eval(a,true);match (&x,&y){(Ok(x),Ok(y))=>{assert_eq!(x.provider_id,y.provider_id);let xb=bits(x);let yb=bits(y);assert_eq!(xb.len(),yb.len());println!("point_parity input={a:?} bits={xb:?}");for (i,(u,v)) in xb.iter().zip(&yb).enumerate(){assert_eq!(u,v,"point first field {} index {} input {:?} original {:?} candidate {:?}",u.0,i,a,x,y);}},(Err(x),Err(y))=>{println!("point_error input={a:?} original={x:?} candidate={y:?}");assert_eq!(format!("{:?}",x),format!("{:?}",y),"input {:?}",a)},_=>panic!("point mismatch input {:?} original {:?} candidate {:?}",a,x,y)}assert_eq!(before,format!("{:?}",a));}
pub fn photo_eval(a:&photon_kernel::Input,candidate:bool)->Result<(Vec<f64>,IgmPhotoInput),rei_microphysics::ForwardError>{reserve(&CELLS,a.stocks.len() as u64,50000000);if candidate{photon_kernel::hoisted(a)}else{photon_kernel::reference(a)}}
pub fn photo_parity(a:&photon_kernel::Input)->Option<IgmPhotoInput>{let x=photo_eval(a,false);let y=photo_eval(a,true);match (x,y){(Ok((x,p)),Ok((y,q)))=>{assert_eq!(x.len(),y.len());println!("photon_parity energies_bits={:?} absorbers_bits={:?} dt_bits={} input_stock_bits={:?} output_stock_bits={:?} gamma_bits={:?} heat_bits={:?}",a.energies.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),a.absorbers.map(f64::to_bits),a.dt.to_bits(),a.stocks.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),x.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),p.gamma_s.map(f64::to_bits),p.heat_erg_per_absorber_s.map(f64::to_bits));for (j,(x,y)) in x.iter().zip(&y).enumerate(){assert_eq!(x.to_bits(),y.to_bits(),"stock {} input {:?}",j,a);assert!(x.is_finite()&&*x>=0.0);}for k in 0..3{assert_eq!(p.gamma_s[k].to_bits(),q.gamma_s[k].to_bits(),"gamma {} input {:?}",k,a);assert_eq!(p.heat_erg_per_absorber_s[k].to_bits(),q.heat_erg_per_absorber_s[k].to_bits(),"heat {} input {:?}",k,a);assert!(p.gamma_s[k].is_finite()&&p.gamma_s[k]>=0.0&&p.heat_erg_per_absorber_s[k].is_finite()&&p.heat_erg_per_absorber_s[k]>=0.0);}Some(p)},(Err(x),Err(y))=>{assert_eq!(format!("{:?}",x),format!("{:?}",y),"input {:?}",a);None},(x,y)=>panic!("photon mismatch input {:?} original {:?} candidate {:?}",a,x,y)}}
pub fn point_matrix()->Vec<PointInput>{let mut temps:Vec<f64>=(0..257).map(|i|10f64.powf(6.0*i as f64/256.0)).collect();for t in [5500f64,9284.0,118348.0/69.07755278982137,13179.0/69.07755278982137,473638.0/69.07755278982137]{temps.extend([f64::from_bits(t.to_bits()-1),t,f64::from_bits(t.to_bits()+1)]);}let mut v=Vec::new();for t in temps{for f in [[0.,0.,0.],[2e-4,1e-5,1e-8],[0.5,0.25,0.25],[1.,0.,1.]]{for nh in [1e-4,1.]{for (p,tcmb) in [(IgmPhotoInput::default(),2.7255),(IgmPhotoInput{gamma_s:[1e-14,2e-14,3e-14],heat_erg_per_absorber_s:[1e-26,2e-26,3e-26]},100.),(IgmPhotoInput{gamma_s:[1e-14,2e-14,3e-14],heat_erg_per_absorber_s:[1e-26,2e-26,3e-26]},1e5)]{v.push(PointInput{gas:IgmGasState::from_temperature(f,nh,0.08*nh,t).unwrap(),nh,nhe:0.08*nh,h:0.,tcmb,photo:p});}}}}v}
pub fn photon_input(sub:usize,angles:usize)->photon_kernel::Input{let src=AxbiSource::new(1e-4,0.2,sub,angles).unwrap();let energies:Vec<f64>=std::iter::once(13.6).chain(src.spectral_cells.iter().map(|c|c.upper_ev)).collect();let signatures=energies.iter().map(|&e|[Absorber::HI,Absorber::HeI,Absorber::HeII].map(|a|AtomicProvider::reference().cross_section(a,e).unwrap())).collect();let stocks=(0..energies.len()*angles).map(|j|(j%17) as f64*1e-4).collect();photon_kernel::Input{energies,signatures,stocks,absorbers:[1e-4,8e-6,0.],nh:1e-4,dt:1e10}}
pub fn validation()->(u64,u64,Vec<f64>){let p0=POINTS.load(Ordering::SeqCst);let c0=CELLS.load(Ordering::SeqCst);let matrix=point_matrix();for a in &matrix{point_parity(a);}let base=matrix[300];let mut extras=Vec::new();let mut x=base;x.gas=IgmGasState::from_temperature([0.5,0.,0.],x.nh,0.,1e4).unwrap();x.nhe=0.;extras.push(x);x=base;x.h=1e-17;extras.push(x);for value in [-1.,f64::NAN,f64::INFINITY]{x=base;x.photo.gamma_s[0]=value;extras.push(x);x=base;x.photo.heat_erg_per_absorber_s[0]=value;extras.push(x);x=base;x.nh=value;extras.push(x);x=base;x.h=value;extras.push(x);x=base;x.tcmb=value;extras.push(x);x=base;x.gas.w_erg_per_h=value;extras.push(x);}x=base;x.photo.gamma_s[0]=0.;x.photo.heat_erg_per_absorber_s[0]=1.;extras.push(x);x=base;x.gas.fractions=[2.,0.,0.];extras.push(x);x.photo.gamma_s[0]=f64::NAN;x.h=-1.;extras.push(x);x=base;x.h=-1.;x.tcmb=f64::NAN;x.photo.gamma_s[0]=f64::NAN;extras.push(x);for a in extras{point_parity(&a);}let mut residuals=Vec::new();let mut combined=0;for sub in [16,32]{for angles in [8,16]{let template=photon_input(sub,angles);for stocks_mode in 0..7{for absorbers in [[1e-4,8e-6,0.],[5e-5,4e-6,2e-6],[0.,0.,0.]]{for dt in [0.,1.,1e10,1e14]{let mut a=template.clone();a.absorbers=absorbers;a.dt=dt;if stocks_mode==0{a.stocks.fill(0.);}else if stocks_mode<=3{a.stocks.fill(0.);let index=(stocks_mode-1)*sub;a.stocks[index]=0.01;}else if stocks_mode==4{a.stocks.fill(0.);a.stocks[a.energies.len()-1]=0.01;}else if stocks_mode==6{a.stocks.truncate(a.stocks.len()-3);}if let Some(photo)=photo_parity(&a){let loss=a.stocks.iter().zip(photo_eval(&a,false).unwrap().0).map(|(x,y)|x-y).sum::<f64>();let rhs=dt*(0..3).map(|k|a.absorbers[k]*photo.gamma_s[k]).sum::<f64>()/a.nh;let scale=a.stocks.iter().sum::<f64>().max(1.0);let residual=(loss-rhs).abs()/scale;assert!(residual<=1e-10,"photon count residual {} loss {} expected {} normalization {} input {:?}",residual,loss,rhs,scale,a);residuals.push(residual);if combined<24&&dt>0.&&stocks_mode>0{let mut p=base;p.photo=photo;point_parity(&p);combined+=1;}}}}}let mut a=template.clone();a.stocks[0]=f64::NAN;photo_parity(&a);a=template;a.energies[0]=1.;a.signatures[0][0]=1e-18;photo_parity(&a);}}assert!(combined>=24);(POINTS.load(Ordering::SeqCst)-p0,CELLS.load(Ordering::SeqCst)-c0,residuals)}
fn cpu_ticks()->u64{let s=std::fs::read_to_string("/proc/self/stat").unwrap();let v:Vec<_>=s.rsplit_once(") ").unwrap().1.split_whitespace().collect();v[11].parse::<u64>().unwrap()+v[12].parse::<u64>().unwrap()}
pub fn timed<F:FnMut()>(mut f:F)->(f64,u64){let c=cpu_ticks();let now=Instant::now();f();(now.elapsed().as_secs_f64(),cpu_ticks()-c)}
fn mix(sum:u64,value:u64)->u64{sum.rotate_left(7)^value}
pub fn benchmark()->String{
 let setup=Instant::now();let points:Vec<_>=point_matrix().into_iter().filter(|a|eval(a,false).is_ok()).step_by(100).take(32).collect();let photon=photon_input(32,16);let setup_s=setup.elapsed().as_secs_f64();let mut rows=Vec::new();
 for repetition in 0..3{let mut point_check=None;let mut photo_check=None;for candidate in [false,true]{let mut checksum=0;let (wall,cpu)=timed(||{for _ in 0..500{for a in &points{let out=black_box(eval(black_box(a),candidate).unwrap());for (_,v) in bits(&out){checksum=mix(checksum,v);}}}});if let Some(x)=point_check{assert_eq!(checksum,x);}else{point_check=Some(checksum);}rows.push(format!("{{\"kind\":\"point\",\"candidate\":{},\"repetition\":{},\"workers\":1,\"work_items\":{},\"wall_s\":{},\"process_cpu_ticks\":{},\"checksum\":{}}}",candidate,repetition,points.len()*500,wall,cpu,checksum));
 let mut checksum=0;let (wall,cpu)=timed(||{for _ in 0..1000{let (stocks,photo)=black_box(photo_eval(black_box(&photon),candidate).unwrap());for v in stocks.into_iter().chain(photo.gamma_s).chain(photo.heat_erg_per_absorber_s){checksum=mix(checksum,v.to_bits());}}});if let Some(x)=photo_check{assert_eq!(checksum,x);}else{photo_check=Some(checksum);}rows.push(format!("{{\"kind\":\"photon\",\"candidate\":{},\"repetition\":{},\"workers\":1,\"work_items\":1000,\"wall_s\":{},\"process_cpu_ticks\":{},\"checksum\":{}}}",candidate,repetition,wall,cpu,checksum));}}
 format!("{{\"setup_wall_s\":{},\"setup_included\":true,\"checksum_overhead_included\":true,\"per_call_factor_construction_included\":true,\"two_worker_throughput\":\"NOT_MEASURED_OPTIONAL_VARIANT_OMITTED\",\"block8\":\"NOT_IMPLEMENTED_OPTIONAL_VARIANT\",\"timings\":[{}]}}",setup_s,rows.join(","))}
