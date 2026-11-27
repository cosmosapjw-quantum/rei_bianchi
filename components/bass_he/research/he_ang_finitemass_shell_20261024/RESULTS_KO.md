# HE-ANG-FINITEMASS-SHELL 연구 결과

## 핵심 결과

유한 nucleus 질량을 포함한 e+H breakup의 lab/COM/Jacobi 사상, 전체 에너지껍질, 양의 radial 해 전부, delta-function Jacobian, 전체 kinematic phase-space volume 및 상수 가중치 검산용 recoil moments를 유도하고 구현했다. 별도 Astra R6의 직접 검토와 Wolfram 21개 항목이 통과했으며, 새 구현의 14개 test method, 6개 energy/binding fixture, 16개 radial reference case 및 7개 고정밀 적분이 통과했다. 실제 독립 C9 판정과 root 수용은 reviews/에 별도로 기록한다.

이 결과는 기존 fixed-center PWBE 및 TDCS413 유한 비교에 없던 finite-M support/frame/recoil 운동학의 구성이다. Physical outgoing amplitude가 아직 결합되지 않았으므로 부모 HE-ANG은 SOURCE_INPUT_PENDING이고, event sigma 및 실제 cross-section-weighted ion recoil 분포의 승인은 열려 있다.

## 1. 최신 작업의 종합과 선택

2026-10-24 11:46 이후 조사에서 7개 repository의 14개 branch/open-PR collection을 30 pages 모두 terminal까지 읽었다. Branch 1,334개, open PR 867개이고, 이전 1,330/863 대비 각각 4개 증가했다. 변경된 관련 core/owner의 pinned 본문 27개를 읽고 exact Git blob을 확인했다. 모든 branch의 모든 본문을 읽었다는 뜻은 아니다.

중앙 HEAD3423209a55d800de7e464f16fc600ec0c278833f는 직전 E2650548a에서 stock/work 전달·복구 metadata 16개만 달라졌다. 중앙 AGENTS/DAG/HE handoff는 기존 E와 byte 동일했고 40개 node, 다른 39개 node의 권한·계약·OPEN을 유지했다. 실제 PR98 HEAD는 d477aafcc620a010e954aa711d108fa2761a1d7e, draft/open/unmerged이며 현재 파일118개와 B1/B2/B3 archive hash를 재확인했다.

새 owner 결과는 각각의 범위로 유지했다.

- HH145 PHYS88: atomic-to-bare neutron-capture remap S0, 9/20, local numerical child0, empirical equivalence OPEN, HH_R10 OFF.
- CR N5 EI energy: frozen 준비 단계, 새 numerical NOT_RUN, full N4/N5 OPEN, 기존 실패·비용 및 Drive UNKNOWN 유지.
- REC134: represented response 627 dense RHS 및 128 exact Fraction dots, 전달20/20. 313 query의 physical uncertainty는 null, H5 uncalibrated/Physical HOLD. 중앙226는 별도 unmerged 관측.
- Vigilode D3: scoped derivation 및 feature-absent RED14fail. 새 numerical campaign NOT_RUN/production HOLD.
- 중앙 stock/work: scoped arithmetic/work 결과와 actual final ACK만 갱신됐고 L4는 false, 과거 cap overrun 및 unknown이 남아 있다.

Dropbox 연구 dossier는 4,916개 항목(파일4,722/폴더194), 9 pages terminal이다. 이전 대비 추가8개, 변경/삭제0개이다. PR98의 B2/B3를 양 provider metadata로 읽었고 HH87 terminal JSON12371bytes를 실제 GET하여 final Git HEAD496670cf 및 S2cf48be1b와 일치함을 확인했다. 그 terminal이 보고한 다른 archive 복원은 owner의 보고로 구분했다. Drive는 제공된 새 paginated 문서 검색에서926개 문서/3pages,27개 폴더/1page를 terminal까지 읽었다. Binary archive 전체 목록은 해당 검색에서 열거되지 않으므로 known-ID metadata 확인과 구별한다. 대화 검색도 query-selected이며, 중앙 대화의 PR98 B3 pending 문구는 실제 최신 PR98 B3 ACK보다 오래된 관측으로 처리했다.

SciSpace 검색1회, Exa 검색2회/fetch2회를 실제 수행했다. Kadyrov et al. (2009)의 arbitrary finite-mass Jacobi mechanics가 이번 정확한 기초 입력이다. Attaourti et al.의 Coulomb-Born 직접 진폭은 후속 후보로 보존했다. 그 preprint Eq18의 추가1/r 불일치, 교환항 생략, publisherPDF403 접근 공백을 남기고 임의 normalization이나 교환항을 만들지 않았다.

## 2. 원전과 새 유도의 구분

Kadyrov et al., Annals of Physics324(2009)1516–1546, DOI10.1016/j.aop.2009.02.003, §3.1 pp1527–1528의 reduced masses/COM Hamiltonian과 Eq79 뒤 energy identity를 실제 PDF로 확인했다:

https://atom.curtin.edu.au/igor/atomlab/sdarticle.pdf

PDF448174bytes SHA256 c7627a718193fc1ab0181d1c7fbabdc334bcf53a28e3a0870c45cd9827da9165. 원전이 제공한 것은 arbitrary-mass COM foundation이다. 아래 lab mapping, root classification/coarea, phase-volume 및 W=1 moments는 이 작업의 직접 유도이다. 원전의 normalized lab detector cross section이나 numerical e-H amplitude를 확보했다고 해석하지 않는다.

NIST SP961(2022 CODATA, May2024 poster)의 mass ratio1836.152673426(32)를 직접 확인하고 central value만 고정했다:

https://physics.nist.gov/cuu/pdf/wall_2022.pdf

그 불확도를 전파하지 않았고, nominal eV 환산 U=27.2는 과거 HE 단위의 convention이다. 정밀 Hartree 상수와 같다는 주장은 없다.

## 3. 전체 shell을 만드는 식

전자 atomic units, target-at-rest lab에서 P=(0,0,sqrt(2E0)), nucleus M>0, binding B>0이다. Q=P-p_A-p_B를 써

  F=E0-B-p_A^2/2-p_B^2/2-Q^2/(2M),
  dLambda=d^3p_A d^3p_B delta(F)

를 정의한다. T=M+2, mu=M/(M+1), nu=(M+1)/(M+2)일 때

  q=p_A-P/T,
  k=p_B+p_A/(M+1)-P/(M+1),
  epsilon=nu E0-B.

변환 determinant는1이며

  EA+EB+ER=P^2/(2T)+k^2/(2mu)+q^2/(2nu).

epsilon>0이면 k=sqrt(2mu epsilon)u, q=sqrt(2nu epsilon)v, |u|^2+|v|^2=1이 모든 labelled final kinematic state를 매개화한다. epsilon<0은 empty, epsilon=0은 zero-measure collapse다. Binding은 fixed B=1/2와 Coulomb reduced-mass B=mu/2를 별도로 비교했다. Binding mass defect와 상대론은 이 Galilean Hamiltonian에 포함되지 않는다.

고정 p_A에서 r=P-p_A, alpha=(M+1)/M,

  H=E0-B-EA-r^2/[2(M+1)],
  c=r/(M+1), rho^2=2H/alpha

로 놓으면 F=H-alpha|p_B-c|^2/2이다. 따라서 conditional support는 이동된 sphere이고, H>0에서 conditional integral은4pi rho/alpha이다.

## 4. 두 radial 해와 fold

검출 ray p_B=p n_B에서 beta=(r.n_B)/M,

  gamma=EA+r^2/(2M)-(E0-B), D=beta^2-2alpha gamma

를 정의한다. 가능한 모든 positive root는

  p_+-=(beta +- sqrt(D))/alpha

중 p>0인 것들이다. D>0/gamma>0/beta>0이면 두 positive roots가 존재한다. Simple root의 Jacobian은

  dLambda/(dEA dOmegaA dOmegaB)=p_A sum_j p_j^2/sqrt(D).

M=1,B=1/2,E0=1,p_A=P/4인 합성 fixture의 두 해는 theta_B=0에서

  p_- = 0.1350453783688632268007715785245...,
  p_+ = 0.9256147934109580598004949646327...

이고 theta_c=arccos(2/3)=48.1896851042214...degree에서 합쳐진다. M=1은 시험용 질량이며 proton의 물리적 질량을 대체한 결과가 아니다.

실제로 계산한 branch-summed angular integral과 regular sphere integral은 각각

  2.48364706644902530860838766758008778119278593068579336719921067705875205676678055

로 저장됐다. 80자리에서 보고된 상대 차이는0.0이다. 정확한 동일성의 근거는 이론의 analytic substitution이고, 수치0.0을 interval certificate로 바꾸지 않는다. Binary64 구현은 raw discriminant와 scale을 보존하고 caustic 근처에서는 NEAR_CAUSTIC_UNRESOLVED를 돌려준다. 음수 D를 임의로0으로 자르거나 무한 weight를 finite하게 만들지 않는다.

## 5. 위상공간 volume과 실제 계산

epsilon>0의 정확한 labelled kinematic volume은

  Phi=4pi^3[M/(M+2)]^(3/2)(nu E0-B)^2.

이 양의 단위는 momentum^6/energy이며 cross section이 아니다. M=1836.152673426에 대한 실제 값은 다음과 같다.

| Nominal E0(eV) | B convention | Phi(binary64) | W=1 mean ER(atomic units) |
|---:|---|---:|---:|
|20|fixed0.5|6.831949361815778|0.000527370873688165|
|20|mu/2|6.8477902236788735|0.0005275189355393669|
|54.4|fixed0.5|278.19714435481035|0.0019023098047527632|
|54.4|mu/2|278.2981790934471|0.001902457866603965|
|413.6|fixed0.5|26748.156800033626|0.016259230270985428|
|413.6|mu/2|26749.147417346012|0.01625937833283663|

W=1은 검산용 kinematic measure이고 실제 ionization amplitude 가중치가 아니다. 그 평균과 분산은

  <ER>=M P^2/(2T^2)+epsilon/T,
  Var(ER)=2M P^2 epsilon/(3T^3)+epsilon^2/(4T^2).

12 axis nodes와64 hypercube nodes를 양의 가중치로 조합한76-node rule은 S5의 degree<=4 moments를 정확히 재현한다. 이 구성으로 lab energy/momentum과 mean/variance를 검사했다. 임의 physical amplitude를76점으로 충분히 적분한다는 주장은 없다.

고정 B의 infinite-M limit에서 beta->0이고 하나의 positive p_B=sqrt(2(E0-B-EA))가 남으며 coarea factor는 p_A p_B로 수렴한다. Phi는4pi^3(E0-B)^2로 수렴한다. 이 극한을 threshold/fold 주변의 uniform numerical error bound로 쓰지 않는다.

## 6. 실제 검증과 비용

| 검사 | 실제 결과 |
|---|---|
|R6 독립 Astra 직접 유도/source 대조|PASS|
|R7 Wolfram|21/21 True, evaluator1회/context0|
|새 targeted test methods|14/14 PASS|
|Energy/binding fixtures|6 PASS|
|독립 mp80 radial cases|16 PASS|
|독립 phase-volume quadrature|6 PASS|
|두 branch fold quadrature|1 PASS|
|76-node states|6 fixtures에서 각76개|
|저장 출력 figure|PNG/SVG 실제 생성; 별도C9 actual visual review|

관측 최대 오차는 binary64 volume4.3022484084710367e-16, ordinary root4.662849293818372e-16, ordinary Jacobian2.5621855173149446e-15, energy3.0751266063160474e-16, momentum2.220446049250313e-16, moment2.418474499767532e-16이다. Mp80 volume quadrature relative error는 최대2.582957358791492e-81이다. Frozen acceptance를 바꾸지 않았다. 유한 fixture의 실측 오차이며 전 정의역의 outward-rounded certificate가 아니다.

| Child | Result | Parent+child CPU(s) | Wall(s) |
|---|---|---:|---:|
|01 tests|PASS|0.064747|0.06918608200066956|
|02 analysis|PASS|0.5463089999999999|0.5751221360005729|
|03 saved-output plot|PASS|1.873395|1.8748732269996253|
|Total|3 PASS|2.484451|2.519181445000868|

할당은8CPU/30wall,512MiB/1thread, reserve0used/1remaining이다. 이전 completed suite 및 scientific kernel의 재실행은0이다. Wolfram tool wall10.709s, bodyCPU1.583364/bodywall1.559547이며 total remoteCPU는UNKNOWN_NOT_ZERO다. 준비·조립·보고·provider/model/IO는 별도 기록하고 전체 end-to-end cap을 입증하지 않는다. 원장의 이전 DDCS/CCC/TDCS54/PWBE/TDCS413/Hex/HE-X1/HE38/D10 비용·실패·unknown을 유지했다.

분석 SHA256:711d8dd054e3d74e0d0c0da15ee352114b7a94b2d44e84504cc0e79f649e4243.
PNG SHA256:acb6c8f1bce35380272826296b6db6c62ba41afee363975095e0a7a9210b98bc.
R6-reviewed theory SHA256:9a2d927f5a04bbac6e0e6db759dad39fe950c08aae31fa948d2ca9ea47343a7b.

## 7. DAG, 게시 및 백업

단계별 실제 근거, 현재 완성도, 게시와 백업 상태는 LOOP_PROGRESS.json에 통합한다. 이론·준비는 B1, 검증된 과학 스냅샷은 S/C 및 B2, 최종 전달은 D/E 및 B3로 보존한다. Provider ACK와 local hash를 독립 remote SHA 검증으로 표기하지 않는다. 모든 ref 갱신은 expected SHA/force=false로 수행하며 병렬 owner의 파일을 보존한다.

순서: 실제 authority/HEAD/AGENTS/backup -> 원전·이론 -> R6 -> R7 -> C1-C5 -> B1실제dualACK -> C6-C8 -> 독립C9 -> S/C/B2 -> D/E/B3 -> 다음 source payload 결합.

이번 단위의 단계 완료율과 전체 HE-ANG 물리 완료율은 구별한다. 새 kinematic subunit이 끝나도 전체 goal percentage는null이다.

## 8. 다음 정확한 의무

첫 global open input은 HE-ANG-SOURCE-PAYLOAD이다. Source-consistent joint outgoing-electron amplitude/event payload와 flux/Fourier normalization, count/spin/exchange, 전체 support, lab/COM, finite-M consistency, calibrated uncertainty/validity를 함께 받아야 한다. 그 뒤 새 shell 위에서 amplitude-weighted electron/ion moments를 같은 law로 평가하고 independent review를 거친다.

확보한 Coulomb-Born 직접 진폭 후보는 원전 Eq16/19로부터 bound overlap -dI/dlambda를 직접 유도하고 phase·normalization·orthogonality를 확인할 수 있다. 하지만 plane/Coulomb 역할을 임의 swap하여 exchange-complete라고 부르지 않으며, fixed-center amplitude에 이번 shell만 붙여 finite-M source consistency를 얻었다고 하지 않는다.

DDCS20 marginal을 전체 event sigma/ion recoil law/HE-X1 경험적 보정으로 확대하지 않는다. C9-NB-01 future partial mu_window theta metadata 의무, 중앙 C23E와 다른 owner의 scoped 결과·OPEN을 유지한다. 새로운 strong no-go나 문헌 최초성 주장은 없다.


## 9. 실제 게시·복구·최종 freshness 전달 보충

앞 1–8절은 Science S `8d481ed47f57774f48bcfb412671ff927601316e`의 과학 결과와 당시 조사 상태를 보존한다. 현재 실제 중앙 C는 `407381b302d8b98f251b54d277823997bc4fca9f` (tree `eee49882efa63ca19043d40b7e96b8fe3cbe0382`)이고, 이 전달 D의 자기 SHA는 CURRENT_FILE_COMMIT 의미다. PR99는 draft/open/unmerged이며 activation=false다. 실제 B2 dual ACK 이후 R10/C10은 이 전달 commit에서 COMPLETE_AT_DELIVERY_COMMIT, 정의된 단위는 20/20 scoped다. 중앙 E와 B3의 실제 최종 영수증은 아직 대기하며 PR99 description의 외부 영수증으로 닫는다. 이 단계 수는 전체 HE-ANG 물리 목표 달성률이 아니다.

B2 `HEANG_FINITEMASS_SHELL_SCIENCE_20261024_8d481ed4_407381b3.tar.gz`는 2281167 bytes / 221 members, 로컬 업로드 bytes SHA256 `c45167100ada3287899a5d49b4686948a2f859c9b36b8db78a2f13bd4bbec43a`다. Drive `1jFe0xxImaBLsqz8K1DFgje4MdQjtMzHb`와 Dropbox `id:BSpOijBcT10AAAAAAD_9lw`의 실제 업로드 및 별도 metadata size ACK가 있다. B2 remote full GET/SHA256은 독립 검증하지 않았다. 로컬 member 검증 및 provider ACK와 구분한다. 포장 CPU 0.28118744900000003초 / wall 0.2813142700033495초는 과학 원장 밖의 운영 비용이다.

18:25 UTC에 다시 확인된 로컬 소실의 원인은 NOT_ESTABLISHED다. 게시 S67을 retained literal payload와 actual Git blob/size로 복원했고 실제 B1 full GET bytes/hash를 대조했다. 과학 재실행은0이다. 공개 복구 receipt3개와 source/RECOVERY_PROVENANCE.json은 원본 source URL/hash, 실제 metadata-only 보관 및 full PDF/text/page image 제외를 구분한다. 전체 복구·provider·host 비용은 UNKNOWN_NOT_ZERO이며 이전 원장을 초기화하지 않았다.

S의 LOOP_PROGRESS top-level C9 및 C8 evidence에는 파생된 과거 PENDING 문구가 남았으나 실제 C9_REPORT/ROOT_ADMISSION과 당시 current_stage는 이미 PASS였다. D에서 그 현재 파생 metadata만 정정했다. 이론·계약·코드·원시 결과·그림·독립 과학 review를 바꾸거나 새 review를 수행하지 않았다.

초기 S0 조사 뒤 CR103은 실제 conditional H1/He4 EI finite-chain으로 완료되었고, HH145는 실제 conditional bare finite-window 및 FINAL 전달로 진행했다. 현재 중앙 C는 6de53766의 이 실제 관측을 보존한 base 위에 게시됐다. CR Library/Dropbox R3 PASS와 Drive UNKNOWN_NO_ACK, full N4/N5 OPEN/N6N7 gated를 구분한다. HH 부모 PARTIAL, empirical source equivalence·covariance/tails·named consumer·stopping OPEN, HH_R10 OFF 및 production NOT_ISSUED를 유지한다. HH FINAL의 양 provider whole GET/restore는 실제 읽은 owner 중앙 영수증의 보고이며 이 worker의 새 GET 주장이 아니다. 각 owner의 실패·별도 비용·unknown은 post_S_parallel addendum에 보존했다.

18:28 UTC의 마지막 metadata 조사도 7개 repo/14개 collection/30 pages 모두 terminal이며 1,336 branches와871 open PRs다. REC135의 six-primitive local source Jacobian 및 VIG86의 manufactured dense-curve certificate는 실제 title/HEAD만 읽은 새 lead이고 본문이나 과학 판정을 승인하지 않았다. 초기 조사와 이 최신 metadata pass를 구분한다. 새 H electron-impact physical amplitude/event payload가 이번 metadata에서 보이지 않았다는 관측을 전역 부재 증명으로 바꾸지 않는다. HE-ANG SOURCE_INPUT_PENDING, C9-NB-01, C23E, 모든 다른 owner OPEN 및 비용 unknown은 그대로다.
