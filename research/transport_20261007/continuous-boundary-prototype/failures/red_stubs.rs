pub const EPS: f64=1.602176634e-12;
pub const EC:f64=13.6;
pub const CHI:[f64;3]=[13.598434599702,24.587389011,54.41776];
#[derive(Clone,Copy,Debug,Default)] pub struct Owners {pub n:f64,pub u:f64,pub an:[f64;3],pub be:[f64;3],pub red:f64,pub qn:f64,pub qe:f64,pub outn:f64,pub oute:f64}
#[derive(Clone,Copy,Debug)] pub struct Density{pub l:f64,pub r:f64,pub a:f64,pub k:f64}
#[derive(Clone,Copy,Debug)] pub struct Closure{pub l:f64,pub r:f64,pub n:f64,pub beta:f64,pub front:bool}
#[derive(Clone,Copy,Debug,PartialEq)] pub enum Inventory{Empty, Linear{n:f64,m:f64}, LogTail{ln_n:f64,ln_m:f64}, Atom{eta:f64,n:f64}}
pub fn kernel(_f:f64,_q:f64,_rates:[f64;3],_h:f64,_e:f64)->Result<Owners,&'static str>{Err("not implemented")}
pub fn moments(_d:Density,_a:f64,_b:f64)->(f64,f64){panic!("not implemented")}
pub fn topology(_l:f64,_r:f64,_events:&[f64])->Vec<f64>{panic!("not implemented")}
pub fn initial_transaction(_d:Density,_s0:f64,_s1:f64,_parts:usize,_opacity:bool)->Owners{panic!("not implemented")}
pub fn source_transaction(_s0:f64,_s1:f64,_t:f64,_emin:f64,_emax:f64,_order:usize)->Owners{panic!("not implemented")}
pub fn source_density(_eta:f64,_t:f64,_emin:f64,_emax:f64)->f64{panic!("not implemented")}
pub fn closure_moments(_c:Closure)->(f64,f64){panic!("not implemented")}
pub fn reconstruct(_l:f64,_r:f64,_n:f64,_m:f64,_front:bool)->Result<Closure,&'static str>{Err("not implemented")}
pub fn density_value(_c:Closure,_eta:f64)->f64{panic!("not implemented")}
pub fn inventory(_lnn:Option<f64>,_lnm:Option<f64>)->Result<Inventory,&'static str>{Err("not implemented")}
pub fn gauss(_a:f64,_b:f64,_n:usize)->Vec<(f64,f64)>{panic!("not implemented")}
pub fn merge_moments(_pairs:&[(f64,f64)])->(f64,f64){panic!("not implemented")}
