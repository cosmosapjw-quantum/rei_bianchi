//! Native Rust consumer of the ORIGINAL 46,080-node F05 tick161 candidate
//! produced by the unchanged source-owner 26-event H/He/thermal map.
//!
//! Consumes the original gzip-expanded 27-column physical CSV on stdin.
//! This does NOT reconstruct the original interval solver or admit tick161.
//! Uses the historical REI HHeModel k_B and explicit population/electron EOS.
//! The accepted parent tick160 and historical V1 failure remain protected.
use rei_microphysics::{igm_state::IgmGasState, HHeModel};
use std::io::{self, BufRead, BufReader};

const ROWS: usize = 46_080;
const COLUMNS: usize = 27;
const K_B_CGS: f64 = 1.380649e-16;

const HEADER: &str = "node,source_H_nuclei_N_lower,source_H_nuclei_N_upper,source_He_nuclei_N_lower,source_He_nuclei_N_upper,tick160_xHII_lower,tick160_xHII_upper,tick161_preview_xHII_lower,tick161_preview_xHII_upper,tick161_preview_xHeII_lower,tick161_preview_xHeII_upper,tick161_preview_xHeIII_lower,tick161_preview_xHeIII_upper,tick160_Tgas_K_lower,tick160_Tgas_K_upper,tick161_preview_Tgas_K_lower,tick161_preview_Tgas_K_upper,tick160_electron_count_N_lower,tick160_electron_count_N_upper,tick161_preview_electron_count_N_lower,tick161_preview_electron_count_N_upper,tick161_preview_U_erg_lower,tick161_preview_U_erg_upper,tick160_to_161_delta_logT_lower,tick160_to_161_delta_logT_upper,tick160_to_161_delta_electron_N_lower,tick160_to_161_delta_electron_N_upper";

#[derive(Default)]
struct Sum {
    sum: f64,
    compensation: f64,
}
impl Sum {
    fn add(&mut self, x: f64) {
        let t = self.sum + x;
        self.compensation += if self.sum.abs() >= x.abs() {
            (self.sum - t) + x
        } else {
            (x - t) + self.sum
        };
        self.sum = t;
    }
    fn total(&self) -> f64 {
        self.sum + self.compensation
    }
}
#[derive(Default)]
struct Results {
    n: usize,
    h: Sum,
    he: Sum,
    ne_low: Sum,
    ne_high: Sum,
    u_low: Sum,
    u_high: Sum,
    dne_low: Sum,
    dne_high: Sum,
    reconstructed_ne: Sum,
    reconstructed_u: Sum,
    max_ne_relative_discrepancy: f64,
    max_u_relative_discrepancy: f64,
    ne_interval_strict_misses: usize,
    u_interval_strict_misses: usize,
    ne_relative_1e10_misses: usize,
    u_relative_1e10_misses: usize,
    min_temperature_k: f64,
    max_temperature_k: f64,
}
fn midpoint(lo: f64, hi: f64) -> f64 {
    lo * 0.5 + hi * 0.5
}

fn check_pair(lo: f64, hi: f64, label: &str) -> Result<(), String> {
    if !lo.is_finite() || !hi.is_finite() || lo > hi {
        return Err(format!("INVALID_ORIGINAL_INTERVAL_{label}"));
    }
    Ok(())
}
fn parse_line(text: &str, expected_index: usize, kb: f64, r: &mut Results) -> Result<(), String> {
    let cols: Vec<&str> = text.trim_end_matches('\r').split(',').collect();
    if cols.len() != COLUMNS {
        return Err(format!(
            "WRONG_ORIGINAL_COLUMN_COUNT:{}:{}",
            expected_index,
            cols.len()
        ));
    }
    let node = cols[0].parse::<usize>().map_err(|_| "BAD_NODE_ID")?;
    if node != expected_index {
        return Err(format!("NODE_ORDER_OR_DUPLICATE:{node}!={expected_index}"));
    }
    let mut a = [0.0_f64; COLUMNS];
    for i in 1..COLUMNS {
        a[i] = cols[i]
            .parse::<f64>()
            .map_err(|_| format!("NOT_FLOAT_NODE_{node}_COL_{i}"))?;
        if !a[i].is_finite() {
            return Err(format!("NONFINITE_ORIGINAL_PHYSICS_NODE_{node}_COL_{i}"));
        }
    }
    for (lo, hi, key) in [
        (1, 2, "NH"),
        (3, 4, "NHE"),
        (5, 6, "XH0"),
        (7, 8, "XH1"),
        (9, 10, "XHEII"),
        (11, 12, "XHEIII"),
        (13, 14, "T0"),
        (15, 16, "T1"),
        (17, 18, "NE0"),
        (19, 20, "NE1"),
        (21, 22, "U1"),
        (23, 24, "DELTA_LNT"),
        (25, 26, "DELTA_NE"),
    ] {
        check_pair(a[lo], a[hi], key)?;
    }
    if a[1] <= 0.0
        || a[3] <= 0.0
        || a[15] <= 0.0
        || a[7] < 0.0
        || a[8] > 1.0
        || a[9] < 0.0
        || a[11] < 0.0
        || a[10] + a[12] > 1.0 + 2e-12
    {
        return Err(format!("INVALID_NATIVE_HHE_POSITIVITY_NODE_{node}"));
    }
    let h = midpoint(a[1], a[2]);
    let he = midpoint(a[3], a[4]);
    let xh = midpoint(a[7], a[8]);
    let xheii = midpoint(a[9], a[10]);
    let xheiii = midpoint(a[11], a[12]);
    let temp = midpoint(a[15], a[16]);
    // Original source quantities N are particle counts per original spatial
    // cell, not proper cm^-3. No hidden cell-volume conversion.
    // Reuse the original, historically validated Rust EOS as a homogeneous
    // number-count operator. Normalizing n_H=1.0 is purely algebraic: it
    // NEVER declares the physical original cell density to be 1 cm^-3.
    // Only the density-homogeneous ideal EOS is used, NOT density-dependent
    // chemistry, opacity or cooling with this normalized convenience frame.
    let he_per_h = he / h;
    let gas = IgmGasState::from_temperature([xh, xheii, xheiii], 1.0, he_per_h, temp)
        .map_err(|e| format!("HISTORICAL_RUST_EOS_INPUT_NODE_{node}:{e}"))?;
    let eos = gas
        .eos(1.0, he_per_h)
        .map_err(|e| format!("HISTORICAL_RUST_EOS_CALC_NODE_{node}:{e}"))?;
    let ne = eos.electron_density_cm3 * h;
    let energy = eos.u_erg_cm3 * h;
    // A separate direct arithmetic expression is a numerical consistency
    // check, with only machine-roundoff budget. This is not an owner gate.
    let ne_direct = h * xh + he * (xheii + 2.0 * xheiii);
    let energy_direct = 1.5 * kb * temp * (h + he + ne_direct);
    if !ne.is_finite() || !energy.is_finite() || ne <= 0.0 || energy <= 0.0 {
        return Err(format!("NONFINITE_HHE_EOS_NODE_{node}"));
    }
    if (ne - ne_direct).abs() > 64.0 * f64::EPSILON * ne_direct
        || (energy - energy_direct).abs() > 64.0 * f64::EPSILON * energy_direct
    {
        return Err(format!(
            "HISTORICAL_RUST_EOS_DIVERGES_FROM_DEFINITION_NODE_{node}"
        ));
    }
    let ne_mid = midpoint(a[19], a[20]);
    let u_mid = midpoint(a[21], a[22]);
    let err_ne = (ne - ne_mid).abs() / ne_mid.abs().max(f64::MIN_POSITIVE);
    let err_u = (energy - u_mid).abs() / u_mid.abs().max(f64::MIN_POSITIVE);
    r.max_ne_relative_discrepancy = r.max_ne_relative_discrepancy.max(err_ne);
    r.max_u_relative_discrepancy = r.max_u_relative_discrepancy.max(err_u);
    if ne < a[19] || ne > a[20] {
        r.ne_interval_strict_misses += 1;
    }
    if energy < a[21] || energy > a[22] {
        r.u_interval_strict_misses += 1;
    }
    // Diagnostic comparison, NOT relaxation of original interval bounds.
    if err_ne > 1e-10 {
        r.ne_relative_1e10_misses += 1;
    }
    if err_u > 1e-10 {
        r.u_relative_1e10_misses += 1;
    }
    r.h.add(h);
    r.he.add(he);
    r.ne_low.add(a[19]);
    r.ne_high.add(a[20]);
    r.u_low.add(a[21]);
    r.u_high.add(a[22]);
    r.dne_low.add(a[25]);
    r.dne_high.add(a[26]);
    r.reconstructed_ne.add(ne);
    r.reconstructed_u.add(energy);
    r.min_temperature_k = r.min_temperature_k.min(a[15]);
    r.max_temperature_k = r.max_temperature_k.max(a[16]);
    r.n += 1;
    Ok(())
}
fn read_source<R: BufRead>(mut input: R, expected: usize) -> Result<Results, String> {
    let mut header = String::new();
    if input.read_line(&mut header).map_err(|_| "HEADER_IO")? == 0 {
        return Err("EMPTY_SOURCE".into());
    }
    if header.trim_end_matches(['\r', '\n']) != HEADER {
        return Err("WRONG_F05_SOURCE_SCHEMA_OR_VERSION".into());
    }
    let model = HHeModel::controlled_fixture();
    if model.kb_erg_k.to_bits() != K_B_CGS.to_bits() {
        return Err("HISTORICAL_RUST_KB_DRIFT".into());
    }
    let mut result = Results {
        min_temperature_k: f64::INFINITY,
        max_temperature_k: f64::NEG_INFINITY,
        ..Default::default()
    };
    for line in input.lines() {
        let s = line.map_err(|_| "BODY_IO")?;
        if s.trim().is_empty() {
            return Err("EMPTY_PHYSICAL_ROW".into());
        }
        if result.n == expected {
            return Err("EXTRA_F05_ROWS".into());
        }
        parse_line(&s, result.n, model.kb_erg_k, &mut result)?;
    }
    if result.n != expected {
        return Err(format!(
            "ORIGINAL_CELL_COUNT_MISMATCH:{}!={expected}",
            result.n
        ));
    }
    // The original source is an INTERVAL physical enclosure. Its arithmetic
    // midpoint is not the exact EOS evaluation at midpoint inputs. Require
    // strict native point inclusion in ALL original source-owner intervals,
    // rather than imposing an invented 1e-10 midpoint "physical gate".
    if result.ne_interval_strict_misses != 0 || result.u_interval_strict_misses != 0 {
        return Err(format!(
            "RUST_F05_EOS_OUTSIDE_ORIGINAL_INTERVAL:Ne={} U={}",
            result.ne_interval_strict_misses, result.u_interval_strict_misses
        ));
    }
    Ok(result)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let stdin = io::stdin();
    let result = read_source(BufReader::new(stdin.lock()), ROWS)?;
    println!("{{\"schema\":\"REI_F05_ORIGINAL_46080_RUST_EOS_CONSUMER_V1\",        \"original_source\":\"original26_native_preview_non_authoritative_tick161\",        \"original_parent_tick\":\"160/131072\",        \"owner_26event_full_map_port\":\"NOT_IMPLEMENTED\",        \"historical_rust_engine_reused\":\"rei_microphysics::igm_state::IgmGasState::from_temperature/eos + HHeModel::kb_erg_k\",        \"native_rust_rows\":{},        \"h_source_total\":{:.17e},\"he_source_total\":{:.17e},        \"electron_lower_total\":{:.17e},\"electron_upper_total\":{:.17e},        \"electron_rust_eos_total\":{:.17e},        \"gas_u_lower_erg\":{:.17e},\"gas_u_upper_erg\":{:.17e},        \"gas_u_rust_eos_erg\":{:.17e},        \"delta_electron_lower\":{:.17e},\"delta_electron_upper\":{:.17e},        \"temperature_min_k\":{:.17e},\"temperature_max_k\":{:.17e},        \"max_rel_electron_mid_discrepancy\":{:.17e},        \"max_rel_gas_energy_mid_discrepancy\":{:.17e},        \"strict_original_electron_interval_misses\":{},        \"strict_original_energy_interval_misses\":{},        \"eos_diagnostic_1e_minus10_misses\":{},        \"production\":\"HOLD\",\"canonical_delta\":0,        \"official_tick161\":\"NOT_ACCEPTED\"}}",
        result.n,result.h.total(),result.he.total(),
        result.ne_low.total(),result.ne_high.total(),result.reconstructed_ne.total(),
        result.u_low.total(),result.u_high.total(),result.reconstructed_u.total(),
        result.dne_low.total(),result.dne_high.total(),
        result.min_temperature_k,result.max_temperature_k,
        result.max_ne_relative_discrepancy,result.max_u_relative_discrepancy,
        result.ne_interval_strict_misses,result.u_interval_strict_misses,
        result.ne_relative_1e10_misses+result.u_relative_1e10_misses);
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    fn row(i: usize) -> String {
        // One physically consistent source row in the real 27-column layout.
        let nh = 1e10;
        let nhe = 1e9;
        let xh = 0.8;
        let xheii = 0.3;
        let xheiii = 0.2;
        // Synthetic source interval is an exact representation of the same
        // historical Rust EOS, not the subtly different direct f64 rounding.
        let gas = IgmGasState::from_temperature([xh, xheii, xheiii], 1.0, nhe / nh, 1e4).unwrap();
        let eos = gas.eos(1.0, nhe / nh).unwrap();
        let ne = eos.electron_density_cm3 * nh;
        let u = eos.u_erg_cm3 * nh;
        let a = vec![
            i.to_string(),
            nh.to_string(),
            nh.to_string(),
            nhe.to_string(),
            nhe.to_string(),
            "0.8".into(),
            "0.8".into(),
            xh.to_string(),
            xh.to_string(),
            xheii.to_string(),
            xheii.to_string(),
            xheiii.to_string(),
            xheiii.to_string(),
            "10000".into(),
            "10000".into(),
            "10000".into(),
            "10000".into(),
            ne.to_string(),
            ne.to_string(),
            ne.to_string(),
            ne.to_string(),
            u.to_string(),
            u.to_string(),
            "0".into(),
            "0".into(),
            "0".into(),
            "0".into(),
        ];
        a.join(",")
    }
    #[test]
    fn valid_eos_and_row_count() {
        let text = format!("{HEADER}\n{}\n", row(0));
        let r = read_source(BufReader::new(text.as_bytes()), 1).unwrap();
        assert_eq!(r.n, 1);
        assert_eq!(r.ne_relative_1e10_misses, 0);
        assert_eq!(r.u_relative_1e10_misses, 0);
        assert!((r.reconstructed_ne.total() - 8.7e9).abs() < 1.0);
    }
    #[test]
    fn rejects_missing_rows() {
        let s = format!("{HEADER}\n{}\n", row(0));
        assert!(read_source(BufReader::new(s.as_bytes()), 2).is_err());
    }
    #[test]
    fn rejects_wrong_source_schema_and_order() {
        let s = format!("badheader\n{}\n", row(0));
        assert!(read_source(BufReader::new(s.as_bytes()), 1).is_err());
        let s = format!("{HEADER}\n{}\n{}\n", row(1), row(0));
        assert!(read_source(BufReader::new(s.as_bytes()), 2).is_err());
    }
    #[test]
    fn rejects_negative_physical_source() {
        let s = format!(
            "{HEADER}\n{}\n",
            row(0).replacen("10000000000", "-10000000000", 1)
        );
        assert!(read_source(BufReader::new(s.as_bytes()), 1).is_err());
    }
}
