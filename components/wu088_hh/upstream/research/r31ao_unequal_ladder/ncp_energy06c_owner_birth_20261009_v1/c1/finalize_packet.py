from pathlib import Path
import json,subprocess,hashlib,re,shutil
O=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def run(n,cmd):
 p=subprocess.run(cmd,cwd=O,capture_output=True);(O/(n+'.stdout')).write_bytes(p.stdout);(O/(n+'.stderr')).write_bytes(p.stderr)
 with (O/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(dict(label=n,argv=cmd,cwd=str(O),exit_code=p.returncode,stdout=str(O/(n+'.stdout')),stderr=str(O/(n+'.stderr'))))+'\n')
 return p
p=run('scoped_tests',['python3','-B','test_packet.py','-v'])
identity=json.loads((O/'CANDIDATE_WORKER_IDENTITY.json').read_text());cmd=identity['command'];dep=cmd[:cmd.index('-L/root/WU088_NCP_EXEC_20261003_v2/prep_r2/backend/prefix/lib')];dep.insert(1,'-MM');run('dependency_closure',dep)
libs=[]
for token in (O/'loader.stdout').read_text().split():
 q=Path(token)
 if token.startswith('/') and q.is_file():libs.append(dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q)))
write('LOADER_BINDING.json',dict(libraries=libs,identity_output=(O/'identity.stdout').read_text(),stability='Snapshot only; recheck immediately before any future authorized invocation'))
checks=json.loads((O/'SOURCE_BINDING.json').read_text())['inputs'];unchanged=all(sha(Path(x['path']))==x['sha256'] for x in checks)
write('INDEPENDENT_CHECKS.json',dict(scoped_tests_exit=p.returncode,tests=8,source_bytes_unchanged=unchanged,scientific_dispatch=0,independent_decision_review=False,red_green_note='No scientific regression or TDD claim. Two actual build failures preserved, final build successful.'))
write('CLAIM_LEDGER.json',dict(byte_identity=unchanged,numerical_equivalence=False,convergence=False,full_box_proof=False,physical_admission=False,provider_admission=False,production_admission=False,upload_restore_verified=False,source_bound_static=True))
write('RUN_LEDGER.jsonl',dict(run_id=identity['run_id'],dispatch_count=0,integrations=0,field_calls=0,status='PREPARATION_COMPLETE_SCIENCE_OPEN'))
report='''# 독립 C1 구현 반환\n\n기준 HEAD 3bfc238f331603c5e4dad54422d75a16ce8e72f1. owner birth 구현과 독립적으로 C1 준비만 수행했다.\n\n별도 candidate integration worker의 cached 107 순서 및 원 log/native schedule을 결속해 컴파일했다. precision128, radius2^-57, signed ordered107, primitive0/fieldO/orbitalS 및 원 272/0 boxes/budget은 proposal에서 유지했다. Frozen 원본/registry는 해시 재확인했다. 기존 build_identity.hpp의 inherited build-source hash는 부모 identity일 뿐이다. 새 worker/source closure/binary hash의 authority는 CANDIDATE_WORKER_IDENTITY.json이다.\n\n공개 실행 진입점은 --identity만 허용한다. 그 외는 exit77이며 field/integration 진입 전에 차단한다. compiled integration draft의 joint_holomorphy_proved=false; whole-box proof가 없는 상태를 true로 승인하지 않았다. 이 binary는 준비용이며 future dispatch에는 proof/admission/controller 및 새 seal이 필요하다.\n\n첫 build는 assembly.hpp include 경로 누락(exit1), 두 번째는 mpfr.h 누락(exit1), 최종 build exit0. 각 실패 로그를 first_/second_로 보존했다. --identity exit0, dispatch-refusal exit77, scoped unittest 8개 통과(exit0). python alias는 없어서 최초 read 명령 exit127, 이후 python3 사용. 통합/field invocation 0, no benchmark/수치동등성/승격. 정확 commands/exit는 COMMANDS.jsonl에 있다. 초기 read-only 탐색 명령은 대화 tool 기록에 남으며 이 ledger는 준비/build/검증 명령이다.\n\nFULL_BOX_FEASIBILITY.json은 source-bound OPEN이다. finite field observations로 적분 admissibility/holomorphic derivative/sign/rank를 증명하지 않았다. 256-term tail은 L1<=64 등 선택 domain에서만 유효하고 바깥은 원 자동 evaluator다. 복소 log image에서 positivity와 sigma 및 branch 조건을 모든 실제 trial box에 대해 증명해야 한다.\n\nCGROUP_BINDING.json: live session CPU/memory unlimited, subtree controllers 비활성. finite delegated C1 cgroup 없음. host/cgroup 변경 및 권한 상승 없음, fake resource file 없음. ancestor/effective memory/host MemAvailable/UID/cap/NoNewPrivs를 raw 기록했으나 reserve/capability-drop admission은 미충족이다.\n\nTWO_CELL_NEW_SCOPE_PROPOSAL_V2.json은 exact source/binary/run ID와 원 budgets를 갖는 OPEN 준비안이다. authorization_record=null, dispatch_count=0, request_ready=false. finite cgroup 및 전체 box proof가 없으므로 실행 승인 요청 준비가 완료되었다고 주장하지 않는다. 과거 scopes는 consumed로 유지한다.\n\n24/289, 265 unbounded, epsilon_C/R=null, B22 OPEN_UNDETERMINED 유지. full49/physical/production admission 없음. 독립 decision review 필요. commit/push/upload 없음. 재현: python3 -B test_packet.py -v (C1 디렉터리). prepare_packet.py는 현재 준비 파일을 재생성하므로 보존된 반환물에서 실행하지 말고 새 별도 C1 경로로 검토 후 복제해야 한다.\n'''
(O/'REPORT_KO.md').write_text(report);(O/'NEXT_HANDOFF_KO.md').write_text('C1 준비 build/test 완료; science OPEN. FULL_BOX_FEASIBILITY.json 의 prerequisites 및 실제 finite delegation을 닫고 새 seal/독립 review/별도 exact authorization 필요. 기존 approvals 재사용 금지. 과학 dispatch0.\n')
write('NCP_LOCAL_CODEX_RETURN.json',dict(status='C1_PREPARATION_BUILT_SCOPED_TESTS_PASSED_SCIENCE_OPEN',tests_exit=p.returncode,dispatch_count=0,authorization_record=None,blockers='BLOCKERS.json',report='REPORT_KO.md',commit=False,push=False))
write('INVENTORY.json',dict(files=[str(q.relative_to(O)) for q in O.rglob('*') if q.is_file()],scope='C1 only'))
manifest=''.join(sha(q)+'  '+str(q.relative_to(O))+'\n' for q in sorted(O.rglob('*')) if q.is_file() and q.name!='SHA256SUMS')
(O/'SHA256SUMS').write_text(manifest)
D=Path('/root/WU088_HH_ENERGY06C_20261009/repo/research/r31ao_unequal_ladder/ncp_energy06c_owner_birth_20261009_v1/c1');D.mkdir(parents=True,exist_ok=True)
for q in O.rglob('*'):
 if q.is_file():d=D/q.relative_to(O);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,d)
assert all(sha(q)==sha(D/q.relative_to(O)) for q in O.rglob('*') if q.is_file())
print(json.dumps(dict(tests_exit=p.returncode,source_unchanged=unchanged,packet=str(D),mirrored=True)))
