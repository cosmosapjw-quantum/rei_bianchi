"""Mechanical serialization of explicit root stage decisions; no scientific execution."""
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
BASE = UNIT.parent
NAMES = ['연구 위치·계약','근거·재사용','주장·전제 정렬','가설·표현 탐색','구성적 유도','독립 검증','판별 검증','결과 판정','정식 결과·코딩 연결','종료·재개',
         '목표·baseline','식–데이터–코드','수치 설계','실행 DAG·자원','구현','구현 검증','과학 검증','수치·재현성','독립 검토','판정·인계']
THEORY = 'unit/THEORY_AND_CONTRACT.md'
ENTRY = 'unit/ENTRY.json'
REVIEW = 'unit/review/INDEPENDENT_THEORY_STATIC_REVIEW.md'
SURVEY = 'survey/github/GITHUB_SURVEY_FINDINGS.md'
LITERATURE = 'survey/literature/PRIMARY_READ_LEDGER.md'
PROPOSAL = 'unit/execution/EXECUTION_PROPOSAL.md'
CODE = 'unit/implementation/directional_pullback.py'
DEPS = 'unit/deps/caloric_branch.py'
TESTS = 'unit/tests/test_directional_pullback.py'
RUNNER = 'unit/execution/run_once.py'
PLOT = 'unit/figures/plot_saved.py'
IDENTITIES = 'unit/execution/PREPARED_IDENTITIES.json'

# Each text records the decision already issued by root, rather than a new admission.
DECISIONS = [
('R1', 'The selected unit is the right directional derivative of the supplied monotone piecewise-affine caloric inverse with moving temperature/energy knots, plus composition with an explicitly supplied callback temperature column. PR242 head3f299062a0d0d35c17f83a9e6081ca515e9d4c4c already completed generic inversion/enclosure and the old finite-thermal tail; those results are reused. The bounded current source survey identifies this interface as distinct from the existing thermal joins and fixed-rate chemical callback.', [ENTRY,THEORY,SURVEY], 'Runtime verification and any physical recipient binding remain separate dependencies.'),
('R2', 'The exact PR242 dependency is Git blob bc3ebd682c363afc7d5c36d164406086145b6964, copied verbatim under deps. The earlier native-review chains /root/finite_thermal_blind_reviewer and /root/finite_thermal_native_blind_review share the old b77c7 source but retain distinct reports, hashes and targeted-check accounting; they are not renamed or added together. Primary-literature passage identities and actual read limits are preserved in PRIMARY_READ_LEDGER.md. Literature motivates thermal ownership and explicit derivatives; the moving-knot formula is a direct construction, not a claimed literature novelty.', [ENTRY,THEORY,DEPS,LITERATURE], 'Physical EOS/heat/rate derivative inputs remain owner-supplied; paper extracts are not copied into public stage payloads.'),
('R3', 'The nominal finite rational data satisfy 0<T0<...<Tn and U0<...<Un, hence positive finite slopes. Directions define the explicit affine epsilon family of knots and target. Temperatures are K; energy knots and target share J/reference-volume and one thermal-store convention; directions are per declared epsilon. At a lower endpoint q=v-b0 must be nonnegative, at an upper endpoint q=v-bn nonpositive. Outward directions are refused. q=0 is feasible for this affine family; a general differentiable family would additionally need actual higher-order feasibility.', [THEORY], 'No physical EOS, astrophysical normalization or physical uncertainty interval is supplied by this rational coordinate map.'),
('R4', 'Three candidates were compared: obtaining an actual recipient EOS/heat certificate (current input dependency); reimplementing PR242 inversion/enclosure (duplicate); and the constructive moving-knot derivative/callback extension (selected). On knots (T,U)=(1,2),(2,4),(4,10), E=4, fixed-knot v=1 gives1/3 while v=-1 gives-1/2. The failure of oddness distinguishes the selected directional map from an unjustified common Jacobian; it is a local example, not a global physical no-go.', [THEORY,SURVEY], 'Actual physical EOS supply remains separate; this candidate does not fill it by assumption.'),
('R5', 'The full unchanged THEORY_AND_CONTRACT.md sections3–6 carries the constructive proof. Differentiating barycentric energy interpolation gives D1, including both temperature- and energy-knot motion. At E=Uj, signed q=v-bj selects the positive-parameter side, giving D2, with exact moving-knot value aj for q=0. Unequal slopes rule out one differential by oddness; equal adjacent slopes share aj+(v-bj)/s with second-order branch mismatch. Endpoint domains are relative/one-sided. D3 is the ordinary supplied-callback expansion Jz dz+fT dT. Under matched moving affine energy coordinates, interpolation cancels Adot/Bdot terms and q scales by positive A, proving covariance.', [THEORY], 'The proof is scoped to the supplied finite branch and explicit callback derivative data; runtime controls remain unexecuted.'),
('R6', 'Actual distinct-author native reviewer /root/current_repo_census returned PASS_SCOPED_INDEPENDENT_THEORY after independently deriving D1/D2, endpoint feasibility, equal-slope differential, covariance and callback composition. The full preserved report separates its initial theory verdict from its later static-code addendum. The reviewer also performed source census and had shared-filesystem/prior context; no blind-isolation claim is made. No mathematical defect requiring repair was found.', [REVIEW,THEORY], 'Independent reasoning does not execute code or admit C6–C8/runtime C9.'),
('R7', 'Analytic controls A–G discriminate interpretations without a new numerical run. A gives11/6 with exact forward error2h/[3(1+h)] and central error−2h²/[3(1−h²)]. B gives directional1/3 and−1/2; centered5/12 is neither side slope, with1/12 positive-direction error. C uses moving q=2,−2,0 to give8/3,1,2. D separates feasible endpoints from outward refusal. E preserves the equal-slope1/2 differential. F distinguishes matched moving energy coordinates from an inconsistent one-sided transformation. G gives supplied callback(11/2,7/3) and missing-column refusal. These values have actual independent manual algebra in the report; authored tests are not executed evidence.', [THEORY,REVIEW,TESTS], 'All runtime controls remain NOT_RUN; optional saved-source derivativeH is NOT_RUN_NOT_SELECTED.'),
('R8', 'Root adopts the constructive moving-knot inverse directional map and explicit callback composition as scoped mathematics. The map is useful for a supplied caloric consumer; unequal-slope nondifferentiability is the local API property proved inR5, not a new strong no-go theorem. No literature novelty, physical EOS, temperature-history accuracy, recipient activation or uncertainty certificate is claimed. Exact analytic candidate discrimination supports this scoped adoption.', [THEORY,REVIEW], 'Actual physical temperature/native25/radii remain null; L4_ready=false/global_physical_completion=null.'),
('R9', 'The frozen three-function contract is inverse_directional(branch,energy,energy_direction,temperature_knot_directions,energy_knot_directions); inverse_linearization(branch,energy); callback_direction(fixed_temperature_jacobian,state_direction,temperature_column,temperature_direction). D1/D2 map to exact directional result and side/segment status; common coefficients map to Linearization; D3 maps to supplied rectangular callback data. Missing fT raises MissingDerivativeInput; unequal knots raise NonDifferentiableKnot; endpoints refuse unrestricted linearization via DomainBoundary. No float/tolerance substitution is permitted.', [THEORY,CODE,DEPS], 'Source correspondence and authored contract do not establish runtime behavior.'),
('R10', 'Root closes R1–R10 as complete scoped mathematics, retaining the unmodified full derivation and actual distinct-author report. The user request remains in progress: numerical/presentation allowance must be resolved before the one targeted invocation, saved-output figure, actual image inspection and executed independent code acceptance. The checkpoint is15/20 only after C1–C5 below, not a complete coding loop or complete user request. Reuse the prepared identities and command; do not rerun old units or reopen closed grants.', [ENTRY,THEORY,REVIEW,PROPOSAL], 'C6–C8 NOT_RUN, C9 static-reviewed but NOT_COMPLETE, C10 pending.'),
('C1', 'Baseline is exact PR242 head3f299062a0d0d35c17f83a9e6081ca515e9d4c4c and dependency blob bc3ebd682c363afc7d5c36d164406086145b6964. The5067-byte dependency copy matches SHA256ac5e5d50a454185550ba5614e50e914b7dad613795cf743347bd8b0b41c61aef. The local unit is an explicitly named source projection; the host has no Git checkout. Existing evaluate/inverse/enclosure/residual APIs are reused unchanged.', [ENTRY,DEPS,IDENTITIES,'unit/execution/DEPENDENCY_API_INDEX.md'], 'No dependency import/test/compile or new baseline replay occurred.'),
('C2', 'Equation-to-data-to-code mapping is explicit: D1/D2 become inverse_directional using exact knots/directions and q=v-bj; coefficient vectors become inverse_linearization inside open segments or equal-slope interior knots; D3 becomes callback_direction using supplied Jz,dz,fT,dT. Dataclasses preserve nominal T, directional T, side/segment/moving-knot status and unrestricted-linearization flag. Exact rectangular dimensions and named missing input prevent silently inferring a physical fT.', [THEORY,CODE,TESTS], 'Physical derivative sources remain missing until actually supplied; manufactured tests do not provide them.'),
('C3', 'Numerical design uses the pinned exact decoder and Fraction arithmetic only, with finite rational data and no tolerance. Knot side is determined by q=v-bj, not by a rounded slope or centered estimate. Outward endpoint directions are refused; q=0 follows the moving affine knot. Equal adjacent slopes retain a common differential while unequal slopes refuse one. Coefficient dimensions and callback shapes are validated; accidental binary floats reject.', [THEORY,CODE,DEPS,TESTS], 'The source is statically inspected; numerical/type/boundary runtime checks remain NOT_RUN.'),
('C4', 'Actual task separation is root science/contract decisions, /root/acquire_preserved_evidence mechanical source authoring, /root/current_repo_census distinct-author theory/static review, and /root/finite_thermal_blind_reviewer literature intake. Backend model telemetry is not inferred from requested tiers. One future command python -B -S execution/run_once.py --execute-authorized uses one child with1 CPU-second/10 wall-second/256MiB stops and an exclusive attempt directory. Proposed cumulative planning20/reserve2 and presentation56/reserve4 remain unapproved. PR242 historical16.586967885/50.928518494, separate native F1 display0.037, main595.225063/600 NO_MORE_IVPs, UNKNOWN_NOT_ZERO and closed grants are retained.', [ENTRY,PROPOSAL,RUNNER], 'No unclosed current-task numerical/presentation grant was established; no foreign allocation transfer or reset.'),
('C5', 'The full additive implementation, exact A–G targeted unittest source, unchanged dependency, one-shot runner and two-panel saved-result plot/packaging script are authored. PREPARED_IDENTITIES records current scientific-source bytes. The actual distinct-author report finds no mathematical or static implementation defect requiring author repair and matches the prepared identities. OptionalH is NOT_RUN_NOT_SELECTED. Authored source and static review complete C5 preparation only; no import, py_compile, unittest, plot, source replay, CAS or IVP was executed.', [CODE,TESTS,'unit/tests/__init__.py',DEPS,RUNNER,PLOT,PROPOSAL,IDENTITIES,REVIEW,'unit/execution/DEPENDENCY_API_INDEX.md'], 'C6–C8 require actual authorized execution; static C9 evidence does not complete runtime C9.')
]

def encode(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def identity(raw):
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}

def payload(relative):
    path=BASE/relative
    raw=path.read_bytes()
    return {'path':relative,**identity(raw),'encoding':'utf-8','content':raw.decode('utf-8')}

def main():
    stages=UNIT/'stages';stages.mkdir(exist_ok=True)
    capsule_dir=UNIT/'delivery/stage_capsules';capsule_dir.mkdir(parents=True,exist_ok=True)
    if any(capsule_dir.glob('*.json')):
        raise SystemExit('Immutable stage capsules already exist; do not rebuild')
    ledger=[];manifest=[]
    for ordinal,(sid,result,refs,remaining) in enumerate(DECISIONS,1):
        index=int(sid[1:])-1+(0 if sid.startswith('R') else 10)
        name=NAMES[index]
        count={'theory':min(ordinal,10),'coding':max(ordinal-10,0),'combined':ordinal,'total':20}
        note=(f'# {sid} — {name}\n\nUnit: rei_caloric_directional_pullback_20261028. Workflow1.0.0.\n'
              f'Status: COMPLETE — scoped '+('mathematics' if sid.startswith('R') else 'authored preparation')+'.\n'
              'Authority: explicit root stage decision; this document mechanically records it.\n\n'
              f'## Scientific result / preparation result\n\n{result}\n\n'
              '## Evidence references\n\n'+''.join(f'- `{p}`\n' for p in refs)+'\n'
              f'## Scope and remaining dependency\n\n{remaining}\n\n'
              'New-unit cumulative reporting order R1..R10,C1..C5: '
              f'theory{count["theory"]}/10, coding{count["coding"]}/10, combined{ordinal}/20.\n'
              'Original DAG remains working33/88, central28/88,88IDs/17edges,delta0. No original node added.\n'
              'Actual recipient temperature/native25/physical radii=null; L4_ready=false; global_physical_completion=null.\n'
              'New local scientific/figure execution: NOT_RUN; no grant inferred.\n')
        stage_path=stages/(sid+'.md');stage_path.write_text(note)
        stage_rel='unit/stages/'+sid+'.md'
        extra=[]
        if sid in ('R1','R2'):
            extra=['unit/SURVEY_SYNTHESIS_KO.md']
        if sid in ('R10','C4'):
            extra=['unit/OPEN_EXECUTION_CHECKPOINT.md']
        artifacts=list(dict.fromkeys([stage_rel,ENTRY]+refs+extra))
        capsule={'schema':'REI_COMPLETED_STAGE_CAPSULE_V1','unit':'rei_caloric_directional_pullback_20261028',
                 'stage':sid,'stage_name':name,'decision_authority':'root explicit frozen decision',
                 'status':'COMPLETE_SCOPED','cumulative':count,'original_DAG':{'working':[33,88],'central':[28,88],'IDs':88,'edges':17,'delta':0},
                 'execution':'NOT_RUN','artifacts':[payload(p) for p in artifacts]}
        raw=encode(capsule);cp=capsule_dir/(sid+'.json')
        with cp.open('xb') as stream:stream.write(raw)
        manifest.append({'stage':sid,'path':str(cp.relative_to(UNIT)),**identity(raw),'payload_count':len(artifacts)})
        ledger.append({'id':sid,'name':name,'status':'COMPLETE','scope':'mathematics' if sid.startswith('R') else 'authored preparation',
                       'evidence_refs':artifacts,'execution_state':'NOT_RUN','cumulative':count})
    for i in range(6,11):
        ledger.append({'id':'C'+str(i),'name':NAMES[9+i],'status':'NOT_COMPLETE' if i==9 else 'PENDING',
                       'evidence_refs':[REVIEW,PROPOSAL] if i==9 else [PROPOSAL],
                       'execution_state':'STATIC_REVIEWED_RUNTIME_NOT_RUN' if i==9 else 'NOT_RUN',
                       'remaining_dependency':'Explicit current allowance and actual targeted execution/figure/review' if i<10 else 'Executed outcome and final handoff'})
    record={'schema':'REI_DIRECTIONAL_STAGE_LEDGER_V1','status':'PARTIAL_PENDING_EXECUTION_ALLOWANCE',
            'authority':'Root explicitly admits R1–R10 scoped mathematics and C1–C5 authored preparation',
            'theory_complete':10,'coding_complete':5,'combined_complete':15,'total':20,
            'original_DAG':{'working':[33,88],'central':[28,88],'IDs':88,'edges':17,'delta':0},
            'stages':ledger,'new_scientific_execution':'NOT_RUN','H':'NOT_RUN_NOT_SELECTED',
            'current_numerical_presentation_authorization':'NOT_ESTABLISHED','whole_user_request':'IN_PROGRESS'}
    (UNIT/'STAGE_LEDGER.json').write_bytes(encode(record))
    (UNIT/'delivery/STAGE_CAPSULE_MANIFEST.json').write_bytes(encode({'capsules':manifest,'immutable_after_creation':True,'external_writes':0}))
    # Public summaries contain authored findings/read identities, not raw private inventories or paper extracts.
    summaries=[LITERATURE,'survey/literature/THERMAL_INTERFACE_SYNTHESIS.md']
    for relative in summaries:
        source=BASE/relative;dest=UNIT/'survey_summaries'/source.name
        dest.parent.mkdir(exist_ok=True);dest.write_bytes(source.read_bytes())
    public=[]
    for p in sorted(UNIT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(UNIT)
        if 'stage_capsules' in rel.parts or p.name=='PUBLICATION_FILES.json':continue
        if '__pycache__' in rel.parts or rel.suffix in ('.png','.zip','.pyc'):continue
        raw=p.read_bytes();text=raw.decode('utf-8')
        public.append({'path':'research/rei_caloric_directional_pullback_20261028/'+rel.as_posix(),
                       'local_path':str(p),**identity(raw),'content':text})
    (UNIT/'delivery/PUBLICATION_FILES.json').write_bytes(encode(public))
    print(json.dumps({'completed_stages':15,'capsules':len(manifest),'public_text_files':len(public),'execution':'NOT_RUN'}))

if __name__=='__main__':main()
