use rei_vigilode_age_transport::{affine_transport::{parallel_error_prefix,AffineErrorMap,AffinePrefixWorkspace},certified::{exact,exp_negative,rational_interval},directed::{self,Interval}};
use num_rational::BigRational;
use num_traits::{Zero,ToPrimitive};
use serde::Deserialize;
use serde_json::{json,Value};
use std::{collections::{BTreeMap,HashMap},path::Path,time::Instant};

#[derive(Deserialize)]
struct Model { observe_time_s:f64, clocks:BTreeMap<String,Vec<f64>> }
struct Rate { lambda:BigRational, shares:[Interval;3], central:f64 }
struct Node { cohort:usize, mass:f64, energy:f64, rate:usize, birth:f64 }
struct Cache { rates:Vec<Rate>, values:HashMap<(usize,u64,u64),Interval>, evaluations:usize }
impl Cache {
    fn survival(&mut self, rate:usize, later:f64, earlier:f64)->Interval {
        assert!(later>=earlier);
        let key=(rate,later.to_bits(),earlier.to_bits());
        if let Some(v)=self.values.get(&key) { return *v; }
        let tau=&self.rates[rate].lambda*(exact(later)-exact(earlier));
        let v=exp_negative(&tau);
        self.evaluations+=1;
        self.values.insert(key,v);
        v
    }
}
fn point(x:f64)->Interval { Interval::point(x).unwrap() }
fn add(a:Interval,b:Interval)->Interval { a.add(b).unwrap() }
fn sub(a:Interval,b:Interval)->Interval { a.sub(b).unwrap() }
fn mul(a:Interval,b:Interval)->Interval {
    let i=a.mul(b).unwrap();
    Interval::new(i.lo.max(0.0),i.hi).unwrap()
}
fn j(i:Interval)->Value { json!([i.lo,i.hi]) }
fn sum(values:impl Iterator<Item=Interval>)->Interval { values.fold(point(0.0),add) }
fn model_input(dir:&Path)->(Model,Vec<Node>,Cache) {
    let model:Model=serde_json::from_slice(&std::fs::read(dir.join("model.json")).unwrap()).unwrap();
    let data=std::fs::read_to_string(dir.join("nodes.csv")).unwrap();
    let mut rates=vec![];
    let mut lookup=HashMap::new();
    let mut nodes=vec![];
    for line in data.lines().skip(1) {
        let x:Vec<&str>=line.split(',').collect();
        assert_eq!(x.len(),17);
        let f=|i:usize|x[i].parse::<f64>().unwrap();
        let lambdas=[f(12),f(13),f(14)];
        assert!(lambdas.iter().all(|v|v.is_finite() && *v>=0.0));
        let key=lambdas.map(f64::to_bits);
        let rate=*lookup.entry(key).or_insert_with(|| {
            let lambda=lambdas.iter().map(|v|exact(*v)).sum::<BigRational>();
            let shares=std::array::from_fn(|k|if lambda.is_zero(){point(0.0)}else{rational_interval(&(exact(lambdas[k])/&lambda))});
            let id=rates.len();
            rates.push(Rate{central:lambda.to_f64().unwrap(),lambda,shares});id
        });
        let node=Node{cohort:x[0].parse().unwrap(),mass:f(4),energy:f(11),rate,birth:f(16)};
        assert!(node.cohort<64 && node.mass>=0.0 && node.energy>=0.0);
        assert_eq!(node.birth,model.clocks["64"][node.cohort]);
        nodes.push(node);
    }
    (model,nodes,Cache{rates,values:HashMap::new(),evaluations:0})
}
fn case(model:&Model,nodes:&[Node],cache:&mut Cache,n:usize)->(Value,Interval,f64) {
    let mut totals=[point(0.0);7]; // N,U,age1,age2,A0,A1,A2
    let mut central=[0.0;7];
    let mut underflow=0usize;
    let mut passive=point(0.0);
    let clocks=&model.clocks[&n.to_string()];
    for node in nodes {
        let b=clocks[node.cohort*n/64];
        let age=exact(model.observe_time_s)-exact(b);
        let age_i=rational_interval(&age);
        let e=cache.survival(node.rate,model.observe_time_s,b);
        let survival=mul(point(node.mass),e);
        let absorbed=mul(point(node.mass),sub(point(1.0),e));
        let row=[survival,mul(survival,point(node.energy)),mul(survival,age_i),
                 mul(mul(survival,age_i),age_i),
                 mul(absorbed,cache.rates[node.rate].shares[0]),
                 mul(absorbed,cache.rates[node.rate].shares[1]),
                 mul(absorbed,cache.rates[node.rate].shares[2])];
        for k in 0..7 {totals[k]=add(totals[k],row[k]);}
        let seconds=model.observe_time_s-b;
        let raw_survival=(-cache.rates[node.rate].central*seconds).exp();
        let nc=node.mass*raw_survival;
        let ac=node.mass*(-(-cache.rates[node.rate].central*seconds).exp_m1());
        let values=[nc,nc*node.energy,nc*seconds,nc*seconds*seconds,
            ac*(cache.rates[node.rate].shares[0].lo+cache.rates[node.rate].shares[0].hi)*0.5,
            ac*(cache.rates[node.rate].shares[1].lo+cache.rates[node.rate].shares[1].hi)*0.5,
            ac*(cache.rates[node.rate].shares[2].lo+cache.rates[node.rate].shares[2].hi)*0.5];
        for k in 0..7 {central[k]+=values[k];}
        if nc==0.0 && node.mass>0.0 {underflow+=1;assert!(survival.hi>0.0);}
        if cache.rates[node.rate].lambda.is_zero(){passive=add(passive,point(node.mass));}
    }
    let initial=sum(nodes.iter().map(|x|point(x.mass)));
    let ledger=sub(sum([totals[0],totals[4],totals[5],totals[6]].into_iter()),initial);
    assert!(ledger.contains_zero());
    (json!({"birth_groups":n,"source_templates":64,"prepared_nodes":nodes.len(),
        "N":j(totals[0]),"U_ev":j(totals[1]),"age_first_number_s":j(totals[2]),
        "age_second_number_s2":j(totals[3]),"species_photoevents":[j(totals[4]),j(totals[5]),j(totals[6])],
        "central":{"N":central[0],"U_ev":central[1],"age_first_number_s":central[2],"age_second_number_s2":central[3],"species_photoevents":&central[4..]},
        "initial_mass":j(initial),"photon_ledger_residual":j(ledger),"ledger_contains_zero":true,
        "passive_surviving_mass":j(passive),"central_underflow_nodes_with_positive_upper_bound":underflow}),totals[0],central[0])
}
fn paired(model:&Model,nodes:&[Node],cache:&mut Cache,n:usize,coarse:Interval,fine:Interval,central_diff:f64)->Value {
    let clocks=&model.clocks[&n.to_string()];
    let mut events:BTreeMap<u64,f64>=BTreeMap::new();
    let mut sharp=0.0;
    let mut group_events:Vec<BTreeMap<u64,f64>>=(0..cache.rates.len()).map(|_|BTreeMap::new()).collect();
    let min_lambda=cache.rates.iter().filter(|r|!r.lambda.is_zero()).map(|r|r.lambda.clone()).min().unwrap();
    for node in nodes {
        if cache.rates[node.rate].lambda.is_zero(){continue;}
        let a=clocks[node.cohort*n/64];let b=node.birth;
        let later=a.max(b);let earlier=a.min(b);
        let e=cache.survival(node.rate,later,earlier);
        let delta=mul(point(node.mass),sub(point(1.0),e)).hi;
        let entry=events.entry(later.to_bits()).or_insert(0.0);
        *entry=directed::add_up(*entry,delta).unwrap();
        let group_entry=group_events[node.rate].entry(later.to_bits()).or_insert(0.0);
        *group_entry=directed::add_up(*group_entry,delta).unwrap();
        let tail=cache.survival(node.rate,model.observe_time_s,later);
        sharp=directed::add_up(sharp,directed::mul_up(delta,tail.hi).unwrap()).unwrap();
    }
    events.entry(model.observe_time_s.to_bits()).or_insert(0.0);
    let mut previous=events.keys().next().map(|v|f64::from_bits(*v)).unwrap();
    let mut leaves=vec![];let mut times=vec![];
    for (bits,defect) in events {
        let t=f64::from_bits(bits);
        let gain=exp_negative(&(&min_lambda*(exact(t)-exact(previous)))).hi;
        leaves.push(AffineErrorMap::new(gain,defect).unwrap());times.push(t);previous=t;
    }
    let mut parity=None;let mut radii=vec![];
    let mut algorithm_counts=json!(null);
    for threads in [1,2,4] {
        let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
        let out=pool.install(||parallel_error_prefix(&leaves,0.0)).unwrap();
        let bytes:Vec<_>=out.radii().iter().map(|v|v.to_bits()).collect();
        if let Some(ref p)=parity{assert_eq!(p,&bytes);}else{parity=Some(bytes);}
        let mut workspace=AffinePrefixWorkspace::new(leaves.len()).unwrap();
        assert_eq!(workspace.evaluate(&leaves,0.0).unwrap(),out.radii());
        radii=out.radii().to_vec();
        algorithm_counts=json!({"leaves":out.leaves(),"compositions":out.compositions(),"sweep_levels":out.sweep_levels()});
    }
    let mut oracle=BigRational::zero();
    for (leaf,bound) in leaves.iter().zip(radii.iter().skip(1)){
        oracle=exact(leaf.gain())*oracle+exact(leaf.defect());assert!(exact(*bound)>=oracle);
    }
    // Each exact rate tuple retains its constant total hazard and source labels.
    // Prefix results from different groups are added in a fixed sorted order.
    let mut group_ids:Vec<usize>=(0..cache.rates.len()).filter(|id|!group_events[*id].is_empty()).collect();
    group_ids.sort_by(|a,b|cache.rates[*a].lambda.cmp(&cache.rates[*b].lambda).then(a.cmp(b)));
    let mut grouped_maps=vec![];
    let mut group_leaves=0usize;
    let mut group_compositions=0usize;
    for id in &group_ids {
        let events=&mut group_events[*id];
        events.entry(model.observe_time_s.to_bits()).or_insert(0.0);
        let mut last=f64::from_bits(*events.keys().next().unwrap());
        let mut maps=vec![];
        for (bits,defect) in events.iter() {
            let time=f64::from_bits(*bits);
            let gain=cache.survival(*id,time,last).hi;
            maps.push(AffineErrorMap::new(gain,*defect).unwrap());
            last=time;
        }
        group_leaves+=maps.len();
        group_compositions+=3*maps.len()-2;
        grouped_maps.push(maps);
    }
    let mut grouped_parity=None;
    let mut grouped_upper=0.0;
    let mut grouped_finals=vec![];
    for threads in [1,2,4] {
        let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
        let finals=pool.install(||grouped_maps.iter().map(|maps|{
            let prefix=parallel_error_prefix(maps,0.0).unwrap();
            let mut oracle=BigRational::zero();
            for (leaf,bound) in maps.iter().zip(prefix.radii().iter().skip(1)) {
                oracle=exact(leaf.gain())*oracle+exact(leaf.defect());
                assert!(exact(*bound)>=oracle);
            }
            *prefix.radii().last().unwrap()
        }).collect::<Vec<_>>());
        let bytes:Vec<_>=finals.iter().map(|v|v.to_bits()).collect();
        if let Some(ref previous)=grouped_parity {assert_eq!(previous,&bytes);}else{grouped_parity=Some(bytes);}
        grouped_upper=finals.iter().copied().try_fold(0.0,directed::add_up).unwrap();
        grouped_finals=finals;
    }
    assert!(grouped_upper>=central_diff.abs());
    let prefix=*radii.last().unwrap();
    let difference=sub(coarse,fine);
    assert!(prefix>=sharp,"prefix {prefix} does not bound sharp {sharp}");
    assert!(prefix>=central_diff.abs());
    json!({"coarse":n,"fine":64,"model_premise":"paired cohorts only after both births; final T includes all cohorts",
        "lambda_min_exact_numerator":min_lambda.numer().to_string(),"lambda_min_exact_denominator":min_lambda.denom().to_string(),
        "signed_N_difference":j(difference),"central_N_difference":central_diff,
        "grouped_affine":{"method":"exact_rate_tuple_grouped_affine_prefix_v1",
            "groups":group_ids.len(),"total_leaves":group_leaves,"total_compositions":group_compositions,
            "final_upper":grouped_upper,"final_min_valid_upper":grouped_upper.min(sharp),
            "independent_upper_bounds_not_required_to_order":true,"thread_byte_parity":true,
            "all_group_prefixes_bound_exact_rational_leaf_recurrence":true,
            "rate_ids_in_fixed_sorted_order":group_ids,"group_final_uppers":grouped_finals},
        "sharp_per_node_final_upper":sharp,"affine_prefix_final_upper":prefix,
        "prefix_bounds_sharp":prefix>=sharp,"prefix_bounds_central_observation":prefix>=central_diff.abs(),
        "all_prefixes_bound_exact_rational_leaf_recurrence":true,"rayon_thread_counts":[1,2,4],"thread_byte_parity":true,
        "workspace_matches_allocating_api":true,"algorithm_counts":algorithm_counts,"event_times_s":times,
        "leaf_gain_upper":leaves.iter().map(|x|x.gain()).collect::<Vec<_>>(),
        "leaf_defect_upper":leaves.iter().map(|x|x.defect()).collect::<Vec<_>>(),"prefix_radii":radii})
}
fn main() {
    let args:Vec<_>=std::env::args().collect();
    if args.get(1).map(String::as_str)==Some("--exp-fixtures") {
        let xs=[0.0,f64::from_bits(1),1e-20,0.125,0.5,0.5000000000000001,1.0,3.75,10.0,23.125,100.0,512.25,700.0,744.0,751.99,752.0,10000.0];
        let result:Vec<_>=xs.iter().map(|x|json!({"tau":x,"interval":j(exp_negative(&exact(*x)))})).collect();
        println!("{}",serde_json::to_string_pretty(&result).unwrap());return;
    }
    let started=Instant::now();
    let (model,nodes,mut cache)=model_input(Path::new(&args[1]));
    let mut cases=vec![];let mut populations=vec![];let mut central=vec![];
    for n in [8,16,32,64] {
        let (result,p,c)=case(&model,&nodes,&mut cache,n);cases.push(result);populations.push(p);central.push(c);
    }
    let mut pairs=vec![];
    for (k,n) in [8,16,32,64].iter().enumerate(){pairs.push(paired(&model,&nodes,&mut cache,*n,populations[k],populations[3],central[k]-central[3]));}
    let result=json!({"schema":"rei.vigilode.fixed_age_transport.v1","PRODUCTION_SCIENTIFIC_ADMISSION":"NOT_ISSUED",
        "model":"fixed-source fixed-opacity endpoint geometry; no nonlinear ODE or cosmological history solve",
        "nodes":nodes.len(),"unique_rate_tuples":cache.rates.len(),"certified_exp_evaluations":cache.evaluations,
        "passive_nodes":nodes.iter().filter(|n|cache.rates[n.rate].lambda.is_zero()).count(),
        "wall_seconds":started.elapsed().as_secs_f64(),"cases":cases,"paired_bounds":pairs});
    std::fs::write(&args[2],serde_json::to_string_pretty(&result).unwrap()+"\n").unwrap();
    println!("{}",json!({"status":"COMPLETED","nodes":nodes.len(),"exp_evaluations":cache.evaluations,"wall_seconds":started.elapsed().as_secs_f64()}));
}
