# 다음 ChatGPT 연구 스레드 handoff

```text
$physmath-research-loop를 사용해 HE32의 완료된 pilot에서 이어가라.
Exa/SciSpace/Wolfram은 이미 문헌 탐색, 원표 확인, 보존량 및 고정밀 율 검산에
사용했다. 현재 단원의 workflow는 user skill 1.0.0, approval 0.2이다.
진행 중인 단원의 버전을 임의로 바꾸지 말라.

repo cosmosapjw-quantum/BASS_HE
branch research/he32-sandbox-primordial-pilot-20261021
PR https://github.com/cosmosapjw-quantum/BASS_HE/pull/85
unit research/he32_sandbox_primordial_20261021
과학 코드·결과 증거 기준 commit (P3): 8d32c9944acffbeed5dc98325d283bf0c3b506f0
게시 영수증·완료 DAG가 포함된 복원 기준 commit (P4): 9179848428510efcc88c2b5da72efc9a71ef2182
자료 열람용 checkout은 P4 또는 그 이후의 문서 보완 commit을 사용한다.
P3_GIT_READBACK.json / FINAL_PUBLICATION.json은 P4에서 추가되었으므로
과학 기준 P3만 checkout한 뒤 그 게시 영수증 파일을 찾지 않는다.
최종 코드·SVG·요약·증거 commit은 delivery/P3_GIT_READBACK.json을 읽어 확정하라.
원자료394NPZ+receipt+PNG는 검증된 전체 archive에 있다:
BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz
SHA256 27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a
Dropbox ID id:BSpOijBcT10AAAAAAD_hsw
Git의 delivery/DATA_DELIVERY.json으로 전달 경로를 확인하라.
후속 게시/백업 ACK는 delivery/FINAL_PUBLICATION.json 및 delivery/FINAL_BACKUP_ACK.json을 읽어라.
과학 executor SHA256:
99f4a0e248d853d641393d78bcc330c4b3913ad1da1b326219e3fa3f60375314

완료 상태:
최적화 O.C1–10 → 물리 P.R1–10 → 코딩 F.C1–10을 수행했고,
392개 nominal + 2개 L24 guard가 평균 z20→2까지 완료됐다.
PNG/SVG 그림 6개, 21개 isotope/ion population, 8개 핵종별 전자 census,
성분별 shear budget이 있다. source/runtime/input/NPZ 해시는 CATALOG와 각 receipt에 있다.

먼저 README.md, RESULTS_KO.md, DAG.json 및 독립 물리 readback을 읽어라.
완료된 동일 과학 조건을 새 라벨로 재적분하거나 상세 benchmark를 기본 작업으로
삼지 말라. 새 실행 결과의 조사는 이전 intake 이후 변경분부터 시작하라.
조회할 수 없는 대화는 확인했다고 쓰지 말라.

핵심 결과:
Sigma(z2) max .0325437252084, Pi_m max 2.84694755335e-5,
Pi_r max 6.99521107829e-4, signed shear 반전 43개 case.
tau(z20→2)=.0531386800700–.0532075626248.
9개 분율을 21개 population으로 정확히 lift한다.
전체 coupled state는 52개이며, 대응하는 unreduced 표현은 97개다.
state 차원 감소를 실측 speedup으로 바꾸어 주장하지 말라.
source budget residual은 1.7391e-9, charge-simplex 오차는 4.1078e-15이다.
L16/L24 guard 2점은 전체 domain의 엄밀한 오차 증명이 아니다.

물리 범위:
Frobenius Sigma=sqrt6|s|/H; Pi_r=|P_gamma+P_nu|이며 부호를 합산한 뒤 norm을 취한다.
Matter stress는 nonbaryonic fm=.1 sector의 것이고, gas pi_b=0은 추가 closure다.
8개 핵종 n,H1,D,T,He3,He4,Li6,Li7의 21개 원자 전하 상태를 추적한다.
모든 불안정 isotope, 음이온, 분자를 포함했다고 주장하지 말라.
Tgas는 20000 K, UV는 5.392–60 eV 및 E^-2.5이다.
ΓHI=1e-12 expit((6-z)/.3), photo + case A RR을 사용한다.
CI/DR/CX와 열·광원의 자기일관성은 포함하지 않으며, 그 누락 오차가 작다고 주장하지 않는다.
n=T=0, Li III/IV=0은 선택한 IC/support 아래의 결과다.
19개 핵반응은 registry와 조건부 freezeout 감소로 다루며 fully reactive 실행은 아니다.
BBN 중앙 조성은 별도 시나리오이며 receiver cosmology에 대한 재보정이나 covariance는 없다.
z는 평균 1/a-1이고, 경과 Gyr는 z20 이후의 시간이다. 방향별 관측 redshift와 구별하라.

복구 이력:
원 실행 394개 IVP가 완료된 뒤 Drive upload의 장기 대기와 scratch reset으로
원 NPZ가 사라졌다. Git P2 및 Dropbox P1/P2, 26개 snapshot을 SHA 검증하여 복원했다.
원 COMPLETE receipt 394개를 보존한 채 동일 identity로 artifact-loss recovery
394개 IVP를 수행했다. 전체 archive로 전달하는 NPZ는 실제 복구 실행 파일이다.
원 NPZ의 byte 복원으로 표시하지 말라. Drive 결과는 UNKNOWN이며,
검증된 Git/Dropbox 결과와 구별하라.

후속 연구:
새 DAG에 의존성을 명시하고 다음 중 필요한 범위를 선택하라.
(A) baryonic anisotropic stress
(B) 열·광원의 자기일관성
(C) CI/DR/CX 및 고에너지 UV

기존 pilot은 완료되었으므로 그림과 데이터를 전달하는 데 새 IVP는 필요하지 않다.
Git만으로는 NPZ가 없으므로 README 절차대로 archive의 results를 별도 디렉터리에
복원한 다음 run.sh plot --out <복원된 results>를 사용하라. Git 문서를 archive의
이전 게시 문서로 덮어쓰지 말라. clean Git run은 자료 복원이 아니라 신규 적분이다.
샌드박스에서 가능한 설계·코딩·가벼운 검증을 완성하고 게시하라.
NCP 64 CPU / 128 GiB는 실제 가용자원과 shared lease 안에서 사용하고
다른 작업을 중단하지 말라. 매 단계의 backup/publication/progress/next DAG를
구체적인 receipt로 기록하라. 최종 Codex handoff와 다음 대화 handoff를
복사 가능한 형태로 제공하라.
```
