"""Generate scoped report and next-node handoff from the recorded evidence."""
from pathlib import Path
import json,hashlib,sys,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from runtime_support import atomic_create,file_identity

def text_create(path,text):
    with path.open('x') as f:f.write(text);f.flush();os.fsync(f.fileno())

a=json.loads((ROOT/'results/analysis/ANALYSIS.json').read_text())
assert a['status']=='ANALYSIS_COMPLETE' and a['gates']['failed_count']==0
checks=json.loads((ROOT/'review/INDEPENDENT_RESULT_CHECKS.json').read_text())
assert checks['status']=='PASS_FOR_EVIDENCE_CONSISTENCY'
rows=[v for g in a['snapshot_diagnostics'].values() for lay in g.values() for v in lay.values()]
basis=[v for lay in a['basis_refinement'].values() for k,v in lay.items() if k.startswith('medium_to_fine')]
metrics={
 'backend_energy_max_abs_difference':max(v['all_returned_energy_max_abs_error'] for v in a['backend_parity'].values()),
 'backend_projector_max_operator_distance':max(v['projector_operator_distance'] for v in a['backend_parity'].values()),
 'all_column_Gram_max_entry_error':max(v['all_column_Gram_max_entry_error'] for v in rows),
 'all_column_Gram_max_operator_norm_error':max(v['all_column_Gram_operator_norm_error'] for v in rows),
 'returned_frame_mass_isometry_max_entry_error':max(v['finite_mass_isometry_max_entry_error'] for v in rows),
 'relative_algebraic_residual_max':max(v['relative_algebraic_residual_max'] for v in rows),
 'observed_supplied_guard_spacing_min':min(v['observed_supplied_guard_spacing'] for v in rows),
 'medium_fine_selected_energy_max_delta':max(v['energy_max_abs_delta'] for v in basis),
 'medium_fine_selected_projector_max_distance':max(v['projector_operator_distance'] for v in basis),
 'medium_fine_trace_r2_max_relative_delta':max(v['trace_r2_relative_delta'] for v in basis),
 'fine_outer_layer_probability_max':max(v['outer_layer_probability_max'] for g in a['snapshot_diagnostics'].values() for lay in g.values() for k,v in lay.items() if k.startswith('fine/')),
 'cross_R_fine_sigma_min':min(lay['fine']['principal_overlap_sigma_min'] for g in a['cross_R'].values() for lay in g.values()),
 'quadrature_cross_R_overlap_max_delta':max(v['cross_R_5x5_overlap_max_abs_delta'] for lay in a['quadrature_refinement'].values() for v in lay.values()),
 'gate_count':len(a['gates']['all']),
 'timing':a['timing'],
}
flags={'CODE_I02_CLOSED':True,'full_C2_closed':False,'scientific_PROMOTE':'HOLD','full_certificate_fail_closed':True,'Eq55_next_node_authorized':False,'Eq55':'NOT_RUN','production_default_change':'NOT_AUTHORIZED','continuum_certificate':False,'full_H_gap_certificate':False,'atomic_correlation_established':False,'NCP64_actual_measurement':False}
nextnode='C2H_INDEPENDENT_DISCRETIZATION_AND_EXTERIOR_GUARD_AUDIT'
claims={'schema':'bass-he.c2g.claims.v1','status':'C2G_MULTISTATE_ADAPTER_AND_BOUNDED_REFERENCE_PILOT_COMPLETE','evidence_status':{'common_embedding_mass_identity':'derived and implementation-verified','multistate_selected_guard_return':'implementation-verified and numerically checked','two_backend_parity':'numerically checked on registered finite pilot','fixed_box_refinement':'numerically checked exploratory screen, not true-error enclosure','atomic_channel_identity':'unresolved','full_spectrum_isolation':'unresolved','NCP64_scaling':'not run'},'scope':{'R_in_a_A':[4.0,4.25],'selected_rank':5,'guard_columns':7,'independent_roots_per_successful_layout':54,'successful_layouts':2,'sector_solves':24,'independent_roots':108,'represented_columns_after_pm_reconstruction':144,'old_scientific_suites_rerun':False,'new_unit_tests':52,'independent_prelaunch_checks':8,'prephysics_failed_MPI_attempts':1},'metrics':metrics,'flags':flags,'evidence':{key:file_identity(ROOT/path) for key,path in {'analysis':'results/analysis/ANALYSIS.json','independent_result_checks':'review/INDEPENDENT_RESULT_CHECKS.json','campaign':'results/campaign_ledger/AMENDED_COMPLETED.json','prelaunch_review':'review/PRELAUNCH_INDEPENDENT_REVIEW.json','retry_amendment':'contract/ENVIRONMENT_RETRY_AMENDMENT.json','retry_review':'review/ENVIRONMENT_RETRY_REVIEW.json'}.items()},'next_single_node':nextnode}
atomic_create(ROOT/'CLAIMS.json',claims)

n=a['timing']['layouts']['numpy_serial_1x1'];f=a['timing']['layouts']['native_mpi_2x1']
report=f'''# C2g 다중 상태 adapter·공통 공간 reference pilot

C2g를 사전 등록한 범위에서 완료했다. 실제 분자 고유해 solver가 selected states와 exterior guards의 계수·고유값·잔차를 모두 반환하며, 정적 축대칭 ±m partner를 구성하여 C2f rank-5 projector/transport에 연결했다. R=4 및 4.25 a_A의 세 기저 해상도에서 NumPy 직렬과 Fortran/OpenMPI 경로를 실행했다. 새 단위 검사 52개, 독립 사전 검사 8개, 실제 결과의 등록된 판정 {metrics['gate_count']}개가 통과했다. 이 수들은 서로 겹치는 구현 불변량을 포함하므로 독립 물리 실험 수로 합산하지 않는다.

전체 C2와 production 인증은 HOLD다. 정확도 보존은 여기서 두 실행 경로 사이의 유한 Galerkin 결과 일치를 뜻한다. 연속체·PDE 오차나 최종 collision dynamics의 정확도 인증을 뜻하지 않는다.

## 구현과 물리 convention

내부 무차원 좌표는 x=r/a_A, 전자 에너지는 H/E_A를 사용한다. 정적 실수 spinless 두 점전하 Hamiltonian, ZA=1/ZB=2, nuclear repulsion 제외, 전자 무한원점 에너지 0, O charge-center 좌표계다. O 좌표의 핵 위치는 zA=-2R/3, zB=R/3이고, rmax=20 a_A의 Dirichlet sphere를 사용한다. 외부 영연장은 L² 비교를 정의하며 실제 외부 파동함수를 구한 것이 아니다.

한 sector당 행렬 조립·eigsh 호출을 한 번만 수행하여 모든 root를 보존한다. 고유쌍은 에너지 정렬 후 각 벡터의 최대 절대 계수가 양수가 되게 위상을 고정한다. 기존 단일 상태 solve API에는 이전 ground probe 위상 convention을 유지했다. 저장값은 실제 C†HC와 C†MC이며, 잔차는 ||Hc−EMc||₂/(||Hc||₂+|E| ||Mc||₂)다. 이 무차원 유한 행렬 잔차와 solver tol을 구별한다. SciPy generalized shift-invert 정의는 [공식 1.17.0 문서](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.sparse.linalg.eigsh.html)와 대조했다.

각 R/기저에서 m=0 root 6개와 |m|=1 root 3개를 독립 계산했다. 선택은 m=0 ordinal 1,2,3 및 ±1 ordinal 0이며, ground와 나머지 반환 root는 guard다. 결과는 selected5+guard7 열이다. ψ±1=G exp(±iφ)/√(2π), ψ0=G/√(2π)를 택하고 ψ−1=ψ+1*로 재구성했다. bright=(ψ+1+ψ−1)/√2, dark=(ψ+1−ψ−1)/(i√2)다. [DLMF 14.30](https://dlmf.nist.gov/14.30)의 표준 구면조화함수와는 명시적 phase convention을 구별한다. ± partner 일치는 독립 음의 m eigensolve 결과가 아니라 대칭성에 의한 구성이다. ETF/회전 동역학의 m 분리를 가정하지 않는다.

서로 다른 R의 계수 배열을 직접 내적하지 않는다. 모든 radial knot의 합집합에 r=16 경계를 더하고, 공통 O 좌표의 양의 가중치 W=r²dr dη dφ를 사용한다. 기본 격자는 radial7/η32/φ5, 95,200점이며 확인 격자는 9/40/7, 214,200점이다. 다항식 exact quadrature로 E†WE=M을 유도했고, 반환 root 공간에서는 (EC)†W(EC)=C†MC를 수치 확인했다. 전체 FEM mass matrix를 별도 수치 생성해 검사했다고 주장하지 않는다.

C2f에 전달한 Hsmall은 H_emb=E M⁻¹H M⁻¹E†W로 정의한 유한 embedded weak-form operator의 실제 C†HC다. 점별 PDE H 적용은 하지 않았다. 이 확장의 쓰이지 않은 주변 공간에서는 H가 0으로 작용하므로 그 공간을 실제 물리적 연속체로 해석할 수 없다. polar transport 이후 열은 혼합 frame이며 개별 고유상태 이름을 붙이지 않는다.

## 실행·정확도

lmax=12/20/28, radial base elements=24/32/40, degree4, radial assembly quadrature14를 사용했다. 실제 radial element 수는 핵 위치를 삽입하여 26/34/42이고, 가장 큰 행렬 차원은 4,843이다. 각 layout은 12개 sector solve/54개 독립 root, 두 layout 합계는 24 solve/108 root다. ± 재구성 후 총 144열을 비교했다. coarse/medium/fine의 반지름 격자는 서로 포함 관계가 없는 격자이므로 변분적 단조 수렴을 주장하지 않는다.

| 지표 | 측정값 | 사전 등록 기준 |
|---|---:|---:|
| 두 backend의 전체 반환 고유값 최대 차이 | {metrics['backend_energy_max_abs_difference']:.6e} E_A | 2e-9 E_A |
| 두 backend의 selected projector 거리 | {metrics['backend_projector_max_operator_distance']:.6e} | 2e-7 |
| 모든 selected/guard Gram의 spectral-norm 오차 | {metrics['all_column_Gram_max_operator_norm_error']:.6e} | 2e-10 |
| 반환 frame mass 사상 최대 entry 오차 | {metrics['returned_frame_mass_isometry_max_entry_error']:.6e} | 2e-10 |
| 유한 행렬 상대 잔차 최댓값 | {metrics['relative_algebraic_residual_max']:.6e} | 1e-10 |
| 기본/확인 격자 cross-R overlap 차이 | {metrics['quadrature_cross_R_overlap_max_delta']:.6e} | 2e-10 |

별도의 독립 검산은 각도 직교성을 해석적으로 적분하고, Vandermonde로 복원한 radial FEM 다항식에 6점 GL을 적용했다. 저자 3D grid 경로와 비교하여 trace(r²) 최대 차이 9.24e-14 a_A², 기저 projector 거리 차이 2.92e-16, cross-R projector 거리 차이 2.95e-15였다. solver·provider·embedding 모듈을 다시 사용하거나 고유해를 재계산하지 않았다.

| R/a_A | medium→fine selected ΔE 최대/E_A | projector 거리 | trace(r²) 상대 변화 |
|---|---:|---:|---:|
'''
for R in [4.,4.25]:
 v=a['basis_refinement']['native_mpi_2x1'][f'medium_to_fine/R{R}']
 report+=f"| {R} | {v['energy_max_abs_delta']:.9g} | {v['projector_operator_distance']:.9g} | {v['trace_r2_relative_delta']:.9g} |\n"
report+=f'''
이 세 지표는 등록한 탐색 기준 0.005 E_A, 0.05, 0.02를 통과했다. 그러나 medium→fine 에너지 변화가 최대 약 1.11e-3 E_A이므로 물리적 오차를 backend 차이인 1e-14 수준으로 말할 수 없다. 현재 남은 불확실성은 계산 경로의 일치보다 기저·box·누락 sector의 정확도에 있다.

반환한 guard와 selected 사이의 최소 관찰 간격은 {metrics['observed_supplied_guard_spacing_min']:.9g} E_A로 등록 floor 1e-4를 넘었다. |m|≥2, 미반환 root, continuum은 검사하지 않았으므로 전체 spectrum gap의 하한이 아니다. fine cross-R 최소 principal overlap은 {metrics['cross_R_fine_sigma_min']:.9g}이고 transport gate 0.5를 넘었다. r=16…20 내부 outer-layer의 selected-span 최대 집중도는 fine에서 {metrics['fine_outer_layer_probability_max']:.6e}였지만 box 바깥 tail의 상한은 아니다. 유한 R 원자 채널 상관관계도 아직 증명하지 않았다.

## 성능과 실행환경 복구

Fortran binary64/O3/OpenMP/SIMD kernel, no-fast-math, no reassociation, fp-contract=off를 유지했다. 실제 새 host는 quota8코어/8GiB였고 NCP64는 실행하지 않았다. BLAS thread1, MPI는 독립 task rank-stride와 summary-only gather다.

| 실행 | 완료 wall time | sampled owned RSS |
|---|---:|---:|
| NumPy serial 1×1 | {n['wall_seconds']:.6f} s | {n['sampled_owned_rss_peak_bytes']/2**20:.2f} MiB |
| Fortran OpenMPI 2×1 | {f['wall_seconds']:.6f} s | {f['sampled_owned_rss_peak_bytes']/2**20:.2f} MiB |

이 한 번의 동일-workload 관찰에서 wall time 비율은 {a['timing']['numpy_serial_wall_over_native_mpi_wall']:.4f}다. backend와 병렬도가 함께 변했으므로 순수 Fortran 가속률이나 반복 통계·64코어 scaling으로 해석하지 않는다. 각 layout의 sampled watchdog은 300초/4GiB였다. RSS는 50ms 표본이며 공유 page를 중복 계산할 수 있고 진짜 peak/할당 상한을 증명하지 않는다.

중단 후 host가 교체되면서 mpi4py가 없었다. 첫 MPI 시도는 MPI_INITIALIZATION에서 실패해 물리 작업 0개였고, 오류·로그를 보존했다. 고정 mpi4py4.1.2를 복구하고 독립 검토한 additive amendment에 따라 같은 native layout을 한 번 재시도했다. 코드·원 manifest·물리 기준은 바꾸지 않았으며 NumPy 기준 계산도 반복하지 않았다. 실패 포함 실제 세 launch의 총 wall time은 원래 600초 상한 안에 있다. 원본과 retry 기록을 분리했다.

## 결론과 다음 단일 연구

C2g adapter·공통 공간 사상·bounded finite-reference pilot은 완료했다. 전체 C2, continuum, production, Eq55는 열지 않는다. 다음 node는 `{nextnode}`다. 물리적 정확도의 지배 항을 가르기 위해 독립 discretization, angular/radial/box 축의 분리된 수렴, |m|≥2 exterior guard를 우선한다. 기존 24개 solve를 새 이름으로 반복하지 않고 저장된 coefficients와 이번 결과를 기준으로 새 변경분만 등록한다. 다음 구현 순서와 실행 전에 고정할 계약 항목은 C2G_NEXT_HANDOFF_KO.md에 정리했다.
'''
text_create(ROOT/'C2G_REPORT_KO.md',report)

handoff=f'''# C2g 다음 인계 — 독립 discretization과 exterior guard

현재 stop은 `C2G_MULTISTATE_ADAPTER_AND_BOUNDED_REFERENCE_PILOT_COMPLETE`이며 다음 단일 node는 `{nextnode}`다. `CLAIMS.json`, `C2G_REPORT_KO.md`, `review/PRELAUNCH_INDEPENDENT_REVIEW.json`, `review/INDEPENDENT_RESULT_CHECKS.json`, 최종 결과 review를 읽고 이어간다. frozen code/manifest를 바꾸어 기존 성공 evidence를 새 hash로 꾸미지 않는다.

## 확정된 구현과 수치

solve_many는 실제 m=0 여섯 root, m=1 세 root와 그 coefficients, C†HC, C†MC, per-state algebraic residual을 반환한다. source archive는 pickle 없이 정확한 bytes/SHA/ordinal과 메모리 변경 검증을 포함한다. ±1 reconstruction과 positive physical common grid로 selected5/guard7 Snapshot을 구성했다. current common_embedding은 동일 O origin, 같은 box, m0/|m|1만 지원하며 B-centered/prolate/different-box 입력은 거부한다. 그 거부를 해제하기만 하고 raw coefficient dot을 대입하면 안 된다.

R=4,4.25 a_A; lmax12/20/28, base radial24/32/40, degree4, box20, radialquad14. 두 layout 각각12sector/54roots, 총24sector/108roots, 재구성144열이다. 모든314등록 판정이 통과했다. backend energy 차이≤{metrics['backend_energy_max_abs_difference']:.8e} E_A, projector 차이≤{metrics['backend_projector_max_operator_distance']:.8e}. 하지만 medium→fine ΔE 최대{metrics['medium_fine_selected_energy_max_delta']:.8e} E_A, projector 거리{metrics['medium_fine_selected_projector_max_distance']:.8e}로 절대 물리 오차는 아직 닫히지 않았다.

## C2h 구현·연구 순서

1. 새 namespace에서 기존 C2g coefficients를 read-only 기준으로 사용한다. rank5는 m0 ordinals1,2,3 및 ±1 ordinal0인 후보일 뿐 finite-R atomic correlation을 선언하지 않는다. 각 비교에 target/gap/observable·source-binding을 보존한다.
2. Angular, radial, box의 효과를 별도로 구분한다. lmax만 늘리는 비교와 고정 lmax에서 radial degree/mesh를 바꾸는 비교를 새 계약으로 등록한다. 이번처럼 두 축을 동시에 바꾼 차이를 한 축의 오차 추정으로 해석하지 않는다. 변경 없는 C2g 기준 solve는 다시 돌리지 않는다.
3. 독립 discretization의 실제 excited states 경로를 연결한다. 현재 prolate pair archive는 ground/realbright 첫 상태뿐이므로 rank5로 이름만 바꾸지 않는다. 새로운 provider가 필요한 모든 selected+guard를 반환하도록 먼저 구현·시험한다. 좌표 사상·출처·residual definition을 명시하고 같은 Hilbert 공간으로 비교한다.
4. 최소 |m|=2의 낮은 exterior states부터 실제 finite spectrum 경계를 점검할 수 있도록 angular/general-m provider와 ± partner 규칙을 확장한다. 이것만으로 모든 높은 m·continuum을 배제했다고 주장하지 않는다. 누락 영역에는 별도의 이론적 lower-bound/enclosure가 있어야 full-H gap certificate를 열 수 있다.
5. box20→더 큰 box 비교는 현재 embedding contract 밖이다. 내부 knots를 보존한 box 확장, 작은-box FEM 함수의 정확한 zero-extension과 공통 positive physical quadrature를 유도·구현·검증한 뒤 등록한다. r16…20 집중도 약1e-10을 box 바깥 tail 상한으로 사용하지 않는다.
6. 실행 전 exact R/tasks/basis/guard/root count/tolerances/wall-memory를 고정하고 독립 검토한다. 기준은 요구 observable accuracy와 error allocation에서 정하며 결과를 본 뒤 기준을 느슨하게 바꾸지 않는다. 최우선 stop은 새로운 독립 reference가 현재 rank5의 기저 오차와 알려진 외부 경계 충돌을 판별하는 데 충분한지다. 생산 R-domain/trajectory 선택은 여전히 별도 미해결이며 electronic adapter 자체를 막는 역방향 의존성을 만들지 않는다.

## 실행과 복구

실제 성공 출력은 `results/numpy_serial_1x1.json`과 `results/native_mpi_2x1_retry1.json`이다. 원 `results/native_mpi_2x1.json`은 mpi4py 누락으로 물리 계산 전에 실패한 기록이다. `results/campaign_ledger/AMENDED_COMPLETED.json`이 두 성공 layout의 최종 ledger다. 원 실패를 지우거나 첫 MPI 파일을 성공본으로 덮어쓰지 않는다. `contract/ENVIRONMENT_RETRY_AMENDMENT.json` 및 `review/ENVIRONMENT_RETRY_REVIEW.json`은 환경 복구 재시도만 승인한다.

새 host에서 Python/NumPy/SciPy/mpi4py/OpenMPI import와 native loader를 먼저 확인한다. 기록된 조합은 Python3.12.14, NumPy2.3.5, SciPy1.17.0, mpi4py4.1.2, OpenMPI4.1.6이다. `requirements.txt`와 private archive dependency wheel을 보존했다. compiler profile·source/library SHA·rank별 binding·thread env·process identity는 새 host에서 다시 관찰한다. 기록된 절대 경로는 당시 evidence 경로이지 다른 host의 존재를 보장하지 않는다. 새 실행은 CLI에 새 absolute output/native path를 명시하며 이 host용 provenance helper를 NCP launcher로 오인하지 않는다.

NCP64는 미실행이다. 유효 core/NUMA/available memory를 확인하고 충분한 독립 task 수와 rank별 메모리 측정에 맞춰 rank×thread layout을 사전 등록한다. Fortran/OpenMP/SIMD와 OpenMPI는 정확도·provenance를 유지하며, backend 선택은 동일 workload의 실제 측정에 따른다. 이번1.846배는 한 번의 local combined layout 관찰이고64코어 예측치가 아니다.

## 계승 gate와 완료 조건

`CODE_I02_CLOSED=true`, `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. selected/guard gap, L² projector, finite Galerkin form을 continuum/PDE/unbounded-Ly 인증으로 승격하지 않는다.

사용자가 승인한 같은 branch additive 게시와 Google Drive+Dropbox 이중 백업을 이어간다. 게시 직전 HEAD를 읽고 다른 변경을 보존한다. ACK/object ID/size 및 commit/tree 검증이 충분하면 동일 bytes를 다시 다운로드하지 않는다. UPLOAD_VERIFIED와 RESTORE_VERIFIED는 구분한다. 연구 종료 시 주장·DAG·다음 단일 node·실패 ledger를 함께 갱신한다.
'''
text_create(ROOT/'C2G_NEXT_HANDOFF_KO.md',handoff)
parent=ROOT.parent/'BASS_HE_C2F_CLUSTER_PROJECTOR_20261002_v1/BASS_HE_C2F_RESEARCH_DAG.json';dag=json.loads(parent.read_text())
dag['schema']='bass-he.research-dag.c2g.v1';dag['scope']='scoped C2g real multistate adapter and two-point finite-reference pilot; inherited nodes unchanged'
dag['parent_c2f']={'commit':'6168fdc85e0b4071b79c28e0b148dbd802097ce6','sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'relative_evidence_paths_scope':'inherited nodes retain their parent-publication evidence scope; C2g evidence is local to this package'}
dag['next_single_node']=nextnode
for node in dag['nodes']:
 if node['id']=='C2g':node.update(status=claims['status'],closed_in_scope=True,full_C2_closed=False,physical_launch_enabled=True,evidence=['CLAIMS.json','results/analysis/ANALYSIS.json','review/INDEPENDENT_RESULT_CHECKS.json'])
 if node['id']=='C2':node.update(c2g_multistate_adapter_implemented=True,c2g_two_point_finite_reference_checked=True)
dag['nodes'].append({'id':'C2h','name':nextnode,'status':'READY_FOR_SCOPED_IMPLEMENTATION_AND_PREREGISTRATION','closed':False,'physical_launch_enabled':False,'immediate_predecessors':['C2g'],'purpose':'separate discretization axes and extend independently computed exterior guard evidence without promoting continuum'})
dag['edges'].append({'from': 'C2g', 'to': 'C2h', 'kind': 'scoped_reference_dependency', 'condition': 'preserve C2g successful state archives; new independent-discretization and exterior-sector work needs separately frozen reviewed contract'})
dag['gates']=flags;atomic_create(ROOT/'BASS_HE_C2G_RESEARCH_DAG.json',dag)
print(json.dumps({'status':claims['status'],'metrics':{k:v for k,v in metrics.items() if k!='timing'},'report_bytes':(ROOT/'C2G_REPORT_KO.md').stat().st_size,'handoff_bytes':(ROOT/'C2G_NEXT_HANDOFF_KO.md').stat().st_size},ensure_ascii=False))
