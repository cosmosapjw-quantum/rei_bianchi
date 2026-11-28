# BASS_HE | 독립 실측 역반응 d+d→⁴He+γ 원전과 광분해 에너지축 연결

**2026-10-30.** 후속 독립 Draft, parent BASS_HE PR120 HEAD `83596b913a08dd31496b7abbb7d5a9972fff5cc1` 불변. *새로운 실제 측정값의 계보와 정확한 물리축 변환*이 핵심이며, 기존 shape 30개나 Fermi conditional 168개의 수치 반복이 아니다.

## 1. 원전, 측정량, 추가 자료

IAEA-NDS `exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871`에서 원본 4개를 정확한 Git blob/SHA로 복원하였다. 신규 실측 출처:

- `C0122`: Whitton, Weller, Hayward, Dodge, Kuhn, *Phys. Rev. C* **48**, 2355 (1993), DOI `10.1103/PhysRevC.48.2355`. `C0122002`와 `003`은 **상대값** `(D,G)He4,,DA,,REL` 총 14행(입사 d lab kinetic 30 및 50 MeV). 단위 `NO-DIM`이므로 절대 포획 단면적이 아니다. `C0122004`와 `005`는 두 종류 편극 analyzing power를 각 행 2개 성분으로 담은 총 15행(20/30/50 MeV). 각 원래 포인터 `1`, `2`를 보존하고 개인적 추측으로 Ay/Ayy 이름을 바꿔 붙이지 않는다. REL 오차에는 통계 외 배경 및 우연 γ rejection이, 편극 오차에는 beam polarization이 포함된다. 소스는 background 및 finite geometry 보정을 기록한다.
- `A1256`: Weller, Colby, Roberson, Tilley, *Phys. Rev. Lett.* **53**, 1325 (1984). `A1256002` 9.7 MeV lab d capture의 **PAR,DA** 각도별 6행(편찬된 **CURVE** 값), 단위 `MB/SR`, 원본 모니터 `(d,dγ)He4,DA` 교정; `A1256003`은 부분적 편극 텐서 `20/PAR,POL/DA,,TAP` 6행(2025 편찬 추가, `NO-DIM`). 총 12행. `PAR,DA`는 무편극 전체 절대 단면적이 아니다. 편찬 각도 오차가 0.5°/0.2°로 따로 명시되어 있다.
- 위 두 독립 논문에서 EXFOR의 **실측 기록 41행**을 추가하였다. 실제 수치 scalar 성분은 REL DA 14개, 포인터 둘인 POL 30개, PAR DA 6개, TAP 6개로 **56개**다. 41행/56성분은 독립 실험횟수나 측정의 독립성 보증이 아니다.
- 이미 알려진 독립 전방 광분해 `M0011` 1978 저자 표 14개 SIG와 `M0826` 1972 구간 SIG4개를 원본 바이트 그대로 crosswalk로 연결하였다. 이 기존 18개는 신규 측정 41개에 추가하여 '59개 신규'로 세지 않는다. M0011의 E2 7행, M0826 각도 구간 9행도 기존 별도 자료이며 이번에 새로 측정된 것은 아니다.

## 2. 정확한 역반응 에너지 map

최초 상태 d_lab(T_d)+d_rest에서 `μ_d=m_dc²`, `μ_α=m_αc²`, 네운동량 부호 `(-,+,+,+)`로

\[
 s=(2\mu_d)^2+2\mu_d T_d,\qquad E_\gamma^{(\alpha\rm -rest)}={s-\mu_\alpha^2\over 2\mu_\alpha},
\]
\[
 q_{\rm cm}c=\sqrt{s/4-\mu_d^2},\qquad k_{\gamma,\rm cm}c={s-\mu_\alpha^2\over 2\sqrt{s}},\qquad Q=2\mu_d-\mu_\alpha=23.84647820\,\mathrm{MeV}.
\]

입력 질량 에너지 `μ_d=1875.61294500 MeV`, `μ_α=3727.37941180 MeV`. 역반응에서 방출된 광자의 **포획계 CM 에너지와 α 정지계 광분해 입사 에너지는 서로 다르다.** 예: T_d=30MeV에서 광분해 α 정지계의 동등 에너지는 39.018723727847MeV이다. 광분해 실험실 `Eγ`와 원래 capture `T_d`를 동일한 수치로 읽지 않는다.

| 원본 d 입사 T_lab (MeV) | α정지계 동등 Eγ (MeV) | `(q/k)^2` 순수 위상공간 인자 |
|---:|---:|---:|
|9.7|28.803787555006|11.13388036769|
|20|33.986735465364|16.53380756980|
|30|39.018723727847|18.86631132242|
|50|49.082700252814|19.97634488890|

`(q/k)^2`는 운동학 인자다. 전체 상세평형 비율은 **광자/핵 스핀 퇴화도 평균, 편극, 동일 입자 교환, 반구/전구 각도 정의와 출처의 `REL`/`PAR` 관례**를 필요로 하므로 계산하지 않는다. 미검증 공통 9/2 또는 2 계수를 임의 곱해 실험의 물리적 `σ_event`로 선언하지 않는다.

## 3. 실측 상대 DA의 near-90° suppression

원본 `C0122002`의 `T_d=30MeV`: 상대 DA(85.0°)=`0.049±0.026`, (50.8°)=`1.88±0.15`. 원본 `C0122003`의 `T_d=50MeV`: (90.6°)=`0.06±0.01`, (42.2°)=`1.60±0.10`. 따라서 `ρ=σ(near90)/σ(shoulder)`는 30MeV `0.0260638297872`, 50MeV `0.0375`. 오차를 각각 ±1배 변동시키는 직교상자(공동 확률 CI **아님**)는 `30: [0.0113300,0.0433526]`; `50: [0.0294118,0.0466667]`. 두 소스의 대칭쌍(180°−θ) 7개는 거의 정확하게 같은 보고값을 가져 **편찬/분석 시 좌우대칭화 여부가 확인되기 전에는 독립된 대칭 검증으로 취급하지 않는다.** 이 suppression은 순수 source-reported REL 차이이며 절대 event rate/ multipole 추론이 아니다.

## 4. 물리적 연결과 보류

같은 물리적 `s`와 원자핵 채널에 대한 실측 기하 비교는 이제 가능하다. M0011002 저에너지 전방 SIG 26–65MeV, M0826002 binned SIG 30–75MeV의 **에너지 지원**과 위 inverse 관측이 겹친다. 그러나 forward total `SIG`, inverse relative `REL DA`, inverse partial `PAR DA`, polarization `TAP`를 하나의 `σ` 배열로 병합하지 않는다. 상대/부분/편극 산출량 각각의 단위, 보정, 편광 계보를 원전 필드로 보존한다. Event-rate `R_event`, 열침적 `heat_rate`, 동역학/광자장 `f_γ(t,x,p)`를 여기서 생성하거나 승격하지 않는다.

상태: Central 28/88, HE physical 14/18, PR114 lowE 3/4, PR119 Angular2/3, PR120 Shape2/2 **모두 불변**. 본 source unit 2/2 scoped (S1 41행 원문 복원, S2 에너지 및 측정량 타입 맵 검증). Physical delta=0. R6/C9 distinct-author NOT_RUN, L4=false, production=HOLD.
