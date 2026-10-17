# rei_bianchi P4/S10 native recovery: 내부·외부 공통척도 정책의 실제 연결

2026-10-17. PR191 `09814115c793bf304654a2ee0066a4772ce51ffd`에서 미실행으로 남았던 S10을 이어서 수행했다. Native parent는 P9 PR190 `512f765fd5d7496381cd4089cea4bd980b06c5f8`, source ZIP SHA256 `024fcc02b15d53c7816c9d888f98b5ec637fdcb875456028cf9f342c5f696446`. 원래 PR191의 미실행 기록을 고쳐 쓰지 않는다. 별도 add-only stage로 실행된 결과를 기록하며 이전 branch와 production PR150 owner를 변경하지 않는다.

## 실제 구현

원본 prototype kernel/tests의 Git blob `e83861538d3bab324b568d30bee566b03d66e2ba`/`ef3c26c20c15db8d858d7d8e937b654b23a66031`를 복원하고 그대로20/20 tests PASS. 새 nested_budget.rs는 원 P9 JointCxSplit에 실제 four-corner 계산을 연결한다. 같은 immutable initial/bridge/config에서 CX rtol과atol만 다르게 하여 C0/F0/C1/F1을 생성한다. 첫 loose pair가 척도 s_i=atol_i+rtol max(|C0_i|,|F0_i|)와groupunion을 정하며 그 interval의 inner ladder 동안 바꾸지 않는다.

O_i=|C1_i-F1_i|/s_i, I_i=(|C0_i-C1_i|+|F0_i-F1_i|)/s_i. Beta=.25 정책을 사용한다. I가 실패하면 같은interval에서 inner를 먼저 강화한다. I통과 후 O>.75이면 h감소. 모두 통과하면 이미 계산한 tight fine만 한번 수락. Ladder소진은StopInnerUnresolved, pair예산소진은StopWorkLimit, native source/ledger/CX작업실패는typed error다. 다음비교는직전tight를loose로재사용한다. h축소로inner소진을숨기지않는다.

409개투영(13종,numericalreservoirs,광자수/에너지/P2,source,4종photoevent,source라벨별stock). 각반단계event는자기midpointvolume으로공변변환. Coarse/fine신생광자는indexzip하지않는다. 반환Chosen.endpoint의budget은마지막반단계만이며전체intervalphotoevents는별도필드다. 비영광자제거0,phase-space병합0. Context문자열은provenancehash가아니며동일성은private계산범위와manifest로관리한다.

## 실제 측정

- Rust1.94.1 release/all-target170tests PASS (inherited140+prototype20+native10),Python8tests,strictClippy,newfile rustfmt PASS. 원본P9파일71개와물리owner12개불변;lib export만추가. 전체새crate79개.
- Native12고정구간probe. h2e9s,DII단독척도1e-7/1e-8에서각각inner1e-12/1e-14를선택. DII1e-9는I=.3120357>.25로inner미해결정지(O=.0120455는통과). 이단독DIIprofile은다른성분tolerance를의도적으로느슨하게한정책stress이며물리오차목표가아니다.
- 일반rtol1e-2/1e-3/3e-4는8e10s도달,수락8/19/28과outer거부1/4/5. DI누적9.770707197046462e-10/9.769608324803967e-10/9.769596109319143e-10com^-3. 모두inner1e-10선택. DII단독1e-8이력은2e10s까지10구간모두inner1e-14선택. DII1e-9시도는첫구간에서정지,초기상태/zero광자/source/events보존.
- 총4완료이력+1의도된inner정지,65acceptedinterval,174precisionpairs,522direct MidpointBridge.advance calls(내부RHS횟수아님),130acceptedhalfsteps. 성능가속은주장하지않는다.
- 선택격자3개를선택된inner로재생한전체AgeStepstatebits일치. 같은격자에inner1e-14를강제한3대조에서일반1e-3/3e-4최종DII차-6.40693347e-8/-6.30553743e-8m^-3. 유한비교이지globaltruth가아니다. 단독DII는애초1e-14라일치가독립정확도증명이아니다.
- Actualfour-corner성분40,082개를Python의정확한binary-rational로검산. 최초Decimal100의등식경계rounding오류는Fraction으로수리,실제실패행회귀추가,허용오차완화없음. Wolfram별도6561rationaltuple에서항등식0/부등식True/239accepted.
- 최대광자ledger5.3725519e-15,acceptedhalfstepenergy6.9435399e-16. 이것은산술잔차이지physicalerrorbound가아니다.
- 별도freshrestore170tests/8analysis/lint/build PASS.12probe+대표완료이력2개를새build로재생하여scientificCSV/전체statebits일치. 전체5이력을재실행했다고주장하지않는다. 첫runner의분석기인자오류와포장helper변수오류는기록했다.

## 가정과 판정

원MD14/50kK truncatedsource,NE16cellmean/angularGL8/birthGL2/opacity4,fullchemistry,manufacturedDdefect.0037eV,CMBbath20K,constantprescribedoff-shellBianchiI(H1.2e-16,s/H.06) regressionfixture. 비틸트scalarabsorption만. 공통편향은네계산의차이로탐지할수없고I는trueinnererror상한이아니다. Wholeagenorm/globalerrorcertificate/무조건양성stiffstable/BASSlotshell/fullEoR는미승인.

**PASS_SCOPED_NATIVE_FROZEN_NORM_INNER_OUTER_POLICY**. S10의미실행blocker는이번범위에서해소됐다. FullP4PARTIAL,SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. 다음연구cycle을자동시작하지않는다.

## 소스 복원과 전체 근거

GitHub는P9원본72파일+exactdelta8파일로전체79개nativecrate를복원한다. 아래복원기는부모/packet/outputSHA256을검사하고새폴더만사용한다. 압축은source전달형식이며photoncompression이아니다.

```bash
python RESTORE_SOURCE.py --base /path/to/restored/rei_iso_couple_p4_s9 --out /tmp/rei_s10_native
cd /tmp/rei_s10_native
# Rust1.94.1 환경 설정 후
cargo test --offline --locked --release --all-targets
cargo clippy --offline --locked --all-targets -- -D warnings
```

P9는같은repo의iso_couple_p4_s9_adaptive_20261017/RESTORE_SOURCE.py와원P8/P6기준으로복원하거나원P9FULLZIP을사용한다. FULLZIP에는모든79개파일,원prototype,검산기,40,082성분CSV,statebitfiles,이론보고서,모든로그가자체포함돼과거폴더를추가로찾을필요가없다.

FULLZIP 5085358bytes/186members/185payloadhashes. SHA256 `32addab0ba299ba288db07a163a6a6ea23949e6d5fbbe73a00cb1e4dc920e530`.
Drive: https://drive.google.com/file/d/1e_WtjL_SiEo3cMBcfgFsZ7ViN3KIclk3/view
Dropbox: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_ISO_COUPLE_P4_S10_NATIVE_20261017_FULL.zip`.
원시전체ZIP은Git에중복저장하지않고,Git에는검증가능한전체source복원표현과요약근거를게시한다. 각클라우드의ACK/content/rawrestore수준은별도publicationreceipt로기록한다.
