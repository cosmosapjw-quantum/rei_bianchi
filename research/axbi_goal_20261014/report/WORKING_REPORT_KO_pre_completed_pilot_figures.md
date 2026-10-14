# 비경사 축대칭 Bianchi I 재이온화 abundance 작업 원고

목표 산출물은 지원되는 전체 구간의 H/He 이온 이력과 BBN 방식 시간·기체 온도 abundance 그림이다. 현재 원고는 물리 관례와 구현된 provider 연결을 담은 작업본이며 새 이력 결과는 아직 삽입하지 않았다.

`manuscript.tex`는 metric, proper clock, q_ref/Sigma 구별, H/He EOS·electron census, Case A escape, 단일 사건 energy owner, photon characteristic, baryon/element normalization을 기술한다. Grackle provider의 1–10⁶ K는 operational domain이며 empirical 정확도나 continuum certificate를 뜻하지 않는다. 기존 F08 15행은 synthetic prescribed endpoint 범위로만 보존하며 전체 시간 이력으로 재해석하지 않는다.

다음 입력은 AX07/AX08의 실제 `history.csv`와 `abundances.csv`, AX11의 baseline+2 refinement 응답, AX12 source/IC 민감도다. 저장 이력이 도착하면 시간순서 abundance_vs_Tgas와 proper-time 그림, FLRW/BI·signed 차이, hydrogen .1/.5/.9 milestone의 reached/censored 상태를 삽입한다. 온도를 정렬하여 비단조 경로를 지우지 않는다. D/T/He3/Li는 구현되지 않은 선택 확장으로 명시한다.

원고/PDF 생성은 science PASS가 아니다. unknown observer tail은 0이 아니며 abundance 목표의 비차단 secondary 항목이다. scoped 독립 결정과 실제 publication 검증은 별도 단계다. 빌드·명령 raw stream은 `raw/`와 `IMPLEMENTATION_RECEIPT.json`에 기록한다.

## 고정 시나리오·연속 source 갱신

AX01은 Planck-like rounded cosmology, zbar20→4, q_amp=.01, 명시적 approximate residual H 및 post-decoupling 냉각 IC를 선택했다. 시간축은 **zbar20 이후 경과 proper time**이며 absolute cosmic age나 matching REC donor를 주장하지 않는다. MD14 SFR/yield, fesc=.2, Zstar=.002와 50,000 K blackbody 13.6–100 eV 연속 photon source를 구현했다. z>8 source law는 phenomenological continuation이다. source spectral cell 평균 에너지의 첫 Simpson8 검증 실패를 보존했고 승인된 Simpson32 수치 수정 후 targeted2 tests가 통과했다. 구현 검증은 full evolution/science admission이 아니다.

## 실제 FLRW 부분 pilot

첫 실제 실행은 zbar20→19.8 목표 중 zbar19.86586760536834에서 `AXBI_OUTPUT_CAP`으로 checkpoint를 남기고 종료했다. accepted2870, actual tentative8667, RHS60693, reject18, wall64.233055s/CPU64.128211s/peak RSS3724KiB다. 수치 실패가 아닌 output 자원 제한이 보고된 종료 이유다. 양전단 pilot은 시작하지 않았고 자동 재시도는 없었다. 전체 pilot/이력 완료나 과학 admission을 주장하지 않는다.

66개 생성 파일 원본234862901bytes를26,097,828byte tar.gz에 lossless 보관했으며 전체 파일의 membership·크기·SHA를 독립 archive stream으로 확인했다. 원본은 남겨두었다. authority는 accepted scalar rows를 모두 보존하고 전체 spectra만 initial/checkpoint/terminal로 저장하는 한 번의 수정을 승인했다. 새 binary/changed-output review/수정 allocation에 따른 후속 실행은 별도다.
