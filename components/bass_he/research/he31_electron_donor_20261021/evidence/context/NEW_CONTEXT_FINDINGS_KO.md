# HE31 신규 대화·백업 delta 조사

관찰 기준은 **2026-10-21 12:39 UTC 이후**다. HE30의 완료된 237개 과학 결과, 20개 첨부, 기존 백업 무결성 검사는 재실행하지 않았다. 이 보고서는 원격 조회와 이미 저장된 결과의 제한된 읽기에서 얻은 근거다.

## 결과

**새로운 전 구간 z=20→2 H/He 전자 donor는 확인하지 못했다.** 확인한 신규 백업은 BASS ACCEL02의 NCP native-moments 실행 반환 1개다. 다른 대화 전체나 모든 백업의 부재를 뜻하지 않는다.

Personal Context는 실제로 1회 호출했지만 `Personal context is unavailable for this conversation.`로 실패했다. 대화 내용은 0개 취득했다. 이 세션에서 Personal Context가 작동했다고 기록하면 안 된다.

| 조사면 | 실제 조회 범위 | cutoff 이후 관찰 |
|---|---|---|
| Dropbox HE dossier | direct children 6페이지, 3,278개, 마지막 has_more=false | 0개 |
| Dropbox REI backup | recursive 1페이지, 71개, has_more=false | 0개 |
| Dropbox BASS_BACKUPS | recursive 1페이지, 220개, has_more=false | ACCEL02 NCP target archive 1개 |
| Drive HE dossier | direct children 1,000개 상한 | 반환 범위 0개; 전체 폴더 부재 판정 불가 |
| Drive REI backup | direct children 153개 | 반환 범위 0개 |
| Drive 검색 | BASS_HE·rei 시간 필터, 키워드 없는 시간 필터, ACCEL02 exact stem | 각 0개; 검색 색인/범위 한계와 구별 |

Dropbox 검색은 요청한 시간 필터와 무관한 과거 파일을 섞어 반환했다. 최종 delta 판단에는 직접 목록의 실제 server timestamp를 사용했다. HE 내부 하위 폴더는 이번 delta에서 재귀적으로 다시 조사하지 않았다. 자세한 범위는 `COVERAGE.json`에 있다.

## 신규 ACCEL02 NCP 반환

- 파일: `BASS_REI_ACCEL02_NCP_TARGET_20261021_ad92f4207a68.zip`
- Dropbox ID: `id:BSpOijBcT10AAAAAAD_g_w`
- 관찰된 수정 시각: 2026-10-21 12:59:43 UTC
- 크기: 6,003,218 bytes; ZIP member 367개
- 실제 GET SHA256: `ad92f4207a6845a0326a095cb904792b6d34bf0654f7148fe3c530b47f5e2817`
- provider content hash도 다운로드 bytes와 일치했다.
- 실행 source pin: `231df3ab717dbc112f63b77953f64def08e9bcb5`
- 당시 fetched head: `d669298f05286728453840da46cae958a3709456`
- branch: `research/rei-sigma-pi-native-moments-20261021`

저장된 receipt는 NCP에서 custom 5개를 각각 2 steps로 실행해 5개 worker PASS를 얻었고, default 729개는 모두 기존 결과 재사용으로 jobs=0이었다고 기록한다. requested worker cap=2, numerical library thread=1이다. 이는 이 별도 ACCEL02 실행의 근거이며 HE30/HE31이 NCP에서 실행됐다는 근거가 아니다. wall-time speedup이나 64-core scaling 측정 근거도 아니다.

과학적 영역은 **warm conditional a=0.1999→0.2**, 즉 z≈4 부근이다. 저장된 각 history는 2행이며 첫 행 a=0.19994999374843703, 마지막 a=0.2이다. 기존 729개나 cold D3의 전 구간과 혼합해서는 안 된다. receipt 자체 상태는 `EXECUTION_COMPLETE_PENDING_INDEPENDENT_SCIENTIFIC_REVIEW`다. 이 조사에서 그 심사를 대신하지 않았다.

## 재사용할 경계와 현재의 한계

같은 archive source의 다음 기존 코드 경계는 donor adapter 준비에 재사용 가능하다.

1. `research/rei_sigma_pi_pilot_20261021/vendor/rei_c15/research/rei_c14_thomson_receiver_20261015/dynamic_thomson.py`
   - SHA256 `e670ea9de650d69f3a0215a42c5f0f77cb2926c5a566659653c68a967d01064f`
   - `ElectronSource.proper_ne_cm3`는 proper cm^-3.
   - `density = x_e_perH * model.nh / a**3`.
   - log(a)에서 PCHIP를 쓰고 extrapolate=False이다.
   - 기존 from_real_c13는 최소 16개 순증가 sample, 유한 양의 전자 값, 명시된 C13 donor 조건을 검사한다. 새 2-row warm 결과를 이 조건의 donor로 인정할 수 없다.

2. `research/rei_sigma_pi_pilot_20261021/vendor/rei_c15/research/rei_c15_sigma_pi_feedback_20261015/coupled.py`
   - SHA256 `a920d0e86c0badf395bfabc61dafaee3449a34e4cfe8ccdc28a833674c1c4b1e`
   - proper `n_H=n_H0/a^3`, `n_e=n_H*x_e_perH`.
   - Thomson rate는 `n_e[cm^-3] * c_cgs * sigma_T[cm^2]`로 s^-1.
   - code의 physics boundary에는 `n_e_cm3`가 있지만 이 5개 저장된 2-step history에는 explicit n_e column과 HeIII history가 없다.

따라서 기존 단위·보간·외삽 금지의 adapter 원칙은 재사용하고, 새 donor의 HII/HeII/HeIII closure, redshift coverage, source pin과 실제 저장된 이력은 별도로 제시해야 한다. z=4까지만 덮는 source를 z=2로 조용히 연장하면 안 된다.

원 archive의 선택한 6개 member hash, 5개 case의 구간/행 수, 실행 요약은 `NCP_TARGET_DELTA_SANITIZED.json`에 저장했다. private transcript, 임시 다운로드 URL, 계정 정보, 서버의 private 작업 경로는 산출물에 포함하지 않았다.

## 활동 경계

이 조사에서 new science=0, old science rerun=0, benchmark=0, attachment rehash=0, 외부 게시=0, 외부 메시지=0이다. 이후 별도로 요청된 기존 B1/R15 donor 복구를 완료했다. 해당 2026-10-10 원본은 cutoff 이후의 신규 donor가 아니다. `DONOR_RECOVERY.json`과 `DONOR_RECOVERY_KO.md`에 선택 복구 근거·구간·closure를 기록했다.

