# REI C16.0B v3 복원 및 경계 수송 인계 (2026-10-15 KST)

## 기준 소스와 검증

- 원본 연구 커밋: `4f55234dee39e538de929b119c865dfcdbb5c673` (PR149), **원본 과학 코드 변경 없음**.
- 독립 재생 ZIP: `REI_C16_CASEA_ESCAPE_20261015_4f55234d_v3.zip`; 201 entries; 1,777,437 bytes.
- 전체 SHA256: `df6e5344ec241d903716fd33e5ba2baadbe3c5e6002bfc8c10ea9db27fdbd2de`.
- v2의 195개 원본 payload는 유지. 누락된 원본 REI Rust `coverage.rs`, `ft03_controlled.rs`와 WU088_HH PHYS19 계약을 Git object SHA로 확인해 추가.
- 새 `replay_v3.py`는 full payload SHA와 source pin을 먼저 검사. WU 원래 guard가 Git HEAD를 출력하도록 요구하므로 추출 폴더에 **새 derived Git commit**을 생성하며, 이는 원본 HEAD가 아님.
- 로컬 새 디렉터리: C12 6, C13 16, C14 9, C15 11, C16.0A 9, C16.0B 11 = **62/62 PASS**, 실제 실행 exit 0.
- Dropbox·Google Drive의 독립 업로드·전체 재다운로드·whole-archive SHA/CRC·독립 62/62 재실행 각각 PASS. 세 테스트 결과와 cloud receipt 각각 기록.
- `build_v3_from_v2.py`, `dual_backup_v3.sh`, `BACKUP_RECEIPT_V3.json`, `V3_LOCAL_TEST_RECEIPT.json`는 이 branch에 별도 보존. 원본 v3 ZIP은 양쪽 cloud에 보관.
- Dropbox: `dbx:bianchi/rei_bianchi/research/REI_C16_CASEA_SOURCE_BACKUPS/REI_C16_CASEA_ESCAPE_20261015_4f55234d_v3.zip`.
- Drive: `gdrv:rei_bianchi_research_backups/REI_C16_CASEA_ESCAPE_20261015_4f55234d_v3.zip`.
- **논리적 판정:** C12 원래 PHYS44 negative admission 의미는 불변. HH physical rate `HOLD`; 전체 coupled EoR production scientific admission `NOT_ISSUED`.

## 구성적 이론: LRS Bianchi I의 문턱 이동 (PR150과 연결 가능한 별도 유도)

Metric `(-,+,+,+)`: `ds²=-c²dt²+a²[e^(-2b)(dx²+dy²)+e^(4b) dz²]`. `s=dot b`, `x=ln a`, `v=s/H` (signed). 방출시 `z=mu_e²`, `d=b-b_e`, `q=a_e epsilon_e`를 고정한 null Killing characteristic에 대해

`R²=(1-z)e^(2d)+z e^(-4d)`, `epsilon=(q/a)R`, `mu²=z e^(-4d)/R²`.

종 j의 이온화 문턱 `epsilon>=chi_j`는 참조 에너지 좌표에서

`q_threshold(x,z)=a(x)chi_j/R(x,z)`,

`d ln q_threshold/dx=1-v[1-3 mu²(x,z)]`.

따라서 모든 ray에 대해 문턱이 증가하는 정확한 signed shear 조건은 `-1/2<v<1`. 횡/축 ray에서 속도는 각각 `1-v`, `1+2v`. `Sigma=sqrt(3)|v|`만으로는 방향 부호 정보를 복원할 수 없음. 충분조건 `Sigma<sqrt(3)/2`는 양 부호에 공통이나 필요한 조건은 아님.

고정된 방출-cohort 양의 `q` number density `f(q,z)>=0`에 대해 (source-free case)
`N_active=integral_{q_threshold}^infinity f dq`,
`dN_active/dx=-q_threshold' f(q_threshold,z)`,
`dN_inactive/dx=+q_threshold' f(q_threshold,z)`.
첫 `q` 모멘트의 interface flux는 위 값에 `q_threshold`를 곱함. 경계에서 양·음 이동 모두 처리해야 하며, 합의 참조-`q` number/energy가 보존됨. **물리 에너지** `epsilon=(R/a)q`는 redshift/shear work에 의해 변하므로 다른 시각 사이의 물리 에너지 보존을 의미하지 않음.

이것은 exact collisionless kinematics 및 per-cohort moving-interface 계약(derived)일 뿐 PR150의 기존 FLRW fixed-covariant-q solver, cold H/He chemistry, sources, adaptive FV/FEM 구현을 교체하거나 완성하지 않음. 서로 다른 emission epoch를 하나의 angle-energy grid에 합칠 때는 cohort의 `b_e` 및 angle mapping을 보존해야 함.

## 독립 CAS 교차 검산

Wolfram Language에서 원래 C16.0B source-escaped 압력함수 `f(z)=[3Bz/sqrt(A+(B-A)z)-sqrt(A+(B-A)z)]/2`를 독립 미분해
`f'(z)=[A(A+5B)+(B-A)(A+2B)z]/[4(A+(B-A)z)^(3/2)]`를 정확히 검증 (차이 **0**).
분자 `z=0: A(A+5B)>0`, `z=1:2B(2A+B)>0`, 끝값 `-sqrt(A)/2,sqrt(B)` PASS. 별도 CAS로 `R`의 `d` 미분과 threshold signed 속도 항등식도 **0** 확인. source-fixed 선형 response 한정으로 유지.

## 문헌 연결 및 후속

- Pawlik & Schaye, *Multi-frequency, thermally coupled radiative transfer with TRAPHIC* (arXiv:1008.1071): photon-conserving H/He radiative transfer의 방법론적 선례.
- Norman et al., ApJS 216 (2015) 16, DOI 10.1088/0067-0049/216/1/16: coupled transport/chemistry 검증 방법의 선례.
- REI [PR150](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/150): FLRW active/passive fixed-reference energy transport, cut cells, 원래 cold solver에 선택적 도입. 본 branch는 PR150에 직접 source mutation 하지 않음.
- `bass_cr` [PR71](https://github.com/cosmosapjw-quantum/bass_cr/pull/71): 정확한 양의 child `q` moment가 공급될 때만 adaptive error envelope 활용. 부모 모멘트로 child를 임의 복구하지 않음.
- `rec_bianchi` [PR94](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/94): HyRec 잔류전자/온도 IC는 opt-in-only.
- `WU088_HH` [PR89](https://github.com/cosmosapjw-quantum/WU088_HH/pull/89) Coulomb 고각 경계 증명은 아직 REI HH 물리 rate 제공 아님.
- `BASS_HE` [PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64): 원래 warm 16-cell 결과, cold production 오인 금지.
- `bass` [PR161](https://github.com/cosmosapjw-quantum/bass/pull/161): 양의 massive Vlasov/recombination-independent stress 별도 lane.

64코어/128기가 NCP는 현재 로컬에서 `ssh -o BatchMode=yes <NCP_HOST>` 시험 결과 `Permission denied (publickey,password)`로 **미실행**. SSH 인증이 확보될 때 본문 외부 고부하 `PR150` q-refinement campaign을 별도 예약 실행할 것. 다른 DAG 작업 수정을 하지 말 것.

다음 최소 실행: 해당 source-fixed moving-threshold 식을 PR150과 명시적 source-ID 비교 후 (1) positive interface operator, (2) 두 방향 전이, (3) threshold-adaptive refinement, (4) photon-energy/thermal/ionization ledgers와 연속성 체크에 통합하는 별도 요청/branch 단계로 이관. 물리적 rate 확정이나 전 역사 수렴은 현재 claim 밖.
