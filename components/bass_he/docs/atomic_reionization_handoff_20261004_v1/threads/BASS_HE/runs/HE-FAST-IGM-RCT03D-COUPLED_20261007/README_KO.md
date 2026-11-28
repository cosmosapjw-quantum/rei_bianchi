# HE-FAST-IGM-RCT03D: 기존 photon path와 RCT coupled root

BOUNDED_EXISTING_PHOTON_PATH_RCT_ROOT_AND_BUDGETS_PASS__ACCURACY_AND_OWNER_ADOPTION_OPEN.

원 short-hhe-midpoint의 Newton, source/cutoff 분할, positive quadrature와 V2 kernel을 재사용했다. 실제 변경은 material/coupled/radiation 세 source의 optional RCT 연결이다. baseline State::new와 기본 OFF는 보존한다. 새 State::with_rct는 고정 source/mean을 보존하고 실제 EOS [1000,10000] K를 선택 ON에서 검사한다. RCT는 nonphoto RHS에만 들어가며 PhotoInput=0, A/B deposition은 한 번이다. MaterialOwners의 escape에는 이미 RCT가 포함되고 별도 RctOwners.escape를 global budget에 다시 더하지 않는다.

제조조건은 원 z12 FLRW 배경과 13.7..100eV/1e-15 photons/H/s source, Delta ln a=2e-4다. common RCT를 위해 초기 T30->2000 K, fractions(2e-4,0,0)->(.1,.05,.9)만 명시적으로 바꿨다. OFF/KF96/GM25, ON mean35eV, panels512, N24/48, Gauss2/4의 12개 chain과 432개 coupled step을 최종 실행했다. 모두 원 nonlinear/number/energy gate를 통과했다. 최대 allowance ratio는 .00774254653/.0000294660509/.00857915727이다. 새로운 exact-flow나 spectral accuracy 승인은 아니다.

N48/Gauss4의 최종 T는 OFF2273.68178059929, KF2273.71328892323, GM2274.21736135918 K다. KF/GM 누적 J는9.34198656679e-7/1.58795769479e-5 events/H이다. GM-OFF의 Delta T=.535580759890 K와 indirect electron/H 변화4.50975341880e-8은 이 제조모형의 결과이지 실제 원자 스펙트럼이나 관측예측이 아니다. N24->48/Gauss4의 GM 온도차9.82547417e-5K는 여전히 시간정확도 후속 대상이다.

원 owner와 수정본을 각각 빌드한 OFF 비교에서25행1000scalar(950binary64+50step/iteration)가 일치했다. 새 native12tests와 기호5식을 검사했다. 최종 fullwrapper exit0, parent/vendor52payload 불변. Exploratory와 canonical을 합쳐 selected864step과 baseline48step을 실행했지만 고유모형은12개다. 기존 과학suite/reference 재실행0, independent review/intervalcertificate NOT_RUN이다.

Zero-source 초기 실패는 기존 positive(q) guard였다. 새 selected-mode에만 q=0 및 stock=0의 정확한 zero-radiation 해를 명시했고 legacy State::new의 기존 거절은 보존했다. Late energy failure에서 old state와 모든 누적장부가 그대로임을 시험했다. 무관한 Python spreadsheet startup warning은 기록했으며 wrapper는 성공했다.

첨부 C1 SHA b56b702d...와 원격 C1 SHA0b15ce02...는 다른 artifact다. 시험 수를 합치거나 같은 backup이라 주장하지 않는다. 최신 원격의 다음 단위명 RCT03D에 정렬했다.

Git에는 요약/입력/반환/patch identity/다음지침을 게시한다. 실제 전체 original/staged source, tests, probe, 12canonical outputs와 실패/성공로그는 DELIVERY_RECEIPT의 ZIP에 있다. OWNER_RCT_DELTA.patch는 current owner3파일의 exact-base apply/hash를 통과했고, receiver igm_rct_point export가 있는 이전 staged dependency를 요구한다. 원격 receiver/root mutation0이다.

다음은 같은 coupled fixture의 temporal/spectral/observable budget이다. 기존 sourcefree N1600 성공과 photon 장기/PARTIAL 실패를 소급변경하지 않는다. HE-F2globalfalse, F09전체미완료, baselineOFF, 실제원자모멘트null, physicalHOLD와owner채택OPEN을유지한다.
