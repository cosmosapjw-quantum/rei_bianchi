use rei_microphysics::{
    axbi_driver::{packet_chemistry_stage, packet_chemistry_stage_budgeted, PacketStageInput},
    coupled_primary::PrimaryPacket,
    igm_state::{w_erg_per_h_to_ev, IgmGasState},
    HHeModel,
};
fn fixture() -> (PacketStageInput, IgmGasState, Vec<PrimaryPacket>) {
    let input=PacketStageInput{n_h_cm3:1e-4,n_he_cm3:8e-6,tcmb_k:27.255};
    let gas=IgmGasState::from_temperature([0.3,0.28,0.01],input.n_h_cm3,input.n_he_cm3,3000.).unwrap();
    let packets=vec![PrimaryPacket{energy_ev:20.,per_h:0.005},PrimaryPacket{energy_ev:30.,per_h:0.003},PrimaryPacket{energy_ev:80.,per_h:0.0002}];
    (input,gas,packets)
}
fn defect(i:PacketStageInput,g:IgmGasState,p:&[PrimaryPacket],s:&rei_microphysics::axbi_driver::PacketStageResult)->f64{
    let c=HHeModel::controlled_fixture().threshold_ev;
    let f=i.n_he_cm3/i.n_h_cm3;let d:Vec<_>=s.gas.fractions.iter().zip(g.fractions).map(|(a,b)|a-b).collect();
    let du=p.iter().zip(&s.stocks).map(|(p,n)|p.energy_ev*(p.per_h-n)).sum::<f64>();
    w_erg_per_h_to_ev(s.gas.w_erg_per_h).unwrap()-w_erg_per_h_to_ev(g.w_erg_per_h).unwrap()
       +c[0]*d[0]+f*(c[1]*d[1]+(c[1]+c[2])*d[2])-du+s.ledgers.escaped_u-s.ledgers.cmb_input
}
#[test]
fn physical_energy_budget_and_original_residual() {
    let (i,g,p)=fixture();let mut found=false;
    for dt in [1e4,1e5,1e6,1e7,1e8,1e9,1e10,1e11,1e12,1e13] {
        let mut count=0;
        let old=packet_chemistry_stage(i,g,&p,dt,&mut count,10000).unwrap();
        let budget=3e-14;
        let mut n=0;
        let new=packet_chemistry_stage_budgeted(i,g,&p,dt,&mut n,10000,budget).unwrap();
        assert!(defect(i,g,&p,&new).abs()<=budget);
        assert!(new.max_residual<=1e-11);
        assert!(p.iter().zip(&new.stocks).all(|(a,b)|*b>=0.&&*b<=a.per_h));
        if defect(i,g,&p,&old).abs()>budget {found=true;assert!(n>=count);}
    }
    assert!(found,"fixture must distinguish legacy and budgeted acceptance");
}
#[test]
fn reject_invalid_and_unattainably_small_budget() {
    let (i,g,p)=fixture();let mut n=0;
    for b in [0.,-1.,f64::NAN,f64::INFINITY] {
        assert!(packet_chemistry_stage_budgeted(i,g,&p,1e9,&mut n,10000,b).is_err());
    }
    assert_eq!(n,0);
    assert!(packet_chemistry_stage_budgeted(i,g,&p,1e9,&mut n,10000,1e-30).is_err());
}
