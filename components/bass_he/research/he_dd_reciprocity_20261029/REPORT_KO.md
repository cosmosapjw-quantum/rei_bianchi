# BASS_HE DD reciprocity: 이론→코딩 루프 결과 (2026-10-29)

## 연구 기준
- 부모: `cosmosapjw-quantum/BASS_HE` PR106 HEAD `b5ee8c135accb98ba0f9533a4beb0c8c6210933e`, add-only branch `research/he-dd-reciprocity-20261029`.
- 원전: Arends et al., Phys. Lett. B 62, 411 (1976), DOI 10.1016/0370-2693(76)90671-7; Silverman et al., Phys. Rev. C 29, 35 (1984), DOI 10.1103/PhysRevC.29.35.
- 원본 EXFOR: IAEA-NDS/exfor_master `939a14d7bba1ddce51975cb5e8711ce96b3b0871`, `M0475.x4` SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`.

## 신규 과학 결과
1. 두 정지표적 실험의 불변량을 정확히 맞춤: Eγ213 MeV ↔ Td375.7505606070 MeV, Eγ330 MeV ↔ Td608.2630266481 MeV, Td376 MeV ↔ Eγ213.1255176098 MeV. 1984 역반응은 330 MeV 직접 정규화 자료가 아님.
2. 비편극, 시간반전, spin-averaged 2→2에서 `R_ordered=(2/9)(s-M²)²/[s(s-4m²)]`. Full-sphere event density가 ordered의 절반인 convention은 `R_event=2R_ordered`. 실제 EXFOR DA convention은 미확정.
3. Eγ213 MeV θCM73° DA 0.41±0.09 nb/sr를 matched Td375.75056에서 역반응에 사상한 가설적 DA 범위: ordered/inclusive-D [0.00821648004,0.01283825007] nb/sr, full-sphere event [0.01643296008,0.02567650013] nb/sr. Eγ330 MeV θCM73°는 matched Td608.263에서 각각 [0.000720840412,0.004325042473], [0.001441680824,0.008650084946] nb/sr. 이 값은 역반응 실측치가 아님.
4. CM→표적 정지계 두 daughter의 에너지·운동량, mass-shell 및 사건당 에너지·바리온수·전하 보존을 유도/검산.

## 실제 구현·검증
- `src/reciprocity.py`: 정확 Fraction 입력/kinematics/ratio/소스검증/조건부 DA, mpmath daughter boost, source identity mismatch와 float/bool 차단, source unknown 유지.
- `tests/test_reciprocity.py`: 현재 세션 Python3.13.5 **33/33 PASS**; `python -m compileall -q src tests` PASS.
- 독립 알고리즘 `evidence/independent_oracle.py`: Decimal80 direct four-vector 8개 사례, Decimal95 비교 최대 절대잔차 2e-73; Wolfram 두 세트 정확 항등식 각 4개 0. 고정밀 출력은 directed rounding 인증이 아님.
- `results/energy_matching.png`, `results/reciprocity_factors.png` 실제 생성·시각 검토. 에너지 매칭 주석 배치 수정. `make_figures.py`로 재생성 가능.
- 최초 32 PASS 뒤 독립 패키지에서 default source path가 없는 문제를 수정하고 한 검사 추가, 최종 33 PASS. Decimal 비교 harness 기본 precision 28로 인한 false failure는 context95 지정으로 수정. 물리 오류로 오인하지 않음.
- 기존 BASS_HE 전체 science suite/IVP, 15-row source campaign, PR105/106 수치계산 재실행하지 않음.

## 근거/승격
- established: 불변 2→2 kinematics, 시간반전 spin/phase-space 공식의 명시적 가정 아래 관계.
- derived + Wolfram checked: 두 frame 에너지 사상, ratio, lab boost, 보존식.
- numerically checked + implementation-verified: 새 코드와 독립 Decimal oracle, 33 tests.
- literature-supported: Arends/Silverman 실험 범위 및 Silverman의 시간반전 일관성 주장. 원 논문의 full normalization·효율 정의는 아직 source-locked하지 못함.
- unresolved: 실제 EXFOR ordered/event κ, detector coincidence efficiency, polarization, 330 MeV inverse measured source, physical photon history, named fast-D stopping/deposition/Cv.

## DAG와 작업 단계
- 중앙 물리 28/88, 기존 HE 14/18, PR105 2/2, PR106 1/2 **변경 없음**.
- 신규 국소 reciprocity 1/2: exact invariant-kinematics source adapter COMPLETE_SCOPED, physical event-semantics node INPUT_MISSING/REVIEW_PENDING.
- R1–R5,R7–R10 완료(9/10); R6 CAS PASS but native independent reviewer NOT_RUN (PARTIAL). C1–C8,C10 완료(9/10); C9 native independent reviewer NOT_RUN (PARTIAL). 즉 **실제 scoped 완료 18/20**, checkpoint 게시 20/20은 별도 집계.
- `R_event=null`, `physical_activation=false`, `L4=false`, `production=HOLD`. 물리 DAG 증가 0.

## 게시/백업
각 단계는 GitHub 독립 stage checkpoint, Google Docs append ACK, Dropbox Paper append ACK를 갖는다. 이는 각 단계에서 전체 source ZIP 20개를 업로드했다는 뜻이 아니다. 최종 source-inclusive ZIP은 별도의 create-only 이중백업과 manifest/크기/해시 증거로 검증한다. 원격 전체 byte readback 여부를 분리 기록한다.

## 다음 실제 과학 작업
Silverman 1984 및 Arends 1976의 full paper/학위논문에서 coincidence acceptance, DA 정의, spin/polarization 및 동일 d counting convention을 원문으로 고정한 뒤 동일 s의 역반응 수치행을 비교하라. 직접 측정이 없다면 정규화 추론 대신 qualified source/uncertainty를 찾아야 한다. 330 MeV의 Td608.263 대응을 유지하라. 실제 photon field/history와 fast-D stopping/deposition은 독립 후속 노드다.
