use rei_microphysics::{
    AxisymContractError, AxisymRunContract, AxisymmetricPoint, AxisymmetryStatus, Clock,
    ClosureChoice, ConstantAxisymmetricBackground, ExecutionMode, Frame, ICProviderRecord,
    MuReflectionStatus, ProviderDomain, ProviderErrorStatus, ProviderRecord, RadiationUnits,
    SourceProviderRecord, SymmetryRecord,
};

fn background(mean_hubble_per_s: f64, shear_per_s: f64) -> ConstantAxisymmetricBackground {
    ConstantAxisymmetricBackground::new(
        0.0,
        AxisymmetricPoint::new(1.0, 0.0, mean_hubble_per_s, shear_per_s).unwrap(),
        [-2.0, 2.0],
    )
    .unwrap()
}

fn provider() -> ProviderRecord {
    ProviderRecord {
        identity: "fixture-provider".into(),
        version: Some("v1".into()),
        domain: Some(ProviderDomain {
            proper_time_s: [-2.0, 2.0],
            temperature_k: None,
            photon_energy_j: None,
        }),
        interpolation: Some("linear".into()),
        error_status: ProviderErrorStatus::Quantified,
    }
}

fn symmetry() -> SymmetryRecord {
    SymmetryRecord {
        axisymmetry: AxisymmetryStatus::CommonZAxis,
        mu_reflection: MuReflectionStatus::Even,
    }
}

#[test]
fn pending_contract_is_geometry_only_and_preserves_absence() {
    let contract = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    assert!(contract.physical_ic.is_none());
    assert!(contract.source.is_none());
    assert!(contract.atomic_provider.is_none());
    assert!(contract.closure.is_none());
    assert!(matches!(
        contract.validate_for(ExecutionMode::GeometryOnly),
        Ok(rei_microphysics::GeometryOnlyAdmission)
    ));
}

#[test]
fn physical_request_reports_first_missing_typed_prerequisite_without_mutation() {
    let mut contract = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    assert!(matches!(
        contract.validate_for(ExecutionMode::PhysicalHistory),
        Err(AxisymContractError::MissingPhysicalInitialCondition)
    ));
    contract.physical_ic = Some(ICProviderRecord {
        provider: provider(),
        symmetry: symmetry(),
    });
    assert!(matches!(
        contract.validate_for(ExecutionMode::PhysicalHistory),
        Err(AxisymContractError::MissingSource)
    ));
    contract.source = Some(SourceProviderRecord {
        provider: provider(),
        symmetry: symmetry(),
    });
    assert!(matches!(
        contract.validate_for(ExecutionMode::PhysicalHistory),
        Err(AxisymContractError::MissingAtomicProvider)
    ));
    contract.atomic_provider = Some(provider());
    assert!(matches!(
        contract.validate_for(ExecutionMode::PhysicalHistory),
        Err(AxisymContractError::MissingClosure)
    ));
    assert!(contract.closure.is_none());
}

#[test]
fn populated_metadata_does_not_admit_physical_history() {
    let mut contract = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    contract.physical_ic = Some(ICProviderRecord {
        provider: provider(),
        symmetry: symmetry(),
    });
    contract.source = Some(SourceProviderRecord {
        provider: provider(),
        symmetry: symmetry(),
    });
    contract.atomic_provider = Some(provider());
    contract.closure = Some(ClosureChoice::FullCoupledOts {
        provider: provider(),
    });
    assert!(matches!(
        contract.validate_for(ExecutionMode::PhysicalHistory),
        Err(AxisymContractError::PhysicalExecutionNotImplemented)
    ));
}

#[test]
fn symmetry_and_unknown_provider_state_are_independent() {
    let record = SymmetryRecord {
        axisymmetry: AxisymmetryStatus::CommonZAxis,
        mu_reflection: MuReflectionStatus::Unknown,
    };
    assert_ne!(record.mu_reflection, MuReflectionStatus::Even);
    let unknown = ProviderRecord {
        identity: "unknown".into(),
        version: None,
        domain: None,
        interpolation: None,
        error_status: ProviderErrorStatus::Unknown,
    };
    assert_eq!(unknown.domain, None);
    assert_eq!(unknown.error_status, ProviderErrorStatus::Unknown);
}

#[test]
fn invalid_geometry_and_conventions_fail_structurally() {
    let mut invalid_domain = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    invalid_domain.background.time_domain_s = [f64::NAN, 1.0];
    assert!(matches!(
        invalid_domain.validate_for(ExecutionMode::GeometryOnly),
        Err(AxisymContractError::InvalidGeometry(_))
    ));
    let mut nonfinite = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    nonfinite.background.reference_point.shear_per_s = f64::NAN;
    assert!(matches!(
        nonfinite.validate_for(ExecutionMode::GeometryOnly),
        Err(AxisymContractError::InvalidGeometry(_))
    ));
    let mut clock = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    clock.clock = Clock::Other;
    assert!(matches!(
        clock.validate_for(ExecutionMode::GeometryOnly),
        Err(AxisymContractError::UnsupportedClock)
    ));
    let mut frame = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    frame.frame = Frame::Other;
    assert!(matches!(
        frame.validate_for(ExecutionMode::GeometryOnly),
        Err(AxisymContractError::UnsupportedFrame)
    ));
    let mut units = AxisymRunContract::pending_geometry(background(0.0, 0.0));
    units.radiation_units = RadiationUnits::Other;
    assert!(matches!(
        units.validate_for(ExecutionMode::GeometryOnly),
        Err(AxisymContractError::UnsupportedRadiationUnits)
    ));
}

#[test]
fn zero_mean_hubble_and_contracting_direction_are_valid() {
    let contract = AxisymRunContract::pending_geometry(background(0.0, 0.1));
    assert!(matches!(
        contract.validate_for(ExecutionMode::GeometryOnly),
        Ok(rei_microphysics::GeometryOnlyAdmission)
    ));
    let snapshot =
        rei_microphysics::GeometryBackground::snapshot(&contract.background, 0.0).unwrap();
    assert!(snapshot.hubble_per_s[0] < 0.0);
}
