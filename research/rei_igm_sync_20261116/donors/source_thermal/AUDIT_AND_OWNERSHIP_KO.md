# HE/CR → 원 REI IGM: 현재 기여와 수정

조회일 2026-11-16 KST. 현재 중앙 선택은 `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`이며 primary-only Case-A escape이고 CR/HH/RCT/secondary/molecules는 OFF다. 이 선택은 이번 통합 담당자가 전달한 실행 범위다. 아래 F05 OTS 결과는 이 AXBI 계산에 수치 공급자로 넣지 않는다.

## 현재 정본과 재사용 범위

| 저장소 | 확인한 최신 연구 HEAD | 결과/남은 의무 |
|---|---|---|
| bass_cr PR167 | 3d6d671474382a019c4aca1c5f331f8a3eabe31f | 원 F05의 4개 수용 시점에서 CR source-point 물질성 임계값. 실제 CR spectrum/clock/transport 미결속, CR OFF 유지. |
| BASS_HE PR154 | 09b07147b280448bc05a1d0a7c0508401cf58a0b | 원 F05 V2 [160,162] He II Lyα의 국소 OTS H/He 흡수·열량 분해. 원 RHS에 이미 포함됨. V2 공식 채택·공간 수송 미완료. |

기본 브랜치는 각각 bass_cr `77237751bdd2aed5934bf7fc3bc626d631a09058`, BASS_HE `6ef63136d14dbe68a1c9eff4a43fece78cd87b35`이며 2026년 9월 기록이다. 최신 연구는 열린 draft 브랜치에 있다. 12개씩 최근 PR metadata/body, 최신 구현·과학 결과·handoff/정책에 접근했다. 전체 PR 본문·모든 backup 바이트의 재검산을 주장하지 않는다. 원문 응답은 evidence/CR_RECENT_PRS.json, HE_RECENT_PRS.json에 보존했다.

## 발견 및 실제 교정

BASS_HE `native_v2_lya_ots_feedback.py`는 적분된 `qsource["escaped"]` [photons]와 `qsource["escape_original"]` [erg]를 직접 interval intersection으로 비교했다. 원 f∈[0.1,1]에서 양쪽 하한이 0이므로 잘못된 단위나 에너지 크기도 통과한다. 같은 저장소의 독립 감사 경로는 이미 Eα×eV→erg 변환을 적용하므로 공개된 물리 합계를 무효화하는 발견은 아니다.

생산자 검사를 Eα=40.813320 eV, 1 eV=1.602176634e-12 erg로 변환한 같은 표현의 양 끝점 비교로 교정했다. 표현 차이의 수치 기준 6e-12는 기존 독립 감사의 source-representation 기준을 재사용하며 원 REI 물리 gate 2e-4/2e-3을 변경하지 않는다. 공통 0 하한의 자명한 교차를 통과 근거로 사용하지 않는다.

실제 실행: Python 3.12.14/NumPy 2.3.5, `python3 -m unittest discover -s research/rei_f05_v2_lya_local_reabsorption_20261115/tests -p test_escape_energy.py -v`. 6/6 통과. SHA256 `6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae`인 원 공개 92,160행에 새 검사를 적용했고 최대 상대 표현차 1.2733868152902887e-15. 단위변환 누락·2배 에너지·비유한 입력의 음성 검사를 포함한다. 원 26-event map, 비공개 NPZ, IVP는 재실행하지 않았다. `git diff --check` 통과. 독립 다른 agent 검토는 최종 통합 담당자가 기록한다.

Wolfram에서 국소 source의 광자 수와 에너지 항등식을 별도 확인했다:
N_H=r(1-v)fz, N_He=r(1-v)f(1-z), N_esc=r(1-v)(1-f).
N_H+N_He+N_esc-r(1-v)=0.
B+Q+E_esc-eV_erg Eα r(1-v)=0.
출력 잔차 {0,0}; 이 항등식은 기존 물리의 재검산이다.

## 지연 원인과 최소 교정

1. **후보 결과가 소비되지 않음.** 최근 PR24개가 모두 draft이고, 각 최신 결과도 중앙 28/88 +0를 보고한다. 구현·원자료 분석 자체는 실질적이지만, 새 수용 이력이나 같은 시나리오 관측량에 결속되지 않았다. 미병합 자체가 실패 원인은 아니며, owner admission/consumer 계약이 비어 있는 것이 병목이다.
2. **watchdog의 문구와 실행이 어긋남.** BASS_HE 11월1일 정책은 한 보조 작업 뒤 중앙 최단 경로로 복귀하라고 명시했다. 이후에도 source-only 후속물이 이어졌다. 이번에는 이 감사/교정 이후 HE/CR 새 계산을 배정하지 않고 중앙 AXBI 결과를 기다린다.
3. **원 시나리오 혼합 위험.** F05 OTS의 f/He/H=0.079, F08 He/H=0.083, 원 AXBI primary-only Case-A는 서로 다른 계약이다. 같은 H/He라는 이유로 source를 합치면 열·광자 소유권이 중복된다. 선택한 AXBI에는 HE OTS와 가상 CR를 주입하지 않는다.
4. **물질 quadrature를 공간 mesh로 오해할 위험.** F05 46,080행은 물질 적분 노드이며 위치·이웃·null ray가 없다. 행 번호로 공간 수송을 만들지 않는다. 공간 source가 요구되면 REI/BASS가 동일 시나리오의 geometry/closure를 먼저 명시한다.

## 담당 경계와 다음 행동

- rei_bianchi: 선택 시나리오, 실행·수용 이력, closure, source/thermal 전체 장부와 최종 IGM 과학 해석.
- BASS_HE: source가 지정한 입자·에너지 영역의 미시 열화/에너지 분배. 이번 baseline에서는 추가 HE channel OFF. 원 F05 결과는 보존하고 별도 호출 때만 사용.
- bass_cr: source spectrum·주입 clock·transport가 지정된 경우의 외부 CR source. 이번 baseline CR OFF이며 계산상 blocker가 아니다.
- bass: 동일 시나리오 geometry, proper clock, ray/observer mapping. 원료를 공간 좌표로 만드는 책임을 HE/CR에 주지 않는다.
- WU/REC: 해당 baseline의 실제 rate/opacity/primary-energy provider 정본. 별도 donor 결과를 임의로 대체하지 않는다.

새 연구 시작 전 매 턴 한 항목만 검사한다: 지금 바꾸는 결과를 중앙의 어느 함수·history·관측량이 어떤 동일 입력으로 소비하는가? 답이 없으면 해당 보조 작업은 배정하지 않는다. 이는 새 승인 gate가 아니라 우선순위 선택이다.

## 상태

이번 수정은 implementation-verified 유지보수이며 새 과학 노드나 새 물리 결과로 계상하지 않는다. 중앙 28/88, working33/88, fast4/7 및 HE14/18은 원문 reported 상태이며 본 감사가 전체 노드별 재집계한 숫자는 아니다. 원 source 결과는 재사용, 원 IVP는 NOT_RUN, 공식 V2 채택·CR ON·전체 coupled IGM는 이번 자료만으로 완료 처리하지 않는다.

