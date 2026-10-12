# PHYS35 실제 독립 최종 결정

**PROMOTE_SCOPED. C35-01–07 채택, C35-08–10 HOLD. fatal 0, 필수 수정 0.**

검토자: /root/joint_decision, 실제 모델 GPT-6 Astra Pro. 후보 생성·검증 설계에 참여하지 않은 별도 agent다. 같은 host/model·입력 계보의 NONBLIND 검토이며 별도 산술 backend나 독립 물리 자료 검증은 아니다. 실제 clock 기준 검토 시작은 2026-10-12 02:27:04 UTC, 판정은 02:33:12 UTC다. 이후 문서 직렬화 시간은 판정 시간과 구별한다.

## 고정 후보와 결론

[최종 후보 freeze](../evidence/FINAL_CANDIDATE_FREEZE.json) SHA256:

e297577b6b8d8e16f1841807bb28b1703c4c393e27a096fb7b9bd5b8a35e2fbb

73개 파일/5,924,395 bytes 모두 일치했다. 실행 전 45개 파일/4,770,910 bytes도 보존된다. [첫 raw](../evidence/CERTIFICATE_FIRST.json)와 replay는 각 87,023 bytes이며 공통 hash는 다음과 같다.

2157dfcf9608590b6f0f2b94be3e6558b9414048117aff9a48ab6e083ad233c2

채택 범위는 고정 source-real kernel, 서로 다른 정확한 A−=−3.2582515E−137 및 A+=−2.2748589E−137 s⁻⁴, 평균18 eV, 원 전체 저장 W±0.25 eV², 실제 W와 uniform/P4, 0≤δ≤0.001 eV다. [계약](../PHYSICS_CONTRACT.json)의 Gα=W−,α(A−)−W+,α(A+)에서 모든 양의 허용 폭에 대해

\[
1.31209\times10^{-4}\delta^4
\le G_p-G_u\le7.87027\times10^{-4}\delta^4
\]

다. 계수는 eV⁻²이며 최대 폭의 변화는 [1.31209,7.87027]E−16 eV²다. δ=0에서는 정확히0이다. 이는 결정론적 포함 구간이며 입력 오차나 점추정이 아니다.

## 주장별 판단

| 주장 | 결정 | 핵심 근거 |
|---|---|---|
| C35-01 | PROMOTE_SCOPED | 원 A·전체 W·J·source 및 prior tube 근 존재 보존 |
| C35-02 | PROMOTE_SCOPED | signed D 기울기 식과 전 경로 geometry/smoothing 오차 |
| C35-03 | PROMOTE_SCOPED | 동일 retained 기준점·정확한 기존 셀·packet 전체 덮임 |
| C35-04 | PROMOTE_SCOPED | p와 1-p의 affine 결합, 양의 분모, 계수 범위 분리 |
| C35-05 | PROMOTE_SCOPED | [Lplus−Uminus,Uplus−Lminus]의 양의 하한 |
| C35-06 | PROMOTE_SCOPED | 정확한 Peano 945 한 번, 미확인 나머지 없음, 폭0 구분 |
| C35-07 | PROMOTE_SCOPED | 실제39/39×2, raw/capture/ledger/복원 바이트 연결 |
| C35-08 | HOLD | 새 공통 A의 두 분지 정리 미완료 |
| C35-09 | HOLD | 실제 J·atomic-fit 불확실성 강건성 미인증 |
| C35-10 | HOLD | 전역 물리 승인·전체 coupled history 미완료 |

## 결정적 증명·소스 검토

[전체 유도](../contributions/theory/JOINT_BRANCH_RATIO_DERIVATION_KO.md)와 [코드](../code/certify_joint_displacement.py)를 읽었다. pW=1/D², qxW=D/D²에서 기울기는 양의 t 가중 k″ 적분이다. 하단 D<0를 곱에 그대로 두고 min/max를 적용하므로 추가 음수 오류가 없다.

기준 k와 k′는 동일 retained energy의 order0/1 primary 경계다. 문자열 identity를 직접 확인했고 두 xref가 exact reconstructed center와 다름을 보존한다. 다른 zero-width residual 중심을 혼용하지 않는다.

중심 선분 차이는 (1−t)δ+tHc 이하다. t 가중 적분에서 d/6+Hc/3을 얻는다. 평균0·공통 μ2로 smoothing 1차 항이 소거되고 이차 나머지에 ∫t=1/2를 적용하면 μ2M4d²/4다. 실제 패킷·기준점과 Taylor 경로는 기존 볼록 에너지 영역에 포함되어 전 tube와 두 근 사이 평균 기울기에 적용된다.

PHYS33 셀은 z_domain.lower/upper의 원 32등분 코드에 연결되며 생성 코드 hash가 이전 final freeze와 같다. PHYS34의 exact_rational_cell 대조도 고정 main에 있다. 확대된 Decimal z_interval을 exact cell로 쓰지 않는다. 선택 셀은 상단 endpoint0/interior30,31, 하단 endpoint31/interior0이며 닫힌 합집합이 패킷 전체를 덮는다. 선택 coefficient hash와 PHYS34 exact-cell 문자열을 prior record에 대조했다.

Peano 식은 Q=(1−z²)⁴의 네 번 부분적분과 정규화에서 얻는 정확한 δ⁴/945 식이다. 분자는 p와 1−p의 affine 끝점으로 감싸고 양의 기울기로 나눈다. ΔW−−ΔW+=δ⁴(Γ+−Γ−)의 방향이 코드와 같다. 이전 coarse 구간의 0 겹침을 새 위치·가중치 정보로 해소했다. 문헌 전체 신규성이나 입력 섭동 강건성을 주장하지 않는다.

보고서의 짧은 outward 계수는 Γ+=[0.000842416,0.00130303], Γ−=[0.000516001,0.000711208]다. gap은 raw 정확 끝점을 직접 결합한 결과다. 짧은 분지 숫자를 재조합한 더 강한 경계로 읽지 않는다.

## 실행과 검토의 한계

[실행 receipt](../evidence/EXECUTION_RECEIPT.json), [복원 receipt](../evidence/RESTORATION_RECEIPT.json), 두 실제 tool envelope·parent process·stdout/stderr·ledger를 읽었다. raw는 byte-identical, 각각39/39이며 child/tool exit0, timeout false, stderr0 bytes다. 46개 archive member는 prefreeze45개와 freeze 자체이며 원본·별도 복원 경로와 모두 같다. 공유 ledger6개도 보존본과 일치한다. 검토자는 보존 증거를 읽었고 원 child를 실시간 관측하거나 다시 실행하지 않았다.

원 입력24개는 원본과 같다. 동결73개는 모두 바이트 identity를 확인했고, 핵심 내용·원 prior proof/raw/decision/source를 읽은 범위는 [JSON 결정](DECISION_REVIEW.json)에 기록했다. 모든 과거 helper를 새로 증명했다는 의미는 아니다.

PHYS33의 과거 외부 envelope·분리 stdout/stderr 누락은 상속한다. PHYS35 capture가 이를 소급 복구하지 않는다. 새 Fraction 조합은 정확해도 원 커널 bound는 inherited Decimal/libmpdec 의미에 조건부다.

과학 추가 실행·import·새 coefficient/kernel·기존 main·generic test는 검토자와 후속 검토에서 모두0이다. first1/replay1은 SPENT, 잔여0이다. 문서 직렬화 중 JS 구문 오류1회는 실행 전 중단되어 파일·과학 변경0이며 과학 main 실패가 아니다. 기록된 prior-freeze 후처리 assertion도 metadata 형식 문제로 구별했다.

PHYS36은 조건부 J 섭동 이론의 PROPOSED_NOT_RUN 인계다. 실제 오차 출처, 섭동근 존재·tube와 margin을 별도로 처리해야 하며 새 입력·오차율·예산을 묵시적으로 채택하지 않는다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0.**

이번 판정은 범위 한정 연구 보고·닫힘 단계의 실제 독립 승격이다. 원격 publication 성공이나 merge를 주장하지 않으며 실제 후속 결과는 별도 publication receipt를 따른다.
