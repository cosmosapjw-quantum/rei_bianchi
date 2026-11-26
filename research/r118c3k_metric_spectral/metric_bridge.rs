//! C3K experiment: native BASS geometry + live REI gas/primary/signed spectrum.
use bianchi_rustcore::kinetic::owned_thomson::{ThomsonOwner,ExternalMatter,ExternalContribution};
use bianchi_rustcore::kinetic::owned_vlasov::OwnedState;
use rei_microphysics::{axbi_covariant_driver::{Driver,DriverConfig,DriverState,compiled_identity},general_history::{GeneralHistory,HistoryPoint},spectral_ff::{SpectralFf,blackbody_per_h}};
use std::{fs,io::{BufWriter,Write},path::Path};
const H0:f64=2.1842852410855023e-18;
const RHO0:f64=3.*299792458.*299792458.*H0*H0/(8.*std::f64::consts::PI*6.67430e-11);
const EV:f64=1.602176634e-19;
fn map<T>(r:Result<T,rei_microphysics::ForwardError>)->Result<T,String>{r.map_err(|e|format!("{e:?}"))}
fn p(g:&OwnedState)->HistoryPoint{HistoryPoint{a:g.a,h:g.h,f:std::array::from_fn(|i|std::array::from_fn(|j|g.f[(i,j)]))}}
#[derive(Clone)]
struct State{gas:DriverState,cool:f64,spec:f64,work:f64,err:[f64;2]}
struct Coupler{d:Driver,feedback:bool,init:f64,rhs:usize,calls:usize}
impl Coupler{
 fn ledger(&self,s:&State)->Result<f64,String>{
  let u=map(self.d.general_moments(&s.gas))?.energy;
  let [w,b]=map(self.d.gas_energy_components(&s.gas))?;
  let l=&s.gas.ledgers;
  Ok(u+w+b+s.cool+s.spec-self.init-l.source_u+l.thermal_work+l.photon_work+l.boundary_u+s.work)
 }
 fn spec_energy(&self,s:&DriverState)->Result<f64,String>{match &s.ff_spectrum{Some(v)=>map(v.energy(map(blackbody_per_h(2.7255/s.a,self.d.n_h0_cm3/s.a.powi(3)))?)),None=>Ok(0.)}}
}
impl ExternalMatter for Coupler{
 type State=State;
 fn contribution(&mut self,s:&State,g:&OwnedState)->Result<ExternalContribution,String>{
  if s.gas.a!=g.a{return Err("clock".into())}
  let nh=self.d.n_h0_cm3/g.a.powi(3);let nhe=self.d.n_he0_cm3/g.a.powi(3);let ne=map(s.gas.gas.eos(nh,nhe))?.electron_density_cm3*1e6;
  if !self.feedback{return Ok(ExternalContribution{rho:0.,pressure:[[0.;3];3],photon_rho:0.,ne_m3:ne})}
  let m=map(self.d.general_moments(&s.gas))?;let [w,b]=map(self.d.gas_energy_components(&s.gas))?;
  let fac=nh*1e6*EV/RHO0;let sec=s.cool+s.spec;
  let rho=fac*(m.energy+w+b-self.init-s.gas.ledgers.source_u+sec);
  let pressure=std::array::from_fn(|i|std::array::from_fn(|j|fac*(m.pressure[i][j]+if i==j{(2.*w+sec)/3.}else{0.})));
  Ok(ExternalContribution{rho,pressure,photon_rho:fac*(m.energy+sec),ne_m3:ne})
 }
 fn advance(&mut self,s:&State,old:&OwnedState,mid:&OwnedState,end:&OwnedState)->Result<State,String>{
  self.calls+=1;
  if self.calls>50000{return Err("stage cap".into())}
  map(self.d.set_general_interval(vec![p(old),p(mid),p(end)]))?;
  let (first,fine,_,err)=map(self.d.c3j_trial_split(&s.gas,end.a,&mut self.rhs))?;
  let mut cool=s.cool;let mut spec=s.spec;let mut work=s.work;
  for (a,b) in [(&s.gas,&first),(&first,&fine)]{
   let r=a.a/b.a;
   let ff=b.cooling_ev[7]-a.cooling_ev[7];
   let c=b.ledgers.escaped_u-a.ledgers.escaped_u-ff;
   let q=ff-(b.ledgers.cmb_input-a.ledgers.cmb_input);
   let cn=r*cool+r.sqrt()*c;
   let sn=r*spec+r.sqrt()*q;
   work+=cool+c-cn+spec+q-sn;
   if b.ff_spectrum.is_some() && (self.spec_energy(b)?-sn).abs()>1e-14{return Err("spectral stock ledger".into())}
   cool=cn;spec=sn;
  }
  let next=State{gas:fine,cool,spec,work,err};
  let res=self.ledger(&next)?;
  let owner=map(self.d.residuals(&next.gas))?.1;
  if res.abs()>1e-8||(res-owner).abs()>1e-12{return Err(format!("bridge ledger {res:e} {owner:e}"))}
  Ok(next)
 }
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args=std::env::args().skip(1).collect::<Vec<_>>();
 if args.len()!=6{return Err("config output mode bins feedback step".into())}
 let mut cfg=DriverConfig::read(&fs::read_to_string(&args[0])?)?;
 let mode:u8=args[2].parse()?;let bins:usize=args[3].parse()?;let feedback=args[4]=="on";let cap:f64=args[5].parse()?;
 if ![2,3].contains(&mode)||cap<=0.{return Err("domain".into())}
 cfg.ff_balance_mode=mode;let target=cfg.local_target;
 let owner=ThomsonOwner::new(0.03,32,8,16,4,8,16)?;
 let mut g=owner.initial(1./21.,[.01,0.,0.,0.,.0075])?;
 let end=1./(1.+cfg.end_zbar);let mut dummy=p(&g.geometry);dummy.a=end;
 let (d,mut gas)=Driver::new_general(cfg,GeneralHistory::new(vec![p(&g.geometry),dummy],4,8)?)?;
 if mode==3{gas.ff_spectrum=Some(SpectralFf::new(1e-10,60.,bins)?);}
 let init=d.gas_energy_components(&gas)?.iter().sum();
 let mut cp=Coupler{d,feedback,init,rhs:0,calls:0};
 let mut s=State{gas,cool:0.,spec:0.,work:0.,err:[0.;2]};
 let out=Path::new(&args[1]);fs::create_dir(out)?;
 let mut f=BufWriter::new(fs::File::create(out.join("history.csv"))?);
 writeln!(f,"a,h,S0,S1,S2,S3,S4,T,xHII,xHeII,xHeIII,ne,primary,w,b,cool,spec,source,thermal_work,photon_work,boundary,secondary_work,ledger,gauss,metric,specN,specU,accepted,rejected")?;
 let mut rejected=0usize;let mut h=cap;let mut maxerr=0_f64;let mut maxspec=0_f64;let mut maxledger=0_f64;
 loop{
  let a=g.geometry.a;
  let eos=s.gas.gas.eos(cp.d.n_h0_cm3/a.powi(3),cp.d.n_he0_cm3/a.powi(3))?;
  let m=cp.d.general_moments(&s.gas)?;let [w,b]=cp.d.gas_energy_components(&s.gas)?;
  let l=&s.gas.ledgers;let ledger=cp.ledger(&s)?;let gauss=owner.constraint_external(&g,&s,&mut cp)?;
  maxledger=maxledger.max(ledger.abs());maxerr=maxerr.max(s.gas.last_error);maxspec=maxspec.max(s.err[0].max(s.err[1]));
  write!(f,"{a:.17e},{:.17e}",g.geometry.h)?;
  for x in g.geometry.s.into_iter().chain([eos.temperature_k]).chain(s.gas.gas.fractions).chain([eos.electron_density_cm3,m.energy,w,b,s.cool,s.spec,l.source_u,l.thermal_work,l.photon_work,l.boundary_u,s.work,ledger,gauss,s.gas.last_error,s.err[0],s.err[1]]){write!(f,",{x:.17e}")?;}
  writeln!(f,",{},{}",s.gas.accepted,rejected)?;
  if (end/a).ln()<1e-12{break}
  let mut du=h.min((end/a).ln());if a*du.exp()>end{du=f64::from_bits(du.to_bits()-1);}
  match owner.step_external(&g,&s,&mut cp,du){
   Ok((gg,ss,_))=>{g=gg;s=ss;h=map(rei_microphysics::external_controller::accepted_step(du,s.gas.last_error,target,cap))?;}
   Err(e)=>{rejected+=1;h=map(rei_microphysics::external_controller::rejected_step(du))?;eprintln!("reject {rejected} a={a:.17e} du={du:e}: {e}");if h<1e-10||rejected>200{return Err(e.into())}}
  }
 }
 f.flush()?;let eos=s.gas.gas.eos(cp.d.n_h0_cm3/s.gas.a.powi(3),cp.d.n_he0_cm3/s.gas.a.powi(3))?;
 if let Some(v)=&s.gas.ff_spectrum{
  let mut f=BufWriter::new(fs::File::create(out.join("spectrum.csv"))?);writeln!(f,"x,delta")?;for (x,y) in v.nodes().iter().zip(v.distortion()){writeln!(f,"{x:.17e},{y:.17e}")?;}
 }
 fs::write(out.join("source.txt"),compiled_identity())?;
 fs::write(out.join("RETURN.txt"),format!("status=COMPLETE\nmode={mode}\nbins={bins}\nfeedback={feedback}\naccepted={}\nrejected={rejected}\nrhs={}\nT={:.17e}\nmax_metric={maxerr:.17e}\nmax_spec_metric={maxspec:.17e}\nmax_ledger={maxledger:.17e}\n",s.gas.accepted,cp.rhs,eos.temperature_k))?;
 println!("COMPLETE mode={mode} bins={bins} feedback={feedback} accepted={} rejected={rejected} T={} maxspec={maxspec:e}",s.gas.accepted,eos.temperature_k);
 Ok(())
}
