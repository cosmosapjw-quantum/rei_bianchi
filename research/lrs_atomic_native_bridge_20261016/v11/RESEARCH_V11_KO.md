# V11: source-free H/He 충돌·열 항 시간배치의 독립 실험 보고서

## 질문과 선행 결과

[rei_bianchi PR #172](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/172)의
V10 Native source-on 51개 이력 및 source-off RR midpoint 실험은 모두
Tgas 시간 self-difference 차수≈1을 보였다. 이는 photon birth/opacity만으로
설명되지 않으며, PR #150의 나머지 endpoint BE chemistry + thermal clock을
분리 측정할 이유다.

## 고정 물리·자료

Frozen native source PR #150 commit `6ea2b1b4b3875c9163cafc45efe720afded43fc4`;
Grackle3.4.1 원천 rate_functions.c commit
`af7939494ce65007887ada7b98d1813df6843346`.
FLRW X=ln(a/a0), a0=1/21, total-H 핵수당 stock과 eV/H thermal energy,
HI/HeI/HeII proper density, electrons x+Y(y+2z),
초기 (HII,HeII,HeIII)=(.075,.12,.03), Tgas=15000K.
source photons zero; CI/CE/FF/CMB/RR/DR microphysics는 ON.
V7 우주론 reference는 source-identical copy이고 owner Rust 파일 3개의
SHA-256은 R5 theorem에 고정돼 있다.

## 구성적 오차 식

q'=F(q)=Σ_j F_j(q). 혼합 implicit 평가
q_{n+1}=q_n+hΣ_j F_j[(1-θ_j)q_n+θ_jq_{n+1}]
의 leading defect:

δq_local=h² Σ_j (θ_j−1/2) DF_j(q)F(q)+O(h³).

각 채널을 midpoint에 놓더라도 다른 채널이 endpoint θ=1에 남으면
일반적으로 전체 전역 오차 O(h)가 지속된다. FLRW 기하의
순방향 정확 half-map은 그 자체로 microphysical O(h) 결함을 제거하지 못한다.
Thermal+chemical+escaped cooling+CMB reservoir+gas expansion work ledger는
양쪽 평가 시계가 일치하도록 구성했다. conservation identity는 시간 차수의 증거가 아니다.

## 실제 샌드박스 계산

원본 C literal table 96 temperature rows×17 coefficients의 최대 상대오차
2.8410045294244635e−14. 새 환경에서 frozen native owner source 세 파일의
SHA와 V7 ref Git blob 확인. `pytest` 41/41 PASS. 저장된 C8 실행
144개 행을 전수 읽고 uniqueness/finite/energy 검사, 파생 case views
생성 후 merge를 다시 수행해 원시 aggregated JSON SHA가 동일했다.
첫 전체 144-case 시도는 sandbox 시간 상한으로 중단됐고,
실제 완료 증거는 3개 독립 48-case 실행에 한정한다.

| case | N128 BE \|ΔT\| [K] | CE만 midpoint [K] | 모든 항 midpoint [K] | 개선율 | p_all(N128→256) |
|---|---:|---:|---:|---:|---:|
| native density, Xend=1e−5 | 2.322904e−4 | 6.907587e−6 | 8.858478e−10 | 97.026% | 1.8725 (roundoff 접근) |
| native density, Xend=1e−4 | 2.1696993e−2 | 6.436818e−4 | 9.287342e−7 | 97.033% | 1.9985 |
| density×5, Xend=1e−5 | 5.401554e−3 | 1.344059e−4 | 1.180124e−7 | 97.512% | 1.9996 |

가장 작은 X 구간에서 원래 native V10 N128 온도와 Python source-free
BE endpoint 차이는 4.3146428652e−9 K. 이는 단일 endpoint numerical
parity이며 Rust V11가 실행됐다는 뜻이 아니다.

저장된 144행의 최대 에너지 ledger residual은 4.4408920985e−15 eV/H.
BE/CE-only/thermal-only 시계는 전역 1차에 접근했고 all-midpoint는
두 비강성 분리 조건에서 약 2차였다.

## 과학적 수용

PASS_SCOPED: Grackle 원본 rate identity, 독립 source-free Radau 비교,
CE time-clock perturbation response, 양수성/종수/에너지 bookkeeping,
복원된 Python 테스트 및 stored C8 evidence.
HOLD: V11 native Rust component-clock causal attribution,
원래 source-on 전체 2차, 실제 cosmological EoR, Case B photon retransport,
signed Bianchi, uniform stiff accuracy.

실제 native owner Driver::fixed_step의 collisional/thermal 항별 O(h)
오차를 인과적으로 입증하려면 NCP에 격리된 original owner 동일 입력
Rust 제어군을 실행해야 한다. `CODEX_NCP_HANDOFF_V11_KO.md` 참조.

## 관련 원문

Smith et al., *Grackle: a chemistry and cooling library for astrophysics*,
MNRAS (2017), https://doi.org/10.1093/mnras/stw3291.
Anninos et al. (1997), https://arxiv.org/abs/astro-ph/9608041.
Norman et al. (2015), https://doi.org/10.1088/0067-0049/216/1/16.
해당 문헌은 충돌·원자물리 방법론의 배경이며, 이 V11 코드의 2차 수렴 인증은
직접 수행한 별도 Radau 계산에 근거한다.
