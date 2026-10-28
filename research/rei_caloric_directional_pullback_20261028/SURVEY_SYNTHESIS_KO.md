# 최신 근거 종합과 다음 연구 단위

조사 기준일: 2026-10-28. 저장소: cosmosapjw-quantum/rei_bianchi.
새 단위: rei_caloric_directional_pullback_20261028.

## 선택한 결과

PR242는 기존 finite_thermal_endpoint의 남은 단계와 supplied-caloric-branch 단위를 각각 20/20으로 이미 마쳤다. 실제 유도, 구현, 첫 실행, 별도 검토, 최종 저장 응답을 읽고 재사용했다. 새 작업은 그 결과가 명시적으로 제외한 **움직이는 온도·에너지 knot를 가진 역함수의 방향미분과, 명시적으로 공급된 온도 미분을 사용하는 callback 연결**이다.

고정 기준은 PR242 head `3f299062a0d0d35c17f83a9e6081ca515e9d4c4c`, science commit `853f1e3423b652f9320f9892bcab0dc8c90e95c0`이다. 기존 `caloric_branch.py`는 Git blob `bc3ebd682c363afc7d5c36d164406086145b6964`, 5,067 bytes의 원문 그대로 재사용한다. 새 branch는 `research/rei-caloric-directional-20261028`이다. 로컬 자료는 connector로 읽은 source projection이며 Git checkout이라고 부르지 않는다.

후보 세 가지를 비교했다. 실제 recipient EOS의 공급·오차 증명은 여전히 입력 의무이고, 일반 역함수·enclosure 재구현은 이미 완료된 PR242와 중복이다. 움직이는 knot 방향미분은 현재 발견한 공개 작업과 겹치지 않으며, 선언된 입력에서 닫힌 유도와 작은 반례를 만들 수 있다. 이 조사 범위 밖의 삭제·비공개·미게시 작업까지 부재를 증명한 것은 아니다.

## 실제 조사 범위

GitHub 조회는 2026-10-28T08:49:48.572Z–09:00:50.082Z에 수행했다. 최근 이력의 시작은 2026-10-25T15:00:00Z, 즉 2026-10-26 00:00 KST이다. 서로 다른 시각의 관측이므로 원자적 snapshot이라고 하지 않는다.

| 표면 | 확인한 범위 | 한계 |
|---|---|---|
| 저장소 | 접근 가능한 metadata 51개 및 마지막 빈 페이지; 관련·기초 15개 선택 | 관련 없는 36개 identity는 산출물에서 제외 |
| 현재 브랜치 | 관련 15개에서 1,469 refs, 서로 다른 repository+tip 1,442개; tip metadata 전부 읽음, 실패 0 | 모든 브랜치의 모든 파일 본문·삭제 refs·미push 작업은 아님 |
| 최근 commit | 최근 tip 81개, 끝까지 읽은 ancestor page 87개, 후속 HE/CR refresh 포함 서로 다른 commit 698개 | 오래된 날짜의 tip 아래 clock-skew ancestry는 범위 밖; commit 날짜를 push 날짜로 쓰지 않음 |
| 최근 PR | 갱신 PR 70개: REI11, REC7, BASS35, VigilODE6, CR10, WU1 | cutoff 이전의 전체 PR 역사는 읽지 않음; 제목보다 실제 source를 우선 |
| 백업 | Dropbox 선택 폴더의 끝 페이지와 Drive REI/BASS/CR/REC 관련 목록; 최근 또는 REC 관련 후보 509개 | 모든 archive 본문 복원은 하지 않음; Drive dossier는 1,000개 제한 이후 continuation 미제공 |
| 대화 | 실제 personal-context 검색과 실제 handoff 파일 | 모든 비공개 대화를 열거·페이지 이동할 도구 없음; 과거 assistant 발언은 source 탐색 단서로 취급 |
| 문헌 | SciSpace 후보 40개, Exa URL 결과 32개에서 논문 10편의 필요한 원문 구간 및 공식 코드·문서 snapshot 5개 | 후보 수는 읽은 논문 수가 아님; 전체 논문·전체 코드 인증 아님 |

원래 DAG는 작업 관측 **33/88**, 중앙 마지막 관측 **28/88**, IDs 88/edges 17, 이번 증가 0이다. 중앙 pin은 `3ec9c8c6b3a0367aa3d8d8f203e72793d33457cb`다. 이전 중앙 pin 이후 변경은 REC native-path backlink이며 count_increment=0이다. 새 연구 단위의 R/C 단계 수를 원래 DAG node 수에 더하지 않는다.

## 다른 담당자의 최신 결과와 현재 선택에 미치는 영향

| 관측된 결과 | 현재 단위에 대한 판단 |
|---|---|
| REI PR241 / VigilODE chemical restriction: 고정 외부 rates의 polynomial, exact Jacobian/remainder와 범위 witness | 실제 thermal rate derivative `f_T`와 별도 REI25 binding을 공급하지 않는다. 이를 0으로 추정하지 않는다. |
| REC PR144 native-path 20/20; reference313/313, physical0/313 | 새 전달 근거를 재사용한다. 실제 물리 certificate나 recipient EOS로 바꾸어 해석하지 않는다. |
| REC PR143 19/20와 PR145 실제313 thermal residual 실행 | 각각의 기존 독립 검토·C10 및 active owner 경로를 유지한다. |
| BASS PR226 BF3-D inverse-lapse/clock package, PR225 frozen-reset, PR223 비섭동 integration | 다른 담당자의 transport/reset/convergence 경로다. 새 caloric-knot derivative와 구분한다. |
| WU PR150 affine forcing 20/20, local27/42 | local denominator를 원래88에 합산하지 않는다. 실제 density/clock 입력은 남아 있다. |
| HE TANGENT13 S08 | 258 MeV angular-quartic aperture 문제다. 열역학 tangent의 구현 근거가 아니다. |
| CR PR114 energy-sum support R10 및 PR113 Cartesian pair support | 조건부 support 구성과 active coding 경로다. 실제 EOS/T/absolute volume/native25의 공급으로 해석하지 않는다. |

정확한 각 head, 읽은 파일과 조회 ledger는 보존된 `survey/github/GITHUB_SURVEY_FINDINGS.md` 및 연결된 snapshot에 있다. 전체 private metadata는 공개 payload에서 제외한다.

## 물리 문헌에서 재사용한 연결

고정 핵 수와 공통 비상대론적 온도를 가정하면 `N=N_H(1+f_He+x_e)`, `U=c_v N T`이다. 입자 수 변화에 따른 온도 항과 에너지 source의 소유권을 구분해야 한다. Hui–Gnedin Eq.(2)의 abundance 항과 proper-volume heating 정의가 이 대응을 뒷받침한다. [Hui–Gnedin 원전](https://doi.org/10.1093/mnras/292.1.27)

RECFAST 원전은 사용한 온도 방정식의 adiabatic/Compton truncation을 명시하며, HyRec Eq.(12)도 그 범위의 식을 사용한다. 따라서 복원된 온도만으로 물리 chemical `f_T`나 모든 열 source가 정해지지 않는다. [RECFAST](https://iopscience.iop.org/article/10.1086/312250/fulltext/995324.text.html), [HyRec](https://arxiv.org/abs/1011.3758)

DarkHistory는 ionization history에 따른 deposition feedback을 명시한다. 공개 HYREC-2의 온도 함수는 K, eV/s/cm³, ln(a) 시간 좌표와 내부 heating partition을 사용한다. 현재 공개 CAMB RECFAST는 내부 세 번째 성분으로 a*T_m을 저장한다. 이 사실들은 향후 adapter의 convention 확인 의무이며, 현재 frozen BASS 코드와 같다는 주장은 아니다. [DarkHistory](https://arxiv.org/abs/1904.09296), [HYREC-2 history.c](https://raw.githubusercontent.com/nanoomlee/HYREC-2/master/history.c), [CAMB recfast.f90](https://raw.githubusercontent.com/cmbant/CAMB/master/fortran/recfast.f90)

최근 문헌 창은 2024-10-28–2026-10-28 KST로 계산했다. 2025 DarkHistory 확장과 2026-10-19 arXiv:2602.06794v2를 구분했다. 후자는 channel별 tabulated efficiencies를 사용하는 범위로만 인용한다. Bianchi 2025 논문의 isotropic pressure/근사적으로 isotropic photon temperature 전제도 별도로 기록했다. 원문 판독 구간, OCR·버전 차이와 읽지 않은 범위는 `PRIMARY_READ_LEDGER.md`에 보존한다.

SciSpace와 Exa는 실제 검색·원문 확보에 사용했다. Wolfram은 context 검색만 수행했다. 새 evaluator/CAS 검산을 수행했다는 주장은 하지 않는다. 새로운 방향미분 식은 직접 유도했고 실제 native reviewer가 별도로 유도했다.

## 새 결과와 현재 실행 상태

전체 증명은 `THEORY_AND_CONTRACT.md`에, 실제 별도 검토는 `review/INDEPENDENT_THEORY_STATIC_REVIEW.md`에 있다. 새 함수는 `inverse_directional`, `inverse_linearization`, `callback_direction`이다.

수학적으로 확보한 범위는 open segment의 D1, moving knot의 D2, endpoint 접선 정의역, equal-slope 예외의 공통 differential, 일관된 에너지 좌표변환, 공급된 callback의 D3이다. unequal-slope knot에서 중앙차분 5/12가 어느 쪽 미분도 아니라는 exact 반례를 포함한다. 새로운 물리 no-go나 문헌 신규성은 주장하지 않는다.

R1–R10은 이 범위의 수학으로 완료, C1–C5는 실제 authored preparation으로 완료다. C6–C8은 NOT_RUN, C9는 static 부분만 검토하여 runtime admission은 NOT_COMPLETE, C10은 재개 checkpoint만 있고 완료가 아니다. 새 단위 **15/20 = 이론10/10 + 코딩5/10**이다. 이전의 두20/20 및 atomic-storage20/20은 각각 별도 단위다. 81-check와158-check도 같은 C8의 별도 근거이며 합산하지 않는다.

실제 REI temperature, native25, physical radii는 null, L4_ready=false, global_physical_completion=null이다. 이 필드는 수학적 directional map의 완성과 독립되어 있다.

## 남은 실행의 구체적 권한

PR242 최종 receipt는 planning/presentation 임시 상한의 종료와 원래10/30 복귀를 명시한다. 누적 charged planning16.586967885, presentation50.928518494와 UNKNOWN_NOT_ZERO를 보존한다. 현재 AGENTS의 원래 기준 대비50% 이상 증액에는 별도 승인이 필요하다는 조항 때문에 새 수치·figure 실행을 시작하지 않았다. 기존 owner 예약이나 main 잔여량을 가져오지 않는다.

검토 가능한 준비물은 모두 작성했다. 제안은 planning 누적 상한20 CPU-s/예약2, 단일 worker1 CPU-s/10 wall-s/256MiB의 한 번의 표적 실행, 그리고 presentation 누적 상한56 CPU-s/예약4, 4 CPU-s/30 wall-s/512MiB의 저장 결과 plot·package 한 번이다. 이 숫자는 **제안이며 미승인**이다. 실제 명령과 수용 기준은 `execution/EXECUTION_PROPOSAL.md`에 있다. Main595.225063/600 NO_MORE_IVPs는 유지한다.

