from pathlib import Path
import json,hashlib,subprocess,os,shutil,datetime
R=Path('/root/WU088_HH_ENERGY06C_20261009/repo'); O=Path(__file__).parent
A=R/'research/r31ao_unequal_ladder'; S=O/'source'; S.mkdir(exist_ok=True)
MASTER=Path('/root/WU088_HH_MASTER_EXEC_20261008/runs/master_20261008')
records=[]
def ident(p):
 p=Path(p); b=p.read_bytes(); return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(n,x): (O/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def run(label,cmd):
 p=subprocess.run(cmd,cwd=O,capture_output=True); (O/(label+'.stdout')).write_bytes(p.stdout); (O/(label+'.stderr')).write_bytes(p.stderr)
 row=dict(label=label,argv=list(map(str,cmd)),cwd=str(O),exit_code=p.returncode,stdout=ident(O/(label+'.stdout')),stderr=ident(O/(label+'.stderr')))
 with (O/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 return p
# Read source bytes before every additive snapshot write; never alter originals.
def copy(p,d):
 b=p.read_bytes(); records.append(ident(p)); d.parent.mkdir(parents=True,exist_ok=True); d.write_bytes(b)
G='gap_closure_20261001_g0_g6_v1'; N='ncp64_acceleration_20261001_v1'; W='wide_domain_20261001_v1'
C=A/'fd2_four_callback_authorized_candidate_20261004_v1/reference/candidate/research/r31ao_unequal_ladder'
for name in ['callback.cpp','callback.hpp','finite_m.hpp']:copy(C/G/'validated_callback'/name,S/G/'validated_callback'/name)
for name in ['assembly.cpp','assembly.hpp']:copy(A/G/'validated_callback'/name,S/G/'validated_callback'/name)
for name in ['petras_host.cpp','petras_host.hpp']:copy(A/G/'interior_pilot'/name,S/G/'interior_pilot'/name)
for name in ['cached_callback.cpp','cached_callback.hpp']:copy(C/N/'native_cache'/name,S/N/'native_cache'/name)
for name in ['primitive_worker.cpp','log_map.hpp']:copy(A/W/'log_native_driver'/name,S/W/'log_native_driver'/name)
for name in ['frozen107_generated.hpp','build_identity.hpp']:copy(Path('/root/WU088_NCP_EXEC_20261003_v2/prep_r2/worker')/name,S/W/'log_native_driver'/name)
worker=S/W/'log_native_driver/primitive_worker.cpp'; t=worker.read_text().replace('int main(int argc,char **argv)', 'int c1_integration_candidate_main(int argc,char **argv)')
# Original conditional holomorphy flag must not be an unconditional C1 proof claim.
t=t.replace('callback.joint_holomorphy_proved=true;', 'callback.joint_holomorphy_proved=false; // C1 full-box proof OPEN; fail closed')
t+='''\n#include <mpfr.h>\n// Preparation binary: no science dispatch route is authorized in this packet.\nint main(int argc,char **argv) {\n if(argc==2 && std::string(argv[1])=="--identity") {\n  std::cout << "C1_INTEGRATION_CANDIDATE_PREPARATION_ONLY precision=128 radius=2^-57 FLINT=" << flint_version << " GMP=" << gmp_version << " MPFR=" << mpfr_get_version() << "\\n"; return 0;\n }\n std::cerr << "C1_DISPATCH_BLOCKED authorization_record=null full_box_proof=OPEN\\n"; return 77;\n}\n'''
worker.write_text(t)
for n in ['TWO_CELL_NEW_SCOPE_PROPOSAL.json','FD2_STATUS.json','BLOCKERS.json','RUN_DAG.json']:
 copy(MASTER/n,O/('original_'+n))
proposal=json.loads((MASTER/'TWO_CELL_NEW_SCOPE_PROPOSAL.json').read_text())
fd=json.loads((MASTER/'FD2_STATUS.json').read_text())
for item in fd['protected_registry_files']:records.append(ident(item['path']))
for cell in ['272','000']:
 base=A/'fd2_four_callback_authorized_candidate_20261004_v1/parent_pilot'
 for typ in ['plans','raw']:copy(base/typ/(cell+'.json'),O/'inputs'/typ/(cell+'.json'))
# Current live resource evidence, read only; no cgroup or host mutations.
cg=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')
anc=[]; p=cg
while True:
 vals={}
 for name in ['memory.max','memory.high','memory.current','cpu.max','cpuset.cpus.effective','cgroup.controllers','cgroup.subtree_control','cgroup.procs']:
  q=p/name
  if q.exists():vals[name]=q.read_text().strip()
 anc.append(dict(path=str(p),values=vals))
 if p==Path('/sys/fs/cgroup'):break
 p=p.parent
status=Path('/proc/self/status').read_text(); mem=Path('/proc/meminfo').read_text()
write('CGROUP_BINDING.json',dict(status='OPEN',live_science_binding=None,delegated_finite_binding_available=False,reason='Current live session has no finite CPU/memory limits and no enabled subtree controllers; no C1 delegated worker cgroup identified. Creating or changing host cgroups lies outside the two owned directories. Historical service limits are not reused.',proc_cgroup=Path('/proc/self/cgroup').read_text(),ancestors=anc,proc_status=status,host_meminfo=mem,affinity=sorted(os.sched_getaffinity(0)),host_changes=0,privilege_escalation=False,reserve_admission=False))
compiler=Path('/usr/bin/x86_64-linux-gnu-g++-13'); prefix=Path('/root/WU088_NCP_EXEC_20261003_v2/prep_r2/backend/prefix')
flags=['-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror=return-type','-DWU088_USE_CACHED=1']
binary=O/'c1_candidate_integration_worker'
cmd=[str(compiler),*flags,'-I'+str(prefix/'include'),'-I'+str(S/G/'validated_callback'),str(worker),str(S/N/'native_cache/cached_callback.cpp'),str(S/G/'validated_callback/assembly.cpp'),str(S/G/'interior_pilot/petras_host.cpp'),'-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
run('compiler_version',[str(compiler),'--version']); build=run('build',cmd)
write('CANDIDATE_WORKER_IDENTITY.json',dict(status='BUILT' if build.returncode==0 else 'BUILD_FAILED',run_id='C1_ENERGY06C_20261009_PREPARATION_V1',source=ident(worker),source_closure=[ident(p) for p in S.rglob('*') if p.is_file()],compiler=ident(compiler),flags=flags,command=cmd,exit_code=build.returncode,binary=ident(binary) if binary.exists() else None,precision_bits=128,radius_exp=-57,cpu_info=Path('/proc/cpuinfo').read_text(),integration_entry='compiled but dispatch-blocked',numerical_equivalence=False,target_host_benchmark=False,promotion=False))
if build.returncode==0:
 run('loader',['ldd',str(binary)]); run('elf',['readelf','-h',str(binary)]); run('identity',[str(binary),'--identity']); run('reject_dispatch',[str(binary)])
write('SOURCE_BINDING.json',dict(inputs=records,exact_scalar_expected='7b06ed12be2afd191831676ed2f3eae4198ae39805434c09fac59b1581f34282',source_files_rechecked_unchanged=all(ident(x['path'])['sha256']==x['sha256'] for x in records)))
(O/'INPUT_SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in records))
write('FULL_BOX_FEASIBILITY.json',dict(status='OPEN_NOT_PROVED',source_bound=True,field_observations={'finite_107':True,'integrations':0,'scope_consumed':True},cell_inputs=proposal['cell_inputs'],field_scope=proposal['field_scope'],kernel_domain=proposal['candidate_sources']['candidate_domain'],tail_bound='sum n=0..255; error |T256|*26471/19815; ratio<=6656/26471 under selected k,r and whole L1<=64',selected_kernel_predicate='odd k <=8, r<=2, z contains zero, finite whole complex ball, L1<=64; outside selected domain unchanged pinned evaluator',whole_physical_boxes_inclusion=False,holomorphic_derivative_admission=False,sign_rank_admission=False,real_rectangle_margin='min(l_t,l_u, (1/(a+T_t)+1/(b+T_u))/2)/2^20, capped by original contract margin',log_image='t=exp(log(2)*x), u=exp(log(2)*y), Jacobian=(log(2))^2*t*u; entire outer balls preserved',proof_prerequisites=['For every trial complex box prove Re(t),Re(u),Re(a+t),Re(b+u),Re(sigma) above exact original margin','Enclose z=-s/(2*sigma); establish selected-series L1<=64 or original evaluator admissibility','Holomorphic principal powers on mapped boxes; parameter integral holomorphy and required derivative/ordered107 sign/rank obligations','Actual finite delegated CPU/memory/capability-drop binding, effective ancestor cap and reserve admission','Exact newly issued human authorization; source/binary/ABI/loader/cgroup/plan hash seal'],order_semantics='acb_calc order 1 requests analytic enclosure, not radial derivative rank; unsupported order >1 refused',precision_bits=128,radius_exp=-57,coverage={'bounded':24,'total':289,'unbounded':265,'epsilon_C':None,'epsilon_R':None,'B22':'OPEN_UNDETERMINED'},science_calls=0))
proposal.update(schema='WU088_C1_TWO_CELL_NEW_SCOPE_PROPOSAL_V2',task_id='C1_ENERGY06C_20261009_PREPARATION_V1',status='OPEN_PROPOSAL_NOT_AUTHORIZATION_NOT_EXECUTABLE',authorization_record=None,dispatch_count=0,scope_consumed=False,request_ready=False,candidate_worker=ident(binary) if binary.exists() else None,candidate_source=ident(worker),cgroup_binding=None,parent_proposal=ident(MASTER/'TWO_CELL_NEW_SCOPE_PROPOSAL.json'),full_box_feasibility=ident(O/'FULL_BOX_FEASIBILITY.json'))
# Remove stale content digest; new canonical digest deliberately excludes itself.
proposal.pop('proposal_content_sha256',None); proposal['proposal_content_sha256']=hashlib.sha256(json.dumps(proposal,sort_keys=True,separators=(',',':')).encode()).hexdigest();write('TWO_CELL_NEW_SCOPE_PROPOSAL_V2.json',proposal)
write('AUTHORIZATION_AUDIT.json',dict(authorization_record=None,dispatch_count=0,old_scopes_consumed=True,old_registry_unchanged=all(ident(x['path'])['sha256']==x['sha256'] for x in fd['protected_registry_files']),integration_calls=0,field_calls=0,owner_birth_implementation_touched=False))
write('BLOCKERS.json',dict(status='OPEN',blockers=['Whole complex integration-box admissibility, holomorphic derivative and sign/rank proof absent','No live finite delegated cgroup science binding','No new exact scientific authorization','Candidate numerical equivalence and target-host benchmark not performed; independent decision review required before promotion']))
write('RUN_DAG.json',dict(nodes=['source read/hash','additive isolated candidate build','non-science identity/refusal tests','OPEN feasibility/proposal'],science_dispatch=0))
print('build exit',build.returncode)
