> Historical live draft; current terminal result: REPORT_KO.md.

# PR171 다음 READY: 실제 age64 실행 기록 (초안)

원 C9 계약과 공개 소스35d9747a/57533355의 MD14/BB50k·Grackle Case-A·q0·8000K 조건을 유지한 새 제한 실행이다. 코드·허용오차를 변경하지 않았다. 소유자가 직접 실행과 새1800s allocation을 승인했다. 원 R9/FULL005 allocation과 비용은 유지한다.

## 현재 관측

관측UTC: 2026-10-18T03:17:43.039976+00:00. supervisor29828과 reference29829/native server31351를 관찰했다. 현재age64 reference RUNNING, elapsed515.1835449390003s, treeRSS112144384bytes. 아직 완료/수렴 판정이 아니다.

## 출력과 해석

새 결과는 같은 8GiB·reference600s/200000RHS·native300s 제한 안에서 실행한다. 첫 terminal 실패에서 다음 command를 시작하지 않는다. 원 solver 내부 trial rejection·복구 정책은 그대로이며, controller 재시도는0이다. 원 native matrix 공통 mesh는8/16/32만 포함하므로 age64 native 지원 여부는 별도 결손이다.

저장된 accepted gas좌표를 원 positive_native::gas_decode와 HHeModel EOS로 해독한다. 실제 clock은 원 setup의 birth_times_s를 사용한다. 재적분·새 원자 rate·helper replay는0이다. 기존age32 endpoint에서 이 해독의 가스4성분 차이는0, 온도 차이는9.094947e-13K였다. 이는 후처리 확인이며 새 물리 검산이 아니다.

H/He-only baryon정규화, 실제 시간/온도, chronology와 정확한zero를 보존한다. D/다른 isotope를 가짜zero로 추가하지 않는다. 전체 target 구간을 못 마치면 prefix를 명시하고 endpoint·Gamma·heat·paired native 오차의 결손을 그대로 둔다. 새 과학 승인NOT_ISSUED, 전구간 EoR/absolute-IVP/tail/continuum-age 및 native-time HOLD 유지.

최종 command/exit/wall/CPU/RSS와 그림·보고서는 terminal receipt 수거 후 갱신한다.
