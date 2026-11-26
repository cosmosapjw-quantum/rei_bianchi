//! C3N unpolarized elastic angular collision on signed secondary frequency radiation.
mod frequency;
use frequency::FreqRays;
use bianchi_rustcore::kinetic::owned_thomson::{ThomsonOwner,ExternalMatter,ExternalContribution};
use bianchi_rustcore::kinetic::owned_vlasov::OwnedState;
use bianchi_rustcore::kinetic::cooling_rays::CoolingRays;
use rei_microphysics::{axbi_covariant_driver::{Driver,DriverConfig,DriverState,compiled_identity},general_history::{GeneralHistory,HistoryPoint},spectral_ff::{SpectralFf,blackbody_per_h}};
use std::{fs,io::{BufWriter,Write},path::Path};
const H0:f64=2.1842852410855023e-18;
const RHO0:f64=3.*299792458.*299792458.*H0*H0/(8.*std::f64::consts::PI*6.67430e-11);
const EV:f64=1.602176634e-19;
fn map<T>(r:Result<T,rei_microphysics::ForwardError>)->Result<T,String>{r.map_err(|e|format!("{e:?}"))}
fn p(g:&OwnedState)->HistoryPoint{HistoryPoint{a:g.a,h:g.h,f:std::array::from_fn(|i|std::array::from_fn(|j|g.f[(i,j)]))}}
#[derive(Clone)]
struct State{gas:DriverState,cool:f64,spec:f64,spec_ref:f64,work:f64,err:[f64;2],cr:Vec<f64>,freq:Vec<f64>,source_n:f64,edge:[f64;4],elastic:[f64;5],max_depth:f64}
struct Coupler{d:Driver,feedback:bool,directional:bool,mean:bool,scatter:bool,rays:CoolingRays,freq:FreqRays,init:f64,rhs:usize,calls:usize}
impl Coupler{
 fn ledger(&self,s:&State)->Result<f64,String>{
  let u=map(self.d.general_moments(&s.gas))?.energy;
  let [w,b]=map(self.d.gas_energy_components(&s.gas))?;
  let l=&s.gas.ledgers;
  Ok(u+w+b+s.cool+s.spec-self.init-l.source_u+l.thermal_work+l.photon_work+l.boundary_u+s.work)
 }
 fn geom_at(&self,g:&OwnedState,a:f64)->Result<OwnedState,String>{
  let q=map(self.d.transport.general_history().ok_or("history")?.point(a))?;
  let mut out=g.clone();out.a=a;out.h=q.h;
  for i in 0..3{for j in 0..3{out.f[(i,j)]=q.f[i][j];}}
  Ok(out)
 }
 fn sec_pressure(&self,s:&State,g:&OwnedState)->Result<[[f64;3];3],String>{
  if !self.directional{return Ok(std::array::from_fn(|i|std::array::from_fn(|j|if i==j{(s.cool+s.spec)/3.}else{0.})))}
  let (c,pc)=self.rays.moments(&s.cr,g)?;
  let (u,p,_)=self.freq.moments(&s.freq,g)?;
  let m:[[f64;3];3]=std::array::from_fn(|i|std::array::from_fn(|j|pc[(i,j)]+p[i][j]));
  if (c-s.cool).abs()>1e-14 || (u-s.spec).abs()>1e-14 || ((0..3).map(|i|m[i][i]).sum::<f64>()-s.cool-s.spec).abs()>1e-14{return Err("directional trace".into())}
  Ok(m)
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
  let psec=self.sec_pressure(s,g)?;
  let pressure=std::array::from_fn(|i|std::array::from_fn(|j|fac*(m.pressure[i][j]+psec[i][j]+if i==j{2.*w/3.}else{0.})));
  Ok(ExternalContribution{rho,pressure,photon_rho:fac*(m.energy+sec),ne_m3:ne})
 }
 fn advance(&mut self,s:&State,old:&OwnedState,mid:&OwnedState,end:&OwnedState)->Result<State,String>{
  self.calls+=1;
  if self.calls>50000{return Err("stage cap".into())}
  map(self.d.set_general_interval(vec![p(old),p(mid),p(end)]))?;
  let mut base=s.gas.clone();
  let mut edge=s.edge;
  if self.mean{
    let (v,b)=self.freq.project(&s.freq,old)?;
    let sp=base.ff_spectrum.as_mut().ok_or("no spectrum")?;
    map(sp.restore_distortion(&v))?;
    for i in 0..4{edge[i]=edge[i].abs().max(b[i].abs());}
  }
  let (first,fine,_,err)=map(self.d.c3j_trial_split(&base,end.a,&mut self.rhs))?;
  let mut cool=s.cool;let mut spec=s.spec;let mut spec_ref=self.spec_energy(&base)?;let mut work=s.work;
  let mut cr=s.cr.clone();let mut freq=s.freq.clone();let mut source_n=s.source_n;let mut elastic=s.elastic;let mut max_depth=s.max_depth;
  for (a,b) in [(&base,&first),(&first,&fine)]{
   let r=a.a/b.a;
   let ff=b.cooling_ev[7]-a.cooling_ev[7];
   let c=b.ledgers.escaped_u-a.ledgers.escaped_u-ff;
   let q=ff-(b.ledgers.cmb_input-a.ledgers.cmb_input);
   let sr=r*spec_ref+r.sqrt()*q;
   if b.ff_spectrum.is_some() && (self.spec_energy(b)?-sr).abs()>1e-14{return Err("scalar spectral stock ledger".into())}
   spec_ref=sr;
   if self.directional{
    let ga=self.geom_at(old,a.a)?;let gb=self.geom_at(old,b.a)?;let gm=self.geom_at(old,(a.a*b.a).sqrt())?;
    let (cn,wc)=self.rays.advance(&cr,&ga,&gm,&gb,c)?;
    let x=a.ff_spectrum.as_ref().ok_or("old spectral stock")?;
    let y=b.ff_spectrum.as_ref().ok_or("new spectral stock")?;
    let delta:Vec<_>=x.distortion().iter().zip(y.distortion()).map(|(u,v)|v-u).collect();
    let ne=0.5*(map(a.gas.eos(self.d.n_h0_cm3/a.a.powi(3),self.d.n_he0_cm3/a.a.powi(3)))?.electron_density_cm3+map(b.gas.eos(self.d.n_h0_cm3/b.a.powi(3),self.d.n_he0_cm3/b.a.powi(3)))?.electron_density_cm3)*1e6;
    let depth=if self.scatter{ne*299792458.*6.6524587051e-29*(b.a/a.a).ln()/(H0*gm.h)}else{0.};
    let (us,ws,dn,du,diag)=self.freq.advance(&mut freq,&ga,&gm,&gb,&delta,depth)?;
    max_depth=max_depth.max(depth);
    for k in 0..3{elastic[k]+=diag[k];}
    for k in 3..5{elastic[k]=elastic[k].max(diag[k]);}
    let uc=self.rays.moments(&cn,&gb)?.0;
    if (du-q).abs()>1e-14 || (uc-cool+wc-c).abs()>1e-14 || (us-spec+ws-q).abs()>1e-14{return Err(format!("spectral work {} {}",du,q))}
    source_n+=dn;work+=wc+ws;cool=uc;spec=us;cr=cn;

   }else{
    let cn=r*cool+r.sqrt()*c;let sn=r*spec+r.sqrt()*q;
    work+=cool+c-cn+spec+q-sn;cool=cn;spec=sn;
   }
  }
  let next=State{gas:fine,cool,spec,spec_ref,work,err,cr,freq,source_n,edge,elastic,max_depth};
  self.sec_pressure(&next,end)?;
  let res=self.ledger(&next)?;
  let owner=map(self.d.residuals(&next.gas))?.1;
  if res.abs()>1e-8||(res-owner).abs()>1e-12{return Err(format!("bridge ledger {res:e} {owner:e}"))}
  Ok(next)
 }
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args=std::env::args().skip(1).collect::<Vec<_>>();
 if args.len()!=9{return Err("config output mode bins feedback step frequency/mean mesh nmu".into())}
 let mut cfg=DriverConfig::read(&fs::read_to_string(&args[0])?)?;
 let mode:u8=args[2].parse()?;let bins:usize=args[3].parse()?;let feedback=args[4]=="on";let cap:f64=args[5].parse()?;
 if mode!=3||cap<=0.{return Err("domain".into())}
 cfg.ff_balance_mode=mode;let target=cfg.local_target;
 let directional=args[6]!="iso";let mean=args[6]=="mean"||args[6]=="elastic";let scatter=args[6]=="elastic";let nmu:usize=args[8].parse()?;let mesh=fs::read_to_string(&args[7])?.lines().skip(1).map(|l|l.split(',').next().unwrap().parse::<f64>()).collect::<Result<Vec<_>,_>>()?;
 let owner=ThomsonOwner::new(0.03,32,8,16,4,8,16)?;
 let mut g=owner.initial(1./21.,[0.01,0.,0.,0.,0.0075])?;
 let end=1./(1.+cfg.end_zbar);let mut dummy=p(&g.geometry);dummy.a=end;
 let (d,mut gas)=Driver::new_general(cfg,GeneralHistory::new(vec![p(&g.geometry),dummy],4,8)?)?;
 if mode==3{gas.ff_spectrum=Some(SpectralFf::new(1e-10,60.,bins)?);}
 let init=d.gas_energy_components(&gas)?.iter().sum();
 let rays=CoolingRays::new(1./21.,nmu,2*nmu)?;
 let fq=FreqRays::new(gas.ff_spectrum.as_ref().unwrap().nodes(),map(blackbody_per_h(2.7255/gas.a,d.n_h0_cm3/gas.a.powi(3)))?,gas.a,nmu)?;
 let mut s=State{gas,cool:0.,spec:0.,spec_ref:0.,work:0.,err:[0.;2],cr:rays.empty(),freq:fq.empty(),source_n:0.,edge:[0.;4],elastic:[0.;5],max_depth:0.};
 let mut cp=Coupler{d,feedback,directional,mean,scatter,rays,freq:fq,init,rhs:0,calls:0};
 if mesh[0]!=g.geometry.a || (mesh.last().unwrap()-end).abs()>1e-15{return Err("mesh endpoints".into())}
 let out=Path::new(&args[1]);fs::create_dir(out)?;
 let mut f=BufWriter::new(fs::File::create(out.join("history.csv"))?);
 writeln!(f,"a,h,S0,S1,S2,S3,S4,T,xHII,xHeII,xHeIII,ne,primary,w,b,cool,spec,source,thermal_work,photon_work,boundary,secondary_work,ledger,gauss,metric,specN,specU,spec_ref,secPxx,secPyy,secPzz,secPxy,secPxz,secPyz,N_dir,N_source,edgeN,edgeU,edgeNabs,edgeUabs,elastic_depth,elastic_moved,elastic_blocked,max_collision_U,max_collision_N,max_depth,accepted,rejected")?;
 let rejected=0usize;let mut idx=0usize;let mut maxerr=0_f64;let mut maxspec=0_f64;let mut maxledger=0_f64;
 loop{
  let a=g.geometry.a;
  let eos=s.gas.gas.eos(cp.d.n_h0_cm3/a.powi(3),cp.d.n_he0_cm3/a.powi(3))?;
  let m=cp.d.general_moments(&s.gas)?;let [w,b]=cp.d.gas_energy_components(&s.gas)?;
  let l=&s.gas.ledgers;let ledger=cp.ledger(&s)?;let gauss=owner.constraint_external(&g,&s,&mut cp)?;let ps=cp.sec_pressure(&s,&g.geometry)?;let (_,_,ns)=cp.freq.moments(&s.freq,&g.geometry)?;
  maxledger=maxledger.max(ledger.abs());maxerr=maxerr.max(s.gas.last_error);maxspec=maxspec.max(s.err[0].max(s.err[1]));
  write!(f,"{a:.17e},{:.17e}",g.geometry.h)?;
  for x in g.geometry.s.into_iter().chain([eos.temperature_k]).chain(s.gas.gas.fractions).chain([eos.electron_density_cm3,m.energy,w,b,s.cool,s.spec,l.source_u,l.thermal_work,l.photon_work,l.boundary_u,s.work,ledger,gauss,s.gas.last_error,s.err[0],s.err[1],s.spec_ref,ps[0][0],ps[1][1],ps[2][2],ps[0][1],ps[0][2],ps[1][2],ns,s.source_n,s.edge[0],s.edge[1],s.edge[2],s.edge[3]]).chain(s.elastic).chain([s.max_depth]){write!(f,",{x:.17e}")?;}
  writeln!(f,",{},{}",s.gas.accepted,rejected)?;
  if idx+1==mesh.len(){if (end-a).abs()>1e-14{return Err("mesh endpoint".into())}break}
  let next=mesh[idx+1];let mut du=(next/a).ln();
  if a*du.exp()>end{du=f64::from_bits(du.to_bits()-1);}
  if du<=0.||du>cap*1.001{return Err("fixed mesh domain".into())}
  let (gg,ss,_)=owner.step_external(&g,&s,&mut cp,du)?;
  if (gg.geometry.a-next).abs()>2e-16 || ss.gas.last_error>=target{return Err("fixed mesh mismatch".into())}
  g=gg;s=ss;idx+=1;

 }
 f.flush()?;let eos=s.gas.gas.eos(cp.d.n_h0_cm3/s.gas.a.powi(3),cp.d.n_he0_cm3/s.gas.a.powi(3))?;
 if let Some(v)=&s.gas.ff_spectrum{
  let mut f=BufWriter::new(fs::File::create(out.join("spectrum.csv"))?);writeln!(f,"x,delta")?;for (x,y) in v.nodes().iter().zip(v.distortion()){writeln!(f,"{x:.17e},{y:.17e}")?;}
 }
 if directional{
  cp.freq.output(&s.freq,&g.geometry,&out.join("directional.csv"))?;
  let (q,e)=cp.freq.project(&s.freq,&g.geometry)?;
  let mut f=BufWriter::new(fs::File::create(out.join("projected.csv"))?);
  writeln!(f,"x,delta")?;for (x,y) in s.gas.ff_spectrum.as_ref().unwrap().nodes().iter().zip(q){writeln!(f,"{x:.17e},{y:.17e}")?;}
  println!("final projection edges {:?}",e);
 }
 fs::write(out.join("source.txt"),compiled_identity())?;
 fs::write(out.join("NORMALIZATION.txt"),format!("nh0_cm3={:.17e}\n",cp.d.n_h0_cm3))?;
 fs::write(out.join("RETURN.txt"),format!("status=COMPLETE\nmode={mode}\nbins={bins}\nfeedback={feedback}\ndirectional={directional}\naccepted={}\nrejected={rejected}\nrhs={}\nT={:.17e}\nmax_metric={maxerr:.17e}\nmax_spec_metric={maxspec:.17e}\nmax_ledger={maxledger:.17e}\n",s.gas.accepted,cp.rhs,eos.temperature_k))?;
 println!("COMPLETE mode={mode} bins={bins} feedback={feedback} accepted={} rejected={rejected} T={} maxspec={maxspec:e}",s.gas.accepted,eos.temperature_k);
 Ok(())
}
