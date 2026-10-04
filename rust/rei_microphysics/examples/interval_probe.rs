use rei_microphysics::{Interval, Jet};
use std::io::{self, BufRead};

fn pair(v: Interval) -> String {
    format!("[{:.17e},{:.17e}]", v.lo, v.hi)
}

fn parse(s: &str) -> Option<f64> {
    let x: f64 = s.parse().ok()?;
    x.is_finite().then_some(x)
}

fn run(line: &str) -> Option<String> {
    let fields: Vec<_> = line.split_whitespace().collect();
    let op = *fields.first()?;
    let expected = match op {
        "EXP" | "LN" => 3,
        "POW" => 4,
        "JET_BETA" => 5,
        _ => return None,
    };
    if fields.len() != expected {
        return None;
    }
    let input = Interval::new(parse(fields[1])?, parse(fields[2])?).ok()?;
    match op {
        "EXP" => Some(format!("{{\"value\":{}}}", pair(input.exp().ok()?))),
        "LN" => Some(format!("{{\"value\":{}}}", pair(input.ln().ok()?))),
        "POW" => Some(format!(
            "{{\"value\":{}}}",
            pair(input.powf(parse(fields[3])?).ok()?)
        )),
        "JET_BETA" => {
            let a = Jet::constant(Interval::point(parse(fields[3])?).ok()?).ok()?;
            let minus_b = Jet::constant(Interval::point(-parse(fields[4])?).ok()?).ok()?;
            let t = Jet::variable(input, 0).ok()?;
            let result = a
                .mul(&t.powf(0.5).ok()?)
                .ok()?
                .mul(&minus_b.div(&t).ok()?.exp().ok()?)
                .ok()?;
            let gradient = result
                .gradient
                .iter()
                .map(|v| pair(*v))
                .collect::<Vec<_>>()
                .join(",");
            let hessian = result
                .hessian
                .iter()
                .map(|row| {
                    format!(
                        "[{}]",
                        row.iter().map(|v| pair(*v)).collect::<Vec<_>>().join(",")
                    )
                })
                .collect::<Vec<_>>()
                .join(",");
            Some(format!(
                "{{\"value\":{},\"gradient\":[{}],\"hessian\":[{}]}}",
                pair(result.value),
                gradient,
                hessian
            ))
        }
        _ => None,
    }
}

fn main() {
    for line in io::stdin().lock().lines() {
        match line {
            Ok(line) => println!(
                "{}",
                run(&line).unwrap_or_else(|| "{\"error\":true}".to_string())
            ),
            Err(_) => break,
        }
    }
}
