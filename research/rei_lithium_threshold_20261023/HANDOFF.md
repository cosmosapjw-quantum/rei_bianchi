# 다음 스레드 handoff — REI ANGTHERM02

아래 블록을 다음 대화에 복사해 연구를 이어갈 수 있다. 최종 commit/ZIP/provider ID의 권위 있는 기록은 기존 PR221 브랜치의 이 단위 delivery/FINAL_DELIVERY.json 또는 FINAL_DELIVERY.md를 먼저 확인한다. 이 문서는 최종 archive와 그 archive 자체의 사후 업로드 영수증을 구분한다.

## 복사용 인계

```text
rei_bianchi의 다음 연구 루프를 이어서 실행해줘.
$physmath-research-loop를 사용하고, SciSpace/Exa/Wolfram은 필요한 근거·독립 계산에 사용해줘.
sandbox에서 물리적으로 줄인 계산을 우선하고, 단계별 DAG·백업·게시·완성도와 다음 handoff를 유지해줘.

현재 완료 단위:
- ANGTHERM01: prescribed Bianchi I background 위 방향별 가스/광자 열화학.
- ANGTHERM02: PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE.
- ANGTHERM02 경로: research/rei_lithium_threshold_20261023.
- repo cosmosapjw-quantum/rei_bianchi.
- 기존 draft PR221 / branch research/rei-coupled-isotope-contract-20261022.
- PR222는 별도 브랜치 b4b5d289aaad9ef167f683f19418b0ff87ed8425; 보존.
- prepared commit1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c.
- implemented-observed commit906f217f412500fd8d4129818e70a4064439c945.
- final commit/백업은 현재브랜치의 delivery/FINAL_DELIVERY.* 확인.
- 전체 연구 또는 full coupled continuum-angular 2e-7 목표가 완료되었다고 해석하지 말 것.

우선 읽을 파일:
SCIENTIFIC_DECISION.md, REPORT_KO.md, THEORY_CONTRACT.md,
THRESHOLD_ASYMPTOTIC.md, INDEPENDENT_REVIEW.md, DAG.json,
results/comparisons.json, results/execution_summary.json,
results/cost_receipts.json, REPRODUCE.md, delivery/FINAL_DELIVERY.*.

완료된 과학 내용:
- eta*=0.10702505819804223의 saved M16 Li seed와
  원래 accepted2410nodes의 prescribed T/ne bath를 공통으로 사용.
- 주 bath: original RHS slopes의 log-Hermite; 대조: 같은 node의 log-PCHIP.
- 후기 surviving10eV cohort의 LiI 광문턱chi5.392eV를 exactsupport로 분할.
- fixed covariant measure dmu0 유지, 실제구간폭 포함 positive GL,
  movingnodes에 photonhistory를 새로 부여하지 않음.
- selected splitGL16는4Lifractions+5eventledgers=9states.
- 첫/마지막 문턱eta .4541530441897191/.7279998916870101.
- fixedM4/M8/M16 대 splitGL32 maxfraction차이:
  1.9806761651e-4 / 1.0126365102e-4 / 3.0612567325e-5.
- splitGL16/32 차이3.3626490481e-11.
- splitGL8/16 차이1.0371814518e-11; asymptoticorderfit 금지.
- fixedM16attenuated가 원래M16을190개exacttimes에서2.5929480785e-11로 재현.
- fixedM16thin/attenuated차이2.8334889990e-11.
- Hermite/PCHIPbath차이2.3851890296e-8: sensitivity이며 exactbathbound아님.
- finitefixedM16 endpointerror3.58154e-8만보면
  eta~.71975의3.06126e-5 transienterror를 놓침.
- maxmass2.44249e-15,charge2.88658e-15,
  eventenergy1.24345e-14eV/Li; floors/clipping/renorm없음.

감쇠 제어:
- frozen delta2e-8.
- same bath/seed이면0<=fIatt-fIthin<=expm1(delta)=2.00000002e-8.
- F'=r1(1-F)-exp(-delta)Lambda0 F,
  B'=YLi sigmaMax(cn/H)F;F(0)=B(0)=0.
- sigmaMax1.66e-18cm2;fitmax1.65892479072499e-18 at6.70826323365eV.
- B_last standard/tight6.032548014e-9/6.032548021e-9.
- maxB+1e-10=6.132548021e-9<2e-8, seed andinitialtau inequalitiesPASS.
- analyticconditionalcomparison과 numericalbootstrap을 구분.
- intervalarithmeticcertificate아님.
- savedM16higherbintail 극소량은 finite retainedrays에만 적용;
  unobservedcontinuumdirections 또는 unknownearlycontinuumseedbound 아님.

새 점근식:
t=etaLast-eta,
mu_c~sqrt(2beta/C)*sqrt(t),
Lambda0~A*sqrt(t),
LambdaE-chiLambda0~(2/3)chi beta A*t^(3/2).
beta=1-b'Last>0,C=1-exp(-6bLast)>0.
초과에너지가열만 extra t suppression;chiLambda0는sqrt(t).
Lambda'의1/sqrt(t) 특이성 때문에 lastcrossing time split유지.

실행/검토:
- preflight13/13, selectedIVP10/10 한 번씩 완료.
- originalfullgas/photon IVP재실행0.
- independentreview가 실제코드,10NPZ,3figures를 확인하고PASS.
- selectedcaseCPU2.095741451s,9states,1055acceptednodes.
- 총차감105.71851917CPU/135.995204254wall,예산120/180 이내.
- knownmeasured45.71851917CPU/45.995204254wall,
  unknown첫실패에는원래상한60/90을보수적차감.
- 두번scratchreset은과학10cases이전; 유실로그를복원됐다고주장하지말것.
- 이후완료cases는packaging/reassurance목적으로재실행하지말것.

다음 우선 연구:
ANGTHERM03 같은새단위에서 corrected Li eventrates의
전자수·가스에너지 피드백과 retainedbath오차를 구분하는
가장작은닫힌결합모델 또는 정당화된응답모델을 먼저유도해줘.
관측bathsensitivity2.385e-8이 splitquadrature차이3.363e-11보다크다.
초기continuumseed와earlyhighbincontinuumtail은fullhistoryclaim의
별도선행조건으로유지해줘.
이전열역학/광자장부에correctedLifraction을그대로붙여전체보존이라고하지말것.
새단위계약에서정확히어떤feedback/seed/초기광자이력을다룰지정하고
한정된검사와실행예산을고정한뒤필요계산만실행해줘.
단순히fixedangularM을다시늘리는전체sweep를기본선택하지말것.

최신주변재사용후보:
REC LINE01PR1286d32330e... detachedlineledger완료,
REC LINE02PR129c038340b... nativeLyalpha/SchurStageA,
BASS_CRPR96aa57be95... C23A/B광전자·에너지원천성분.
sources/SOURCE_ASSESSMENT.md와실제현재diff를확인해해당다음단계에만도입.
stopping/emission/sourceclosure/Einsteinfeedback이완료됐다고확대하지말것.

작업운영:
기존AGENTS와physmath정책을읽고 Astra계약·판정,
하위코딩worker구현/한정실행, freshAstra독립검토역할유지.
기존checkout사용, 새clone/worktree불필요, 원본데이터보존.
기존PR221에expected-headlease additivecommit, noforce/nomerge.
단계별prepared/implemented/final ZIP을기존Drive폴더와Dropbox경로에보존하고
실제완료응답과크기확인뒤에만백업완료라고기록.
전체목표백분율을발명하지말고완료/열림/다음의존성DAG로보여줘.
```

## 복구 위치와 정확한 입력

기본 작업 경로:
`/workspace/scratch/d5baa30c266d/rei_isotope/research/rei_lithium_threshold_20261023`.

현재 workspace가 사라졌다면 최종 ANGTHERM02 ZIP의 donor/ 아래 필요한 기존 입력이 포함되어 있다. 전체 ANGTHERM01의 별도 원자료는 다음 백업에 있다.

- ANGTHERM01 ZIP: REI_ANGTHERM01_FINAL_20261023_46519489c540.zip
- SHA256: 46519489c5406499a6c74c826fc53f1b02a46de6846773773ddc7476c0e7a036
- 크기:15,397,188 bytes,148members.
- Drive: https://drive.google.com/file/d/1p2ElUGvZfkwCxEjHme4ryXIjiCxGi6DW/view
- Dropbox ID:id:BSpOijBcT10AAAAAAD_v1g.
- M16donorSHA256:87196e8ff76689820c827e0f277ac00fc435df74e53c8c29c05e4d7fbd0399e8.
- ANGTHERM02bathdriverSHA256:710ae55ea075ac442a7f52fec24f64cff52a55edad7d5b832c46dbaa73ca6cae.
- grid044SHA256:ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b.

Prepared ANGTHERM02:
- Drive:https://drive.google.com/file/d/1eveiHxP6JYTCVU7ED-04fNI3CZIR0ruP/view
- DropboxID:id:BSpOijBcT10AAAAAAD_6VQ.
- ZIP SHA256:2e975f8f8e49c93a9ca062178166816d2c28c59760ace5ad657c1814329e75cb.
- Recovered ZIP timestamps differ from the first lost package; prepared member bytes match. This is packaging identity, not a changed scientific source.

Implemented-observed ANGTHERM02:
- Drive:https://drive.google.com/file/d/1ijIIWWaIBP0dO__Wvv0WPSYzrLS32i-a/view
- DropboxID:id:BSpOijBcT10AAAAAAD_6Vg.
- ZIP SHA256:ad0bbea0836b53f41ac36e1635634f047c540f1d5a32dda31d8f75b7dad5850f.
- This earlier checkpoint predates final figure-axis/cost/review/report updates; prefer the FINAL archive for resumption.

기존 PR221/222에 관측된 Rust fmt 실패 및 test skip은 별도 프로젝트 CI 상태이며, 이번 Python leaf의 수치결과를 소급 취소하거나 전체 CI 통과로 바꾸지 않는다. 최종 새커밋의 CI를 확인하지 않았으면 그 상태를 추정하지 않는다.

