# REI 현재 인계 — 2026-10-25

현재 소유권 교정: ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md에 따라 reusable REI-CHEM-LEDGER-01 compiler lead는 WU088_HH, 중앙 staging은 rei_bianchi, scenario event-assembly consumer는 REI다. 역사적 unit명과 동결된 이론·수치계약은 바꾸지 않는다. 검토된 동일 source identity의 WU import를 후속 인계하며 별도 재구현은 하지 않는다. 현재 저장소별 확장 계획은 `rei_bianchi/research/program_expansion_20261025/`의 세 문서를 따른다.

```text
repo: cosmosapjw-quantum/rei_bianchi
central branch: research/orchestration-sandbox-20261022
observed HEAD: c5050305f84a051cb797cd84c84768c76bcb18b9
fixed authority: 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17
AGENTS blob:429a5a13ee75b1222bc50627f8d5973d01dd21c4
current authority packet: research/orchestration_20261025/authority/rei/ (root decides final publication path)

Read AUDIT_KO.md, DAG_DELTA.json, THEORY.md, FROZEN_COMPILER_CONTRACT.md.
New selected unit: REI-CHEM-LEDGER-01
Role: exact isotope/molecule stoichiometry + explicit electron pools + energy basis + event ownership interface.
Current status at this packet: theory DERIVED_SCOPED, mechanical implementation/run delegated by root, scientific admission pending independent reviewer.
Allowed leaf: research/rei_chem_ledger_20261025/** in root staging sandbox; no clone/worktree.
New separate cap:30CPU/120wall/512MiB,1worker,1scientific child; saved-outputSVG within same budget.
Actual runtime model UNOBSERVED; requested authority/coder tier is a role assignment.

Do not repeat: old83cohort, original L0 suites22/66, ANGTHERM01/02, stock/work/nativeHI, massive stress/strain, GRID044, donor campaigns.
Historical L0:10.110448/10CPU fail(overrun0.110448) preserved; known partial afterstrain11.449628;wholeUNKNOWN_NOT_ZERO.
ANGTHERM02 protected head8d10231b1f0f788164d5eadbe1bcee0b802cceca READ_ONLY; actual leaf PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE,10smallIVPs, no more requested.
GRID044 Library opacity:18/18PASS_SCOPED,main595.225063/600CPU NO_MORE_IVPs;continuation8.001104/10CPU. No newbudget inferred.

Actual latest REI science: HI strain190e283357f49f287ab02442a3751959cc53b4bd;deliveryb24a9daee54fc0860c4cf299c4ea5f2a977c0fd4.
L0 admitted selected algebra;L1 finite HI subunits admitted but actual birthhistory/density/IC/geometry/clock/frame/stopping pending.
L4_ready=false,globalphysicalcompletion=null.
```

이번 target 확장은 n/H1/D/T/He3/He4/Li6/Li7의 기존21population을 보존하면서, 임의의 유한 `(Z,A,isomer)` catalog와 여러 nucleus를 포함한 molecule, 음이온, 명시된 excited state와 electron pool을 표현하도록 한다. 새 fixture H−/H2/HD/LiH/HeH+와 C12/C13은 정확한 인공 수치로 interface를 검사한다. 실제 molecular rate·threshold·boundstate 또는 전체 핵종 coverage를 공급하지 않는다.

WU088_HH는 실제 isotope/molecular species와 microscopic channel/source dossier를, bass_cr는 stopping·distribution·PI/RR/secondary consumer를, BASS_HE는 angular/recoil/finite-mass event law를 공급한다. REC의 line/continuum/history와 BASS의 geometry/external matter-radiation 공급, VigilODE 수치 자료를 각 owner identity로 연결한다. 인접 외부 photon/baryon sources도 event/channel/source-history별 공급자를 명시하고 흡수 sink와 complementary reservoir를 함께 전달한다. 동일 event는 한 번만 계수한다.

Compiler PASS 뒤 next executable action은 source-qualified 한 channel의 실제 species/levels, normalization, rate/spectrum, electron/ion/photon energy/momentum partition, uncertainty를 입력 받아 연결하는 것이다. Missing provider는UNQUALIFIED, supported zero는별도 값으로 유지한다. 큰 source history/thermal/Einstein 계산은 별도 입력·cap·acceptance·owner 계약 없이 시작하지 않는다.

중앙 계획 갱신은 원40contracts/17edges/7authorities와 기존 completion/failure를 보존한 additive observation으로 한다. PR229 및 Library-only 결과를 canonical에 이미 병합되었다고 표시하지 않는다. 게시 직전 freshHEAD/AGENTS/parallel diff를 재확인하고 expected-SHA/force=false를 사용한다. 본 authority task에서는 구현·수치 실행·push를 하지 않았다.
