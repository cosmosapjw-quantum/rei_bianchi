use rei_microphysics::{
    ft03_coefficients, AxisymmetricPoint, CharacteristicRay, ConstantAxisymmetricBackground,
    ConstantHubbleBackground, GeometryBackground, GeometrySnapshot,
};
fn close(a: f64, b: f64) {
    assert!(a.is_finite() && b.is_finite());
    assert!(
        (a - b).abs() <= 3e-13 * b.abs().max(1e-30),
        "{a:e} != {b:e}"
    );
}
#[test]
fn independent_exact_characteristic_points() {
    let g0 = GeometrySnapshot::new([1.0, 1.0, 1.0], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([2.0, 2.0, 2.0], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(40.0, [1.0, 0.0, 0.0], 0.37).unwrap();
    let image = ray.pullback(&g0, &g1).unwrap();
    close(image.energy_ev, 20.0);
    for (x, y) in image.direction.into_iter().zip([1.0, 0.0, 0.0]) {
        close(x, y);
    }
    assert_eq!(image.occupation, ray.occupation);
    close(ray.solid_angle_jacobian(&g0, &g1).unwrap(), 1.0);
    close(image.direction.into_iter().map(|v| v * v).sum::<f64>(), 1.0);
    let g0 = GeometrySnapshot::new([1.0, 1.0, 1.0], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([2.0, 3.0, 4.0], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(80.0, [0.0, 0.0, 1.0], 0.37).unwrap();
    let image = ray.pullback(&g0, &g1).unwrap();
    close(image.energy_ev, 20.0);
    for (x, y) in image.direction.into_iter().zip([0.0, 0.0, 1.0]) {
        close(x, y);
    }
    assert_eq!(image.occupation, ray.occupation);
    close(
        ray.solid_angle_jacobian(&g0, &g1).unwrap(),
        2.6666666666666665,
    );
    close(image.direction.into_iter().map(|v| v * v).sum::<f64>(), 1.0);
    let g0 = GeometrySnapshot::new([1.0, 1.0, 1.0], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([2.0, 3.0, 4.0], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(
        45.0,
        [0.6666666666666666, 0.3333333333333333, 0.6666666666666666],
        0.37,
    )
    .unwrap();
    let image = ray.pullback(&g0, &g1).unwrap();
    close(image.energy_ev, 17.5);
    for (x, y) in image.direction.into_iter().zip([
        0.8571428571428571,
        0.2857142857142857,
        0.42857142857142855,
    ]) {
        close(x, y);
    }
    assert_eq!(image.occupation, ray.occupation);
    close(
        ray.solid_angle_jacobian(&g0, &g1).unwrap(),
        0.7084548104956269,
    );
    close(image.direction.into_iter().map(|v| v * v).sum::<f64>(), 1.0);
    let g0 = GeometrySnapshot::new([1.0, 1.2, 0.8], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([1.03, 1.19, 0.82], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(
        70.0,
        [0.6666666666666666, 0.3333333333333333, 0.6666666666666666],
        0.37,
    )
    .unwrap();
    let image = ray.pullback(&g0, &g1).unwrap();
    close(image.energy_ev, 68.40495510506778);
    for (x, y) in image.direction.into_iter().zip([
        0.6623415408445928,
        0.34397232961509105,
        0.6655724751901763,
    ]) {
        close(x, y);
    }
    assert_eq!(image.occupation, ray.occupation);
    close(
        ray.solid_angle_jacobian(&g0, &g1).unwrap(),
        1.023539548480569,
    );
    close(image.direction.into_iter().map(|v| v * v).sum::<f64>(), 1.0);
    let g0 = GeometrySnapshot::new([1.0, 1.0, 1.0], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([1000000000000000.0, 1e-15, 100000.0], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(
        30.0,
        [0.6666666666666666, 0.3333333333333333, 0.6666666666666666],
        0.37,
    )
    .unwrap();
    let image = ray.pullback(&g0, &g1).unwrap();
    close(image.energy_ev, 1e+16);
    for (x, y) in image.direction.into_iter().zip([2e-30, 1.0, 2e-20]) {
        close(x, y);
    }
    assert_eq!(image.occupation, ray.occupation);
    close(ray.solid_angle_jacobian(&g0, &g1).unwrap(), 2.7e-49);
    close(image.direction.into_iter().map(|v| v * v).sum::<f64>(), 1.0);
}
#[test]
fn differential_r1_and_background() {
    let background = ConstantHubbleBackground::new([1.0; 3], [0.1, 0.2, 0.3]).unwrap();
    let g = background.snapshot(1.0).unwrap();
    for (a, b) in g
        .scale_factors
        .into_iter()
        .zip([0.1_f64.exp(), 0.2_f64.exp(), 0.3_f64.exp()])
    {
        close(a, b);
    }
    close(g.volume_factor().unwrap(), 0.6_f64.exp());
    let ray = CharacteristicRay::new(30.0, [2.0 / 3.0, 1.0 / 3.0, 2.0 / 3.0], 1.0).unwrap();
    let rhs = ray.derivative(&g).unwrap();
    let hd = (0.1 * 4.0 + 0.2 + 0.3 * 4.0) / 9.0;
    close(rhs.energy_dot_ev_s, -30.0 * hd);
    for ((d, e), h) in rhs
        .direction_dot_per_s
        .into_iter()
        .zip(ray.direction)
        .zip([0.1, 0.2, 0.3])
    {
        let expected = e * (hd - h);
        // The ideal rational middle component is zero. Binary64 input
        // representation and projection/subtraction have a finite absolute
        // rounding bound; comparing to zero with a relative 1e-30 floor is
        // invalid and must not make the evaluator clip resolved shear.
        if expected == 0.0 {
            assert!(d.abs() <= 8.0 * f64::EPSILON * e.abs() * h.abs());
        } else {
            close(d, expected);
        }
    }
    assert!(
        ray.direction
            .into_iter()
            .zip(rhs.direction_dot_per_s)
            .map(|(a, b)| a * b)
            .sum::<f64>()
            .abs()
            < 1e-15
    );
}
#[test]
fn identity_inverse_and_temperature_coordinates() {
    let a = GeometrySnapshot::new([1.0; 3], [0.0; 3]).unwrap();
    let b = GeometrySnapshot::new([1.5, 0.8, 2.0], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(40.0, [2.0 / 3.0, 1.0 / 3.0, 2.0 / 3.0], 0.2).unwrap();
    let identity = ray.pullback(&a, &a).unwrap();
    close(identity.energy_ev, ray.energy_ev);
    let back = ray.pullback(&a, &b).unwrap().pullback(&b, &a).unwrap();
    close(back.energy_ev, ray.energy_ev);
    for (x, y) in back.direction.into_iter().zip(ray.direction) {
        close(x, y);
    }
    let before = ft03_coefficients(50000.0).unwrap();
    let _ = ray.pullback(&a, &b).unwrap();
    let after = ft03_coefficients(50000.0).unwrap();
    assert_eq!(before.alpha_rr_cm3_s, after.alpha_rr_cm3_s);
}
#[test]
fn domain_errors() {
    for a in [
        [0.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [f64::NAN, 1.0, 1.0],
        [1e-200; 3],
        [1e200; 3],
    ] {
        assert!(GeometrySnapshot::new(a, [0.0; 3]).is_err());
    }
    assert!(CharacteristicRay::new(0.0, [1.0, 0.0, 0.0], 1.0).is_err());
    assert!(CharacteristicRay::new(20.0, [1.0; 3], 1.0).is_err());
    assert!(CharacteristicRay::new(20.0, [1.0, 0.0, 0.0], -1.0).is_err());
    assert!(CharacteristicRay::new(f64::INFINITY, [1.0, 0.0, 0.0], 1.0).is_err());
    let b = ConstantHubbleBackground::new([1.0; 3], [1.0; 3]).unwrap();
    assert!(b.snapshot(1000.0).is_err());
    assert!(b.snapshot(f64::NAN).is_err());
    let g0 = GeometrySnapshot::new([1.0; 3], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([1e100; 3], [0.0; 3]).unwrap();
    let ray = CharacteristicRay::new(1e-300, [1.0, 0.0, 0.0], 1.0).unwrap();
    assert!(ray.pullback(&g0, &g1).is_err());
}

#[test]
fn axisymmetric_proper_time_background_and_exact_rays() {
    let point = AxisymmetricPoint::new(2.0, 0.1, 0.02, 0.03).unwrap();
    let snapshot = point.snapshot().unwrap();
    close(snapshot.volume_factor().unwrap(), 8.0);
    close(snapshot.hubble_per_s[0], -0.01);
    close(snapshot.hubble_per_s[2], 0.08);

    let background = ConstantAxisymmetricBackground::new(1.0, point, [0.0, 2.0]).unwrap();
    let later = background.snapshot(2.0).unwrap();
    close(later.volume_factor().unwrap(), 8.0 * 0.06_f64.exp());
    let axis = CharacteristicRay::new(40.0, [0.0, 0.0, 1.0], 0.7).unwrap();
    let equator = CharacteristicRay::new(40.0, [1.0, 0.0, 0.0], 0.7).unwrap();
    close(
        axis.pullback(&snapshot, &later).unwrap().energy_ev,
        40.0 * (-0.08_f64).exp(),
    );
    close(
        equator.pullback(&snapshot, &later).unwrap().energy_ev,
        40.0 * 0.01_f64.exp(),
    );
    for ray in [axis, equator] {
        let image = ray.pullback(&snapshot, &later).unwrap();
        let jacobian = ray.solid_angle_jacobian(&snapshot, &later).unwrap();
        close(
            (image.energy_ev / ray.energy_ev).powi(3) * jacobian,
            snapshot.volume_factor().unwrap() / later.volume_factor().unwrap(),
        );
        let restored = image.pullback(&later, &snapshot).unwrap();
        close(restored.energy_ev, ray.energy_ev);
        assert_eq!(restored.occupation, ray.occupation);
    }
}

#[test]
fn axisymmetric_flrw_limit_and_domain_errors() {
    let point = AxisymmetricPoint::new(1.5, 0.0, 0.02, 0.0).unwrap();
    let background = ConstantAxisymmetricBackground::new(0.0, point, [-1.0, 1.0]).unwrap();
    let g = background.snapshot(0.5).unwrap();
    for scale in g.scale_factors {
        close(scale, 1.5 * 0.01_f64.exp());
    }
    assert!(AxisymmetricPoint::new(0.0, 0.0, 0.0, 0.0).is_err());
    assert!(AxisymmetricPoint::new(1.0, f64::NAN, 0.0, 0.0).is_err());
    assert!(ConstantAxisymmetricBackground::new(0.0, point, [1.0, -1.0]).is_err());
    assert!(background.snapshot(2.0).is_err());
    let mut mutated = background;
    mutated.time_domain_s = [f64::NAN, f64::NAN];
    assert!(mutated.snapshot(0.0).is_err());
    let overflow = AxisymmetricPoint::new(1.0, -1000.0, 0.0, 0.0);
    assert!(overflow.is_err());
}
