//! Actual original MD14/BB50k photon births and Verner/D photo absorption,
//! affine time-dependent prescribed H_i; gas density strictly comoving-frozen.
use rei_iso_couple_reference::{
    HHeModel,
    affine_threshold_events::{
        AffineHubbleBackground, AffinePhotoControls, AffineSourceControls, FrozenPhotoDensities,
        source_on_affine_photo_pilot,
    },
    axbi_sources::{AxbiSource, SOURCE_ID},
    deuterium_atomic::DAtomicProvider,
    positive_spectral::SpectralMode,
};
fn main() {
    let tmax = 5e8;
    let source = AxbiSource::new(1900. / (21_f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    assert_eq!(SOURCE_ID, "MD14_Z002_FESC_BB50K_13P6_100_V1");
    let bg = AffineHubbleBackground::new(0., [1. / 21.; 3], [1e-10; 3], [-1e-19; 3], [0., tmax])
        .unwrap();
    let ch = HHeModel::controlled_fixture().threshold_ev[0];
    let d = DAtomicProvider::new(ch, 13.602134599702, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let gas = FrozenPhotoDensities {
        proper_reference_time_s: 0.,
        neutral_m3: [8000., 2000., 500., 1600.],
    };
    println!(
        "birth_gl,opacity_slices,spectral,event_split,cohorts,event_cuts,newborn_com3,survivors_com3,HI_com3,HeI_com3,HeII_com3,DI_com3,absorbed_energy_j_com3,geometry_work_j_com3,relative_number_residual,relative_energy_residual"
    );
    let jobs = [
        (2, 2, SpectralMode::OriginalCellMean, false),
        (2, 2, SpectralMode::OriginalCellMean, true),
        (2, 2, SpectralMode::SplitPositiveGauss3, false),
        (2, 2, SpectralMode::SplitPositiveGauss3, true),
        (2, 8, SpectralMode::SplitPositiveGauss3, true),
        (4, 8, SpectralMode::SplitPositiveGauss3, true),
    ];
    for (gl, m, spec, ev) in jobs {
        let controls = AffineSourceControls {
            gauss_birth: gl,
            photon: AffinePhotoControls {
                substeps: m,
                split_events: ev,
            },
            spectrum: spec,
        };
        let o = source_on_affine_photo_pilot(&source, &bg, d, gas, 0., tmax, controls).unwrap();
        let nrel = o.number_residual() / o.newborn_count_com3;
        let erel = o.event_energy_residual() / o.photo_energy_j_com3;
        println!(
            "{gl},{m},{spec:?},{ev},{},{},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e}",
            o.true_cohorts,
            o.event_cuts,
            o.newborn_count_com3,
            o.survivor_count_com3,
            o.absorber_events_com3[0],
            o.absorber_events_com3[1],
            o.absorber_events_com3[2],
            o.absorber_events_com3[3],
            o.photo_energy_j_com3,
            o.radiation_geometry_work_j_com3,
            nrel,
            erel
        );
    }
}
