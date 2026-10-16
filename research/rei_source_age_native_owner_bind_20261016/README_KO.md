# SOURCE_AGE_NATIVE_OWNER_BIND 결과

## 과학적 범위와 판정

PR #164의 frozen neutral source-age 기준해를 실제 REI native MD14 source, signed Bianchi geometry, Grackle Case-A gas chemistry에 연결한 opt-in 연구 실행기다. 실행 원본은 PR #150의 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`이며 PR #160의 완료된 chemistry를 변경하거나 중복 구현하지 않았다. 실행 후 확인된 PR #150 HEAD `90f1d25b7b7700b1bd158320e2d309e9f50705f5`에서 관련 native 7개 파일 blob은 실행 원본과 동일하다.

결론은 **`HOLD_SOURCE_MATCHED_INDEPENDENT_REFERENCE_AND_AGE_REFINEMENT`**다. 짧은 source-native transaction과 보존 검사는 통과했다. 실제 MD14/signed 조건의 독립 DOP853가 내부 trial에서 음의 photon moment를 만들어 native domain guard가 중단했으므로, source-matched 정확도 승인은 없다. 출생시각 격자의 endpoint 차이도 감소하지 않았다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## 새로운 구현

`native_owner.rs`는 양의 cohort에 출생 `ln a`, proper time, 방향, 물리적 에너지 support 및 원래 reference-q moments를 보존한다. Native `AxbiSource`의 per-H proper-second photon rate를 `j=dN/dln a=rate/H`로 변환하여 출생 구간의 적분량만 넣는다. 각 cohort의 원래 `PreparedAbsorption`을 동일한 gas trial에 대해 평가하고 HI/HeI/HeII Gamma와 heat를 한 번 합쳐 원래 `igm_point_rhs`/Grackle Newton gas update에 전달한다. Photon sink는 각 prepared survivor의 단일 소유다. Case-A escape는 bolometric energy만 기록하며 임의 photon spectrum이나 pressure를 만들지 않는다. Signed `s/H`와 `Sigma=sqrt(3)*abs(s)/H`는 구별한다. Verner activation `(13.60,24.59,54.42) eV`와 native binding `(13.598434599702,24.587389011,54.41776) eV`를 별도로 사용한다.

출생 cursor, gas, cohort, photon/thermal/binding/escape/CMB/geometric-work ledger는 private trial에 있다가 accepted step에서 함께 commit된다. 실패 후 rhs 횟수만 청구하고 전 상태를 rollback한다. native EOS와 rate 온도 영역을 geometry endpoint에서도 검사하도록 독립 리뷰 뒤 수리했다. `prepared_node_accessor.rs`는 독립 연속 RHS 실험을 위한 scratch-only read accessor이며 native 원본 접두 바이트를 그대로 보존한다.

## 직접 실행 근거

| 실행 | 결과 | 근거 |
|---|---:|---|
| PR #164 선행 기준해 `PYTHONPATH=... pytest -q` | 34/34, exit 0 | `evidence/local_reference_pass.log`; 첫 경로 오류 exit 2 보존 |
| Repaired local `bash run_local.sh` | 11 검사군, signed 45 사례, exit 0 | `evidence/repaired_local/` |
| Repaired NCP `bash run_local.sh` | 11 검사군, signed 45 사례, exit 0 | `evidence/repaired_ncp/` |
| Local/NCP 공통 수치 파일 | 51/51 byte 동일 | `evidence/repaired_ncp_{remote,local}_sha256.txt` 및 비교 |
| PR #164 coarse angular terminal-cut 반례 | exit 0 | `evidence/terminal_cut_regression.json` |
| source-matched DOP853 | exit 1, domain guard | `evidence/repaired_source_reference/`, `evidence/source_matched_first_failure.stderr` |

Native NCP: `s1a0e5abed09`, 64 logical CPUs, 125 GiB RAM, Rust/Cargo 1.99.0. Repaired build 11.33 s/peak RSS 344056 KiB; run 28.62 s/peak RSS 11724 KiB. 병렬 성능 향상은 측정하지 않았다. 기존 BASS/R9/PR150 프로세스 및 checkpoint는 변경하지 않았다. 최대 energy closure `7.396083745447868e-12 eV/H`, photon closure `8.131516293641283e-20/H`. 출생 뒤 강제 실패 1회에서 RHS 7회를 청구하고 축소 retry가 clean accepted state와 bitwise 동일했다.

`evidence/refinement_summary.json`은 age 8/16/32, angle 8/16/32, source spectral 8/16/32, proper-time 32/64/128, transport cells 16/32/64를 다른 축 고정 상태에서 비교한다. 예를 들어 `s/H=0`에서 photon number의 consecutive absolute changes는 age `7.13e-9, 6.78e-8/H`, angular `5.17e-26, 2.58e-26/H`, spectral `3.33e-19, 2.09e-20/H`, time `1.20e-10, 9.18e-12/H`다. Age 차이가 증가하고 일부 gas observable의 time trend도 단조롭지 않다. Angular photon number의 작은 차이만으로 pressure 정확도를 주장하지 않는다. PR #164 저해상도 pressure 반례에서는 global error `1.466406e-4`에 비해 terminal split error `2.870580e-3`이다.

Species-resolved photo/RR/CI endpoint 적분 event와 `N,U,xHII,xHeII,xHeIII,w,escaped,CMB,work` 원자료는 `history.csv`, 독립 격자별 절대 차이는 `refinement_summary.json`에 있다. 이는 원래 Grackle coefficient와 수치 trajectory의 단일 실행 측정값이며, 별도 literal-C full-history 동등성 증명으로 승격하지 않는다. `independent_solver.py`의 source-free fixed-geometry native continuous RHS Radau/DOP853 비교는 조건부 보조 기준이다.

## 첫 실패와 후속 노드

초기 include/CSV/unsupported nmu/invalid config 실패와 수리 로그는 `evidence/first_build_failure/`에 보존했다. 리뷰 뒤 boundary regression의 첫 테스트 가정 오류와 수리 로그도 `evidence/first_boundary_regression/`에 있다. source-matched 독립 기준해는 291번째 DOP853 RHS 호출에서 photon number 최솟값 `-1.0561176359772685e-20/H`의 trial을 거부했다. positivity preserving 독립 적분기를 설계하고 age quadrature 수렴 원인을 판별하는 다음 노드가 `contracts/NEXT_DAG.json`에 있다. 전체 EoR history 및 energy-momentum 검증은 미실행이다.
