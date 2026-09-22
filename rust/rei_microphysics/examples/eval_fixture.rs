//! Bounded whitespace protocol frontend. Calls the library, never an oracle.
use rei_microphysics::*;
use std::io::{self, BufRead};

struct Tokens<'a>(std::str::SplitWhitespace<'a>);
impl<'a> Tokens<'a> {
    fn text(&mut self) -> Result<&'a str, ForwardError> {
        self.0.next().ok_or(ForwardError::InvalidInput("BAD_SHAPE"))
    }
    fn number(&mut self) -> Result<f64, ForwardError> {
        match self.text()? {
            "NaN" => Ok(f64::NAN), "Inf" => Ok(f64::INFINITY), "-Inf" => Ok(f64::NEG_INFINITY),
            s => s.parse().map_err(|_| ForwardError::InvalidInput("BAD_FLOAT")),
        }
    }
    fn count(&mut self) -> Result<usize, ForwardError> {
        let n: usize = self.text()?.parse().map_err(|_| ForwardError::InvalidInput("BAD_SHAPE"))?;
        if n > 65536 { return Err(ForwardError::InvalidInput("BAD_SHAPE")); }
        Ok(n)
    }
    fn vector(&mut self, n: usize) -> Result<Vec<f64>, ForwardError> {
        (0..n).map(|_| self.number()).collect()
    }
    fn array<const N: usize>(&mut self) -> Result<[f64; N], ForwardError> {
        self.vector(N)?.try_into().map_err(|_| ForwardError::InvalidInput("BAD_SHAPE"))
    }
    fn table(&mut self) -> Result<PchipTable, ForwardError> {
        let n = self.count()?;
        if n < 2 { return Err(ForwardError::InvalidInput("BAD_TABLE")); }
        let knots = self.vector(n)?;
        let c = [self.vector(n-1)?, self.vector(n-1)?, self.vector(n-1)?, self.vector(n-1)?];
        PchipTable::new(knots, c)
    }
    fn end(&mut self) -> Result<(), ForwardError> {
        if self.0.next().is_some() { Err(ForwardError::InvalidInput("BAD_SHAPE")) } else { Ok(()) }
    }
}
fn evaluate(op: &str, t: &mut Tokens<'_>) -> Result<Vec<f64>, ForwardError> {
    match op {
        "mass" | "signed" => {
            let v = t.number()?; let n = t.count()?; let prior = t.vector(n)?; t.end()?;
            if op == "mass" { positive_mass_projection(&prior, v) }
            else { let s = signed_transfer_lift(v, &prior)?; Ok([s.positive, s.negative, s.signed].concat()) }
        }
        "transform" => {
            let z = t.array::<9>()?; t.end()?; let s = transform_z_to_y(&z);
            let mut out = s.n_comoving_per_cmpc3.to_vec(); out.push(s.x_hii);
            out.extend(s.helium); out.extend([s.u_erg_per_cm3, s.gamma_hi_per_s]); Ok(out)
        }
        "pchip" => {
            let x = t.number()?; let table = t.table()?; t.end()?; Ok(vec![pchip_eval(&table, x)?])
        }
        "gamma" | "opacity" | "photons" => {
            let s = State { n_comoving_per_cmpc3: t.array()?, x_hii: t.number()?, helium: t.array()?, u_erg_per_cm3: t.number()?, gamma_hi_per_s: t.number()? };
            let z = t.number()?; let nh = t.number()?; let nhe = t.number()?; let h = t.number()?;
            let hi = t.array()?; let hei = t.array()?; let heii = t.array()?;
            let red = t.array()?; let fraction = t.array()?; let emission = t.array()?;
            let tables = [t.table()?, t.table()?]; t.end()?;
            let p = GroupParams { redshift: z, n_h_proper_per_cm3: nh, n_he_proper_per_cm3: nhe,
                hubble_per_s: h, sigma_hi_cm2: hi, sigma_hei_cm2: hei, sigma_heii_cm2: heii,
                redshift_coeff: red, source_fraction: fraction, lowgroup_log_opacity: tables };
            if op == "gamma" { let g = gamma_species(&s, &p); let mut out = vec![g.hi_per_s, g.hei_per_s, g.heii_per_s]; out.extend(g.group_hi_per_s); Ok(out) }
            else if op == "opacity" { Ok(opacity_cMpc_inv(&s, &p)?.to_vec()) }
            else { Ok(photon_rates(&s, &emission, &p)?.to_vec()) }
        }
        _ => Err(ForwardError::InvalidInput("BAD_OPERATION")),
    }
}
fn token(v: f64) -> String {
    if v.is_nan() { "NaN".into() } else if v == f64::INFINITY { "Inf".into() }
    else if v == f64::NEG_INFINITY { "-Inf".into() } else { format!("{v:.17e}") }
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    for line in io::stdin().lock().lines() {
        let line = line?;
        if line.trim().is_empty() { continue; }
        let mut t = Tokens(line.split_whitespace());
        let id = t.text()?; let op = t.text()?;
        match evaluate(op, &mut t) {
            Ok(values) => println!("{} OK {}{}", id, values.len(), values.iter().map(|v| format!(" {}", token(*v))).collect::<String>()),
            Err(e) => println!("{} ERR {}", id, e.code()),
        }
    }
    Ok(())
}
