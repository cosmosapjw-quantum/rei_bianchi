# HARMONIC10 S06 — R6/C6 실제 검증과 한정된 targeted 수정 결과

최초 full suite는 immutable local `2e1de5c12311b94002ca2c786cfa4d25d050314f`,
same-tree remote `aff451808e2e2b637d8dc7d1e7b3fb031cdf8391`에서 1회 실행했다.
실제 결과는 **25 unique method, 24 PASS, 1 FAIL, error0**다. 이 FAIL을 고치거나
원 report를 덮어쓰지 않았다. 원 source tree는 `99fd138c9e4d2d731a1b0a416a9c3a89761a851c`다.

실패는 test20의 empty coincidence fixture에 양의 manual width를 요구한 assertion이었다.
독립 same-pass reviewer와 parent가 fixture만 고치도록 승인했고, 원 empty manual fixture를
exact0 control로 남겼다. polar A[0,1], B[-1,0]의 positive fixture에는 기존 arc와 모든
기존 tolerance·폭 assertion을 적용했다. 다른24 method, production, runner, plotter,
Wolfram program은 그대로다. 상세 증명과 static 변경 확인은 review의 F02·repair 기록에 있다.

실제 source publication·Drive·Dropbox ACK 이후 immutable repair local
`86098945065a4fe603fc1e3a0dfeebe4222628c2`, same-tree remote
`90830e045b2d63354ad8e7d9536fbaf850235377`, tree
`81456123c98ad26bd9563a2f0128397c08f5c7e6`에서 **test20만 1회** 실행했다.
원 external resource receipt를 prior로 전달했으며 결과는 **1 PASS, failure0, error0**다.
original exact0 control과 unchanged default/manual assertion이 모두 통과했다.

최종 검증 증거는 **25 unique method에 대한 26 evaluations**다. 원24 PASS를 변경되지
않은 dependency와 method body에 한해 재사용하고, 수정된 test20의 PASS를 연결한다.
역사적 평가 결과는 총25 PASS와 원1 FAIL이며, 26개 평가가 모두 PASS였다고 주장하지 않는다.
원 raw는 `evidence/validation/initial/`, targeted raw는 `evidence/validation/targeted01/`에
분리 보존했다. targeted reserve는 **1회 소비, 0회 남음**이며 full suite 재실행은 없었다.

| 실제 자원 | 첫 full suite | Targeted test20 | 누적 |
|---|---:|---:|---:|
| Whole process CPU(s) | 0.791723 | 0.192342 | 0.984065 |
| Whole process wall(s) | 0.816976851 | 0.265796554 | 1.082773405 |
| Outer orchestration CPU(s), 별도 | 0.003971411 | 0.004107734 | 0.008079145 |

누적 CPU20s·wall60s 한도를 통과했다. process당 AS512MiB·thread1을 적용했고 예산을
초기화하거나 이전 단위에서 옮기지 않았다. whole process CPU에는 bounded runner의
startup/shutdown과 waited children을 포함한다. outer 최종 metadata serialization과
interpreter startup/shutdown은 재귀 계측하지 않는 기존 측정 범위를 유지한다.

수정된 default coincidence 폭은 **5.5063741233403325e-15**이며 2^-40보다 작다.
manual delta1/16 폭은 **0.02421728950198976**, polar bound는
**0.041666666666666664**다. positive manual gap과 실제 폭 한도 assertion이 통과했다.
이 결과는 manual delta에 default epsilon을 일괄 보장하지 않는 기존 계약과 일치한다.

도표용 `evidence/SAVED_PLOT_DATA.json`은 원 saved JSON들을 읽어 기계적으로 조립했다.
원 orientation17·native3·nonseparable·stress 등 모든 다른 dataset을 유지하고
width_rows의 default/manual_1_16 두 row만 targeted 결과로 교체했다. 원 empty width
row는 assembly provenance에 따로 보존했다. 각 dataset에 raw source JSON 경로와
SHA256을 연결했고 original validation FAIL key도 유지했다. 이 조립에는 scientific
import·function call·수치 재계산이 없었다.

S06은 검증 work product 완료다. CAS, saved-only plot과 같은 independent review pass의
actual result 심사는 아직 pending이며 scoped scientific admission은 확정하지 않았다.
manufactured declared law·exact stored mass 범위를 유지하고 thermal binding과
production을 승인하지 않는다. local9/14·중앙28/88, HE delta0, birth_pool=UNASSIGNED,
global physical completion=null, L4=false, production=NOT_APPROVED다.
