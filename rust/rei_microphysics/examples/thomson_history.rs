//! Export a normal-frame Thomson constitutive history from a published AX08
//! abundance CSV or a native AXBI history CSV, with a separately declared tilt.
use rei_microphysics::thomson::{thomson_history, DensityConstraint, MaterialKnot};
use std::error::Error;
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Write};

type Result<T> = std::result::Result<T, Box<dyn Error>>;
const USAGE: &str = "thomson_history AX08.csv CASE rest|normal-inventory BX BY BZ EX EY EZ (or replace BX BY BZ with --beta-series TSV)";
fn number(s: &str) -> Result<f64> {
    let v = s.parse::<f64>()?;
    if !v.is_finite() {
        return Err("nonfinite value".into());
    }
    Ok(v)
}
fn triple(s: &[String]) -> Result<[f64; 3]> {
    if s.len() != 3 {
        return Err(USAGE.into());
    }
    Ok([number(&s[0])?, number(&s[1])?, number(&s[2])?])
}
fn native_history(path: &str, case: &str) -> Result<(Vec<MaterialKnot>, f64)> {
    let mut lines = BufReader::new(File::open(path)?).lines();
    let header = lines.next().ok_or("empty abundance history")??;
    let names: Vec<_> = header.split(',').collect();
    let index = |name: &str| {
        names
            .iter()
            .position(|&s| s == name)
            .ok_or("missing history field")
    };
    let id = index("case").or_else(|_| index("case_id"))?;
    let t = index("time_s")?;
    let a = index("a")?;
    let b = index("b")?;
    let nh = index("nH_proper_cm3")?;
    let ne = index("ne_proper_cm3")?;
    let h = index("x_HII")?;
    let he1 = index("x_HeII")?;
    let he2 = index("x_HeIII")?;
    let mut out = Vec::new();
    let mut discrepancy = 0.0_f64;
    let f_he = 0.2454 / (4.0 * (1.0 - 0.2454)); // AX08 density-fixed composition.
    for l in lines {
        let line = l?;
        let row: Vec<_> = line.split(',').collect();
        if row.len() != names.len() {
            return Err("incomplete abundance row".into());
        }
        if row[id] != case {
            continue;
        }
        let (nh, ne, h, he1, he2) = (
            number(row[nh])?,
            number(row[ne])?,
            number(row[h])?,
            number(row[he1])?,
            number(row[he2])?,
        );
        if nh <= 0.0
            || ne < 0.0
            || !(0.0..=1.0).contains(&h)
            || he1 < 0.0
            || he2 < 0.0
            || he1 + he2 > 1.0 + 1e-12
        {
            return Err("abundance domain".into());
        }
        let xe = ne / nh;
        let species = h + f_he * (he1 + 2.0 * he2);
        if species != 0.0 || xe != 0.0 {
            discrepancy = discrepancy.max((species - xe).abs() / species.abs().max(xe.abs()));
        }
        out.push(MaterialKnot {
            normal_t_s: number(row[t])?,
            a: number(row[a])?,
            b: number(row[b])?,
            n_reference_m3: nh * 1e6,
            electrons_per_reference: xe,
            beta: [0.0; 3],
        });
    }
    // Two independently interpolated columns in the released 1001-knot/case AX08
    // table differ up to 1.865e-9. A materially inconsistent case is not exportable.
    if discrepancy > 1e-7 {
        return Err("AX08 proper ne and H/He charge differ by >1e-7 relative".into());
    }
    Ok((out, discrepancy))
}
fn apply_velocity_file(knots: &mut [MaterialKnot], path: &str) -> Result<()> {
    let mut rows = BufReader::new(File::open(path)?).lines();
    if rows.next().ok_or("empty velocity series")?? != "normal_t_s\tbeta_x\tbeta_y\tbeta_z" {
        return Err("velocity TSV header".into());
    }
    for knot in knots {
        let line = rows
            .next()
            .ok_or("velocity series shorter than material series")??;
        let fields = line.split('\t').map(number).collect::<Result<Vec<_>>>()?;
        let [t, bx, by, bz]: [f64; 4] =
            fields.try_into().map_err(|_| "velocity TSV field count")?;
        if t != knot.normal_t_s {
            return Err("velocity series requires exact matching normal-time knots".into());
        }
        knot.beta = [bx, by, bz];
    }
    if rows.next().is_some() {
        return Err("velocity series longer than material series".into());
    }
    Ok(())
}
fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if !(8..=9).contains(&args.len()) {
        return Err(USAGE.into());
    }
    if args[1].is_empty()
        || !args[1]
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b))
    {
        return Err("AXBI case identifier".into());
    }
    let constraint = match args[2].as_str() {
        "rest" => DensityConstraint::FixedRest,
        "normal-inventory" => DensityConstraint::FixedNormalInventory,
        _ => return Err(USAGE.into()),
    };
    let (mut knots, discrepancy) = native_history(&args[0], &args[1])?;
    let mode = if args.len() == 8 && args[3] == "--beta-series" {
        apply_velocity_file(&mut knots, &args[4])?;
        "external_history"
    } else if args.len() == 9 {
        let beta = triple(&args[3..6])?;
        for k in &mut knots {
            k.beta = beta;
        }
        if beta == [0.0; 3] {
            "native_zero"
        } else {
            "external_constant"
        }
    } else {
        return Err(USAGE.into());
    };
    let samples = thomson_history(&knots, constraint, triple(&args[args.len() - 3..])?)?;
    let mut out = BufWriter::new(io::stdout().lock());
    writeln!(out,"normal_t_s\tn_reference_rest_m3\telectrons_per_reference\tbeta_x\tbeta_y\tbeta_z\tdir_x\tdir_y\tdir_z\tN\tb")?;
    for s in &samples {
        let k = &s.material;
        let [vx, vy, vz] = k.beta;
        let [ex, ey, ez] = s.direction;
        writeln!(
            out,
            "{}\t{}\t{}\t{vx}\t{vy}\t{vz}\t{ex}\t{ey}\t{ez}\t{}\t{}",
            k.normal_t_s,
            s.n_reference_rest_m3,
            k.electrons_per_reference,
            k.a.ln(),
            k.b
        )?;
    }
    out.flush()?;
    let tau = samples[0].tau_to_receiver;
    let mass: f64 = samples.iter().map(|s| s.next_cell_mass).sum();
    eprintln!(
        r#"{{"owner":"rei_total","case":"{}","density_constraint":"{}","velocity":"{mode}","rows":{},"tau_to_terminal":{tau},"scattering_mass":{mass},"mass_closure_abs":{},"max_charge_relative_difference":{discrepancy}}}"#,
        args[1],
        args[2],
        samples.len(),
        (mass + (-tau).exp_m1()).abs()
    );
    Ok(())
}
