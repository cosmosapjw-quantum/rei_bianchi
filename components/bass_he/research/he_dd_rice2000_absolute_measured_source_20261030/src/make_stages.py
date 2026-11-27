#!/usr/bin/env python3
"""Persist science-bearing stage checkpoint notes from this bounded Rice study."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
input_hash=hashlib.sha256((R/'sources'/'RICE2000_TABLE_I_AUTHORITATIVE.json').read_bytes()).hexdigest()
stages={
'R01':('0/3','계약 고정','Rice 출판본 Table I 12 measured absolute DA를 확보하고 기존 canonical 28/88, HE14/18를 보호. 실제 물리 데이터 목표; 문헌 PDF를 public Git에 게시하지 않는다.'),
'R02':('1/3','원본 증거','Rice2000 Table I PDF4 absolute DA 12, Table II PDF5 fit8, Rice1998 thesis Table5.1 PDF115 same run early6, X4R8587는 M0826 old source. 전부 SHA와 source class를 분리.'),
'R03':('1/3','의미론 점검','Rice2000 Table I 값은 energy bin average·statistical error; systematic 7.1/13% 별도. 1998 예비값을 독립 재실측으로 합산 금지. 동일D 회전 반사점은 새 데이터 아님.'),
'R04':('1/3','물리 경로 비교','(a) 12 DA source-owned, (b) 8 Legendre total fit model alternatives, (c) photon-bin reciprocity conditional envelope, (d) pair birth kinetic support; source photon history 없으므로 rate 계산 경로 배제.'),
'R05':('2/3','직접 유도','s=M²+2ME, k²=(s-M²)²/(4s), q²=(s-4m²)/4; cap/photo^ord=2 k²/(9q²). Rice event total sigma=2πA0. cap/photo ratio interval monotone for 150–250 MeV.'),
'R06':('2/3','적대적 근거 검토','SERIAL_BLIND_REFEREE: source A0=1.31 vs total8.32 anomaly; 1998/2000 ~1.21 revision; systematics covariance null. NATIVE_DIFFERENT_AUTHOR_NOT_RUN.'),
'R07':('2/3','판별 검산','Wolfram 213 MeV photo/cap ratio38.946 compatible Silverman1984 original38.9, endpoint factors; Python PDF source token12+6 pass. 7/8 Legendre fit identities round-compatible, one source discrepancy.'),
'R08':('3/3','claim gate','Rice absolute source blocker CLOSED_SCOPED 12/12; fit8 typed, preliminary6 typed; new source DAG3/3. Physical HE remains14/18 since target photon field/stopping absent.'),
'R09':('3/3','정식화','Theory note includes exact kinematics, unit conversion, event/inclusive D, photon-bin weighting assumptions, source discrepancies, systematic reconstruction and next coupling.'),
'R10':('3/3','인계','Original source SHA, 12 published DA, 8 fit models, photon-bin conditional bounds, tagged Rice source issue and next unit captured in handoff. No automatic next node.'),
'C01':('0/3','기준 구현','Parent PR124 exact SHA fixed; original PDFs not Git-published; source original reported values, units, 12+8+6 grain and physical HOLD chosen as acceptance.'),
'C02':('1/3','자료 연결','Locked source JSON Rice Table I and II + prior thesis + user M0826 x4 request; SHA256 verified. Read-only originals, source provenance to each observation.'),
'C03':('1/3','계산식','Decimal exact mass convention and formula for bin endpoints, pair kinetic support, rho ratio; no photon energy midpoint promoted to measured sample.'),
'C04':('1/3','실행 설계','std-lib Python, direct full PDF token verifier optional with PyMuPDF; source data without PDF originals reproducible; expensive IVP and LP excluded.'),
'C05':('2/3','코딩 생산','build_rice.py emits 12-row measurement JSON/CSV, 8 alternative fits, six preliminary rows, correlated systematic NONE, physical support envelopes, source anomaly evidence.'),
'C06':('2/3','구현 테스트','Targeted unittest 28/28, compileall, immutable source-tamper rejects, exact energy s matching and same-s ratio. Commands in REPRODUCE.sh.'),
'C07':('3/3','물리 테스트','Rice paper TableI 12/12 + thesis6/6 exact PDF tokens, Silverman38.9 ratio consistency, sigma_tot 2π A0 except one original author anomaly. Source published 3/3.'),
'C08':('3/3','재현성','Source hash-locked files, deterministic JSON, generated CSV, code/test and evidence summary. No claim of runtime beyond current local execution.'),
'C09':('3/3','적대적 코드 심사','SERIAL_ADVERSARIAL: checked bin-vs-point, duplicate reflected, 1998 superseded, unknown covariance, original author typo, no rate; NATIVE_DISTINCT_AUTHOR_NOT_RUN.'),
'C10':('3/3','배포 판정','Draft child PR, source data and exact Git blobs with per-stage receipts. No merge, no force push, central28/88 HE14/18, production HOLD, next source-owned photon spectrum and fast-D stopping.'),
}
assert len(stages)==20
for stage,(progress,title,details) in stages.items():
 text=f'''# {stage} | {title}\n\n- UNIT: HE_DD_RICE2000_AUTHOR_ABSOLUTE_12_AND_EVENT_NORMALIZATION\n- SCIENCE: {details}\n- SOURCE_TABLE_I_SHA256: `{input_hash}`\n- CANONICAL_DAG: `28/88`; HE_PHYSICAL_DAG: `14/18`; NEW_RICE_SCOPED_DAG: `{progress}`; PHYSICAL_DELTA: `0`\n- BACKUP_BEFORE_EXTERNAL_MUTATION: `LOCAL_SHA256_CHECKPOINT` (specific SHA recorded in STAGE_LEDGER after publication).\n- DISTINCT_AUTHOR_NATIVE_R6_C9: `NOT_RUN`; MANUAL_ADVERSARIAL_READBACK: `SCOPED`\n- R_event=null; heat_rate=null; kappa=null; L4=false; production=HOLD.\n'''
 (R/'stages'/f'{stage}.md').write_text(text,encoding='utf-8')
print('Scientific stage checkpoints',len(stages))
