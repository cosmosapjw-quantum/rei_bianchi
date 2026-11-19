use rei_microphysics::axbi_driver::{Driver,DriverConfig};
use rei_microphysics::axbi_background::{AxbiBackground,BackgroundFamily,Cosmology};

fn bits(p: rei_microphysics::axbi_background::BackgroundPoint)->[u64;7] {
    [p.a,p.b,p.time_s,p.h_flrw_per_s,p.h_per_s,p.s_per_s,p.sigma].map(f64::to_bits)
}
fn streams(d:&Driver,s:&rei_microphysics::axbi_driver::DriverState)->Vec<Vec<u8>> {
    let(mut h,mut a,mut p,mut l,mut f)=(vec![],vec![],vec![],vec![],vec![]);
    d.output_row(s,"AX11",&mut h,&mut a,&mut p,&mut l,&mut f).unwrap();
    vec![h,a,p,l,f]
}
#[test]
fn exact_background_bits_and_model_separation() {
    fn send_sync<T:Send+Sync>() {} send_sync::<AxbiBackground>();
    let cosmology=Cosmology{h0_per_s:2.1842852410855023e-18,omega_m:0.315,omega_r:9.2e-5,omega_lambda:1.0-0.315-9.2e-5};
    for q in [0.0,0.01,-0.01] {
        for family in [BackgroundFamily::PhysicalDensityFixed,BackgroundFamily::SameHDiagnostic] {
            for panels in [8,4096] {
                std::env::set_var("AX11_CACHE","0");
                let raw=AxbiBackground::new(cosmology,1.0/21.0,0.2,0.0,q,family,panels).unwrap();
                std::env::set_var("AX11_CACHE","1");
                let cached=AxbiBackground::new(cosmology,1.0/21.0,0.2,0.0,q,family,panels).unwrap();
                for a in [1.0/21.0,0.08873100115616298,0.08873100115616298,1.0/21.0,0.2] {
                    assert_eq!(bits(raw.point_at_scale(a).unwrap()),bits(cached.point_at_scale(a).unwrap()));
                }
                for bad in [f64::NAN,0.0,0.3] { assert!(cached.point_at_scale(bad).is_err()); }
            }
        }
    }
}
#[test]
fn lazy_all_streams_and_exact_terminal_reserve() {
    std::env::set_var("AX11_CACHE","1");
    for q in [0.0,0.01,-0.01] {
        let mut c=DriverConfig::baseline(); c.q_ref=q;
        std::env::set_var("AX11_LAZY","0"); let (raw,mut s)=Driver::new(c.clone()).unwrap();
        std::env::set_var("AX11_LAZY","1"); let (lazy,_)=Driver::new(c).unwrap();
        for _ in 0..4 {
            let original=streams(&raw,&s); let candidate=streams(&lazy,&s);
            assert_eq!(original,candidate);
            assert_eq!(original[2].len(),lazy.ax11_reserved_spectrum_bytes(&s,"AX11").unwrap());
            loop { if raw.adaptive_step(&mut s).unwrap() { break; } }
        }
    }
}
#[test]
fn component_l1_keeps_cancellation_and_fold_contract() {
    let (d,mut half)=Driver::new(DriverConfig::baseline()).unwrap();
    half.photons[0]=1.0; half.photons[1]=1.0;
    let mut full=half.clone(); full.photons[0]+=0.125; full.photons[1]-=0.125;
    let metric=d.error_metric(&full,&half).unwrap();
    let p=d.last_error_components().unwrap();
    assert_eq!(p[4],0.125); // abs(sum(delta)) would incorrectly be zero.
    assert_eq!(metric,p.into_iter().fold(0.0_f64,f64::max));
    let mut s=half; d.adaptive_step(&mut s).ok();
}
