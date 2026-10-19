from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];C=R/'code/rei_bass_coupled'
p=C/'examples/retarded_joint_server.rs';s=p.read_text()
s=s.replace('let g = common::load(case, 121);','let subdivisions: usize = args.get(2).map_or(Ok(1), |v| v.parse()).map_err(|_| io::Error::other("invalid subdivision"))?;\n    let g = common::load(case, 121);')
old='''let (mut cohorts, seed, panels) = b
        .emit_births(p0.time_s, p1.time_s - p0.time_s, &conf, &gas_mid)
        .unwrap();'''
assert s.count(old)==1
s=s.replace(old,'''let (mut cohorts, seed, panels) = rei_iso_couple_reference::source_support::emit_refined_births(
        &b,p0.time_s,p1.time_s-p0.time_s,&conf,&gas_mid,subdivisions)
        .map_err(|e|io::Error::other(format!("{e:?}")))?;''')
s=s.replace('//! RUN08 exact native finite source packet and retarded RHS verification server.','//! RUN09 derived native exporter: only birth panel subdivision is changed.')
(C/'examples/source_support_server.rs').write_text(s)
(R/'contracts/SUPPORT_EXPORTER_DERIVATION.json').write_text(json.dumps({'parent':'examples/retarded_joint_server.rs','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'replacements':['new CLI subdivision','emit_births -> emit_refined_births','file description'],'scientific_change':'subdivide original graded panels only; same provider evaluation and serializer','schema':'rei.run09.exporter.derivation.v1'},indent=2)+'\n')
