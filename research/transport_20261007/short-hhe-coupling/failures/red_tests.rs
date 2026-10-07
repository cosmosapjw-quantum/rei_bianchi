use short_hhe_control::photo_delta;
#[test]
fn shared_species_transfer() {
 let a=[0.003,0.002,0.0005]; let b=[1e-13,1e-13,5e-14];
 let got=photo_delta(a,b,0.08);
 assert!((got[0]-0.003).abs()<1e-16,"H owner missing");
 assert!((got[1]-0.01875).abs()<1e-16,"HeI-HeII owner/fHe missing");
 assert!((got[2]-0.00625).abs()<1e-16,"HeIII owner/fHe missing");
 let chi=rei_microphysics::HHeModel::controlled_fixture();
 let heat:f64=(0..3).map(|i|b[i]-chi.ev_erg*chi.threshold_ev[i]*a[i]).sum();
 assert!((got[3]-heat).abs()<1e-27,"shared absorbed energy minus binding missing");
}
