# R10K: source-support 결론 검토와 author-reproduction lane 명세 고정

## 0. 목표와 기준

repo cosmosapjw-quantum/BASS_HE. PR17 연구 branch는 research/shared-c64-crossrepo-20260928, R10I 기준 commit은 8a240af8f490a9fe519a15b837d9678bfed53405이다. PR15 expected HEAD b8b2fe47a367459f6faf6796eb2f251feacbbd7c는 변경하지 않는다. root AGENTS.md와 R10I DECISION.json/DERIVATION.md/NEXT_PROMPT_KO.md를 fresh-read한다. 최신 PR17이 앞서갔으면 현재 변경 중 관련된 부분만 확인한다.

이번 R10J는 이미 source-line trace, 도달성 증명, 조건부 고리 면적, 실제 frozen two-support probe까지 실행했다. 별도 Codex의 역할은 전달된 코드와 결론을 제한적으로 검토하고 재현하는 것이다. 이미 닫힌 R10I full query audit나 R10G endpoint/Delta solve를 다시 하지 않는다.

## 1. 패키지 identity

같은 namespace의 DELIVERY_RECEIPT.json에 실제 ZIP 이름/크기/SHA256와 두 provider ID가 있다. GitHub에 게시된 문서 subset을 전체 runtime package로 오인하지 않는다. 첨부 ZIP 또는 provider raw object에서 같은 원본 bytes를 받아 MANIFEST.json의 모든 path/bytes/SHA256을 검증한다. placeholder/error-text를 정상 contract로 처리하지 않는다.

고정 원전:
- author dataset DOI 10.17632/n43srxwdnm.1
- author archive SHA256 48a06833600ae1789ba853945d9b878837ffd9c95d08c085a3875c12cd41bc67
- arseny.f SHA256 96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78
- R10G input ZIP SHA256 90e5b3a0dbecd9fef6ef82f8cbe30f5440cd77796de615e66e66ce6fea40d6ee
- actual prepared query SHA256 01a820cf753df7adc594de47df61cfc6e315289a1848800015e6d0fd83a42b1c

## 2. 먼저 static claim을 검토한다

SOURCE_CROSSWALK.md의 author lines 1191,1593,1903,1977을 원본에서 확인한다. 마지막 RB slot은 ReRc이며 JRO=JRQ가 이를 선택한다. Appendix-A p.18도 REAL을 표시한다. 본문 Eq52의 EXTENDED와 source test desk를 혼합하지 않는다.

접근 이벤트는 outer-to-inner이며 current initial index2에서 변경된 upper event target은 항상 비어 있다. reversible approach와 absorbing-both 차이는 이 입력에서 무효지만 전체 행렬은 다르다. R10I의 WRN full-matrix 비동등/소비열 동등 판정도 유지한다.

Q23 outer annulus에서 나머지 event가 현재 입사열에 영향을 주지 않고 rotation=I인지 확인한다. p(2-p)와 pi*(bext^2-breal^2) 면적은 frozen model에서만 사용한다.

## 3. 준비된 실행기를 검토하고 한 번만 fresh 재현

Python, NumPy, SciPy 버전을 기록한다. 원 author FORTRAN을 실행/번역하지 않는다. vendor/eta_rotation.py는 R10G clean-room 원본이고 신규 generator가 아니다. package의 frozen action/fixture가 수정되지 않았는지 확인한다.

실행 예:
    PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 python -m pytest -q -p no:cacheprovider test_support_semantics.py test_runner.py
    python verify_stored_results.py
    OPENBLAS_NUM_THREADS=1 PYTHONPATH=. python frozen_support_runner.py --out /absolute/new/R10K_PREPARE
    OPENBLAS_NUM_THREADS=1 PYTHONPATH=. python frozen_support_runner.py --out /absolute/new/R10K_RUN --execute

reproduce_analytic.py의 별도 재생은 두 번째 scratch copy에서만 수행한다. 그 스크립트는 evidence를 갱신하므로 동일한 copy에서 후속 package identity 검사를 하면 실패할 수 있다. 검증된 원본 copy를 runner용으로 보존한다.

각 --out은 존재하지 않는 새 디렉터리여야 한다. archived evidence를 덮어쓰지 않는다. reproduce_analytic.py는 evidence/ANALYTIC_RESULT.json을 쓰므로 반드시 원본 ZIP에서 추출한 scratch copy에서만 실행하거나 원본 evidence를 보존한 별도 copy를 사용한다.

정확히 고정된 범위:
- two policies: PAPER_EXTENDED, AUTHOR_REAL
- SAME frozen Delta0, factor2, Coulomb trajectory, author rotational cutoff
- phase-specific S inbound/A outbound, current initial column
- rho<=25/12 a0에서 9구간, 고정 GL 32/64/128 orders; query는 bundled PREPARED_QUERY_CONTRACT.json의 hex를 사용
- max rho evaluations=2016, 새 Delta=0
- rho>25/12에서 piecewise-constant population의 해석적 면적; 모든 real/extended cutoff를 분할
- eta128/256 <=1e-7, DOP853 <=1e-8, unitarity/stochasticity <=5e-13
- 36성분의 |I64-I32|<=tol 및 |I128-I64|<=0.25tol; tol=1e-10+2e-4|I128|
- extended frozen baseline이 R10G를 재현해야 한다.

gate 실패 시 기록 후 중단한다. order/split/tolerance/rotation step을 확대하지 않는다. 새 rho/Delta 또는 dynamic-action support 비교는 이 계약에 포함되지 않는다.

## 4. 판정과 정지조건

source trace/도달성/회전/적분/baseline을 만족하면 SOURCE_SUPPORT_REVIEW_PASS를 반환한다. 독립 runtime이라는 뜻이지 outcome-blind는 아니다. 전체 WRN 동등성 또는 physical promotion을 선언하지 않는다.

R10J에서 관측한 all-six/n2n3 RMS는 REAL 1.0007748316/1.0004352047, EXTENDED 2.8001741333/1.7478122217이다. 이는 수치를 본 후 계산한 diagnostic이지 미리 정한 0.2% 합격기준이 아니다. 잔여 약0.12%를 없애기 위한 fitting/threshold 변경은 금지한다.

성공 시 다음 두 모델을 구별한 AUTHOR_REPRODUCTION_LANE_SPEC.json을 만든다:
A. author-reproduction research lane: REAL-support + frozen Delta0 + factor2 + Coulomb/author cutoff; current-input sink/basis equivalence의 제한 명시. 본 실행은 author midpoint/WRN 자체를 실행한 것이 아니며 원 action discretization identity는 주장하지 않는다.
B. 기존 physical-model research lane: F2 dynamic Delta(rho), printed EXTENDED-support. 삭제/기본값 변경하지 않는다.

이를 만든 뒤 작업을 종료한다. 추가 support interpolation, 실험 데이터 fitting, Nmax 확대, C_S_AT/MODKG, continuum, Eq55 production은 별도 연구 결정으로 남긴다.

## 5. 반환과 게시

실제 fresh refs, ZIP/query/source hashes, focused tests/commands/exits, source-support review verdict, R10J와의 numerical difference, 여섯 shell ratios/RMS, 새 Delta=0을 반환한다. 모든 원시 failure/기존 결과는 보존한다.

새 evidence는 PR17의 새 namespace에 append-only/nonforce 게시한다. 기존 Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI와 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 create-only 백업하고 upload ACK/content identity/raw restore를 구별한다. write/readback이 실제 실패하면 그대로 보고한다.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
