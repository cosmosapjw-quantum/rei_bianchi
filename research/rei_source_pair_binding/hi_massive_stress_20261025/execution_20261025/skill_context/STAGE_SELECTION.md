# Selected-stage execution contract

Stage IDs remain R1–R10 and C1–C10. Selection controls work; dependencies control
what must be read or clarified, not an automatic expansion of selection.

| User request | Work in this invocation |
|---|---|
| `1단계를 돌려줘` | active-track stage 1 only; default R1 if no track exists |
| `이론 4단계만` / `R4` | R4 only |
| `코딩 4단계` / `C4` | C4 only |
| `R1,R4` | R1 then R4; leave R2/R3 status unchanged |
| `1~4단계` / `R1–R4` | selected range only |
| `R4부터 계속` / `4단계부터 끝까지` | explicit remaining range R4–R10 |
| `전체 이론 루프` / `이론 전체 10단계` | R1–R10, reusing valid completed work |
| `다음 단계` / bare invocation | next incomplete stage only |
| `10단계만` | stage 10 only, not all ten |
| `전체 자료를 읽고 4단계만` | R4 only; “전체 자료” is not “full loop” |
| `subagent-only, R4` | R4 with actual native dispatch required |
| `문헌조사` / `literature review` | R2 only |
| `발산적 탐색` / `divergent exploration` | R4 only |
| `문헌조사와 발산적 탐색` | R2 and R4 only; preserve other stages |
| `코드 구현` / `수렴성과 전역 오차` | C5 / C8 respectively |
| `독립 검증` | R6 or C9 according to the object and active track; clarify when unresolved |

Inherit the active track from current project context, never merely the last R/C
mentioned in quoted text. Explicit R/C prefixes take precedence. If all stages are
complete, return the current completion state; start a new cycle only if requested.
A named deliverable without a number can be mapped to its relevant stage(s) from
intent; expose the chosen boundary in one sentence rather than forcing R1.

Read existing prerequisites and do lightweight stage-local support. R4 can carry
conditional assumptions and candidate equations without rerunning R1–R3. R6 checks
the supplied derivation without automatically rewriting it as an R5 campaign.
A material prerequisite gap is one explicit missing input/lemma, not permission to
run every ancestor. Complete feasible portions and record the gap.

Per-stage self-checks are part of delivering that stage. Formal global acceptance,
publishing, HPC sweeps and later-stage integration require the corresponding scope.
“PASS → next executable action” means return/checkpoint when the selected boundary
has been reached. Save only the changed stage statuses. Out-of-scope stages remain
pending, previously complete or otherwise unchanged; do not mark them NOT_APPLICABLE.

`scripts/stage_selector.py` accepts the documented grammar. The parent resolves
negation, quoted commands and mixed or complex language before calling it. It
rejects ambiguous combinations instead of silently dropping stage IDs. It never
runs research. `--completed` must contain evidence-backed completion IDs from the
current cycle, not an invented checklist.

## Natural-language selection

Use [the one-line guide](references/STAGE_GUIDE_KO.md) to map the requested output.
[STAGE_CATALOG.json](references/STAGE_CATALOG.json) stores canonical names, descriptions
and supported deterministic aliases. Explicit numeric selection controls the boundary
even when other stage names appear as background or future work. Distinctive names
select their own track; the inherited track only resolves genuinely ambiguous names.
An explicit track conflicting with a named stage requires intent resolution.

The helper keeps aliases in request order, collapses synonyms, and prioritizes a
longer stage name over contained generic aliases. Compound names select a list, not
all intervening stages. An explicit named range/tail selects its stated range.
Quotation, negation and incidental topics are resolved by the parent before passing
normalized IDs. Unknown descriptive input raises an unresolved-selection result;
only a genuine bare/next/resume request uses next-pending fallback. The helper is an
alias parser; the parent handles free-form paraphrases by consulting the guide.

Changing selection changes only this invocation. It does not prove prerequisite
stages complete, broaden permissions, or reinterpret previously saved results.

