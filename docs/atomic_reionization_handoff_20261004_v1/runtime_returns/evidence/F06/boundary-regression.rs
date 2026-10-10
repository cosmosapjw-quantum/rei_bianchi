use rei_microphysics::{CharacteristicRay,GeometrySnapshot,PhotonPacket,PhotonGrid,RadiationState};
fn g(a:[f64;3])->GeometrySnapshot { GeometrySnapshot::new(a,[0.;3]).unwrap() }
fn packet(e:f64,n:f64)->PhotonPacket { PhotonPacket::new(CharacteristicRay::new(e,[1.,0.,0.],0.7).unwrap(),n).unwrap() }
fn main(){
 let mut checks=0;
 macro_rules! check {($test:expr)=>{{assert!($test,"{}",stringify!($test));checks+=1;}}}
 macro_rules! close {($a:expr,$b:expr,$tol:expr)=>{{let(a,b): (f64,f64)=($a,$b);check!(a.is_finite() && (a-b).abs() <= $tol*b.abs());}}}
 let grid=PhotonGrid::new(vec![1.,15.,30.],vec![-1.,1.],1).unwrap();
 check!(RadiationState::new(g([1.;3]),vec![packet(1e-200,1e-200)]).is_err());
 let zero=RadiationState::new(g([1.;3]),vec![packet(1e-200,0.)]).unwrap();
 check!(zero.comoving_energy_ev_cm3().unwrap()==0.);
 let s=RadiationState::new(g([1e100,1e100,1.]),vec![packet(1e200,1e-200)]).unwrap();
 check!(s.proper_photon_density_cm3().is_err());
 let g0=g([1e-200,1.,1e100]);let g1=g([1e100,1e100,1.]);
 let ray=CharacteristicRay::new(1e200,[1e-100,1.,0.],0.7).unwrap();
 let image=ray.pullback(&g0,&g1).unwrap();let back=image.pullback(&g1,&g0).unwrap();
 close!(image.direction[0],1e-300,3e-13);
 close!(g1.scale_factors[0]*image.energy_ev*image.direction[0],1e-100,3e-13);
 close!(back.direction[0],ray.direction[0],3e-13);
 close!(back.energy_ev,ray.energy_ev,3e-13);
 let tiny=2f64.powi(-54);let mut packets=vec![packet(10.,1.)];
 for _ in 0..4096 { packets.push(packet(20.,tiny)); }
 for reverse in [false,true] {
  if reverse { packets.reverse(); }
  let s=RadiationState::new(g([1.;3]),packets.clone()).unwrap();let bins=s.remap(&grid).unwrap();
  let expected_count=1.+4096.*tiny;let expected_energy=10.+4096.*tiny*20.;
  close!(s.comoving_photon_count().unwrap(),expected_count,5e-14);
  close!(bins.total_count().unwrap(),expected_count,5e-14);
  close!(s.comoving_energy_ev_cm3().unwrap(),expected_energy,5e-14);
  close!(bins.total_energy_ev_cm3().unwrap(),expected_energy,5e-14);
 }
 let raw=CharacteristicRay{energy_ev:1.,direction:[1.+5e-13,0.,0.],occupation:0.7};
 let p=PhotonPacket::new(raw,1.).unwrap();check!(p.ray.direction==[1.,0.,0.]);
 check!(raw.pullback(&g([1.;3]),&g([1.;3])).unwrap().energy_ev==1.);
 let iso=raw.derivative(&GeometrySnapshot::new([1.;3],[1.;3]).unwrap()).unwrap();
 check!(iso.direction_dot_per_s==[0.;3]);
 let delta=4.*f64::EPSILON;let weak=CharacteristicRay::new(1.,[0.6,0.8,0.],0.7).unwrap();
 let rhs=weak.derivative(&GeometrySnapshot::new([1.;3],[1.,1.+delta,1.]).unwrap()).unwrap();
 close!(rhs.direction_dot_per_s[0],0.6*0.64*delta,3e-13);
 close!(rhs.direction_dot_per_s[1],-0.8*0.36*delta,3e-13);
 let state=RadiationState::new(g([1.;3]),vec![packet(1e-300,1.)]).unwrap();let before=state.clone();
 check!(state.transport(g([1e100;3])).is_err());check!(state==before);
 println!("PASS {checks} assertions: underflow/covector/inverse/compensated ledgers/normalization/resolved shear/immutability; scientific HOLD");
}
