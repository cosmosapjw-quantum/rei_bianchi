# 다음 대화 스레드 handoff

```text
$physmath-research-loop, $exa, $scispace, $wolfram을 사용해 BASS_HE→rei_bianchi 연구를 이어줘.
먼저 새 대화/branch/GitHub repo/Drive·Dropbox backup과 NCP 결과의 delta를 확인해.
읽을 수 없는 대화나 partial 목록은 coverage에 명시해. 이미 완료된 단계의 복구 보고로
끝내지 말고, 확인된 새 의존성을 대상으로 다음 구성적 이론·코딩 연구 단위를 실행해.

완료된 현재 단위는 HE31_ELECTRON_DONOR_20261021이다.
Repo https://github.com/cosmosapjw-quantum/BASS_HE
PR84 https://github.com/cosmosapjw-quantum/BASS_HE/pull/84 (draft, PR83 위 stacked)
Branch research/he31-electron-donor-thomson-20261021
과학 구현 pin 1c8a56aac89d0e40ede8770009f80ebca40a4d2c
Unit research/he31_electron_donor_20261021
R1–R10/C1–C10은20/20 scoped 완료, pending stage0.
최종 P2 archive SHA e7a01a46b95ae30820bde7a46a6e94f920474a6e05574b188bb084051b51e577,
2,832,001bytes; Dropbox id:BSpOijBcT10AAAAAAD_hjw, Drive 1-3utJjmUyFlzhXymeCcgOurJ02ruzoxC 양쪽completed.
P1 Drive UNKNOWN은 이력으로 보존; 새 원격 전체 GET/hash 검증은 수행하지 않았음.
최종 delivery metadata는 이 branch의 delivery/PUBLICATION.json, P1/P2_ACK.json,
DAG.json, RESEARCH_LOOP_LEDGER_KO.md를 읽어.

HE31에서 완료:
1) strict H/He donor census(ne=nH*xHII+nHe*(xHeII+2*xHeIII)), unit/frame,
   immutable source SHA, ln(a) comoving-ne PCHIP, exact zero와 구간 이탈 거절.
2) 원본 canonical quadrature를 바꾸지 않은 prepared FV evaluator.
3) 기존 full40 photon-only Thomson receiver + target-H tau 진단1,
   matter/photon/neutrino signed stress 별도 저장.
4) 실제 복원 R15/HG97-B donor z20→4 on/off2와 reference1 완료,
   네 그림, 독립 코드·물리·결과 검토, light contracts, completed reuse worker0.
5) NCP pilot18_on 및 joint175_on 설정과 run_ncp.sh, 자동 저장결과 그림 코드 준비.
   HE31 NCP 실행 결과는 아직 없음. 새 결과가 생겼는지 먼저 확인할 것.

실제 donor identity 96661134c04f69c67188863e585d831f61e090ac0fdc05dda7e977f1810d9eaa.
원본 history SHA 93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4.
16,385행, R15/HG97 CaseB Q closure, HII+HeII, HeIII0, residual electrons 없음.
source FLRW와 target background가 다르며 mean a의 일방향 처방이다.
이 작은 donor control을 완전한 native H/He feedback으로 서술하지 말 것.

실제 on/off IC=(Sigma_F .003,P_m +.0003,P_r -.001), z20→4:
tau_on=.03724155220658596, Sigma_on=.00013890261117025876,
Sigma_off=.00013717105385392087, ΔSigma=1.731557316337896e-6.
|Pgamma|3.29049% 감소, |Pr|1.94676% 감소, Sigma1.26233% 증가(이 한 사례).
reference parity 최대 전체 state 절대차1.8030021919912542e-12.
초기 NumPy JSON 실패2개와 clock rounding 기준 실패1개는 보존됨;
수정 영향 범위만 재확인했고 solver tolerance는 그대로임.

기존 HE30은 완료된237개 z20→2 궤적,4그림,20단계 scoped 완료다.
HE30 PR83, latest e173f373cd481864d0395e3a7a76520615a80e1a,
scientific snapshot d3505c4c01686d44b3095852df87b0f5df2bd400.
완료 baseline237을 다시 적분하지 말고 source/identity가 같으면 재사용해.
REI D8 PR216=1f32cc442ebde284bbb944455ba96066c9e0e055의4late sign bracket은
저장 표본 bracket이며 정확한 event root가 아님.

이번 intake에서 새 ACCEL02 NCP archive ad92f4207a6845a0326a095cb904792b6d34bf0654f7148fe3c530b47f5e2817를 발견:
실행 source231df3ab717dbc112f63b77953f64def08e9bcb5, fetched d669298f05286728453840da46cae958a3709456,
custom5×2steps a=.1999→.2; 기본729는 REUSED_ALL/jobs0. HE31/z2 HHe 결과가 아님.
PR199는 eb8042b729051f4700bd5d88d6781c4620009bcb로 전진했지만 D8 게시 delta이며
axbi source/driver의 z>=4 guard 및 PR147 kernel은 그대로였음.

다음 핵심 연구 의존성:
실제로 z20→2를 지지하는 H/He ionization donor와 z<4 emissivity/thermal/HeIII
가정을 정식 채택·생성하는 한 연구 단위를 잡아. 현 source generator의 z>=4 guard를
단순 삭제하거나 기존 z4 donor를 extrapolate하지 말 것. 새 donor가 확보되면 HE31
prepare_donor.py axbi 및 campaign.py prepare --z-end 2로 같은 consumer를 사용 가능.
가능한 이론·코드 수정은 ChatGPT sandbox에서 완료하고 push해서 NCP에는 실행만 넘겨줘.

운영: NCP64CPU/128GiB에서 다른 session을 종료하거나 전체 중지하지 말고 실제
headroom+공통 lease로 나누어 실행. 기본 max64/reserve2CPU16GiB/native thread1.
상세 benchmark·무변경 전체 재검증은 불필요. 새 실패는 보존하고 영향 범위만 검증.
매 단계 DAG·백업·게시 상태, 실제 provider ACK와 과학 완료를 구분하고,
Codex handoff 및 다음 thread handoff를 본문에서 복사 가능하게 제공해.
```
