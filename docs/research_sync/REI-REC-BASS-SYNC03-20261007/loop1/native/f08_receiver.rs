// Research-only density consumer. The imported modules are exact BASS sources.
#[allow(dead_code)]
mod microphysics {
    pub mod frame;
    pub mod visibility;
    pub mod visibility_clock;
}
use microphysics::frame::MaterialFrame;
use microphysics::visibility::ElectronState;
use microphysics::visibility_clock::{integrate_clock_visibility, RayClockGrid};
use std::io::{self, BufRead, Write};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut times = Vec::<f64>::new();
    let mut ne_cm3 = Vec::<f64>::new();
    let mut rates = Vec::<f64>::new();
    let frame = MaterialFrame::new([0.0; 3]).unwrap();
    for (line_no, line) in io::stdin().lock().lines().enumerate() {
        let line = line?;
        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() != 2 { return Err(format!("expected t,ne at row {line_no}").into()); }
        let t: f64 = fields[0].parse()?;
        let ne: f64 = fields[1].parse()?;
        // This is an algebraic aggregate-density container, not H-only composition.
        let electrons = ElectronState::new(ne * 1_000_000.0, 0.0, 1.0, 0.0, 0.0)
            .map_err(|e| format!("density row {line_no}: {e:?}"))?;
        let q = electrons.scattering_rate_per_normal_second(frame, [1.0, 0.0, 0.0])
            .map_err(|e| format!("rate row {line_no}: {e:?}"))?;
        times.push(t); ne_cm3.push(ne); rates.push(q);
    }
    let means: Vec<f64> = rates.windows(2).map(|q| (q[0] + q[1]) * 0.5).collect();
    let baseline = integrate_clock_visibility(RayClockGrid::NormalSeconds { edges_seconds: &times }, &means, 0.0)
        .map_err(|e| format!("baseline schedule: {e:?}"))?;
    let tail = integrate_clock_visibility(RayClockGrid::NormalSeconds { edges_seconds: &times }, &means, 0.1)
        .map_err(|e| format!("tail schedule: {e:?}"))?;
    let mut out = io::BufWriter::new(io::stdout().lock());
    writeln!(out, "normal_time_s,ne_proper_cm3,q_normal_s_inverse,tau_tail0,survival_tail0,cell_probability_tail0,tau_tail01,survival_tail01,cell_probability_tail01")?;
    for i in 0..times.len() {
        let p = baseline.visibility.interval_probability.get(i).copied().unwrap_or(0.0);
        let pt = tail.visibility.interval_probability.get(i).copied().unwrap_or(0.0);
        writeln!(out, "{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}", times[i], ne_cm3[i], rates[i], baseline.visibility.optical_depth[i], baseline.visibility.survival[i], p, tail.visibility.optical_depth[i], tail.visibility.survival[i], pt)?;
    }
    out.flush()?;
    Ok(())
}
