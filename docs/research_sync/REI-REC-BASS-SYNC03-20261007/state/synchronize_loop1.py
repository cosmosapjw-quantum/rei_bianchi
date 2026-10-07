import json,pathlib,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
review=json.loads((R/'review/LOOP1_DECISION.json').read_text()); assert review['loop1_admitted']
registry={
 'schema':'sync03.four-thread-registry.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'input_status':'source-pinned current at intake; later moving heads are publication identities only',
 'threads':{
 'rei_bianchi':{'source_pin':'84afbe7660ec79e5e43822e7aea49a0a9ee8daea','igm_pin':'a9aea514e086fec6d50cdf14496ff46054cc895e','completed':['F08 actual paired campaign already complete','SYNC03 exact BASS finite-history receiver executed and independently admitted'],'active_owner':['FT_SPEC_BRIDGE02 existing F08 schedule/cohort admission','IGM boundary/midpoint and long-history transport'],'sync03_next':'conditional observable transfer'},
 'BASS_HE':{'source_pin':'eae1d2209fd9a555bea461032f272c7c7c19766e','completed':['HE-FAST-REJOIN01 point bridge13tests56points, upstream evidence'],'baseline_S0_RCT':'OFF','IGM_RCT_common_T_K':[1000,10000],'FT03_RCT_common_T':'EMPTY','active_owner':['HE-FAST-REJOIN02 short history and stage EOS guards'],'history_admitted':False},
 'bass_cr':{'source_pin':'c277bb4305ccddf5b5d94f83f59f398e7f6c3b62','completed':['F04E actual F05 receiver already complete','CR-F0-R1 point bridge23tests6points, upstream evidence'],'baseline_CR':'OFF','candidate_OFF_counts':{'load':0,'callback':0},'owner_history_counts':None,'active_owner':['prepared bridge import and actual history counter instrumentation']},
 'WU088_HH':{'source_pin':'47accb0b3ac9adca40913dc06c797a509c1a7b49','research_lane':'ACTIVE','completed':['ON05B matched finite histories','TH05 bounded FT03 HII/optical-memory theorem, upstream evidence'],'baseline_S0_HH':'OFF','active_owner':['ON06 coherent native pilot'],'total_ne_sign_from_HII_only':'NOT_ADMITTED'}},
 'auxiliary':{'rec_bianchi':{'source_pin':'73ed56b2383e21014fcb70cd8f87f1d010731c60','status':'prior scoped Peebles/REC transfer reused; no unchanged rerun'},'bass':{'source_pin':'1e45e0f48cd83dcb21c23d4087fa5526195331d7','active_native_pin':'1c5db6ddc32c16cacf4ef548f0f6839415ee950a','receiver':'SCOPED_MODULE_EXECUTION_PASS','full_crate':'NOT_RUN_THIS_TASK','finite_temperature_physical_gate':'HOLD'}},
 'legacy_lane':{'policy':'preserved additive, callable on explicit task contract; not required baseline dependency','prior_archive_commit':'7c5469101f8d6ef027c8c3119cc5c053e15ba1d9','no_deletion_or_rebaseline':True},
 'supersedes':['SYNC02 F08 pending','SYNC02 F04E next','HH PARKED/WAITING labels for active research lane','applying old FT03 empty RCT domain to new IGM'],
 'not_superseded':['old source-specific failures','physical HOLD','S0 optional OFF defaults','legacy atomic gates','old backup failures']}
(R/'state/FOUR_THREAD_SYNC.json').write_text(json.dumps(registry,indent=2)+'\n')
evidence=['loop1/RETURN.json','loop1/outputs/NATIVE_SUMMARY.json','loop1/evidence/DECIMAL_RESULT.json','review/LOOP1_DECISION.json','state/FOUR_THREAD_SYNC.json','intake/atomic/ATOMIC_INTAKE.json','intake/rei/NE_INPUT_MANIFEST.json']
gate={'loop1_admitted':True,'synchronized_before_loop2':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision_owner':'independent observable_theory_review','evidence':{p:sha(p) for p in evidence},'next':'loop2/analyze_transfer.py','scope':'conditional endpoint-linear finite slab, no continuum or physical EoR admission'}
(R/'state/SYNC_GATE_LOOP1.json').write_text(json.dumps(gate,indent=2)+'\n');print(json.dumps(gate,indent=2))
