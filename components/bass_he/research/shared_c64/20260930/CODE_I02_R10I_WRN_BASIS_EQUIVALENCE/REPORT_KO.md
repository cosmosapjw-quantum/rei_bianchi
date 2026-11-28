# R10I WRN basis equivalence audit

## Verdict

**`WRN_BASIS_NOT_EQUIVALENT`**: 고정 3270 rotation-active 질의에서 author WRN의 m>=0 parity-even 확률 행렬과 현재 clean-room signed-m + incoherent |m| collapse의 최대 원소 차이는 `0.4997281277454655`였다. 기준은 `1e-8`이다. 두 표현의 독립 step/유니터리/확률합 gate는 PASS했다. 최악 질의의 별도 DOP853 amplitude 검사도 이 차이를 재현했다.

그러나 현재 R10G 초기상태와 다섯 branch의 approach event 순서는 회전 직전에 **m=0 열만** 소비한다. 두 표현의 m=0 열은 대수적으로 같고, 전체 질의의 그 열 차이는 최대 `1.3933298959045715e-13`이다. R10H의 l=1 factor-two 경고는 전 행렬의 다른 열에 관한 것이며, 현재 shell-total residual의 설명으로 채택할 수 없다.

## Inputs and execution

- PR15 `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`; PR17 input `ce0d2a7cfbb65297d45f217ea788fc06a201e38f`.
- Author source DOI 10.17632/n43srxwdnm.1, `arseny.f` SHA256 `96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78`, lines 1913-1962 and 2033-2070 read-only.
- R10G endpoint result and original 300 Delta cache rows preserved. R10F outer table + R10G first 60 q nodes give exactly 300 rho and 1260 active branch/rho pairs. Query manifest hash is in `QUERY_MANIFEST.json`.
- Environment Python 3.12.3, NumPy 2.3.5, SciPy 1.17.0. Research source is confined to this namespace; production source/default/tolerance unchanged.
- TDD RED: 5 behavior failures, 1 pass, exit 1, no collection error in the valid RED. Final focused tests: 8/8 PASS, exit 0. An initial path setup error and a test float-equality assertion correction are retained separately as engineering records.

All 3270 active queries cover l=1,2; straight/Coulomb; CPC/author cutoff; E=0.5/5 keV/u. Author-even low/high 최대 차 `2.645658359057279e-09`; clean low/high 최대 `2.6456524748752486e-09`. 최대 유니터리 결함은 각각 `1.8252066569777614e-13` / `2.2382096176443156e-13`; 최대 stochasticity 결함은 `1.8252066524837574e-13` / `1.545430450278218e-13`. Even+odd를 원 signed collapse로 다시 조립하면 최대 차 `1.3933298959045715e-13`이다.

Worst query: Coulomb/CPC, E=0.5 keV/u, (N,l)=(3,1), rho=`0x1.9afbb98f335bcp-4`, final m=0/initial m=1. Separate full signed/reduced DOP853 amplitude 차 `7.309742140011427e-14`; DOP 확률 차 `0.4997281277455441`. Author FORTRAN 실행 결과가 아니라 정적 계수 해석을 검증한 것이다.

## Allowed two shell lanes

비동등성과 양쪽 수치 gate PASS 이후에만 저장 Delta 1260 pair를 사용해 `AUTHOR_REDUCED_SL_CPC`와 `AUTHOR_REDUCED_COUL_AUTHOR`를 계산했다. 새 rho·Delta·contour solve는 **0**. 기존 R10G 첫 q구간의 2→3 grid와 바깥 16구간 고정 GK15/G7을 사용했고, initial/final 각각 36/36 embedded PASS, 최종 max normalized error `0.0020566397505609626`, successive-grid 변화 `1.0154914991470068e-06`이다.

두 lane 모두 원 clean lane 대비 direct CORDIR shell의 material 변화는 **0/6**이다. 최대 shell 절대/상대 차는 reduced straight/CPC `1.1303091795866749e-10` / `6.948640740928907e-11`; reduced Coulomb/author `6.126388285565554e-11` / `3.079624085884478e-11`이다. Appendix-A RMS는 reduced straight/CPC `1.9757710695733708` (all-six), `1.412799752493352` (dominant n2/n3); reduced Coulomb/author `2.0125238508779555`, `1.2888567844146919`다. 원 clean 값과 수치상 동일하다. **`AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`**.

첫 shell script 호출은 0.0을 hex 문자열로 넘기지 않아 TypeError로 멈췄다. 실패 기록을 보존했고 입력 타입을 고쳐 같은 고정 rho/Delta 기록에서 재실행했다. 이 오류는 contour/Delta 호출 전에 발생했다.

## Scope

`C_S_AT/MODKG` subshell 변환은 구현하지 않았다. Author FORTRAN, 새 Delta/contour, Eq55, production 변경, CODE-I02 재감사, 56-action replay, worker sweep, L2/Krawczyk는 실행하지 않았다. 전체 행렬 비동등과 현재 reachable-subspace 동등을 분리해야 하며, 새로운 초기 상태나 event topology에는 이 shell 결론을 상속할 수 없다.

`CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.
