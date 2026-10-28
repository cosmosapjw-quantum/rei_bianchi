"""Write a client with coefficients derived from WU incidence and saved rates."""
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def rust_array(values):
    arr=np.asarray(values)
    if arr.ndim==1:return '['+', '.join(format(float(v),'.17e') for v in arr)+']'
    return '['+',\n'.join(rust_array(row) for row in arr)+']'

def write_client(result):
    folder=ROOT/'rust';folder.mkdir(exist_ok=True)
    matrix=np.asarray(result['wu_coefficient_matrix_21_by_21'])
    x=np.asarray(result['x']);upper=np.asarray(result['client_box']['upper'])
    # A strict interior exists only in the supported isotope blocks. n/T have
    # zero-width bounds and remain exactly zero in this diagnostic point.
    positive=upper/4.0
    constants='const A: [[f64;21];21] = '+rust_array(matrix)+';\n'
    constants+='const X: [f64;21] = '+rust_array(x)+';\n'
    constants+='const UPPER: [f64;21] = '+rust_array(upper)+';\n'
    constants+='const POSITIVE_SUPPORTED: [f64;21] = '+rust_array(positive)+';\n'
    code='''//! Generated selected physical coefficients; no solver or norm implementation.
#[path="../reused/gateway.rs"] mod gateway;
use gateway::{BoxDomain,Gate,RuntimeWitness,CallbackFault,Fault};
'''+constants+'''
fn rhs(_t:f64,y:&[f64;21],out:&mut[f64;21])->Result<(),CallbackFault>{
    for i in 0..21 {out[i]=(0..21).map(|j|A[i][j]*y[j]).sum();} Ok(())
}
fn jac(_t:f64,_y:&[f64;21],out:&mut[[f64;21];21])->Result<(),CallbackFault>{
    *out=A; Ok(())
}
fn wrong_jac(_t:f64,_y:&[f64;21],out:&mut[[f64;21];21])->Result<(),CallbackFault>{
    *out=A;out[1][1]*=1.5;Ok(())
}
fn main(){
    let domain=BoxDomain::new(0.0,0.0,[0.0;21],UPPER).unwrap();
    let mut gate=Gate::new(domain,1);
    let mut witness=||RuntimeWitness{epoch:1,environment_ok:true};
    let actual=gate.prepare_pair(0.0,&X,&mut witness,&mut rhs,&mut jac).unwrap();
    let positive=gate.prepare_pair(0.0,&POSITIVE_SUPPORTED,&mut witness,&mut rhs,&mut jac).unwrap();
    let zero=gate.prepare_pair(0.0,&[0.0;21],&mut witness,&mut rhs,&mut jac).unwrap();
    let wrong=gate.prepare_pair(0.0,&X,&mut witness,&mut rhs,&mut wrong_jac);
    let wrong_admitted=wrong.is_ok();
    let wrong=wrong.unwrap();
    let mut bad=X;bad[1]=-1.0e-6;
    let negative_rejected=matches!(gate.eval_rhs(0.0,&bad,&mut witness,&mut rhs),Err(Fault::OutsideDomain));
    let time_rejected=matches!(gate.eval_rhs(1.0,&X,&mut witness,&mut rhs),Err(Fault::OutsideDomain));
    let time_stencil_rejected=matches!(gate.estimate_partial_t_centered(0.0,&X,1.0e-3,&mut witness,&mut rhs),Err(Fault::OutsideDomain));
    let mut over=X;over[1]=UPPER[1]+1.0;
    let upper_rejected=matches!(gate.eval_rhs(0.0,&over,&mut witness,&mut rhs),Err(Fault::OutsideDomain));
    println!("{{");
    println!("\\\"actual_rhs\\\":{:?},",actual.rhs);
    println!("\\\"actual_jacobian\\\":{:?},",actual.jacobian);
    println!("\\\"positive_supported_point\\\":{:?},",POSITIVE_SUPPORTED);
    println!("\\\"positive_supported_rhs\\\":{:?},",positive.rhs);
    println!("\\\"zero_boundary_rhs\\\":{:?},",zero.rhs);
    println!("\\\"wrong_finite_jacobian\\\":{:?},",wrong.jacobian);
    println!("\\\"wrong_finite_jacobian_gate_admitted\\\":{},",wrong_admitted);
    println!("\\\"negative_state_rejected\\\":{},",negative_rejected);
    println!("\\\"outside_time_rejected\\\":{},",time_rejected);
    println!("\\\"outside_upper_rejected\\\":{},",upper_rejected);
    println!("\\\"time_derivative_stencil_rejected\\\":{},",time_stencil_rejected);
    println!("\\\"rhs_calls\\\":{},\\\"jac_calls\\\":{},\\\"pairs\\\":{}",gate.counters().rhs,gate.counters().jac,gate.counters().pairs);
    println!("}}");
}
'''
    (folder/'client.rs').write_text(code)
    return str((folder/'client.rs').relative_to(ROOT))
