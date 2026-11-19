# T1 진행 중 발견한 절대 이온화 상태 변화

Owner consumer: `rei_bianchi scientific admission owner / AX11`.
원 DAG **10/17**, 확장 **28/88**. 계산 중간의 보존된 native checkpoint를
소비한 진단이며 새 완료 노드는 0이다.

ZERO의 597000 accepted checkpoint에서 zbar=7.29447200765866,
x_HII(T1)=0.38337934072525703이다. 기존 T0 1001점 표를 이 checkpoint의
ln(a)에 추가 선형 보간한 값과의 차이는 -0.0034936973388024484다.
PLUS의 583860 accepted checkpoint에서는 zbar=7.466521491074426,
x_HII(T1)=0.35064854042097743이고 같은 방식의 차이는
-0.003160297196567241이다. 두 checkpoint의 a가 다르므로 이 두 수를
빼서 paired response를 구성하지 않는다.

추가 T0 보간을 local PCHIP으로 바꾸었을 때 선형 보간과의 차이는
각각 -1.5402755042526195e-6, -2.700691836832192e-8이다. 이는 이 진단의
보간 방법 민감도이며 보간 오차 상계가 아니다. 실제 원래 1001개 좌표에서의
D01은 종료 후 native 이력을 소비하여 별도로 계산한다.

ZERO 원본 config와 현재 bound config를 직접 비교했다. 과학 설정의 변경은
local_target=1e-5에서 2.5e-6으로의 time refinement이고, q/IC/source,
energy16, mu8, background4096, initial_dln_a=1e-4 및 spectrum 저장 주기는
유지된다. 나머지 config 변경은 명시된 자원 cap이다. 실제 두 config 값과
checkpoint SHA256은 `EARLY_STATE_DIAGNOSTIC.json`에 보존했다.

관측된 변화 크기는 원래 empirical fraction absolute target 0.001과
비교할 필요가 있다. 현재 값은 원래 표의 query와 다른 좌표에서 얻었으므로
최종 정확도 판정을 발행하지 않는다. 다음 owner 판정은 원래 좌표의
개별 ZERO/PLUS 상태 변화와 paired 변화 양쪽을 사용한다. 작은 paired
변화가 공통 상태 변화를 가리지 않게 한다. 어느 refinement가 정확해에
얼마나 가까운지와 T2의 D12는 아직 미확정이다.

원자료: `checkpoints/ZERO_597000.txt`, `checkpoints/PLUS_583860.txt`,
`receipts/BASELINE_ZERO_ORIGINAL.cfg`, `receipts/BASELINE_REUSE.json`.
해당 파일은 이 문서를 포함하는 git snapshot으로 게시하고 native 원본은
실행 디렉터리에 그대로 보존한다. 전체 실행 raw archive와 provider 검증은
wave 종료 후 예정된 postprocessing의 대상이다.
