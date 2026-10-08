//! Explicit strict manufactured-history configuration. No hidden physical defaults.
use crate::{
    igm_background::{FlatFlrwBackground, FlatFlrwConfig},
    igm_source::ConstantSource,
    ForwardError,
};
#[derive(Clone, Debug)]
pub struct HistoryConfig {
    pub model_id: String,
    pub provider_id: String,
    pub closure_id: String,
    pub background: FlatFlrwBackground,
    pub start: f64,
    pub end: f64,
    pub fractions: [f64; 3],
    pub temperature_k: f64,
    pub source: ConstantSource,
    pub birth_panels: usize,
    pub energy_panels: usize,
    pub max_dln_a: f64,
    pub min_dln_a: f64,
    pub output_panels: usize,
    pub max_packets: usize,
    pub max_steps: usize,
}

fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_CONFIG_INVALID")
}
pub fn parse_config(text: &str) -> Result<HistoryConfig, ForwardError> {
    let mut map = std::collections::BTreeMap::new();
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let (k, v) = line.split_once('=').ok_or_else(invalid)?;
        if k.trim().is_empty() || v.trim().is_empty() || map.insert(k.trim(), v.trim()).is_some() {
            return Err(invalid());
        }
    }
    let take = |m: &mut std::collections::BTreeMap<&str, &str>, k: &str| {
        m.remove(k).map(str::to_string).ok_or_else(invalid)
    };
    if take(&mut map, "schema")? != "igm_history_config_v1"
        || take(&mut map, "criteria_id")? != "igm_history_frozen_20261006_v1"
    {
        return Err(invalid());
    }
    let model_id = take(&mut map, "model_id")?;
    let provider_id = take(&mut map, "provider_id")?;
    let closure_id = take(&mut map, "closure_id")?;
    if provider_id != "grackle341_caseA_lowT_subset_v1"
        || closure_id != "caseA_escape_C1_primary_only"
    {
        return Err(invalid());
    }
    let number =
        |m: &mut std::collections::BTreeMap<&str, &str>, k: &str| -> Result<f64, ForwardError> {
            let v = take(m, k)?.parse::<f64>().map_err(|_| invalid())?;
            if v.is_finite() {
                Ok(v)
            } else {
                Err(invalid())
            }
        };
    let integer =
        |m: &mut std::collections::BTreeMap<&str, &str>, k: &str| -> Result<usize, ForwardError> {
            let v = take(m, k)?.parse::<usize>().map_err(|_| invalid())?;
            if v > 0 {
                Ok(v)
            } else {
                Err(invalid())
            }
        };
    let h0 = number(&mut map, "h0")?;
    let omega_r = number(&mut map, "omega_r")?;
    let omega_m = number(&mut map, "omega_m")?;
    let omega_b = number(&mut map, "omega_b")?;
    let omega_lambda = number(&mut map, "omega_lambda")?;
    let y = number(&mut map, "y_he")?;
    let tcmb0 = number(&mut map, "tcmb0")?;
    let z0 = number(&mut map, "z_start")?;
    let z1 = number(&mut map, "z_end")?;
    if z0 <= z1 || z1 <= -1.0 {
        return Err(invalid());
    }
    let start = -z0.ln_1p();
    let end = -z1.ln_1p();
    let background = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_r,
        omega_m,
        omega_b,
        omega_lambda,
        helium_mass_fraction: y,
        tcmb0_k: tcmb0,
        ln_a_min: start,
        ln_a_max: end,
        parameter_source: model_id.clone(),
    })?;
    let fractions = [
        number(&mut map, "x_hii")?,
        number(&mut map, "x_heii")?,
        number(&mut map, "x_heiii")?,
    ];
    let temperature_k = number(&mut map, "temperature_k")?;
    let source = ConstantSource {
        photons_per_h_per_s: number(&mut map, "source_rate")?,
        energy_min_ev: number(&mut map, "energy_min_ev")?,
        energy_max_ev: number(&mut map, "energy_max_ev")?,
    };
    let birth_panels = integer(&mut map, "birth_panels")?;
    let energy_panels = integer(&mut map, "energy_panels")?;
    let max_dln_a = number(&mut map, "max_dln_a")?;
    let min_dln_a = number(&mut map, "min_dln_a")?;
    let output_panels = integer(&mut map, "output_panels")?;
    let max_packets = integer(&mut map, "max_packets")?;
    let max_steps = integer(&mut map, "max_steps")?;
    if !map.is_empty()
        || !min_dln_a.is_normal()
        || min_dln_a <= 0.0
        || max_dln_a < min_dln_a
        || max_dln_a > end - start
    {
        return Err(invalid());
    }
    if energy_panels > max_packets / 2 || birth_panels > max_packets / 2 {
        return Err(invalid());
    }
    let nodes = source.energy_quadrature(energy_panels)?;
    if birth_panels
        .checked_mul(2)
        .and_then(|v| v.checked_mul(nodes.len()))
        .ok_or_else(invalid)?
        > max_packets
    {
        return Err(invalid());
    }
    let p = background.at_ln_a(start)?;
    let g = crate::igm_state::IgmGasState::from_temperature(
        fractions,
        p.n_h_cm3,
        p.n_he_cm3,
        temperature_k,
    )?;
    crate::igm_thermal::igm_point_rhs(
        &g,
        p.n_h_cm3,
        p.n_he_cm3,
        p.hubble_per_s,
        p.tcmb_k,
        Default::default(),
    )?;
    Ok(HistoryConfig {
        model_id,
        provider_id,
        closure_id,
        background,
        start,
        end,
        fractions,
        temperature_k,
        source,
        birth_panels,
        energy_panels,
        max_dln_a,
        min_dln_a,
        output_panels,
        max_packets,
        max_steps,
    })
}
