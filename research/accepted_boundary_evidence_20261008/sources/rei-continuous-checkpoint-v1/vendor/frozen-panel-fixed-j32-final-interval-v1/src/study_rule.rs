//! Fixed equal-subcell rule admission, separate from trajectory acceptance.
pub fn allowed_order(j: usize) -> bool { [2,4,8,16,32].contains(&j) }
pub fn interval(l:f64,r:f64,j:usize,n:usize)->Result<(f64,f64),String>{
    if !allowed_order(n) || j>=n || !l.is_finite() || !r.is_finite() || r<=l {return Err("unsupported order or geometry".into());}
    let a=l+(r-l)*j as f64/n as f64;
    let b=if j+1==n {r} else {l+(r-l)*(j+1) as f64/n as f64};
    if !(a>=l && b<=r && b>a) {return Err("unresolved subcell".into());}
    Ok((a,b))
}
pub fn gate(errors:&[f64;13])->Result<bool,String>{
    if errors.iter().any(|x|!x.is_finite() || *x<0.) {return Err("invalid owner error".into());}
    Ok(errors.iter().all(|x|*x<=1e-6))
}
