# Copy into owner-side Codex

아래를 그대로 실행 작업으로 받아 이어가라. `physmath-research-loop`를 적용하고 각 R/C 단계에서 실제 수행·재사용·pending 상태를 구분하여 기록하라. 단계마다 공개 선택된 코드·결과를 durable checkpoint와 Dropbox/Drive backup으로 보존하고 실제 응답을 기록하되, private raw telemetry는 비공개로 유지하라. 기존 사용자 승인은 계속 유효하다. 파일이 없다는 이유로 사용자에게 ZIP 수동 다운로드·대형 첨부·새 승인을 요구하지 말라. AGENTS에 따라 Astra는 계약·수치 판정·독립 검토에, lower-tier는 구현·경량 검증에 라우팅하고, 요청된 역할을 관측된 모델 identity로 쓰지 말라.

1. 검토된 runtime commit은 `e0d547521cd71047670d5c3967ca4289ea0db8b1`이다. 후속 문서는 이 prompt를 포함하는 C10 commit의 자료다. 기존 인증된 checkout/app이 있으면 필요한 파일을 `git show COMMIT:path`로 새 task directory에 취득하고 dirty checkout은 보존한다. checkout이나 파일이 없으면 아래 코드를 실행하여 **작은 단위 checkpoint ZIP만** 자동 내려받아라. 전체 repository archive나 새 checkout은 필요 없다. 상위 전달문에 containing commit이 있으면 도구가 환경변수에 넣고, 없으면 branch HEAD를 한 번 resolve한다. package metadata, 작은 ZIP, AGENTS 모두 같은 immutable SHA에서 읽는다. 사용자가 채우거나 내려받을 항목은 없다.

```python
import hashlib, io, json, os, pathlib, tempfile, urllib.parse, urllib.request, zipfile
repository='cosmosapjw-quantum/rei_bianchi'
branch='research/flrw-production-integration-20261015'
unit='research/flrw_nonlinear_error_budget_20261016'
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'rei-nonlinear-continuation'})
    with urllib.request.urlopen(request,timeout=20) as response:return response.read()
pin=os.environ.get('REI_NONLINEAR_CONTAINING_COMMIT')
if not pin:
    reference=urllib.parse.quote(branch,safe='')
    pin=json.loads(fetch('https://api.github.com/repos/'+repository+'/commits/'+reference))['sha']
base='https://raw.githubusercontent.com/'+repository+'/'+pin+'/'
work=pathlib.Path(tempfile.mkdtemp(prefix='rei-nonlinear-'))
agents=fetch(base+'AGENTS.md')
(work/'AGENTS.md').write_bytes(agents)
print(agents.decode())
package_bytes=fetch(base+unit+'/checkpoints/C10_PACKAGE.json')
package=json.loads(package_bytes)
archive_path=unit+'/checkpoints/REI_FLRW_NONLINEAR_ERROR_BUDGET_20261016_C10_v1.zip'
if package['archive']!=archive_path:raise ValueError('C10 package path mismatch')
payload=fetch(base+archive_path)
if len(payload)!=package['size_bytes'] or hashlib.sha256(payload).hexdigest()!=package['sha256']:
    raise ValueError('C10 package byte identity mismatch')
(work/'C10_PACKAGE.json').write_bytes(package_bytes)
(work/'unit.zip').write_bytes(payload)
with zipfile.ZipFile(io.BytesIO(payload)) as archive:archive.extractall(work/'payload')
(work/'FETCH_RECEIPT.json').write_text(json.dumps({'containing_commit':pin,
    'reviewed_code_commit':'e0d547521cd71047670d5c3967ca4289ea0db8b1',
    'unit_archive':archive_path,'size_bytes':len(payload),'sha256':package['sha256']},indent=2)+'\n')
print('Runtime and documents:',work/'payload'/unit)
```

먼저 출력된 선택 commit의 AGENTS를 읽고 적용한다. 이 ZIP은 해당 단위 코드·증거·인계 묶음이며 production repo나 private raw 전체를 대신하지 않는다. 실제 제공된 pinned cloud checkpoint URL도 사용할 수 있다. 공개 취득에 실패하면 기존 인증된 GitHub 도구/checkout에서 같은 commit의 이 세 파일을 자동 취득하라. 취득 오류를 사용자 수동 다운로드·업로드 요구로 바꾸지 않는다.

2. `research/flrw_nonlinear_error_budget_20261016/`의 `CONTRACT.json`, `INDEPENDENT_REVIEW.json`, `REPORT_KO.md`, `HANDOFF.md`, `SOURCE_BINDING_HANDOFF.md`, `NEXT_DAG.json`, `NEXT_NATIVE_OBSERVER_PLAN.json`을 읽어라. 현재 standalone은 stdlib 하나의 `nonlinear_budget.py`이며 C9 `PASS_SCOPED`다. 실제 accepted-stage residual/J/state packet이 없어 actual attribution은 NOT_RUN이다. null template은 HOLD 설명용이고 이미 끝난 synthetic/PL/oracle 검산을 반복할 필요가 없다.

정확한 CLI는 다음과 같다. 실제 complete packet 또는 다음 단위에서 source binding을 명시적으로 이전한 packet에 사용한다.

```text
python3 research/flrw_nonlinear_error_budget_20261016/nonlinear_budget.py --input STAGE_PACKET.json --output FRESH_DIRECTORY
```

누락·stale·singular·nonfinite·source mismatch는 exit2/typed HOLD/null metrics로 남기며 새 raw를 만들어내지 않는다. 결과·receipt·실측 command/CPU/wall·input/module hash를 보존한다. 실제 R/J packet은 owner 로컬/허용 private backup에 두고, 공개 선택이 이미 선언된 경우를 제외하면 public Git/ZIP에 raw telemetry를 올리지 않는다.

3. 이어서 최신 canonical `research/flrw_covariant_transport_20261015/{LATEST_RESUME.json,NEXT_DAG.json,HANDOFF.json}`와 SOURCE009 현재 소유자/최신 완료 결과를 실제 최신 branch에서 read-only intake하라. 이 handoff의 과거 snapshot이 현재 소유권/실행 완료를 대신하지 않는다. 이미 완료된 SOURCE009 결과를 재사용하고 active owner 파일을 덮어쓰거나 worker를 재시작하지 않는다.

4. 적절한 다음 source를 골라 별도 producer-owned observer 단위의 R1–R10/C1–C10을 이어가라. 기존 이론·cached oracle·완료된 검토는 identity가 유지되면 재사용하고 변경된 seam만 다룬다. `NEXT_NATIVE_OBSERVER_PLAN.json`에 따라 default-off bounded observer를 구현한다. accepted chemical state에서 기존 raw R을 보존하고 같은 prepared context에서 J를 추가 평가한다. 모든 추가 RHS/FD invocation을 실패·fallback·parallel reservation까지 세며 별도 실제 비용을 기존 owner cap/deadline에 합산한다. 기본 경로에는 새 evaluation/I/O가 없어야 한다. full/first-half/second-half와 eventual adaptive accepted/rejected/aborted를 정확히 구분하고, bounded buffer를 안전한 outer boundary에서 한 번 저장한다.

계획의 whole-observer 상한6 packets/48 추가 시도는 이미 실행된 NCP case나 새 배정이 아니다. 실제 source·case·launch·deadline·remaining budget은 plan에서 아직 null이고 최신 owner 기록으로 해소한다. 기존 full005 NCP/PL156.5376037069618/300s, 잔여143.4623962930382s, deadline1792122617.77407은 원래 용도대로 유지한다. 다른 source에 자동 이전하거나 만료된 예산을 초기화하지 않는다. owner의 이미 승인된 적절한 bounded 실행과 live envelope가 있으면 수행하고, 만료/소진이면 named resource HOLD를 남긴다. missing telemetry HOLD는 observer 준비 전체의 중단 사유가 아니다.

5. observer를 넣은 driver의 실제 새 blob을 기록하라. 현재 adapter의 옛 blob으로 새 producer를 표시하지 말라. residual/state order/frozen scales/EOS/prepared context/acceptance 및 FD seam의 unchanged-semantics 비교를 기록하고 다음 단위에서 source-binding을 명시적으로 이전한다. file byte mismatch만으로 physics failure를 선언하지 않는다. default-off 불변성, accepted-initial-residual-pass, 비용 cap/fallback, branch/outcome tag와 buffered output만 targeted 검증하고 독립 검토로 넘긴다. 실제 complete packet을 얻은 뒤 standalone으로 분석한다. 결과는 local linearized chemical-stage correction이며 actual root error가 아니다. 이것만으로 source007 원인 확정·nonlinear error certificate·전체 수렴·Bianchi/D 목표 완료를 선언하지 않는다.
