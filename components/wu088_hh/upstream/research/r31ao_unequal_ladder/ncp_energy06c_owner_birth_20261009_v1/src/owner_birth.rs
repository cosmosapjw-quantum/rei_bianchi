// Opt-in source-bound owner adapter. Default owner runtime is never modified.
// Native parameter family certificates are absent: no permit can be issued.
#[derive(Clone,Debug)]pub struct BirthLaw {pub source_bits:u64,pub energy_bits:u64,pub policy:&'static str}
#[derive(Clone,Debug)]pub struct StepScheme {pub label:&'static str,pub times:[f64;2],pub steps:[f64;2],pub stages:usize}
pub fn source_law()->BirthLaw{BirthLaw{source_bits:SOURCE.to_bits(),energy_bits:BIRTH.to_bits(),policy:"OWNER_SOURCE_WEIGHTS_AT_ENDPOINT_BIRTH_BEFORE_BE"}}
pub fn schemes(t:f64,h:f64)->Result<[StepScheme;2],ForwardError>{
 if t.to_bits()!=1.6e11_f64.to_bits()||h.to_bits()!=1.25e9_f64.to_bits(){return Err(fail("ENERGY06C_CLOCK"));}
 Ok([StepScheme{label:"full_diagnostic",times:[t+h,t+h],steps:[h,0.0],stages:1},StepScheme{label:"twohalf_accepted_only",times:[t+h/2.0,t+h],steps:[h/2.0,h/2.0],stages:2}])
}
pub fn contract_valid(clock:f64,lambda:f64,origin:&str,law:&str,angle:&str)->bool{
 clock.to_bits()==1.6e11_f64.to_bits()&&lambda.to_bits()==1.0_f64.to_bits()&&origin=="ON06G"&&law=="original"&&angle=="128x33"
}
pub fn accepted_events(_full:f64,a:f64,b:f64)->f64{a+b}
pub fn carry_rhs(previous:f64,birth:f64,photon:f64,hh:f64)->f64{previous+birth+photon+hh}
// No authorization issuance API. The private token is unavailable to callers.
struct ExactSciencePermit { _private:() }
pub fn scientific_dispatch_requested()->Result<(),ForwardError>{Err(fail("ENERGY06C_EXACT_AUTHORIZATION_MISSING"))}
fn actual_full(_permit:&ExactSciencePermit,c:&HhRunConfig,s:&HhPairedState,dt:f64)->Result<(HhPairedState,String,f64,[f64;2]),ForwardError>{
 hh_check(c,s)?;let nodes=energy_nodes(c.grid())?;
 if c.mode()==HhMode::Off {let (b,a,l)=endpoint(c.grid(),c.hubble(),s.base(),dt,&nodes)?;Ok((HhPairedState{base:b,..s.clone()},a,l,[0.0;2]))}
 else{hh_endpoint_state(c,s,dt,&nodes)}
}
fn actual_twohalf(p:&ExactSciencePermit,c:&HhRunConfig,s:&HhPairedState,dt:f64)->Result<(HhPairedState,[String;2],f64,[[f64;2];2]),ForwardError>{
 let (half,a,l,e)=actual_full(p,c,s,dt/2.0)?;let (two,b,m,f)=actual_full(p,c,&half,dt/2.0)?;Ok((two,[a,b],l.max(m),[e,f]))
}
fn actual_linked_chain(p:&ExactSciencePermit,c:&HhRunConfig,s:&HhPairedState,dt:f64)->Result<HhPairedTrial,ForwardError>{
 let (full,a,l,e)=actual_full(p,c,s,dt)?;let (two,ab,m,ef)=actual_twohalf(p,c,s,dt)?;
 let nodes=energy_nodes(c.grid())?;let local=difference(full.base(),two.base(),&nodes)?;let public=width(two.base(),&nodes)?;let ledger=l.max(m);
 if local>=2e-4{return Err(fail("PAIRED_LOCAL_GATE"));}if public>=2e-3{return Err(fail("PAIRED_WIDTH_GATE"));}if ledger>1e-12{return Err(fail("PAIRED_LEDGER_GATE"));}
 Ok(HhPairedTrial{state:two,local_bound:local,public_width:public,max_ledger:ledger,audits:vec![a,ab[0].clone(),ab[1].clone()],source_hh_events:[e[0],ef[0][0],ef[1][0]],source_hh_heat:[e[1],ef[0][1],ef[1][1]]})
}
#[derive(Debug)]pub struct Prebirth {pub photons:Vec<f64>,pub boxes:Vec<Interval>,pub weights:Vec<f64>,pub source_n:f64,pub source_u:f64,pub transport_n:f64,pub transport_u:f64,pub redshift_loss:f64,pub groups:Vec<f64>,pub group_boxes:Vec<Interval>,pub index:Vec<usize>}
// Body extracted verbatim from the pinned actual HH endpoint through pre-BE grouping.
// No stage solve, root certificate, endpoint acceptance or HH q call is made.
pub fn prepare_actual_birth(c:&PairedConfig,h:[f64;3],s:&PairedState,dt:f64,nodes:&[f64])->Result<Prebirth,ForwardError>{
 let canonical=energy_nodes(c)?;
 if c.spectral_subdivisions!=8||c.n_mu!=8||c.n_phi!=16||nodes.len()!=canonical.len()||!nodes.iter().zip(&canonical).all(|(a,b)|a.to_bits()==b.to_bits())||s.time_s.to_bits()!=1.6e11_f64.to_bits()||![1.25e9_f64.to_bits(),6.25e8_f64.to_bits()].contains(&dt.to_bits())||!(h==[1e-14;3]||h==[1.01e-14,0.99e-14,1e-14]){return Err(fail("ENERGY06C_OWNER_INPUT_BINDING"));}
 validate(c,s,nodes)?;
 if !dt.is_finite()||dt<=0.0{return Err(fail("ENERGY06C_PREPARE_CLOCK"));}
    let n=nodes.len();let nd=directions(c)?;let t1=s.time_s+dt;
    let background=ConstantHubbleBackground::new([1.0;3],h)?;
    let snapshot0=background.snapshot(s.time_s)?;let snapshot1=background.snapshot(t1)?;
    let mut transported=vec![0.0;nd*n];let mut tb=vec![p(0.0)?;nd*n];
    let mut guard_n=s.lower_guard_n.clone();let mut guard_u=vec![0.0;nd];
    let mut guard_nb=s.lower_guard_n_box.clone();let mut guard_ub=vec![p(0.0)?;nd];
    for d in 0..nd {let q=qhat(c,d);let r=g_point(q,h,t1)/g_point(q,h,s.time_s);
        let e0=[q[0]*(-h[0]*s.time_s).exp(),q[1]*(-h[1]*s.time_s).exp(),q[2]*(-h[2]*s.time_s).exp()];
        let e0norm=e0[0].hypot(e0[1]).hypot(e0[2]);
        let ray=CharacteristicRay::new(BIRTH,e0.map(|x|x/e0norm),0.0)?;
        let pulled=ray.pullback(&snapshot0,&snapshot1)?;
        if (pulled.energy_ev/BIRTH-r).abs()>1e-12 {return Err(fail("PAIRED_CHARACTERISTIC_PARITY"));}
        let rb=div(g_box(q,h,t1)?,g_box(q,h,s.time_s)?)?;
        if !r.is_finite() || r<=0.0 || !contains(rb,r){return Err(fail("PAIRED_REDSHIFT_RANGE"));}
        guard_u[d]=s.lower_guard_u[d]*r;
        guard_ub[d]=nonneg(widened(mul(s.lower_guard_u_box[d],rb)?,guard_u[d])?)?;
        for j in 0..n {let old=s.photons[d*n+j];let ob=s.photon_boxes[d*n+j];if old==0.0 && ob.hi==0.0{continue;}
            let e=nodes[j]*r;let eb=mul(p(nodes[j])?,rb)?;
            if e>20.0 || eb.hi>20.0{return Err(fail("PAIRED_UPPER_GUARD_UNIMPLEMENTED"));}
            if eb.lo<10.0 {
                let exported=if e<10.0 {old}else{0.0};
                let possible=if eb.hi<10.0 {ob}else{Interval::new(0.0,ob.hi).map_err(ie)?};
                guard_n[d]+=exported;guard_u[d]+=exported*e;
                guard_nb[d]=add_nonneg(guard_nb[d],possible)?;
                guard_ub[d]=add_nonneg(guard_ub[d],nonneg(mul(possible,eb)?)?)?;
            }
            if e<10.0 && eb.hi<10.0 {continue;}
            for k in 0..n {let a=if e<10.0 {0.0}else{hat(e,nodes,k)};let mut ab=hat_box(eb,nodes,k)?;
                if eb.lo<10.0 {ab=Interval::new(0.0,ab.hi).map_err(ie)?;}
                if a==0.0 && ab.hi==0.0{continue;}
                transported[d*n+k]+=old*a;
                tb[d*n+k]=add_nonneg(tb[d*n+k],nonneg(mul(ob,ab)?)?)?;
            }
        }
        guard_nb[d]=nonneg(widened(guard_nb[d],guard_n[d])?)?;
        guard_ub[d]=nonneg(widened(guard_ub[d],guard_u[d])?)?;
    }
    for i in 0..transported.len(){tb[i]=nonneg(widened(tb[i],transported[i])?)?;}
    let old_u=photon_energy(s,nodes);let transport_u=weighted_sum(&transported.iter().enumerate().map(|(i,x)|x*nodes[i%n]).chain(guard_u.iter().copied()).collect::<Vec<_>>());
    let old_n=photon_number(s);let transport_n=weighted_sum(&transported.iter().copied().chain(guard_n.iter().copied()).collect::<Vec<_>>());
    let redshift_loss=old_u-transport_u;
    if redshift_loss < -1e-12 || !redshift_loss.is_finite(){return Err(fail("PAIRED_REDSHIFT_LEDGER"));}
    let (weights,wb)=source_weights(c,h,t1)?;let source_n=dt*SOURCE;let source_u=source_n*BIRTH;let birth_index=3*c.spectral_subdivisions;
    for d in 0..nd {let i=d*n+birth_index;let z=source_n*weights[d];transported[i]+=z;tb[i]=nonneg(widened(add_nonneg(tb[i],mul(p(source_n)?,wb[d])?)?,transported[i])?)?;}
    let mut groups=vec![0.0;n];let mut gc=vec![0.0;n];let mut gb=vec![p(0.0)?;n];
    for d in 0..nd {for k in 0..n {let z=accumulate(groups[k],gc[k],transported[d*n+k]);groups[k]=z.0;gc[k]=z.1;gb[k]=add_nonneg(gb[k],tb[d*n+k])?;}}
    for k in 0..n {gb[k]=nonneg(widened(gb[k],groups[k])?)?;}
    let index:Vec<usize>=(0..n).filter(|&k|groups[k]>0.0 || gb[k].hi>0.0).collect();
    let packets=index.iter().map(|&k|PrimaryPacket{energy_ev:nodes[k],per_h:groups[k]}).collect::<Vec<_>>();

 let _=(packets,old_n);
 Ok(Prebirth{photons:transported,boxes:tb,weights,source_n,source_u,transport_n,transport_u,redshift_loss,groups,group_boxes:gb,index})
}
// Point minus enclosing root is not a root-family certificate.
pub fn enclosing_defect(full:&[Interval],two:&[Interval])->Result<Vec<Interval>,ForwardError>{
 if full.len()!=two.len()||full.is_empty(){return Err(fail("ENERGY06C_DEFECT_SHAPE"));}
 full.iter().zip(two).map(|(f,t)|sub(*t,*f)).collect()
}
pub fn validate_tangent(gas:&[f64],photons:&[f64],energies:&[f64],angles:usize)->Result<(),ForwardError>{
 let canonical=energy_nodes(&PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16})?;
 if gas.len()!=4||photons.len()!=4224||energies.len()!=33||angles!=128||gas.iter().chain(photons).chain(energies).any(|x|!x.is_finite())||!energies.iter().zip(&canonical).all(|(a,b)|a.to_bits()==b.to_bits()){return Err(fail("ENERGY06C_TANGENT_LABELS"));}Ok(())
}
fn cfg(member:usize)->Result<HhRunConfig,ForwardError>{HhRunConfig::new(PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16},if member<2{[1e-14;3]}else{[1.01e-14,0.99e-14,1e-14]},if member%2==0{HhMode::Off}else{HhMode::Lcs91})}
pub fn audit_cli()->Result<(),Box<dyn std::error::Error>>{
 let args=std::env::args().collect::<Vec<_>>();if args.len()!=2{return Err("usage: owner_birth_probe SEED_DIR (read-only pre-BE audit only)".into());}
 for member in 0..4{
  let bytes=std::fs::read(std::path::Path::new(&args[1]).join(format!("member{member}.bin")))?;let c=cfg(member)?;let s=hh_checkpoint_decode(&c,&bytes)?;let native=rei_microphysics::paired_runtime::hh_checkpoint_decode(&rei_microphysics::paired_runtime::HhRunConfig::new(rei_microphysics::paired_runtime::PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16},c.hubble(),c.mode())?,&bytes)?;
  if hh_checkpoint_encode(&c,&s)?!=bytes||native.base().photons!=s.base.photons{return Err("checkpoint independent decoder mismatch".into());}
  schemes(s.base.time_s,1.25e9)?;let nodes=energy_nodes(c.grid())?;
  for (label,dt) in [("full_preBE",1.25e9),("half1_preBE",6.25e8)]{
   let b=prepare_actual_birth(c.grid(),c.hubble(),s.base(),dt,&nodes)?;
   println!("{{\"member\":{member},\"label\":\"{label}\",\"initial_time\":{:?},\"endpoint_time\":{:?},\"source_bits\":\"{:016x}\",\"birth_energy_bits\":\"{:016x}\",\"source_n\":{:?},\"source_u\":{:?},\"transport_n\":{:?},\"transport_u\":{:?},\"redshift_loss\":{:?},\"source_weights\":{:?},\"groups\":{:?},\"indices\":{:?},\"photons\":{},\"native_roundtrip\":true,\"root_dispatch\":0}}",s.base.time_s,s.base.time_s+dt,SOURCE.to_bits(),BIRTH.to_bits(),b.source_n,b.source_u,b.transport_n,b.transport_u,b.redshift_loss,b.weights,b.groups,b.index,b.photons.len());
  }
  let (w,_)=source_weights(c.grid(),c.hubble(),s.base.time_s+1.25e9)?;println!("{{\"member\":{member},\"label\":\"half2_birth_weights_only\",\"source_n\":{:?},\"source_weights\":{:?},\"half2_incoming_state\":null,\"root_dispatch\":0}}",6.25e8*SOURCE,w);
 }
 Ok(())
}
include!("owner_tests.rs");
// Compile-only actual local lambda tangent. It needs a matching birth-included
// stage certificate, incoming derivatives, and a caller-supplied enclosing box.
// Neither certificate nor science permit is issued by this preparation tool.
fn linked_tangent_stage(_permit:&ExactSciencePermit,stage:&crate::coupled_primary::PrimaryStage,old:&crate::coupled_primary::PrimaryState,parent:&crate::coupled_primary::PrimaryBox,root:&crate::coupled_primary::HhRoot,dt:f64,incoming:[Interval;4],packet_lambda:&[Interval],preconditioner:[[f64;4];4],candidate:[Interval;4])->Result<([Interval;4],Interval,Interval),ForwardError>{
 use crate::coupled_primary::{hh_root_matches,hh_rate_jet,hh_interval_source};
 let control=StepControl{max_iterations:200,residual_tolerance:1e-15};
 if !hh_root_matches(root,stage,old,parent,dt,control,HhMode::Lcs91)||packet_lambda.len()!=old.packets.len(){return Err(fail("ENERGY06C_TANGENT_ROOT_IDENTITY"));}
 let gas=&root.root.gas;let (jets,_)=hh_interval_source(stage,old,gas,&parent.photons,dt,HhMode::Lcs91)?;let q=hh_rate_jet(stage,gas)?;
 let mut rhs=incoming;let cdt=mul(p(dt)?,mul(p(29979245800.0)?,p(stage.n_h_cm3)?)?)?;
 let provider=AtomicProvider::reference();
 for (packet,dn) in old.packets.iter().zip(packet_lambda){
  let sig=[provider.cross_section(Absorber::HI,packet.energy_ev)?,provider.cross_section(Absorber::HeI,packet.energy_ev)?,provider.cross_section(Absorber::HeII,packet.energy_ev)?];
  let lower=[sub(p(1.0)?,gas[0])?,mul(p(FHE)?,sub(sub(p(1.0)?,gas[1])?,gas[2])?)?,mul(p(FHE)?,gas[1])?];
  let mut opacity=p(0.0)?;for a in 0..3{opacity=add(opacity,mul(lower[a],p(sig[a])?)?)?;}
  let den=add(p(1.0)?,mul(cdt,opacity)?)?;let mut absorbed=[p(0.0)?;3];
  for a in 0..3{absorbed[a]=div(mul(mul(cdt,lower[a])?,mul(p(sig[a])?,*dn)?)?,den)?;}
  rhs[0]=add(rhs[0],absorbed[0])?;rhs[1]=add(rhs[1],div(sub(absorbed[1],absorbed[2])?,p(FHE)?)?)?;rhs[2]=add(rhs[2],div(absorbed[2],p(FHE)?)?)?;
  for a in 0..3{rhs[3]=add(rhs[3],mul(absorbed[a],sub(p(packet.energy_ev)?,p(CHI[a])?)?)?)?;}
 }
 rhs[0]=add(rhs[0],mul(p(dt)?,q.value)?)?;rhs[3]=sub(rhs[3],mul(mul(p(dt)?,p(CHI[0])?)?,q.value)?)?;
 let mut matrix=[[p(0.0)?;4];4];for i in 0..4{for j in 0..4{matrix[i][j]=sub(p(if i==j{1.0}else{0.0})?,mul(p(dt)?,jets[i].gradient[j])?)?;}}
 let mut image=[p(0.0)?;4];let mut maxnorm=0.0_f64;
 for i in 0..4{
  let mut norms=[0.0;4];for j in 0..4{image[i]=add(image[i],mul(p(preconditioner[i][j])?,rhs[j])?)?;}
  for k in 0..4{let mut r=p(if i==k{1.0}else{0.0})?;for j in 0..4{r=sub(r,mul(p(preconditioner[i][j])?,matrix[j][k])?)?;}norms[k]=r.lo.abs().max(r.hi.abs());image[i]=add(image[i],mul(r,candidate[k])?)?;}
  maxnorm=maxnorm.max(norm_upper(norms)?);
  if !(image[i].lo>candidate[i].lo&&image[i].hi<candidate[i].hi){return Err(fail("ENERGY06C_TANGENT_INCLUSION_OPEN"));}
 }
 if maxnorm>=1.0{return Err(fail("ENERGY06C_TANGENT_CONTRACTION_OPEN"));}
 let mut dq=q.value;for j in 0..4{dq=add(dq,mul(q.gradient[j],image[j])?)?;}
 let dj=mul(p(dt)?,dq)?;let heat=mul(p(-CHI[0])?,dj)?;Ok((image,dj,heat))
}
// For fixed theta, lambda changes HH only. Remap is linear in incoming photons;
// no division by old stock and no reset at the second source is used. Geometry,
// energy or angle parameter derivatives require a separate family proof.
#[derive(Debug)]struct PhotonTangent { photons:Vec<Interval>,guard_n:Vec<Interval>,guard_u:Vec<Interval> }
fn hull_zero(x:Interval)->Result<Interval,ForwardError>{Interval::new(x.lo.min(0.0),x.hi.max(0.0)).map_err(ie)}
fn remap_lambda_fixed_theta(c:&PairedConfig,h:[f64;3],time:f64,dt:f64,nodes:&[f64],incoming:&[Interval],guard_n:&[Interval],guard_u:&[Interval])->Result<PhotonTangent,ForwardError>{
 let canonical=energy_nodes(c)?;
 if nodes.len()!=33||incoming.len()!=4224||directions(c)?!=128||guard_n.len()!=128||guard_u.len()!=128||!nodes.iter().zip(&canonical).all(|(a,b)|a.to_bits()==b.to_bits()){return Err(fail("ENERGY06C_REMAP_TANGENT_LABELS"));}
 for x in incoming.iter().chain(guard_n).chain(guard_u){Interval::new(x.lo,x.hi).map_err(ie)?;}
 let mut result=vec![p(0.0)?;incoming.len()];let mut gn=guard_n.to_vec();let mut gu=guard_u.to_vec();
 for d in 0..128{let q=qhat(c,d);let rb=div(g_box(q,h,time+dt)?,g_box(q,h,time)?)?;gu[d]=mul(guard_u[d],rb)?;
  for j in 0..33{
   let dn=incoming[d*33+j];Interval::new(dn.lo,dn.hi).map_err(ie)?;
   if dn.lo==0.0&&dn.hi==0.0{continue;}
   let eb=mul(p(nodes[j])?,rb)?;
   if eb.hi>20.0{return Err(fail("ENERGY06C_TANGENT_UPPER_GUARD_UNSUPPORTED"));}
   if eb.lo<10.0 {let exported=if eb.hi<10.0{dn}else{hull_zero(dn)?};gn[d]=add(gn[d],exported)?;gu[d]=add(gu[d],mul(exported,eb)?)?;}
   if eb.hi<10.0{continue;}
   for k in 0..33{let ab=hat_box(eb,nodes,k)?;let contribution=mul(dn,ab)?;result[d*33+k]=add(result[d*33+k],if eb.lo<10.0{hull_zero(contribution)?}else{contribution})?;}
  }
 }
 Ok(PhotonTangent{photons:result,guard_n:gn,guard_u:gu})
}
fn norm_upper(values:[f64;4])->Result<f64,ForwardError>{let mut n=p(0.0)?;for x in values{if x<0.0{return Err(fail("ENERGY06C_NORM_DOMAIN"));}n=add(n,p(x)?)?;}Ok(n.hi)}
