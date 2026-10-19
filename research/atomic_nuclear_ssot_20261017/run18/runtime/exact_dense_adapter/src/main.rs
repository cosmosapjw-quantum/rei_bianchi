use num_bigint::BigInt;
use num_rational::BigRational;
use std::io::{self, BufRead};
use std::str::FromStr;
use rei_run18_exact_dense_adapter::{self as exact, Q};

fn bits(text:&str)->Result<u64,String> {
    if text.len()!=16 || !text.bytes().all(|c|c.is_ascii_hexdigit()) {
        return Err("16 hexadecimal bit digits required".into());
    }
    u64::from_str_radix(text,16).map_err(|e|e.to_string())
}

fn process(line:&str)->Result<String,String> {
    let f:Vec<_>=line.split_whitespace().collect();
    if f.len()<2 || !f[1].bytes().all(|b|b.is_ascii_alphanumeric() || b==b'_') {
        return Err("command and ASCII alphanumeric/underscore identifier required".into());
    }
    match f[0] {
        "END" if f.len()==14 => {
            let raw:Vec<u64>=f[2..].iter().map(|s|bits(s)).collect::<Result<_,_>>()?;
            let q:Vec<Q>=raw.iter().map(|b|exact::rational_bits(*b)).collect::<Result<_,_>>()?;
            let coefficients:[Q;7]=q[5..].to_vec().try_into().map_err(|_|"seven coefficients")?;
            let raw_coeff:[u64;7]=raw[5..].try_into().map_err(|_|"seven raw coefficients")?;
            let (value,derivative,x)=exact::dense_value_derivative(&q[0],&q[1],&q[2],&q[3],&coefficients)?;
            let (_,start_derivative,_)=exact::dense_value_derivative(&q[0],&q[1],&q[0],&q[3],&coefficients)?;
            let jump=&q[4]-&value;
            let p=exact::dense_power(&q[3],&coefficients,&x);
            let b=exact::bernstein(&p)?;
            let lower=b.iter().min().ok_or("empty Bernstein vector")?;
            let (iv,id)=exact::interval_dense(raw[0],raw[1],raw[2],raw[3],&raw_coeff)
                .map_err(|e|format!("{e:?}"))?;
            if !exact::interval_contains_exact(iv,&value) || !exact::interval_contains_exact(id,&derivative) {
                return Err("VigilODE interval missed exact dense value or derivative".into());
            }
            Ok(format!(concat!("{{\"id\":\"{}\",\"x_end\":\"{}\",\"value\":\"{}\",",
                "\"derivative\":\"{}\",\"start_derivative\":\"{}\",\"jump\":\"{}\",",
                "\"bernstein_min\":\"{}\",\"value_interval_bits\":[\"{:016x}\",\"{:016x}\"],",
                "\"derivative_interval_bits\":[\"{:016x}\",\"{:016x}\"],",
                "\"exact_value_and_derivative_included\":true}}"),
                f[1],x,value,derivative,start_derivative,jump,lower,
                iv.lo.to_bits(),iv.hi.to_bits(),id.lo.to_bits(),id.hi.to_bits()))
        },
        "BETA" if f.len()==4 => {
            let numerator=BigInt::from_str(f[2]).map_err(|e|e.to_string())?;
            let denominator=BigInt::from_str(f[3]).map_err(|e|e.to_string())?;
            if denominator==BigInt::from(0) {return Err("nonzero denominator required".into());}
            let gamma=BigRational::new(numerator,denominator);
            let (beta,interval)=exact::beta_and_vigilode_enclosure(&gamma)?;
            Ok(format!("{{\"id\":\"{}\",\"gamma\":\"{}\",\"beta\":\"{}\",\"vigilode_interval_bits\":[\"{:016x}\",\"{:016x}\"],\"exact_beta_included\":true}}",
                f[1],gamma,beta,interval.lo.to_bits(),interval.hi.to_bits()))
        },
        _=>Err("END needs12 IEEE64 operands; BETA needs integer numerator/denominator".into()),
    }
}

fn main() {
    for (index,line) in io::stdin().lock().lines().enumerate() {
        let answer=line.map_err(|e|e.to_string()).and_then(|line|process(&line));
        match answer {
            Ok(text)=>println!("{text}"),
            Err(error)=>{eprintln!("input line{}: {error}",index+1);std::process::exit(2);}
        }
    }
}
