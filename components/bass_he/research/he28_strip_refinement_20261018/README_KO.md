# HE28: 좁은 cutoff strip 독립 정제와 NCP 실행 준비

2026-10-18. 원본 HE27 PR75 `2a9e27ade27fb2762bc955882799b736970bb786`에 추가한 opt-in 연구다. 과학 코드 commit `62acea9141324ef176110314226cb5c40a05bf82`. 기존 HE25/26/27 및 native microphysics는 변경하지 않았다. 현재 새 native 실행은 0회이며 source-only 경량 검증만 완료했다.

## 백업에서 먼저 확인한 실제 상태

최신 HE27 백업 두 Drive 조각을 복원하고 113771104-byte 전체 SHA256 `0a08d9a505a1af9fb2f0452e2db4207789186ad7d1780b9fd5e8a522ccaf5faf`를 검증했다. October18 패키징 안에는 이미 끝난 HE27 native A/B,17/17 matrix, Radau/DOP853 비교가 들어 있다. 이는 새 October18 과학 재실행이 아니다. 따라서 원래 HE27 캠페인을 반복하지 않고, 미해결인 좁은 cutoff strip의 미래 attenuation 오차만 선택했다.

## 수학적 결과

8개 source 모멘트 (광자수, 에너지, HI/HeI/HeII photoevent 및 photoheat kernel)가 일치해도 미래 생존함수 exp[-u lambda(E)]의 모든 모멘트가 일치하는 것은 아니다. lambda=c*nH*sum(alpha_i*sigma_i), u는 proper seconds. 전개에는 lambda^2,lambda^3 등이 들어간다. Wolfram은

`d² exp(-u lambda(E))/dE² = exp(-u lambda(E)) [u² lambda'(E)² - u lambda''(E)]`

항등식과 분산 상계 대수식을 잔차0으로 확인했다. 양의 두 분포가 같은 **국소** [l,h]에서 N,U를 보존하고 f가 매끄러우면 Taylor 전개와 Var<=width²/4로 |delta integral f|<=N sup|f''| width²/4. 이 조건부 국소 정리는 현재 HE27의 전역 per-band minimum-change moment fit에 대한 rigorous spectral bound가 아니다.

## 실제 구현

`RefinedSourceModel`은 넓은 패널 분할 m과 좁은 패널 분할 r을 분리한다. r=1은 원래 격자/원래 source와 동일하다. r=2,4,8,16에서는 좁은 패널을 실제로 나누고 고정 Killing momentum, crossing proper time, state scale, 양의 8-moment source와 one-sided table을 다시 만든다. 기존 photon stock을 remap하거나 출생시각을 합치지 않는다.

파일: `src/refined_source.py`, `src/run_source_study.py`, `src/execution.py`, `src/he28_run.py`, `ncp/BOOTSTRAP.sh`. 후자는 원본 Rust lib와 unchanged HE25 owner_server를 컴파일하고 격리된 pilot을 실행하도록 완성했다. 여기서 새 Rust 컴파일/native chemistry 실행은 하지 않았다.

## 샌드박스 증거

- 27/27 pytest PASS. 독립 Drive 복원본에서 27/27 재실행 PASS.
- q=-.005,0,+.005 × m4/8/16 × r1/2/4/8/16 × birth fraction .1/.37/.9 × frozen age1e10/1e11s: 270 source-only 미래 kernel 비교.
- 기존 HE27 18개 frozen control 재현 최대 차이3.552713678800501e-15.
- 독립 physical-birth GL128/256 참조의 최대 성분 절댓값 차이1.9539925233402755e-14. 성분마다 단위가 다르므로 이를 하나의 물리적 전역 오차로 해석하지 않는다.
- 최대 global source moment relative residual2.943386384739483e-14, angle-band2.9834732969683934e-14. 기존 gate3e-13 유지.
- source table256과512는 각각210개 경계/내부점 통과. 512표 최대 global2.7522573987174383e-14, local2.809044464005892e-14. build13.8145s, 보수적 memory estimate13173840bytes. Native 호출0.

q0,m16의 최대 생존광자 오차(방출광자1개당):

| r | modes | 최대 절댓값 오차 |
|---|---:|---:|
|1|832|3.582992108563943e-8|
|2|896|1.1850303294203002e-8|
|4|1024|6.884057879297245e-9|
|8|1280|1.3721871416905174e-9|
|16|1792|1.7226467474706908e-9|

r8에서 약26.1배 줄지만 r16은 다시 커진다. 단조 수렴과 연속 스펙트럼 수렴은 HOLD. m4에서는 넓은 패널 오차가 먼저 지배한다. 이 결과는 frozen gas/source measure 비교이며 기체 온도나 실제 EoR 오차가 아니다.

초기 missing-module RED, old run_native.py import collision, NaN 비교 누락을 원시 로그로 보존하고 수정했다. 물리 tolerance 완화 없음. 별도 native subagent/독립 심사 도구는 없어 NOT_RUN. 자기 검토와 independent-variable reference를 외부 독립 심사로 부르지 않는다.

## 다음 실행

원본 owner `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`를 고정한다. 새 work directory에서 `bash ncp/BOOTSTRAP.sh`를 실행하면 q0,m4,r2,n16,GL4,table512의 native transport+Radau+DOP853 pilot을 수행한다. photon3e-15/H,energy3e-12eV/H 등의 기존 ledger와 source3e-13을 유지하며 pilot T1e-8K/fraction1e-11,reference stability1e-9K를 별도로 확인한다. 이후 m8,r2/4/8,n32/64의6개 study만 실행한다. case wall3600s,table wall600s와2GiB table cap,process-group timeout,create-only raw 기록을 제공한다. 새 model/table에 원래 native PASS를 승계하지 않는다.

## 보존

단계0/1/2는 각각 별도 commit과 Drive 아카이브로 보존하고 전부 실제 다운로드 SHA 및 압축해제를 확인했다. 전체 source package는123765bytes,SHA256 `b50eced554dcdd7a210ef5ec0346e2b5cf9be5c1b8cdb018e200a5e718f527b1`, Drive id `1GWJUJuBO0N0Sq8d6FGzdrsJgJQdUfO6A`. 50개 내부 파일 hash+독립 복원27tests 통과. 원본 native 라이브러리/바이너리는 이 작은 패키지에 포함하지 않으며 스크립트가 정확한 원본 Git 소스를 가져와 컴파일한다.

전체 패키지는 Dropbox에도 upload COMPLETED: `id:BSpOijBcT10AAAAAAD-8Tw`, `/BASS_DERIVATION_DOSSIERS_20260912/HE28_STAGE2_C6_C8_SOURCE_20261018.tar.gz`. 제공자 content_hash `709d0f2e3b57ee31ab913cb72c85a1352162feaddf1b3e97de7ac879b6ef7925`가 로컬 계산과 일치한다. Dropbox raw download는 현재 URL-download 경계에서 막혔으므로 full readback을 주장하지 않는다. 단계0 최초 Dropbox FETCH_FAILED도 별도로 보존한다. Drive의 full readback과 Dropbox metadata-content-hash 확인은 다른 보증이다.

Primary method context: Mirocha etal2012, doi:10.1088/0004-637X/756/1/94; Pawlik/Schaye2011 TRAPHIC arXiv1008.1071. Cross-repo REI195 source-free thermal clock and bass_cr79 manufactured MIDEXP 결과는 참고만 했으며 source/physics를 교체하지 않았다.
