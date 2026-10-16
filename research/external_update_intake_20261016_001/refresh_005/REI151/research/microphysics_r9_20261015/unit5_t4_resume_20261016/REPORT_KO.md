# R9 Unit5: 저장 Krylov 재개와 잔차 기반 스펙트럼 진단

이 연구 단위는 실제 Unit4의 64차 결과를 재사용하는 실행기를 준비한다. 저장된 V, KV, next_vector, next_beta에서 반복을 이어가는 식과 구현 계약을 완성했고, 독립 이론 검토는 PASS_SCOPED_PREIMPLEMENTATION_THEORY, 최종 구현 검토는 PASS_SCOPED_LOCAL_IMPLEMENTATION이다. 실제 Unit4의 32→64 refinement HOLD는 유지된다. 최종 구현 검토와 실제 경량 실행의 근거는 review/IMPLEMENTATION_REVIEW.json과 results/final_run/execution.json에 연결한다.

## 기준과 물리적 대상

기준은 PR151 commit 7e07012a6d2030699c698a7209a9100bd04578d2이다. repair001의 대칭화된 적분과 frozen V6 H-action, 92개 공통 궤도 및 385112개 determinant를 그대로 사용한다. 정규화된 daughter 바닥상태 g와 parent i에 대해 Q=I−gg†, u=Qi/√W, K=Q(H−E₀)Q이다. 에너지는 Hartree 단위이다. W=0.42436081799220793은 이 유한공간의 바닥상태 직교 보완성분의 가중치이다.

실제 Unit4의 상태는 PARTIAL_WALL_LIMIT이다. 16·32·64차 내부 검사는 통과했지만, η=0.05 Eh의 32→64 spectrum L1/W=0.40797817146515336와 max CDF change/W=0.04109454416532721은 각각 기준 0.001을 넘었다. 128차 결과는 생성되지 않았다. 조건부 평균과 분산이 안정적이라는 사실만으로 분포의 수렴을 채택할 수 없다. 이를 보이는 작은 반례는 평균2·분산1이 같으면서 서로 다른 두 이산분포이며, spec/THEORY.md에 직접 구성했다.

## 재개 알고리즘과 계산 절감

1. 저장된 입력과 연산자의 대응을 확인하고 V, KV, g, u, 다음 벡터·계수를 복원한다. 이전 실행기 해시와 새 실행기 해시는 달라도 동일한 물리 연산자로의 명시적 대응을 기록한다.
2. C=V†KV와 J=(C+C†)/2를 저장 배열에서 재구성한다. 이전 16·32·64차 진단도 해당 prefix에서 계산한다. 이 단계의 추가 H-action은 0이다.
3. 실제 재개 전에는 기존 Hamiltonian 재구성 검사 3회와 저장된 KV에 대한 첫 열·마지막 열·고정 선형결합의 3회 비교를 수행한다. 모든 작용을 새 예산에 포함한다. 이 표본 비교는 전체 cache의 수학적 증명으로 해석하지 않는다.
4. 첫 신규 반복은 K v₆₅이다. 기존 64개 열에 대한 2회 완전 재직교화를 유지하고 최대128차까지 이어간다. 바닥상태 FCI와 앞선64개 Krylov 작용을 다시 계산할 필요가 없다.

따라서 재구성3+cache 비교3+연장최대64=최대70회의 새 작용으로 준비했다. 원래 기한은 2026-10-16T01:51:37.258157Z에서 만료되었다. 새 실행의 n회는 과거의 미확정 구간 [86,160]과 분리하여 총 [86+n,160+n]으로 보고한다. 과거의 하한86을 실제 최종 횟수로 바꾸지 않는다.

## 직접 유도한 오차식

복소 에너지 z=ω+iη, η>0에 대해 t=(zI−J)⁻¹e₁, m_J=e₁†t를 계산한다. E=KV−VJ와 d=u−Ve₁를 사용하면 잔차는 r=d+Et=u−(zI−K)Vt이다. 자기수반 K의 resolvent norm ≤1/η에서

B_m(z)=‖u‖‖d+Et‖/η + |(u†V−e₁†)t|,

|m(z)−m_J(z)|≤B_m(z),  |S(ω)−S_J(ω)|≤W B_m(z)/π

를 얻는다. 두 번째 항은 유한 정밀도에서 생기는 초기 좌표와 관측 벡터의 오차를 보존한다. J로 resolvent를 풀면서 E에 C를 대신 넣지 않는다.

이 식은 자기수반성과 KV cache의 정확성을 전제로 한 점별 진단이다. 현재 구현은 부동소수점 평가이므로 outward-rounded interval certificate가 아니다. ω∈[0,20] Eh의 0.01 Eh 격자와 η=0.05,0.1,0.2 Eh에서 보고하며, 기존 spectrum/CDF refinement 판정은 그대로 둔다. 현재 구현은 격자점마다 직접 잔차 norm을 평가하며 추가 H-action은 사용하지 않는다. 비용은 O(Ngrid·d·m)이다. 실제 d=385112, m=128, 6003개 (ω,η) 조합에서는 약2.37 TB 상당의 실수 E 배열 접근이 누적될 수 있고 복소 임시배열 비용도 추가된다. 실제 wall time은 측정하지 않았다. A=[d,E]의 Gram을 한 번 만들고 작은 이차형식을 평가하는 대안은 이론에 제시했으나 이번 코드에는 구현하지 않았다. 따라서 준비된7200초 안의 실제 완료를 보장하지 않는다.

## 문헌과 도구 근거

SciSpace와 Exa에서 원전 후보를 찾고 Morikuni의 Hermitian resolvent 논문 PDF, Frommer 등 및 Chen–Greenbaum–Musco의 원전 초록을 확인했다. 구체적인 재개 규칙과 위 오차식은 이 단위에서 직접 유도했다. 그림에서 값을 추출하지 않았다.

- https://arxiv.org/pdf/2002.06738
- https://arxiv.org/abs/1204.5052
- https://arxiv.org/abs/2106.09806

Wolfram의 두 실제 호출은 MCP 내부 오류로 끝났다. 외부 검산 성공으로 기록하지 않았으며 원문 오류와 요청은 evidence/WOLFRAM_ATTEMPTS.json에 있다. 대체 검산의 실제 결과와 도구 환경은 results/ 및 최종 독립 검토를 참조한다.

## 실제 샌드박스 결과

| 검증 | 관측 결과 | 근거 범위 |
|---|---|---|
| 최종 회귀·계약 시험 | 8/8 PASS; 시험 내부0.569초, 명령0.690초 | 차원최대96의 결정적 dense fixture |
| 실수 합성64차 재개 | 95차 happy breakdown; 신규31회; 연속 실행 대비 spectrum 최대차0 | 보완공간95차를 모두 채운 결과; 128차 실행을 뜻하지 않음 |
| 복소 Hermitian32→64 | 신규32회; spectrum 최대차3.121808367367862×10⁻¹⁴ | 직렬화·복원·연장의 일치 |
| cache 재압축 / 표본 비교 | 추가작용0 / 3회 | 이전64회 반복 없음 |
| 감독된 합성 worker | exit0; 37회=3+3+31; 약0.363초 | 실제 CLI worker 흐름에 toy 입력·재구성을 주입 |
| 독립 유리수 검산 | 잔차·scalar error 항등식 exact; 14593/21250 ≤109/50 | 하나의 비자명한 정확 유리수 사례와 수학 유도 |
| 실제 checkpoint·PySCF·NCP | NOT_RUN; 새 물리 H-action0회 | 실제385112차원 입력의 검증으로 확대하지 않음 |

첫 합성 worker 시험은 샌드박스 가용메모리 약9 GiB가 기존 host headroom20 GiB보다 작아서 작용0회로 중단했다. 이후 toy harness에만 headroom 검사를 끄고 작은 합성 입력으로 control flow를 검사했다. native 실행기의 기준은 그대로이다. 원래 실패·수정된 toy 검산과 각 명령의 stdout/stderr를 모두 보존했다.

합성 worker의 [123,197] 표기는 bookkeeping 동작을 시험한 가상 누적구간이다. 실제 NCP 과거 횟수는 계속 UNKNOWN [86,160]이며 이번 물리 작용은0회다.

## 채택 범위와 남은 연결

실제 약394 MB checkpoint archive는 이번 샌드박스에서 내려받거나 복원하지 않았다. 합성 legacy-format 파일의 통과와 실제 파일의 호환성은 구별한다. 실제 호환성, native PySCF 재구성, 실제64→128 및 새 잔차 진단의 실제 값은 NOT_RUN이다.

다음 물리 의존성은 실제 재개 → 64→128 refinement → T2의 에너지 정규화 continuum 및 exclusive channel 연결이다. electron capture의 별도 연산자, recoil/phase-space, 완전기저 closure도 계속 열려 있다. 이 단위의 실행기 완성으로 T4 전체가 완료되지는 않는다.

Strong no-go 채택은 없다. NG1–NG7은 새로운 배제 정리로의 확대를 허용하지 않는 범위 심사로 적용했다. 원래 refinement 실패는 특정 유한공간 계산의 수렴 미달이며 물리적 불가능성 정리가 아니다.
