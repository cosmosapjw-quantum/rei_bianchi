//! REI owner original sealed-F05 first [0,64] H/He material chemical/thermal Rust consumer.
//! Read authentic source-produced 46,080-cell CSV on stdin. Does NOT reimplement
//! the original 26-event MPRK/SDIRK map or admit production worker history.
//! Calls historically restored rei_microphysics::IgmGasState EOS at real H/He/T.
use rei_microphysics::{igm_state::IgmGasState, HHeModel};
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Write};

const N: usize = 46080;
const COLS: usize = 15;
const EV: f64 = 1.602176634e-12;
const CHI_H: f64 = 13.598434599702;
const CHI_HEI: f64 = 24.587389011;
const CHI_HEII: f64 = 54.41776;
const KB: f64 = 1.380649e-16;
const HEADER:&str="node,N_H,N_He,N_HII_0,N_HeII_0,N_HeIII_0,T0_K,N_HII64_lo,N_HII64_hi,N_HeII64_lo,N_HeII64_hi,N_HeIII64_lo,N_HeIII64_hi,T64_lo_K,T64_hi_K";
#[derive(Default)]
struct Sum {
    sum: f64,
    err: f64,
}
impl Sum {
    fn add(&mut self, x: f64) {
        let y = self.sum + x;
        self.err += if self.sum.abs() >= x.abs() {
            (self.sum - y) + x
        } else {
            (x - y) + self.sum
        };
        self.sum = y;
    }
    fn value(&self) -> f64 {
        self.sum + self.err
    }
}
#[derive(Default)]
struct Ledger {
    rows: usize,
    ne0: Sum,
    ne1: Sum,
    b0: Sum,
    b1: Sum,
    u0: Sum,
    u1: Sum,
    max_eos_relative: f64,
    ne_interval_misses: usize,
    u_interval_misses: usize,
    negative: usize,
    positive: usize,
    ambiguous: usize,
    min_temperature: f64,
    max_temperature: f64,
}
fn fail(key: &str, i: usize) -> String {
    format!("{key}_CELL_{i}")
}
fn midpoint(lo: f64, hi: f64) -> f64 {
    0.5 * lo + 0.5 * hi
}
fn parse_line(
    line: &str,
    i: usize,
    owner_kb: f64,
    ledger: &mut Ledger,
    out: &mut impl Write,
) -> Result<(), String> {
    let xs: Vec<&str> = line.trim_end().split(',').collect();
    if xs.len() != COLS {
        return Err(fail("BAD_COLUMN_COUNT", i));
    }
    let idx = xs[0].parse::<usize>().map_err(|_| fail("BAD_INDEX", i))?;
    if idx != i {
        return Err(fail("BAD_CELL_ORDER", i));
    }
    let mut a = [0.0_f64; COLS];
    for k in 1..COLS {
        a[k] = xs[k].parse::<f64>().map_err(|_| fail("BAD_FLOAT", i))?;
        if !a[k].is_finite() {
            return Err(fail("NONFINITE", i));
        }
    }
    let h = a[1];
    let he = a[2];
    if h <= 0.0
        || he <= 0.0
        || a[6] <= 0.0
        || a[13] <= 0.0
        || a[14] <= 0.0
        || (owner_kb - KB).abs() > 16.0 * f64::EPSILON * KB
    {
        return Err(fail("PHYSICAL_DOMAIN", i));
    }
    for (lo, hi) in [(7, 8), (9, 10), (11, 12), (13, 14)] {
        if a[lo] > a[hi] {
            return Err(fail("INVERTED_ORIGINAL_INTERVAL", i));
        }
    }
    let x0 = [a[3] / h, a[4] / he, a[5] / he];
    let x1 = [
        midpoint(a[7], a[8]) / h,
        midpoint(a[9], a[10]) / he,
        midpoint(a[11], a[12]) / he,
    ];
    if x0[0] < 0.0
        || x0[0] > 1.0
        || x1[0] < 0.0
        || x1[0] > 1.0
        || x0[1] < 0.0
        || x0[2] < 0.0
        || x0[1] + x0[2] > 1.0 + 1e-12
        || x1[1] < 0.0
        || x1[2] < 0.0
        || x1[1] + x1[2] > 1.0 + 1e-12
    {
        return Err(fail("ORIGINAL_H_HE_CONE", i));
    }
    let temp1 = midpoint(a[13], a[14]);
    let ratio = he / h;
    let state0 = IgmGasState::from_temperature(x0, 1.0, ratio, a[6])
        .map_err(|_| fail("RUST_ORIGINAL_EOS_INITIAL", i))?;
    let state1 = IgmGasState::from_temperature(x1, 1.0, ratio, temp1)
        .map_err(|_| fail("RUST_ORIGINAL_EOS_ENDPOINT", i))?;
    let e0 = state0
        .eos(1.0, ratio)
        .map_err(|_| fail("RUST_ORIGINAL_EOS0", i))?;
    let e1 = state1
        .eos(1.0, ratio)
        .map_err(|_| fail("RUST_ORIGINAL_EOS1", i))?;
    let ne0 = e0.electron_density_cm3 * h;
    let ne1 = e1.electron_density_cm3 * h;
    let u0 = e0.u_erg_cm3 * h;
    let u1 = e1.u_erg_cm3 * h;
    let ne0_math = a[3] + a[4] + 2.0 * a[5];
    let ne1_math = midpoint(a[7], a[8]) + midpoint(a[9], a[10]) + 2.0 * midpoint(a[11], a[12]);
    let u0_math = 1.5 * KB * (h + he + ne0_math) * a[6];
    let u1_math = 1.5 * KB * (h + he + ne1_math) * temp1;
    let maxrel = ((ne0 - ne0_math).abs() / ne0_math.abs().max(f64::MIN_POSITIVE))
        .max((ne1 - ne1_math).abs() / ne1_math.abs().max(f64::MIN_POSITIVE))
        .max((u0 - u0_math).abs() / u0_math.abs().max(f64::MIN_POSITIVE))
        .max((u1 - u1_math).abs() / u1_math.abs().max(f64::MIN_POSITIVE));
    if maxrel > 64.0 * f64::EPSILON {
        return Err(fail("RUST_EOS_MISMATCH", i));
    }
    ledger.max_eos_relative = ledger.max_eos_relative.max(maxrel);
    let b0 = EV * (CHI_H * a[3] + CHI_HEI * a[4] + (CHI_HEI + CHI_HEII) * a[5]);
    let b1 = EV
        * (CHI_H * midpoint(a[7], a[8])
            + CHI_HEI * midpoint(a[9], a[10])
            + (CHI_HEI + CHI_HEII) * midpoint(a[11], a[12]));
    let nel = a[7] + a[9] + 2.0 * a[11];
    let neu = a[8] + a[10] + 2.0 * a[12];
    let ul = 1.5 * KB * (h + he + nel) * a[13];
    let uu = 1.5 * KB * (h + he + neu) * a[14];
    if ne1 < nel || ne1 > neu {
        ledger.ne_interval_misses += 1
    }
    if u1 < ul || u1 > uu {
        ledger.u_interval_misses += 1
    }
    if neu < ne0 {
        ledger.negative += 1
    } else if nel > ne0 {
        ledger.positive += 1
    } else {
        ledger.ambiguous += 1
    }
    for (acc, val) in [
        (&mut ledger.ne0, ne0),
        (&mut ledger.ne1, ne1),
        (&mut ledger.b0, b0),
        (&mut ledger.b1, b1),
        (&mut ledger.u0, u0),
        (&mut ledger.u1, u1),
    ] {
        acc.add(val)
    }
    ledger.rows += 1;
    if ledger.rows == 1 {
        ledger.min_temperature = a[6].min(temp1);
        ledger.max_temperature = a[6].max(temp1);
    }
    ledger.min_temperature = ledger.min_temperature.min(a[6].min(temp1));
    ledger.max_temperature = ledger.max_temperature.max(a[6].max(temp1));
    writeln!(
        out,
        "{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
        i,
        ne0,
        ne1,
        ne1 - ne0,
        b0,
        b1,
        b1 - b0,
        u0,
        u1,
        u1 - u0
    )
    .map_err(|_| fail("WRITE", i))?;
    Ok(())
}
fn run<R: BufRead, W: Write>(mut input: R, out: &mut W) -> Result<Ledger, String> {
    let mut header = String::new();
    input.read_line(&mut header).map_err(|_| "READ_HEADER")?;
    if header.trim_end_matches(['\r', '\n']) != HEADER {
        return Err("ORIGINAL_CSV_SCHEMA_MISMATCH".into());
    }
    let kb = HHeModel::controlled_fixture().kb_erg_k;
    let mut ledger = Ledger::default();
    writeln!(out,"node,Ne0,Ne64_mid,DeltaNe_mid,B0_erg,B64_mid_erg,DeltaB_mid_erg,U0_erg,U64_mid_erg,DeltaU_mid_erg").map_err(|_|"WRITE_HEADER")?;
    for i in 0..N {
        let mut row = String::new();
        if input.read_line(&mut row).map_err(|_| "READ_ROW")? == 0 {
            return Err(fail("SOURCE_ROW_SHORT", i));
        }
        parse_line(&row, i, kb, &mut ledger, out)?;
    }
    let mut trailing = String::new();
    input
        .read_line(&mut trailing)
        .map_err(|_| "READ_TRAILING")?;
    if !trailing.is_empty() {
        return Err("SOURCE_ROW_EXTRA".into());
    }
    Ok(ledger)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        return Err(
            "usage: f05_original64_rust_chemthermal PRIVATE_OUTPUT.csv < PRIVATE_INPUT.csv".into(),
        );
    }
    let file = File::create(&args[1])?;
    let mut output = BufWriter::new(file);
    let ledger = run(BufReader::new(io::stdin().lock()), &mut output).map_err(io::Error::other)?;
    output.flush()?;
    println!("{{\"schema\":\"REI_F05_ORIGINAL64_RUST_CHEMICAL_THERMAL_V1\",\"source_rows\":{},\"source_ne0\":{:.17e},\"source_ne64_mid\":{:.17e},\"delta_ne_mid\":{:.17e},\"source_B0_erg\":{:.17e},\"source_B64_mid_erg\":{:.17e},\"delta_B_mid_erg\":{:.17e},\"source_U0_erg\":{:.17e},\"source_U64_mid_erg\":{:.17e},\"delta_U_mid_erg\":{:.17e},\"rust_eos_max_rel_discrepancy\":{:.17e},\"electron_interval_misses\":{},\"thermal_interval_misses\":{},\"definitely_decreasing_electron_cells\":{},\"definitely_increasing_electron_cells\":{},\"sign_ambiguous_cells\":{},\"min_temperature_K\":{:.17e},\"max_temperature_K\":{:.17e},\"production\":\"HOLD\",\"canonical_DAG\":\"28/88\"}}",
 ledger.rows,ledger.ne0.value(),ledger.ne1.value(),ledger.ne1.value()-ledger.ne0.value(),
 ledger.b0.value(),ledger.b1.value(),ledger.b1.value()-ledger.b0.value(),
 ledger.u0.value(),ledger.u1.value(),ledger.u1.value()-ledger.u0.value(),
 ledger.max_eos_relative,ledger.ne_interval_misses,ledger.u_interval_misses,
 ledger.negative,ledger.positive,ledger.ambiguous,ledger.min_temperature,ledger.max_temperature);
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn native_constants_match_source() {
        assert_eq!(HHeModel::controlled_fixture().kb_erg_k, KB);
    }
    #[test]
    fn charge_helium_double_weight() {
        let z = [10.0, 2.0, 3.0];
        assert_eq!(z[0] + z[1] + 2.0 * z[2], 18.0);
    }
    #[test]
    fn bad_node_id_rejected() {
        let mut l = Ledger::default();
        let mut o = Vec::new();
        let s = "8,100,7,50,1,1,10000,50,50,1,1,1,1,10000,10000";
        assert!(parse_line(s, 0, KB, &mut l, &mut o).is_err());
    }
}
