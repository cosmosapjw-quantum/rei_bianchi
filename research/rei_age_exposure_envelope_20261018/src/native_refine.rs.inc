// Task-only CLI adapter. Original setup/physics/RHS/old native modes remain above.
fn native_refine(
    q: f64,
    out: &Path,
    birth_count: usize,
    nmu: usize,
    source: usize,
    transport_cells: usize,
    refinement_levels: &[usize],
    time_factor: usize,
) -> Result<(), Box<dyn std::error::Error>> {
    if birth_count == 0 || nmu == 0 || source == 0 || transport_cells == 0
        || time_factor == 0 || refinement_levels.is_empty()
        || !refinement_levels.contains(&birth_count) || !refinement_levels.contains(&8)
        || refinement_levels.iter().any(|n| *n == 0 || *n > 1024)
        || refinement_levels.windows(2).any(|w| w[0] >= w[1])
    {
        return Err("REFINEMENT_CONFIG_DOMAIN".into());
    }
    let maximum_segments = refinement_levels.iter().sum::<usize>() + 1;
    if maximum_segments.checked_mul(time_factor).map_or(true, |n| n > 1_000_000) {
        return Err("REFINEMENT_MESH_BUDGET".into());
    }
    if out.join("endpoint.json").exists() {
        return Err("REFINEMENT_OUTPUT_EXISTS".into());
    }
    let s = setup(q, birth_count, nmu, source, transport_cells)?;
    let to = (s.s0.gas_owner.a.ln() + 0.002).exp();
    let mesh = common_mesh(s.s0.gas_owner.a, to, refinement_levels, time_factor);
    fs::create_dir_all(out)?;
    fs::write(out.join("common_mesh_ln_a.json"), format!("{:?}", mesh))?;
    fs::write(out.join("refinement_config.json"), format!(
        "{{\"q\":{q},\"birth_panels\":{birth_count},\"n_mu\":{nmu},\"source_subdivisions\":{source},\"transport_cells\":{transport_cells},\"common_birth_levels\":{:?},\"time_factor\":{time_factor},\"native_steps\":{}}}",
        refinement_levels, mesh.len()))?;
    let mut calls = 0;
    let (state, trace) = trial_on_mesh_trace(&s.d, &s.s0, to, birth_count, &mesh, &mut calls)?;
    let observe = common_mesh(s.s0.gas_owner.a, to, &[8], 1);
    let mut observations = Vec::new();
    for (x, post, st) in &trace {
        if !observe.iter().any(|v| v.to_bits() == x.to_bits()) { continue; }
        let physical = native_physical(&s.d, st)?;
        let make = |side: &str| format!(
            "{{\"x\":{x},\"side\":\"{side}\",\"active\":{},\"physical\":{physical}}}", st.cohorts.len());
        observations.push(make(if *post {"post"} else {"pre"}));
        // Explicitly equal pre/post only where the source schedule has NO jump.
        let has_birth = trace.iter().any(|(bx, is_post, _)| *is_post && bx.to_bits() == x.to_bits());
        if !*post && !has_birth { observations.push(make("post")); }
    }
    fs::write(out.join("observations.json"),format!("[{}]",observations.join(",")))?;
    fs::write(out.join("endpoint.json"), native_physical(&s.d, &state)?)?;
    fs::write(out.join("native_return.json"), format!(
        "{{\"status\":\"SCOPED_NUMERICAL_EXECUTION_COMPLETE\",\"rhs_evaluations\":{calls},\"native_steps\":{},\"active_cohorts\":{},\"production_admission\":\"NOT_ISSUED\"}}\n",
        mesh.len(), state.cohorts.len()))?;
    Ok(())
}
