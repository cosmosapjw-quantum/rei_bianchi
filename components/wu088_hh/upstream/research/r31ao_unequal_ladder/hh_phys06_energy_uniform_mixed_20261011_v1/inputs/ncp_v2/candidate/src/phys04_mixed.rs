// Source callback extension: arithmetic at supplied boxes, never a BE/root solver.
pub const PHYS04_LAMBDA_SLOT:usize=4;
pub const PHYS04_B_SLOT:usize=5;
static PHYS04_DERIVATIVES:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
static PHYS04_SOURCE_RHS:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
static PHYS04_LINEAR:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
pub fn phys04_arithmetic_counts()->[usize;3]{[&PHYS04_DERIVATIVES,&PHYS04_SOURCE_RHS,&PHYS04_LINEAR].map(|x|x.load(std::sync::atomic::Ordering::SeqCst))}
pub fn phys04_parameter(value:Interval,slot:usize)->Result<Jet,ForwardError>{Jet::variable(value,slot).map_err(ie)}
pub fn phys04_carry(value:Interval,u:Interval,v:Interval,w:Interval)->Result<Jet,ForwardError>{
 let mut j=Jet::constant(value).map_err(ie)?;j.gradient[4]=u;j.gradient[5]=v;j.hessian[4][5]=w;j.hessian[5][4]=w;Ok(j)
}
// Full multivariate chain rule into the owner's seven-slot outward Jet.
fn phys04_compose(raw:&Jet,gas:&[Jet;4])->Result<Jet,ForwardError>{
 let mut out=Jet::constant(raw.value).map_err(ie)?;
 for a in 0..7 {
  for i in 0..4 {out.gradient[a]=ia(&out.gradient[a],&im(&raw.gradient[i],&gas[i].gradient[a])?)?;}
  for b in 0..7 {for i in 0..4 {
   out.hessian[a][b]=ia(&out.hessian[a][b],&im(&raw.gradient[i],&gas[i].hessian[a][b])?)?;
   for j in 0..4 {out.hessian[a][b]=ia(&out.hessian[a][b],&im(&im(&raw.hessian[i][j],&gas[i].gradient[a])?,&gas[j].gradient[b])?)?;}
  }}
 }Ok(out)
}
#[derive(Clone,Debug)]
pub struct Phys04DerivativeExport {pub residual:[Jet;4],pub photons:Vec<Jet>,pub denominators:Vec<Jet>,pub rhs:[Jet;4],pub native_root_certified:bool}
pub fn phys04_reduced_residual(stage:&PrimaryStage,old:&[Jet;4],gas:&[Jet;4],incoming:&[Jet],energies:&[f64],lambda:&Jet,dt:f64)->Result<Phys04DerivativeExport,ForwardError>{
 PHYS04_DERIVATIVES.fetch_add(1,std::sync::atomic::Ordering::SeqCst);
 if !dt.is_finite()||dt<=0.0||incoming.len()!=energies.len()||lambda.value.lo<0.0||lambda.value.hi>1.0||incoming.iter().any(|j|j.value.lo<0.0){return Err(fail("PHYS04_PARAMETER_OR_LAYOUT"));}
 let mut m=model(stage)?;m.gas.sigma_cm2=[[0.0;3];3];
 let bx=gas.each_ref().map(|j|j.value);let dummy=ip(1.0)?;
 PHYS04_SOURCE_RHS.fetch_add(1,std::sync::atomic::Ordering::SeqCst);
 let raw=ft03_interval_rhs(&m,&[bx[0],bx[1],bx[2],bx[3],dummy,dummy,dummy])?;
 let mut f=[phys04_compose(&raw[0],gas)?,phys04_compose(&raw[1],gas)?,phys04_compose(&raw[2],gas)?,phys04_compose(&raw[3],gas)?];
 let q=phys04_compose(&hh_rate_jet(stage,&bx)?,gas)?;
 f[0]=jadd(&f[0],&jmul(lambda,&q)?)?;f[3]=jsub(&f[3],&jprod(&[ic(CHI[0])?,lambda.clone(),q])?)?;
 let lower=[jsub(&ic(1.0)?,&gas[0])?,jmul(&ic(stage.f_he)?,&jsub(&jsub(&ic(1.0)?,&gas[1])?,&gas[2])?)?,jmul(&ic(stage.f_he)?,&gas[1])?];
 let provider=AtomicProvider::reference();let mut photons=Vec::new();let mut denominators=Vec::new();
 for (n,e) in incoming.iter().zip(energies){
  let sigma=[provider.cross_section(Absorber::HI,*e)?,provider.cross_section(Absorber::HeI,*e)?,provider.cross_section(Absorber::HeII,*e)?];
  let mut opacity=ic(0.0)?;for a in 0..3 {opacity=jadd(&opacity,&jprod(&[ic(m.gas.c_cm_s)?,ic(stage.n_h_cm3)?,lower[a].clone(),ic(sigma[a])?])?)?;}
  let den=jadd(&ic(1.0)?,&jmul(&ic(dt)?,&opacity)?)?;
  if den.value.lo<=0.0{return Err(fail("PHYS04_POSITIVE_DENOMINATOR_MISSING"));}
  // Jet quotient retains N_a,N_b,N_ab even at zero stock, and both cross terms.
  let ph=jdiv(n,&den)?;let mut rates=[ic(0.0)?,ic(0.0)?,ic(0.0)?];
  for a in 0..3 {rates[a]=jprod(&[ic(m.gas.c_cm_s)?,ic(stage.n_h_cm3)?,lower[a].clone(),ic(sigma[a])?,ph.clone()])?;f[3]=jadd(&f[3],&jmul(&rates[a],&ic(*e-CHI[a])?)?)?;}
  f[0]=jadd(&f[0],&rates[0])?;f[1]=jadd(&f[1],&jdiv(&jsub(&rates[1],&rates[2])?,&ic(stage.f_he)?)?)?;f[2]=jadd(&f[2],&jdiv(&rates[2],&ic(stage.f_he)?)?)?;
  photons.push(ph);denominators.push(den);
 }
 f[3]=jsub(&f[3],&jprod(&[ic(2.0)?,ic(stage.h_mean_per_s)?,gas[3].clone()])?)?;
 let residual=[jsub(&jsub(&gas[0],&old[0])?,&jmul(&ic(dt)?,&f[0])?)?,jsub(&jsub(&gas[1],&old[1])?,&jmul(&ic(dt)?,&f[1])?)?,jsub(&jsub(&gas[2],&old[2])?,&jmul(&ic(dt)?,&f[2])?)?,jsub(&jsub(&gas[3],&old[3])?,&jmul(&ic(dt)?,&f[3])?)?];
 Ok(Phys04DerivativeExport{residual,photons,denominators,rhs:f,native_root_certified:false})
}
#[derive(Clone,Debug)]
pub struct Phys04MixedArithmetic {pub u:[Interval;4],pub v:[Interval;4],pub w:[Interval;4],pub photons:Vec<Jet>,pub matrix:[[Interval;4];4],pub fixed_c:[[f64;4];4],pub contraction:f64,pub native_root_certified:bool}
// C is computed once from the source centre Jacobian. Caller supplies only declared
// tangent boxes; strict fixed-C inclusion is arithmetic evidence, not root authority.
fn phys04_linear_image(a:&[[Interval;4];4],c:&[[f64;4];4],rhs:[Interval;4],box_: [Interval;4],scales:[f64;4])->Result<([Interval;4],f64),ForwardError>{
 PHYS04_LINEAR.fetch_add(1,std::sync::atomic::Ordering::SeqCst);
 let mut out=[ip(0.0)?;4];let mut q=0.0_f64;
 for i in 0..4 {let mut row=ip(0.0)?;
  for j in 0..4 {out[i]=ia(&out[i],&im(&ip(c[i][j])?,&rhs[j])?)?;}
  for k in 0..4 {let mut r=ip(if i==k{1.0}else{0.0})?;for j in 0..4 {r=is(&r,&im(&ip(c[i][j])?,&a[j][k])?)?;}
   out[i]=ia(&out[i],&im(&r,&box_[k])?)?;row=ia(&row,&im(&ip(r.lo.abs().max(r.hi.abs()))?,&ip(scales[k])?.div(&ip(scales[i])?).map_err(ie)?)?)?;
  }q=q.max(row.hi);
  if !(box_[i].lo<out[i].lo&&out[i].hi<box_[i].hi){return Err(fail("PHYS04_TANGENT_INCLUSION_OPEN"));}
 }if q>=1.0{return Err(fail("PHYS04_TANGENT_CONTRACTION_OPEN"));}Ok((out,q))
}
pub fn phys04_mixed_at_box(stage:&PrimaryStage,old:&[Jet;4],gas:[Interval;4],incoming:&[Jet],energies:&[f64],lambda:Interval,dt:f64,candidates:[[Interval;4];3])->Result<Phys04MixedArithmetic,ForwardError>{
 let y=std::array::from_fn(|i|Jet::variable(gas[i],i).unwrap());let lam=phys04_parameter(lambda,4)?;
 let jac=phys04_reduced_residual(stage,old,&y,incoming,energies,&lam,dt)?;
 let matrix=std::array::from_fn(|i|std::array::from_fn(|j|jac.residual[i].gradient[j]));
 let centre=gas.map(|v|ip(v.lo+(v.hi-v.lo)/2.0).unwrap());
 let centre_y=std::array::from_fn(|i|Jet::variable(centre[i],i).unwrap());
 let centre_lam=Jet::constant(ip(lambda.lo+(lambda.hi-lambda.lo)/2.0)?).map_err(ie)?;
 let centre_n=incoming.iter().map(|j|Jet::constant(ip(j.value.lo+(j.value.hi-j.value.lo)/2.0)?).map_err(ie)).collect::<Result<Vec<_>,_>>()?;
 let centre_jac=phys04_reduced_residual(stage,old,&centre_y,&centre_n,energies,&centre_lam,dt)?;
 let c=inverse4(std::array::from_fn(|i|std::array::from_fn(|j|{let x=centre_jac.residual[i].gradient[j];x.lo+(x.hi-x.lo)/2.0})))?;
 let scales=[1.0,1.0,1.0,centre[3].lo];
 let (u,qu)=phys04_linear_image(&matrix,&c,jac.residual.each_ref().map(|j|j.gradient[4].neg().unwrap()),candidates[0],scales)?;
 let (v,qv)=phys04_linear_image(&matrix,&c,jac.residual.each_ref().map(|j|j.gradient[5].neg().unwrap()),candidates[1],scales)?;
 let z=ip(0.0)?;let mixed_y=[phys04_carry(gas[0],u[0],v[0],z)?,phys04_carry(gas[1],u[1],v[1],z)?,phys04_carry(gas[2],u[2],v[2],z)?,phys04_carry(gas[3],u[3],v[3],z)?];
 let forcing=phys04_reduced_residual(stage,old,&mixed_y,incoming,energies,&lam,dt)?;
 let (w,qw)=phys04_linear_image(&matrix,&c,forcing.residual.each_ref().map(|j|j.hessian[4][5].neg().unwrap()),candidates[2],scales)?;
 let final_y=[phys04_carry(gas[0],u[0],v[0],w[0])?,phys04_carry(gas[1],u[1],v[1],w[1])?,phys04_carry(gas[2],u[2],v[2],w[2])?,phys04_carry(gas[3],u[3],v[3],w[3])?];
 let final_=phys04_reduced_residual(stage,old,&final_y,incoming,energies,&lam,dt)?;
 Ok(Phys04MixedArithmetic{u,v,w,photons:final_.photons,matrix,fixed_c:c,contraction:qu.max(qv).max(qw),native_root_certified:false})
}
