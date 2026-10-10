# REI-ACCEL02 후속 실행 시작문

REI-ACCEL02의 최신 publication receipt가 가리키는 additive branch/commit과 durable checkpoint에서 재개하라. campaign ID의 `20261011`은 한국 날짜이며, 이번 실제 실행·review의 UTC 날짜는 `2026-10-10`이다. 최신 commit/tree, 실행 중인 process, 실제 존재하는 source/evidence부터 확인하고 대화 요약으로 파일 존재나 완료를 추정하지 마라.

먼저 `research/accel02_20261011/`의 `NEXT_DAG.json`, `integration/CONTRACT.json`, `n1/REPORT_KO.md`, `n2/CONTRACT.md`, `n2/evidence/EVENT_TIME_COMPARISON.json`, `review/phase2/QUANTITATIVE_DECISION.json` 및 최신 EVENT_COUPLED003 결과·comparison·review를 읽어라. 파일명·위치가 publication projection에서 바뀌었다면 delivery manifest로 정확한 artifact를 찾아라. 완료된 ACCEL01 RUN002와 변하지 않은 provider/old-BASS 검산은 반복하지 마라.

현재 확정된 기준점은 **FLRW r=0, energy128×angle2의 EVENT001/002 same-grid time refinement와 conservation의 독립 scoped PASS**다. 최대 field error `1.4231727742082953e-8`은 기준 `2e-6` 이내이고, combined endpoint/common-epoch energy residual `5.2481356770047917e-11`, number residual `5.010378245671749e-10`은 각각 `1e-9` 이내다. 이 결과가 이전 EVENT001의 number FAIL을 보존한 채 수렴시킨 것이다. EVENT002에서 모든 accepted gas states의 domain은 **NOT_EXPLICITLY_MEASURED**이므로 과거 로그를 all-accepted PASS로 다시 쓰지 마라. 저장된 129개 epoch의 gas domain과 모든 accepted photon positivity만 그 실행의 실제 검증 범위다.

N1의 source/cold Case-A native binding은 scoped DONE이다. N2는 chronology·time·conservation 부분이 완료됐으며 spectral/angular 검증이 남았다. N4는 BASS PR140에서 **이전 ACCEL01 reduced FLRW/r=.1 cell**을 실제 native receiver에 연결한 scoped DONE이다. 이를 이번 native H/He history가 이미 BASS에 수신됐다는 뜻으로 사용하지 마라. N3의 paired Bianchi와 continuum/observational admission은 아직 HOLD다.

EVENT_COUPLED003은 energy256×angle2, r=0, rtol1e-11이며 새 spectral 비교와 all-accepted gas diagnostics를 위한 계산이다. 결과를 먼저 판독하라.

1. **003 결과가 완성되어 기준을 통과했다면**: 저장된 002/003의 공통 epoch에서 field-wise spectral 차이와 actual accepted gas/finiteness/fraction/EOS 진단을 기록하라. residual gate는 segment endpoint와 공통 output epoch의 최대값을 모두 포함한다. 독립 decision이 이미 있으면 같은 결과를 다시 감사하지 말고 그 scope를 재사용하라. 이후 r=.05 Bianchi 장기 paired run으로 진행한다.
2. **003이 spectral 또는 conservation/domain 기준을 실패했다면**: 첫 실패와 source/code identity를 보존하고 어떤 field·energy threshold·source knot가 지배하는지 저장된 자료로 먼저 분류하라. 필요한 수치 수정이나 spectral refinement를 같은 z15.9→4 전체 구간에 적용한다. 허용 기준을 완화하거나 인접한 좁은 redshift interval 검사로 연구 목표를 바꾸지 마라. unchanged failure를 그대로 재실행하지 않는다.
3. **003이 미완료라면**: 실제 process가 살아 있는지 먼저 확인하고 중복 run을 띄우지 마라. process가 종료됐는데 최종 결과가 없으면 interruption/runtime failure로 정확히 분류한다. `RESTART.npz`는 state checkpoint지만 현재 event driver에 `--resume` CLI는 없다. 이를 곧바로 solver 재개 가능한 파일이라고 주장하지 마라. 복구 CLI를 실제 구현·검증하지 않는 한 새로운 campaign 실행은 처음부터 시작한다. 기존 NPZ는 원인 분석·provenance 보존 자료다.

보호할 budget은 time field `2e-6`, initial-energy-normalized energy residual `1e-9`, initial-nH-normalized photon-number residual `1e-9`, N2의 empirical spectral/angular field target `1e-3`, geometry identity `1e-11`이다. nonzero field는 공통 epoch의 차이를 해당 field의 전체 history amplitude로 정상화하고 zero channel은 exact zero를 유지한다. accumulated-budget energy residual은 보조 진단이며 initial-energy target의 대체 기준이 아니다. 새 Bianchi case에는 해당 case의 temporal·spectral·angular 수치 근거가 필요하며 FLRW PASS를 자동 복사하지 않는다.

다음 최소 과학 비교는 **동일 물리 계약의 FLRW와 r=s_i/H_i=.05 전체 z15.9→4**다. 새 source나 CR을 먼저 만들 필요는 없다. HM12 source·conditional initial gas·원자율·Case-A escape·CMB bath를 유지하고, Bianchi characteristic의 late 50keV source까지 q coverage를 잡아라. actual anisotropic angular refinement는 최소 angle4/8 비교에서 시작하며 spectral/time budget도 그 case에서 판단한다. 다음 명령은 003 통과 및 source/build identity 확인 뒤 사용할 최초 candidate 예시다. output 경로는 새 이름으로 만들고 기존 실행을 덮어쓰지 마라.

```bash
repo_path=$(git rev-parse --show-toplevel)
python3 "$repo_path/research/accel02_20261011/n2/run_event_coupled.py" \
  --base-driver "$repo_path/research/accel02_20261011/integration/run_native_history.py" \
  --n1 "$repo_path/research/accel02_20261011/n1" \
  --output "$repo_path/research/accel02_20261011/n2/evidence/EVENT_BIANCHI_R005_E256_A4_NEW" \
  --energy 256 --angle 4 --shear 0.05 --rtol 1e-11 --max-step 0.00390625
```

공통 **mean-volume redshift**에서 `Delta x_HII`, `Delta x_HeII`, `Delta x_HeIII`, `Delta T`, `Delta Gamma_a`, photon number/energy와 명시적으로 export한 경우 photon quadrupole을 비교하라. 효과가 discretization error보다 작으면 검출이 아니라 해상도 한계 또는 bound로 보고한다. homogeneous ionic fraction과 reduced filling factor Q를 같은 변수로 취급하지 마라. source-only frozen-bath diagnostic을 full coupled history로 승격하지 마라.

새 history가 수용되면 별도 후속 N4_NATIVE_CELLS로 실제 `ne(t)`를 BASS에 연결한다. 각 proper-time cell의 `ne_eff=(integral ne dt)/Delta t`를 producer의 실제 quadrature와 함께 export하고 새 run/hash·cosmology·closure·time/density units·frame identity를 담아라. snapshot/old reduced schema와 구분한 뒤 기존 native fixed-time optical-depth/visibility primitive로 한 번 수신한다. 같은 proper-time 경계의 segment tau만 주장하라. observer tail과 실제 null-covector endpoint inversion 없이 total CMB tau 또는 fixed-observed-z 방향별 tau라고 부르지 마라.

선택한 과학 범위는 primary-only, Case-A escaped radiation, 물리 band10–50000eV, prescribed isotropic `T_CMB=2.7255(1+z)` bath다. 초기 `T=20K`, `xHII=2e-4`, neutral He는 conditional IC이며 HyRec 출력이 아니다. 50keV 위 원 HM12 source energy 누락이 z4에서7.668%인 점, 이를 HeII/heating error와 동일시할 수 없다는 점, 실제 Bianchi CMB anisotropy·diffuse 재흡수·backreaction·CR·RCT가 포함되지 않은 점을 유지한다. 원래 CR/RCT/HH 원자물리 lane과 그 blocker는 별도 보존하라.

각 실제 run 완료·첫 실패·수정·decision 시 exact source/binary/input identity, as-run code, 결과·원 로그·checkpoint NPZ·criteria·comparison·review·DAG를 durable checkpoint로 남겨라. additive GitHub publication과 기존 Drive/Dropbox 백업 권한은 유지한다. 기존 owner branch를 force-push하거나 merge하지 않는다. 정상 게시 후 immutable remote identity와 provider ACK/size가 충분하면 같은 자료를 반복 내려받아 hash하는 루프를 만들지 않는다. UPLOAD_VERIFIED와 RESTORE_VERIFIED를 구분한다.

이 후속 작업은 필요한 실제 장기 계산과 그 판별을 수행하는 작업이다. 새 blocker를 해결하지 않는 광범위한 문헌 재탐색·변함없는 certificate 재검사·좁은 interval 반복은 하지 마라.
