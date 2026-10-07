#[path = "../src/tail.rs"]
mod tail;
use std::io::{self, BufRead};
use tail::{characteristic,LogPositive};
fn main(){for line in io::stdin().lock().lines(){let line=line.unwrap();if line.trim().is_empty(){continue;}let x:Vec<f64>=line.split_whitespace().map(|x|x.parse().unwrap()).collect();assert_eq!(x.len(),7);let o=characteristic(LogPositive::from_log(x[0]).unwrap(),LogPositive::from_log(x[1]).unwrap(),[x[2],x[3],x[4]],x[5],x[6]).unwrap();let logs=o.owners.as_array().map(|x|x.log_parts().0.to_string());let vals=o.owners.as_array().map(|x|x.readout().unwrap().value.to_string());let omitted=o.omitted_addend_bounds.as_array().map(|x|x.log_parts().0.to_string());let lows=o.owners.as_array().map(|x|x.log_parts().1.to_string());println!("{}|{}|{}|{}",logs.join(","),vals.join(","),omitted.join(","),lows.join(","));}}
