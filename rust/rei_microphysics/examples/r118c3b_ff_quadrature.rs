use rei_microphysics::ff_balance::absorption_ratio_n;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("T,Tcmb,z2frac,mode,n,ratio");
    for t in [8., 10., 20., 50., 100., 132., 236., 1e4] {
        for tc in [50., 57.] {
            for f in [0., 0.2, 1.] {
                for m in [1, 2] {
                    for n in [128, 256, 512, 2048] {
                        println!(
                            "{t},{tc},{f},{m},{n},{:.17e}",
                            absorption_ratio_n(t, tc, f, m, n)?
                        );
                    }
                }
            }
        }
    }
    Ok(())
}
