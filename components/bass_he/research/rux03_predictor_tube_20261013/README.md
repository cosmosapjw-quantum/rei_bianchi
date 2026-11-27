# BASS_HE THEORY07: full-rate predictor tubes and old-state reanchoring

Unit: `HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07`.

The new construction gives a source-pinned rational full H/He predictor, two physical full-Jacobian tubes through `h = 1000000000` seconds, a compact old-gas family, and a finite affine reanchoring/error-transport contract. Its actual scientific checks comprise 45 named groups in four Wolfram evaluator calls, including actual xAct/xTensor with 12 tensor residuals equal to zero. Independent adoption is recorded in `review/DECISION.json`; closeout and the next open construction are in `dossier/`.

## Read the result

- [한국어 연구 보고서](dossier/REPORT_KO.md)
- [정확한 구현 계약](dossier/CODING_CONTRACT.md)
- [주장과 전제](dossier/CLAIMS.json)
- [두 튜브의 유도](derivations/PREDICTOR_TUBE_CONSTRUCTION.md) and [실제 수치](derivations/TUBE_CERTIFICATE_NUMBERS.md)
- [Anchor 계수와 predictor](derivations/ANCHOR_RATE_ENCLOSURES.md)
- [Old-state family와 finite reanchor](derivations/OLD_STATE_FAMILY_AND_REANCHORING.md)
- [실행·입력·원응답 연결](evidence/EXECUTION_RECORD.json)
- [독립 판정](review/DECISION.json) and [다음 DAG](dossier/NEXT_DAG.json)

## Scientific identity

Parent theory: BASS_HE PR34, commit `3932669f7904f7f68f2f07dced4cf1da9d472480`. Actual retained source: rei_bianchi PR114, commit `a5c958c414dea41216b445c05f58df837f05cacb`. The full CI3/RR3/DR2/photo source, Case-A kinetic/binding escape, fixed Eulerian density/tetrad and common gas velocity are retained. The input family varies the old gas only; the six old photon inventories and external source remain fixed.

The original owner DAG and four pending native owners are unchanged. The next theoretical node is `HERE_RUX03_JOINT_INPUT_AND_TWO_STAGE_ENCLOSURE_08`, which must construct joint gas/photon input bounds and an actual two-stage domain inclusion before composing errors.

## Evidence conventions

The preserved `.wl` inputs and call JSON files define exactly what was dispatched. Raw responses, normalized results and capture records distinguish actual output from displays. Counts of internal interval witnesses and tensor residuals are separate from named check groups. No native RHS, stage iteration or ODE computation was executed in this theoretical unit.

Only source-specific derivatives, enclosures and new variations were checked. Unchanged THEORY06 evidence is reused by exact identity. Auxiliary literature/context caches and publication/backup receipts remain outside the immutable scientific payload. Full third-party paper texts and xAct package copies are not redistributed.
