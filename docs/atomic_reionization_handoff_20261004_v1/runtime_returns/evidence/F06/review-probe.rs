use rei_microphysics::{CharacteristicRay,GeometrySnapshot,PhotonPacket,PhotonGrid,RadiationState};
fn g(a:[f64;3])->GeometrySnapshot { GeometrySnapshot::new(a,[0.;3]).unwrap() }
fn packet(e:f64,n:f64)->PhotonPacket { PhotonPacket::new(CharacteristicRay::new(e,[1.,0.,0.],0.7).unwrap(),n).unwrap() }
fn main(){
    let grid=PhotonGrid::new(vec![1.,15.,30.],vec![-1.,1.],1).unwrap();
    let s=RadiationState::new(g([1.;3]),vec![packet(1e-200,1e-200)]).unwrap();
    let b=s.remap(&grid).unwrap();
    println!("POSITIVE_ENERGY_UNDERFLOW state=Ok count={:e} energy={:?} below_count={:e} below_energy={:e}",s.comoving_photon_count().unwrap(),s.comoving_energy_ev_cm3(),b.below_count_cm3,b.below_energy_ev_cm3);
    let s=RadiationState::new(g([1e100,1e100,1.]),vec![packet(1e200,1e-200)]).unwrap();
    println!("POSITIVE_DENSITY_UNDERFLOW count={:e} volume={:e} density={:?}",s.comoving_photon_count().unwrap(),s.geometry.volume_factor().unwrap(),s.proper_photon_density_cm3());
    let g0=g([1e-200,1.,1e100]);let g1=g([1e100,1e100,1.]);
    let ray=CharacteristicRay::new(1e200,[1e-100,1.,0.],0.7).unwrap();
    let im=ray.pullback(&g0,&g1).unwrap();let back=im.pullback(&g1,&g0).unwrap();
    println!("COMPONENT_UNDERFLOW mapped={im:?} inverse={back:?} q0_x={:e} q1_x={:e} expected_e1_x=1e-300",g0.scale_factors[0]*ray.energy_ev*ray.direction[0],g1.scale_factors[0]*im.energy_ev*im.direction[0]);
    let tiny=2f64.powi(-54);let mut packets=vec![packet(10.,1.)];
    for _ in 0..4096 { packets.push(packet(20.,tiny)); }
    let s=RadiationState::new(g([1.;3]),packets).unwrap();let bins=s.remap(&grid).unwrap();
    let expected_count=1.+4096.*tiny;let expected_energy=10.+4096.*tiny*20.;
    println!("ACCUMULATION raw_count={:.17e} remap_count={:.17e} exact_count={expected_count:.17e} raw_energy={:.17e} remap_energy={:.17e} exact_energy={expected_energy:.17e}",s.comoving_photon_count().unwrap(),bins.total_count().unwrap(),s.comoving_energy_ev_cm3().unwrap(),bins.total_energy_ev_cm3().unwrap());
    let ray=CharacteristicRay{energy_ev:1.,direction:[1.+5e-13,0.,0.],occupation:0.7};
    let packet=PhotonPacket::new(ray,1.).unwrap();
    println!("MUTABLE_DIRECTION preserved={:?} identity={:?} derivative={:?}",packet.ray,ray.pullback(&g([1.;3]),&g([1.;3])),ray.derivative(&GeometrySnapshot::new([1.;3],[1.;3]).unwrap()));
    let delta=4.*f64::EPSILON;let ray=CharacteristicRay::new(1.,[0.6,0.8,0.],0.7).unwrap();
    let bg=GeometrySnapshot::new([1.;3],[1.,1.+delta,1.]).unwrap();let rhs=ray.derivative(&bg).unwrap();
    let expected=[0.6*0.64*delta,-0.8*0.36*delta,0.];
    println!("DERIVATIVE_CLIPPING direction={:?} H={:?} actual={rhs:?} rational_expected_direction_dot={expected:?}",ray.direction,bg.hubble_per_s);
    let ray=CharacteristicRay::new(30.,[2./3.,1./3.,2./3.],1.).unwrap();
    println!("FROZEN_RATIONAL_DERIVATIVE direction={:?} rhs={:?}",ray.direction,ray.derivative(&GeometrySnapshot::new([1.;3],[0.1,0.2,0.3]).unwrap()));
    let s=RadiationState::new(g([1.;3]),vec![packet_fn(1e-300,1.)]).unwrap();let before=s.clone();
    let rejected=s.transport(g([1e100;3])).is_err();println!("REJECTION_IMMUTABILITY rejected={rejected} unchanged={}",s==before);
}
fn packet_fn(e:f64,n:f64)->PhotonPacket {packet(e,n)}
