# C12 전체 이력 실행 복구와 local Codex 재개

이 문서는 복구 절차이며, 이 문서를 작성하면서 원격 다운로드·복구·수치 실행을 수행하지 않았다. 기존 업로드 ACK와 해시 증거는 `UPLOAD_VERIFIED`의 해당 범위일 뿐 `RESTORE_VERIFIED`가 아니다. 실제 복구 뒤에는 수행한 파일 검증과 새 실행 결과를 별도 기록한다.

후속 연결 대상은 versioned source를 유지하고 composite log-q opacity candidate를 명시적으로 묶는 `C2_FULL004`다. **이 문서 수정 시점에는 failure67 후속 후보의 scoped review가 아직 완료되지 않았으며, root가 그 review 이후에만 새 child를 생성한다.** 앞선 단일128/256 refinement는 한 macro를 수용한 뒤 다음 attempt67에서 다시1e-7 기준을 충족하지 못했고, 실패를 그대로 보존했다. 새 후보의 좌표·panel 정책·실제 source/absorption 경로와 SHA는 최신 선택 bundle과 review에서 읽으며 과거 후보 버전을 고정 가정하지 않는다. 복구 문서나 candidate 구현만으로 실행 GO를 부여하지 않는다. 실제 활성 run·generation·cursor·남은 예산·실행 허용 여부는 같은 최종 게시 단계의 `STATE.json`, `HANDOFF.json`, 실제 journal 및 review 결정에서 읽는다. 아래 경로는 별도 명시가 없으면 `rei_bianchi` repo root 기준이다.

## 먼저 읽을 파일

1. `research/accel02_20261011/q1b/c12/STATE.json`
2. `research/accel02_20261011/q1b/c12/HANDOFF.json`
3. `research/accel02_20261011/q1b/c12/GIT_EVIDENCE_SCOPE.json`
4. `research/accel02_20261011/q1b/c12/PUBLICATION_RECEIPTS.json`
5. `research/accel02_20261011/q1b/c12/review/FAILURE42_DECISION.json`, `FAILURE42_ACTUAL_ADDENDUM.json`, 그리고 최신 HANDOFF가 지목하는 failure66·67/opacity candidate 결정과 실제 실행 addendum
6. `research/accel02_20261011/q1b/c12/NEXT_DAG.json`

Composite log-q 후보의 수학적 선택은 `research/accel02_20261011/q1b/c12/repair/opacity_math_v3/STRATEGY.json`과 `COMPOSITE_LOGQ_DERIVATION.md`에 있다. 현재 선언은 threshold별 양의64/128 Gauss panel, `|p|Δx≤4`, 최대128 panels이며, 기존 moment-fit1e-12와 response1e-7을 유지한다. 이는 동일한 positive closure의 적분좌표 변경 후보이며 보편적인 유한차수 오차 정리나 전구간 승격이 아니다. 실제 채택은 review와 bundle의 명시된 numerical identity가 결정한다.

Git에는 구현·문서·review·전체 파일 SHA manifest·각 chunk의 launch/result/exit/log receipt가 남는다. 새 bulk checkpoint 배열·누적 metadata·native map payload는 모두 Git blob으로 중복 게시되지 않는다. 따라서 **Git checkout만으로 최신 실행 복구가 완료되지는 않는다.** 최종 게시 Git의 `GIT_EVIDENCE_SCOPE.json`이 지목한 전체 stage archive가 필요하다. Archive는 upload 이전 immutable snapshot이라 그 안의 scope/receipt가 해당 stage보다 한 단계 이전일 수 있다. Archive 선택의 authority는 아래에서 checkout 밖에 저장하는 최종 Git receipt이며, archive 내부의 이전 receipt가 아니다.

## 필요한 입력과 다운로드

기본 묶음은 `REI_ACCEL02_C11R4_FINAL_20261011.zip`이다. SHA256은 `efadfe355a743b91f5e80212cabc2c8a177eeec3c69316ca946b827589748949`, 크기는2091483 bytes다. Drive object는 `1g7wKiBfRu5ZilgNDT2VNVth34OQSqZV2`, Dropbox object는 `id:BSpOijBcT10AAAAAAD4Hkg`다. 이 archive에는 C11 증거, 원래 dependency closure와 두 native binary가 포함된다. 환경 전체나 Git 이력을 포함하는 독립 설치본은 아니다.

그 위에 C12 최신 전체 stage archive를 덮어쓴다. 정확한 파일명·SHA·크기·provider object ID는 최신 `GIT_EVIDENCE_SCOPE.json#/archive`와 `PUBLICATION_RECEIPTS.json#/stages`가 기준이다. 예를 들어 이 문서 작성 당시 확인된 항목은 `REI_ACCEL02_C12R6_REPAIR_NATIVE_TRIALS_20261011.zip`이며, SHA256은 `80425ef858513e4746466d733544547f903a5bb8a76d51b7911584a150472761`,30813153 bytes, Drive `1OBWfRlSneiNEam7-05FEJhbb1YaPEGZ0`, Dropbox `id:BSpOijBcT10AAAAAAD4IgQ`였다. 이후 단계가 게시되면 그 단계의 항목을 사용한다.

다음 과거 객체는 사용하지 않는다: `REI_ACCEL02_C12R3_CONTINUATION_021_20261011.zip`은 잘린 ZIP으로 분류되어 있다. 해당 단계가 꼭 필요하면 `_REPAIRED_` 파일만 유효하며, 최신 전체 archive가 이를 포함하면 과거 단계들을 순서대로 모두 내려받을 필요는 없다. `failed_publication_attempts`에 기록된 실패 객체의 ACK를 성공 근거로 재사용하지 않는다.

Drive 또는 Dropbox에서 선택한 정상 객체들을 로컬의 별도 다운로드 디렉터리에 준비한다. 파일명을 receipt와 맞추되 실제 bytes/SHA를 먼저 확인한다. 브라우저가 붙인 `.bin`·`(1)` 같은 접미사를 이름만 보고 동일성 근거로 삼지 않는다. 양쪽 provider를 모두 다운로드할 필요는 없다. 하나의 완전한 객체를 검증해 복구하고, 다른 provider의 기존 백업 상태는 별도로 보존한다.

### 큰 archive의 분할 전송

Drive connector는 개별 파일이104857600 bytes(100 MiB)를 넘으면 업로드를 거부한다. 실제 C12R13 단일 ZIP 전송에서 HTTP413이 발생한 이유는 이 connector 한도이며, 이것만으로 과학 데이터나 로컬 ZIP의 손상을 뜻하지 않는다. 이 경우 원래 ZIP bytes를 최대67108864 bytes(64 MiB)의 raw part로 분할해 전송한다. 수치 내용·ZIP 내용·checkpoint identity는 바뀌지 않는다.

최종 `GIT_EVIDENCE_SCOPE.json#/archive`의 `parts` 및 연결된 transport manifest에서 각 part의 index·정확한 이름·bytes·SHA·provider ID를 읽는다. 형식은 `RAW_ZIP_BYTE_PARTS_CONCATENATE_IN_INDEX_ORDER`이며, `.zip.part001` 등은 각각 독립 ZIP이 아니다. 누락된 part를 빈 파일로 대체하거나 각 part에 unzip을 호출하지 않는다. 파일명의 사전순이나 다운로드 순서를 추정해 연결하지 말고 manifest의 index 순서를 따른다.

Transport manifest의 원래 ZIP 이름·총 bytes·SHA가 최종 Git receipt와 일치하고, manifest 자체의 기록된 SHA도 맞는지 먼저 확인한다. 원래 ZIP 이름은 transport manifest의 `archive` 문자열 또는 `name`으로 주어질 수 있다. 최종 scope의 `archive.drive_id`/`dropbox_id`가 multipart index/manifest 객체를 가리키는 경우 이를 전체 ZIP 객체 ID로 오인하지 않는다. 실제 part ID는 `archive.parts`에 있다. 모든 part를 내려받아 각 bytes/SHA를 확인한 뒤 header·separator·padding 없이 raw bytes를 이어붙인다. 마지막 part가64 MiB보다 작은 것은 정상이다. 복원된 전체 ZIP의 bytes/SHA/CRC 및 이후 모든 member manifest를 확인하기 전에는 overlay하지 않는다. Part별 업로드 ACK를 전체 ZIP 복구 성공으로 해석하지 않는다.

아래 명령은 다운로드 폴더 안에 놓인, 최종 Git receipt의 transport manifest를 사용한다. `REI_TRANSPORT_MANIFEST`는 그 실제 경로로 지정한다. `REI_FULL_ARCHIVE_DESCRIPTOR`에는 해당 full archive의 **최종 Git `archive` 객체**를 그대로 JSON으로 저장한 파일 경로를 지정한다. 보통 `GIT_EVIDENCE_SCOPE.json#/archive`이며, 작은 delta가 앞선 full archive를 참조하면 그 명시된 base의 descriptor를 선택한다. Descriptor 자체의 출처 Git commit을 복구 기록에 남긴다. Unsplit archive에는 이 단계가 필요 없고 기존 절차를 그대로 사용한다.

```bash
export REI_ARCHIVE_DIR=/absolute/path/to/downloaded_archives
export REI_TRANSPORT_MANIFEST=/absolute/path/to/verified_transport_manifest.json
export REI_FULL_ARCHIVE_DESCRIPTOR=/absolute/path/to/git_full_archive_descriptor.json
python - <<'PY'
from pathlib import Path
import hashlib,json,os,zipfile
downloads=Path(os.environ['REI_ARCHIVE_DIR']).resolve()
descriptor=json.loads(Path(os.environ['REI_FULL_ARCHIVE_DESCRIPTOR']).read_text())
manifest_path=Path(os.environ['REI_TRANSPORT_MANIFEST'])
expected=descriptor['transport_manifest']; raw=manifest_path.read_bytes()
assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'], 'TRANSPORT_MANIFEST_IDENTITY'
m=json.loads(raw)
assert m['format']=='RAW_ZIP_BYTE_PARTS_CONCATENATE_IN_INDEX_ORDER'
archive_name=m.get('archive') or m['name']
assert archive_name==(descriptor.get('name') or descriptor.get('archive')), 'ORIGINAL_ZIP_NAME'
assert (m['bytes'],m['sha256'])==(descriptor['bytes'],descriptor['sha256']), 'ORIGINAL_ZIP_IDENTITY'
parts=sorted(m['parts'],key=lambda x:x['index'])
declared=sorted(descriptor['parts'],key=lambda x:x['index'])
assert [{k:x[k] for k in ('index','name','bytes','sha256')} for x in parts]==[{k:x[k] for k in ('index','name','bytes','sha256')} for x in declared], 'PART_LIST_IDENTITY'
assert [x['index'] for x in parts]==list(range(1,len(parts)+1)), 'PART_INDEX_GAP_OR_DUPLICATE'
assert sum(x['bytes'] for x in parts)==m['bytes'], 'TOTAL_PART_BYTES'
assert all(0<x['bytes']<=67108864 for x in parts), 'PART_SIZE_DOMAIN'
assert Path(archive_name).name==archive_name
target=downloads/archive_name
assert not target.exists(), 'DO_NOT_OVERWRITE_EXISTING_ARCHIVE'
temp=target.with_name(target.name+'.assembling')
whole=hashlib.sha256()
with temp.open('xb') as out:
    for row in parts:
        name=row['name']; assert Path(name).name==name
        payload=(downloads/name).read_bytes()
        assert len(payload)==row['bytes'], ('PART_SIZE',name)
        assert hashlib.sha256(payload).hexdigest()==row['sha256'], ('PART_SHA',name)
        out.write(payload); whole.update(payload)
    out.flush(); os.fsync(out.fileno())
assert temp.stat().st_size==m['bytes'] and whole.hexdigest()==m['sha256'], 'WHOLE_ZIP_IDENTITY'
with zipfile.ZipFile(temp) as z:
    assert z.testzip() is None, 'WHOLE_ZIP_CRC'
temp.rename(target)
print(target,whole.hexdigest())
PY
```

Assembly 실패 시 `.assembling`과 실패 기록을 보존하고 누락/잘못된 part만 바로잡는다. 과학 실행으로 대체 payload를 만들지 않는다. 이미 완성 ZIP이 존재하면 그 파일을 최종 receipt의 bytes/SHA/CRC로 확인해 재사용하며, 분할 part를 다시 이어붙이는 의식을 반복하지 않는다.

최종 작은 synchronization archive가 별도 base full archive를 요구한다고 선언한 경우에는 **C11R4 → 명시된 base full archive(예: C12R14) → 작은 metadata overlay** 순으로 적용한다. 작은 overlay만으로 bulk checkpoint가 복구된다고 가정하지 않는다. 순서와 각 원래 ZIP SHA는 최종 scope/receipt의 `restore_order` 및 base 참조 선언을 따른다. 아래 복구 계획의 `stage_names`도 이 경우에는 단일 최신 파일이 아니라 선언된 순서의 원래 ZIP 이름 목록으로 채운다. C11R4는 코드에서 이미 앞에 추가하므로 `stage_names`에 중복 넣지 않는다. Full archive가 multipart이면 위 단계로 먼저 전체 ZIP을 복원한 뒤 동일한 overlay 절차에 넣는다.

## 새 작업 디렉터리와 복구 계획 고정

기존 실행 디렉터리에 겹쳐 복구하지 않는다. 다음은 **local Codex가 실제 복구할 때 실행할 명령**이다. 첫 checkout은 최신 receipt를 읽는 용도이며, 실제 복구 Git baseline은 stage archive의 `MANIFEST.json#/baseline`에서 가져온다. 해당 baseline을 추정해서 대체하지 않는다.

```bash
git clone --branch research/accel02-native-broad-20261011 https://github.com/cosmosapjw-quantum/rei_bianchi.git rei_bianchi_restore
cd rei_bianchi_restore
export REI_ARCHIVE_DIR=/absolute/path/to/downloaded_archives
export REI_RESTORE_PLAN="$(pwd)/../rei_restore_plan.json"
```

최신 receipt를 checkout 밖에 고정하고, 실제 다운로드 파일의 SHA·크기를 검사한다. 아래 검증은 수치 검산을 실행하지 않는다.

```bash
python - <<'PY'
from pathlib import Path
import hashlib, json, os, subprocess, zipfile
repo=Path.cwd(); c12=repo/'research/accel02_20261011/q1b/c12'
scope=json.loads((c12/'GIT_EVIDENCE_SCOPE.json').read_text())
receipts=json.loads((c12/'PUBLICATION_RECEIPTS.json').read_text())
base_receipts=json.loads((c12.parent/'c11/PUBLICATION_RECEIPTS.json').read_text())
base=next(x for x in base_receipts['stages'] if x['stage']=='C11R4_FINAL')
name=scope['archive'].get('name') or scope['archive'].get('archive')
stage_names=[name]  # base-full + delta가 선언되면 정확한 restore_order의 ZIP 이름 목록으로 교체
stages=[next(x for x in reversed(receipts['stages']) if (x.get('name') or x.get('archive'))==n) for n in stage_names]
downloads=Path(os.environ['REI_ARCHIVE_DIR']).resolve()
selected=[]
for item in (base,*stages):
    filename=item.get('archive') or item['name']; p=downloads/filename
    assert p.stat().st_size==item['bytes'], ('SIZE_MISMATCH',filename)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'], ('SHA_MISMATCH',filename)
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None, ('ZIP_CRC_ERROR',filename)
        manifest=json.loads(z.read('MANIFEST.json'))
    selected.append({'path':str(p),'receipt':item,'manifest':manifest})
assert selected[-1]['manifest']['stage']==scope['stage'], 'STAGE_MISMATCH'
plan={'source_git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'git_baseline':selected[1]['manifest']['baseline'],  # 첫 full archive의 baseline
      'selected':selected,'git_scope':scope,'receipt_status':'LOCAL_ARCHIVE_SHA_SIZE_CRC_CHECKED',
      'remote_restore':'NOT_CLAIMED_BY_THIS_PRECHECK'}
Path(os.environ['REI_RESTORE_PLAN']).write_text(json.dumps(plan,indent=2)+'\n')
print(plan['git_baseline'],scope['stage'])
PY
REI_RESTORE_BASELINE=$(python -c 'import json,os; print(json.load(open(os.environ["REI_RESTORE_PLAN"]))["git_baseline"])')
git switch --detach "$REI_RESTORE_BASELINE"
```

## Overlay와 모든 member 검증

C11 manifest의 파일 경로는 `repos/rei_bianchi/...`, C12 manifest는 repo 상대 경로이고 ZIP member에는 `repos/rei_bianchi/` 접두사가 붙는다. 아래는 두 형식을 구분하며, REI 내용만 복구한다. C11 ZIP에 동봉된 BASS consumer snapshot은 검증하되 REI 경로에 넣지 않는다. 기존 파일은 선택한 검증된 archive 내용으로 덮어쓰므로 위의 전용 새 checkout에서만 수행한다.

```bash
python - <<'PY'
from pathlib import Path, PurePosixPath
import hashlib, json, os, zipfile
repo=Path.cwd().resolve(); plan=json.loads(Path(os.environ['REI_RESTORE_PLAN']).read_text())
records=[]
for item in plan['selected']:
    with zipfile.ZipFile(item['path']) as z:
        for row in item['manifest']['files']:
            raw=row['path']
            member=raw if raw.startswith('repos/') else 'repos/rei_bianchi/'+raw
            payload=z.read(member)
            assert len(payload)==row['bytes'], ('MEMBER_SIZE',member)
            assert hashlib.sha256(payload).hexdigest()==row['sha256'], ('MEMBER_SHA',member)
            if not member.startswith('repos/rei_bianchi/'):
                continue
            rel=PurePosixPath(member.removeprefix('repos/rei_bianchi/'))
            assert not rel.is_absolute() and '..' not in rel.parts, ('UNSAFE_MEMBER',member)
            target=repo/str(rel); target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(payload)
            mode=row['mode']; assert mode in ('100644','100755'), ('UNSUPPORTED_MODE',mode)
            target.chmod(0o755 if mode=='100755' else 0o644)
            assert hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256']
            records.append({'stage':item['manifest']['stage'],'path':str(rel),'sha256':row['sha256']})
receipt=repo.parent/'rei_local_overlay_receipt.json'
receipt.write_text(json.dumps({'status':'LOCAL_ARCHIVE_OVERLAY_MEMBER_SHA_VERIFIED',
    'repo':str(repo),'baseline':plan['git_baseline'],'files':records,
    'numerical_calls':0,'remote_restore_scope':'Only the actually downloaded objects and this checked local overlay'},indent=2)+'\n')
print(receipt)
PY
```

ZIP은 upload 이전 snapshot이고 이후 ACK·receipt commit은 나중에 만들어진다. 따라서 archive 내부의 pending 문구가 외부 최신 receipt를 소급 무효화하지는 않는다. 반대로 최신 receipt가 누락된 checkpoint payload를 대신하지도 않는다. Manifest에 포함된 파일이 하나라도 누락되거나 SHA가 다르면 해당 복구를 중단하고 원인을 기록한다. 완료 검산을 다시 실행하여 누락된 증거를 임의 재생성하지 않는다.

Overlay 검증 후에는 **최종 Git의 관리 문서만** 명시적으로 다시 적용한다. 이는 pre-upload archive와 post-ACK Git이 동일한 bytes라는 주장이 아니다. 최신 administrative STATE/HANDOFF/DAG/scope/receipt를 과거 archive 값으로 낮추지 않기 위한 별도 provenance 단계다. 아래는 후보 dependency에 포함된 파일이면 덮어쓰기를 거부한다. Dependency 수를 과거 값으로 고정하지 않으며, 선택한 authoritative transition bundle의 전체 경로·해시 목록을 읽는다. 새 opacity binding 때문에 추가된 항목도 전부 확인한다.

```bash
python - <<'PY'
from pathlib import Path
import hashlib,json,os,subprocess
repo=Path.cwd(); c12='research/accel02_20261011/q1b/c12/'
plan=json.loads(Path(os.environ['REI_RESTORE_PLAN']).read_text()); commit=plan['source_git_head']
def git_bytes(rel):
    return subprocess.check_output(['git','show',f'{commit}:{rel}'])
h=json.loads(git_bytes(c12+'HANDOFF.json'))
b=json.loads((repo/h['transition_bundle']).read_text())
pinned={key.removeprefix('dependency:') for key in b['dependency_closure']}
changes=[]
for name in ('STATE.json','HANDOFF.json','NEXT_DAG.json','GIT_EVIDENCE_SCOPE.json','PUBLICATION_RECEIPTS.json'):
    rel=c12+name; assert rel not in pinned, ('REFUSE_PINNED_OVERWRITE',rel)
    target=repo/rel; before=hashlib.sha256(target.read_bytes()).hexdigest()
    payload=git_bytes(rel); target.write_bytes(payload)
    changes.append({'path':rel,'archive_sha256':before,'post_ACK_Git_sha256':hashlib.sha256(payload).hexdigest()})
(repo.parent/'rei_post_ack_metadata_receipt.json').write_text(json.dumps({
    'source_git_commit':commit,'administrative_only':True,'changes':changes,
    'archive_member_verification_precedes_this_step':True,'pinned_dependency_bytes_changed':False},indent=2)+'\n')
print('POST_ACK_ADMIN_METADATA_REAPPLIED; archive and Git identities remain distinct')
PY
```

최종 Git을 이미 checkout한 경로에 overlay하는 다른 복구 방식을 사용하더라도 같은 원칙을 적용한다. 먼저 archive member를 검증하고, 최신 Git 관리 문서를 명시적으로 복구하며, pinned code/checkpoint·과거 ASRUN·failed journal은 변형하지 않는다. 최신 Git이 가리키는 checkpoint payload가 선택 archive에 없다면 선택한 stage가 맞지 않는 것이므로 코드 재실행으로 보충하지 않는다.

## 활성 checkpoint와 dependency의 파일 동일성 확인

다음은 `HANDOFF.json`에 기록된 checkpoint와 배열/metadata/identity의 bytes를 검사한다. Generation을 숫자로 하드코딩하지 않으며, 가장 큰 디렉터리 번호를 무조건 채택하지 않는다. `TRANSITION_RESULT.json`의 generation/cursor는 child를 처음 만든 시점의 seed다. 실제 후속 진행은 저장 journal과 `STATE/HANDOFF`를 따른다.

```bash
python - <<'PY'
from pathlib import Path
import hashlib,json
repo=Path.cwd(); c12=repo/'research/accel02_20261011/q1b/c12'
h=json.loads((c12/'HANDOFF.json').read_text()); state=json.loads((c12/'STATE.json').read_text())
b=json.loads((repo/h['transition_bundle']).read_text())
for key,digest in b['dependency_closure'].items():
    rel=key.removeprefix('dependency:'); p=repo/rel
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest, ('DEPENDENCY_MISMATCH',rel)
ref=h['current_checkpoint']; active=c12/h['active_run']
gen=active/'CHECKPOINTS'/f"gen-{ref['generation']:08d}"
m=gen/'manifest.json'
assert hashlib.sha256(m.read_bytes()).hexdigest()==ref['manifest_sha256']
manifest=json.loads(m.read_text())
for name,row in manifest['files'].items():
    p=gen/name
    assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
assert json.loads((gen/'identity.json').read_text())==b['identity']
assert (active/'RUN/INITIAL_OUTPUT_DONE.json').exists(), 'MISSING_SAVED_INITIAL_OUTPUT'
print('FILE_IDENTITIES_VERIFIED; no native or old numerical tests executed')
print('Recorded status:',state['status'],'next:',h['next_anchor'])
PY
```

두 binary 경로는 `research/accel02_20261011/n1/native/target/release/rei_n1_native`와 `research/accel02_20261011/q1b/native/target/release/rei_q1b_cell_native_v1`이다. Archive의 `100755` mode를 보존한다. 이전 launch에 기록된 Python/NumPy/SciPy 및 Linux native 실행환경을 참조한다. Binary가 현재 호스트에서 실행되지 않는 경우 실행환경 오류로 기록하며, 다시 빌드한 다른 bytes를 동일 identity로 위장하지 않는다. 이미 완료한 MP 정밀도 검산을 재개 의식처럼 반복할 필요는 없다.

## Administrative absolute path만 별도 복사본에서 relocation

Archive의 `TRANSITION_RESULT.json`에는 원래 호스트의 absolute path가 남는다. 원본 bundle과 checkpoint-bound 파일은 그대로 보존한다. 새 `TRANSITION_RESULT_LOCAL.json`에서 다음 네 administrative 항목만 새 checkout의 동일 상대 경로로 치환한다: `checkpoint_directory`, `generation_path`, `transition_path`, `schedule_path`. `source_module_path`와 새 `absorption_module_path`는 이미 repo 상대 경로이므로 바꾸지 않는다. Physics/source/control/identity/dependency closure, seed generation, cursor, budget 및 과거 ASRUN 문자열은 수정하지 않는다. Source SHA `a29207b6ebee37024c35b87723dd64516e528a4f0a160b17ce9965b8dd7e0779`는 이번 opacity 변경에서도 유지된다.

```bash
python - <<'PY'
from pathlib import Path
import copy, hashlib, json
repo=Path.cwd().resolve(); c12=repo/'research/accel02_20261011/q1b/c12'
h=json.loads((c12/'HANDOFF.json').read_text()); original=repo/h['transition_bundle']
old=json.loads(original.read_text()); new=copy.deepcopy(old); changes={}
for key in ('checkpoint_directory','generation_path','transition_path','schedule_path'):
    value=old[key]; marker='/research/'
    assert marker in value, ('UNKNOWN_PATH_LAYOUT',key,value)
    rel='research/'+value.split(marker,1)[1]
    target=repo/rel; assert target.exists(), ('MISSING_RELOCATION_TARGET',key,str(target))
    new[key]=str(target); changes[key]={'old':value,'new':str(target)}
for key in old:
    if key not in changes: assert old[key]==new[key]
local=original.with_name('TRANSITION_RESULT_LOCAL.json')
assert not local.exists(), 'KEEP_EXISTING_LOCAL_RELOCATION_RECEIPT'
local.write_text(json.dumps(new,indent=2)+'\n')
receipt=original.with_name('LOCAL_RELOCATION_RECEIPT.json')
receipt.write_text(json.dumps({'schema':'rei.c12.local_administrative_relocation.v1',
    'original_bundle_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
    'local_bundle_sha256':hashlib.sha256(local.read_bytes()).hexdigest(),
    'changes':changes,'identity_unchanged':True,'native_calls':0},indent=2)+'\n')
print(local)
PY
```

Relocation은 이미 저장된 child를 다른 경로에서 읽도록 하는 관리 변경이다. Child를 다시 생성하는 물리/numerical identity 전환이 아니다. 이미 child가 있으면 `prepare_opacity_transition_v4.py`, `prepare_opacity_transition.py`, `prepare_failure_transition.py`, 원래 `prepare_production_transition.py`를 재호출하지 않는다. 기존 journal·checkpoint·ASRUN을 삭제하거나 정리하지 않는다. `C2_FULL001`의 source attempt42, `C2_FULL002`의 opacity attempt66, `C2_FULL003`의 opacity attempt67 실패와 세 unresolved journal을 모두 실패 증거로 보존하며 그 실패 lane을 다시 실행하지 않는다. 새 child가 아직 없거나 candidate review가 pending이면, 존재하지 않는 복구 대상을 임의 생성하거나 후보 GO를 추정하지 않고 최신 HANDOFF의 해당 작업부터 수행한다.

## Local Codex가 실행할 다음 단위

먼저 최신 `HANDOFF.json`의 status·command_status·stop·allocation을 읽는다. `ALLOCATION_EXHAUSTED`, unresolved inflight, review pending 또는 새 concrete failure이면 동일 명령 자동 재시도로 넘어가지 않는다. 실패 입력과 마지막 accepted checkpoint를 보존하고, 허용된 다음 변경이나 새 allocation이 명시되었는지 확인한다. 남은 allocation이 있고 최신 decision이 continuation을 허용하면 기존 child에서 다음 chunk를 실행한다. 사용 중인 controller의 cumulative attempts 및 failed-attempt debit을 0으로 초기화하지 않는다.

C2_FULL004 전환의 예정된 예산 정체성은 completed-attempt cap102 + 외부에서 별도 계상한 실패3 = 원래 물리 attempt cap105다. Accepted-macro cap은103이며, 실제 남은 횟수와 채택된 controls는 최신 bundle/cursor에서 읽는다. Transition bundle에 남는 seed cursor와 처음 계산된 remaining 값은 후속 journal의 현재 cursor를 대체하지 않는다. 세 과거 실패를 성공/수용 attempt로 재분류하거나 debit을 없애지 않는다.

C2_FULL004 child가 이미 생성되고 **latest review/HANDOFF에서 실제 continuation을 허용한 뒤** 사용할 명령의 형태는 다음과 같다. 이 문서 자체는 pending 후보의 실행 승인이 아니다. `HANDOFF.json`이 이후 version/run을 지목하면 그 실제 명령을 사용하되 relocation bundle 인수만 대응하는 로컬 복사본으로 바꾼다.

```bash
python -u research/accel02_20261011/q1b/c12/repair/production_v4/run_full_history_chunk_v4.py \
  --transition-bundle research/accel02_20261011/q1b/c12/evidence/C2_FULL004/TRANSITION_RESULT_LOCAL.json \
  --run-directory research/accel02_20261011/q1b/c12/evidence/C2_FULL004/RUN \
  --new-attempt-cap 3 --wall-s 45
```

이 명령은 초기조건부터 재시작하지 않는다. 저장 journal이 지목하는 현재 accepted prefix와 rejected cursor에서 같은 전구간 목표로 이어간다. 기존 `INITIAL_OUTPUT_DONE.json`과 epoch0 output을 사용하며 h=0 진단을 다시 생성하지 않는다. 45초는 새 trial 시작 전에 확인하는 cooperative 한도이며 진행 중인 native trial의 강제시간 상한은 아니다.

각 chunk 뒤에 exact result/exit/로그와 새 checkpoint·journal·output을 보존하고, 전체 SHA manifest 및 Git/Drive/Dropbox receipt를 남긴다. 전체 payload를 archive에만 저장했다면 Git receipt에 그 범위를 명시한다. 복구 성공, 실행 성공, 전구간 물리 허용을 구별한다. 최종 시간9-field2e-6·spectral24-field1e-3, 기존 ledger1e-9·geometry1e-11 및65/129 별도 own-fine normalization은 변경하지 않는다. FLRW 실행의 진전만으로 nonzero-shear/BASS 또는 원래 atomic/CR/RCT lane을 승격하지 않는다.

Local Codex 시작 프롬프트:

> C12의 RESTORE_AND_LOCAL_CODEX_KO.md, 최신 STATE.json과 HANDOFF.json을 읽어 Git baseline과 정상 전체 archive로 실행을 복구해줘. 실제 다운로드 archive SHA/크기·member manifest·활성 checkpoint와 authoritative bundle의 전체 dependency 해시 목록을 확인하고, 네 administrative absolute path만 별도 relocation bundle에 기록해줘. 최신 HANDOFF가 가리키는 기존 child·journal·초기 output을 재사용하고, C2_FULL001 source 실패42·C2_FULL002 opacity 실패66·C2_FULL003 opacity 실패67 및 ASRUN/journal을 모두 보존해줘. 최신 선택 후보의 source/absorption provenance를 bundle에서 확인하고, composite log-q 후보의 기존1e-7·moment-fit1e-12 기준과 실제 scoped review 결정을 확인해줘. Pending 후보를 GO로 간주하지 말아줘. 완료 검산·PILOT02·초기 h=0·기존 child prepare를 반복하지 말고, cumulative counters와 외부 실패3의 debit을 유지해줘. 최신 허용 결정과 남은 allocation 내에서 전구간 목표로 다음 durable chunk를 실행하고, 매 단계 exact evidence와 Git·Drive/Dropbox 백업을 남겨줘. 실제 복구를 하지 않았다면 RESTORE_VERIFIED라고 하지 말아줘.
