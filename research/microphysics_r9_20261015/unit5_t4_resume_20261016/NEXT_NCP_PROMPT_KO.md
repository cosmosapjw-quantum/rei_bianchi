# 복사 가능한 다음 NCP 실행 인계

아래 프롬프트를 NCP 접근이 가능한 local Codex에 전달하면 새 실행 예산을 명시적으로 부여하는 다음 작업이 된다. 이번 샌드박스에서 해당 실행은 수행하지 않았다. 파일을 사용자가 따로 내려받을 필요가 없도록 기존 저장소·NCP 파일과 설정된 rclone을 사용한다.

```text
R9 Unit5의 실제64→128 재개를 실행하고 결과를 회수·독립 검토·백업·게시해줘. 이 메시지로 별개의 새 실행 예산을 승인한다: 최대7200초,24GiB,OMP12/BLAS1,신규 Hamiltonian 작용 최대70회,최대128차. 원래 Unit4 기한과 UNKNOWN 횟수는 변경하지 마라.

기존 /home/cosmosapjw/Dropbox/bianchi/rei_bianchi의 AGENTS.md와 작업상태를 먼저 읽고, PR151 최신 head에서 research/microphysics_r9_20261015/unit5_t4_resume_20261016/{README.md,spec/CONTRACT.json,spec/THEORY.md,review/IMPLEMENTATION_REVIEW.json,progress/DELIVERY_FINAL.json}을 읽어라. clone/worktree/branch 전환이나 다른 owner 파일 변경 없이, 필요한 Unit5 파일을 GitHub API 또는 기존 git object에서 새 task staging으로 자동 취득하라. 검토가 수용한 code/test hash와 같음을 확인하라. 과거 S1 이론 게시 commit은 c2928c5d6d0e981d6a0d3b5b484237566e68fbc6이며 실제 실행은 최종 검토된 Unit5 코드를 쓴다. 이미 같은 작업이 실행 중이거나 끝났으면 재실행하지 말고 기존 결과를 회수하라.

기존 SSH 설정으로 NCP에 접근하고 /root/REI_R9_T4_SPECTRAL_20261016T001338Z_REPAIR001/checkpoint.npz 및 milestone_064.json, 기존 Unit4 inputs/data.npz·inputs/receipt.json·baseline/microphysics_driver_v6.py를 찾아 재사용하라. 사용자에게 파일 다운로드를 요청하지 마라. 누락 시 설정된 rclone dbx/gdrv로 자동 회수하라. checkpoint archive는 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/REI_R9_T4_CHECKPOINT064_20261016T010856Z.tar.gz, Drive id1DXvQ30UeWwBMt_ZReX0ndoHzl6V3pDWf이다. archive SHA256=098875b3d2a5c4e702a1d32e0fbac4b6eef36fc8b74f8f97210562037f47f14a, 내부checkpoint SHA256=1a056d3095f70c6f2473e1e242b1e0eb329427688df58a85cfdb2667938f704f이다. 원래 입력묶음은 REI_R9_UNIT4_T4_SPECTRAL_20261016.tar.gz, Drive id1h8b044Pia3JfM_tvL4IMTKeNN4YnrXGt, SHA256=91977313e1004be22a540b1fd2b874ded4d437301b1f61e9ff54d59cbbda275b이다. 복원 대상의 실제 identity를 계약과 대조하라.

현재 NCP 자원과 다른 owner 작업을 확인하고 원래20GiB host headroom을 유지하라. 기존 /root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python과 설치된 PySCF를 사용하라. prepared allocation_template의 새복사본에 고유allocation_id, authorized=true,실제시작issued_utc,그때부터최대7200초인absolute_deadline_utc를 기록하라. 실제실행 전 만든 만료된 설정을 재사용하지 마라. README의 완성된 run CLI에 실제 절대경로를 채워 새 출력디렉터리로 실행하라. SCF/바닥상태 FCI와 앞선64차 작용은 반복하지 마라. 재구성3회와 cache 표본확인3회도70회에 포함하라. xAct나 Wolfram 성공을 이번 자료에 소급 기재하지 마라.

실제checkpoint 복원·재압축·native 재구성·cache 비교·64→128 각각의 결과를 분리하여 기록하라. η=0.05,0.1,0.2 Eh의 기존 spectrum/CDF refinement 기준0.001을 유지하고, 잔차 기반 점별오차 진단을 함께 보고하라. 현재 잔차진단은 격자점마다 직접norm을 계산하므로 실제성능은 미측정이며7200초 내 완료를 보장하지 않는다. wall limit이면 체크포인트와 부분결과를 보존한다. 코드 변경이 필요하면 실패를 보존하고 AGENTS의 이론계약→구현→독립검토 분담을 적용한다. 원래시한 재설정이나 자동추가실행은 하지 마라.

새작용n회가 정확하면 캠페인 구간은[86+n,160+n]이다. 강제종료로 최종수가 불명확하면 그 불확실성을 보존하라. 합성시험의37회 또는[123,197]을 실제NCP 횟수로 사용하지 마라. W를 이온화확률로 해석하지 말고 실제refinement와 continuum/EC/완전기저 closure를 구분하라.

원시checkpoint·logs·receipt를 고유한 immutable archive로 묶어 기존 Dropbox 폴더와 Drive folder1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI에 이중백업하라. 제공된크기/checksum과 실제검증수준을 기록한다. PR151 최신head에 task-owned compact결과·source수정·독립검토·DAG·백업영수증만 fast-forward로 게시하고 원격대조하라. 큰raw는 백업으로 연결한다. force push/merge나 PR150 owner작업 변경은 하지 마라. 마지막에는 실제 수행값,부분완료 여부,남은 물리의존성을 반환하라.
```
