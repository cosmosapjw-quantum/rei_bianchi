# PHYS29 portable stage 사용

`PHYS29_PORTABLE_STAGE.zip`은 runtime 26개와 manifest 1개를 담는다. 원 최초 raw 결과는 상위 연구 묶음의 `contributions/numerics/SECOND_ORDER_FIRST.json`에 있으며 stage 밖의 비교 기준이다. 실행 환경은 Python3.12.14의 표준 라이브러리다.

이 루프의 실제 replay는 이미 정확히 한 번 끝났다. 아래 명령은 이후 별도의 재현 사용자를 위한 실행 형식이며 현재 루프에서 추가 호출하지 않았다. `--destination`과 `--record-prefix`는 새 경로를 지정해야 한다.

```bash
python3 -B portability/repro.py \
  --archive portability/PHYS29_PORTABLE_STAGE.zip \
  --archive-sha256 8d33fe3493dad0164c0134def6e5d7a78c4250a4365b07949449022fec819230 \
  --destination /tmp/phys29_new_reproduction \
  --record-prefix /tmp/phys29_new_reproduction_evidence/REPLAY \
  --reference-result contributions/numerics/SECOND_ORDER_FIRST.json \
  --replay
```

과학 프로그램을 실행하지 않고 복구 bytes·modes·선언된 입력 closure만 확인하려면 별도의 새 경로에서 `--verify-only`를 쓴다. 이 모드에는 `--reference-result`가 필요하지 않다.

```bash
python3 -B portability/repro.py \
  --archive portability/PHYS29_PORTABLE_STAGE.zip \
  --archive-sha256 8d33fe3493dad0164c0134def6e5d7a78c4250a4365b07949449022fec819230 \
  --destination /tmp/phys29_verify_only \
  --record-prefix /tmp/phys29_verify_only_evidence/VERIFY \
  --verify-only
```

runner는 archive SHA, safe paths, regular mode, manifest의 정확한 member 집합, protocol20→freeze25→runtime26 관계를 확인한 뒤 복구한다. replay가 선택되면 invocation debit을 먼저 쓰고 새 과학 프로그램을 한 번 호출하여 raw stdout/stderr, exit, 시간, 결과와 원 기준의 byte/JSON 비교, runtime 전후 불변성을 기록한다. 자동 retry와 기존 결과 덮어쓰기는 없다. `build_stage.py`는 원 stage 생성 절차를 남긴 metadata 프로그램이며 이미 있는 stage/evidence 파일을 덮어쓰지 않는다.
