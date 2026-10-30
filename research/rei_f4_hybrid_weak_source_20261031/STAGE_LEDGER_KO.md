# REI F4 | 이번 연구 단위의 R/C 단계별 근거

모든 단계는 **하나의 bounded physics computation**에 대한 실제 재사용/수행/검증 기록이며, 20개의 독립적 원본 IVP나 20개의 별도 심사가 아니다. 각각의 원본 stage JSON은 source-inclusive master ZIP의 `stages/`에 있으며, 이 Git 표는 단계별 인계·게시 인덱스다. 아래 세 숫자는 **Working DAG / Central DAG / Physical-fast DAG**, 매 단계 모두 변화 0이며 새 auxiliary node만 1/1 scoped.

| 단계 | 실제 근거·수행 산출물 | DAG (Working / Central / Fast) |
|---|---|---|
| R1 | 실제 source owner와 193 epoch 기준 고정 | 33/88 | 28/88 | 4/7 |
| R2 | BASS 약붕괴·Grackle 원전 및 기존 PR295/296/297 재사용 | 33/88 | 28/88 | 4/7 |
| R3 | Y=n_i/n_b, q,A,H,clock 및 owner 정합화 | 33/88 | 28/88 | 4/7 |
| R4 | H/He 행 치환과 weak-preserving 대안 구성 | 33/88 | 28/88 | 4/7 |
| R5 | A·J_naive≠0 반례 및 weak 복원식 직접 유도 | 33/88 | 28/88 | 4/7 |
| R6 | same-author 적대적 확인; distinct author NOT_RUN | 33/88 | 28/88 | 4/7 |
| R7 | Wolfram 보존식과 원본 193 source-J 확인 | 33/88 | 28/88 | 4/7 |
| R8 | source-scoped auxiliary 채택, F4 production HOLD | 33/88 | 28/88 | 4/7 |
| R9 | 21×21 계산식, off-manifold 약붕괴 항, thermal port 명세 | 33/88 | 28/88 | 4/7 |
| R10 | 44-file manifest/원본 source ZIP 및 재개 계약 | 33/88 | 28/88 | 4/7 |
| C1 | PR295 byte-lock & 193×21 native source/J 기준 | 33/88 | 28/88 | 4/7 |
| C2 | BASS F21,J21 및 REI HHe F5,J5×21 mapping | 33/88 | 28/88 | 4/7 |
| C3 | ne=n_b qY, 21-state hybrid J 및 열용량 공통 bath | 33/88 | 28/88 | 4/7 |
| C4 | 새 IVP 없는 독립 실행·재현 경로 | 33/88 | 28/88 | 4/7 |
| C5 | full source hybrid.py + compact minimal reconstruct 실행 | 33/88 | 28/88 | 4/7 |
| C6 | targeted Python 15/15, negative beta test | 33/88 | 28/88 | 4/7 |
| C7 | 193 epochs F/J 보존과 source direct oracle | 33/88 | 28/88 | 4/7 |
| C8 | small-rate finite diff 실패 분리, 해석적 Jacobian 검증 | 33/88 | 28/88 | 4/7 |
| C9 | same-author code audit; distinct-author NOT_RUN | 33/88 | 28/88 | 4/7 |
| C10 | 44/44 manifest, 9/9 output replay, ZIP/plots/handoff | 33/88 | 28/88 | 4/7 |

**Validation:** original PR295 full source ZIP SHA256 `156cad079282f8418530d1b38af8a4cc44e0a8711ed9c9e23367fff4db3fb7e9`; new master SHA256 `012635501cc5d9717ae775e9482b351b239003aa6c7db4dd2035ffa4760b7f2d`; 44/44 manifest; 15/15 targeted Python; 9/9 outputs. Native R6/C9 distinct-author NOT_RUN, native subagent NOT_RUN, production HOLD, no merges/IVPs/force pushes. Cloud copy ACK not established because the container session expired. Git code available at `code/reconstruct_minimal.py`, complete source implementation and 193x21x21 physical data reside in master ZIP.
