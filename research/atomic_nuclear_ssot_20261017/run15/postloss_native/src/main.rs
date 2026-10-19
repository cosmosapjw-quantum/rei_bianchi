use rei_run15_positive_planck::panel;
use std::io::{self, BufRead, Write};

fn response(line: &str) -> String {
    let fields: Vec<_> = line.split_whitespace().collect();
    if fields.len() != 4 {
        return "{\"error\":\"ProtocolInput\",\"detail\":\"expected lo hi kt order\"}".into();
    }
    let args = (fields[0].parse::<f64>(), fields[1].parse::<f64>(), fields[2].parse::<f64>(), fields[3].parse::<usize>());
    let (Ok(lo), Ok(hi), Ok(kt), Ok(order)) = args else {
        return "{\"error\":\"ProtocolInput\",\"detail\":\"invalid numeric field\"}".into();
    };
    match panel(lo, hi, kt, order) {
        Err(error) => format!("{{\"error\":\"{error}\"}}"),
        Ok(q) => {
            let nodes = q.nodes.iter().map(|node| format!("[{:.17e},{:.17e}]", node.energy_ev, node.absolute_weight)).collect::<Vec<_>>().join(",");
            format!("{{\"mass\":{:.17e},\"nodes\":[{}],\"mean\":{:.17e},\"retained_mean\":{:.17e},\"mass_residual\":{:.17e},\"mean_residual\":{:.17e},\"local_mean_residual\":{:.17e},\"raw_gl64_mass\":{:.17e},\"mass_anchor_scale\":{:.17e},\"eigen_residual\":{:.17e},\"order\":{}}}", q.mass, nodes, q.mean, q.retained_mean, q.mass_residual, q.mean_residual, q.local_mean_residual, q.raw_gl64_mass, q.mass_anchor_scale, q.eigen_residual, order)
        }
    }
}

fn main() -> io::Result<()> {
    let mut out = io::BufWriter::new(io::stdout().lock());
    for line in io::stdin().lock().lines() {
        writeln!(out, "{}", response(&line?))?;
        out.flush()?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn line_protocol_errors_are_json_and_do_not_panic() {
        for line in ["", "13.6 14.0 4.0", "13.6 14.0 4.0 four", "NaN 14.0 4.0 4", "14.0 13.6 4.0 4", "13.6 14.0 4.0 20"] {
            let out = response(line);
            assert!(out.starts_with("{\"error\":"));
            assert!(out.ends_with('}'));
        }
    }
}
