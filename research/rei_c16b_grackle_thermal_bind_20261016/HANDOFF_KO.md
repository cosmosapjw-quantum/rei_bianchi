# GRACKLE_RR_CI_THERMAL_BIND handoff

## 새 기여와 출처

Native coupled backward Euler/Newton을 source-of-truth로 유지한 보존적 단일 transaction, trial reject/step-halving, gas·4 photon arrays·ledger·source cursor·emission cohort의 atomic rollback, 실제 MD14 source adapter를 개발했다. Photon sink는 PreparedAbsorption 한 곳만 소유한다. 원본 Grackle coefficient와 native 과학식은 변경하지 않았다. 계수 단순 치환을 positivity/2차 정확도 증명으로 취급하지 않는다.

Branch `research/rei-c16b-grackle-thermal-bind-20261016`, stacked base PR157 `710f08b2bebaefbd6a28690d450d759877053ebb`. 실제 native PR150 source `a42fd7c9849306074a9f7a262628cd852ce34dea`; 이전 `0e25846433170d0f420c4cda44a0bedbf02cd177`와 전체 Rust tree blob `c7b70221d08ab2617384ccb57af8582a7495b91f` 동일. PR154 `daf653e87a5b208ed6f51113e83d56fec4abf4f8`, PR155 `f8f26710e3961609acf4d7e7930bc7b2a95bd39c`. 최종 게시 commit/PR 및 클라우드 영수증은 DELIVERY_RECEIPT.json에 기록한다. 연구 science commit 이후 영수증 commit을 구분한다.

## 실제 검증

- `python tests_native.py`: 203 mechanical checks, exit 0. 원본 focused native 7 targets / 51 tests, exit 0. Native histories 46개 보존.
- `run_reference.sh`: 60 matched states / 4,980 point checks, 실패 0, 최종 비교 exit 0. Python 독립 full RHS + 변경하지 않은 literal-C Grackle + SciPy Radau. 전체 RHS 최대 상대잔차 7.56032e-15.
- 종별 최대 상대잔차 (HI/HeI/HeII; RR은 해당 ion의 recombination channel):

| 항목 | H | He I channel | He II channel |
|---|---:|---:|---:|
| Gamma | 0 | 1.26484e-16 | 2.00326e-16 |
| heat/absorber | 1.31754e-16 | 2.37072e-16 | 0 |
| CI coefficient | 3.46077e-15 | 7.12492e-15 | 7.16624e-15 |
| RR coefficient | 0 | 0 | 0 |

DR/CE/RR cooling/freefree coefficient 차이 0. 구조적 zero는 exact 비교. 위 표는 이번 60-state 자료이며 PR157 기존 잔차와 구별한다. `evidence/reference/species_maxima.json` 참조.

- Native 누적 최대 에너지 잔차 1.53110e-9 eV/H, 실제 gross 16.8111 eV/H, 변경하지 않은 1e-10 gross bound의 0.910771배. Photon 4.44089e-16/H, charge 3.17964e-12/H. 원자핵은 fraction/EOS 구성과 domain 검사를 독립 확인. Thermal/binding/escape/CMB 및 radiation/work ledger를 분리한다.
- Radau tight rtol1e-10 전 시간 ledger: energy/gross <=3.5115e-12, photon/gross <=1.5281e-11, charge <=8.138e-16. rtol1e-9 dense interpolation의 marginal ledger 실패도 보존했다.
- Proper-time: recomb8000 n128 최대오차 3.33716e-5, 차수 .99878; collision1e5 n128 7.01141e-5, .99927. Mixed n128/n512 transient accuracy 실패를 보존하고 n1024에서 고정 33 observation times .00272292, 자체 1025 grid .00280372, endpoint 4.09569e-5, fixed-grid 차수 .98391. 계약 .005 충족. BE 1차 정확도 범위만 주장한다.
- 실제 MD14 reference-born anisotropic cohort의 독립 source-spectral16/32/64, angular8/16/32, transport32/64/128 refinement: 마지막 인접 차이 1.753e-13 / 2.1864e-4 / .00304396. Fixed-background spectrum/map 시험이다. Birth z20→local z9 mapping은 gas cosmological trajectory가 아니다.
- Stiff initial exposures absorption86.8201, RR10, CI10: positivity/domain/ledger PASS. Coarse strong-absorption trajectory error .01219는 accuracy NOT_ADMITTED. Pulse endpoint 오차 .00145852/.00329694만 보고하며 coarse pulse all-time .06–.14를 정확도 PASS로 취급하지 않는다.
- 원래 dynamic Driver MD14/background/work q_ref0,±.1 각 3 accepted /18 rejects/465 RHS, 총 .47s. 실제 진행 ~112일이며 signed shear/work가 활성화되었다. 동적 수렴 또는 전체 이력 결과가 아니다.

## 첫 실패와 수리

반복 monoenergetic source injection의 N/U 부동소수 표현이 native exact support validator와 충돌했다. 원본 native를 변경하지 않고 thin pulse adapter가 동일 q의 support를 확인한 뒤 N을 합쳐 native add_delta를 한 번 호출하도록 수정했다. 수정 전 pulse nominal32가 실제76/68 substeps였음을 보존했다. 수정 후 실제32 steps이며 artificial substeps 제거에 따른 BE 궤적 차이는 반올림 차이라고 주장하지 않는다. 권위 자료는 evidence/native/pulse_repair/. 검증기 old-path 오류도 수정했다. 성공한 native trial 후 강제 reject→half-step retry는 clean half-steps와 accepted bundle byte-equal, photon/source 중복 없음.

독립 reference의 exactzero subsystem solver tinynegative, metadata serialization/filename 오류, coarse-grid accuracy miss, baseline Radau dense-ledger miss를 first_failure/raw logs에 남겼다. Zero mode는 수학적 invariant 제거, positive sourcefree photon은 log coordinate로 해결했다. Clipping이나 tolerance 완화 없음. 상세 exit code는 양쪽 execution_summary.json과 raw exits.txt에 있다. 기존 untouched native Rust의 cargo fmt baseline 문제를 새 코드 PASS와 혼동하지 않는다.

## NCP 실측과 성능

Host `s1a0e5abed09`, 64 logical CPU, RAM135050518528 B, available 약122GiB, Rust/cargo1.99.0. 기존 R9 (~12 cores)와 full005 raw/checkpoint/binary 보호. build2 jobs, 8GiB limit; worker<=8, 각300s timeout. Source build11.86s/peak327664KiB; focused tests6.12s/168504KiB; native campaign .61s/3584KiB; born-cohort grids3.55s/5592KiB; independent reference15.38s/123836KiB, 최종 dense comparison7.57s/299468KiB. 실제 run별 time-v/RSS는 raw evidence에 있다.

동일 물리 출력 serial/8-worker exact equality (worker metadata 제외). 0.015005724s 대 0.019240846s: 이 workload에서 8 workers가 느리다. HPC speedup을 주장하지 않는다. rclone 미설치이므로 연결된 Dropbox/Drive 파일 API로 업로드한다. 전체 재다운로드 SHA/CRC/manifest 및 각 fresh-source build/essential tests 결과는 DELIVERY_RECEIPT.json에 기록한다.

## 미해결 물리와 다음 READY

Source-age는 emitted interval/mean age metadata이며 surviving cohort spectrum을 풀지 않는다. Case-A escape는 bolometric ledger, frequency/angular distribution 미정. Full MD14 시간 source, surviving-age cohorts, signed evolving Bianchi work와 gas의 장시간 결합, dynamic angular/spectral/time convergence, baryon recoil/Einstein feedback 및 실제 z20→4 이력이 남아 있다. HH 미검증 rate와 conditional REC donor는 활성화하지 않았다.

다음 READY: **SOURCE_AGE_AND_BIANCHI_REFINEMENT** (NEXT_DAG.json). Production scientific admission **NOT_ISSUED**.

복원 후 정확한 최소 실행 명령:

```bash
PYTHON=python3 NATIVE_ROOT=$(mktemp -d /tmp/rei-grackle-native.XXXXXX) bash research/rei_c16b_grackle_thermal_bind_20261016/restore_verify.sh
```

전체 캠페인 재실행은 README_NATIVE_KO.md/README_REFERENCE_KO.md의 mode별 명령을 사용한다. PR150 production full solver를 재시작하지 않는다. 다음 연구에서는 먼저 DELIVERY_RECEIPT.json과 NEXT_DAG.json 및 최신 remote HEAD를 읽는다.
