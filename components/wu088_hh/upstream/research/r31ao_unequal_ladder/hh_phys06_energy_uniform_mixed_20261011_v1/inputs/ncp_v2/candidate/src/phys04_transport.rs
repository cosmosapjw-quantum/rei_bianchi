// Geometry/clock fixed in lambda,b; all signed Jet slots follow the same map.
#[derive(Clone,Debug)]
pub struct Phys04PreBE {
 pub gas:[Jet;4],pub photons:Vec<Jet>,pub guard_n:Vec<Jet>,pub guard_u:Vec<Jet>,
 pub groups:Vec<Jet>,pub energies:Vec<f64>,pub stage:PrimaryStage,
 pub time_s:f64,pub dt:f64,pub source_n:Jet,pub source_u:Jet,
 pub source_weights:Vec<Interval>,pub guard_exports:usize,
 input_words:Vec<u64>,output_words:Vec<u64>,source_bytes:Vec<u8>,
}
fn phys04_zero_jet(j:&Jet)->bool{j.value.lo==0.0&&j.value.hi==0.0&&j.gradient.iter().chain(j.hessian.iter().flatten()).all(|x|x.lo==0.0&&x.hi==0.0)}
pub fn phys04_prepare_family(c:&PairedConfig,h:[f64;3],time:f64,dt:f64,gas:&[Jet;4],photons:&[Jet],gn:&[Jet],gu:&[Jet],b:&Jet)->Result<Phys04PreBE,ForwardError>{
 if c.spectral_subdivisions!=8||c.n_mu!=8||c.n_phi!=16{return Err(fail("PHYS04_FIXED_GRID_IDENTITY"));}
 let nodes=energy_nodes(c)?;let nd=directions(c)?;let n=nodes.len();
 if n!=33||nd!=128||photons.len()!=nd*n||gn.len()!=nd||gu.len()!=nd||h.iter().any(|x|!x.is_finite()||*x<0.0)||!time.is_finite()||!dt.is_finite()||dt<=0.0||time<0.0||time+dt>1e13||b.value.lo<0.0||b.value.hi>1.0 {return Err(fail("PHYS04_TRANSPORT_IDENTITY"));}
 for j in gas.iter().chain(photons).chain(gn).chain(gu).chain(std::iter::once(b)){j.add(&Jet::constant(p(0.0)?).map_err(ie)?).map_err(ie)?;}
 if photons.iter().chain(gn).chain(gu).any(|j|j.value.lo<0.0){return Err(fail("PHYS04_PHYSICAL_STOCK_SIGN"));}
 let zero=Jet::constant(p(0.0)?).map_err(ie)?;let mut out=vec![zero.clone();photons.len()];let mut guard_n=gn.to_vec();let mut guard_u=gu.to_vec();let mut exports=0;
 for d in 0..nd {
  let rb=if h==[0.0;3]{p(1.0)?}else{div(g_box(qhat(c,d),h,time+dt)?,g_box(qhat(c,d),h,time)?)?};
  let rj=Jet::constant(rb).map_err(ie)?;guard_u[d]=gu[d].mul(&rj).map_err(ie)?;
  for j in 0..n {
   let eb=mul(p(nodes[j])?,rb)?;let x=&photons[d*n+j];
   if eb.hi>20.0 {return Err(fail("PHYS04_UPPER_GUARD_UNSUPPORTED"));}
   if eb.hi<10.0 {guard_n[d]=guard_n[d].add(x).map_err(ie)?;guard_u[d]=guard_u[d].add(&x.mul(&Jet::constant(eb).map_err(ie)?).map_err(ie)?).map_err(ie)?;exports+=1;continue;}
   if eb.lo<10.0{return Err(fail("PHYS04_GUARD_BRANCH_CROSSING"));}
   // A geometry enclosure straddling a hat knot needs a piecewise proof.
   if nodes.iter().any(|k|eb.lo<*k&&*k<eb.hi){return Err(fail("PHYS04_HAT_BRANCH_CROSSING"));}
   if phys04_zero_jet(x){continue;}
   for k in 0..n {let weight=hat_box(eb,&nodes,k)?;if weight.lo==0.0&&weight.hi==0.0{continue;}out[d*n+k]=out[d*n+k].add(&x.mul(&Jet::constant(weight).map_err(ie)?).map_err(ie)?).map_err(ie)?;}
  }
 }
 let (_,wb)=source_weights(c,h,time+dt)?;
 let source_n=b.mul(&Jet::constant(p(dt*SOURCE)?).map_err(ie)?).map_err(ie)?;
 let source_u=source_n.mul(&Jet::constant(p(BIRTH)?).map_err(ie)?).map_err(ie)?;
 for d in 0..nd {let born=source_n.mul(&Jet::constant(wb[d]).map_err(ie)?).map_err(ie)?;let i=d*n+3*c.spectral_subdivisions;out[i]=out[i].add(&born).map_err(ie)?;}
 // Retain all fixed nodes, including zero stock with nonzero signed forcing.
 let mut groups=vec![zero;n];for d in 0..nd {for k in 0..n {groups[k]=groups[k].add(&out[d*n+k]).map_err(ie)?;}}
 // Only physical values have a proven nonnegative cone. Tangents remain signed.
 for j in out.iter_mut().chain(&mut groups).chain(&mut guard_n).chain(&mut guard_u){j.value=nonneg(j.value)?;}
 let mut pre=Phys04PreBE{gas:gas.clone(),photons:out,guard_n,guard_u,groups,energies:nodes,stage:PrimaryStage{n_h_cm3:1e-4*(-h.iter().sum::<f64>()*(time+dt)).exp(),f_he:FHE,h_mean_per_s:h.iter().sum::<f64>()/3.0},time_s:time+dt,dt,source_n,source_u,source_weights:wb,guard_exports:exports,input_words:phys04_frame_words(h,time,dt,gas,photons,gn,gu,b),output_words:Vec::new(),source_bytes:phys04_transport_source_bytes()};pre.output_words=phys04_prebe_words(&pre);Ok(pre)
}
pub fn phys04_distribute_after_be(pre:&Phys04PreBE,gas:&[Jet;4])->Result<Vec<Jet>,ForwardError>{
 let provider=AtomicProvider::reference();let one=Jet::constant(p(1.0)?).map_err(ie)?;
 let lower=[one.sub(&gas[0]).map_err(ie)?,one.sub(&gas[1]).map_err(ie)?.sub(&gas[2]).map_err(ie)?.mul(&Jet::constant(p(FHE)?).map_err(ie)?).map_err(ie)?,gas[1].mul(&Jet::constant(p(FHE)?).map_err(ie)?).map_err(ie)?];
 let mut out=Vec::with_capacity(pre.photons.len());
 for (i,n) in pre.photons.iter().enumerate(){let e=pre.energies[i%33];let sigma=[provider.cross_section(Absorber::HI,e)?,provider.cross_section(Absorber::HeI,e)?,provider.cross_section(Absorber::HeII,e)?];let mut opacity=Jet::constant(p(0.0)?).map_err(ie)?;
  for a in 0..3 {opacity=opacity.add(&lower[a].mul(&Jet::constant(p(sigma[a]*29979245800.0*pre.stage.n_h_cm3)?).map_err(ie)?).map_err(ie)?).map_err(ie)?;}
  let den=one.add(&opacity.mul(&Jet::constant(p(pre.dt)?).map_err(ie)?).map_err(ie)?).map_err(ie)?;
  if den.value.lo<=0.0||n.value.lo<0.0{return Err(fail("PHYS04_POSITIVE_DENOMINATOR_MISSING"));}
  let mut next=n.div(&den).map_err(ie)?;next.value=nonneg(next.value)?;out.push(next);
 }Ok(out)
}
impl Phys04PreBE {
 pub fn validate_family_input(&self,h:[f64;3],time:f64,dt:f64,gas:&[Jet;4],photons:&[Jet],gn:&[Jet],gu:&[Jet],b:Interval)->Result<(),ForwardError>{
  let mut expected_b=Jet::variable(b,5).map_err(ie)?;
  // Lambda and b have no geometry slots; b is the direct source parameter.
  expected_b.hessian=[[p(0.0)?;7];7];
  let input=phys04_frame_words(h,time,dt,gas,photons,gn,gu,&expected_b);
  if input!=self.input_words||phys04_prebe_words(self)!=self.output_words||self.source_bytes!=phys04_transport_source_bytes(){return Err(fail("PHYS04_PREBE_SOURCE_PARAMETER_PROVENANCE"));}Ok(())
 }
}
fn phys04_jet_words(j:&Jet,out:&mut Vec<u64>){for v in std::iter::once(&j.value).chain(j.gradient.iter()).chain(j.hessian.iter().flatten()){out.extend([v.lo.to_bits(),v.hi.to_bits()]);}}
fn phys04_frame_words(h:[f64;3],time:f64,dt:f64,gas:&[Jet;4],photons:&[Jet],gn:&[Jet],gu:&[Jet],b:&Jet)->Vec<u64>{let mut out=h.map(f64::to_bits).to_vec();out.extend([time.to_bits(),dt.to_bits()]);for j in gas.iter().chain(photons).chain(gn).chain(gu).chain(std::iter::once(b)){phys04_jet_words(j,&mut out);}out}
fn phys04_prebe_words(pre:&Phys04PreBE)->Vec<u64>{let mut out=vec![pre.time_s.to_bits(),pre.dt.to_bits(),pre.stage.n_h_cm3.to_bits(),pre.stage.f_he.to_bits(),pre.stage.h_mean_per_s.to_bits(),pre.guard_exports as u64];for j in pre.gas.iter().chain(&pre.photons).chain(&pre.guard_n).chain(&pre.guard_u).chain(&pre.groups).chain([&pre.source_n,&pre.source_u]){phys04_jet_words(j,&mut out);}out.extend(pre.energies.iter().map(|x|x.to_bits()));for x in &pre.source_weights{out.extend([x.lo.to_bits(),x.hi.to_bits()]);}out}
fn phys04_transport_source_bytes()->Vec<u8>{[include_bytes!("paired_runtime.rs").as_slice(),include_bytes!("phys04_transport.rs").as_slice(),include_bytes!("interval_ad.rs").as_slice(),include_bytes!("interval_math.rs").as_slice()].concat()}
