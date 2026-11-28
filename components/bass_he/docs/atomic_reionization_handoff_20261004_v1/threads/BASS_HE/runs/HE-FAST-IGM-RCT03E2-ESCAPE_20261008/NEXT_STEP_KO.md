# RCT03E3: 실제 rate 시간·분광 예산과 남은 선택격자 범위

읽기: REPORT_KO.md, RESULT_SUMMARY.json, PLAN.json, evidence/analysis_final/RESULTS.json, staged/examples/e2/support.rs.

E2에서 OFF/KF/GM escape의 N192→384 시간비교는 기존 목표를 통과했다. GM에는 새 N384 panel256/512, Gauss2/4를 더해 18필드 합산기준도 통과했다. OFF/KF의 N384 전체3축은 미평가다. 과거 N192 escape FAIL과 이번 성공은 서로 다른 격자범위다. 원자를 다시 계산하거나 성공한 sourcefree/기존 coupled 전체suite를 재실행하지 않는다.

다음 중심 관측은 이미 출력된 actual `radiation::gamma`다. 각 endpoint의 gamma와 target heat는 weights*density*sigma의 원 함수 readout이고 evolution에 들어가지 않는다. Gamma를 A/(n_abs dt)로 역산하지 않으며, 현재 gate에는 Gamma 시간정확도가 없다는 점을 유지한다. 같은 격자의 두 native reduction 표현은 독립 atomic model이 아니다.

가장 작은 추가 설계는 (i) Gamma를 출력한 N192의 필요한 모드만 새 readout으로 계산해 N384와 동일시각 비교, (ii) 실제 cutoff/source birth-front를 분리하는 endpoint readout 구적과 기존 positive restriction의 계약 확인, (iii) 필요한 경우 OFF/KF의 N384 분광control만 추가하는 것이다. 각 관측량 허용량은 새 실행 전에 명시한다. 기존 구적차수를 올린 것만으로 continuum bias를 닫지 않는다. N/U 또는 inverse-cubic bound를 Verner 인증으로 대체하지 않는다.

E2의 N384 clock은 새 probe에만 있고 기존 radiation::time_at의 제한은 그대로다. 기존 모든 시각에 위임하며 new384의 even node는old192와bit-equal이다. N768는 여전히 미선언이다. Grid::new source/cutoff anchors는24-grid이며, 이 사실을 숨기고 새 lattice가 spectral support까지 해결했다고 주장하지 않는다. root/energy ratios가초반에1에가까운기록을보존하고tightening/loosening을자동으로하지않는다.

실제 source/threshold/Ebar35eV, baselineOFF, 원자모멘트null, physicalHOLD와owner채택OPEN을유지한다. 기존 staged receiver를다시작성하지않는다. 원격receiver/root는이번에도수정하지않았다.

재현: `bash run_checks.sh /absolute/new/output`. 기존 증거를 덮어쓰지 않는다. Rust1.94.1 prefix와Python만 필요하다. 여기서는 wrapper 구성명령과문법을검증했으며,추가5이력을wrapper검사때문에반복하지않았다. 첫tool200초중단의3prefix는실패폴더에있고canonical5이력만정상반환으로사용한다. 원상태/스펙트럼이없는partialCSV를restart checkpoint로쓰지않는다.
