
// HH-ON06B: source-consistent opt-in at the actual F08 endpoint and trial seam.
// The original OFF functions above remain byte-identical. No new history driver
// or physical opacity prescription is defined here.
use crate::coupled_primary::{HhMode,hh_stage_step_conservative,hh_stage_root,hh_return_enclosure};
pub const HH_PAIRED_MODEL_ID:&str="HH_ON06B_FT03_LCS_FIXED_GRID_BINARY64_REAL_V1";
#[derive(Clone,Debug,PartialEq,Eq)]
struct HhRunIdentity {schema:u32,words:Vec<u64>}
#[derive(Clone,Debug)]
pub struct HhRunConfig {grid:PairedConfig,hubble:[f64;3],mode:HhMode,identity:HhRunIdentity}
impl HhRunConfig {
 pub fn new(grid:PairedConfig,hubble:[f64;3],mode:HhMode)->Result<Self,ForwardError>{
  energy_nodes(&grid)?;
  if hubble.iter().any(|x|!x.is_finite() || *x<0.0) || !hubble.iter().sum::<f64>().is_finite(){return Err(fail("HH_PAIRED_CONFIG"));}
  // Bind the grid, geometry, provider, source/thermal constants and fixed gates.
  // The identity is a versioned in-process input token, not a proof validator.
  let mut words=vec![grid.spectral_subdivisions as u64,grid.n_mu as u64,grid.n_phi as u64,if mode==HhMode::Off{0}else{1}];
  words.extend(hubble.map(f64::to_bits));
  words.extend([SOURCE,BIRTH,FHE,CHI[0],CHI[1],CHI[2],29979245800.0,1.380649e-16,1.602176634e-12,1.2e-17,1.2,157800.0,1e-4,1e-15,2e-4,2e-3,1e-12,35000.0,60000.0].map(f64::to_bits));
  words.push(200);
  Ok(Self{grid,hubble,mode,identity:HhRunIdentity{schema:1,words}})
 }
 pub fn mode(&self)->HhMode{self.mode}
 pub fn grid(&self)->&PairedConfig{&self.grid}
 pub fn hubble(&self)->[f64;3]{self.hubble}
}
#[derive(Clone,Debug)]
pub struct HhPairedState {base:PairedState,hh_events:f64,hh_heat:f64,hh_comp:[f64;2],identity:HhRunIdentity}
impl HhPairedState {
 pub fn base(&self)->&PairedState{&self.base}
 pub fn hh_events_per_h(&self)->f64{self.hh_events}
 pub fn hh_heat_ev_per_h(&self)->f64{self.hh_heat}
 pub fn hh_compensation(&self)->[f64;2]{self.hh_comp}
}
#[derive(Clone,Debug)]
pub struct HhPairedTrial {pub state:HhPairedState,pub local_bound:f64,pub public_width:f64,pub max_ledger:f64,pub audits:Vec<String>,pub source_hh_events:[f64;3],pub source_hh_heat:[f64;3]}
pub fn hh_paired_initial(c:&HhRunConfig)->Result<HhPairedState,ForwardError>{
 Ok(HhPairedState{base:paired_initial(&c.grid)?,hh_events:0.0,hh_heat:0.0,hh_comp:[0.0;2],identity:c.identity.clone()})
}
fn hh_check(c:&HhRunConfig,s:&HhPairedState)->Result<(),ForwardError>{
 if c.identity!=s.identity{return Err(fail("HH_PAIRED_IDENTITY"));}
 if !s.hh_events.is_finite() || s.hh_events<0.0 || !s.hh_heat.is_finite() || s.hh_heat>0.0 || s.hh_comp.iter().any(|x|!x.is_finite()) || !s.base.energy_comp.is_finite(){return Err(fail("HH_PAIRED_LEDGER"));}
 if c.mode==HhMode::Off && (s.hh_events!=0.0||s.hh_heat!=0.0||s.hh_comp!=[0.0;2]) {return Err(fail("HH_PAIRED_OFF_LEDGER"));}
 let nodes=energy_nodes(&c.grid)?;validate(&c.grid,&s.base,&nodes)?;
 for b in s.base.gas_box.iter().chain(&s.base.photon_boxes).chain(&s.base.lower_guard_n_box).chain(&s.base.lower_guard_u_box){b.valid().map_err(ie)?;}
 Ok(())
}
fn hh_endpoint_state(c:&HhRunConfig,s:&HhPairedState,dt:f64,nodes:&[f64])->Result<(HhPairedState,String,f64,[f64;2]),ForwardError>{
 let (base,audit,ledger,events)=hh_source_endpoint(&c.grid,c.hubble,&s.base,dt,nodes)?;
 let j=accumulate(s.hh_events,s.hh_comp[0],events[0]);
 let q=accumulate(s.hh_heat,s.hh_comp[1],events[1]);
 let out=HhPairedState{base,hh_events:j.0,hh_heat:q.0,hh_comp:[j.1,q.1],identity:s.identity.clone()};
 hh_check(c,&out)?;
 Ok((out,audit,ledger,events))
}
pub fn hh_paired_trial(c:&HhRunConfig,s:&HhPairedState,dt:f64)->Result<HhPairedTrial,ForwardError>{
 hh_check(c,s)?;
 if c.mode==HhMode::Off {
  let t=paired_trial(&c.grid,c.hubble,&s.base,dt)?;
  return Ok(HhPairedTrial{state:HhPairedState{base:t.state,..s.clone()},local_bound:t.local_bound,public_width:t.public_width,max_ledger:t.max_ledger,audits:t.audits,source_hh_events:[0.0;3],source_hh_heat:[0.0;3]});
 }
 let nodes=energy_nodes(&c.grid)?;
 if !dt.is_finite() || dt<1000.0 || s.base.time_s+dt>1e13 {return Err(fail("PAIRED_TRIAL_DOMAIN"));}
 let (full,a1,l1,e1)=hh_endpoint_state(c,s,dt,&nodes)?;
 let (half,a2,l2,e2)=hh_endpoint_state(c,s,dt/2.0,&nodes)?;
 let (two,a3,l3,e3)=hh_endpoint_state(c,&half,dt/2.0,&nodes)?;
 let local=difference(&full.base,&two.base,&nodes)?;
 let public=width(&two.base,&nodes)?;
 let ledger=l1.max(l2).max(l3);
 if local>=2e-4{return Err(fail("PAIRED_LOCAL_GATE"));}
 if public>=2e-3{return Err(fail("PAIRED_WIDTH_GATE"));}
 if ledger>1e-12{return Err(fail("PAIRED_LEDGER_GATE"));}
 Ok(HhPairedTrial{state:two,local_bound:local,public_width:public,max_ledger:ledger,audits:vec![a1,a2,a3],source_hh_events:[e1[0],e2[0],e3[0]],source_hh_heat:[e1[1],e2[1],e3[1]]})
}
pub fn try_hh_paired_step(c:&HhRunConfig,s:&mut HhPairedState,dt:f64)->Result<HhPairedTrial,ForwardError>{
 let t=hh_paired_trial(c,s,dt)?; *s=t.state.clone(); Ok(t)
}
/// Commit all geometries/modes only after every immutable trial has passed.
pub fn try_hh_paired_ensemble(configs:&[HhRunConfig],states:&mut[HhPairedState],dt:f64)->Result<Vec<HhPairedTrial>,ForwardError>{
 if configs.len()!=states.len() || configs.is_empty() || configs.len()>4{return Err(fail("HH_PAIRED_ENSEMBLE_LENGTH"));}
 let mut trials=Vec::with_capacity(states.len());
 for (c,s) in configs.iter().zip(states.iter()){trials.push(hh_paired_trial(c,s,dt)?);}
 for (s,t) in states.iter_mut().zip(&trials){*s=t.state.clone();}
 Ok(trials)
}

fn hh_source_endpoint(c:&PairedConfig,h:[f64;3],s:&PairedState,dt:f64,nodes:&[f64])->Result<(PairedState,String,f64,[f64;2]),ForwardError>{
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
    let old=PrimaryState{fractions:s.gas.fractions,w_ev_per_h:s.gas.w_ev_per_h,escape_ev_per_h:s.gas.escape_ev_per_h,packets};
    let stage=PrimaryStage{n_h_cm3:1e-4*(-h.iter().sum::<f64>()*t1).exp(),f_he:FHE,h_mean_per_s:h.iter().sum::<f64>()/3.0};
    let parent=PrimaryBox{gas:s.gas_box,photons:index.iter().map(|&k|gb[k]).collect()};
    let control=StepControl{max_iterations:200,residual_tolerance:1e-15};
    let (hh_step,energy_comp)=hh_stage_step_conservative(&stage,&old,dt,control,s.energy_comp,HhMode::Lcs91)?;
    let certificate=hh_stage_root(&stage,&old,&parent,dt,control,HhMode::Lcs91)?;
    let carry=hh_return_enclosure(&stage,&old,&parent,dt,control,&hh_step,&certificate)?;
    let point=hh_step.base.clone();
    // Root certificate retains its original box. The carry envelope also contains
    // the numerical returned point and is used for transport and the next input.
    let mut root=certificate.root.clone();
    root.gas=carry.gas;
    root.photons=carry.photons.clone();
    guard_temperature(root.gas)?;
    let provider=AtomicProvider::reference();let mut out=vec![0.0;nd*n];let mut outb=vec![p(0.0)?;nd*n];
    for (slot,&k) in index.iter().enumerate(){
        let sig=[provider.cross_section(Absorber::HI,nodes[k])?,provider.cross_section(Absorber::HeI,nodes[k])?,provider.cross_section(Absorber::HeII,nodes[k])?];
        let lower=[sub(p(1.0)?,root.gas[0])?,mul(p(FHE)?,sub(sub(p(1.0)?,root.gas[1])?,root.gas[2])?)?,mul(p(FHE)?,root.gas[1])?];
        let mut opacity=p(0.0)?;for a in 0..3 {opacity=add(opacity,mul(lower[a],p(sig[a])?)?)?;}
        let factor=div(p(1.0)?,add(p(1.0)?,mul(p(dt*29979245800.0*stage.n_h_cm3)?,opacity)?)?)?;
        let actual=if groups[k]==0.0 {1.0} else {point.state.packets[slot].per_h/groups[k]};
        for d in 0..nd {let i=d*n+k;out[i]=transported[i]*actual;outb[i]=nonneg(widened(mul(tb[i],factor)?,out[i])?)?;}
    }
    let mut gas=point.state.clone();gas.packets=index.iter().enumerate().map(|(j,&k)|PrimaryPacket{energy_ev:nodes[k],per_h:point.state.packets[j].per_h}).collect();
    let absorbed=weighted_sum(&point.events.photo_per_h.iter().flat_map(|a|a.iter()).copied().collect::<Vec<_>>());
    let thermal=point.events.thermal_work_ev_per_h;
    let increments=[redshift_loss,thermal,source_n,source_u,absorbed];
    let previous=[s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h];
    let updated:[(f64,f64);5]=std::array::from_fn(|i|accumulate(previous[i],s.ledger_comp[i],increments[i]));
    let next=PairedState{time_s:t1,gas,gas_box:root.gas,photons:out,photon_boxes:outb,
        lower_guard_n:guard_n,lower_guard_u:guard_u,lower_guard_n_box:guard_nb,lower_guard_u_box:guard_ub,
        redshift_work_ev_per_h:updated[0].0,thermal_work_ev_per_h:updated[1].0,
        source_photons_per_h:updated[2].0,source_energy_ev_per_h:updated[3].0,
        absorbed_photons_per_h:updated[4].0,ledger_comp:updated.map(|v|v.1),energy_comp};
    let nn=photon_number(&next);let uu=photon_energy(&next,nodes);
    let number_res=(transport_n+source_n-nn-absorbed).abs()/(old_n+source_n).max(0.05);
    let stage_input= matter_energy(&old)+transport_u+source_u;
    let stage_output=matter_energy(&next.gas)+uu+thermal;
    let energy_res=(stage_output-stage_input).abs()/(matter_energy(&old)+old_u+source_u).max(0.05*BIRTH);
    let transport_res=(transport_n-old_n).abs()/(old_n+source_n).max(0.05);
    // Prefix cumulative diagnostics do not gate individual steps.
    let max_ledger=number_res.max(energy_res).max(transport_res);
    if max_ledger>1e-12{return Err(fail("PAIRED_LEDGER_GATE"));}
    let centre_boxes=certificate.root.centre.map(|x|Interval::point(x).expect("finite certified centre"));
    let (centre_jets,_)=crate::coupled_primary::hh_interval_source(&stage,&old,&centre_boxes,&parent.photons,dt,HhMode::Lcs91)?;
    let (box_jets,_)=crate::coupled_primary::hh_interval_source(&stage,&old,&certificate.root.gas,&parent.photons,dt,HhMode::Lcs91)?;
    let mut audit=site_audit(&stage,t1,dt,nodes,&index,&old,&parent,&certificate.root,&point,transport_n,transport_u,source_n,source_u)?;
    audit.pop();
    let array=|xs:&[f64]|format!("[{}]",xs.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(","));
    let boxes=|xs:&[Interval]|format!("[{}]",xs.iter().map(|x|array(&[x.lo,x.hi])).collect::<Vec<_>>().join(","));
    write!(audit,",\"hh_mode\":\"LCS\",\"hh_events\":{:.17e},\"hh_heat\":{:.17e},\"root_image\":{},\"root_scales\":{},\"carry_gas\":{},\"carry_photons\":{},\"old_escape\":{:.17e},\"incoming_energy_comp\":{:.17e},\"outgoing_energy_comp\":{:.17e}}}",hh_step.hh_events_per_h,hh_step.hh_heat_ev_per_h,boxes(&certificate.image),array(&certificate.scales),boxes(&carry.gas),boxes(&carry.photons),old.escape_ev_per_h,s.energy_comp,energy_comp).map_err(|_|fail("PAIRED_AUDIT_WRITE"))?;
    audit.pop();
    let f0:Vec<Interval>=centre_jets.iter().map(|j|j.value).collect();
    let jac=box_jets.iter().map(|j|boxes(&j.gradient[..4])).collect::<Vec<_>>().join(",");
    write!(audit,",\"centre_rhs\":{},\"box_jacobian\":[{}]}}",boxes(&f0),jac).map_err(|_|fail("PAIRED_AUDIT_WRITE"))?;
    audit.pop();
    write!(audit,",\"old_point_photons\":{},\"n_he_cm3\":{:.17e}}}",array(&old.packets.iter().map(|p|p.per_h).collect::<Vec<_>>()),stage.n_h_cm3*stage.f_he).map_err(|_|fail("PAIRED_AUDIT_WRITE"))?;
    Ok((next,audit,max_ledger,[hh_step.hh_events_per_h,hh_step.hh_heat_ev_per_h]))
}
// Binary v1 checkpoint for trusted local persistence. The source tag and FNV
// checksum detect accidental mismatch/corruption; neither authenticates an
// untrusted state nor proves that arbitrary restored intervals are valid proofs.
fn hh_fnv(bytes:&[u8],mut state:u64)->u64{for b in bytes{state^=*b as u64;state=state.wrapping_mul(0x100000001b3);}state}
fn hh_source_tag()->u64{
 let sources:&[&[u8]]=&[include_bytes!("paired_runtime.rs"),include_bytes!("hh_paired_extension.rs"),include_bytes!("coupled_primary.rs"),include_bytes!("hh_primary_extension.rs"),include_bytes!("hh_return_enclosure.rs"),include_bytes!("ft03_rates.rs"),include_bytes!("ft03_controlled.rs"),include_bytes!("ft03_interval.rs"),include_bytes!("interval_math.rs"),include_bytes!("interval_ad.rs"),include_bytes!("atomic_provider.rs"),include_bytes!("bianchi_i.rs"),include_bytes!("hhe_events.rs"),include_bytes!("group_rates.rs"),include_bytes!("homogeneous_rates.rs"),include_bytes!("microstep.rs"),include_bytes!("thermal.rs")];
 let mut tag=hh_fnv(HH_PAIRED_MODEL_ID.as_bytes(),0xcbf29ce484222325);
 for data in sources {tag=hh_fnv(&(data.len() as u64).to_le_bytes(),tag);tag=hh_fnv(data,tag);} tag
}
const HH_CHECKPOINT_MAGIC:u64=u64::from_le_bytes(*b"HH06Bv01");
fn hh_write_word(out:&mut Vec<u8>,x:u64){out.extend_from_slice(&x.to_le_bytes());}
fn hh_write_floats(out:&mut Vec<u8>,xs:&[f64]){for x in xs{hh_write_word(out,x.to_bits());}}
fn hh_write_boxes(out:&mut Vec<u8>,xs:&[Interval]){for x in xs{hh_write_floats(out,&[x.lo,x.hi]);}}
pub fn hh_checkpoint_encode(c:&HhRunConfig,s:&HhPairedState)->Result<Vec<u8>,ForwardError>{
 hh_check(c,s)?;
 let mut out=Vec::new();hh_write_word(&mut out,HH_CHECKPOINT_MAGIC);hh_write_word(&mut out,hh_source_tag());
 hh_write_word(&mut out,c.identity.schema as u64);hh_write_word(&mut out,c.identity.words.len() as u64);
 for w in &c.identity.words{hh_write_word(&mut out,*w);}
 let b=&s.base;hh_write_floats(&mut out,&[b.time_s]);
 hh_write_floats(&mut out,&b.gas.fractions);hh_write_floats(&mut out,&[b.gas.w_ev_per_h,b.gas.escape_ev_per_h]);
 hh_write_word(&mut out,b.gas.packets.len() as u64);
 for p in &b.gas.packets{hh_write_floats(&mut out,&[p.energy_ev,p.per_h]);}
 hh_write_boxes(&mut out,&b.gas_box);hh_write_floats(&mut out,&b.photons);hh_write_boxes(&mut out,&b.photon_boxes);
 hh_write_floats(&mut out,&b.lower_guard_n);hh_write_floats(&mut out,&b.lower_guard_u);
 hh_write_boxes(&mut out,&b.lower_guard_n_box);hh_write_boxes(&mut out,&b.lower_guard_u_box);
 hh_write_floats(&mut out,&[b.redshift_work_ev_per_h,b.thermal_work_ev_per_h,b.source_photons_per_h,b.source_energy_ev_per_h,b.absorbed_photons_per_h]);
 hh_write_floats(&mut out,&b.ledger_comp);hh_write_floats(&mut out,&[b.energy_comp,s.hh_events,s.hh_heat,s.hh_comp[0],s.hh_comp[1]]);
 let sum=hh_fnv(&out,0xcbf29ce484222325);hh_write_word(&mut out,sum);Ok(out)
}
struct HhReader<'a>{data:&'a[u8],at:usize}
impl<'a> HhReader<'a>{
 fn word(&mut self)->Result<u64,ForwardError>{
  let end=self.at.checked_add(8).ok_or(fail("HH_CHECKPOINT_TRUNCATED"))?;
  let bytes=self.data.get(self.at..end).ok_or(fail("HH_CHECKPOINT_TRUNCATED"))?;
  self.at=end;Ok(u64::from_le_bytes(bytes.try_into().map_err(|_|fail("HH_CHECKPOINT_TRUNCATED"))?))
 }
 fn floats(&mut self,n:usize)->Result<Vec<f64>,ForwardError>{
  if n>self.data.len().saturating_sub(self.at)/8{return Err(fail("HH_CHECKPOINT_TRUNCATED"));}
  let mut v=Vec::with_capacity(n);for _ in 0..n{v.push(f64::from_bits(self.word()?));}Ok(v)
 }
 fn boxes(&mut self,n:usize)->Result<Vec<Interval>,ForwardError>{
  if n>self.data.len().saturating_sub(self.at)/16{return Err(fail("HH_CHECKPOINT_TRUNCATED"));}
  let mut v=Vec::with_capacity(n);for _ in 0..n{let x=self.floats(2)?;v.push(Interval::new(x[0],x[1]).map_err(ie)?);}Ok(v)
 }
}
pub fn hh_checkpoint_decode(c:&HhRunConfig,data:&[u8])->Result<HhPairedState,ForwardError>{
 if data.len()<40||data.len()%8!=0||data.len()>64*1024*1024{return Err(fail("HH_CHECKPOINT_SIZE"));}
 let end=data.len()-8;let mut rd=HhReader{data:&data[..end],at:0};
 let checksum=u64::from_le_bytes(data[end..].try_into().map_err(|_|fail("HH_CHECKPOINT_SIZE"))?);
 if hh_fnv(&data[..end],0xcbf29ce484222325)!=checksum{return Err(fail("HH_CHECKPOINT_CHECKSUM"));}
 if rd.word()?!=HH_CHECKPOINT_MAGIC||rd.word()?!=hh_source_tag(){return Err(fail("HH_CHECKPOINT_MODEL"));}
 if rd.word()?!=c.identity.schema as u64||rd.word()?!=c.identity.words.len() as u64{return Err(fail("HH_CHECKPOINT_IDENTITY"));}
 for want in &c.identity.words{if rd.word()?!=*want{return Err(fail("HH_CHECKPOINT_IDENTITY"));}}
 let nodes=energy_nodes(&c.grid)?;let nd=directions(&c.grid)?;let np=nd.checked_mul(nodes.len()).ok_or(fail("HH_CHECKPOINT_SIZE"))?;
 let time_s=rd.floats(1)?[0];let f=rd.floats(3)?;let w=rd.floats(2)?;let count=rd.word()?;
 if count>nodes.len() as u64{return Err(fail("HH_CHECKPOINT_PACKET_COUNT"));}
 let mut packets=Vec::with_capacity(count as usize);
 for _ in 0..count{let p=rd.floats(2)?;if !p[1].is_finite()||p[1]<0.0||!nodes.iter().any(|e|e.to_bits()==p[0].to_bits()){return Err(fail("HH_CHECKPOINT_PACKET"));}packets.push(PrimaryPacket{energy_ev:p[0],per_h:p[1]});}
 let g=rd.boxes(4)?;let photons=rd.floats(np)?;let photon_boxes=rd.boxes(np)?;
 let lower_guard_n=rd.floats(nd)?;let lower_guard_u=rd.floats(nd)?;let lower_guard_n_box=rd.boxes(nd)?;let lower_guard_u_box=rd.boxes(nd)?;
 let ledger=rd.floats(5)?;let comp=rd.floats(5)?;let extra=rd.floats(5)?;
 if rd.at!=end{return Err(fail("HH_CHECKPOINT_TRAILING_DATA"));}
 let base=PairedState{time_s,gas:PrimaryState{fractions:[f[0],f[1],f[2]],w_ev_per_h:w[0],escape_ev_per_h:w[1],packets},gas_box:[g[0],g[1],g[2],g[3]],photons,photon_boxes,lower_guard_n,lower_guard_u,lower_guard_n_box,lower_guard_u_box,redshift_work_ev_per_h:ledger[0],thermal_work_ev_per_h:ledger[1],source_photons_per_h:ledger[2],source_energy_ev_per_h:ledger[3],absorbed_photons_per_h:ledger[4],ledger_comp:[comp[0],comp[1],comp[2],comp[3],comp[4]],energy_comp:extra[0]};
 let state=HhPairedState{base,hh_events:extra[1],hh_heat:extra[2],hh_comp:[extra[3],extra[4]],identity:c.identity.clone()};
 if !state.base.gas.escape_ev_per_h.is_finite()||state.base.gas.escape_ev_per_h<0.0{return Err(fail("HH_CHECKPOINT_GAS"));}
 if state.base.gas.fractions[0]<0.0||state.base.gas.fractions[0]>1.0||state.base.gas.fractions[1]<0.0||state.base.gas.fractions[2]<0.0||state.base.gas.fractions[1]+state.base.gas.fractions[2]>1.0{return Err(fail("HH_CHECKPOINT_GAS"));}
 hh_check(c,&state)?;Ok(state)
}
