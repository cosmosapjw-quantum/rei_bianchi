# RCT03D: original photon-stage residual에 optional RCT 연결

직전 RCT03B N1600의7PASS와본RCT03C frozenstage54점을다시기본과학선행조건으로돌리지않는다. sourcefree채택과production photonrouting은owner의별도결정이며현실행은그ACK가아니다.

읽기: REPORT_KO.md의3–5절, SOURCEFREE_TRANSFER.json, PHOTON_STAGE_CONTRACT.json, evidence/RESULTS.json, inputs/owner_context/{material,coupled,radiation}.rs, native/src/lib.rs.

선택한실제연결경로는원래coupled::evaluate가사용하는
r=U1-U0-dt F_nonphoto+RCT(M)-material::photo_delta(O[U0,U1])다. RCT는actualpoint의photoinput0경로에한번만결합하고,별도midpointRctIntegral장부를추가한다. O는기존radiation::transaction_path가모든event-boundedstage에서계산한다. source/cutoff/topology/부모gates를보존한다. effectiveGamma=A/(rho dt)는본interiorcrosscheck일뿐zeroabsorber에서쓰는productionAPI가아니다.

원source에쓰기전owner예약과현재blob를확인한다. implicitroot와state/event/energycandidate를한번에평가하고동시에commit한다. q_primary에RCTescape를재주입하지않고mean35eV등명시선택은atomicprediction으로부르지않는다. nH와H는각stage를따른다.

첫실행은owner의짧은photon/sourcefixture중공통EOS/source구간을명시한한경우의OFF/선택ON pair다. 원prototype의hotFT03/F08에저온RCT를그대로붙이지않는다. 기존spectralgrid와timegate를고정하고sourcefree한계는원수신된midpoint계약을비교기준으로쓴다. 실제입력이달라지면그범위를새로선언한다. 과거coarseFAIL/longhistory/small-dtFAIL은보존한다.

새adaptivecontroller나genericreferenceODE를필수로먼저작성하지않는다. 분광·시간정확도와원자모멘트권위는별도다. 현재stagefrozen검증이전체curve/statepositivity를보증하지않는다.

재현: bash run_checks.sh /absolute/new/output. snapshot을새위치에복사하여고유출력디렉터리에서특정test+54probe+고정밀verifier만실행한다. Rust1.94.1,Pythonmpmath/SymPy가필요하며code/dependency는ZIP에포함된다. 기존증거를덮어쓰지않는다.
