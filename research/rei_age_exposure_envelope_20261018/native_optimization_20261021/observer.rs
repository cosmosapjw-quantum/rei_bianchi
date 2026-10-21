fn rei_observe_accepted(context:&Context<'_>,next:&Accepted,dt:f64)->Result<(),ForwardError> {
    let Ok(path)=std::env::var("REI_BE_TRACE") else {return Ok(());};
    use std::io::Write;
    let gas=&next.gas_owner.gas;let a=context.old.gas_owner.a;
    let nh=context.d.n_h0_cm3/a.powi(3);let nhe=context.d.n_he0_cm3/a.powi(3);
    let [x,y,z]=gas.fractions;let abs=[nh*(1.-x),nhe*(1.-y-z),nhe*y];
    let mut output=String::new();
    for (i,p) in context.prepared.iter().enumerate() {
        let e=p.rei_exposure(abs,dt)?;
        let (q,nodes,low,high)=(e.q,e.nodes,e.low,e.high);
        let before=context.old.cohorts[i].surviving.number.iter().sum::<f64>();
        let after=next.cohorts[i].surviving.number.iter().sum::<f64>();
        output.push_str(&format!("{{\"cohort\":{i},\"d_min\":{:.17e},\"d_max\":{:.17e},\"Q_lo\":{:.17e},\"Q_hi\":{:.17e},\"S_lo\":{:.17e},\"S_hi\":{:.17e},\"sum_method\":\"Q_COMPENSATED;BEFORE_AFTER_PLAIN_ROUNDED\",\"kernel\":\"STORED_DENOMINATOR_DISCRETE_BE\",",e.d_min,e.d_max,e.q_lo,e.q_hi,e.s_lo,e.s_hi));
        output.push_str(&format!("\"birth_bits\":\"{:016x}\",\"a_bits\":\"{:016x}\",\"dt\":{dt:.17e},\"before_N\":{before:.17e},\"Q\":{q:.17e},\"after_N\":{after:.17e},\"nodes\":{nodes},\"lambda_min\":{low:.17e},\"lambda_max\":{high:.17e},\"reconstruction_delta\":{:.17e},\"bits\":[\"{:016x}\",\"{:016x}\",\"{:016x}\",\"{:016x}\",\"{:016x}\",\"{:016x}\"]}}\n",context.old.cohorts[i].birth.x.to_bits(),a.to_bits(),q-before,dt.to_bits(),before.to_bits(),q.to_bits(),after.to_bits(),low.to_bits(),high.to_bits()));
    }
    // Diagnostic failures are explicit execution failures, never changed physics decisions.
    let mut file=std::fs::OpenOptions::new().create(true).append(true).open(path).map_err(|_|err("REI_OBSERVER_IO"))?;
    file.write_all(output.as_bytes()).map_err(|_|err("REI_OBSERVER_IO"))?;Ok(())
}
