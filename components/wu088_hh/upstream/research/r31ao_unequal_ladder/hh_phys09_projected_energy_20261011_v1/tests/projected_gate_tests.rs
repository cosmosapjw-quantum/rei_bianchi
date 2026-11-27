//! Dependency-free saved-data consumer and hand-derived semantic checks.
//! Build once on NCP with the pinned wrapper; no test framework or Cargo.
//! Synthetic semantic inputs are distinct from the two archived source stages.
#![forbid(unsafe_code)]

#[path = "../src/projected_gate.rs"]
mod projected_gate;

use std::path::Path;
use projected_gate::{assemble_energy, determinant, dot, evaluate, inverse_action,
    inverse_setup, parse_input, projected_terms, read_input, Interval, Jet, Matrix,
    StageInput, Vector, BIRTH, CHANNELS, DIM, GROUPS, JET_COUNT, JET_WORD_PAIRS,
    LAMBDA, ONE, ROWS_PER_STAGE, ZERO};

const SEMANTIC_IDS: [&str; 7] = [
    "hh_reaction_cancellation", "five_term_sign_reversal", "zero_and_zero_touch",
    "coupled_neumann_tail", "signed_subnormal_and_zero_bits",
    "invalid_domain_and_contraction", "invalid_input_and_arithmetic",
];

fn p(x: f64) -> Interval { Interval::point(x).expect("finite dyadic fixture") }
fn identity() -> Matrix {
    std::array::from_fn(|i| std::array::from_fn(|j| if i == j { ONE } else { ZERO }))
}
fn fixture() -> StageInput {
    let mut residual = [Jet::zero(); DIM];
    for i in 0..DIM { residual[i].g[i] = ONE; }
    StageInput {
        dt: p(0.5), f_he: p(0.125), n_h: ONE, n_he: p(0.125),
        kb: ONE, ev: ONE, hmean: ZERO, chi: [p(2.0), p(4.0), p(8.0)],
        x: [Interval::new(0.125, 0.375).unwrap(), Interval::new(0.125, 0.375).unwrap(),
            Interval::new(0.125, 0.375).unwrap(), Interval::new(6.0, 10.0).unwrap()],
        center: [p(0.25), p(0.25), p(0.25), p(8.0)],
        radius: [p(0.0625), p(0.0625), p(0.0625), p(1.0)], gc: [ZERO; DIM],
        c: identity(), residual, nonphoto: [Jet::zero(); DIM],
        rates: [[Jet::zero(); CHANNELS]; GROUPS], hhq: Jet::zero(),
        heat: [[ZERO; CHANNELS]; GROUPS],
    }
}
fn sum(terms: [Interval; 5]) -> Interval {
    let mut out = ZERO;
    for value in terms { out = out.add(value).unwrap(); }
    out
}
fn assert_contains(actual: Interval, exact_dyadic: f64) {
    assert!(actual.contains(exact_dyadic), "missing exact dyadic {exact_dyadic:?}: {actual:?}");
}

fn semantic_checks() -> usize {
    projected_gate::check_arithmetic_environment().expect("IEEE-754 environment guard");
    assert_eq!(JET_COUNT, 108);
    assert_eq!(JET_WORD_PAIRS, 57);
    assert_eq!(ROWS_PER_STAGE, 6297);
    let mut groups = 0;

    // ell=(2,1/2,3/2,1). NP=(1,2,3,4), one HI rate=5,
    // heat=1/2, expansion=-2*(1/4)*8. E=2+1+9/2+4+25/2-4=20.
    // HH=q*(1,0,0,-2) contributes exactly zero for every q. Its independent
    // interval projection is wide; the assembled expression uses the identity.
    let mut f = fixture(); f.x[3] = p(8.0); f.hmean = p(0.25);
    for i in 0..DIM { f.nonphoto[i].v = p((i + 1) as f64); }
    f.rates[0][0].v = p(5.0); f.heat[0][0] = p(0.5);
    f.hhq.v = Interval::new(-1.0, 1.0).unwrap();
    let first = assemble_energy(&f).unwrap();
    assert_contains(first.v, 20.0);
    assert_eq!(first.v.sign(), "STRICT_POSITIVE");
    let naive_hh = dot([p(2.0), p(0.5), p(1.5), ONE],
        [f.hhq.v, ZERO, ZERO, p(-2.0).mul(f.hhq.v).unwrap()]).unwrap();
    assert!(naive_hh.lo < 0.0 && naive_hh.hi > 0.0);
    f.hhq.v = Interval::new(-1.0e100, 1.0e100).unwrap();
    let changed_q = assemble_energy(&f).unwrap();
    assert_eq!(first.v, changed_q.v); assert_eq!(first.g, changed_q.g);
    assert_eq!(first.h, changed_q.h);
    groups += 1;

    // Hand-derived five terms at d=1/2, U0=V0=1/2, W0=-1:
    // (-1,3/8,-1/8,1/4,1), total 1/2. Changing E_lambda,b to -2
    // changes only the last term to -1, so the total becomes -3/2.
    let mut energy = Jet::zero(); energy.g[0] = p(2.0); energy.h[0][0] = p(3.0);
    energy.h[0][LAMBDA] = p(-0.5); energy.h[LAMBDA][0] = p(-0.5);
    energy.h[0][BIRTH] = ONE; energy.h[BIRTH][0] = ONE;
    energy.h[LAMBDA][BIRTH] = p(2.0); energy.h[BIRTH][LAMBDA] = p(2.0);
    let u: Vector = [p(0.5), ZERO, ZERO, ZERO]; let v = u;
    let w: Vector = [p(-1.0), ZERO, ZERO, ZERO];
    let terms = projected_terms(p(0.5), &energy, u, v, w).unwrap();
    for (term, expected) in terms.into_iter().zip([-1.0, 0.375, -0.125, 0.25, 1.0]) {
        assert_contains(term, expected);
    }
    let positive = sum(terms); assert_contains(positive, 0.5);
    assert_eq!(positive.sign(), "STRICT_POSITIVE");
    energy.h[LAMBDA][BIRTH] = p(-2.0); energy.h[BIRTH][LAMBDA] = p(-2.0);
    let negative = sum(projected_terms(p(0.5), &energy, u, v, w).unwrap());
    assert_contains(negative, -1.5); assert_eq!(negative.sign(), "STRICT_NEGATIVE");
    groups += 1;

    let exact_zero = sum(projected_terms(ONE, &Jet::zero(), [ZERO; DIM],
        [ZERO; DIM], [ZERO; DIM]).unwrap());
    assert_contains(exact_zero, 0.0); assert_eq!(exact_zero.sign(), "ZERO_CONTAINING");
    let mut touch_jet = Jet::zero(); touch_jet.g[0] = ONE;
    let touch = sum(projected_terms(ONE, &touch_jet, [ZERO; DIM], [ZERO; DIM],
        [Interval::new(-1.0, 0.0).unwrap(), ZERO, ZERO, ZERO]).unwrap());
    assert_contains(touch, -1.0); assert_contains(touch, 0.0);
    assert_eq!(touch.sign(), "ZERO_CONTAINING");
    groups += 1;

    // K's leading 2x2 block is [[1/4,1/4],[1/4,1/4]]. With rhs=(1,1,0,0)
    // and C=I, K has eigenvalue 1/2 in that direction: A^-1 rhs=(2,2,0,0).
    // Four terms give (15/8,15/8,0,0); the exact weighted tail radius is 1/8.
    // The omitted tail would exclude the known inverse action.
    let mut a = identity(); a[0][0] = p(0.75); a[0][1] = p(-0.25);
    a[1][0] = p(-0.25); a[1][1] = p(0.75);
    let inv = inverse_setup(&a, &identity(), [ONE; DIM]).unwrap();
    assert!(inv.gamma_upper >= 0.5 && inv.gamma_upper < 0.75);
    let solved = inverse_action(&inv, [ONE, ONE, ZERO, ZERO]).unwrap();
    assert_contains(solved[0], 2.0); assert_contains(solved[1], 2.0);
    assert_contains(solved[2], 0.0); assert_contains(solved[3], 0.0);
    assert!(p(1.875).hi < 2.0);
    assert_contains(determinant(&a).unwrap(), 0.5);
    groups += 1;

    let negative_min = p(-f64::from_bits(1));
    assert_eq!(negative_min.lo.to_bits(), 0x8000_0000_0000_0001);
    let sub = negative_min.mul(p(0.5)).unwrap();
    assert!(sub.lo <= -f64::from_bits(1) && sub.hi >= 0.0);
    assert_eq!(sub.sign(), "ZERO_CONTAINING");
    let signed_zeros = Interval::new(-0.0, 0.0).unwrap();
    assert_eq!(signed_zeros.lo.to_bits(), 0x8000_0000_0000_0000);
    assert_eq!(signed_zeros.hi.to_bits(), 0);
    let negated = signed_zeros.neg().unwrap();
    assert_eq!(negated.lo.to_bits(), 0x8000_0000_0000_0000);
    assert_eq!(negated.hi.to_bits(), 0);
    groups += 1;

    let good = fixture();
    let full_gate = evaluate(&good).unwrap();
    assert!(full_gate.gamma.hi < 1.0 && full_gate.margins.iter().all(|x| x.lo > 0.0));
    let mut bad = good.clone(); bad.radius[0] = ZERO;
    assert!(evaluate(&bad).unwrap_err().starts_with("INVALID_CENTER_OR_RADIUS"));
    let mut bad = good.clone(); bad.x[0] = p(0.25);
    assert_eq!(evaluate(&bad).unwrap_err(), "BALL_NOT_INSIDE_X");
    let mut bad = good.clone(); bad.c = [[ZERO; DIM]; DIM];
    assert_eq!(evaluate(&bad).unwrap_err(), "PRECONDITIONER_NONSINGULARITY_UNRESOLVED");
    let mut bad = good.clone(); bad.residual = [Jet::zero(); DIM];
    assert_eq!(evaluate(&bad).unwrap_err(), "CONTRACTION_NOT_STRICT");
    let mut bad = good.clone(); bad.gc[0] = p(1.0);
    assert!(evaluate(&bad).unwrap_err().starts_with("STRICT_IMAGE_MARGIN_FAILED"));
    groups += 1;

    assert!(Interval::new(f64::NAN, 1.0).is_err());
    assert!(Interval::new(0.0, f64::INFINITY).is_err());
    assert!(Interval::new(2.0, 1.0).is_err());
    assert_eq!(p(f64::MAX).add(ZERO).unwrap_err(), "OUTWARD_RANGE_OVERFLOW");
    assert_eq!(p(f64::MAX).mul(p(2.0)).unwrap_err(), "NONFINITE_ARITHMETIC");
    assert_eq!(ONE.div(Interval::new(-1.0, 1.0).unwrap()).unwrap_err(), "DIVISOR_CONTAINS_ZERO");
    assert_eq!(parse_input("incorrect header\n").unwrap_err(), "INPUT_HEADER");
    let duplicate = concat!("stage\tkey\tlo_bits\thi_bits\n",
        "full\tdt\t3ff0000000000000\t3ff0000000000000\n",
        "full\tdt\t3ff0000000000000\t3ff0000000000000\n");
    assert!(parse_input(duplicate).unwrap_err().starts_with("DUPLICATE_KEY"));
    let unknown_stage = concat!("stage\tkey\tlo_bits\thi_bits\n",
        "second_half\tdt\t3ff0000000000000\t3ff0000000000000\n");
    assert!(parse_input(unknown_stage).unwrap_err().starts_with("INPUT_STAGE"));
    let uppercase = concat!("stage\tkey\tlo_bits\thi_bits\n",
        "full\tdt\t3FF0000000000000\t3ff0000000000000\n");
    assert_eq!(parse_input(uppercase).unwrap_err(), "EXPECTED_LOWERCASE_16_HEX_BITS");
    assert!(parse_input("stage\tkey\tlo_bits\thi_bits\n").unwrap_err().starts_with("STAGE_ROW_COUNT"));
    groups += 1;
    assert_eq!(groups, SEMANTIC_IDS.len());
    groups
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 || args[1] != "--vectors" {
        eprintln!("usage: projected_gate_tests --vectors FILE.tsv");
        std::process::exit(2);
    }
    let groups = semantic_checks();
    let ids = SEMANTIC_IDS.iter().map(|s| format!("\"{s}\"")).collect::<Vec<_>>().join(",");
    println!("{{\"type\":\"semantic_checks\",\"status\":\"PASS\",\"groups\":{},\"case_ids\":[{}],\"data_origin\":\"HAND_DERIVED_SYNTHETIC_DISTINCT_FROM_ARCHIVED_STAGES\"}}", groups, ids);
    let stages = match read_input(Path::new(&args[2])) {
        Ok(value) => value,
        Err(error) => { eprintln!("saved input failure: {error}"); std::process::exit(2); }
    };
    for (name, input) in ["full", "first_half"].into_iter().zip(stages.iter()) {
        match evaluate(input).and_then(|out| out.json(name)) {
            Ok(row) => println!("{row}"),
            Err(error) => { eprintln!("stage {name}: {error}"); std::process::exit(1); }
        }
    }
    println!(concat!("{{\"type\":\"summary\",\"semantic_groups\":{},",
        "\"archived_stage_evaluations\":2,\"semantic_gate_evaluations\":6,",
        "\"input_rows\":{},\"source_routes\":0,",
        "\"provider_routes\":0,\"root_routes\":0,",
        "\"external_oracle_validation\":\"NOT_PERFORMED_BY_THIS_BINARY\"}}"),
        groups, 2 * ROWS_PER_STAGE);
}
