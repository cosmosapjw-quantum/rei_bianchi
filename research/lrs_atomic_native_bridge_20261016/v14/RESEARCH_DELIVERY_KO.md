# REI-LRS V14: 출생시각 실행 코드 게시와 독립 사건·열에너지 검사

## 재개 기준
2026-10-18 지정된 Google Drive 및 Dropbox의 rei_bianchi 백업을 먼저 확인했다. V14에는 R5/C5_C6만 있었고 새 native 실행 영수증을 찾지 못했다. GitHub V14 HEAD도 1c219805bb3684a83377e68eebd581ec00d97cde였다. 이는 조회한 경로의 결과이지 사용자의 모든 저장소에 결과가 없다는 주장이 아니다.

직전 복구 아카이브 d2ae9b8af0c9fe68e60e263d5dedfdb25edd9663251d5942a7d6f62f4626b406 (2353693 bytes)를 입력으로 재사용했다. 과거 V11 문서의 NOT_RUN/출력 수치는 현재 V14의 실행 증거가 아니다. V12/V13의 기존 source capsule은 변경하지 않았다.

## 완료한 코드 수정
직전 복구에서는 32 Python tests 및 76개 제조 수치 문제를 실행했지만, 수정된 분석기·실행기의 GitHub 게시가 없었다. 이번에는 누락된 복원기, source manifest, 실행기, Python reference, 테스트, native module 등록 조각을 모두 정상 repository 파일로 게시했다. 코드 anchor는 f6046418d15e2f44418dfbc04ca67999f389a7df이다. NCP에서 압축 소스 capsule을 복사·해독할 필요가 없다.

새로 발견한 결함: 기존 분석기는 native가 적은 energy_residual 값이 0이면 CE/RR/FF/CMB/팽창 work/escape/photo-binding/electron 열을 개별적으로 바꾼 잘못된 CSV도 받아들였다. 먼저 8 FAIL / 1 PASS 반례를 보존했다. event_energy_audit.py와 연결된 analyze_v14.py는 원시 열을 이용해 여섯 회계를 따로 재구성한다. 수정 뒤 57/57 PASS: 기존32 + 반례·무사건9 + 혼합 비영 사건/부호 있는 CMB16이다. 이 검증용 CSV는 실제 native 이력이 아니다.

## 물리적 정의와 직접 유도
평탄 FLRW, X=ln(a/a0), metric (-,+,+,+), a0=1/21. 모든 사건수와 에너지는 전체 H 핵수당 정규화한다. Y=0.2454/[4(1-0.2454)]는 He/H 핵수비, x,y,z는 HII/HeII/HeIII 분율이다. e=x+Y(y+2z), w=(3/2) k_B T(1+Y+e)/eV_erg이다. k_B=1.380649e-16 erg/K 및 eV_erg=1.602176634e-12 erg/eV를 유지한다.

P_i,C_i,R_i는 HI/HeI/HeII 광이온화, 충돌이온화, 대응 이온의 RR 누적 사건/H이고 D는 HeII DR 사건/H이다. 결합에너지 문턱 chi=(13.598434599702,24.587389011,54.41776)eV는 native hhe_events의 정의이며 Verner fitting cutoff와 혼동하지 않는다.

B=chi_H*x+Y[chi_HeI*y+(chi_HeI+chi_HeII)*z].
C_B=sum_i chi_i C_i, R_B=sum_i chi_i R_i+chi_HeI D, P_B=sum_i chi_i P_i.
Q=Q_RR+Q_DR+Q_CE+Q_FF. E_CMB는 기체로 유입되는 부호 있는 열량이다.

Delta e=sum(P+C-R)-D
Delta B=P_B+C_B-R_B
Delta w=Q_photoheat-C_B-Q+E_CMB-W_gas
E_escape=R_B+Q

따라서 Delta(w+B)+E_escape+W_gas-E_CMB-(Q_photoheat+P_B)=0이다. Wolfram Language의 직접 대수 전개 잔차가 정확히 0이었다. 이는 주어진 owner 회계의 항등식이지 실제 재결합 photon spectrum, Case-B 재수송 또는 이산화 정확도 정리가 아니다.

검사하는 여섯 잔차: reported electron/EOS, electron/events, photo-binding, chemical binding, escaped cooling+capture binding, gas thermal. energy 1e-9 eV/H 및 events 1e-9/H는 기존 V14 analyzer의 bound 그대로다. 이 bound의 적합성은 후속 실제 실행에서 관측 오차·Newton residual과 함께 보고해야 하며 정확도 목표로 오해하지 않는다. V14 고정 초기상태(.075,.12,.03),15000K에 한정한다. 초기상태를 바꾸려면 판독 계약도 함께 바꿔야 한다.

## 기존 수치 결과 재사용
직전 실행의 76개 제조 문제(선형54, 비선형16, 강성6)는 보존·재검산한다. 고정 S,k 선형 GL2는 약4차, 일반적인 curved-opacity 비선형은 약2차이고, k=1000의 한 단계 GL2 생존량은 상대오차 약100%였다. 이들에 Grackle/Verner 전체 source-on 정확도를 부여하지 않는다. 이번 새 과학/코드 결과는 여섯 독립 회계의 유도와 반례를 잡는 수정이며, 과거76건을 새 native 실행으로 세지 않는다.

## 실행·게시 범위
Python57, shell syntax, 원본을 복원한 native 네 파일 SHA 검사가 실제 수행됐다. Rust compiler/cargo가 없고 sandbox DNS도 실패했으므로 컴파일과 NCP 실행은 NOT_RUN이다. 네 Rust 파일은 이번 수정에서 그대로 유지됐다. 독립 subagent 도구가 없어 native_subagent NOT_RUN, user-authorized serial implementation이다.

표적 native 테스트는 기존29+V14 신규7로 예상하지만 실제 통과를 주장하지 않는다. 넓은 V13 crate 시험의 과거 누락 fixture 실패도 지우지 않는다. 실행은 RUN_V14.sh가 담당하며, 두 구간에서 7모드×6N=84이력/7056 macro rows를 만들도록 설정되어 있다.

CSV에 살아남은 photon energy와 boundary photon number가 없으므로 완전한 photon energy/number 독립 재구성은 여기서 주장하지 않는다. 저장된 native residual 검사는 유지하되 이것을 독립 검증으로 다시 세지 않는다. full source-on p2, uniform stiff accuracy, Case B, full EoR, signed Bianchi는 HOLD.

## 문헌과 근거
Grackle: Smith et al., MNRAS, DOI 10.1093/mnras/stw3291. Photon-conserving transfer: Mellema et al. astro-ph/0508416. 시간 중심 optical depth: Mackey arXiv:1201.5651. 이 문헌은 배경이며 V14 판독기 검증의 근거는 실제 반례/회귀 로그다. 동료 프로젝트의 source-age 연구는 PR185 및 bass_cr PR76/77/79를 참조하되 본 native owner를 자동 교체하지 않는다.
