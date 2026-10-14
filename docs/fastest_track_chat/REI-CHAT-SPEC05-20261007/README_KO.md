# SPEC05: absorption-weighted stopping and thermal error bound

Task: REI-CHAT-SPEC05-20261007. Date:2026-10-07.
판정: ABSORPTION_WEIGHTED_PREFIX_AND_THERMAL_BOUND_CONDITIONALLY_ENCLOSED.

같은FT03/S0,0..1e12s,원IC/연속source/cutoff/원자율과SPEC04의검증된tube/M/C를유지했다. 이전proof및trajectory는재실행하지않았다.

Activehazard의uniformlower m=0.660774707935660981296334917863528393869687893470832943045003 (time=t/1e12)를사용한다. 이는actualrealisedopacity가아니며passivebelowcutoff에는적용하지않는다. SX-Se의정확Duhamel식에서과거grid survival과미래continuum survival을분리한다. Early boundary에는흡수후남아exit한weight Wm,late에는현재activeweight Am를사용한다. E[SX|X-e|]는sqrt(v*u*Z2m)로제한한다. Heat survival-memory는continuouscutoff에서멈추며fullprefix와birthconvolution은유지한다.

결과 xHII<0.017088875,T<437.810K. 정확 Tupper=437.809208476466166172543467841725421488175248699588024505712.
이전679.830K보다약35.60%작지만보수적absolutebound다. Signedbias/accuracyPASS/native시간오차/물리승격은아니다.
DirectD_J<0.0113406345179446951893420761562908309252907503542247200609773,D_Q/w0<0.000161732415495572302014261794960150260922834799708834760082390.
a=1 weighted Bpast=.11840783015,Bduhamel=.11204732176; freeB=.17741581451.

Negativecontrol: k=m=1,TX=.3,Tc=.8,a=1이면실제survival차 .29148925656. free mismatch .5에exp(-1)을곱한 .18393972059는상계가아니다. 전체photonTV selfblock=0을유지한다.

Fresh3명령exit0. unit7(초기3개helperred-green,추가4개tests-after),path60,exactCauchy80,symbolic4,80digitphase39성분,feedback5성분,저장129prefix확인. NewIVP/native/cargo/campaign/parentproof재실행0. Parentarchive288payloadsha검사. Native scientific source 변경0.

외부IGMfoundation/thermal 두커밋47632ba..,a0001ca..을보존했다. 외부166tests는수신증거이지여기서재실행한것이아니다. Source-read ft03_rates blob b8a85ff..와 atomic_provider blob62211d..는부모와동일하다. 새IGMprovider를FT03에혼합하지않는다.

다음은signedbulk/boundaryprefix의별도enclosure와gasfeedback. ActualBItransaction,1e12native시간오차,physicalfit/omittedcooling은open. local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존.

전체REPORT,코드,exactinputs,independentresults,실패로그는별도sealedZIP에있다. 이폴더에는8개summary/contract/result/return/handoff/source/backup/sync자료만추가한다.
재현: python research/run_checks.py --output NEW_DIRECTORY. 기존증명과history재실행없음.

## Sealed archive

REI_CHAT_SPEC05_20261007.zip: 879584 bytes, 327 entries, 326 payload hashes.
SHA256: e904d747dfaa735cf466ed24028939839b489ccd031f892f45c47054690e66ce
Drive: https://drive.google.com/file/d/1aKoIbiATv0FmWK2r79b_UzkIAuim4OEW/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_SPEC05_20261007.zip
본문 반올림 상계는 위쪽으로 표시했다. 정확한 수치 권위는 sealed results/final_verified/ABSORPTION_WEIGHTED_THERMAL_BOUND.json이다.
