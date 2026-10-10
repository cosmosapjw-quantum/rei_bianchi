# SPEC04: 문턱 통과 구간의 FT03 열적 스펙트럼 오차

판정: THRESHOLD_OCCUPATION_THERMAL_BOUND_CONDITIONALLY_ENCLOSED_CONSERVATIVE.

같은 S0/FT03 HG CaseA HHe CI/RR/두 DR, 초기13.7eV .05/H와 연속5e-15/H/s, prescribed FLRW H=1e-14/s를 0..1e12s에서 비교했다. Native 시간분할이 아닌 고정격자 exact-time 대 연속에너지 exact-time의 차이다. SPEC03의 초기 rare-hit bound를 장시간에 외삽하지 않았다.

1. 비흡수 격자의 최초 cutoff 아래 도달시간 T_Delta와 연속 cutoff 시각 Tc를 비교했다. S(a)=Pr(T_Delta>a), z(a)=integral_0^a S이면 B(a)=a-z(a) (a<=Tc), B(a)=Tc+z(a)-2z(Tc) (a>Tc)다. B는 문턱 상태가 불일치하는 시간의 기대 길이이며 이른/늦은 도달 모두 포함한다. Tc=7.32604009207288e11s, mean exit=7.33707454245021e11s, std=2.58900637426194e11s, B(1)*1e12=1.77415814506534e11s다. 이것은 실제 흡수 후 생존확률이 아니다.
2. 실제 cutoff jump를 sigma_c 및 (Ec-chi)*sigma_c로 분리하고 나머지의 Lipschitz 경계와 에너지분산을 사용했다. 전 prefix count/heat forcing에는 초기광자와 실제 continuous-birth convolution을 모두 넣었다. Cutoff flag/provider를 바꾸거나 source를 pulse로 바꾸지 않았다.
3. 새 gas first-exit tube는 nominal xH [.9,.9635], xHeII [.3,.3003], xHeIII [.59994,.6], w/w0 [.971,1.0005]다. 실제 초기면은 pinned binary64 값을 포함한다. 원 FT03 interval nonphoto RHS와 총 photoevent<=.055/H로 닫았다. Ttube=[47129.41109058,50025.23641820]K. 이전 radius .02 tube의 무단 외삽이 아니다.
4. Gas4+common-birth survival TV의5block에 전체 누적 forcing을 전파했다. Passive photon도 TV에 포함하므로 radiation diagonal upper=0이며 음의 최소흡수율을 전광자에 적용하지 않았다. b'=M b+C d, e<=d+b를128slab에서 누적했다.

조건부 absolute upper: xHII<.026467314, xHeII<5.058925e-6, xHeIII<5.492998e-7, w/w0<9.120518e-4, T<679.830K. 매우 보수적이며 accuracy gate PASS 또는 signed thermal bias certificate가 아니다. 부모 native-time 인증은1.25e9s에 한정되어 있으므로 이를1e12s에 합성하지 않았다.

독립 실제 thermal reference: grid xH=.9377313551829972,T=47942.4645619292K; continuum xH=.938940348181805,T=47917.6292226325K. Cont-grid Delta xH=.001208992998807834, Delta T=-24.83533929670375K. Grid photoevent 상대차=-3.638079258%, heat상대차=+3.930274362%. Shadow D_J=-.001415065513203/H와 D_Q/w0=6.10070376572e-6이며 실제 gas오차는 단순 -D가 아니다. 수치참조는certificate입력이 아니며 age-moment K6/K8 차이는 별도 엄밀한 truncation 증명이 아니다.

최종3명령exit0. Unit3,exact stopping80,symbolic5,derivative17,independent90digit phase3/feedback5,referenceprefix129. 새reference는6variants/10IVPsegments/max32변수. Native/cargo/oldcampaign/부모증명 재실행0. Parent235 payload의hash만확인했다.

새 boundary helper의post-cutoff branch 오류와 exactdecimal .3 lowerface가 binary64 IC를 배제한 오류를 각각 red/green으로 고쳤다. 실패코드/로그보존,원물리식/허용오차수정없음. 나머지검사는tests-after다. 산술신뢰base는계승된Decimal60 directed연산과expanded-nearest exp/ln이며formalindependentproof없음.

다음 SPEC05_ABSORPTION_WEIGHTED_STOPPING_BOUND는 실제 survival가중 early/late occupation과bulk signed cancellation으로 느슨한경계를개선한다. ActualBI첫rawtransaction은별도open. OriginalCODEX_SYNC/runtime_returns/F00/F03/FT03/S0와 local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존.

## 재현 패키지

REI_CHAT_SPEC04_20261006.zip: 624680 bytes,289 entries,288 payload hashes.
SHA256: 16e62e72a7b9659850dc979c2a4175ddc89580a4b1e773fd0f134b5c7912dc5d
Drive: https://drive.google.com/file/d/1RvUHfEyR169On3O5kYqOslazg-f6ER5C/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_SPEC04_20261006.zip

전체REPORT_KO.md,source/실패기록/원입력/독립검산은ZIP의rei_chat_spec04_20261006/ 아래다. 최종authority는results/final_verified/FINAL_VERIFICATION.json과THRESHOLD_THERMAL_BOUND.json. 재현은 python research/run_checks.py --output NEW_DIRECTORY. 기본runner는새interval증거를계산하고저장reference를검사하며native/IVP재실행없음. check_thermal_reference.py직접실행만새10개IVPsegments추가.

이repo폴더에는8개요약/계약/인계/영수증만추가했다. 두backup은R1metadata확인이며remote전체restore나bytehash검증은없다.
