#[cfg(test)]
mod tests {
    use super::*;
    fn close(a: f64, b: f64, t: f64) {
        assert!(
            (a - b).abs() <= t * 1f64.max(a.abs()).max(b.abs()),
            "{a:.17e} != {b:.17e}"
        );
    }
    #[test]
    fn moments_are_exact_integrals() {
        let c = Cell {
            l: 2.,
            r: 5.,
            a: 3.,
            b: -0.7,
        };
        let (n, u) = moments(c);
        close(n, 9., 1e-14);
        close(u, 30.45, 1e-14);
    }
    #[test]
    fn dg_weak_moments_match_fluxes() {
        let c = Cell {
            l: 2.,
            r: 5.,
            a: 3.,
            b: -0.7,
        };
        let (da, db) = dg_rhs(c, -4., -7.);
        let (nd, ud) = moments(Cell { a: da, b: db, ..c });
        close(nd, 3., 1e-14);
        close(ud, -5. * (-7.) + 2. * (-4.) - 30.45, 1e-14);
    }
    #[test]
    fn empty_inflow_exposes_positivity_energy_conflict() {
        let c = Cell {
            l: 1.,
            r: 2.,
            a: 0.,
            b: 0.,
        };
        let (da, db) = dg_rhs(c, 0., -2.);
        let mut y = Cell {
            a: 1e-8 * da,
            b: 1e-8 * db,
            ..c
        };
        let (n, u) = moments(y);
        close(u / n, 2., 1e-14);
        assert!(y.a - y.b < 0.);
        let du = limit(&mut y).unwrap();
        let (nn, uu) = moments(y);
        close(nn, n, 1e-14);
        close(uu / n, 5. / 3., 1e-14);
        close(du, uu - u, 1e-14);
        assert!(y.a - y.b >= 0.);
        assert!(du < 0.);
    }
    #[test]
    fn limiter_rejects_negative_mean() {
        let mut c = Cell {
            l: 1.,
            r: 2.,
            a: -1e-30,
            b: 0.,
        };
        assert!(limit(&mut c).is_err());
    }
    #[test]
    fn partial_panel_ledgers_and_edges() {
        for s in [0., 0.2, 0.4, 0.6, 0.9, 1.2] {
            let (n, u, no, eo, w) = panel(0.4, 0.9, 2., s);
            close(n + no, 1., 1e-14);
            close(u + eo + w, 13.6 * 2. * (0.9f64.exp() - 0.4f64.exp()), 1e-14);
            close(eo, 13.6 * no, 1e-14);
            assert!(n >= 0. && no >= 0. && w >= 0.);
        }
    }
    #[test]
    fn fv_interior_energy_defect_is_exposed() {
        let mut cs = vec![];
        for i in 0..4 {
            cs.push(Cell {
                l: 2f64.powi(i),
                r: 2f64.powi(i + 1),
                a: if i == 2 { 1. } else { 0. },
                b: 0.,
            });
        }
        let f = fluxes(&cs);
        let mut nd = 0.;
        let mut ud = 0.;
        for i in 0..4 {
            let da = -(f[i + 1] - f[i]) / (cs[i].r - cs[i].l);
            let (n, u) = moments(Cell {
                a: da,
                b: 0.,
                ..cs[i]
            });
            nd += n;
            ud += u;
        }
        let u = moments(cs[2]).1;
        close(nd, 0., 1e-14);
        close(ud, -u / 2., 1e-14);
        assert!((ud + u).abs() > 1.);
    }
    #[test]
    fn rk_ledgers_and_limiter_accounting() {
        for limited in [false, true] {
            let cs = vec![
                Cell {
                    l: 1.,
                    r: 2.,
                    a: 0.,
                    b: 0.,
                },
                Cell {
                    l: 2.,
                    r: 3.,
                    a: 1.,
                    b: 0.,
                },
            ];
            let u0 = cs.iter().map(|c| moments(*c).1).sum::<f64>();
            let n0 = 1.;
            let mut st = State::new(cs);
            for _ in 0..5 {
                step(&mut st, 0.01, true, limited).unwrap();
            }
            let (n, u) = totals(&st.cells);
            close(n + st.no, n0, 1e-13);
            close(u + st.eo + st.w - u0, st.du, 1e-13);
            if limited {
                assert!(st.du.abs() > 1e-10);
            } else {
                close(st.du, 0., 1e-14);
            }
        }
    }
    #[test]
    fn signed_slopes_match_independent_simpson_moments_and_face_identity() {
        for a in [0.0, 0.3, 2.0] {
            for b in [-3.0, -0.1, 0.0, 0.1, 3.0] {
                let c = Cell {
                    l: 1.7,
                    r: 4.1,
                    a,
                    b,
                };
                let d = c.r - c.l;
                let mid = (c.l + c.r) / 2.;
                let sn = d / 6. * ((a - b) + 4. * a + (a + b));
                let su = d / 6. * (c.l * (a - b) + 4. * mid * a + c.r * (a + b));
                let (n, u) = moments(c);
                close(n, sn, 1e-14);
                close(u, su, 1e-14);
                for (fl, fr) in [(-2.3, -0.2), (0.1, -3.2), (0., 0.)] {
                    let (da, db) = dg_rhs(c, fl, fr);
                    let (nd, ud) = moments(Cell { a: da, b: db, ..c });
                    close(nd, fl - fr, 1e-14);
                    close(ud, c.l * fl - c.r * fr - su, 1e-14);
                }
            }
        }
    }
    #[test]
    fn actual_stock_node_has_exact_threshold_and_independent_work() {
        let x = 0.4;
        let mass = 0.73;
        for s in [0.0, 0.2, 0.4 - 1e-12, 0.4, 0.4 + 1e-12, 1.0] {
            let (n, u, no, eo, w) = node(x, mass, s);
            close(n + no, mass, 1e-14);
            close(u + eo + w, mass * EC * x.exp(), 1e-14);
            if s >= x {
                close(n, 0., 0.);
                close(no, mass, 0.);
                close(eo, EC * mass, 1e-14);
            } else {
                close(n, mass, 0.);
                close(no, 0., 0.);
            }
        }
        close(node(x, mass, 0.).4, 0., 0.);
    }
}
