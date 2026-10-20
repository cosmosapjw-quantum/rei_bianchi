// Appended to the scratch binary source only under cfg(test).
#[test]
fn fixture_full_study_thread_parity(){
 let ages=CLOCKS.iter().map(|n|(0..*n).map(|j|exact(65.0-(j*64/n) as f64)).collect()).collect();
 let input=Input{nodes:vec![Node{cohort:0,w:2.0,energy:4.0,rate:0},Node{cohort:63,w:3.0,energy:5.0,rate:1}],rates:vec![Rate{lambda:Q::zero(),shares:[p(0.0);3]},Rate{lambda:exact(0.5),shares:[p(1.0),p(0.0),p(0.0)]}],ages};
 let run=|n|rayon::ThreadPoolBuilder::new().num_threads(n).build().unwrap().install(||study(&input));
 let a=run(1);let b=run(2);assert_eq!(a["cases"],b["cases"]);assert_eq!(a["pairs"],b["pairs"]);assert_eq!(a["mode"]["unique_exp_computed"],b["mode"]["unique_exp_computed"]);
 assert!(a["mode"]["unique_exp_computed"].as_u64().unwrap()<16);
}
