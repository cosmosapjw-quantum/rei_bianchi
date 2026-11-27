# BASS_HE HE28 NCP 실행 인계: 소스 정제 코드는 완성, 실제 native 검증만 수행

사용자에게 파일 다운로드·업로드·명령 입력을 요구하지 말고 허용된 GitHub/NCP/클라우드 연결을 사용하라. 소스 개발을 다시 시작하지 말고 아래 고정 구현을 실행하라. 접근 권한을 우회하지 않는다.

## Authority

- 저장소: https://github.com/cosmosapjw-quantum/BASS_HE
- Draft PR76, branch `research/he28-strip-refinement-20261018`.
- 실행 코드 및 테스트 revision: `2e824c21d41c68f728f9630f2b219fa11f0c3b53`. 이후 문서·backup receipt 커밋은 읽되 물리 코드 변경이 없음을 확인한다.
- 폴더: `research/he28_strip_refinement_20261018`.
- 원본 native microphysics: `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`.
- HE27 완료 캠페인과 HE25/26 source/geometry/transport/reference는 재실행하거나 바꾸지 않는다.

먼저 README_KO.md, RESUME_REPORT_KO.md(후속 문서 커밋), DAG_STATUS.json, provenance/PARENT_SHA256.json, ncp/BOOTSTRAP.sh, src/he28_run.py를 읽어라. source_table_nodes=512에서 받은 pilot을256 또는1024의 study 승인으로 재사용하지 않는다. 소스·binary·owner·pilot 설계·table 기록의 일치 검사를 그대로 유지한다.

## 실행

1. 사용자 승인된 NCP에 직접 접속한다. Rust 경로 `$HOME/.cargo/bin`을 확인한다. 신규 Git checkout과 신규 work root만 사용한다. 기존 dirty tree, production 프로세스, 실패 기록을 지우지 않는다.
2. GitHub에서 위 브랜치를 직접 fetch하고 revision 및 parent source hash를 검사한다. 원본 owner repo가 이미 있으면 HE28_OWNER_REPO로 지정할 수 있지만 읽기만 한다.
3. 다음 명령은 Codex가 실행한다. HE28_WORK_ROOT에는 존재하지 않는 새 절대경로를 할당한다.

```sh
D="$PWD/research/he28_strip_refinement_20261018"
export HE28_WORK_ROOT="$HOME/HE28_NATIVE_$(date -u +%Y%m%dT%H%M%SZ)"
bash "$D/ncp/BOOTSTRAP.sh"
```

스크립트는 원본 Rust lib와 unchanged HE25 owner_server를 빌드하고 Python35개 테스트, preflight, q0/m4/r2/n16/GL4/table512 pilot(transport+동일-table Radau+DOP853)을 실행한다. 아직 이 native pilot은 수행되지 않았다. 건설된 fixture 테스트를 native 승인으로 승계하지 않는다.

4. 실제 pilot이 통과한 경우에만:

```sh
PY="${HE28_PYTHON:-$HE28_WORK_ROOT/venv/bin/python}"
"$PY" "$D/src/he28_run.py" campaign --stage study \
  --binary "$HE28_WORK_ROOT/build/he28_owner_server" \
  --build-receipt "$HE28_WORK_ROOT/build/RECEIPT.json" \
  --pilot-result "$HE28_WORK_ROOT/pilot/m4_r2_n16/RESULT.json" \
  --out "$HE28_WORK_ROOT/study" --table-nodes 512 \
  --table-mb 2048 --table-wall-s 600 --case-wall-s 3600
```

이 study는 q0/GL4, m8, r2/4/8, n32/64의6개 케이스만 실행한다. 전체 Cartesian sweep이나 자동 정밀도/허용치 변경은 하지 않는다. 같은 source/table에서의 단일 pilot 통과를 전역 spectral/time 수렴으로 부르지 않는다. 상수·원자 반응률·희소 strip 알고리즘은 이미 작성되었다. 허용되는 수정은 재현 가능한 경로/빌드 환경/실행 경계의 작은 수정뿐이며 물리적 재설계가 필요하면 실패 증거를 보존해 연구 스레드에 반환한다.

## Gate와 회수

기존 source moment3e-13, photon3e-15/H,energy3e-12eV/H,gas fractions1e-11,pilot temperature1e-8K,reference stability1e-9K를 유지한다. 첫 실패 원본 argv/stdout/stderr/table identity/gas state를 보존하고 무한 retry하지 않는다. study 완료 후 logs/build receipt/preflight/pilot/study 전체와 실제 소스 manifest를 별도 불변 아카이브로 만든다. BOOTSTRAP의 초기 evidence tar는 study 이전 파일만 포함하므로 study까지 포함한 새 return archive가 필요하다.

NCP는 컴파일/작은 환경 수정/실제 실행 담당이다. 단계마다 실제 DAG 진척, 새 결과 Git commit/Draft PR 및 create-only Dropbox+Drive 백업과 가능한 실제 full SHA readback을 기록한다. provider content_hash만 맞춘 경우 raw-byte readback과 구분한다. 공개 저장소에 SSH 키·토큰·개인 접속정보를 올리지 않는다. 본문 최종 보고에는 실행 case 수, native calls, 별도 residual/accuracy 판정, source/binary/table SHA, source-only와 native 증거 구분, cloud 복원 상태를 명시한다. 연속 스펙트럼·full EoR/upstream Grackle 직접 동등성/CMB 관측은 해당 범위의 검증 전 HOLD다.
