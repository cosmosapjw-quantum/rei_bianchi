// Bounded regression driver. All scientific calls use pinned original modules.
// This file is prepared but has not been compiled in the ChatGPT runtime.
use std::io::{self, Read};

struct Tokens<'a>(std::str::SplitWhitespace<'a>);
impl<'a> Tokens<'a> {
    fn next_f(&mut self) -> Result<f64, String> {
        self.0.next().ok_or("INPUT_EOF")?.parse().map_err(|_| "INPUT_FLOAT".into())
    }
    fn next_n(&mut self) -> Result<usize, String> {
        self.0.next().ok_or("INPUT_EOF")?.parse().map_err(|_| "INPUT_INTEGER".into())
    }
    fn three(&mut self) -> Result<[f64; 3], String> {
        Ok([self.next_f()?, self.next_f()?, self.next_f()?])
    }
    fn four(&mut self) -> Result<[f64; 4], String> {
        Ok([self.next_f()?, self.next_f()?, self.next_f()?, self.next_f()?])
    }
}
fn array_json(xs: &[f64]) -> String {
    format!("[{}]", xs.iter().map(|x| format!("{:.17e}", x)).collect::<Vec<_>>().join(","))
}
fn run_probe() -> Result<(), String> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).map_err(|e| e.to_string())?;
    let mut t = Tokens(input.split_whitespace());
    let count = t.next_n()?;
    let provider = AtomicProvider::reference();
    let mut returned_bin_absorption = [0.0_f64; 3];
    for i in 0..count {
        let a = t.next_f()?;
        let density = t.three()?;
        let n = t.next_n()?;
        if n > 4096 { return Err("UNBOUNDED_NODE_INPUT".into()); }
        let mut nodes = Vec::with_capacity(n);
        for _ in 0..n {
            nodes.push(PhotonNode { energy_ev: t.next_f()?, n_comoving_per_cmpc3: t.next_f()? });
        }
        match homogeneous_photo_rates(&provider, density, a, &nodes) {
            Ok(r) => {
                if i < 3 { returned_bin_absorption[i] = r.events_proper_per_cm3_s.iter().sum(); }
                println!("{{\"kind\":\"photo\",\"index\":{},\"status\":\"ok\",\"gamma\":{},\"events\":{},\"heat\":{},\"binding\":{},\"absorbed\":{:.17e},\"loss_comoving\":{:.17e}}}",
                    i, array_json(&r.gamma_per_s), array_json(&r.events_proper_per_cm3_s),
                    array_json(&r.heat_erg_per_cm3_s), array_json(&r.binding_erg_per_cm3_s),
                    r.absorbed_erg_per_cm3_s, r.photon_loss_comoving_per_cmpc3_s);
            },
            Err(e) => {
                if i < 3 { return Err(format!("BASELINE_NATIVE_CALL_{}_FAILED:{}", i, e)); }
                println!("{{\"kind\":\"photo\",\"index\":{},\"status\":\"error\",\"error\":\"{}\"}}", i, e.code());
            }
        }
    }
    let a = t.next_f()?;
    let h = t.next_f()?;
    let photons = t.three()?;
    let edges = t.four()?;
    let traces = t.four()?;
    let source = t.three()?;
    if t.0.next().is_some() { return Err("UNCONSUMED_INPUT".into()); }
    // No expected/reference absorption is read from input: these sinks are
    // the actual bin0/1/2 native event returns above.
    let p = flrw_three_equations::photon_balance(flrw_three_equations::PhotonInput {
        scale_factor: a, hubble_s: h, comoving_photons_cm3: photons,
        edge_energy_ev: edges, edge_n_per_cm3_ev: traces,
        source_proper_cm3_s: source, absorption_proper_cm3_s: returned_bin_absorption,
    }).map_err(|e| e.to_string())?;
    println!("{{\"kind\":\"photon\",\"status\":\"ok\",\"dc\":{},\"dp\":{},\"flux\":{},\"loss\":{:.17e},\"source\":{:.17e},\"absorption\":{:.17e},\"residual\":{:.17e}}}",
        array_json(&p.comoving_dot_cm3_s), array_json(&p.proper_dot_cm3_s),
        array_json(&p.edge_flux_comoving_cm3_s), p.boundary_net_loss_comoving_cm3_s,
        p.source_comoving_cm3_s, p.absorption_comoving_cm3_s, p.summed_balance_residual);
    Ok(())
}
fn main() {
    if let Err(e) = run_probe() { eprintln!("{e}"); std::process::exit(2); }
}
