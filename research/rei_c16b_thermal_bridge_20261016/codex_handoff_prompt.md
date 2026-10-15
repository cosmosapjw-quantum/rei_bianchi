# Codex handoff: REI C16B → native H/He photo–RR/CI–thermal integration

**목표:** `rei_bianchi`의 실행 가능한 cold reionization production 경로를 향해, 본 패키지의 source-aware photon photoionization 및 positive RR/CI/thermal reference를 **읽기 전용 parity comparator**로 삼아 원래 native Grackle Case-A/MD14 owner와 정확히 연결한다. 기존 PR150 NCP 전체 이력은 우선 보호한다. 필요 자원은 독립 64코어/125GiB NCP를 사용하되 현재 CPU/RAM/활성 작업을 먼저 확인하고 겹치는 full run은 시작하지 않는다.

## 실행 원칙 / read first

이 패키지에서 `README_KO.md`, `NCP_EXECUTION_KO.md`, `contracts/native_authority.json`, `evidence/study_results.json`, `verify.sh`, `src/*.py`, `tests/*.py`부터 읽어라. `AGENTS.md` 등 현재 실제 repo 정책과 `physmath-research-loop`의 scope/유한 검증/실행우선/typed identity 지침을 사용하라. 과거 대화상의 HEAD는 현재 Git 상태의 대용물이 아니다. owner Ubuntu의 `rei_bianchi` 모든 worktree·dirty/untracked·최신 remote HEAD, PR #150 (production), #154 (source-aware baseline), #153 (independent dynamic Verner), #152, #149, 이와 독립적인 `bass_cr` #72, `BASS_HE` #67, `rec_bianchi` #96, `bass` #164를 조사하라. 관련된 실제 구현만 source pin을 확인해 조건부 재사용하고, 출처가 다른 물리 lane을 자동 병합하지 말라.

**동결된 비교 시작점:** PR154 parent commit `daf653e87a5b208ed6f51113e83d56fec4abf4f8`, 원본 photon file Git blob SHA1 `db822a53da3ccdca7cf96628e9ef3bbcec83db5a`. PR150는 본 조사 때 `fe789b0b13b1883c5a74cbc907f72f6f963a5d66`였지만, 지금은 새 HEAD로 바뀌었을 수 있으므로 먼저 갱신하라. `contracts/native_authority.json`의 나머지 original blob SHAs도 같은 의미로 다뤄라. 이전 PR #154/source zip과 이 패키지의 `source_aware.py`는 **바이트 동일**이어야 한다. 이미 실행 중인 /root/REI_FLRW...과 64-core R9 작업은 재개·종료·변경하지 않는다.

## 실행할 범위, 정확한 DAG

1. **SOURCE_INVENTORY:** Git/NCP/disk process/thread resource/source identity 조사. `git status`가 dirty면 그대로 보존하고 전용 isolated 작업 경로를 사용한다. 런타임 환경/IO blocker는 이론/수치/구현 오류와 분리. 원본 live source/checkpoints immutable.
2. **PORTABLE_REPLAY:** 이 handoff ZIP의 SHA, manifest hash를 확인하고 `./verify.sh` 실행. 29개 신규 +22개 PR154 이전 테스트, 독립 DOP853 제조된 rate sweep, 도표를 검증한다. 미통과시 최초 실패를 보존해 repair+targeted regression 하나만 시행한다.
3. **NATIVE_POINT_PARITY:** `IgmGasState`/`igm_rates`/`igm_thermal::igm_point_rhs` 및 `AxbiSource`, `CovariantTransport`, `PreparedAbsorption::evaluate` 실제 ABI/source를 검토한다. Native `(xHII,yHeII,zHeIII)`과 독립 per-H species `(HI,HII,HeI,HeII,HeIII)` 변환, proper `nH,nHe`, `γ_i = c nH Σ_j N_j σ_i(E_j)`, `heat_erg_per_absorber_s = c nH ev_erg Σ_j N_j σ_i(E_j)(E_j−χ_i)`를 exact donor units로 맞춰 같은 조건에서 native RHS photo-event/heat/binding과 비교한다. N/energy per H versus cm³를 혼동하지 말 것. Native actual χ_i in `HHeModel` is distinct from Verner fit threshold E_th. `IgmPhotoInput` does **not** own the photon population; native `PreparedAbsorption`/cold Newton already own physical photon consumption. 이를 중복 수행하면 안 된다.
4. **GRACKLE_RECOMB_THERMAL_BINDING:** 원본 `igm_rates(t)` (RR/CI/DR/CE/freefree)·`igm_point_rhs`·CMB·expansion work를 authoritative provider로 쓰고, **이 패키지의 manufactured alpha,beta,ξ**를 physical rate로 결코 전달하지 마라. 실제 RR kinetic cooling coefficient / rate 비율이 의미 있는 도메인에서만 비교하고 0/DR branch를 별도 처리. RR escaping bolometric energy는 실제 Case-A owner에서 받아야 하고, 광자 **number/energy/angle/source-age distribution을 모른다면 UV에 재삽입하지 마라**. CI thermal depletion, recombination binding/energy, CMB reservoir와 photon energy/work를 한 owner씩 나눠라. 물리적 반례/미확인 부분은 미확인으로 둔다.
5. **PHYSICS_GATES:** (i) H/He nuclei, electron/charge, total photon count and true source/absorption events, (ii) thermal/binding/escaped/CMB/stellar & shear-redshift work, (iii) positivity including stiff extreme and rejected thermal deficit, (iv) source & geometry history exact time/age and sign flips, (v) original FLRW/no-source/zero-ionization limits, (vi) independent angular, spectral-q and proper-time refinements, (vii) matched original native Rust reference, stable tolerance no widening. Source-free symmetric operator second order only for fixed geometry/rates; dynamic T-dependent native parity not inherited from this benchmark.
6. **NCP_LIGHT_HPC:** NCP 연결이 가능하면 입력·resource·source pin을 확인하고, 별도 namespace에서 Python benchmark `hpc_sweep.py`를 serial/8-process로 수행해 deterministic science JSON 바이트 동등성을 검증. Rust native parity runs는 target-specific cargo tests로 진행하고, full production campaign 재실행은 기존 PR150 DAG gate가 정확히 READY일 때만 허용한다.
7. **REVIEW/PUBLISH/BACKUP:** 완료된 과학적 범위만 문서화하고 별도 PR/브랜치로 게시, 원래 production PR150 수정은 별도 리뷰/승인 gate로 보류. 실제 Diff·tests·raw errors·raw outputs 및 native NCP bin/config identity를 commit. 소스와 runnable ZIP + git bundle (가능하면) 생성. `dbx:`와 `gdrv:` 각각 실물 업로드, 독립 전체 SHA 재다운로드 및 필요시 fresh unpack/run 후 receipt 저장. 현재 cloud write capability가 일부 막혀 있다면 분리해 보고하고, 각 단계에서 checkpoint.

## 산출물 수용조건

반드시 (a) 식→입력→native 함수 대응표, (b) 최초 실패와 repair 로그, (c) matched native event/thermal/electron + complete energy ledger 수치 잔차, (d) source·config·provider SHA/commit, (e) 실행 명령과 exit·테스트 수, (f) CPU64/RAM125GiB 실제 메모리·wall·throughput 측정, (g) exact return handoff 및 양쪽 백업·readback ACK를 남겨라. 조건을 못 채우면 `BLOCKED`와 구체적 최소 작업을 기재하고, **photo-only 51 tests**를 완전한 우주론적 재이온화 역사로 승격하지 말라.

## 완료 중단조건

(1) source-aware per-absorber native point parity를 실제 검증하고 그 다음 연산자가 담당할 물리 owner를 확정했거나, (2) 원본 수치 source·자원·권한 blocker를 하나 특정했고 독립 가능한 부분을 저장했으면 현재 범위를 종료한다. 의미 없는 메타검증 반복 금지. 원래 최종 사용자 목표는 non-tilted axisymmetric Bianchi-I의 물리적 `z=20→4` 이온/광자/온도 history와 BBN-style plot이다. 이번 DAG만으로 그 목표를 달성했다고 주장하지 않는다.

**Return payload (이 대화로 복붙할 요약):** git HEAD/branch/PR, exact source refs SHA, native parity 3 ion species table and ledger residuals, tests+exit, NCP machine/log/hardware, archived source+data ZIP/bundle SHA & both provider verified paths/links, unresolved physics and the *single* next READY node.