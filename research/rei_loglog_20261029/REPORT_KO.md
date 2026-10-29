# REI 로그 축 재구성과 조건부 Jacobian 연구

현재 결과는 분석·코드 준비 단계이며 사용자가 요청한 새 로그–로그 그림은 아직 생성하지 않았다. 기존 PR259의 완성된 그림은 그대로 유지한다. 새 12쪽 구성은 전체17상태, 다섯 군, 부호를 분리한 응답·refinement·보존량, 세 초기 transient 그림이며 저장된 값만 연결한다.

17상태의 시작은 모두 elapsed proper time0, mean z20이다. 10개 상태의 초기값은0이지만 ON_refined에서는 첫 양의 저장시간0.08238295318127252초에 모두 양수다. 기존 overview에서 아홉 상태의 초기 양의 점이 표시 하한보다 낮아 곡선이 늦게 시작한 듯 보였다. 시간0과 abundance0은 로그 축에 그릴 수 없으므로 원시값과 초기값 표에 보존한다. 양의 epsilon을 넣거나 시작시점을 바꾸지 않는다.

고정된 prescribed bath의 기존23상태 다항식 RHS에 대한23×23 analytic Jacobian을 유도하고 원본 RHS와 정적으로 대조했다. 이는 실제 자기일관적 물리 chemistry Jacobian이나 source sensitivity가 아니다. 실제 저장 bath를 구성하는 외부 NPZ와 donor 구현은 아직 확보되지 않았으므로 새 검증은 source-defined fixed coefficients에 대한 structural validation으로 제한한다. source-compiled fixed-field structural validation, zero/signed polynomial·capture gradient·세 plot contract test와 onset audit는 완료됐다. 실제 저장 bath linkage는 MISSING이며 독립 결과검토 FINAL_SCIENTIFIC_REVIEW.md에서 PASS_SCOPED로 수용됐다. 결과는 outputs/main_structural_20261029에 보존한다. 독립검토자가 확인한 최대 normalized ledger residual은1.37e-16, scale-transform discrepancy는2.47e-32, raw directional finite-difference discrepancy는1.443e-13이다. 실행 전 root가 동결한 판정은 componentwise1e-6×signal_bound+roundoff_allowance와 ledger1e-12이며, 초기 제안의1e-7/5e-13과 구별한다.

등방·비편극 원자의 선형 scalar photo-rate는 고정 spectral monopole에서 quadrupole만 바꾸면 변하지 않는다. Bianchi Liouville 방정식의 shear–quadrupole 결합은 monopole을 변화시킬 수 있으며 near-isotropic ordering에서는 그 scalar 효과가2차다. 이 해석과 계수·부호는 분석적으로 유도했다. Exa와 SciSpace의 문헌 맥락을 사용했다. Wolfram 맥락을 사용했고3초 제한 angular-integral 호출은 `$Aborted`를 반환했다. 그 호출의 검증된 CAS 결과는 없으며 분석 유도의 수치 검증으로 세지 않는다. Personal context는 사용할 수 없었다.

작업용 DAG33/88, 중앙28/88, physical-fast4/7은 모두 유지한다. 새로운 원본 완료 node나 실제 저장 bath 검증, 새 IVP를 수행하지 않았다. 전체 요청은 PARTIAL이다.

## 자원과 실행 경계

원래 정책 ceiling은 main600/presentation30/planning10 CPU초다. 기존 누적608.750604/65.980312494/20.819461885와 UNKNOWN_NOT_ZERO 비용은 그대로 보존한다. main의 새4초 reservation은 임시620 ceiling(원래600보다3.333%) 안에서 별도 bounded validation을 위한 것이며 실제 CPU0.214128초, 측정 누적608.964732다. 전체 reservation을 유지한 main 누적은612.750604이며 미사용3.785872초도 보류 차감으로 유지한다. 정책 ceiling600을 복원했고 임시620의 해당 단위는 종료·만료됐다. 최초 `/usr/bin/time` 부재 exit127을 보존했으며 root가 launcher만 고치도록 승인했다. IVP 재시도가 아니고 실패 overhead는 UNKNOWN_NOT_ZERO다.

presentation의 이전66 ceiling은 소모 후 만료됐다. 새4초 reservation을 수용하는 누적70 ceiling은 원래30 대비133.333% 증가로 별도 승인이 필요하다. 예측 실행량≤3.5초, wall60초, memory512MiB,1회, 자동재시도 없음이다. 아직 실행·raster·새12쪽 시각 검토를 수행하지 않았다.

승인의 근거는 저장소 AGENTS.md의 사용자 정책이다: “An increase of exactly 50 percent or more requires separate approval.” 같은 문서는 임시 증가를 이전 임시 ceiling이 아닌 original baseline과 비교하고, 종료 후 원래 ceiling을 복원하며 누적비용을 유지하도록 한다. 스킬이 중복 승인을 요구해서가 아니라 이 명시적 정책 때문에 presentation70 승인이 필요하다.

## 연구·구현 단계 상태

| 단계 | R 이론 작업 | C 구현 작업 |
|---|---|---|
|1|범위 동결|baseline 동결|
|2|source 조사|방정식–source 대응|
|3|가정 명시|전체 양의 값·부호 분리 로그 설계|
|4|선택규칙·후보 검토|분리된 main/presentation 예산|
|5|STF 결합·Jacobian 유도|23상태 Jacobian·plot code|
|6|독립 분석·source 검토|36 FD·zero·capture·3 tests PASS|
|7|적용 범위 점검|fixed-field source check PASS, 실제 bath 없음|
|8|조건부 범위 수용|저장 grid 범위, 기존 convergence 재사용|
|9|code contract 검토|독립검토 PASS_SCOPED, render 대기|
|10|부분 결과 handoff|code·data publication checkpoint, 전체 요청 PARTIAL|

근거는 theory/START_AUDIT_AND_QUADRUPOLE_CONTRACT.md, intake/github/JACOBIAN_CONTRACT.md, review/FINAL_SCIENTIFIC_REVIEW.md와 outputs/main_structural_20261029다. 표의 단계별 작업은 전체 요청 완료를 뜻하지 않는다. 새12쪽 render·시각 검증은 승인 대기다.

코드 source review는 실행·그림 검증의 대체가 아니다. 본 문서와 STATE의 대기 항목은 실제 영수증과 독립검토 이후에만 갱신한다. 공개 패키지는 allowlist만 사용하며 계정 전체 raw inventory와 private intake는 제외한다. 원시 입력은 기존PR259 경로를 참조하고 self-contained backup에는 선택 입력 bytes와 vector code를 포함한다.
