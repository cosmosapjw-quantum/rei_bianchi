# Local Codex에 그대로 전달할 prompt

BASS_HE의 완료된 E13C6 OFF 네 경로 정밀화를 이 실행 호스트에서 한 번 재현해줘.
이번 작업은 새 N512/P60 1회와 그 저장 결과의 exact analysis 1회다.
아래에서 지정한 단일 ZIP을 사용하면 되고, 사용자에게 추가 파일을 요청하지 마라.

## 단일 전달 archive의 실제 identity

- 파일명: BASS_HE_E13C6_NCP_READY_20261011_sha_e934c49820de.zip
- bytes: 14180748
- SHA-256: e934c49820def56e2735545ade1f6b87e83a504381e0bf35fe60de5ce94cb9b2
- Google Drive: https://drive.google.com/file/d/1PDOGMny3PzRSbEUsh7Pg1sFxnFGatUHi/view?usp=drivesdk
- Drive file ID: 1PDOGMny3PzRSbEUsh7Pg1sFxnFGatUHi
- 대체 Dropbox file ID: id:BSpOijBcT10AAAAAAD4IrA
- Dropbox 경로: /BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C6_NCP_READY_20261011_sha_e934c49820de.zip
- 승인된 Drive parent: 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
- 두 백업 모두 upload ACK와 이름·14,180,748-byte metadata readback을 확인했다.
  클라우드 재다운로드/복구를 이미 검증했다고 간주하지 말고, 이 호스트에서 받은 실제 ZIP bytes/SHA를 위 값과 대조해라.

동일 SHA로 검증된 로컬 ZIP이 이미 있으면 재사용해라. 없다면 연결된 기능으로 위
백업 중 한 곳에서 받아라. Drive의 반환 이름에 추가 접미사가 붙어도 SHA 검증 전
이름만으로 선택하거나 임의의 이전 part002 파일을 쓰지 마라. 여기에는 조각 결합이
없다. 받은 단일 archive의 실제 bytes/SHA를 확인한 뒤 명시된 ZIP basename에
비덮어쓰기 방식으로 배치할 수 있다. 원 다운로드와 실패 영수증은 보존해라.

새 디렉터리에 안전하게 풀고, 121개 member와 PACKAGE_MANIFEST.json의 120개
payload bytes/SHA를 확인해라. 절대경로, 경로이탈, symlink, 중복명, 예상과 다른
package root를 허용하지 마라. 추출된 NCP_HANDOFF_KO.md가 아래 실행 계약과
일치해야 한다. SOURCE_LOCK 15개와 EXECUTION_LOCK 26개 파일이 모두 들어 있다.

소스 기준 head는 d06b8066aafab930add24be971b494b591d87257이다. 이 작업의 실행
정체성은 위 archive와 아래 EXECUTION_LOCK이다. Git publication head는 별도
delivery receipt에 기록되며, 움직이는 branch를 pull해 이 실행 입력을 바꾸지 마라.

## 사전에 완료된 연구 결과와 이번 호스트의 상태

Chat 연구 환경에서 N32/P60, N128/P60, N512/P60, N32/P80을 완료했고, 독립 검토가
N512/P60의 raw same-target 교체를 PROMOTE_SCOPED로 수용했다. 새 구간136/136이
기존 구간에 포함되며 전체 OFF photon 폭 1.021889240910055%, species-sum heat 폭
0.3156955305604365% 감소다. N32 진단과 N128 동일해상도 비교는 이미 끝났으므로
다시 실행하지 마라.

E13C5의 실패 뒤 복구·saved budget은 실제 반환에서 성공했고 원본 반환도 ZIP에
들어 있다. 이전 transport/recovery/full-budget은 반복하지 마라. 이 새 E13C6의
실제 NCP 재현은 전달 시점 NOT_RUN이다. 아래 wrapper를 실행한 새 영수증이
있어야 이 호스트의 결과를 판정할 수 있다.

---

# NCP local Codex handoff — BASS_HE E13C6 OFF 네 경로 정밀화

## 실행할 작업

BASS_HE의 `HE_E13C6_DOMINANT_COMPLEMENT_SAME_TARGET01`에서 이미 완성된
새 N512/P60 정밀화 결과를 이 호스트에서 **한 번만 재현**하고, 실제 새 결과의
전체 numerical projection 및 exact finite-budget analysis를 고정 기준과 비교해줘.
코드나 계산법을 새로 만들지 말고, 아래 SHA로 고정된 전달본을 그대로 실행해줘.

이번 전달본에는 코드, 원본 OFF 입력 CSV, 선택된 네 이전 경로, 직접 계산된
retained budget, 완료된 기준 결과와 실행 wrapper가 모두 들어 있다.
추가 첨부 파일은 필요하지 않다.

E13C5의 part002 파일명 배치·전체 ZIP 복구·저장 결과 budget 합산은 새 반환에서
이미 성공했다. 그 이력과 실패 영수증을 보존하고, **소진된 E13C5 transport나
full-budget 작업을 다시 실행하지 마라.** 이번에 허용된 새 작업은 아래의
OFF 네 경로 N512/P60 한 건과, 그 저장 결과를 읽는 exact analysis 한 건이다.

## 전달본과 고정 기준

이 문서는 전달 archive 내부의 실행 지침이다. 외부 bootstrap 메시지에 있는
archive의 실제 bytes/SHA-256과 백업 locator를 먼저 확인하고 이 문서를 열어라.
Archive 자신의 SHA나 반환 file ID를 자기 내부에 넣지 않는다. 같은 SHA의
검증된 로컬 파일이 있으면 재사용하고, 다운로드 이름만으로 다른 자료나 이전
recovery 조각을 선택하지 마라. 이 전달본 하나에 모든 runtime 입력이 포함되어 있다.

| 항목 | 고정값 |
|---|---|
| archive 안의 package root | `BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1` |
| `EXECUTION_LOCK.json` SHA-256 | `fb75072a17effe87b8ca9d118d04c227c3e1cf6923f9eb38b0f6a80ba102a101` |
| `SOURCE_LOCK.json` SHA-256 | `0b4688c61c6070e0663fa78043a4ff3c37af2250f1e9d98d1e5485f568efaf47` |
| N512/P60 whole numerical semantic SHA | `c9321b00102920e8aedbcc2f9f5cdcd374e67742f346754b928cc873d0e25f23` |
| whole exact-analysis semantic SHA | `d975525df1f0d3a1cc18a254c05cc92d36677e2538438e71a420644ab46a7db2` |
| source predecessor head | `d06b8066aafab930add24be971b494b591d87257` |

외부 bootstrap의 publication head는 출판 이력이다. 실행 입력은 외부에서
고정한 archive와 `EXECUTION_LOCK.json`이다. 이동하는 branch를 pull하거나
과거 PR의 소스를 임의로 최신화해서 실행 입력을 바꾸지 마라.

Archive 검증 후 새 디렉터리에 안전하게 추출해라. 절대 경로, `..` 경로,
symlink, 중복 member 이름이나 예상 밖의 루트가 있으면 중단하고 그 증거를
보존해라. 기존 출력·소스·영수증 위에 추출하지 마라.

## 허용 범위와 자원

- Mode `OFF`, nodes `[101, 102, 410, 413]`, 각 경로 chronological step 1·2의
  segment 0, 총 네 경로·여덟 구간이다.
- N512/P60 새 work unit 한 건, 여덟 local enclosure, coefficient evaluation
  `8192`, cache reuse `0`이다.
- 과학 계산 worker 한 개, worker의 CPU affinity 한 개, thread 한 개,
  address-space 상한 `1073741824` bytes이다. primary의 내부 budget은 300초,
  wrapper의 primary timeout은 310초다.
- Linux의 기존 CPython 3.12.x를 사용한다. 이전 기록의 CPython 3.12.3도
  허용된다. 설치·업그레이드·의존성 교체를 하지 마라. 모두 표준 라이브러리다.
- exact analysis는 새 RESULTS를 읽어 Fraction으로 수행하는 한 건이다.
  과학 kernel·coefficient·ODE를 호출하지 않으며 timeout은 60초다.
- ODE solve, native run, gas advance, full-first2 rerun, old full-budget rerun,
  E13C5 transport replay, 자동 재시도는 모두 `0`이어야 한다.
- N32/P60·N128/P60·N32/P80 진단은 전달본에서 이미 완료되었다. NCP에서
  다시 실행하지 마라. 추가 성능 측정·테스트·정밀도 변경도 실행하지 마라.

Provider는 hostname이나 실행 성공으로 추정하지 마라. 별도로 사용자가 제공한
기존 증거가 없으면 `NOT_ASSERTED`로 기록하고 진행해라. Provider 증거가 없다는
이유로 로그인·추가 승인·별도 증명을 요구하지 마라. 사용자가 명시적으로
제공한 파일이 실제로 있을 때만 wrapper의 `--provider-evidence`에 그 경로를
넘길 수 있다. 그 경우에도 wrapper는 받은 증거를 기록할 뿐 독립적으로
provider를 인증했다고 주장하지 않는다.

## 한 번 실행

실제 추출 위치와 **아직 존재하지 않는** 출력 위치를 아래 두 변수에 넣어라.
출력은 immutable package 바깥의 새 디렉터리여야 한다. 아래 명령을 한 번만
호출하고, 별도로 primary나 analysis를 직접 호출하지 마라.

```bash
BASS_E13C6_ROOT='/absolute/extracted/BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1'
BASS_E13C6_OUT='/absolute/outputs/BASS_HE_E13C6_NCP_EXEC01'
python3 "$BASS_E13C6_ROOT/code/ncp_execute_once.py" \
  --execution-lock-sha256 'fb75072a17effe87b8ca9d118d04c227c3e1cf6923f9eb38b0f6a80ba102a101' \
  --output-root "$BASS_E13C6_OUT"
```

Wrapper는 외부에서 받은 execution-lock SHA, 15개 scientific source/input의
SOURCE_LOCK, wrapper·analysis 코드와 기준 결과의 실제 SHA를 확인한다.
이어서 기준 RESULTS에서 전체 numerical projection을 다시 구성하고 그
identity를 확인한다. 이 단계가 통과한 후에만 새 N512/P60을 실행한다.

새 numerical 결과의 전체 projection이 기준과 일치해야 exact analysis로
진행한다. 분석에서는 34개 observable의 직접 retained sum과 네 새 경로를
결합하고, species-sum A/B/H 정의를 양쪽에 동일하게 적용한다. 전체 analysis
object의 semantic identity와 `GLOBAL_WIDTHS.csv`의 실제 bytes도 비교한다.
소스·입력·lock·기준 결과는 실행 후에 다시 확인한다.

호스트·시각·경로·자원 영수증이 들어 있는 `RESULTS.json`의 파일 SHA는 새로
기록한다. 기준 RESULTS의 파일 SHA가 다르다는 이유만으로 semantic failure라고
판정하지 마라. 반대로 저장된 digest만 같다고 수용하지 마라. Wrapper는 실제
RESULTS와 전체 projection을 연결해서 확인한다.

## 중단과 반환

어느 단계에서든 실패하면 재시도 없이 중단해라. 새 출력 디렉터리를 만들어
같은 job을 다시 호출하거나, 실패한 파일을 고쳐서 덮어쓰지 마라. Wrapper가
만든 실패 영수증·로그·부분 checkpoint·ZIP을 그대로 보존하고 정확한 실패
단계를 보고해라. Launch 예약과 실제 child 실행 수를 구분해서 보고해라.
예약 전 실패는 `NOT_RUN`, 예약 이후 실패는 `FAIL_PRESERVED_NO_RETRY`다.
출력 경로 충돌은 기존 결과를 건드리지 않고 `NOT_RUN_OUTPUT_COLLISION`로
끝나므로 그 stderr를 보존해라.

실행 성공의 scope는 `PASS_SCOPED_NEW_OFF4_N512_AND_EXACT_ANALYSIS_PARITY`다.
이는 고정 코드의 기록된 호스트 재현이다. 독립 수학 증명이나 물리 검증으로
올리지 마라. `physical`, `continuum`, `production`, `receiver`는 모두 `HOLD`다.

반환해야 할 원본은 출력 디렉터리의 다음 두 파일이다.

- `NCP_RETURN.zip`: START, before/after source closure, launch·process receipts,
  새 N512/P60 실제 결과, exact analysis, parity 또는 실패, 실행 영수증,
  member별 bytes/SHA manifest가 포함된 실제 반환본이다.
- `RETURN_ARCHIVE_IDENTITY.json`: 위 ZIP의 실제 bytes/SHA와 member 수를 기록한
  외부 sidecar다. 자기 자신의 archive SHA를 archive 내부에 넣으려 하지 마라.

반환 archive를 이미 승인된 아래 두 위치에 **새 이름으로** 올리고 ACK와
이름·크기 readback을 확인해라. 기존 파일을 대체하거나 삭제하지 마라.

- Google Drive folder ID: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- Dropbox folder: `/BASS_DERIVATION_DOSSIERS_20260912/`

외부 반환 이름은 `BASS_HE_E13C6_DOMINANT_COMPLEMENT_NCP_RETURN_<UTC>_<SHA앞12자>.zip`
처럼 새로 정할 수 있다. 원본 ZIP bytes와 SHA는 그대로 유지하고, 실제 업로드
이름과 반환 file ID를 별도로 기록해라. 연결된 업로드 기능이 이 호스트에
없으면 archive와 sidecar를 보존하고 그 사실을 명시해라. 업로드를 확인하지
못한 상태를 완료로 보고하지 마라.

마지막 보고에는 실행 상태, 실패 시 정확한 phase, 새 N512 invocation `0/1`,
새 analysis invocation `0/1`, 소진된 slot `0/1`, 금지된 호출 전부 `0`,
host·CPython·libmpdec·CPU affinity·provider 증거 상태, 실제 numerical/analysis
semantic SHA, source-before/after 결과, 반환 archive의 bytes/SHA와 실제
업로드 링크를 포함해라. 성능·동일 코드 parity로 물리 정확도나 실제 receiver
adoption을 주장하지 마라.
