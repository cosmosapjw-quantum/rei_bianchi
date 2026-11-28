# HE R2 원전 조사 — 2026-10-28

## 조사 범위와 실제 수행

현재 날짜는 Asia/Seoul 기준 2026-10-28이다. 원 실험(1976), 후속 실험·학위논문(1998–2000), 그 이후부터 현재까지의 동일 반응 문헌을 별도 검색했다. Exa 6회 검색에서 요청한 후보 슬롯 합계는 35이며, SciSpace 자연어 검색은 10개 후보를 반환했다. 후보의 제목·초록과 실제 반응을 대조했고, 적합한 항목은 원문·공식 데이터로 다시 읽었다. SciSpace 결과는 발견 도구이며 증명이나 정규화 근거로 채택하지 않았다. 최신 동일 반응 문헌의 완전한 부재는 주장하지 않는다.

추가로 공식 IAEA EXFOR GitHub 기록을 직접 읽고, TUNL이 제공하는 Rice 학위논문 PDF를 내려받아 필요한 스캔 페이지를 OCR 및 이미지로 읽었다. 첫 일반 shell HTTP 시도는 Operation not permitted였고, 공개 원문 다운로드에 한정한 현재 실행의 sandbox escalation은 승인되어 성공했다. 기존 HARMONIC10 과학·검증 작업은 실행하지 않았다.

## S1: 공식 EXFOR M0475

- 공식 파일: https://github.com/IAEA-NDS/exfor_master/blob/5392fe533a7230d52147949b59ba8cd9b2f5c081/exforall/M04/M0475.x4
- 파일 변경 commit: `5392fe533a7230d52147949b59ba8cd9b2f5c081`.
- EXFOR 기록 수정일: 2016-04-26; 전송일: 2016-07-01.
- 내려받은 원문 텍스트 SHA-256: `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, 3349 bytes.
- 데이터·출처: `EXFOR_M0475_PROVENANCE_AND_DATA.json`.

M0475001은 liquid-helium 원통형 target, bremsstrahlung photon, reaction-particle kinematic tagging, 두 deuteron coincidence/TOF를 명시한다. M0475002는 원 논문 Table1의 12점, `EN/ANG-CM/DATA-CM/ERR-S`, 단위 `MEV/ADEG/NB/SR/NB/SR`를 보존한다. `ERR-S`는 통계오차이다. covariance, 동시 신뢰수준, 전각 law, 실험 target-electron correction, 동일입자 event/inclusive 변환식은 이 기록에 없다.

M0475003은 다른 에너지격자에서 Table2의 total SIG 여섯 점을 제공한다.

| Eγ (MeV) | SIG (nb) | ERR-S (nb) |
|---|---:|---:|
| 201 | 2.41 | 0.32 |
| 225 | 1.29 | 0.23 |
| 253 | 0.92 | 0.20 |
| 285 | 1.04 | 0.20 |
| 320 | 0.61 | 0.16 |
| 359 | 0.55 | 0.15 |

이 점들은 213/258/330 MeV DCS와 동일 에너지가 아니므로 보간/에너지모델 없이 합치지 않는다. IAEA repository의 배포 라이선스는 CC-BY-4.0로 표시된다. 원 논문에 대한 저작권과 EXFOR 데이터 배포는 구별한다.

## S2: Arends et al. (1976)

J. Arends et al., *Experimental investigation of the 4He(γ,d)d reaction*, Physics Letters B 62(4), 411–412 (21 June 1976), DOI https://doi.org/10.1016/0370-2693(76)90671-7.

Publisher: https://www.sciencedirect.com/science/article/abs/pii/0370269376906717

Publisher 페이지와 EXFOR의 논문 식별·숫자는 확인했다. 정규화 수식이 있는 원 논문 본문은 확보하지 못했다. Exa의 DOI metadata에 나온 June1은 publisher의 June21보다 낮은 우선순위다. CERN의 Hartmann1976 동일반응 문헌 레코드도 찾았으나 본문은 확보하지 못했다. 따라서 이 조사에서 Arends 자체의 event/inclusive 정의를 직접 확인했다고 기록하지 않는다.

## S3: Rice (1998) 실험 학위논문 — 핵심 원문

Bryan Joseph Rice, *The 4He(γ,dd) Reaction at Eγ=150–250 MeV*, Duke University, 1998.

공식 원문: https://nucldata.tunl.duke.edu/nucldata/Theses/PhD/Rice_1998.pdf

SHA-256: `1a16b9384b6a30ea915445d49ac44e6b529e246442e69ed11a0515655ed6fd84`. 페이지 매핑과 열람 상태는 `RICE1998_SOURCE_IDENTITY.json`에 있다.

인쇄 p114 Eq(5.4)는 동일한 outgoing deuteron에 대해 event total을 `σ_TOT=2π A0`로 정의한다. 같은 절은 대칭 Legendre fit을 사용하며, 측정하지 않은 0°/180°에서 단면적을 0으로 고정한다. p115는 Arends의 total도 같은 endpoint 제약을 둔 fit에서 추출됐다고 설명한다. 이는 Rice 자신의 실험/정의에 대한 1차 근거이며, Arends에 대한 설명은 후속 연구자의 기록이다.

pp111–113의 LEGS analyzing-power 자료는 185–237 MeV 범위다. `npd` 오염과 부족한 통계 때문에 저자는 이를 upper-limit 성격의 추정으로 취급하고, systematic error를 제시하지 않는다. 전각 polarization law 입력으로 바로 승격하지 않는다.

인용 가능 짧은 구절(이 문헌에서 총 13단어): “the total cross section is obtained by integrating over only 2π solid angle”.

## S4: Rice et al. (2000) 논문

B. J. Rice et al., *Two-deuteron photodisintegration of 4He at Eγ=150–250 MeV*, Physical Review C 61, 064612 (18 May 2000), DOI https://doi.org/10.1103/PhysRevC.61.064612.

Publisher: https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612

Publisher 초록은 coincidence로 얻은 6각도·두 energy-bin의 절대단면적, 그리고 낮은 차수 angular-fit/TME 해석을 확인한다. 본문은 subscription wall이고 해당 논문의 수식·오차를 학위논문과 같다고 자동 간주하지 않았다. 150–250 MeV 결과를 Arends의 다른 고정에너지 자료 대신 채택하지 않는다.

## EXFOR11 입력에 대한 귀결

1. S1의 12점과 통계오차를 원래 문자열로 유지한다. ±ERR-S를 선택한 sensitivity window로 사용하며 joint confidence라는 이름을 붙이지 않는다.
2. 무관한 overall event/inclusive factor가 소거되는 acceptance ratio를 연구 목표로 삼으면 원 단면적 절대정규화를 고정하지 않고 진행할 수 있다. 소거에 필요한 공통 scale 전제는 수학 계약에 명시한다.
3. 짝함수·양성 cone 및 azimuth-uniform reference는 선언한 모델족이다. Rice 원문은 과거 endpoint extrapolation이 가정이었다는 직접 동기를 제공한다. 새 degree4/8 모델의 endpoint 조건·유연성은 자체 계약과 비교해 기록한다.
4. M0475003 여섯 점은 provenance를 확보한 별도 입력이다. 현 에너지별 DCS 적합집합에는 추가하지 않는다.
5. liquid-He → bare-alpha 응답 연결, 실제 full angular/polarization law 및 photon encounter history, named deposition은 계속 별도 물리 입력이다. 이 문헌 조사로 global physical completion이나 L4/production을 변경하지 않는다.

## 게시 경계

`PUBLICATION_SAFE/`의 이 요약과 source identity/data JSON만 새 source tree에 포함해도 된다. `Rice_1998.pdf`, `rice_pages/`, `rice_toc-*.png`, OCR txt와 원문 스캔은 공개 Git 게시에서 제외한다. 원문은 링크와 hash로 참조한다. raw tool logs는 `survey/literature/`에 있다.
