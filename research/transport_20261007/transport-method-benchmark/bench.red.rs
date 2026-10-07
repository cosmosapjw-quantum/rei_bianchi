#[derive(Clone,Copy)] struct Cell{l:f64,r:f64,a:f64,b:f64}
fn moments(_c:Cell)->(f64,f64){(0.,0.)}
fn dg_rhs(_c:Cell,_fl:f64,_fr:f64)->(f64,f64){(0.,0.)}
fn limit(_c:&mut Cell)->Result<f64,String>{Ok(0.)}
fn panel(_l:f64,_r:f64,_a:f64,_s:f64)->(f64,f64,f64,f64,f64){(0.,0.,0.,0.,0.)}
fn fluxes(c:&[Cell])->Vec<f64>{vec![0.;c.len()+1]}
fn totals(c:&[Cell])->(f64,f64){c.iter().map(|x|moments(*x)).fold((0.,0.),|a,b|(a.0+b.0,a.1+b.1))}
struct State{cells:Vec<Cell>,no:f64,eo:f64,w:f64,du:f64}
impl State{fn new(cells:Vec<Cell>)->Self{Self{cells,no:0.,eo:0.,w:0.,du:0.}}}
fn step(_s:&mut State,_dt:f64,_dg:bool,_limited:bool)->Result<(),String>{Ok(())}
include!("tests.rs");
fn main(){}
