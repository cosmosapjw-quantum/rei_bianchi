# RUN13: 동일 m2 스펙트럼 표본의 공동해와 미해상 문턱 아래 생존 성분

2026-10-18 KST. 선택 단위 `P4-S4C-SPECTRAL-EDGE-SUPPORT/M2-CONVERGENCE`.

## 결론

**PASS_SCOPED_M1_M2_COMPARISON_WITH_UNRESOLVED_SUBTHRESHOLD_COMPONENT.** RUN11에서 생성한 m2 입력을 바꾸지 않고 기본·엄격 DOP853 공동해 두 개를 초기상태부터 완성했다. m1 대비 전체 생존 광자수 변화는 8.40233834e-6 상대값, D I 누적 흡수 변화는 -1.55783805e-7이다. 같은 m2 허용오차 강화의 민감도는 훨씬 작다. 그러나 첫 셀에서 종료 에너지가 H fit 문턱 아래인 생존 성분은 51.987945% 달라졌다. 유한 표본 비교는 완료됐으나 연속 스펙트럼 수렴을 승인하지 않는다.

이번 과학적 실행은 두 m2 궤적이다. m1 기본·엄격 값은 원래 RUN11 manifest로 검증한 보존 endpoint이다. 이를 새로 재적분했다고 세지 않는다. 기존 native160개/Python11개와 새 Python10개를 실행했으며, 별도 모델·연구자·native subagent 검토는 NOT_RUN이다. 자기 재검토와 독립 시간적분기 검토를 혼동하지 않는다.

## 1. 중단 복구와 백업 우선 처리

중단 직전 RUN12 backfill은 GitHub 040a019ec47fb1eefdda67e7c9ef60c34ce000dd, Drive1MZxg8q7lTn8SreH-5chJU4FAtMvVfkr2, Dropbox id:BSpOijBcT10AAAAAAD_Krw에 이미 저장돼 있었다. 이번에 Git HEAD와 Dropbox metadata를 확인하고 Drive ZIP을 인증된 경로로 받아 SHA256 61a52684255dc754110a4b83b7aee78ad39ed5de684957b6cc71dead4f018f5b,17148847bytes를 대조했다. 완료된 backfill을 다시 업로드하지 않았다.

이 backfill의 RUN12 계산값은 이전 최종 응답을 재구성한 TRANSCRIPT_REPORTED다. raw Wolfram source/output을 회수하거나 새로 실행한 것으로 승격하지 않았다. 제조 E^-3/고정 중성밀도 모형은 이번 실제 BASS/Verner 결과에 사용하지 않았다.

이전 대화의 m2 4854구간 진행 기록에 대응하는 scratch 상태를 이번 작업공간·검색한 backup에서 회수하지 못했다. 그 진척을 계산 완료에 상속하지 않고, 원래 RUN11 입력에서 다시 시작했다. RUN11 ZIP17968344bytes의 SHA256 cd9258a2b7ca6fee8f82155d4fa2bc016ac5d05a25b061f8fcf74db3c3e2d0a8 및202payload를 검증했다. 원본은 provenance/RUN11.zip에 보존한다.

## 2. 같은 물리 입력, 다른 첫 셀의 유한 스펙트럼 표본

계량 부호(-,+,+,+), 고유시간 s, 에너지 eV, proper 수밀도 m^-3를 사용하고 c=299792458m/s,k_B=1.380649e-23J/K,epsilon_eV=1.602176634e-19J/eV를 유지했다. BASS121 SIGNED_MINUS의 prescribed Einstein–Vlasov 기하에서

\[
X=\ln(a/a_{\rm ref}),\quad a_{\rm ref}=1/21,\quad X\in[0.7,0.7004]
\]

를 적분했다. MD14/BB50k fesc=.2, 출생160개, GL8방향, Grackle/Verner/Savin/DAtomicProvider와 원래 기체 RHS를 유지했다. 초기T10000K,HII=DII=.1,He4=(.8,.15,.05),D/H2.5e-5,YHe=.245,D defect.0037eV는 기존 제조 입력이다. CMB bath=2.7255/aK는 외부 처방이다. REC donor나 정밀 isotope spectroscopy를 새로 채택하지 않았고 새 gas/photon stress로 Einstein 방정식을 다시 풀지 않았다.

첫 셀 [13.6,14.112863291954786]eV만 m1→m2로 세분한 기존 입력을 사용했다. H binding13.598434599702와 HI fit 활성 문턱13.6,D 활성 문턱13.602134599702eV를 구별한다. D는 inherited threshold-gated H-equality 근사다.

m1packet SHA86ccbb1dfa2fe68c8895658c93a8f0b2d75d3fe2695a0ef1cc1c100658fd5dc4,
m2packet SHA67ec6958ac6f662125e049003d785c917c89e832b6bcbbd026ab8a332870b88a.

m1은70400,m2는80640 physical cohorts다. m2는 정확한 ±mu 대칭 집계 뒤40320개 optical depth+37개 기체/누적량=40357변수,paired threshold6080개,6242eventpoints,6241적분구간이다. 모든 출생·교차를 유지했다. endpoint의 한쪽 활성 branch 표현은 RUN11 그대로이며 node/weight clipping이나 사후 정규화를 수행하지 않았다.

나머지47셀60160개 tuple은 바이트 단위로 같고 SHA256 ac91b49c3c620dd4610b38a58476189bff34cd8a605b87d255d42e73cb164ccc다.1280개 첫 셀 birth/direction키가 같으며 key별 count상대차 최대7.86073e-16,평균에너지 차 최대5.32907e-15eV였다. 전체 광원율·기하·IC metadata도 같다. 기존 native코드·입력·핵심Python113개 경로의 해시 동일성을 확인했다. 새 native 코드 변경은 없으며 원자 owner12개도 그대로다.

## 3. 공동 방정식과 사건·오차 관계

변수 Y_s=d n_s,U=d u,d=(a/a0)^3,출생 이후 P_alpha=B_alpha exp(-tau_alpha)를 사용한다. 기존 방정식은

\[
\tau_{\alpha,X}=\frac{c}{H}\sum_a n_{\ell_a}\sigma_a(E_\alpha),\qquad
F_{\alpha a}=\frac{c}{H}n_{\ell_a}\sigma_a(E_\alpha)P_\alpha,
\]
\[
Y_{s,X}=\frac{d}{H}G_s+\sum_{\alpha a}\nu_{sa}F_{\alpha a},\qquad
U_X=\frac{d}{H}G_u+\epsilon_{\rm eV}\sum_{\alpha a}(E_\alpha-\chi_a)F_{\alpha a}-2U.
\]

기체 RHS의 photo는 OFF이고 같은 사건이 광자·종별 변화·열·결합에너지를 한 번씩 소유한다. 기하학적 일 Wgas_X=2U와 광자 적색편이 일도 유지한다. 큰 상태벡터에서 기체 오차가 희석되지 않도록 기존 component-scaled L2 제어를 그대로 사용했다. 이는 국소 제어이지 global 정확도 보증이 아니다.

표본 k의 수치 광자 잔차를 r_k=P_k+sum_a A_ak-B_k라 하면

\[
\Delta P+\sum_a\Delta A_a-\Delta B=\Delta r
\]

이다. 이번 기본 m2−m1 대비의 좌변은 -4.07061281e-16comoving m^-3,잔차 차와의 추가 차이는 -4.35159e-21이다. 잔차 차를 실제 spectral response로 오해하면 안 된다. 특히 작은 종·작은 잔존 성분의 상대오차는 전체 광자 회계만으로 제한되지 않는다.

가정적으로 Q_m=Q_*+C h_m^4이고 h2=h1/2이면 Q1−Q2=15(Q2−Q_*)이다. Wolfram에서 이 대수 관계와 위 광자 contrast,관측차=표본차+solver오차차의 잔차를 확인했다(0,15,0). 그러나 실제 공동계의4차 점근성을 이번 두 표본만으로 증명하지 않았으므로 차이/15를 실제 오차 상계로 사용하지 않는다. m0는 다른 centroid 규칙이어서 m0,m1,m2를 같은 점근열의 세 격자로 취급하지 않는다.

## 4. 완료된 실제 계산

동일 m2packet을 rtol3e-11와6e-12에서 각각 초기상태부터 적분했다. 같은 DOP853와native원자RHS를 공유하며 새로운 Radau나 독립원자자료 대조는 아니다. m1기본·엄격값은 sealed parent의 결과다.

| 양 | m1 기본 | m2 기본 | (m2−m1)/m2 |
|---|---:|---:|---:|
| T[K] |9994.351243209323|9994.351243395630|+1.86411651e-11|
| 생존광자[comoving m^-3] |5.107816939964918e-7|5.107859857931650e-7|+8.40233834e-6|
| HI누적흡수[comoving m^-3] |5.552147290119659e-5|5.552146860921187e-5|-7.73031554e-8|
| HeI누적흡수[comoving m^-3] |4.024414265958554e-6|4.024414265955503e-6|-7.58125897e-13|
| HeII누적흡수[comoving m^-3] |3.395099851083037e-9|3.395099851082130e-9|-2.67028951e-13|
| DI누적흡수[comoving m^-3] |1.386321851859872e-9|1.386321635893413e-9|-1.55783805e-7|
| DII분율 |.10117088885157106|.10117088882903148|-2.22787222e-10|
| thermal proper[J/m^3] |5.389590542452006e-17|5.389590542451877e-17|-2.38990687e-14|

상대 열은 백분율이 아니다. 생존수+0.000840234%,DI흡수-0.0000155784%이며,전체 광원 생성량은6.0061450281933294e-5comoving m^-3로 같다. 네 photoheat성분,전체 heat,모든 chargefraction,photon/gaswork,광자에너지도 CSV/JSON에 보존했다. 큰 자릿수는 수치 비교용이지 물리 입력의 유효숫자 보증이 아니다.

m2의 허용오차를5배 강화하면 DeltaT=+1.81898940e-11K,생존수상대=-1.45100658e-15,HI흡수상대=-7.01859298e-12,DI흡수상대=-7.00270285e-12다. 두 엄격 표본의 차이는 생존수8.40233834e-6,HI흡수-7.72973639e-8,DI흡수-1.55778032e-7로 유지된다. 주요 표본 차이는 관측된 solver설정 민감도와 구별되지만 rigorous reference enclosure는 아니다. 매우 작은 He/heat 변화는 절대 크기와roundoff/solver민감도를 함께 보아야 한다.

기본m2의photonledger8.56152e-12,energy/initial1.50733e-14,energy/source8.36384e-12다. 엄격m2는각각2.07326e-12,6.65052e-15,3.69023e-12이다. 작은 보존잔차를 spectrum 정확도로 대신하지 않는다.

## 5. 전체 생존수 뒤의 미해상 성분

실제 endpoint E를 이용해 첫 셀의 생존 광자를 HI fit문턱13.6eV 아래,13.6≤E<chiD,chiD이상으로 나눴다. 첫 구간의 경계는 H화학결합에너지13.598434599702가 아니라 현재 sigma의활성문턱이다. 따라서 '문턱 아래'는 이 모델의 fit기준이다.

| 생존 성분[comoving m^-3] | m1 기본 | m2 기본 |
|---|---:|---:|
| 첫 셀 E_final<13.6 |3.963580101474543e-12|8.255385244169650e-12|
| 첫 셀 13.6≤E_final<chiD |4.651060467708421e-11|4.651060467592393e-11|
| 첫 셀 E_final≥chiD |1.141361194666945e-8|1.141361194828066e-8|
| 나머지47셀 |4.993176078650438e-7|4.993176078549643e-7|

첫 성분의 차4.29180514e-12가 총 생존수 차4.29179667e-12의 거의 전부다. 이 작은 성분의(m2−m1)/m2는0.5198794503,약51.99%다. 엄격solver에서도같은분해가유지됐다. 따라서 전체생존수변화0.000840%만보고 저에너지잔존분까지수렴했다고선언할수없다. 현존source/ray/opacity에서 추가해상도가필요하다는실제수치finding이며,고정E^-3제조모형을실제native실패증거로쓴것이아니다.

이 분석으로 곧바로 전체 spectrum이나 새로운 m4를 계산하지 않았다. 다음 leaf에서는 실제 ray와 opacity로 근문턱 에너지층의 크기를 진단하고 양의 국소 세분을 비교해야 한다. 기존 m2는 이때 baseline으로 보존한다.

## 6. 온도 변화는 가열 증가와 같지 않다

같은 마지막 기하에서 T=2U/(3k_B N_th)이므로

\[
\frac{T_2}{T_1}=\frac{U_2}{U_1}\frac{N_{\rm th,1}}{N_{\rm th,2}}.
\]

직접 endpoint에서 정규화된 U의 상대변화는-2.40282e-14,N_th의상대변화는-1.86652e-11이고, 위 비율은1.0000000000186413이다. 실제DeltaT=+1.86306352e-7K는 주로 이온화 사건 감소에 따른 열입자수 감소로 설명된다. 더 뜨겁다는 결과를 photoheat가 늘었다고 해석하면 안 된다. 실제 photoheat합은 상대-2.26615e-11,열에너지도극소감소였다. 이는 동일EOS의분해이며 정밀관측예측이아니다.

## 7. 구현, 실패와 검증

물리적 native code/inputs/solver는변경하지않았다. 새 `run13_endpoint_guard.py`는신규COMPLETE상태와모든event구간,packet/state해시,차원,finite상태,endpoint/commitmarker일치를검사한다. 과거sealed부모결과는원래manifest로검증하는별도reader를써서현재partialcheckpoint의대체경로가되지않게했다. `run13_analyze.py`는동일source비교,네사건/열량/전하분율/생존성분과EOS분해를계산한다. `run13_replay.py`와`REPLAY_RUN13.sh`는명시적인부분복원계약이다.

native160개와기존Python11개는재실행PASS,새endpointguard10개도PASS이다. 부분상태·마지막구간누락·packet변경·손상상태·endpoint불일치·eventgap 거절검사의예상실패후통과를보존했다. 처음6개예상assertion실패외에positivepath stuberror가있었으며,추가sealedparent3개는tests-after다. 모든시험을TDD라고부르지않는다. StrictClippy와기존신규native파일rustfmt를재실행했다. 새Python은unittest/byte-compilation검증이며별도Pythonlinter통과를주장하지않는다.

실패는 `evidence/run13/failures.json`에보존한다. 상대Path의부모경로오독은복원inventory압축의FileNotFoundError였고resolve후고쳤다. sealed m1에checkpoint.json이있을거라고가정한분석기오류는별도manifest-reader로수정했다. 프로세스시작전BLAS thread가고정되지않으면scalar재계산의마지막비트가다른현상은새분석CLI가한번명시적환경으로재시작하도록수정했다. 원래수치허용오차나물리상태는수정하지않았다.

새m2기본은17개chunk,엄격은12개chunk로총29개성공종료를기록했다. 각chunk는사건경계에서generationstate와SHA를먼저쓰고metadata를commit했다. 같은output의병행실행은없었다. 실제정상완료구간의적분내부wall합은327.99184917+322.900004407=650.891853577s다. 소스/모델준비,재로딩,checkpoint쓰기,설치/시험,이전분실계산,분석/복원/게시는제외한다. 최대완료processRSS1563216KiB(약1.49GiB),4GiB메모리상한,4CPUquota,BLAS/Cargo각1thread/job이었다. No local/Codex/NCP/SSH.

## 8. 복원·원격 저장 수준

봉인전 저장된 기본m2 6156→6241(85구간)을재실행해40357endpoint값의binary64동일성을확인했다. 최종ZIP은별도새디렉터리에풀어verify/build/tests/lint/compare/tail을검증하고외부DELIVERY_RECEIPT.json에실제상태를기록한다. tail은중간상태부터의부분재실행이며full m2/tight/m1 초기값문제재실행이아니다. 전체m2두해의원래실행과복원시선택재생을구분한다.

RUN13중간3071checkpoint와완료standardendpoint도Drive/Dropbox에별도로저장했다. 이들은RUN11부모입력을필요로하는중간캡슐이며독립fullZIP이아니다. 최종fullZIP에전체실행소스/입력/두endpoint/중간state/로그/부모RUN11과RUN12backfill문서를포함한다. GitHub에는실제새분석/검증/복원code와결과/DAG를add-only게시한다. historical RUN06누락Git전체checkout은이번변경분으로소급완료되지않는다. 복원은fullZIP기준이다.

완료된백업을반복하지않고최종ZIP을Drive/Dropbox에새이름으로업로드한다. 실제remoteIDs,최종SHA,providerchecksum/재다운로드/실행복원수준은외부receipt가권위다. ZIP을업로드후자신의hash를넣으려고재봉인하지않는다. toolchain,target,font,credential은포함하지않는다.

## 9. 다음 판정과 범위

다음실행점은`P4-S4C-SPECTRAL-EDGE-SUPPORT/SUBTHRESHOLD-SURVIVOR-RESOLUTION`이다. m1/m2공동해비교는완료됐지만작은subthreshold생존성분에대한추가해상도는HOLD다. m4미실행,새Radau미실행,rigorousspectral/birthcontinuum상계·각도·전체donor·Einsteinreactionfeedback·fullEoR·FLRW-CONV·BI-SIGNED·ISO-COUPLEfull·미완료Li/Be/nuclearT1–T8는그대로남긴다. 원래45/26DAG는preservedancestors에유지된다.

## 출처와 증거 구분

실제수치와실행의원전은`inputs/spectral11/m2.json`,`evidence/joint11_sided_m2_*`,`evidence/run13/`이다. 부모실행증거는`provenance/RUN11.zip`와원manifest다. SciSpace검색은목표Mirocha2012를직접찾지못했으며주변결과를채택하지않았다. Exa로원문arXiv1204.1944를확인했다. Mirocha etal2012,ApJ75694,DOI10.1088/0004-637X/756/1/94는스펙트럼표현민감도의선행문헌이지이번수치값·독창성인증이아니다.

SciPy1.17.0 solve_ivp 공식문서 https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html 는DOP853/국소오차제어의근거다. NIST DLMF3.5 https://dlmf.nist.gov/3.5 는Gauss구적나머지식의근거이며결합계의점근차수나오차상계를대신증명하지않는다. Wolfram은세대수관계(0,15,0)를검산했으며RUN12제조연구를재실행하지않았다.
