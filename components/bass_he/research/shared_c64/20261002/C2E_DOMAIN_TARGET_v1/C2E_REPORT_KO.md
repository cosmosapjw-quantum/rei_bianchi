# BASS_HE C2e: 충돌 영역과 spectral target 계약

C2e의 **정의·유도 단계는 완료**됐다. 판정은 `SCOPED_DOMAIN_MAP_AND_SPECTRAL_TARGET_DEFINITIONS_COMPLETE`, 독립 검토는 `PASS_IN_DEFINED_C2E_SCOPE`다. 완료 범위는 source authority 회수, 조건부 궤적→R 영역 사상, 서로 다른 spectral target의 정의, UA gap 장애의 유도와 다음 구현 계약이다. 실제 production 충돌 영역·유한 R 외부 gap·연속공간 오차 인증은 미해결이며 전체 C2를 닫지 않았다.

## 회수한 물리 입력

원 사용자 계약과 고정 Git revision의 관련 자료를 확인했다. 문헌별 에너지 좌표에 관한 기존 ledger는 계승한 근거로 표시했고, 개별 논문을 이번에 다시 검증했다고 하지 않는다.

| 항목 | 확인된 내용 | 아직 고정되지 않은 내용 |
|---|---|---|
| 조사 에너지 | 0.5·5 keV/u 및 주변 source-native energies | 공통 lab/CM frame, u 정규화, isotope·질량, 연속 production energy 범위 |
| 핵 궤적 | 전자모형 고정 후 직선·Coulomb/Rutherford·고전 결합 운동 비교 | production 궤적 선택, coupled force law·초기조건 |
| 공간·시간 범위 | small-R·최근접·large-R 및 small-b·long-tail 검증 요구 | 유한 b 구간·time/z 창·production R 양 끝점 |
| 출력·모형 | D1 최소 g/e/bright 3상태, 정당화된 fourth state; 이후 shell/subshell·return 확장 | 전체 rank-5·6을 D1으로 자동 대체하는 결정 |

기존 REAL/EXTENDED support, legacy pilot의 b 표본, DR9A의 head-on 거리 proxy는 production cutoff가 아니다. 원 계약도 support mask를 diagnostic only로 한정한다. 전자 charge-center O와 핵 질량중심·에너지 frame 역시 다르다. 근거와 원문 행 번호는 `source_notes/DOMAIN_AUTHORITY_KO.md`, `DOMAIN_AUTHORITY.json`에 있다.

## 새로 정리한 수학적 결론

직선 모형 R⃗=(b,0,vt)에서는 R_min=b이고, 유한 [−T,T]의 반경 범위는 [b,√(b²+v²T²)]다. 반발 중심퍼텐셜 U=K/R를 별도로 채택하면

\[
R_{\min}=\frac{K}{2E_{\rm cm}}+\sqrt{\left(\frac{K}{2E_{\rm cm}}\right)^2+b^2}.
\]

두 모형의 head-on 극한은 다르다. bare 핵 K=2κ 모형은 neutral H entrance의 screened electronic energy surface와 같지 않으므로 이 식에 기존 proxy 숫자를 끼워 넣지 않았다. 에너지 frame 변환, 각속도 부호, 핵 공통scalar와 continuum threshold, finite-window·impact-tail 오차의 구분은 `math/COLLISION_DOMAIN_DERIVATION_KO.md`에서 유도했다.

정적 전자 문제의 target은 다음처럼 구별한다. 한 전자 spinless 모형이며 He n=2는 hydrogenic He⁺ 전자 shell이다.

| 대상 | 차원·구조 | 확보된 의미 |
|---|---|---|
| 기존 g+real bright pair | rank 2; m=0 및 real cosφ sector의 각각 최저 상태 | 지정한 상태와 coupling의 기존 수치 검증. incoming H1s는 미포함 |
| H1s+He⁺ n=2 cluster | rank 5; m=0 세 개, m=±1 각 한 개 | 큰 R에서의 해석적 cluster. 유한 구간의 외부 gap은 미검증 |
| 위 cluster+ground | rank 6 | 원자 채널 embedding 후보. 6채널 dynamics 정확도 인증이 아님 |
| planar-even 축소 | 조건 충족 시 cluster rank 4, ground 포함 5 | 전체 generator의 reflection symmetry와 even 초기상태를 별도로 요구; 이번에 채택하지 않음 |

기존 bright의 sinφ dark partner는 정확히 같은 에너지를 갖는다. 따라서 g+bright는 H와 가환하는 2차원 부분공간이지만 전체 H의 에너지 Riesz projector는 아니며, 유지·제외 block 사이의 spectral distance는 0이다. **이 사실은 기존 두 상태 coupling의 수치 검증을 무효화하지 않는다.** 그 검증에는 해당 symmetry sector 안의 상태 동정이 필요하다.

UA 극한 H_U=−ℏ²Δ/(2m_e)−3κ/r에 대한 norm-resolvent convergence와 H_R≥−9E_A/2를 명시적으로 유도했다. UA shell은 E_n=−9E_A/(2n²), 차원 n²다. 여기서 다음 조건부 장애가 나온다.

> 전체 H의 bound-spectrum rank-5 Riesz projector가 exact ground를 제외하면서 continuum까지 포함한 외부 gap에 R↓0에서 균일한 양의 하한을 갖는다는 세 요구는 양립하지 않는다.

균일 gap은 선택 spectrum이 threshold로 도피하는 것을 막고, norm-resolvent limit는 완전한 UA shell을 선택하도록 강제한다. Ground를 제외한 shell 차원 4,9,16,…의 합으로 5를 만들 수 없기 때문이다. Ground를 포함한 고정 rank 6에도 같은 counting 장애가 있다. 구체적인 finite-R adiabatic correlation을 추정해서 얻은 결론이 아니다. 반면 양의 R_min을 갖는 compact interval, symmetry-sector continuation 또는 Q 공간을 보존한 dynamics는 이 명제로 배제하지 않는다. 자세한 증명과 가정은 `math/SPECTRAL_TARGET_DERIVATION_KO.md` §§2–7에 있다.

내부 level crossing과 외부 gap closure도 분리했다. 내부 퇴화가 있어도 전체 cluster는 안정할 수 있으므로 U(k) frame과 물리적 overlap의 polar transport가 필요하다. Ritz gap은 연속 연산자 외부 gap의 하한이 아니며, L² projector 오차만으로 비유계 L_y=r×p 관측량의 오차를 인증할 수도 없다. weighted derivative/tail 또는 적절한 observable bound가 별도로 필요하다.

## 검증과 실행 범위

계약 검사기의 manufactured 의미 검사 **15개 통과**, 저자 정수·유리수 검사 **24개 통과**, 별도 reviewer의 독립 exact 검사 **22개 통과**다. 두 exact 검사 묶음은 서로 겹치는 항목이 있으므로 합쳐 독립 테스트 수로 세지 않는다. 해석학적 증명은 이 유리수 검사로 대체하지 않았다. source 16개 입력의 bytes/SHA와 그중 12개 고정 Git blob identity도 확인했다.

새 molecular eigensolve·과학적 quadrature·충돌 전파·Eq55는 **0회**, 기존 완료 scientific suite의 재실행도 **0회**다. 계약 검사는 frozen v1의 특정 의미 오류를 거부하는 장치이며 일반 schema completeness 또는 물리적 타당성의 자동 증명기는 아니다. contract valid와 physical launch ready는 별개이고, 현재 launch는 비활성이다. 이번에는 NCP64 성능 측정을 하지 않았다.

## 다음 단일 단계

다음 node는 **C2F_SYMMETRY_COMPLETE_CLUSTER_PROJECTOR_IMPLEMENTATION**이다. 여러 m-sector 상태와 제외 spectrum의 guard states를 구별하는 인터페이스, full-energy target과 symmetry-block target, 공통 Hilbert 내적에 의한 principal angles·polar transport를 구현한다. 먼저 manufactured 내부 퇴화·외부 gap closure·누락된 축퇴 partner·작은 overlap singular value를 검증한다.

그 이후의 physical reference pilot에는 exact R set·target multiplicity·basis/box·guard-state 수·projector/gap 기준·실행 예산을 별도 등록해야 한다. `contract/C2F_PREREGISTRATION_DRAFT.json`은 이 입력을 null로 보존하며 physical launch를 켜지 않는다. 궤적과 독립적인 전자구조 reference pilot은 그 자체의 명시적 계약으로 production domain 선택 전에 진행할 수 있다.

원래 DAG의 F1은 C2·D1·D2·E1·E2 이후다. F1의 완료를 C2의 모든 구현 작업의 선행조건으로 바꾸지 않는다. 조건부 domain API를 지금 고정하고 실제 collision coverage 판정은 미해결로 남기는 방식으로 이 순환 대기를 피한다. D1을 선행 해제하지는 않는다.

정확도 보존 Fortran binary64/OpenMP/SIMD+명시적 OpenMPI, 실제 topology/memory preflight, no-fast-math, reference parity 정책을 후속 계산에도 유지한다. C2d의 local-unbound CPU affinity 수정도 계승한다. 측정되지 않은 64코어 가속률은 주장하지 않는다.

`full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. 공개 namespace는 새 문서·계약·검사 코드와 source identity를 포함하고, 전체 묶음에는 확인한 입력 사본이 있다. 이번에 원 논문 PDF를 재배포하지 않는다.
