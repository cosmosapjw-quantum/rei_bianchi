//! Write a BASS `--ionization` table (eta, x_e per H) that joins a REC/HYREC
//! recombination table, one native AX08 REI case and the donor-matched z<4
//! continuation. Usage:
//!   bass_ionization REC.tsv AX08.csv CASE [--z-emit 1100] [--z-heii 3.5]
//!                   [--dz-heii 0.5] [--dz 0.01] [--physical-tail FILE.tsv] > merged.tsv 2> report.json
use rei_microphysics::bass_ionization::{merge, merge_with_physical_tail, Continuation, Knot};
use std::error::Error;
use std::fs;

type Result<T> = std::result::Result<T, Box<dyn Error>>;

/// AX08 density-fixed composition (Y_He = 0.2454).
const F_HE: f64 = 0.2454 / (4.0 * (1.0 - 0.2454));

fn read_rec(path: &str) -> Result<Vec<Knot>> {
    let text = fs::read_to_string(path)?;
    let mut lines = text.lines();
    if lines.next().map(str::trim) != Some("eta\txe_per_H") {
        return Err("REC table header must be 'eta<TAB>xe_per_H'".into());
    }
    lines
        .filter(|l| !l.trim().is_empty())
        .map(|l| {
            let mut f = l.split('\t');
            let eta: f64 = f.next().ok_or("missing eta")?.parse()?;
            let xe: f64 = f.next().ok_or("missing x_e")?.parse()?;
            Ok(Knot { eta, xe })
        })
        .collect()
}

fn read_ax08(path: &str, case: &str) -> Result<Vec<(f64, f64)>> {
    let text = fs::read_to_string(path)?;
    let mut lines = text.lines();
    let header: Vec<&str> = lines.next().ok_or("empty AX08 table")?.split(',').collect();
    let col = |name: &str| {
        header
            .iter()
            .position(|h| *h == name)
            .ok_or(format!("AX08 table lacks column {name}"))
    };
    let (c_case, c_z, c_xe) = (col("case")?, col("zbar")?, col("xe_per_H")?);
    let mut rows = Vec::new();
    for (idx, line) in lines.filter(|l| !l.trim().is_empty()).enumerate() {
        let f: Vec<&str> = line.split(',').collect();
        if f.get(c_case) == Some(&case) {
            let z_s = f
                .get(c_z)
                .ok_or_else(|| format!("missing zbar column on row {}", idx + 2))?;
            let xe_s = f
                .get(c_xe)
                .ok_or_else(|| format!("missing xe_per_H column on row {}", idx + 2))?;
            rows.push((z_s.parse()?, xe_s.parse()?));
        }
    }
    if rows.is_empty() {
        return Err(format!("no AX08 rows for case {case}").into());
    }
    Ok(rows)
}

/// Caller-supplied native low-z history with explicit mean-redshift clock.
fn read_tail(path: &str) -> Result<Vec<(f64, f64)>> {
    let text = fs::read_to_string(path)?;
    let mut lines = text.lines();
    if lines.next().map(str::trim) != Some("zbar\txe_per_H") {
        return Err("tail header must be zbar<TAB>xe_per_H".into());
    }
    lines
        .filter(|l| !l.trim().is_empty())
        .map(|l| {
            let f: Vec<_> = l.split_whitespace().collect();
            if f.len() != 2 {
                return Err("tail row must contain exactly zbar and xe_per_H".into());
            }
            Ok((f[0].parse()?, f[1].parse()?))
        })
        .collect()
}

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() < 3 || args.len() % 2 == 0 {
        return Err("usage: bass_ionization REC.tsv AX08.csv CASE [--z-emit Z --z-heii Z --dz-heii DZ --dz DZ --physical-tail FILE.tsv]".into());
    }
    let mut z_emit = 1100.0;
    let mut cont = Continuation {
        f_he: F_HE,
        z_heii: 3.5,
        dz_heii: 0.5,
    };
    let mut dz = 0.01;
    let mut physical_tail = None;
    let mut placeholder_options = false;
    for pair in args[3..].chunks(2) {
        if pair[0] == "--physical-tail" {
            if physical_tail.replace(pair[1].as_str()).is_some() {
                return Err("duplicate physical-tail option".into());
            }
            continue;
        }
        let v: f64 = pair[1].parse()?;
        placeholder_options |= pair[0] != "--z-emit";
        match pair[0].as_str() {
            "--z-emit" => z_emit = v,
            "--z-heii" => cont.z_heii = v,
            "--dz-heii" => cont.dz_heii = v,
            "--dz" => dz = v,
            other => return Err(format!("unknown option {other}").into()),
        }
    }
    let rec = read_rec(&args[0])?;
    let rei = read_ax08(&args[1], &args[2])?;
    if physical_tail.is_some() && placeholder_options {
        return Err("physical-tail replaces the placeholder continuation options".into());
    }
    let (knots, report) = if let Some(path) = physical_tail {
        merge_with_physical_tail(&rec, &rei, &read_tail(path)?, z_emit, F_HE)?
    } else {
        merge(&rec, &rei, z_emit, cont, dz)?
    };
    println!("eta\txe_per_H");
    for k in &knots {
        println!("{:.17e}\t{:.17e}", k.eta, k.xe);
    }
    if physical_tail.is_some() {
        eprintln!("{{\"schema\":\"rei.bass_ionization.v2\",\"tail_owner\":\"caller_supplied_history\",\"z_below_low_is_conditional_placeholder\":false,\"z_high\":{},\"z_low\":{},\"jump_at_z_high\":{:e},\"rec_knots\":{},\"rei_knots\":{},\"physical_tail_knots\":{}}}",report.z_high,report.z_low,report.jump_at_z_high,report.rec_knots,report.rei_knots,report.continuation_knots);
        return Ok(());
    }
    eprintln!(
        "{{\"schema\":\"rei.bass_ionization.v1\",\"case\":\"{}\",\"z_emit\":{},\"f_he\":{},\"z_heii\":{},\"dz_heii\":{},\"z_high\":{},\"z_low\":{},\"jump_at_z_high\":{:e},\"rec_knots\":{},\"rei_knots\":{},\"continuation_knots\":{},\"z_below_low_is_conditional_placeholder\":true}}",
        args[2],
        z_emit,
        cont.f_he,
        cont.z_heii,
        cont.dz_heii,
        report.z_high,
        report.z_low,
        report.jump_at_z_high,
        report.rec_knots,
        report.rei_knots,
        report.continuation_knots
    );
    Ok(())
}
