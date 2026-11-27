//! C3J shadow-only source-owned chemistry + spectral Newton on prescribed BASS geometry.
use rei_microphysics::{axbi_covariant_driver::{Driver,DriverConfig,DriverState,compiled_identity},general_history::{GeneralHistory,HistoryPoint},spectral_ff::{SpectralFf,blackbody_per_h}};
use std::{fs,io::{BufWriter,Write},path::Path};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args=std::env::args().skip(1).collect::<Vec<_>>();
 if args.len()!=5{return Err("config geometry out mode bins".into())}
 let mut cfg=DriverConfig::read(&fs::read_to_string(&args[0])?)?;
 let mode:u8=args[3].parse()?;let bins:usize=args[4].parse()?;cfg.ff_balance_mode=mode;
 if ![2,3].contains(&mode){return Err("mode".into())}
 let text=fs::read_to_string(&args[1])?;
 let mut points=Vec::new();
 for line in text.lines().skip(1){
  let v=line.split(',').map(str::parse::<f64>).collect::<Result<Vec<_>,_>>()?;
  points.push(HistoryPoint{a:v[0],h:v[2],f:std::array::from_fn(|i|std::array::from_fn(|j|v[8+3*i+j]))});
 }
 let mut dummy=points[0];dummy.a=points.last().unwrap().a;
 let (mut d,mut s)=Driver::new_general(cfg,GeneralHistory::new(vec![points[0],dummy],4,8)?)?;
 d.set_general_interval(points.clone())?;
 if mode==3{s.ff_spectrum=Some(SpectralFf::new(1e-10,60.,bins)?);}
 let out=Path::new(&args[2]);fs::create_dir(out)?;
 let mut f=BufWriter::new(fs::File::create(out.join("half.csv"))?);
 writeln!(f,"outer,half,a,T,xHII,xHeII,xHeIII,ne,primary,thermal,binding,spec,source_u,thermal_work,photon_work,escaped,cmb_input,FF_birth,FF_abs,photo_H,photo_HeI,photo_HeII,RR_H,RR_HeI,RR_HeII,CI_H,CI_HeI,CI_HeII,DR,boundary_u,residual,spec_step_residual,spec_work")?;
 let mut rhs=0usize;let mut max_spec=0_f64;let mut max_ledger=0_f64;
 let energy=|s:&DriverState|->Result<f64,Box<dyn std::error::Error>>{
  Ok(match &s.ff_spectrum{Some(p)=>p.energy(blackbody_per_h(2.7255/s.a,d.n_h0_cm3/s.a.powi(3))?)?,None=>0.})
 };
 let row=|f:&mut BufWriter<fs::File>,k:usize,j:usize,s:&DriverState,sr:f64,sw:f64|->Result<(),Box<dyn std::error::Error>>{
  let eos=s.gas.eos(d.n_h0_cm3/s.a.powi(3),d.n_he0_cm3/s.a.powi(3))?;
  let [w,b]=d.gas_energy_components(s)?;let l=&s.ledgers;
  write!(f,"{k},{j},{:.17e},{:.17e}",s.a,eos.temperature_k)?;
  for z in s.gas.fractions.into_iter().chain([eos.electron_density_cm3,d.general_moments(s)?.energy,w,b,energy(s)?,l.source_u,l.thermal_work,l.photon_work,l.escaped_u,l.cmb_input,s.cooling_ev[7],s.ff_abs_ev]).chain(l.photo_events).chain(l.rr_events).chain(l.ci_events).chain([l.dr_events,l.boundary_u,d.residuals(s)?.1,sr,sw]){
   write!(f,",{z:.17e}")?;
  }
  writeln!(f)?;Ok(())
 };
 row(&mut f,0,0,&s,0.,0.)?;
 // Invalid trial must not modify accepted input. Rust borrows it immutably; check state representation too.
 let before=s.gas.w_erg_per_h.to_bits();assert!(d.c3j_trial_split(&s,s.a,&mut rhs).is_err());assert_eq!(before,s.gas.w_erg_per_h.to_bits());
 for (k,p) in points.iter().enumerate().skip(1){
  let oldw=s.gas.w_erg_per_h.to_bits();let oldf=s.gas.fractions.map(f64::to_bits);let oldsp=s.ff_spectrum.as_ref().map(|p|p.distortion().to_vec());
  let (first,fine,_)=d.c3j_trial_split(&s,p.a,&mut rhs)?;
  assert_eq!(oldw,s.gas.w_erg_per_h.to_bits());assert_eq!(oldf,s.gas.fractions.map(f64::to_bits));
  assert_eq!(oldsp.as_deref(),s.ff_spectrum.as_ref().map(|p|p.distortion()));
  for (j,(a,b)) in [(&s,&first),(&first,&fine)].into_iter().enumerate(){
   let ua=energy(a)?;let ub=energy(b)?;let r=a.a/b.a;
   let q=b.cooling_ev[7]-a.cooling_ev[7]-(b.ledgers.cmb_input-a.ledgers.cmb_input);
   let work=(1.-r)*ua+(1.-r.sqrt())*q;let defect=if mode==3{ub-ua+work-q}else{0.};
   max_spec=max_spec.max(defect.abs());max_ledger=max_ledger.max(d.residuals(b)?.1.abs());
   if mode==3&&defect.abs()>1e-14{return Err(format!("spectral ledger {defect:e}").into())}
   row(&mut f,k,j+1,b,defect,if mode==3{work}else{0.})?;
  }
  s=fine;
  if k%100==0{println!("accepted {k} rhs {rhs}");}
 }
 f.flush()?;let eos=s.gas.eos(d.n_h0_cm3/s.a.powi(3),d.n_he0_cm3/s.a.powi(3))?;
 if let Some(p)=&s.ff_spectrum{
  let mut z=BufWriter::new(fs::File::create(out.join("spectrum.csv"))?);writeln!(z,"x,delta")?;
  for (x,y) in p.nodes().iter().zip(p.distortion()){writeln!(z,"{x:.17e},{y:.17e}")?;}
 }
 fs::write(out.join("source.txt"),compiled_identity())?;
 fs::write(out.join("RETURN.txt"),format!("status=COMPLETE\nmode={mode}\nbins={bins}\naccepted={}\nrhs={rhs}\nT={:.17e}\nmax_native_ledger={max_ledger:.17e}\nmax_spectral_ledger={max_spec:.17e}\n",s.accepted,eos.temperature_k))?;
 println!("COMPLETE mode={mode} bins={bins} accepted={} T={} spec={max_spec:e}",s.accepted,eos.temperature_k);Ok(())
}
