//! Pinned integrated PR378 source, research-only secondary DG collision trial.
mod dg;
use dg::{Grid,Stock};
use bianchi_rustcore::kinetic::{owned_thomson::{ThomsonOwner,ExternalMatter,ExternalContribution},owned_vlasov::OwnedState,cooling_rays::CoolingRays};
use rei_microphysics::{axbi_covariant_driver::{Driver,DriverConfig,DriverState,compiled_identity},general_history::{GeneralHistory,HistoryPoint},spectral_ff::{SpectralFf,blackbody_per_h}};
use std::{fs,io::{BufWriter,Write},path::Path};
const H0:f64=2.1842852410855023e-18;
const RHO0:f64=3.*299792458.*299792458.*H0*H0/(8.*std::f64::consts::PI*6.67430e-11);
const EV:f64=1.602176634e-19;
fn map<T>(r:Result<T,rei_microphysics::ForwardError>)->Result<T,String>{r.map_err(|e|format!("{e:?}"))}
fn p(g:&OwnedState)->HistoryPoint{HistoryPoint{a:g.a,h:g.h,f:std::array::from_fn(|i|std::array::from_fn(|j|g.f[(i,j)]))}}
#[derive(Clone,Debug)]
struct State{gas:DriverState,cool:f64,spec:f64,work:f64,cr:Vec<f64>,dg:Stock,source_n:f64,diag:[f64;9],edge:[f64;4],err:[f64;2],tau:f64}
struct Coupler{d:Driver,grid:Grid,rays:CoolingRays,init:f64,on:bool,mean:bool,force_reject:bool,rhs:usize,calls:usize}
impl Coupler{
 fn ledger(&self,s:&State)->Result<f64,String>{let u=map(self.d.general_moments(&s.gas))?.energy;let[w,b]=map(self.d.gas_energy_components(&s.gas))?;let l=&s.gas.ledgers;Ok(u+w+b+s.cool+s.spec-self.init-l.source_u+l.thermal_work+l.photon_work+l.boundary_u+s.work)}
 fn geom_at(&self,g:&OwnedState,a:f64)->Result<OwnedState,String>{let q=map(self.d.transport.general_history().ok_or("history")?.point(a))?;let mut out=g.clone();out.a=a;out.h=q.h;for i in 0..3{for j in 0..3{out.f[(i,j)]=q.f[i][j];}}Ok(out)}
 fn sec_pressure(&self,s:&State,g:&OwnedState)->Result<[[f64;3];3],String>{let(c,pc)=self.rays.moments(&s.cr,g)?;let(u,p,_)=self.grid.moments(&s.dg,g)?;if (c-s.cool).abs()>1e-14||(u-s.spec).abs()>1e-14{return Err("secondary trace identity".into())}let m=[[0.;3];3];let m=std::array::from_fn(|i|std::array::from_fn(|j|pc[(i,j)]+p[i][j]));if ((0..3).map(|i|m[i][i]).sum::<f64>()-s.cool-s.spec).abs()>1e-14{return Err("secondary trace".into())}Ok(m)}
 fn spec_energy(&self,s:&DriverState)->Result<f64,String>{match &s.ff_spectrum{Some(v)=>map(v.energy(map(blackbody_per_h(2.7255/s.a,self.d.n_h0_cm3/s.a.powi(3)))?)),None=>Ok(0.)}}
 fn update(&self,stock:&mut Stock,a:&DriverState,b:&DriverState,ga:&OwnedState,gm:&OwnedState,gb:&OwnedState)->Result<(f64,f64,f64,[f64;6],f64),String>{
  let u0=self.grid.moments(stock,ga)?.0;let um=self.grid.moments(stock,gm)?.0;
  let x=a.ff_spectrum.as_ref().ok_or("old spectrum")?;let y=b.ff_spectrum.as_ref().ok_or("new spectrum")?;
  let delta:Vec<_>=x.distortion().iter().zip(y.distortion()).map(|(a,b)|b-a).collect();
  let (dn,du)=self.grid.birth(stock,gm,&delta)?;
  let en=map(b.gas.eos(self.d.n_h0_cm3/b.a.powi(3),self.d.n_he0_cm3/b.a.powi(3)))?;
  let eo=map(a.gas.eos(self.d.n_h0_cm3/a.a.powi(3),self.d.n_he0_cm3/a.a.powi(3)))?;
  let depth=0.5*(eo.electron_density_cm3+en.electron_density_cm3)*1e6*299792458.*6.6524587051e-29*(b.a/a.a).ln()/(H0*gm.h);
  let diag=self.grid.collide(stock,gm,8.617333262145e-5*en.temperature_k/510998.9499961642,en.temperature_k/(2.7255/gm.a),if self.on{depth}else{0.})?;
  let um1=self.grid.moments(stock,gm)?.0;let u1=self.grid.moments(stock,gb)?.0;let work=u0-um+um1-u1;
  if (um1-um-du).abs()>1e-14{return Err(format!("DG midpoint energy {um1:e} {um:e} {du:e}"))}
  Ok((u1,work,dn,diag,depth))
 }
}
impl ExternalMatter for Coupler{
 type State=State;
 fn contribution(&mut self,s:&State,g:&OwnedState)->Result<ExternalContribution,String>{
  if s.gas.a!=g.a{return Err("clock".into())}
  let nh=self.d.n_h0_cm3/g.a.powi(3);let nhe=self.d.n_he0_cm3/g.a.powi(3);let ne=map(s.gas.gas.eos(nh,nhe))?.electron_density_cm3*1e6;
  let m=map(self.d.general_moments(&s.gas))?;let[w,b]=map(self.d.gas_energy_components(&s.gas))?;let fac=nh*1e6*EV/RHO0;let sec=s.cool+s.spec;let ps=self.sec_pressure(s,g)?;
  Ok(ExternalContribution{rho:fac*(m.energy+w+b-self.init-s.gas.ledgers.source_u+sec),pressure:std::array::from_fn(|i|std::array::from_fn(|j|fac*(m.pressure[i][j]+ps[i][j]+if i==j{2.*w/3.}else{0.}))),photon_rho:fac*(m.energy+sec),ne_m3:ne})
 }
 fn advance(&mut self,s:&State,old:&OwnedState,mid:&OwnedState,end:&OwnedState)->Result<State,String>{
  self.calls+=1;map(self.d.set_general_interval(vec![p(old),p(mid),p(end)]))?;
  let mut base=s.gas.clone();let mut edge=s.edge;
  if self.mean{let(v,e)=self.grid.project(&s.dg,old)?;map(base.ff_spectrum.as_mut().ok_or("missing spectrum")?.restore_distortion(&v))?;for k in 0..4{edge[k]=edge[k].max(e[k].abs());}}
  let (full,first,fine,_,err)=map(self.d.c3p_trial_split(&base,end.a,&mut self.rhs))?;
  if std::env::var_os("R118C4M_TRACE").is_some(){
   for (role,z) in [(0,&base),(1,&first),(2,&fine),(3,&full)]{
    let mut line=format!("C4M_CHEM,{},{role},{:.17e},{:.17e}",self.calls,z.a,z.gas.w_erg_per_h);
    for v in z.gas.fractions{line.push_str(&format!(",{v:.17e}"));}
    let l=&z.ledgers;
    for v in [l.source_n,l.source_u,l.absorbed_n,l.escaped_u,l.thermal_work,l.photon_work,l.boundary_u,l.cmb_input,z.photons.iter().sum::<f64>(),z.photon_energy_ref.iter().sum::<f64>(),z.heii_above.as_ref().map_or(0.,|p|p.number.iter().sum()),z.hei_middle.as_ref().map_or(0.,|p|p.number.iter().sum()),z.hi_below.as_ref().map_or(0.,|p|p.number.iter().sum())]{line.push_str(&format!(",{v:.17e}"));}
    line.push_str(&format!(",{},{},{},{}",z.photons.iter().filter(|x|**x>0.).count(),z.heii_above.as_ref().map_or(0,|p|p.number.iter().filter(|x|**x>0.).count()),z.hei_middle.as_ref().map_or(0,|p|p.number.iter().filter(|x|**x>0.).count()),z.hi_below.as_ref().map_or(0,|p|p.number.iter().filter(|x|**x>0.).count())));eprintln!("{line}");
   }
  }
  let mut dg=s.dg.clone();let mut cr=s.cr.clone();let mut cool=s.cool;let mut spec=s.spec;let mut work=s.work;let mut sn=s.source_n;let mut diag=s.diag;let mut tau=s.tau;
  let mut spec_ref=self.spec_energy(&base)?;
  for(a,b) in [(&base,&first),(&first,&fine)]{
   let ga=self.geom_at(old,a.a)?;let gm=self.geom_at(old,(a.a*b.a).sqrt())?;let gb=self.geom_at(old,b.a)?;
   let ff=b.cooling_ev[7]-a.cooling_ev[7];let c=b.ledgers.escaped_u-a.ledgers.escaped_u-ff;let q=ff-(b.ledgers.cmb_input-a.ledgers.cmb_input);
   let sr=(a.a/b.a)*spec_ref+(a.a/b.a).sqrt()*q;if (self.spec_energy(b)?-sr).abs()>1e-14{return Err("native scalar stock ledger".into())}spec_ref=sr;
   let(cn,wc)=self.rays.advance(&cr,&ga,&gm,&gb,c)?;
   let(us,ws,dn,dd,depth)=self.update(&mut dg,a,b,&ga,&gm,&gb)?;
   let uc=self.rays.moments(&cn,&gb)?.0;
   if (uc-cool+wc-c).abs()>1e-14||(us-spec+ws-q).abs()>1e-14{return Err(format!("DG source ledger {} {}",us-spec+ws,q))}
   cr=cn;cool=uc;spec=us;work+=wc+ws;sn+=dn;tau+=depth;
   diag[0]=diag[0].max(dd[0]);diag[1]=diag[1].max(dd[1]);diag[2]+=dd[4]*depth*self.grid.cap;diag[3]=diag[3].min(self.grid.coefficients(&dg)?.2);
  }
  // Independent full vs two-half signed collision correction. Both start from
  // same immutable state and use native full/fine scalar sources.
  let mut dgfull=s.dg.clone();let gm=self.geom_at(old,(base.a*full.a).sqrt())?;
  self.update(&mut dgfull,&base,&full,old,&gm,end)?;
  let (dn,dv)=self.grid.corr_diff(&dg,&dgfull);diag[4]=diag[4].max(dn);diag[5]=diag[5].max(dv);
  let (u,_,n)=self.grid.moments(&dg,end)?;diag[6]=diag[6].max((n-sn).abs());diag[7]=diag[7].max((u-spec).abs());
  if dn>1e-14||dv>1e-14||(n-sn).abs()>1e-12{return Err("DG fullhalf/number gate".into())}
  let next=State{gas:fine,cool,spec,work,cr,dg,source_n:sn,diag,edge,err,tau};
  self.sec_pressure(&next,end)?;let res=self.ledger(&next)?;let owner=map(self.d.residuals(&next.gas))?.1;
  if res.abs()>1e-8||(res-owner).abs()>1e-12{return Err(format!("DG ledger {res:e} {owner:e}"))}
  // Explicit trial rejection after actual native gas + directional candidate,
  // before state publication. The caller compares accepted snapshots.
  if self.force_reject{self.force_reject=false;return Err("C3V intentional trial rejection".into())}
  if std::env::var_os("R118C4M_TRACE").is_some(){eprintln!("C4M_ADVANCE,{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",self.calls,old.a,mid.a,end.a,next.cool,next.spec,next.work,next.source_n,next.tau);}
  Ok(next)
 }
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args=std::env::args().skip(1).collect::<Vec<_>>();if args.len()!=12{return Err("cfg out bins nc nmu nstep z_end on/off coarse/fine mean/autonomous".into())}
 let mut cfg=DriverConfig::read(&fs::read_to_string(&args[0])?)?;let bins:usize=args[2].parse()?;let nc:usize=args[3].parse()?;let nmu:usize=args[4].parse()?;let ns:usize=args[5].parse()?;cfg.end_zbar=args[6].parse()?;cfg.ff_balance_mode=3;let target=cfg.local_target;
 let on=args[7]=="on";let fine=args[8]=="fine";let mean=args[9]=="mean";
 let owner=ThomsonOwner::new(0.03,32,8,16,4,8,16)?;let scale:f64=std::env::var("C4M_SHEAR_SCALE").unwrap_or("1".into()).parse()?;let mut g=owner.initial(1./21.,[0.01*scale,0.,0.,0.,0.0075*scale])?;let end=1./(1.+cfg.end_zbar);
 let mut dummy=p(&g.geometry);dummy.a=end;
 let(mut d,mut gas)=Driver::new_general(cfg,GeneralHistory::new(vec![p(&g.geometry),dummy],4,8)?)?;
 let heii:f64=args[10].parse()?;let heiii:f64=args[11].parse()?;
 if heii!=0. || heiii!=0.{
  let nh=d.n_h0_cm3/gas.a.powi(3);let nhe=d.n_he0_cm3/gas.a.powi(3);let t=map(gas.gas.eos(nh,nhe))?.temperature_k;
  gas.gas=map(rei_microphysics::igm_state::IgmGasState::from_temperature([gas.gas.fractions[0],heii,heiii],nh,nhe,t))?;
  map(d.c4c_rebase_initial(&gas))?;
 }
 gas.ff_spectrum=Some(SpectralFf::new(1e-10,60.,bins)?);
 let initial_energy_parts=d.gas_energy_components(&gas)?;let init=initial_energy_parts.iter().sum();let grid=Grid::new(gas.ff_spectrum.as_ref().unwrap().nodes(),map(blackbody_per_h(2.7255/gas.a,d.n_h0_cm3/gas.a.powi(3)))?,gas.a,nmu,nc,fine)?;
 let rays=CoolingRays::new(1./21.,4,8)?;let mut diag=[0.;9];diag[3]=1.;
 let mut s=State{gas,cool:0.,spec:0.,work:0.,cr:rays.empty(),dg:grid.empty(),source_n:0.,diag,edge:[0.;4],err:[0.;2],tau:0.};
 let mut cp=Coupler{d,grid,rays,init,on,mean,force_reject:false,rhs:0,calls:0};
 let out=Path::new(&args[1]);fs::create_dir(out)?;let mut f=BufWriter::new(fs::File::create(out.join("history.csv"))?);
 let mut mat=BufWriter::new(fs::File::create(out.join("matter.csv"))?);
 let mut ext=BufWriter::new(fs::File::create(out.join("external.csv"))?);
 writeln!(ext,"a,nh_m3,ne_m3,rho_owner,rho_stable,primary,thermal,binding,cool,spec,init_w,init_b,source_u,thermal_work,photon_work,boundary_u,secondary_work,prim_Pxx,prim_Pyy,prim_Pzz,prim_Pxy,prim_Pxz,prim_Pyz,cool_Pxx,cool_Pyy,cool_Pzz,cool_Pxy,cool_Pxz,cool_Pyz,spec_Pxx,spec_Pyy,spec_Pzz,spec_Pxy,spec_Pxz,spec_Pyz,owner_Pxx,owner_Pyy,owner_Pzz,owner_Pxy,owner_Pxz,owner_Pyz")?;
 writeln!(mat,"a,h,rho,Pxx,Pyy,Pzz,Pxy,Pxz,Pyz,F00,F01,F02,F10,F11,F12,F20,F21,F22,ne_m3,nh_m3")?;
 writeln!(f,"a,h,T,xHII,xHeII,xHeIII,S0,S1,S2,S3,S4,primary,thermal,binding,cool,spec,N,N_source,secondary_work,ledger,gauss,metric,specerrN,specerrU,tau,margin,coll_N_res,coll_U_res,coll_moved,fullhalf_N,fullhalf_V,edgeN,edgeU,corr_U,corr_N,corr_Pxx,corr_Pyy,corr_Pzz,corr_Pxy,corr_Pxz,corr_Pyz,proper_s,accepted,rejected")?;
 let a0=g.geometry.a;let mut tau=0.;let mut rejected=0;let mut rollback=false;
 for i in 0..=ns{
  let a=g.geometry.a;let eos=map(s.gas.gas.eos(cp.d.n_h0_cm3/a.powi(3),cp.d.n_he0_cm3/a.powi(3)))?;
  let m=map(cp.d.general_moments(&s.gas))?;let[w,b]=map(cp.d.gas_energy_components(&s.gas))?;let(_,_,n)=cp.grid.moments(&s.dg,&g.geometry)?;let(cu,p0,cn)=cp.grid.corr(&s.dg,&g.geometry)?;let led=cp.ledger(&s)?;let gauss=owner.constraint_external(&g,&s,&mut cp)?;
  let mm=owner.matter(&g)?;let v=cp.contribution(&s,&g.geometry)?;
  // Diagnostics at accepted node only. No values below enter advance/contribution or geometry.
  let nh=cp.d.n_h0_cm3*1e6/a.powi(3);let fac=nh*EV/RHO0;
  let l=&s.gas.ledgers;let stable=fac*(m.energy+(w-initial_energy_parts[0])+(b-initial_energy_parts[1])-l.source_u+s.cool+s.spec);
  let (_,pc)=cp.rays.moments(&s.cr,&g.geometry)?;
  let (_,pd,_)=cp.grid.moments(&s.dg,&g.geometry)?;
  let mut evs=vec![a,nh,v.ne_m3,v.rho,stable,m.energy,w,b,s.cool,s.spec,initial_energy_parts[0],initial_energy_parts[1],l.source_u,l.thermal_work,l.photon_work,l.boundary_u,s.work];
  for (i,j) in [(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)] {evs.push(m.pressure[i][j]);}
  for (i,j) in [(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)] {evs.push(pc[(i,j)]);}
  for (i,j) in [(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)] {evs.push(pd[i][j]);}
  for (i,j) in [(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)] {evs.push(v.pressure[i][j]);}
  for (k,x) in evs.iter().enumerate(){if k>0{write!(ext,",")?;}write!(ext,"{x:.17e}")?;}writeln!(ext)?;ext.flush()?;
  let p=|i:usize,j:usize|mm.pressure[(i,j)]+v.pressure[i][j];
  let mut valsm=vec![a,g.geometry.h,mm.rho+v.rho,p(0,0),p(1,1),p(2,2),p(0,1),p(0,2),p(1,2)];
  for i in 0..3{for j in 0..3{valsm.push(g.geometry.f[(i,j)]);}}
  valsm.extend([v.ne_m3,cp.d.n_h0_cm3*1e6/a.powi(3)]);
  for(k,x)in valsm.iter().enumerate(){if k>0{write!(mat,",")?;}write!(mat,"{x:.17e}")?;}writeln!(mat)?;mat.flush()?;
  let vals=[a,g.geometry.h,eos.temperature_k,s.gas.gas.fractions[0],s.gas.gas.fractions[1],s.gas.gas.fractions[2],g.geometry.s[0],g.geometry.s[1],g.geometry.s[2],g.geometry.s[3],g.geometry.s[4],m.energy,w,b,s.cool,s.spec,n,s.source_n,s.work,led,gauss,s.gas.last_error,s.err[0],s.err[1],s.tau,s.diag[3],s.diag[0],s.diag[1],s.diag[2],s.diag[4],s.diag[5],s.edge[0],s.edge[1],cu,cn,p0[0][0],p0[1][1],p0[2][2],p0[0][1],p0[0][2],p0[1][2],tau];
  for(k,x) in vals.iter().enumerate(){if k>0{write!(f,",")?}write!(f,"{x:.17e}")?}writeln!(f,",{},{}",s.gas.accepted,rejected)?;f.flush()?;
  if i==ns{break}
  let next=a0*((end/a0).ln()*(i+1)as f64/ns as f64).exp();let mut du=(next/a).ln();if a*du.exp()>end{du=f64::from_bits(du.to_bits()-1)}
  if i==0&&on&&nmu==4&&ns==2{
   let old=format!("{:?}",s);let geom=format!("{:?}",g.geometry);cp.force_reject=true;
   let r=owner.step_external(&g,&s,&mut cp,du);
   match r{Err(e) if e.contains("intentional trial rejection")=>(),Err(e)=>return Err(format!("unexpected reject {e}").into()),Ok(_)=>return Err("intentional rejection failed".into())}
   if old!=format!("{:?}",s)||geom!=format!("{:?}",g.geometry){return Err("rollback mutated state".into())}
   rejected+=1;rollback=true;
  }
  let (gg,ss,_)=owner.step_external(&g,&s,&mut cp,du)?;if ss.gas.last_error>=target{return Err("native metric".into())}
  tau+=du*0.5*(1./g.geometry.h+1./gg.geometry.h)/H0;g=gg;s=ss;
 }
 if !cp.grid.rollback_test(&s.dg){return Err("positivity rejection rollback".into())}
 let e=cp.grid.e.clone();let mut o=BufWriter::new(fs::File::create(out.join("stock.csv"))?);writeln!(o,"ray,cell,lo,hi,N,V,collision_N,collision_V")?;
 for i in 0..s.dg.n.len(){let j=i%(e.len()-1);writeln!(o,"{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",i/(e.len()-1),j,e[j],e[j+1],s.dg.n[i],s.dg.v[i],s.dg.dn[i],s.dg.dv[i])?}
 fs::write(out.join("RETURN.txt"),format!("status=COMPLETE\naccepted={}\nrejected={rejected}\nrollback={rollback}\nbins={bins}\ncells={nc}\nrays={}\non={on}\nmean={mean}\nquadrature_fine={fine}\ncap={:.17e}\ncalls={}\nrhs={}\n",s.gas.accepted,2*nmu*nmu,cp.grid.cap,cp.calls,cp.rhs))?;
 fs::write(out.join("source.txt"),compiled_identity())?;
 println!("COMPLETE bins={bins} cells={nc} nmu={nmu} accepted={} rejected={rejected} diag={:?}",s.gas.accepted,s.diag);Ok(())
}
