# C10 독립 판정

판정은 **국소 구성요소와 제한된 실제 경계 재시작만 PROMOTE, production은 HOLD**다. C10 구현·시험을 작성하지 않은 별도 reviewer가 최종 코드와 원 로그·JSON·NPZ를 읽고 판정했다. 기존 계산이나 시험을 재실행하지 않았다. 새 전체 역사나 BASS receiver의 과학적 채택은 승인하지 않는다.

| 대상 | 판정 범위 | 직접 근거 |
|---|---|---|
| C3 및 C2/C3 | 초기 source/IC·opacity 비교 승격 | source 최대 2.247e−15; C3/direct 1.881e−6, C2/C3 6.174e−5 < 1e−4 |
| source/redshift | 거부 조건을 유지한 국소 구현 승격 | 독립 Decimal 제조해와 source-only 공통 종료시각 비교; 최대 차이 7.013e−12 |
| 양의 absorption·photoheat | 국소 functional 승격 | 공통 양의 가중치, N/U·흡수 counter pairing, 직접 excess-energy heat 및 ABI 차이 검증, 최종 7개 시험 |
| 실제 native gas 결합 | 제한된 경계의 구현·보존 성질만 승격 | 공통 종료 1e11 s, 1/2/4 step, 경계 7개; gas RHS 84회, SIGMA 5024회 |
| checkpoint | 실제 bounded split 경계 결합 승격 | 2.5e10→5e10 s의 load 후 다음 step에서 gas/N/U/counters/R/support bitwise 일치 |

실제 7개 snapshot의 manifest와 dependency closure를 확인하고, 저장 배열에서 strict gas/photon domain, 전체 prefix, extrema, 고정 초기값 ledger를 독립 재계산했다. 불일치는 없었다. 최대 energy 잔차는 3.729308634919418e−12, number 잔차는 1.9020753347564594e−19였다. C3의 129/65 epoch normalization도 각 집합에서 재계산하여 일치했다. 이 검사는 저장 증거의 검증이며 simulation 재실행은 아니다.

검토 중 Important 결함 하나를 수정했다. 원래 absorption은 K0와 KE의 order 차이만 검사하여, 문턱 근처의 작은 photoheat KE−χK0 오차를 놓칠 수 있었다. 실제 제조 반례에서 KE 차이 2.875e−9가 통과하는 동안 heat 차이는 3.383e−6였다. 최종 코드는 incident와 attenuated 상태 모두에서 heat 자체의 fine scale, 직접 Σ(E−χ)σP, ABI subtraction과의 일치를 검사한다. 최초 반례·RED·수정 전 코드는 보존되어 있고, 최종 실제 native family는 수정 후 hash를 사용한다. Ledger 실패 전 상태를 accepted prefix에 넣던 runner 순서도 수정되어 새 실패 사례 시험을 통과했다.

남은 시간·정밀도 한계는 해소되지 않았다. 초기 source 구간 h=5e9 및 2.5e9 s는 1e−10 quadrature 기준을 위반한다. 큰 source-only 구간의 성공으로 coupled step을 키울 수는 없다. 실제 공통 종료시각 family의 9개 필드는 두 비교 모두 단일 초기 endpoint 자체를 기준으로 한 2e−6 진단값을 넘는다. 가장 큰 HeIII 차이는 1/2 step에서 0.612389, 2/4 step에서 0.361457이다.

**이 초기 endpoint 진단 실패는 전체 역사 시간 기준의 실패를 증명하지 않는다.** 원래 기준은 각 65/129 epoch 집합 전체에서 정한 field amplitude로 정규화한다. 그 역사는 계산하지 않았다. 따라서 극소 초기 HeIII 값에 sub-ppm 상대정밀도가 반드시 필요하다는 결론이나, 가능한 모든 timestep·정밀도 표현이 실패한다는 결론도 내리지 않는다. Production HOLD는 아직 닫히지 않은 시간 제어·정밀도·endpoint·전체 역사 gate에 근거한다.

Source의 전체 partition 일치 1e−12, 시간 적분의 per-cell 1e−10 검사, 얇은 birth 순간 moment의 독립 정밀도 보증은 서로 다르다. 마지막 보증을 새로 얻었다고 주장하지 않는다. Native 문턱/endpoint trace는 여전히 fail-closed이며 seed·floor·clipping·provider 교체는 없다. 제조 fixed-gas checkpoint 결과와 실제 native 재시작 결과는 구분했다. 실제 재시작 검사는 동일 process에서 저장 경계를 load하여 다음 split step을 계산한 범위이며 cold-process·adaptive 장기 운전·숨은 BDF 상태 복원까지 확장하지 않는다.

원래 Whole15.9→4, temporal 2e−6, fixed-initial energy/number 1e−9, 24-field spectral/angular 1e−3, geometry 1e−11, 65/129 자체 normalization을 유지한다. CR/RCT/secondary OFF noncompletion, 이전 C1/C2 실패, 이전 N4 범위도 유지한다. 다음 작업은 기존 과학 기준 아래 source/native 좌표 정밀도와 시간 제어를 연결하고, 그 뒤 원래 전체 역사 gate를 실제로 평가하는 것이다.
