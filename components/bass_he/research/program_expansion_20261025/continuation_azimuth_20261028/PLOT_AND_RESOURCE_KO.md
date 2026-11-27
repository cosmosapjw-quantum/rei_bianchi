# AZIMUTH09 R8 / C8 — 저장 결과 그림과 자원 판정

## 실제 결과

이번 새 단위의 저장값 그림은 첫 실행에서 PASS다. 전체 plot subprocess CPU는
2.053974 / 8 s, wall은 2.124947346004774 / 20 s다. 종료 코드는 0이며 timeout,
수리, 재시도는 없다. 과학 import와 과학 함수 호출은 각각 0이다. 이미 완료한
KINEMATIC08, APERTURE07, PHOTON05의 과학·검증·그림 실행은 재사용하지 않았다.
그들의 결과를 읽어 근거로 재사용했으며 실행하지 않았다.

실제로 실행한 local source는 S07 `2fbe4657b480149b393c54cac6009feb4fd05ac6`,
같은 tree를 게시한 remote commit은 `4750c693cfb51433060db10ad81c8732382f3f17`,
exact tree는 `40c6184a0a4cf5ac04c1a2428015659b3709c3f8`다.
입력은 단 한 번의 S05 검증 실행이 저장한
`evidence/validation_attempt1/SAVED_PLOT_DATA.json`이며 SHA256은
`8d37a7cb3bc3ac69f06f80c4c5a1a4bc0341275fe95523cbe76c3ac2fb0ddb0e`다.

| 원본 출력 | 크기 | SHA256 |
|---|---:|---|
| AZIMUTH09.png | 114698 bytes | `7a6aad304342a72dc97d267c18e70c880c834345fafaa623dc5e6d0f9d455440` |
| AZIMUTH09.svg | 59918 bytes | `305cba8f9c243639f84152756a1d21da9841782ff1ef43337f26a8889c746add` |

PNG는 원래 생성한 파일을 단계 ZIP에 보존한다. SVG와 생성 영수증은 source에
보존한다. 어떤 출력도 다시 렌더하지 않았다. Root와 독립 검토자는 같은 원 PNG를
직접 확인했다. 네 패널의 축, 범례, 선언 측도에 관한 caption은 읽을 수 있으며
저장된 값과 의미가 일치한다.

## 네 패널의 과학적 해석

1. **회전 법칙.** A는 시작점 0의 1/4-turn sector, B는 시작점 alpha의 같은 폭이다.
   전 극각창과 정규화된 균일 mu 밀도에서 서로 다른 딸 coincidence는
   `Y(alpha)=2 max(0,1/4-|alpha-1/2|)`, `0<=alpha<=1`이다.
   한 실행에 저장된 정확 유리수 17개가 이 식과 일치한다. Wolfram의 좌표는
   반대 정렬에서 잰 상대 offset `d=(alpha-1/2) mod 1`이므로 peak 위치 표기가 다르다.
   상대 회전을 균일 평균한 적분은 1/8이다. 이 추가 평균을 고정 기하의 일반 법칙으로
   바꾸어 쓰지 않는다.
2. **구별 가능한 반례.** 반 turn을 생략하면 1/2 대신 0, 독립 검출을 가정하면
   1/2 대신 1/8, 두 assignment를 단순 합하면 1 대신 2, both-hit를 서로 다른
   딸 coincidence로 간주하면 0 대신 1이 되는 네 manufactured witness다.
   이는 저장된 counterfactual 비교이며 mutation campaign 실행 기록은 아니다.
3. **선언 native scalar 입력.** 저장된 질량과 photon energy 213, 258, 330 MeV를
   사용하되 밀도는 `rho`의 Bernstein coefficients `[0,3/2,0]`, sigma=1이고
   방위각 법칙은 명시적 `UNIFORM_DECLARED`다. 선택한 유한 sector 기하에서
   coincidence와 Hit-A가 같아 두 곡선이 겹친다. 그 coincidence midpoint는 각각
   약 0.04549154153823495, 0.04312933465472360, 0.03985114599133981이다.
   실제 interval width는 각각 약 6.456649895888889e-15,
   6.314763998323604e-15, 6.108266209958474e-15다. 원 exact fraction은 저장 JSON이
   권위 있다. 이 세 점은 empirical DCS 또는 실제 사건률 데이터가 아니다.
4. **반환된 Hit-A 폭.** 수동 delta=1/16 예의 실제 Hit-A interval은
   `[17/48,19/48]`, width=width_bound=1/24다. 같은 비교의 기본 delta에서는
   width=1/26388279066624다. 이 패널은 Hit-A를 그리며 coincidence는 두 예 모두
   정확히 0이다. 기본 sigma/2^40 점선은 수동 delta 또는 conditional ratio에
   일괄 적용되는 보장이 아니다.

## 자원 측정의 범위

전체 subprocess 수치는 Python 시작, 기다린 descendant, 그림 생성, 내부 최종
영수증 저장과 interpreter 종료를 포함한다. 바깥 orchestration CPU
0.008875835000000006 s는 별도 보고한다. 바깥 최종 직렬화·fsync 및 바깥 interpreter
시작·종료까지 재귀적으로 측정했다는 주장은 없다. Peak subprocess RSS는
61512 KiB이며 address-space cap은 **프로세스별** 512 MiB, thread는 1이다.
이 cap들을 엄밀한 모든 자손 합산 선제 CPU/memory cap으로 서술하지 않는다.

실제 환경에서는 기존 font metadata cache를 읽었다. 따라서 이번 시간은 그 환경의
관측값이고 clean-cache benchmark 또는 이전 KINEMATIC08 그림 대비 speedup의
근거가 아니다. KINEMATIC08의 7.040661/6 s FAIL과 workflow PARTIAL은 그대로다.

## 검토와 다음 전이

같은 독립 검토 pass 1에서 원 그림, 저장 input 및 source identity, 자원 결과를
확인했다. `evidence/PLOT_RESULT.json`의 visual/scientific admission PENDING은
그 기계적 기록을 만들던 시점의 snapshot이다. 이를 덮어쓰지 않고 독립
`review/FINAL_REVIEW.json` 및 root의 S09 채택 문서로 후속 판정을 명시한다.

이 단계는 R8/C8 결과를 게시하는 단계다. 현재 local DAG는 **8 complete + 1 partial
+ 1 pending + 3 physical open / 13**, 즉 **8/13**이다. 중앙의 실제 최신 `ed6a899...`
base는 **28/88**, 이번 HE delta는 0이다. 새 노드의 complete 전이는 S09의 명시적
scoped 채택에서만 수행한다. 물리 입력 세 개, global physical completion null,
L4 false와 production NOT_APPROVED는 유지한다.
