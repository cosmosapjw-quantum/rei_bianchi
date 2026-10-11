//! Opt-in production protocol for the fixed conditional P01 interval.
use rei_microphysics::axisym_conditional::ConditionalSession;
use std::io::{self, BufRead, Write};

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = stdout.lock();
    let mut session = ConditionalSession::default();
    for line in stdin.lock().lines() {
        match session.command(&line?) {
            Ok(values) => {
                write!(out, "OK")?;
                for value in values {
                    write!(out, " {value:.17e}")?;
                }
                writeln!(out)?;
            }
            Err(error) => writeln!(out, "ERR {error}")?,
        }
        out.flush()?;
    }
    Ok(())
}
