# BASS 유한 원자 저장량 소비자 — R1–R10 / C1–C10 결과

## 판정과 완료 범위

과학 판정은 **PASS_SCOPED_FINITE_BASS_ATOMIC_STORAGE_REPRESENTATION**이다. 새 이론 10단계와 코딩 10단계의 연구 내용을 수행했고, 신규 14개 test method와 실제 공급자 자료에 대한 10개 control이 첫 실행에서 모두 통과했다. 독립 primary review의 blocking finding과 required repair는 모두 0이다. 과학 실행은 1회, 재실행은 0회이다.

자원·전달 종합 판정은 **HOLD_PRESENTATION_DELIVERY_NO_GLOBAL_OR_L4_PROMOTION**이다. Planning은 계측·보수적 예약 합계 15.929490885/16 CPU s이며 이번 과학 실행은 승인 범위 안에서 끝났다. Presentation은 46.331767494/46 CPU s로 초과했다. 추가 local packaging을 멈추었고, R1–R3의 ZIP 3개와 이후 exact UTF-8 source capsule을 구별한다. 최종 C10 게시 후 실제 영수증은 delivery/FINAL_DELIVERY_RECEIPT.json 및 WORKFLOW20_ACKS.json에서 확인한다. 원문 백업을 ZIP 완료로 표시하지 않는다.

원래 연구 DAG는 **작업 33/88, 중앙 28/88**이다. 작업 32→33은 이번 실행 전에 공개 BASS B3h owner completion을 채택한 결과이며 새 REI 소비자의 원래 DAG 증가량은 0이다. 기존 88 IDs/17 edges와 계약·과거 관측을 보존했다. L4_ready=false, global_physical_completion=null이다. 이 20단계의 분모를 원래 88노드와 바꾸어 세지 않는다.

## 이미 승인된 두 작업의 결과

사용자가 승인한 finite-cohort/affine 최초 runtime 검사와 기존 전체 source ZIP은 모두 끝났다.

- Cohort 20/20, affine 16/16, 합계 36개의 최초 검사 PASS. 이전 검사를 반복한 것이 아니다.
- 최초 scientific launcher 앞에서 /usr/bin/time 부재로 exit127이 발생한 기록을 남겼다. 해당 실패에서는 runner가 시작되지 않았다. 과학 재실행은 없고 미측정 비용은 UNKNOWN_NOT_ZERO이다.
- Approved recovery science publication: 9a19c6f0a0ed5f913a3239b5712100928ddc86dd.
- 전체 source ZIP: 127 payload files / 128 entries, 3,992,645 bytes.
- SHA256: ea51d2965d6e67c8b85d45b0df19508db8c4795c644d630e03a8607fabfdce8c.
- Drive: 1wDRrBFIGPxGQpH6sjMWplGgVspfKJ1ab.
- Dropbox: id:BSpOijBcT10AAAAAAEDH4Q.
- Both completed ACK와 metadata size를 확인했다. Local CRC/hash는 한 번 수행했다. Remote full restore를 수행했다고 주장하지 않는다.
- Recovery closeout: e50a3f705204935f7801e5404b0eeca5d56061f8.

새 BASS 소비자 루프는 이 두 승인 작업 이후, 같은 명시적 cap16/46 내에서 예약한 planning0.35와 presentation0.60으로 시작했다. 과거 실패와 HOLD를 지우지 않았다.

## 조사 범위와 실제 접근 한계

SOURCE_SURVEY.json과 intake/TERMINAL_PROVIDER_DELTA.json이 조사 범위와 시간 경계를 기록한다. Accessible owner repository metadata 51개를 확인했고, 직접 연결된 7개 repo의 branch 목록은 terminal page까지 조사했다: REI282, BASS290, HE107, WU159, REC158, CR188, Vigil219, 합계1403개다. BASS205/HE102/WU150/REC139의 all-state PR 목록과 CR/Vigil 변경 PR을 읽었다. 이는 51개 repo의 모든 파일을 읽었다는 뜻은 아니다.

Dropbox root immediate472, CR177은 terminal listing이다. REI listing은 root298과 parallel317의 서로 다른 관측이므로 불일치를 그대로 남겼다. Drive는 REI document-filter22개와 지정 ID metadata 확인이며 전체 계정 전수조사는 아니다. 다른 대화 조회는 실제로 “Personal context is unavailable for this conversation.”을 반환했다. 읽지 못한 대화의 완료 주장을 공개 admission으로 채택하지 않았다.

최종 relevant delta cutoff는 2026-10-27 14:54:50 UTC이다.

| 공급자 | 확인한 새 근거 | 유지되는 경계 |
|---|---|---|
| BASS PR205 | 과학634c3046, 이후 deliverycc0e91b; result tree와 admission 동일 | 이번 선택된 finite effective-H/FLRW q=1 scope |
| CR108 | frozen2776752de6952f60d8d690a128f33fec4df2c57b 유지 | finalC9 PENDING의 기존 관측을 대체하는 공개 결과 미확인 |
| CR110 | science2eed7ef8 C9PASS, head616b166f C10본문, immutable source 양쪽R3영수증 | 다른100K conditional H1/He4모형; C10게시후 별도ACK미확인; CR108/109대체불가 |
| REC H5 | f22d6548 actual313 native-reference PASS;10016point containments,38controls,11581reviewed intervals | physicalcoverage0/313, epsilon/tube/full-stateK/M2null; observed C10deliverypending |
| HE | 12702837 ANGULAR06 snapshot 공개, 중앙8af3e56→5cabe반영 | physicalprovider/rate/globalconsumer admission false, activationfalse |
| WU R7 | f6beb6c7 primary144/reference376 보고, 당시14/20 | finalC9 및 physicalconsumer 별도 |
| Vigil | PR91 scoped59nativecontracts, V8rowwise backup-only근거 | actualREI25client/segment/tube 미제공, publicadmission gate별도 |

중앙 최신 확인 HEAD는 5cabe78f89f3ecd79d11faa29088bf30992a1017이다. 중앙 조사자는 이전74aff와 비교하여 88개 current_status와 nested contract, 88IDs/17edges/15authorities가 동일함을 확인했다. HE5개 node의 status_observation과 REC H5 owner-return 첨부만 달라졌다. 중앙 완료 수는28/88이다. Root는 변경된 REC 결정·중앙 return, CR110source/C10, HE중앙 관측 원문을 직접 읽었다.

## 선택한 새 질문

BASS는 ground,2s,2p,continuum 네 원자 재고와 atomic internal energy를 저장한다. REI의 H1I/H1II 좌표로 옮길 때 excited bound stock을 잃거나 thermal continuum 전자를 fast-electron zeta에 넣으면 유한 거래의 원자 수와 에너지 소유권이 달라진다.

이번 질문은 **이미 채택된 한 유한 거래를, 원문 잔차와 excited atomic storage 및 target ion-energy convention을 보존하며 coarse 원자 좌표로 표현할 수 있는가**이다. 새 provider solve나 물리적 history를 생성하는 문제가 아니다.

BASS 과학 source는634c3046ffccc5d00f1ab7588b5834a6eb8053ad, raw blob은a9ea559f123da6c8f1fe070139bc80145d4582fc, 크기는3,554,206bytes, SHA256은a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac이다. 원문 bytes를 보존했고 실제 실행에서 한 번 읽어 identity 검증·parse·consume했다.

## 구성과 증명

공통 왼쪽 reference volume을 Va=V0=1m3로 고정한다. Fine inventory는 N=(Ng,Ns,Np,Nc)이며 coarse inventory는 P N이다.

\[
P=\begin{pmatrix}1&1&1&0\\0&0&0&1\\0&0&0&1\end{pmatrix}.
\]

첫 행은 HI, 둘째는 HII, 셋째는 thermal free electrons이다. Bound-bound 전이 d=(1,0,-1,0)는 Pd=0이며, continuum→2p의 d=(0,0,1,-1)는 Pd=(1,-1,-1)이다. 따라서 내부 Lyalpha 사건은 coarse 원자 수를 바꾸지 않고 recombination은 thermal electron 수를 줄인다. 이 선택된 거래의 fast-zeta 사건 증분은 0이다.

중성 변화는 dg+ds+dp로 직접 계산한다. 보존 complement -dc는 진단으로 따로 남긴다. 둘의 차이인 원래 baryon residual을 clipping하거나 neutral sum을 덮어쓰지 않는다.

이미 SI로 저장된 atomic event energy를 A, target ion reference를 chiR라고 하면

\[
E_{\rm ion}=\chi_Rd_c,\qquad E_h=A-\chi_Rd_c.
\]

두 포트의 합은 A이므로 나머지 source sectors를 그대로 더하면 원래 저장 energy sum이 정확히 보존된다. E_h는 signed atomic storage/convention 포트이다. 이것을 gas heat, fast kinetic energy 또는 external work로 해석하지 않는다.

Target chiR는 명시적 decimal13.6eV×exactSI=2.17896022224e-18J이다. BASS 원래 에너지는 native binary64 EV_J의 precise lift convention으로 이미 저장돼 있다. 두 convention을 구별하며 source를 재변환하지 않는다. 정확한 target decimal convention을 native runtime bit-equivalence로 주장하지 않는다.

R=Vb/V0>0, rN=Nb-Na-d이면

\[
PN_b/R-PN_a=Pd/R+PN_a(1/R-1)+Pr_N/R.
\]

따라서 event, dilution, 원래 endpoint residual이 분리된다. Positive ba,bb가 실제 공급될 경우에만 conditional abundance 진단

\[
D_Y=PN_b/(Rb_b)-PN_a/b_a
\]

를 정의한다. Full JVP는

\[
\dot D_Y=
\frac{P\dot N_b}{Rb_b}-\frac{P\dot N_a}{b_a}
-\frac{PN_b\dot R}{R^2b_b}
-\frac{PN_b\dot b_b}{Rb_b^2}
+\frac{PN_a\dot b_a}{b_a^2}.
\]

Energy JVP는 \(\dot E_h=\dot A-\chi_R\dot d_c-\dot\chi_R d_c\)이다. 기존 variable-density endpoint/quotient 논증을 재사용하고 새 R/source/energy 좌표 결합을 확인했다. 이 양은 integrated event이므로1/H를 넣지 않는다. ddt와ddeta는 별도 clock argument로 남는다.

구성적 증명은 R5, 독립 검토는 R6, 재사용 가능한 명제는 R9에 있다. Wolfram의 새 검산은8개 exact identity가 모두0이었다. Kernel expression CPU0.00035099999999976816은 보존한CASreserve0.02안에 포함된다. Context 도구의2회internalerror도 기록했으며 kernel startup/tool 비용은 UNKNOWN_NOT_ZERO이다.

SciSpace·Exa를 이용해 Ali-Haimoud & Hirata, Physical Review D82,063521(2010), arXiv:1006.1355의 원문을 확인했다. §II.3 eq9–11의 bound-bound 항과 §III eq12–14의 QSS 문맥을 구별했다. 이 문헌은 표현의 물리적 문맥이며 이번 유한 excited stock을 정확히 ground stock과 같게 만드는 근거가 아니다. 일반 coarse graining이나 EMLA의 신규성을 주장하지 않는다.

## 실제 구현과 최초 결과

구현은 atomic_storage.py, test_atomic_storage.py, run_once.py이다. Runner는 source/code blob 결속, 엄격한 numeric-string/Fraction 처리, positive divisor guard, exact rational 저장, explicit ownership을 사용한다.

Code commit은 ba68aa31127c54108ef2ccfc99ef130e98e5a7a6이다. 세 blob은 각각 ee8afb928445e5c32abb2e1477fcfa1cd618f417, e36e0627c08ec066782856315bd7ce3e8f964021, 5a31dd0c0516355f099111ba087924bc683864bd이다.

14개 method는 일반·경계·입력 guard·새 표현을 검사했고,10개 actual-source control은 원문binding, 에너지identity, endpointsplit, thermalownership, fast0, nullfullstate, 원래residual, 실제Lyalpha coarse0/fast0, energyport중복없음을 검사했다. 두 분모를 합쳐 단일 “24test”로 표시하지 않는다.

| 실제 저장 양 | 결과 |
|---|---|
| Actual saved Lyalpha net count | 약27.074256828887243, coarse/fast 증분0 |
| 전체 HII 및 thermal electron event increment | 각각 약-31956.608899857890 /V0 |
| HI event increment | 양수 |
| HI proper-density endpoint change | volume correction을 포함하여 음수 |
| Hidden atomic storage | +8.77533431352e-18 J/V0 preview |
| Source gas thermal event energy | 약-8.69214293300880224e-16 J/V0 |
| Baryon residual | -6.67155299596e-65 preview |
| Exact-decimal source energy sum | 9.651e-82 J/V0 |
| Inherited provider MP event residual | 9.597344645419174...e-82 |
| 새 mapped energy sum minus source sum | 정확0 |

Exact numerator/denominator 문자열이 권위 있는 결과이며 preview는 표시용이다. Exact representation residual0은 물리 uncertainty0이나 공급자 residual0을 뜻하지 않는다.

Actual recipient nb와EOS/state가 없으므로 actual_native25=null, temperature_update=null, full_state_update=false이다. 물리radii eS/en/eE/geometry/temporal/total은 모두null이다. Fixture b1.4e6m^-3를 actual nb로 대체하지 않았다. Native H1I/H1II1/2, fastzeta21,wnt22,wext23,logT24의 의미와 별도 photon port를 유지했다.

## 자원 계정과 전달 실패

C6 CPU before-final0.22632999999999998, outer user0.113+system0.132=0.245CPU s, wall0.248s, exit0이다. Outer는 종료 비용을 포함하므로 내부 CPU를 다시 더하지 않는다.

Planning charge는0.245+0.002display+0.05retainedtail+0.02retainedCAS=0.317이다. 이전15.612490885에서15.929490885/16으로 기록했다. 명목잔여0.070509115는 미측정 비용을 모두 뺀 실행 가능액이 아니다. 추가 local science를 자동 승인하지 않는다.

새 checkpoint ZIP helper는 R1–R3을 만든 뒤 종료되었다. 실제 outer user0.607+system0.336=0.943CPU s, exit155, “Profiling timer expired”였다. 예약0.60을 넘었고 원인에 관한 추측은 하지 않는다. 실제 outerbound가 지켜지지 않은 실패를 보존한다. Charge0.943+0.002display+0.10retainedtail=1.045로,45.286767494→46.331767494/46이 되었다. R4ZIP은 시작하지 않았고 helper를 다시 띄우지 않았다.

기존10/30 policycap, 이번 사용자의 명시적16/46 승인, historical cumulative debit, main595.225063/600 NO_MORE_IVPs, foreign-owner budget은 각각 구별한다. Reset·transfer·알 수 없는 비용의0처리는 없다.

## 이후 직접 의무

다음 물리 진전은 source와모형이 일치하는 입력에서 시작해야 한다: frozenCR108finalC9, source-matched injection/history와recipientnb, photon measure, RECfiniteopacity, BASStransport/absorption/errorradii, HEphysicalstopping/thermalization및미분, REInativeVigilODEclient/positiveuniformtube. 선택한 모형에 필요한 직접 의무를 연결하며 모든 source alternative를 무조건AND하거나합산하지 않는다.

같은 pulse의 누적Fi를공유하고 li=prefix max lower, ui=all-timecap을적용한suffix min upper, window=[max(0,lb-ua),ub-la]를유지한다. 기존sharpness는interval/monotonicity information polytope안의결론이고 N/Eproduct는outerinformation set이다. 이새원자representation은그scope를물리전체로승격하지않는다.

PR219bootstrap, 기존83, GRID044opacity, PR221conditional과후속승인, 기존causal3189PASS·264derivatives·528FD·maxrelative2.7094758927889796e-10<2e-8을재사용했다. 새83전구간/NCP/IVP/provider solve/projection/quadrature/oldfullsuite/attempt01은실행하지않았다.

남은 전달 항목은 새 unit의 전체 source ZIP이다. 원문·code·결과·receipt를 먼저 고정·게시·양쪽백업하고, 별도승인이생기면 정적으로준비한 단일실행packager와 frozenmanifest만 사용한다. 제안cap47/reservation0.65는 아직승인되지않았다. 그승인을기존cap46허용으로간주하지않는다.

## 주요 파일

- CONTRACT.json, SOURCE_SURVEY.json, intake/TERMINAL_PROVIDER_DELTA.json
- theory/R5_CONSERVATIVE_LIFT.md, R7_SYMBOLIC_CHECK.json, R9_THEOREM_AND_CODE_CONTRACT.md
- implementation/atomic_storage.py, test_atomic_storage.py, run_once.py
- execution/FIRST_RESULT.json, FIRST_TEST_STDERR.txt, FIRST_OUTER_TIME.txt, CODE_PINS.json, C6_PREEXEC.json
- review/C9_ACTUAL_RUNTIME_REVIEW.json, C9_FINAL_DECISION.json
- results/C7_INTERPRETATION_KO.md, C8_ERROR_RESOURCE_REPRODUCIBILITY.json
- delivery/FINAL_DELIVERY_RECEIPT.json, WORKFLOW20_ACKS.json
- HANDOFF_KO.md
