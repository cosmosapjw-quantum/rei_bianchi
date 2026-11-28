//! PHYS73 finite-quadrature Green action. The PHYS72 exact certificate is separate.
//!
//! No external crates, fast-math, matrix symmetrization, or conjugation are used.
//! A task contains d_i = phi_i*f_i, t_i = f_i/f_(i-1), and a weighted source x_i.
//! t_0 is an unused protocol sentinel and must be exactly zero.
use std::env;
use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter, Read, Write};
use std::path::Path;
use std::thread;
use std::time::Instant;

const INPUT_MAGIC: &[u8; 8] = b"HHG73V01";
const OUTPUT_MAGIC: &[u8; 8] = b"HHO73V01";
const MAX_TASKS: usize = 65_536;
const MAX_NODES: usize = 1_048_576;
const MAX_VALUES: usize = 16_777_216;
const MAX_DENSE_PAIRS: u128 = 1_000_000_000;
const MAX_REPEAT: usize = 10_000;
const MAX_WORKERS: usize = 1_024;

type Result<T> = std::result::Result<T, String>;

#[derive(Clone, Copy, Debug, Default, PartialEq)]
struct Complex {
    re: f64,
    im: f64,
}

impl Complex {
    const ZERO: Self = Self { re: 0.0, im: 0.0 };
    const ONE: Self = Self { re: 1.0, im: 0.0 };
    fn finite(self) -> bool { self.re.is_finite() && self.im.is_finite() }
    fn subnormals(self) -> u64 {
        u64::from(self.re.is_subnormal()) + u64::from(self.im.is_subnormal())
    }
}

#[derive(Clone, Copy, Debug, Default)]
struct Diagnostics {
    arithmetic_subnormal_results: u64,
    multiplication_underflow_to_zero: u64,
}

impl Diagnostics {
    fn merge(&mut self, other: Self) {
        self.arithmetic_subnormal_results += other.arithmetic_subnormal_results;
        self.multiplication_underflow_to_zero += other.multiplication_underflow_to_zero;
    }
    fn finite(&mut self, x: f64) -> Result<f64> {
        if !x.is_finite() { return Err("nonfinite arithmetic intermediate".into()); }
        self.arithmetic_subnormal_results += u64::from(x.is_subnormal());
        Ok(x)
    }
    fn mul(&mut self, a: f64, b: f64) -> Result<f64> {
        let p = self.finite(a * b)?;
        if a != 0.0 && b != 0.0 && p == 0.0 { self.multiplication_underflow_to_zero += 1; }
        Ok(p)
    }
}

/// Ordered Neumaier sum. This compensates addition; product errors are not certified.
#[derive(Clone, Copy, Debug, Default)]
struct Sum {
    hi: f64,
    lo: f64,
}

impl Sum {
    fn from(x: f64) -> Self { Self { hi: x, lo: 0.0 } }
    fn add(&mut self, x: f64, diag: &mut Diagnostics) -> Result<()> {
        let next = diag.finite(self.hi + x)?;
        let error = if self.hi.abs() >= x.abs() {
            let first = diag.finite(self.hi - next)?;
            diag.finite(first + x)?
        } else {
            let first = diag.finite(x - next)?;
            diag.finite(first + self.hi)?
        };
        self.lo = diag.finite(self.lo + error)?;
        self.hi = next;
        Ok(())
    }
    fn value(self, diag: &mut Diagnostics) -> Result<f64> { diag.finite(self.hi + self.lo) }
}

#[derive(Clone, Copy, Debug, Default)]
struct ComplexSum {
    re: Sum,
    im: Sum,
}

impl ComplexSum {
    fn from(z: Complex) -> Self { Self { re: Sum::from(z.re), im: Sum::from(z.im) } }
    fn high(self) -> Complex { Complex { re: self.re.hi, im: self.im.hi } }
    fn low(self) -> Complex { Complex { re: self.re.lo, im: self.im.lo } }
    fn add(&mut self, z: Complex, diag: &mut Diagnostics) -> Result<()> {
        self.re.add(z.re, diag)?;
        self.im.add(z.im, diag)
    }
    fn add_product(&mut self, a: Complex, b: Complex, diag: &mut Diagnostics) -> Result<()> {
        // Explicit arithmetic order; no conjugation and no mul_add/FMA contraction.
        let rr = diag.mul(a.re, b.re)?;
        let ii = diag.mul(a.im, b.im)?;
        let ri = diag.mul(a.re, b.im)?;
        let ir = diag.mul(a.im, b.re)?;
        self.re.add(rr, diag)?;
        self.re.add(-ii, diag)?;
        self.im.add(ri, diag)?;
        self.im.add(ir, diag)
    }
    fn value(self, diag: &mut Diagnostics) -> Result<Complex> {
        Ok(Complex { re: self.re.value(diag)?, im: self.im.value(diag)? })
    }
    fn scale(self, a: Complex, diag: &mut Diagnostics) -> Result<Self> {
        let mut result = Self::default();
        result.add_product(a, self.high(), diag)?;
        result.add_product(a, self.low(), diag)?;
        Ok(result)
    }
}

fn multiply(a: Complex, b: Complex, diag: &mut Diagnostics) -> Result<Complex> {
    let mut sum = ComplexSum::default();
    sum.add_product(a, b, diag)?;
    sum.value(diag)
}

struct Task {
    d: Vec<Complex>,
    t: Vec<Complex>,
    x: Vec<Complex>,
}

struct Input {
    tasks: Vec<Task>,
    nodes: usize,
    input_subnormal_components: u64,
    input_bytes: u64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
enum Mode { Sweep, Dense }

impl Mode {
    fn name(self) -> &'static str { match self { Self::Sweep => "sweep", Self::Dense => "dense" } }
}

/// Exact-arithmetic identity:
/// L_i=t_i L_(i-1)+d_i x_i; T_i=t_(i+1)(x_(i+1)+T_(i+1)); u_i=L_i+d_i T_i.
fn sweep(task: &Task, output: &mut [Complex]) -> Result<Diagnostics> {
    let n = output.len();
    let mut diag = Diagnostics::default();
    let mut left = ComplexSum::default();
    for (i, slot) in output.iter_mut().enumerate() {
        if i != 0 { left = left.scale(task.t[i], &mut diag)?; }
        left.add_product(task.d[i], task.x[i], &mut diag)?;
        // Prefix is rounded once to output precision before combining the upper part.
        *slot = left.value(&mut diag)?;
    }
    let mut tail = ComplexSum::default();
    for i in (0..n.saturating_sub(1)).rev() {
        tail.add(task.x[i + 1], &mut diag)?;
        tail = tail.scale(task.t[i + 1], &mut diag)?;
        let mut total = ComplexSum::from(output[i]);
        total.add_product(task.d[i], tail.high(), &mut diag)?;
        total.add_product(task.d[i], tail.low(), &mut diag)?;
        output[i] = total.value(&mut diag)?;
    }
    Ok(diag)
}

/// Same finite matrix, evaluated with O(n^2) ratio products and ordered sums.
/// G_ik=d_min(i,k)*product(t_(min+1)..t_max), with empty product=1.
fn dense(task: &Task, output: &mut [Complex]) -> Result<Diagnostics> {
    let n = output.len();
    let mut diag = Diagnostics::default();
    for (i, slot) in output.iter_mut().enumerate() {
        let mut sum = ComplexSum::default();
        let mut ratio = Complex::ONE;
        for k in (0..=i).rev() {
            if k < i { ratio = multiply(ratio, task.t[k + 1], &mut diag)?; }
            let coefficient = multiply(task.d[k], ratio, &mut diag)?;
            sum.add_product(coefficient, task.x[k], &mut diag)?;
        }
        ratio = Complex::ONE;
        for k in (i + 1)..n {
            ratio = multiply(ratio, task.t[k], &mut diag)?;
            let coefficient = multiply(task.d[i], ratio, &mut diag)?;
            sum.add_product(coefficient, task.x[k], &mut diag)?;
        }
        *slot = sum.value(&mut diag)?;
    }
    Ok(diag)
}

fn run_parallel(tasks: &[Task], nodes: usize, output: &mut [Complex], workers: usize, mode: Mode) -> Result<Diagnostics> {
    if tasks.is_empty() || nodes == 0 || workers == 0 || workers > tasks.len() || output.len() != tasks.len() * nodes {
        return Err("invalid internal kernel shape".into());
    }
    thread::scope(|scope| {
        let mut handles = Vec::new();
        let base = tasks.len() / workers;
        let extra = tasks.len() % workers;
        let mut first = 0;
        let mut remaining_output = output;
        for worker in 0..workers {
            let jobs = base + usize::from(worker < extra);
            let job_chunk = &tasks[first..first + jobs];
            let (output_chunk, rest) = remaining_output.split_at_mut(jobs * nodes);
            remaining_output = rest;
            first += jobs;
            handles.push(scope.spawn(move || -> Result<Diagnostics> {
                let mut total = Diagnostics::default();
                for (task, result) in job_chunk.iter().zip(output_chunk.chunks_mut(nodes)) {
                    total.merge(match mode { Mode::Sweep => sweep(task, result)?, Mode::Dense => dense(task, result)? });
                }
                Ok(total)
            }));
        }
        let mut total = Diagnostics::default();
        let mut first_error = None;
        for handle in handles {
            match handle.join() {
                Ok(Ok(diag)) => total.merge(diag),
                Ok(Err(error)) => { if first_error.is_none() { first_error = Some(error); } },
                Err(_) => { if first_error.is_none() { first_error = Some("kernel worker panicked".into()); } },
            }
        }
        if let Some(error) = first_error { Err(error) } else { Ok(total) }
    })
}

fn read_u64<R: Read>(reader: &mut R) -> Result<u64> {
    let mut bytes = [0_u8; 8];
    reader.read_exact(&mut bytes).map_err(|e| format!("input read failed: {e}"))?;
    Ok(u64::from_le_bytes(bytes))
}

fn read_array<R: Read>(reader: &mut R, n: usize, subnormals: &mut u64) -> Result<Vec<Complex>> {
    let mut out = Vec::with_capacity(n);
    for _ in 0..n {
        let value = Complex { re: f64::from_bits(read_u64(reader)?), im: f64::from_bits(read_u64(reader)?) };
        if !value.finite() { return Err("nonfinite input component".into()); }
        *subnormals += value.subnormals();
        out.push(value);
    }
    Ok(out)
}

fn checked_shape(tasks: u64, nodes: u64) -> Result<(usize, usize, u64)> {
    if tasks == 0 || tasks > MAX_TASKS as u64 || nodes == 0 || nodes > MAX_NODES as u64 {
        return Err("task/node count outside hard limits".into());
    }
    let total = (tasks as u128) * (nodes as u128);
    if total > MAX_VALUES as u128 { return Err("total node count outside allocation limit".into()); }
    let bytes = 24 + 48 * total;
    Ok((tasks as usize, nodes as usize, bytes as u64))
}

fn read_input(path: &Path) -> Result<Input> {
    let file = File::open(path).map_err(|e| format!("cannot open input: {e}"))?;
    let metadata = file.metadata().map_err(|e| format!("input metadata failed: {e}"))?;
    if !metadata.is_file() { return Err("input must be a regular file".into()); }
    let file_bytes = metadata.len();
    let mut reader = BufReader::new(file);
    let mut magic = [0_u8; 8];
    reader.read_exact(&mut magic).map_err(|e| format!("input header failed: {e}"))?;
    if &magic != INPUT_MAGIC { return Err("invalid input magic/version".into()); }
    let tasks_raw = read_u64(&mut reader)?;
    let nodes_raw = read_u64(&mut reader)?;
    let (task_count, nodes, expected_bytes) = checked_shape(tasks_raw, nodes_raw)?;
    if file_bytes != expected_bytes { return Err(format!("input length mismatch: expected {expected_bytes}, got {file_bytes}")); }
    let mut subnormals = 0;
    let mut tasks = Vec::with_capacity(task_count);
    for _ in 0..task_count {
        let d = read_array(&mut reader, nodes, &mut subnormals)?;
        let t = read_array(&mut reader, nodes, &mut subnormals)?;
        let x = read_array(&mut reader, nodes, &mut subnormals)?;
        if t[0] != Complex::ZERO { return Err("t[0] must be the unused zero sentinel".into()); }
        tasks.push(Task { d, t, x });
    }
    let mut trailing = [0_u8; 1];
    if reader.read(&mut trailing).map_err(|e| format!("input trailing read failed: {e}"))? != 0 {
        return Err("input changed or has trailing bytes".into());
    }
    Ok(Input { tasks, nodes, input_subnormal_components: subnormals, input_bytes: expected_bytes })
}

fn write_output(path: &Path, tasks: usize, nodes: usize, output: &[Complex]) -> Result<()> {
    let file = OpenOptions::new().write(true).create_new(true).open(path).map_err(|e| format!("cannot create new output: {e}"))?;
    let mut writer = BufWriter::new(file);
    writer.write_all(OUTPUT_MAGIC).map_err(|e| format!("output write failed: {e}"))?;
    writer.write_all(&(tasks as u64).to_le_bytes()).map_err(|e| format!("output write failed: {e}"))?;
    writer.write_all(&(nodes as u64).to_le_bytes()).map_err(|e| format!("output write failed: {e}"))?;
    for value in output {
        writer.write_all(&value.re.to_le_bytes()).map_err(|e| format!("output write failed: {e}"))?;
        writer.write_all(&value.im.to_le_bytes()).map_err(|e| format!("output write failed: {e}"))?;
    }
    writer.flush().map_err(|e| format!("output flush failed: {e}"))
}

struct Options {
    input: String,
    output: String,
    workers: usize,
    mode: Mode,
    repeat: usize,
}

fn positive(text: &str, what: &str, max: usize) -> Result<usize> {
    let value = text.parse::<usize>().map_err(|_| format!("invalid {what}"))?;
    if value == 0 || value > max { return Err(format!("{what} outside 1..={max}")); }
    Ok(value)
}

fn options(args: &[String]) -> Result<Options> {
    if args.len() < 3 { return Err("usage: green_batch INPUT OUTPUT [--workers N] [--mode sweep|dense] [--repeat N]".into()); }
    let mut opts = Options { input: args[1].clone(), output: args[2].clone(), workers: 1, mode: Mode::Sweep, repeat: 1 };
    let mut seen = std::collections::HashSet::new();
    let mut i = 3;
    while i < args.len() {
        if i + 1 >= args.len() || !seen.insert(args[i].as_str()) { return Err("missing value or duplicate option".into()); }
        match args[i].as_str() {
            "--workers" => opts.workers = positive(&args[i + 1], "workers", MAX_WORKERS)?,
            "--repeat" => opts.repeat = positive(&args[i + 1], "repeat", MAX_REPEAT)?,
            "--mode" => opts.mode = match args[i + 1].as_str() { "sweep" => Mode::Sweep, "dense" => Mode::Dense, _ => return Err("mode must be sweep or dense".into()) },
            _ => return Err("unknown option".into()),
        }
        i += 2;
    }
    Ok(opts)
}

fn execute(opts: Options) -> Result<()> {
    if env::var("HH_R10").is_ok_and(|s| s != "OFF") { return Err("HH_R10 must remain OFF".into()); }
    if Path::new(&opts.output).exists() { return Err("output exists; choose a new path".into()); }
    let input = read_input(Path::new(&opts.input))?;
    let count = input.tasks.len();
    if opts.mode == Mode::Dense && (count as u128) * (input.nodes as u128).pow(2) * (opts.repeat as u128) > MAX_DENSE_PAIRS {
        return Err("dense work exceeds hard pair-evaluation limit".into());
    }
    let available = thread::available_parallelism().map(|n| n.get()).unwrap_or(1);
    let workers = opts.workers.min(available).min(count);
    let mut output = vec![Complex::ZERO; count * input.nodes];
    let mut timings = Vec::with_capacity(opts.repeat);
    let mut diag = Diagnostics::default();
    for _ in 0..opts.repeat {
        let start = Instant::now();
        diag.merge(run_parallel(&input.tasks, input.nodes, &mut output, workers, opts.mode)?);
        timings.push(start.elapsed().as_secs_f64());
    }
    let output_subnormals: u64 = output.iter().map(|z| z.subnormals()).sum();
    write_output(Path::new(&opts.output), count, input.nodes, &output)?;
    let times = timings.iter().map(|s| format!("{s:.9}")).collect::<Vec<_>>().join(",");
    println!("{{\"schema\":\"PHYS73_GREEN_RUN_V1\",\"mode\":\"{}\",\"tasks\":{},\"nodes\":{},\"workers_requested\":{},\"workers_effective\":{},\"available_parallelism\":{},\"repeat\":{},\"kernel_seconds\":[{}],\"kernel_timing_includes_worker_spawn\":true,\"input_bytes\":{},\"output_bytes\":{},\"input_subnormal_components\":{},\"output_subnormal_components\":{},\"arithmetic_subnormal_results_all_repeats\":{},\"multiplication_underflow_to_zero_all_repeats\":{},\"precision\":\"binary64\",\"certified\":false,\"HH_R10\":\"OFF\"}}", opts.mode.name(),count,input.nodes,opts.workers,workers,available,opts.repeat,times,input.input_bytes,24+16*count*input.nodes,input.input_subnormal_components,output_subnormals,diag.arithmetic_subnormal_results,diag.multiplication_underflow_to_zero);
    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if let Err(error) = options(&args).and_then(execute) {
        eprintln!("green_batch: {error}");
        std::process::exit(2);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};
    static TEMP_ID: AtomicU64 = AtomicU64::new(0);
    fn z(re: f64, im: f64) -> Complex { Complex { re, im } }
    fn example(n: usize, shift: f64) -> Task {
        Task {
            d: (0..n).map(|i| z((i as f64 + shift) / (n as f64), 0.13 * (i as f64).sin())).collect(),
            t: (0..n).map(|i| if i == 0 { Complex::ZERO } else { z(0.8, 0.1) }).collect(),
            x: (0..n).map(|i| z((i as f64 * 0.3).cos(), (i as f64 * 0.7).sin())).collect(),
        }
    }
    fn encode(task: &Task) -> Vec<u8> {
        let mut b = INPUT_MAGIC.to_vec();
        b.extend_from_slice(&1_u64.to_le_bytes());
        b.extend_from_slice(&(task.d.len() as u64).to_le_bytes());
        for a in [&task.d, &task.t, &task.x] { for v in a { b.extend_from_slice(&v.re.to_le_bytes()); b.extend_from_slice(&v.im.to_le_bytes()); } }
        b
    }
    fn parse(bytes: &[u8]) -> Result<Input> {
        let id = TEMP_ID.fetch_add(1, Ordering::Relaxed);
        let path = env::temp_dir().join(format!("phys73_rust_test_{}_{}",std::process::id(),id));
        let mut file = OpenOptions::new().write(true).create_new(true).open(&path).unwrap();
        file.write_all(bytes).unwrap(); drop(file);
        let result = read_input(&path);
        std::fs::remove_file(path).unwrap();
        result
    }
    #[test]
    fn exact_small_matrix_and_single_node() {
        let task = Task { d: vec![z(0.0,0.0),z(1.0,0.0),z(2.0,0.0)],t:vec![Complex::ZERO,Complex::ONE,Complex::ONE],x:vec![z(1.0,0.0),z(2.0,0.0),z(3.0,0.0)] };
        let mut out=vec![Complex::ZERO;3]; sweep(&task,&mut out).unwrap();
        assert_eq!(out,vec![z(0.0,0.0),z(5.0,0.0),z(8.0,0.0)]);
        let one=Task { d:vec![z(2.0,3.0)],t:vec![Complex::ZERO],x:vec![z(4.0,5.0)] };
        let mut out=vec![Complex::ZERO]; sweep(&one,&mut out).unwrap(); assert_eq!(out,vec![z(-7.0,22.0)]);
    }
    #[test]
    fn dense_and_sweep_agree_with_complex_cancellation() {
        for n in [2,7,31,128] {
            let task=example(n,0.25);let mut a=vec![Complex::ZERO;n];let mut b=a.clone();
            sweep(&task,&mut a).unwrap();dense(&task,&mut b).unwrap();
            for (x,y) in a.iter().zip(&b) { assert!((x.re-y.re).abs()+(x.im-y.im).abs()<2.0e-13*(1.0+y.re.abs()+y.im.abs())); }
        }
    }
    #[test]
    fn parallel_workers_have_identical_bits() {
        for (count,workers) in [(17,4),(7,6),(1,1)] {
            let tasks:Vec<_>=(0..count).map(|i| example(33,i as f64)).collect();
            for mode in [Mode::Sweep,Mode::Dense] {
                let mut a=vec![Complex::ZERO;count*33];let mut b=a.clone();
                run_parallel(&tasks,33,&mut a,1,mode).unwrap();run_parallel(&tasks,33,&mut b,workers,mode).unwrap();
                for (x,y) in a.iter().zip(&b) { assert_eq!(x.re.to_bits(),y.re.to_bits());assert_eq!(x.im.to_bits(),y.im.to_bits()); }
            }
        }
    }
    #[test]
    fn parser_rejects_bad_shape_and_payload() {
        let bytes=encode(&example(3,0.0));assert!(parse(&bytes).is_ok());
        assert!(parse(&bytes[..bytes.len()-1]).is_err());
        let mut trailing=bytes.clone();trailing.push(0);assert!(parse(&trailing).is_err());
        let mut bad=bytes.clone();bad[0]=b'X';assert!(parse(&bad).is_err());
        let mut bad=bytes.clone();bad[24..32].copy_from_slice(&f64::NAN.to_le_bytes());assert!(parse(&bad).is_err());
        let mut bad=bytes.clone();bad[24+3*16..32+3*16].copy_from_slice(&1.0_f64.to_le_bytes());assert!(parse(&bad).is_err());
        assert!(checked_shape(0,1).is_err());assert!(checked_shape(u64::MAX,u64::MAX).is_err());assert!(checked_shape(65_536,1_048_576).is_err());
    }
    #[test]
    fn overflow_rejected_underflow_counted() {
        let mut task=Task{d:vec![z(1.0e308,0.0)],t:vec![Complex::ZERO],x:vec![z(1.0e308,0.0)]};
        let mut out=vec![Complex::ZERO];assert!(sweep(&task,&mut out).is_err());
        task.d[0]=z(1.0e-300,0.0);task.x[0]=z(1.0e-100,0.0);
        let diag=sweep(&task,&mut out).unwrap();assert!(diag.multiplication_underflow_to_zero>0);assert_eq!(out[0],Complex::ZERO);
    }
    #[test]
    fn cli_rejects_bad_and_duplicate_options() {
        for tail in [vec!["--workers","0"],vec!["--mode","other"],vec!["--repeat","10001"],vec!["--workers","1","--workers","2"],vec!["--unknown","1"]] {
            let a:Vec<String>=[vec!["x","input","output"],tail].concat().iter().map(|s|s.to_string()).collect();assert!(options(&a).is_err());
        }
    }
}
