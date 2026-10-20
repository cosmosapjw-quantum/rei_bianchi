//! RUN19 C7: exact-stored-node polynomial versus its rounded four-node kernel.
//! No source fit, log, exp, density, geometry or native RHS is evaluated here.
#![forbid(unsafe_code)]
use std::{fs::File, io::{BufRead, BufReader, BufWriter, Write}, time::Instant};
#[derive(Debug)]
pub enum CoreError { InvalidInput(String), NonFinite(String) }
pub type CoreResult<T> = Result<T, CoreError>;
mod directed;
mod kernel_fragment;
use directed::Interval as I;

fn ideal_weights(t: f64) -> CoreResult<[I; 4]> {
    let t=I::point(t)?;
    let one=I::point(1.0)?;
    let two=I::point(2.0)?;
    let six=I::point(6.0)?;
    let tp=t.add(one)?;
    let tm1=t.sub(one)?;
    let tm2=t.sub(two)?;
    Ok([
        (-t).mul(tm1)?.mul(tm2)?.div(six)?,
        tp.mul(tm1)?.mul(tm2)?.div(two)?,
        (-tp).mul(t)?.mul(tm2)?.div(two)?,
        tp.mul(t)?.mul(tm1)?.div(six)?,
    ])
}
fn from_hex(s:&str)->f64 { f64::from_bits(u64::from_str_radix(s,16).expect("f64 bits")) }
fn main() {
    let args:Vec<_>=std::env::args().collect();
    assert_eq!(args.len(),3,"input.csv output.csv");
    let input=BufReader::new(File::open(&args[1]).expect("input"));
    let mut output=BufWriter::new(File::options().create_new(true).write(true).open(&args[2]).expect("output"));
    writeln!(output,"case,cell,channel,theta_bits,a_bits,b_bits,c_bits,d_bits,tag,structural_zero,value_bits,ideal_lower_bits,ideal_upper_bits,error_upper_bits,relative_upper_bits").unwrap();
    let started=Instant::now();
    let mut cases=0usize;
    let mut positive=0usize;
    let mut zero=0usize;
    let mut max_relative=0.0f64;
    for line in input.lines().skip(1) {
        let line=line.expect("line");
        let fields:Vec<_>=line.split(',').collect();
        assert_eq!(fields.len(),10);
        let t=from_hex(fields[3]);
        assert!((0.0..=1.0).contains(&t));
        let v=[from_hex(fields[4]),from_hex(fields[5]),from_hex(fields[6]),from_hex(fields[7])];
        assert!(v.iter().all(|x|x.is_finite() && *x>=0.0));
        let w=ideal_weights(t).expect("outward weights");
        let p=w[0].mul(I::point(v[0]).unwrap()).unwrap()
            .add(w[1].mul(I::point(v[1]).unwrap()).unwrap()).unwrap()
            .add(w[2].mul(I::point(v[2]).unwrap()).unwrap()).unwrap()
            .add(w[3].mul(I::point(v[3]).unwrap()).unwrap()).unwrap();
        // Verbatim generic source fragment, instantiated for one channel.
        let actual=kernel_fragment::weighted_channels(&[v[0]],&[v[1]],&[v[2]],&[v[3]],
            kernel_fragment::centered_weights(t))[0];
        assert!(actual.is_finite());
        let absolute=I::point(actual).unwrap().sub(p).unwrap().mag();
        let relative=if p.lo>0.0 {
            positive+=1;
            let b=directed::div_up(absolute,p.lo).unwrap();
            max_relative=max_relative.max(b);
            format!("{:016x}",b.to_bits())
        } else {
            assert!(p.lo==0.0 && p.hi==0.0 && actual==0.0,"only certified zero may omit relative bound");
            zero+=1;
            "-".to_string()
        };
        writeln!(output,"{line},{:016x},{:016x},{:016x},{:016x},{relative}",
            actual.to_bits(),p.lo.to_bits(),p.hi.to_bits(),absolute.to_bits()).unwrap();
        cases+=1;
    }
    output.flush().unwrap();
    println!("{{\"cases\":{cases},\"positive_cases\":{positive},\"exact_zero_cases\":{zero},\"max_relative_error_upper\":{max_relative:.17e},\"kernel_wall_seconds\":{:.9},\"source_function_calls\":0,\"native_rhs_calls\":0,\"ivp_runs\":0}}",started.elapsed().as_secs_f64());
}
