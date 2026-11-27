# 최신 상태 종합과 다음 연구 선택

2026-10-24 UTC 관측. 이번 단위는 HE-ANG-DDCS20-WINDOW다.
이 문서는 R1–R4의 실제 조사와 선택을 기록한다. 개별 결과의 원자료는
evidence/survey/ 및 evidence/preflight/PREFLIGHT.json에 있다.

## R1 목표와 재개 위치

사용자가 지정한 고정 인계는 rei_bianchi commit
0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17의
research/orchestration_longterm_20261023/assembly/HANDOFF_BASS_HE_KO.md다.
그 뒤 완료된 HE-X1, HE-ANG-CONTRACT와 HE-ANG-SOURCE-HEX-INTAKE의 결과를
현재 HEAD와 대조하여 재사용한다. BASS_HE 새 작업의 실제 base는
bf3c21a39b1111497ed77667d05b8a853ffe6646, 중앙 관측 HEAD는
8b6e741ceb305cb0a6fde244ee002eb5926559fe다.

HE-X1은 COMPLETE_SCOPED다. 이론·32개 fixtures·독립 검토를 다시 실행하지
않으며 X1을 경험적 각분포 보정으로 확대하지 않는다. HE-ANG-CONTRACT의
source/frame/count/event 요구 사항과 Hex의 실제 공급 파일 조사도 재사용한다.
새 의무는 실제 angular 입력 중 검증 가능한 작은 부분을 물리량으로 연결하는 것이다.

## R2 조사 범위와 최신 결과

여섯 저장소의 branch metadata pagination을 끝까지 읽었다. 이는 모든
branch 내용 전체를 정독했다는 뜻은 아니다. 최신 PR와 인계에서 관련된
source/claim/owner/budget 의존성을 추려 실제 파일을 읽었다.

| 저장소 | branch refs | 최신 관련 결과와 HE-ANG에 대한 의미 |
|---|---:|---|
| BASS_HE | 98 | PR93 Hex source intake COMPLETE_SCOPED. PR92 provider 계약과 HE38 결과 재사용. H1 ionization joint payload는 기존 조사에서 미확보. |
| bass | 269 | PR184 G1B collisionless finite Einstein–Vlasov. 새로운 collision/recoil provider로 받아들이지 않음. 독립 검토 미실행 표시 유지. |
| bass_cr | 177 | PR99 C23D 고정 T=10000 K, ne=0.14 cm^-3, lnLambda=20, 0<W<10 eV closed-box e–e 범위. 중성·ion·inelastic·finite-bath 의무는 별도. |
| WU088_HH | 151 | PHYS83 excitation 1s↔2s/2p. PHYS84 수치 WAIT, PHYS85 theory 이후 구현 대기/owner 유지. H ionization DDCS와 혼용하지 않음. |
| rec_bianchi | 149 | ADM01 입력 범위 검증과 REC-HISTORY 부분 결과. 조사 중 PR131의 delivery-only HEAD 이동을 확인. HISTORY02 owner 예약 유지. |
| rei_bianchi | 264 | ANGTHERM01 prescribed background 결과와 ANGTHERM02 예약. 중앙 HE-ANG 관측만 갱신할 수 있으며 다른 owner 계획을 승격하지 않음. |
| 합계 | 1108 | branch metadata 관측 범위. 코드·과학 결과의 완료 개수와 다름. |

BASS_HE open PR 93개와 나머지 저장소의 최근 PR 검색 결과 69개를 조사했다.
상세 참조 SHA와 PR 연결은 evidence/survey/SURVEY.json에 보존되어 있다.

대화 검색은 제공된 retrieval summary 범위다. 전체 대화 export를 읽을 수
없으므로 전 대화 본문 열람 완료로 표시하지 않는다. 검색 요약은 탐색에만
사용하고 과학적 admission은 고정 Git/원전으로 확인했다.
사용자가 첨부한 20개 파일의 이름/크기를 조사하고 관련 지침 텍스트와
9개 archive member list를 읽었다. 목록 조사와 내용 정독을 구별한다.
CMB 전용 물리 조건을 atomic DDCS에 가져오지 않았다.

Dropbox의 HEANG 검색은 27개 결과로 종료했고, BASS_HE 검색은 도구가
100개 결과/has_more=false를 반환했다. 후자는 유사 이름 folder도 포함하므로
모든 백업 내용의 과학적 검토를 뜻하지 않는다. Drive 제목 검색은 알려진
ID가 존재함에도 빈 결과를 반환했고 parent 조회는 100개 결과만 노출했다.
따라서 Drive 전체 부재를 추론하지 않는다. 이전 Hex archive는 두 provider의
정확한 ID로 metadata와 8,855,085 bytes를 다시 확인했다. 원격 SHA를 별도로
받았다고 주장하지 않는다. 이전 실패와 UNKNOWN_NOT_ZERO 비용도 보존한다.

### 실제로 새로 확보된 원전

SciSpace search_papers를 실제 실행하고 APS, 저자기관 PDF, CCC 공식 자료와
대조했다. Childers et al. (2004), DOI 10.1103/PhysRevA.69.022709의 Table IV는
E0=20 eV H ionization DDCS 40개 값을 제공한다. 독립 원전 담당자가 표 이미지를
읽고 텍스트 추출과 대조했으며 root도 표 이미지를 확인했다. 전사는 source/에
있다. 원문 PDF·전체 추출·원문 이미지는 공개 산출물에 넣지 않는다.

이 논문의 1-electron 검출 표에는 입사/검출 lab 변수와 CCC reference를 통한
절대 정규화 설명이 있다. 그러나 joint outgoing electron angles, covariance,
spin-resolved metadata, finite-mass recoil event law, 명시적 전체 적분의
event-count 정규화는 제공되지 않는다. 그 경계는 source convention audit에
근거를 남겼다. CCC/Hex가 제공하는 다른 물리 범위와 source version을 합치지 않는다.

## R3 판별 가능한 연구 단위

다음 세 후보 중 첫 번째를 선택했다.

1. 실제 Table IV의 E=3–6 eV, theta=15–120 degree 구간에서 양의 보간
   DDCS 모멘트와 지정한 오차 box의 극값을 계산한다. 입력과 단위가 확보됐고
   전자 momentum tensor/covariance로 연결되는 유도가 가능하다.
2. CCC/Hex의 raw joint amplitude 또는 event sampler를 추가 탐색하여 full
   angular provider를 만든다. 현재 확보된 파일에는 필요한 joint payload가
   없으므로 다음 입력 의무로 유지한다.
3. 동일 원전의 다른 incident energy 표까지 한 번에 넓힌다. 지금은 독립
   전사와 convention 확인이 끝난 Table IV에 한정하여 한 실제 계산을 닫는다.

판별 질문은 (a) positive interpolation의 모멘트와 PSD가 실제 구현에서도
성립하는가, (b) 정규화 모멘트의 box 극값을 독립 oracle이 확인하는가,
(c) 같은 node에서 linear-theta 모델로 바꾸면 얼마만큼 움직이는가다.
보간 민감도를 실제 실험 오차 bound로 선언하지 않는다.

## R4 표현 선택과 실행 연결

mu=cos(theta), E_eV의 tensor-product linear hats를 고정한다. 양성성,
partition of unity와 유한차원 선형 functional 구조를 직접 이용한다.
signed angular weights와 positive denominator의 ratio는 b/a 정렬의 threshold
vertex scan으로 정확히 최적화한다. 이는 출력과 관계없는 추상 구조가 아니라
실제 데이터의 민감도 계산 알고리즘이다.

R5 유도는 THEORY_KO.md, R6은 독립 원전/수학 검토, R7은 Wolfram 실제 잔차다.
R8–R10에서 조건부 결과를 판정하고 C1–C4의 입력·알고리즘·검증·예산으로
연결한다. C5–C8은 별도 coding executor, C9는 구현하지 않은 독립 reviewer다.
각 단계의 evidence와 상태는 LOOP_PROGRESS.json에서 관리한다. 같은 시점에
닫힌 단계는 하나의 실제 checkpoint/dual-provider ACK를 공유하되 각 행에
게시와 백업 상태를 명시한다. 과학 게시와 admission은 독립 검토 후 수행한다.

전체 목표의 물리적 완료율을 숫자로 추정하지 않는다. 이번 20단계 루프의
완료율과 HE-ANG parent의 SOURCE_INPUT_PENDING은 서로 다른 상태다.
