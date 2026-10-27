# C7 — 실제 BASS 거래의 REI 원자 저장량 소비 결과

## 채택

C6의 최초 실행은 신규 test method 14/14, 실제 source control 10/10 PASS, exit 0이다. 독립 검토는 PASS_SCOPED_FINITE_BASS_ATOMIC_STORAGE_REPRESENTATION, blocking 0이다. 이 단계는 저장 결과를 해석하며 과학 실행을 반복하지 않는다.

과학 source는 BASS 634c3046ffccc5d00f1ab7588b5834a6eb8053ad, 원문 blob a9ea559f123da6c8f1fe070139bc80145d4582fc이다. PR205의 이후 전달 변경은 이 과학 결과를 바꾸지 않았다. 유효범위는 선택된 effective-H, scalar FLRW q=1, frozen-left non-Lyalpha channel/activity-clock 유한 거래이다. Incoming radiation moment/history의 조건부 성격을 유지한다.

## 실제 사건과 coarse 원자 수

fine 재고 순서는 (ground,2s,2p,continuum), coarse 순서는 (HI,HII,thermal free electrons)이다.

P = [[1,1,1,0],[0,0,0,1],[0,0,0,1]].

실제 저장 Lyalpha net count는 약 27.074256828887243이며, 해당 내부 전이의 coarse 사건 변화와 fast-zeta 변화는 정확히 0이다. 전체 유한 거래의 HII와 thermal electron 사건 변화는 각각 약 -31956.608899857890 count per reference V0이다. HI 사건 변화는 양수이며, 명시적으로 세 bound stock의 합에서 계산한 값과 conservation-complement 진단을 별도로 보존했다. Fast-zeta 사건 변화는 0이다.

실제 HI 사건 변화가 양수여도 proper-density endpoint change는 음수다. R=Vb/V0 > 1이므로 초기 재고의 volume correction이 사건 항과 함께 들어간다. 이것은 화학적 재결합 사건 증가와 팽창으로 인한 proper density 변화가 서로 다른 양임을 보여 준다.

Va=V0, d=저장 event delta, rN=Nb-Na-d에 대해 적용한 항등식은

P Nb/R - P Na = P d/R + P Na(1/R - 1) + P rN/R

이다. 마지막 source endpoint residual을 버리거나 사건을 endpoint의 대체값으로 사용하지 않았다. R preview는 1.00025473244이고 권위 있는 원문은 FIRST_RESULT.json의 exact numerator/denominator 및 source 문자열이다.

## 에너지 분해와 단일 소유권

선언한 target threshold는 decimal 13.6 eV에 exact SI를 한 번 적용한 chiR=2.17896022224e-18 J이다. 이는 target ledger convention이며 native binary floating-point runtime과 bit-equivalent라는 주장이 아니다. 공급자의 이미 J로 저장된 값은 원래 binary64 EV_J의 precise lift convention을 유지하며 다시 변환하지 않는다.

저장 atomic event energy A와 continuum 사건수 dc에 대해

Eion = chiR dc,
Ehidden = A - chiR dc

를 적용했다. Actual hidden atomic storage preview는 +8.77533431352e-18 J/V0이다. 이는 excited atomic storage와 선언된 ion-reference convention 차이를 보존하는 signed 보완량이다. Gas heat, fast kinetic energy 또는 external work로 넣지 않는다.

원래 5개 source energy port는 reference-only이고, 실제 적용 목록은 다음 6개이다.

1. rest_dust
2. target_ion_binding
3. hidden_atomic_storage
4. gas_thermal
5. ambient_radiation
6. outgoing_Lyalpha

Canonical transaction ID는 source commit, original result blob, full-finite-owner-transaction을 함께 포함한다. 원래 atomic port를 다시 더하지 않는다. Virtual 311 radiation count를 원자 stock으로 넣지 않는다. Gas thermal port는 약 -8.69214293300880224e-16 J/V0의 실제 비영 값을 보존하지만, recipient EOS 없이 temperature update로 투영하지 않는다. Geometry work와 common-V0/right-proper energy encoding diagnostic은 별도 유지한다.

## 세 잔차의 구분

| 양 | 저장 결과 | 의미 |
|---|---|---|
| 5개 저장 decimal energy의 exact 합 | 9.651e-82 J/V0 | 원문 decimal 문자열의 표현 합 |
| 공급자가 저장한 MP event-energy residual | 9.597344645419174349910605973561459254926111365074290292289550124738356e-82 | 공급자 내부 계산에서 저장한 residual lexeme |
| mapped energy sum - source decimal energy sum | 정확히 0 | 새 표현이 저장된 에너지 합을 그대로 보존함 |

앞의 두 값은 계산·표현 단계가 다르므로 하나로 덮어쓰지 않는다. 정확한 representation identity가 물리 오차 반경 0이나 공급자 원래 에너지 잔차 0을 뜻하지 않는다.

Baryon residual preview -6.67155299596e-65, source stock endpoint-minus-event residual, saved interface residual, energy endpoint/work diagnostic은 그대로 남는다. 결과를 conservation complement로 수리하거나 작은 값을 clipping하지 않았다.

## 미제공 물리 입력과 적용 경계

actual recipient nb=null, actual native25=null, temperature_update=null, full_state_update=false이다. inherited eS,en,eE,geometry,temporal,total physical radii도 null이다. 기존 b=1.4e6 m^-3는 fixture이고 이 source의 실제 recipient density로 간주하지 않는다. Conditional abundance/quotient JVP는 positive ba,bb가 명시적으로 공급될 때의 별도 함수일 뿐 이번 actual projection이 아니다.

Integrated event에는 1/H를 넣지 않는다. ddt와 ddeta clock argument를 합치지 않는다. Native25와 photon port는 별도이다. 다른 CR/BASS/WU/HE source alternative나 다른 source-matched history를 이 거래에 합산하지 않는다.

## 진행 및 근거

새 연구 내용 진행 17/20. 원래 DAG 작업 33/88, 중앙 마지막 확정 관측 28/88; 이번 REI science delta 0, 기존 88 IDs/17 edges 유지. L4_ready=false, global_physical_completion=null.

근거: execution/FIRST_RESULT.json, FIRST_TEST_STDERR.txt, FIRST_OUTER_TIME.txt, CODE_PINS.json, C6_PREEXEC.json; review/C9_ACTUAL_RUNTIME_REVIEW.json. 12자리 preview는 표시용이고 exact rational 문자열이 권위 있는 출력이다.

Planning 15.929490885/16, presentation 46.331767494/46 HOLD. 이번 단계는 재계산 없이 읽기·해석·Git 게시·원문 백업만 수행한다. 미측정 비용은 UNKNOWN_NOT_ZERO이다.
