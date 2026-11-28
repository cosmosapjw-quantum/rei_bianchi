# QUARTIC12 독립 비작성자 검토 — 실행 전

**판정: PASS_PREEXEC_SCOPED. 차단 결함 0, 요청한 수정 0.** 실제 S05 게시와 불변 실행 pin을 만든 후 root GO로 단 한 번의 새 캠페인을 진행할 수 있다. 이 판정은 계산 결과의 통과나 과학 노드의 최종 admission을 뜻하지 않는다.

검토자는 새 이론·구현을 작성하지 않았다. 새 과학 모듈 import, 테스트, 최적화, CAS, 그림 생성 및 이전 작업 재실행을 모두 하지 않았다. 계약, 자족적 이론, 실행 계획, 여섯 Python 파일, CAS 입력과 근거 문서를 읽고 수학 및 byte identity를 확인했다. 본 보고서와 JSON만 작성했다. 이후 실제 결과·CAS·그림·중앙 메타데이터 검토는 같은 단일 검토의 연속이다.

## 과학적 검토

1. **포함 상자와 정규화 하한.** 46°,61°,87°의 z=cos²θ 간격 1/5와 관측 창 [0,1]에서 Lagrange 전개가 (75,150,75)의 계수 상계를 준다. B=160은 참 가족을 포함한다. 87°의 L*=7/50, |f′|≤6B와 δ=L*/(12B)를 이용한 적분 하한 Dmin=49/4,800,000도 맞다. 참 가족의 비음수성이 나머지 적분의 하한을 보장한다.

2. **Signed data와 positivity sandwich.** 독립적인 z,z² 포함구간의 midpoint 오차를 B로 제한한 epsilon은 계수 부호와 무관하다. inner 수축과 outer 확장의 부등식 방향, endpoint 변수 제거, 중복 행의 더 강한 RHS 선택이 일치한다. 각 cell의 quadratic Bernstein controls는 충분조건, nodal positivity는 필요조건이다. N=1,4,16의 중첩 방향과 chord 기반 −max(b2,0)/(4N²) 하한도 맞다. THEORY는 고정 data 수축으로 생기는 경계 배제를 refinement만으로 제거하지 못한다는 한계를 명시한다.

3. **정확한 endpoint cone.** q(1)=0이면 q=(1−z)[b0+(b0+b1)z]이며 정확 조건은 b0≥0, 2b0+b1≥0이다. 구현은 세 계수 상자 및 Dfloor까지 모두 두 변수로 변환한다. 에너지마다 한 번만 계산한다.

4. **완전한 정점 열거와 독립 reader.** bounded polytope의 정점은 낮은 차원으로 퇴화해도 r개의 독립 active normals를 갖는다. 모든 active subset을 exact inverse로 조사하고 전체 부등식으로 필터링하므로 열거의 완전성 주장이 성립한다. matrix 공유는 RHS별 검사를 유지한다. JSON reader는 저장된 exact scalar certificate를 확인하며 두 번째 최적화 또는 별도의 완전성 증명으로 과장하지 않는다.

5. **Signed moment와 ratio bounds.** 계수가 음수일 때 moment 끝점을 바꾸는 구현이 필요하며 실제로 반영됐다. numerator 하한은 concave, 상한은 convex다. λv D(v)/D(b)의 양의 가중치로 Jensen을 나누면 요구한 정점 극값이 성립한다. inner의 min-upper와 max-lower는 참 극값에 대한 attained-witness bounds다. 전체 attained range와 같다고 주장하지 않는다. FULL=1은 outer만 있을 때 조건부 값이며 존재 증명이 아니라는 점도 THEORY에 명시돼 있다.

6. **물리 구간과 실패 의미.** raw outer 범위가 [0,1]과 만나지 않으면 raw를 보존하고 physical_range=null 및 EMPTY_PHYSICAL_INTERSECTION을 저장한다. inner witness까지 있으면 검증 모순으로 실패한다. outer 공집합 또는 특정 quartic 배제를 물리적·보편적 no-go로 확장하지 않는다.

## 실행·근거 검토

여섯 새 Python 파일은 기존 STATIC_SYNTAX의 SHA256와 일치한다. 다섯 상속 모듈은 검증된 EXFOR11 실행 source identity와 동일하다. 공식 입력 SHA256는 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f, 이전 saved JSON은 5a13b55d1e8f9a0960cddb7c8c06ae08fcb6212425d71642e41d5a311a9b2243이다. 전체 파일별 hash는 동반 JSON에 있다.

7개의 새 control method, 12개의 고정 case, 저장 certificate reader가 한 initial process에 들어간다. 중복 행 제거 전 정적 상한은 inverse attempts 27,052개, RHS candidates 81,564개다. 실제 시간이나 실제 count로 표시해서는 안 된다. runner는 실제 source commit·manifest·입력·prior evidence hash를 요구하며 science CPU120s/wall300s, plot CPU10s/wall30s, AS768MiB 및 threads1을 부과하고 whole runner와 기다린 자식 CPU를 기록한다. 외부 orchestration 범위는 분리돼 있다. 예상하지 못한 시간 초과가 발생해도 모델 변경이나 자동 재실행은 허용되지 않는다.

CAS_SUBMITTED.wl의 16개 zero identity와 12개 Boolean control을 정적으로 읽었다. 유한 Sum/Product/Part 보간식과 implicit multiplication 구문에서 식별된 차단 사항은 없다. 아직 Wolfram 평가가 실행됐다고 주장하지 않는다. 실제 provider literal 출력과 bounded invocation은 이후 같은 검토에서 확인한다.

S04 실제 commit은 513afc5049cb6defecfb1d01995e2dbe607d2ec5, tree는 c62fbb77f799b8523bf7b1ad62bfc29ff62f1924다. 새 구현의 S05 실제 실행 pin은 아직 미래 단계이며 본 검토가 대체하지 않는다. S03 즉시 readback mismatch의 원문은 보존되지 않았다는 기록을 그대로 인정한다. recovery receipt는 실제 ref·commit·parent 및 두 changed blob을 대조한 복구를 기록하며, ref retry·archive 재생성·과학 실행이 아니었다. 이를 과학 실패나 누락 없는 원문 보존으로 바꾸어 서술하지 않는다.

## 남은 동일 검토 단계와 상태

실제 S05 pin, 새 control/campaign 결과·resource receipt, CAS 출력, 실제 PNG와 해석을 확인한 뒤에만 과학 admission을 권고할 수 있다. 이후 중앙 후보의 HE 전용 metadata와 실제 publication ACK/readback을 확인한다.

현재 Local **11/16** =11 complete+1 inherited partial+3 physical open+1 pending. Central **28/88**, HE delta0. 독립 binding RHS, Gamma_thermal, Cv, species heating 및 thermal deposition을 포함한 미공급 port는 null로 남는다. Global physical completion=null, L4=false, production=NOT_APPROVED, activation=false.
