//! Standalone dependency-free semantic checks and exact-bit vector driver.
//! Build: rustc --edition=2021 tests/weighted_gate_tests.rs -o weighted_gate_tests
//! Run once: weighted_gate_tests --vectors results/weighted_corrected/GATE_INPUTS.tsv

#[path = "../src/weighted_gate.rs"]
mod weighted_gate;

use std::path::Path;
use weighted_gate::{evaluate, GateError, GateInput, GateOutput, Interval, StrictSign, VectorRole};

#[derive(Default)]
struct Counts {
    semantic_groups: usize,
    gate_evaluations: usize,
    returned_gate_errors: usize,
    vector_rows: usize,
}

fn point(x: f64) -> Interval {
    Interval::point(x).expect("finite semantic test constant")
}

fn contains(interval: Interval, exact_dyadic: f64) -> bool {
    interval.lo <= exact_dyadic && exact_dyadic <= interval.hi
}

fn counted(input: &GateInput, counts: &mut Counts) -> Result<GateOutput, GateError> {
    counts.gate_evaluations += 1;
    let result = evaluate(input);
    if result.is_err() {
        counts.returned_gate_errors += 1;
    }
    result
}

fn base_input(v: [f64; 4]) -> GateInput {
    GateInput {
        role: VectorRole::PhysicalPhotoPN,
        p: point(2.0),
        w: point(12.0),
        fhat: point(0.125),
        v: v.map(point),
        temperature: Some(point(48.0)),
    }
}

fn semantic_checks(counts: &mut Counts) {
    // R_low=1, a_low=1/8 eV; a_high=20 eV. A high-energy support point
    // alone does not determine the rate-weighted sign. All constants and
    // expected B/DT values here are exact dyadics, derived by hand.
    let tiny = base_input([257.0 / 256.0, 0.0, 0.0, 13.0 / 64.0]);
    let tiny_out = counted(&tiny, counts).expect("tiny tail gate");
    assert!(contains(tiny_out.balance, -745.0 / 64.0));
    assert!(contains(tiny_out.dt.unwrap(), -745.0 / 32.0));
    assert_eq!(tiny_out.balance_sign, StrictSign::Negative);
    assert_eq!(tiny_out.dt_sign, Some(StrictSign::Negative));
    // Thermal energy rises while temperature falls: the observables differ.
    assert_eq!(tiny.v[3].strict_sign().unwrap(), StrictSign::Positive);
    let large = base_input([2.0, 0.0, 0.0, 161.0 / 8.0]);
    let large_out = counted(&large, counts).expect("large tail gate");
    assert!(contains(large_out.balance, 65.0 / 4.0));
    assert!(contains(large_out.dt.unwrap(), 65.0 / 2.0));
    assert_eq!(large_out.balance_sign, StrictSign::Positive);
    assert_eq!(large_out.dt_sign, Some(StrictSign::Positive));
    counts.semantic_groups += 1;

    let zero = base_input([1.0, 0.0, 0.0, 6.0]);
    let zero_out = counted(&zero, counts).expect("zero balance gate");
    assert!(contains(zero_out.balance, 0.0));
    assert!(contains(zero_out.dt.unwrap(), 0.0));
    assert_eq!(zero_out.balance_sign, StrictSign::Unresolved);
    assert_eq!(zero_out.dt_sign, Some(StrictSign::Unresolved));
    counts.semantic_groups += 1;

    // Oppositely signed He components have a nonzero net particle effect.
    // Dropping them would reverse the certified sign in this example.
    let signed = base_input([1.0, -0.5, 0.125, 47.0 / 8.0]);
    let signed_out = counted(&signed, counts).expect("signed helium gate");
    assert!(contains(signed_out.balance, 0.125));
    assert_eq!(signed_out.balance_sign, StrictSign::Positive);
    let dropped = base_input([1.0, 0.0, 0.0, 47.0 / 8.0]);
    let dropped_out = counted(&dropped, counts).expect("contrasting omitted helium gate");
    assert!(contains(dropped_out.balance, -0.25));
    assert_eq!(dropped_out.balance_sign, StrictSign::Negative);
    counts.semantic_groups += 1;

    // Positive source scaling is linear at fixed p,w,fhat,T. Test exact
    // scalar containment, not equality of two differently widened boxes.
    let scaled = base_input([257.0 / 32.0, 0.0, 0.0, 13.0 / 8.0]);
    let scaled_out = counted(&scaled, counts).expect("positive scaling gate");
    assert!(contains(scaled_out.balance, -745.0 / 8.0));
    assert!(contains(scaled_out.dt.unwrap(), -745.0 / 4.0));
    assert_eq!(scaled_out.balance_sign, tiny_out.balance_sign);
    counts.semantic_groups += 1;

    let derivative = GateInput { role: VectorRole::BirthDerivativePM, ..tiny };
    let derivative_out = counted(&derivative, counts).expect("derivative-labelled gate");
    assert_eq!(derivative_out.role, VectorRole::BirthDerivativePM);
    assert_eq!(tiny_out.role, VectorRole::PhysicalPhotoPN);
    assert_eq!(derivative_out.balance, tiny_out.balance);
    let no_t = GateInput { temperature: None, role: VectorRole::SignedVector, ..tiny };
    let no_t_out = counted(&no_t, counts).expect("balance-only gate");
    assert_eq!(no_t_out.dt, None);
    assert_eq!(no_t_out.dt_sign, None);
    counts.semantic_groups += 1;

    for (bad, expected) in [
        (GateInput { p: point(0.0), ..tiny }, GateError::NonPositiveP),
        (GateInput { w: Interval { lo: -1.0, hi: 1.0 }, ..tiny }, GateError::NonPositiveW),
        (GateInput { p: Interval { lo: 2.0, hi: 1.0 }, ..tiny }, GateError::InvalidInterval),
        (GateInput { fhat: Interval { lo: f64::NAN, hi: 1.0 }, ..tiny }, GateError::InvalidInterval),
        (GateInput { fhat: Interval { lo: 0.0, hi: f64::INFINITY }, ..tiny }, GateError::InvalidInterval),
        (GateInput { temperature: Some(point(0.0)), ..tiny }, GateError::NonPositiveTemperature),
        (GateInput { v: [point(0.0), point(0.0), point(0.0), point(f64::MAX)], ..tiny }, GateError::NonFiniteArithmetic),
    ] {
        assert_eq!(counted(&bad, counts).unwrap_err(), expected);
    }
    assert_eq!(point(f64::MAX).add(point(0.0)).unwrap_err(), GateError::OutwardRangeOverflow);
    assert_eq!(point(1.0).div(Interval { lo: -1.0, hi: 1.0 }).unwrap_err(), GateError::DenominatorContainsZero);
    counts.semantic_groups += 1;

    // Gradual underflow: 2^-1075 lies strictly between 0 and min_subnormal.
    // A positive/negative sign must not be invented from its rounded zero.
    let sub = point(f64::from_bits(1)).mul(point(0.5)).unwrap();
    assert!(sub.lo <= 0.0 && sub.hi >= f64::from_bits(1));
    assert_eq!(sub.strict_sign().unwrap(), StrictSign::Unresolved);
    let negative_sub = point(-f64::from_bits(1)).mul(point(0.5)).unwrap();
    assert!(negative_sub.lo <= -f64::from_bits(1) && negative_sub.hi >= 0.0);
    assert_eq!(negative_sub.strict_sign().unwrap(), StrictSign::Unresolved);
    counts.semantic_groups += 1;
}

fn parse_bits(word: &str) -> Result<f64, String> {
    if word.len() != 16 || !word.bytes().all(|c| c.is_ascii_hexdigit()) {
        return Err(format!("expected 16 hexadecimal binary64 bits, got {word:?}"));
    }
    let bits = u64::from_str_radix(word, 16).map_err(|e| e.to_string())?;
    Ok(f64::from_bits(bits))
}

fn parse_interval(fields: &[&str], index: usize) -> Result<Interval, String> {
    // Keep invalid finite ordering/NaN/Inf intact for the gate's rejection.
    Ok(Interval { lo: parse_bits(fields[index])?, hi: parse_bits(fields[index + 1])? })
}

fn interval_json(value: Interval) -> String {
    format!("{{\"lo_bits\":\"{:016x}\",\"hi_bits\":\"{:016x}\"}}", value.lo.to_bits(), value.hi.to_bits())
}

fn drive_vectors(path: &Path, counts: &mut Counts) -> Result<(), String> {
    let input = std::fs::read_to_string(path).map_err(|e| format!("read vectors: {e}"))?;
    for (line_number, line) in input.lines().enumerate() {
        let text = line.trim();
        if text.is_empty() || text.starts_with('#') {
            continue;
        }
        let fields: Vec<&str> = text.split_whitespace().collect();
        if fields.len() != 18 {
            return Err(format!("line {}: expected 18 fields, got {}", line_number + 1, fields.len()));
        }
        let id = fields[0];
        if !id.bytes().all(|c| c.is_ascii_alphanumeric() || b"_.-".contains(&c)) {
            return Err(format!("line {}: unsafe case identifier", line_number + 1));
        }
        let role = match fields[1] {
            "P_N" => VectorRole::PhysicalPhotoPN,
            "P_M" => VectorRole::BirthDerivativePM,
            "SIGNED_VECTOR" => VectorRole::SignedVector,
            _ => return Err(format!("line {}: unknown role", line_number + 1)),
        };
        let temperature = if fields[16] == "-" && fields[17] == "-" {
            None
        } else {
            Some(parse_interval(&fields, 16)?)
        };
        let case = GateInput {
            role,
            p: parse_interval(&fields, 2)?,
            w: parse_interval(&fields, 4)?,
            fhat: parse_interval(&fields, 6)?,
            v: [parse_interval(&fields, 8)?, parse_interval(&fields, 10)?,
                parse_interval(&fields, 12)?, parse_interval(&fields, 14)?],
            temperature,
        };
        counts.vector_rows += 1;
        match counted(&case, counts) {
            Ok(out) => {
                let dt = out.dt.map(interval_json).unwrap_or_else(|| "null".into());
                let dt_sign = out.dt_sign.map(|s| format!("\"{}\"", s.code())).unwrap_or_else(|| "null".into());
                println!("{{\"kind\":\"gate\",\"case_id\":\"{}\",\"role\":\"{}\",\"status\":\"OK\",\"B\":{},\"B_sign\":\"{}\",\"DT\":{},\"DT_sign\":{}}}",
                    id, out.role.code(), interval_json(out.balance), out.balance_sign.code(), dt, dt_sign);
            }
            Err(error) => println!("{{\"kind\":\"gate\",\"case_id\":\"{}\",\"role\":\"{}\",\"status\":\"ERROR\",\"error\":\"{}\"}}",
                id, role.code(), error.code()),
        }
    }
    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if !(args.len() == 1 || (args.len() == 3 && args[1] == "--vectors")) {
        eprintln!("usage: weighted_gate_tests [--vectors FILE.tsv]");
        std::process::exit(2);
    }
    let mut counts = Counts::default();
    semantic_checks(&mut counts);
    println!("{{\"kind\":\"semantic_checks\",\"status\":\"PASS\",\"groups\":{}}}", counts.semantic_groups);
    if args.len() == 3 {
        if let Err(error) = drive_vectors(Path::new(&args[2]), &mut counts) {
            eprintln!("vector input failure: {error}");
            std::process::exit(2);
        }
    }
    println!("{{\"kind\":\"summary\",\"semantic_groups\":{},\"gate_evaluations\":{},\"returned_gate_errors\":{},\"vector_rows\":{},\"external_oracle_validation\":\"NOT_PERFORMED_BY_THIS_BINARY\",\"source_calls\":0,\"transport_calls\":0,\"provider_calls\":0,\"root_calls\":0}}",
        counts.semantic_groups, counts.gate_evaluations, counts.returned_gate_errors, counts.vector_rows);
}
