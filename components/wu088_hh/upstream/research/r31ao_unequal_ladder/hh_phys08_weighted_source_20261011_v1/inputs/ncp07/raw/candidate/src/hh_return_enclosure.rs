/// Enclose both the exact discrete root family and the numerical returned point.
/// This widens an uncertainty set, never projects a state or resets old error.
/// It is not a continuous-time error certificate or an untrusted-proof validator.
pub(crate) fn hh_amplitude_return_enclosure(
    g:&PrimaryStage,old:&PrimaryState,parent:&PrimaryBox,dt:f64,c:StepControl,
    step:&HhStep,root:&HhRoot,lambda:f64,
)->Result<PrimaryBox,ForwardError>{
    if !(if step.mode==HhMode::Off{hh_root_matches(root,g,old,parent,dt,c,step.mode)}else{hh_amplitude_root_matches(root,g,old,parent,dt,c,lambda)})
        || root.root.q>=1.0 || !root.root.q.is_finite()
        || step.base.state.packets.len()!=old.packets.len()
        || step.base.state.packets.len()!=root.root.photons.len()
        || !step.base.residual.is_finite() || step.base.residual>c.residual_tolerance {
        return Err(fail("HH_ON06_RETURN_IDENTITY"));
    }
    let m=model(g)?;valid(&m,&step.base.state)?;
    let sigma=signatures(old)?;
    if step.base.state.packets.iter().zip(&old.packets)
        .any(|(a,b)|a.energy_ev.to_bits()!=b.energy_ev.to_bits()) {
        return Err(fail("HH_ON06_RETURN_IDENTITY"));
    }
    // A stale low residual field cannot authorize a changed state.
    let (residual,event)=match step.mode{
        HhMode::Off=>(endpoint(g,&m,old,&step.base.state,&sigma,dt)?.0,0.0),
        HhMode::Lcs91=>{let(r,_,j)=hh_endpoint_amplitude(g,&m,old,&step.base.state,&sigma,dt,lambda)?;(r,j)},
    };
    let heat=if step.mode==HhMode::Off {0.0}else{-CHI[0]*event};
    if step.hh_events_per_h.to_bits()!=event.to_bits() || step.hh_heat_ev_per_h.to_bits()!=heat.to_bits() {
        return Err(fail("HH_ON06_RETURN_EVENT"));
    }
    if residual>c.residual_tolerance{return Err(fail("HH_ON06_RETURN_RESIDUAL"));}
    let values=[step.base.state.fractions[0],step.base.state.fractions[1],step.base.state.fractions[2],step.base.state.w_ev_per_h];
    let gas=std::array::from_fn(|i|Interval{lo:root.root.gas[i].lo.min(values[i]),hi:root.root.gas[i].hi.max(values[i])});
    let photons:Vec<Interval>=root.root.photons.iter().zip(&step.base.state.packets)
        .map(|(b,p)|Interval::new(b.lo.min(p.per_h),b.hi.max(p.per_h)).map_err(ie)).collect::<Result<_,_>>()?;
    // Fail closed if the wider return envelope leaves the admitted domain.
    hh_interval_rhs_amplitude(g,&m,&step.base.state,&gas,&photons,&sigma,0.0,step.mode,lambda)?;
    Ok(PrimaryBox{gas,photons})
}

pub fn hh_return_enclosure(g:&PrimaryStage,old:&PrimaryState,parent:&PrimaryBox,dt:f64,c:StepControl,step:&HhStep,root:&HhRoot)->Result<PrimaryBox,ForwardError>{hh_amplitude_return_enclosure(g,old,parent,dt,c,step,root,if step.mode==HhMode::Off{0.0}else{1.0})}
