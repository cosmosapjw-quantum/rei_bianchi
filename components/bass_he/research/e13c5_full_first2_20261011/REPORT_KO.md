# HE E13C5 full first2 실행 결과

고정된 OFF/KF/GM 캡처의 모든 2440개 node에 대해 첫 두 step의 enclosure를
단 한 번 실행했다. 총 7320 paths / 14652 segments 중 PR19에서 검토한
36개 segment를 재사용하고 14616개를 새로 계산했다. 기존 Decimal60,
128-panel helper와 species mask/source/anchor 정책을 그대로 사용했다.

실행 exit 0, 사용자 CPU 13949.17초, 시스템 CPU 5.56초, process wall
3:54:41, 최대 RSS 98484 KiB를 관찰했다. 초기 실패와 재시작은 없다.
정확 유리수·key·stream controls는 exit 0이며 0.262초였다.

완료된 58608개 prefix/per-step ledger 검사와 모든 mode의 weighted
per-step/whole-path ledger는 zero를 포함했다. 별도의 다섯 representation
차이는 PATHS.jsonl 및 RESULTS.json에 보존했다. AGGREGATE endpoint와
step transaction을 구별했으며 representation rounding 차이를 equality
판정으로 사용하지 않았다.

후속 fresh independent Astra 판정은 PASS_SCOPED다. 23개 input pin 및
9개 receipt hash, 전체 coverage, 2351508개 유한 ordered interval,
비음수 endpoint lower bound, carry·seam·weighted ledger를 독립 확인했다.
판정 원문을 controller가 전달한 내용은 independent_review.json에 추가했다.
원 실행 receipt와 RESULTS의 pending 표기는 역사적 실행 단계로 보존한다.

승인 범위는 frozen gas interpolation/mask/source branch/energy seam을
사용한 첫 두 captured step의 모든 node에 대한 유한 enclosure다.
물리·global·production admission, cosmological continuum convergence,
새 gas evolution, 실제 photon/heat/recoil 전달, receiver adoption은 HOLD다.
292932850-byte PATHS는 local recovery tar에 보관하고 일반 Git blob에서는
제외한다. 후속 최소 행동은 게시 후 controller의 dependency-safe READY 판정이다.
