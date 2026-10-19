# 통합 패키지의 범위와 재현

이 패키지는 검산한 원본 RUN13 ZIP, 현재 게시된 RUN15 소스·결과·증거, 실행 가능한 두 native binary를 담는다. Git 역사 전체를 담은 bundle은 아니다. 소실 전 새 native 네 이력의 raw state·packet·ZIP은 포함하지 않는다.

## 배치

- `MANIFEST.json`: 모든 payload의 bytes/SHA-256, 파일 mode 및 고정 science Git checkpoint.
- `original/REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip`: 원본 41,075,268 bytes. SHA-256 `6912c7f90dedaaee312d3fdc3248e4e8839409c0fb2944262de945e1b2f34e96`.
- `run15/`: Git의 canonical 경로와 같은 RUN15 상대 배치. `source_recovery/`에는 회수 범위와 누락 범위를 명시한 과거 소스·기록이 있다.
- `run15/postloss_diagnostic/`: 현재 재현 가능한 새 fixed-gas 계산.
- `run15/postloss_native/`: 현재 컴파일 가능한 새 native positive quadrature 구현과 실제 세 CLI control.
- `run15/verification/`: 고정 Git science commit에서 실제로 수행한 범위 제한 clean reproduction 증거.
- `run15/bin/`: Linux x86_64에서 실제 빌드된 gas 및 postloss quadrature binary. 다른 플랫폼에서는 원본 source와 기록한 toolchain으로 빌드한다.

새 빈 디렉터리에 통합 ZIP을 풀고, 그 디렉터리에서 원본 ZIP을 `run13/recovered/`로 풀면 canonical native dependency 상대 경로가 성립한다. 원본 내부 경로는 `code/`, `inputs/`, `results/` 등의 상대 경로이며 ZIP SHA와 경로 안전성을 검증한 원본만 사용한다. 기존 디렉터리와 archive를 덮어쓰지 않는다.

```bash
python3 -m zipfile -e original/REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip run13/recovered
python3 run15/postloss_diagnostic/postloss_fixed_gas_optical_response.py \
  --source-root /ABSOLUTE/DELIVERY/run13/recovered \
  --output /ABSOLUTE/NEW_OUTPUT/FIXED_GAS_OPTICAL_RESPONSE.json
```

위 새 진단은 정의된 fixed-gas 경로의 다섯 설정을 계산한다. 원래 RUN13/RUN14 native IVP를 실행하지 않는다. 입력 hash는 실제 원본 manifest에 대조한다. Output path는 기존 파일이 없어야 한다. Toolchain 설치 및 native 재현은 `postloss_native/README_KO.md`와 `recovery/postloss_runtime_delivery/`의 정확한 recipe를 따른다.

통합 archive 자체의 SHA와 양쪽 원격 다운로드 대조는 archive 밖의 최종 `DELIVERY.json` 및 Git의 `RESUME_DELIVERY.json`에 기록한다. Archive가 자기 SHA 또는 자신을 업로드한 뒤의 receipt를 내부에 포함했다고 주장하지 않는다. 뒤의 delivery/verification commit은 검증한 science commit을 명시한다. 그 커밋에는 packaging·검증 helper와 receipt가 추가되며 과학 source/results는 바꾸지 않는다.
