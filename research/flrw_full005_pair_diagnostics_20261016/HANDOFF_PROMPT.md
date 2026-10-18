# FULL005 continuous pair diagnostic continuation

아래 전체 내용을 owner-side Codex에 전달한다. 파일을 사용자가 수동으로 내려받거나 다시 첨부할 필요가 없다.

---

`rei_bianchi`의 이미 검토된 FULL005 저장 이력 PL 진단을 이어서 수행하라. 과학적 범위는 저장된 binary64 `ln(a)`에서 두 연속 piecewise-linear 재구성의 supremum, L1, I2, L2, RMS이다. 새 solver 실행, 완료된 9개 그림의 render replay, ledger/checkpoint 재검사, SOURCE007/SOURCE008 수정은 이 작업에 없다. 전체 실제 raw 이력에 대한 새 norm은 아직 `NOT_RUN`이다. 독립 C9 판정은 `PASS_SCOPED`이고 solver 정확도나 수렴을 승인하지 않았다.

검토된 코드 commit은 **`e881b38951bc896c29d5ea57bb8fb1f2803873e1`**이다. 저장소는 `cosmosapjw-quantum/rei_bianchi`, 통합 branch는 `research/flrw-production-integration-20261015`이다. 기존 dirty checkout을 reset/overwrite하지 말고 이 commit의 필요한 파일을 새 runtime 디렉터리로 자동 취득하라. 선택한 commit의 `AGENTS.md`를 먼저 읽고 적용하라. 이 prompt가 포함된 C10 패키지의 저장 확인은 `DELIVERY_LOG.json`에 있으며, runtime 코드는 위 C9 commit에 고정한다.

## 1. Runtime 자동 취득

기존 인증된 checkout이 있으면 아래 명령의 `REPO`를 실제 발견한 checkout 경로로 설정해서 실행하라. `git fetch`는 기존 branch/worktree 내용을 바꾸지 않는다.

```bash
export REPO="$(git rev-parse --show-toplevel)"
export REI_PAIR_WORK="$(mktemp -d "${TMPDIR:-/tmp}/rei-full005-pair.XXXXXXXX")"
export REI_PAIR_PIN=e881b38951bc896c29d5ea57bb8fb1f2803873e1
git -C "$REPO" fetch origin research/flrw-production-integration-20261015
git -C "$REPO" cat-file -e "$REI_PAIR_PIN^{commit}"
git -C "$REPO" show "$REI_PAIR_PIN:AGENTS.md" > "$REI_PAIR_WORK/AGENTS.md"
cat "$REI_PAIR_WORK/AGENTS.md"
python3 - <<'PY'
import os, pathlib, subprocess
root=pathlib.Path(os.environ['REI_PAIR_WORK'])
unit='research/flrw_full005_pair_diagnostics_20261016/'
base='research/flrw_full005_postprocess_20261015/'
paths=[unit+'analyze_saved_pair.py',unit+'CONTRACT.json',unit+'INDEPENDENT_REVIEW.json',
       base+'vendor/pair_diagnostics.py',base+'vendor/compare_histories.py',
       base+'vendor/source_pair_guard.py',base+'vendor/reconstruction_support.py',
       base+'completed_pair_20261016_001/results/POSTPROCESS_RECEIPT.json',
       base+'completed_pair_20261016_001/RETURN_CONTRACT.json']
for name in paths:
    target=root/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(subprocess.check_output(
        ['git','-C',os.environ['REPO'],'show',os.environ['REI_PAIR_PIN']+':'+name]))
(root/'FETCHED_CODE_COMMIT.txt').write_text(os.environ['REI_PAIR_PIN']+'\n')
print(root)
PY
```

기존 checkout이 없으면 같은 공개된 commit archive를 자동 취득한다. 인증은 이미 사용 가능한 GitHub 앱/`gh` 세션을 재사용한다. 예를 들어 `gh api repos/cosmosapjw-quantum/rei_bianchi/zipball/e881b38951bc896c29d5ea57bb8fb1f2803873e1 > "$REI_PAIR_WORK/reviewed.zip"`를 실행하고, Python `zipfile`로 archive의 한 최상위 디렉터리를 제거하여 새 runtime에 풀면 된다. 해당 commit의 archive URL은 `https://github.com/cosmosapjw-quantum/rei_bianchi/archive/e881b38951bc896c29d5ea57bb8fb1f2803873e1.zip`이다. 실제 제공된 C10 cloud archive URL이 있으면 그것을 자동 내려받아도 된다. 이 경우에도 C9 코드 identity와 `AGENTS.md`를 확인하라. 다운로드/인증 실패는 실제 원인과 재개 위치를 보고하고 사용자의 수동 파일 전달 단계로 바꾸지 말라.

## 2. 기존 raw와 누적 실행 기록 확인

bundled `POSTPROCESS_RECEIPT.json`을 읽어 성공 status, 두 case, source relation, 원래 SHA256와 경로를 확인하라. 원래 owner 경로는 다음과 같다.

```text
/home/cosmosapjw/REI_POSTPROCESS_20261015_001/AUTO_FULL005_001/inputs/runs/<case_id>/
/home/cosmosapjw/REI_POSTPROCESS_20261015_001/AUTO_FULL005_001/inputs/launches/<case_id>.binding.json
```

필요한 것은 각 case의 `history.csv`, `abundances.csv`, `config.cfg`, `source_identity.txt`, `RETURN.txt`와 작은 controller binding이다. 원래 경로가 있으면 그대로 사용한다. NCP 또는 다른 owner cache에 이미 이동된 raw가 있으면 기존 반환 기록/작업 디렉터리에서 해당 두 root를 자동 발견하고 `REI_PAIR_RUNS_ROOT`와 `REI_PAIR_BINDINGS_ROOT`로 설정하라. 이 변수는 선택적이며, analyzer의 `--runs-root ROOT`와 `--bindings-root ROOT`로 연결된다. expected SHA256는 수정하지 않는다. compressed display CSV는 전체 raw를 대신하지 않는다. raw를 새로 수집하거나 solver를 다시 실행하지 않는다.

원래 `RETURN_CONTRACT.json`의 누적 postprocess 사용량은 **103.79374452296179 s**, 원래 300 s 한도에서 남은 상한은 **196.206255477 s**이다. 원래 절대 deadline은 **1792122617.77407**, 즉 **2026-10-16T03:50:17.774070Z**이고 `deadline_reset=false`이다. 이후 실행/실패/중단 기록을 확인하여 추가 debit을 합산하고, 중복 receipt를 두 번 더하지 말라. 기존 continuation budget 파일이 있으면 그 경로를 `REI_PAIR_BUDGET`에 설정한다. 추가 debit을 실제 기록으로 확인한 값으로 `REI_PAIR_LATER_DEBIT_SECONDS`에 설정하라. 0은 이후 시도가 없음을 기록으로 확인했을 때 사용한다. 기록이 불명확한 중단 시도는 기존 할당 상한을 보수적으로 debit한다. 새 output/runtime 디렉터리가 새 예산을 만들지 않는다.

## 3. 기존 deadline 안에서 단 한 번 실행

정확한 analyzer CLI는 다음 형태다. 아래 wrapper가 이 명령을 자동 구성하고 timeout/로그/누적 debit을 보존한다.

```text
python3 -B research/flrw_full005_pair_diagnostics_20261016/analyze_saved_pair.py --validated-receipt research/flrw_full005_postprocess_20261015/completed_pair_20261016_001/results/POSTPROCESS_RECEIPT.json --output FRESH_DIRECTORY [--runs-root EXISTING_ROOT] [--bindings-root EXISTING_ROOT]
```

`REI_PAIR_WORK`, 확인된 추가 debit과 선택적 relocation 변수를 설정한 뒤 다음 Python block을 실행하라. cap은 누적 예산과 원래 deadline 각각에서 5초 stop reserve를 뺀 상한들의 최솟값이다. cap이 양수가 아니거나 GNU `timeout`이 없으면 typed HOLD를 쓰고 analyzer/raw 읽기를 시작하지 않는다. deadline을 새로 만들거나 예산을 초기화하지 않는다.

```python
import json, os, pathlib, resource, shutil, signal, subprocess, sys, tempfile, time
root=pathlib.Path(os.environ['REI_PAIR_WORK']).resolve()
later=float(os.environ['REI_PAIR_LATER_DEBIT_SECONDS'])
if not (0 <= later < float('inf')):
    raise ValueError('invalid observed later debit')
budget=pathlib.Path(os.environ.get('REI_PAIR_BUDGET',str(
    pathlib.Path.home()/'REI_POSTPROCESS_20261015_001/FULL005_PAIR_CONTINUATION_BUDGET.json')))
deadline=1792122617.77407
baseline=103.79374452296179
state=json.loads(budget.read_text()) if budget.exists() else {}
recorded_used=float(state.get('cumulative_wall_seconds',baseline))
if state.get('active'):
    recorded_used+=float(state['active_allowance_seconds'])  # Interrupted unknown timing.
used=max(baseline+later,recorded_used)  # Later inventory may already include it.
stop_reserve=5.0
cap=min(196.206255477-later-stop_reserve,300-used-stop_reserve,
        deadline-time.time()-stop_reserve)
timeout_tool=None
if cap > 0:
    candidate=shutil.which('timeout')
    if candidate:
        try:
            version=subprocess.check_output([candidate,'--version'],text=True,
                stderr=subprocess.STDOUT,timeout=1)
            if 'GNU coreutils' in version:timeout_tool=candidate
        except (OSError,subprocess.SubprocessError):pass
    cap=min(cap,deadline-time.time()-stop_reserve)
status=dict(code_commit='e881b38951bc896c29d5ea57bb8fb1f2803873e1',
    unchanged_deadline_epoch=deadline,deadline_reset=False,
    cumulative_wall_seconds=used,solver_runs=0,renderer_runs=0,metrics=None,
    active=False,active_allowance_seconds=0,stop_reserve_seconds=stop_reserve)
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temporary=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(descriptor,'w') as stream:
            stream.write(json.dumps(value,indent=2,allow_nan=False)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary,path)
        try:
            directory=os.open(path.parent,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
            try:os.fsync(directory)
            finally:os.close(directory)
        except OSError:pass  # Directory fsync is used when supported by this host.
    finally:
        pathlib.Path(temporary).unlink(missing_ok=True)
if cap <= 0 or timeout_tool is None:
    status.update(status=('HOLD_RETAINED_DEADLINE_OR_BUDGET_EXHAUSTED' if cap <= 0
                          else 'HOLD_GNU_TIMEOUT_UNAVAILABLE'),executed=False)
    save(budget,status)
    save(root/'CONTINUATION_STATUS.json',status)
    print(json.dumps(status))
else:
    unit=root/'research/flrw_full005_pair_diagnostics_20261016'
    prior=root/'research/flrw_full005_postprocess_20261015/completed_pair_20261016_001/results/POSTPROCESS_RECEIPT.json'
    output=root/'continuous_results'  # Fresh root guarantees a fresh output.
    cmd=[sys.executable,'-B',str(unit/'analyze_saved_pair.py'),
         '--validated-receipt',str(prior),'--output',str(output)]
    for variable,flag in [('REI_PAIR_RUNS_ROOT','--runs-root'),
                          ('REI_PAIR_BINDINGS_ROOT','--bindings-root')]:
        if os.environ.get(variable):cmd.extend([flag,os.environ[variable]])
    cmd=[timeout_tool,'--signal=TERM','--kill-after=1',str(cap)+'s',*cmd]
    status.update(status='RUNNING',executed=True,argv=cmd,wall_cap_seconds=cap,
                  start_epoch=time.time(),active=True,
                  active_allowance_seconds=cap+stop_reserve)
    save(budget,status)
    started=time.perf_counter()
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (root/'analyzer.stdout').open('wb') as stdout, (root/'analyzer.stderr').open('wb') as stderr:
        process=subprocess.Popen(cmd,cwd=root,stdout=stdout,stderr=stderr,start_new_session=True)
        timed_out=False
        try:
            code=process.wait(timeout=cap+2)  # GNU timeout has its own 1s hard-kill grace.
        except subprocess.TimeoutExpired:
            timed_out=True
            try:os.killpg(process.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:code=process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                code=process.wait()
        normalized_shell_exit=128-code if code < 0 else code
        timed_out=timed_out or normalized_shell_exit in (124,137)
    elapsed=time.perf_counter()-started
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    status.update(status='HOLD_TIMEOUT' if timed_out else ('EXECUTION_COMPLETE' if code==0 else 'HOLD_ANALYZER_INPUT_OR_ARITHMETIC'),
        exit_code=code,normalized_shell_exit=normalized_shell_exit,
        timed_out=timed_out,wall_seconds=elapsed,
        cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        peak_rss_kib_linux=after.ru_maxrss,end_epoch=time.time(),
        cumulative_wall_seconds=used+elapsed,active=False,active_allowance_seconds=0)
    save(budget,status)
    save(root/'CONTINUATION_STATUS.json',status)
    print(json.dumps(status,allow_nan=False))
```

실행 성공 시 반환할 파일은 `analyzer.stdout`, `analyzer.stderr`, `CONTINUATION_STATUS.json`, 누적 budget, `continuous_results/PAIR_DIAGNOSTICS_RECEIPT.json`, `full_pair_continuous_diagnostics.json`, `full_pair_continuous_summary.csv`이다. exact command, 실제 경로/해시, code commit, Python, start/end/deadline, exit/timeout, CPU/wall/RSS와 누적 debit을 함께 반환하라. analyzer는 ledger/checkpoint를 열지 않고 renderer/NumPy/Matplotlib를 import하지 않는다.

raw 누락·해시 불일치는 null metrics와 typed HOLD, 비양수 cap은 `HOLD_RETAINED_DEADLINE_OR_BUDGET_EXHAUSTED`로 보고한다. timeout에서 남은 파일은 부분 결과로 보존하고 승인된 metric으로 채택하지 않는다. 실행 성공 뒤 실제 full-overlap 결과만 독립 검토자에게 전달하라. canonical convergence/Bianchi/isotope 과제는 기존 owner DAG에서 이어진다. 새 PL norm만으로 전체 목표 완료나 solver 정확도 승인을 선언하지 말라.
