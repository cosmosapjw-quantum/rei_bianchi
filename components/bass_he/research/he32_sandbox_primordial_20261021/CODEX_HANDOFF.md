# Codex / NCP handoff: HE32 completed sandbox pilot

아래 내용을 다음 Codex 세션에 전달한다. 추가 연구 설계나 기존 IVP의 재실행을
기본 작업으로 삼지 않는다.

```text
프로젝트: cosmosapjw-quantum/BASS_HE
branch: research/he32-sandbox-primordial-pilot-20261021
PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/85 (draft, stacked on HE31)
unit: research/he32_sandbox_primordial_20261021
과학 코드·결과 증거 기준 commit (P3): 8d32c9944acffbeed5dc98325d283bf0c3b506f0
게시 영수증·완료 DAG가 포함된 복원 기준 commit (P4): 9179848428510efcc88c2b5da72efc9a71ef2182
자료 열람용 checkout은 P4 또는 그 이후의 문서 보완 commit을 사용한다.
P3_GIT_READBACK.json / FINAL_PUBLICATION.json은 P4에서 추가되었으므로
과학 기준 P3만 checkout한 뒤 그 게시 영수증 파일을 찾지 않는다.
과학 코드 baseline P2: 0c016a11966547d81dbc61117ab45e8f0ab81790
최종 코드·SVG·요약·증거 게시: delivery/P3_GIT_READBACK.json의 commit을 먼저 확인한다.
원자료394NPZ+case receipt+PNG: 검증된 전체 archive로 전달한다.
archive: BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz
SHA256: 27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a
Dropbox ID: id:BSpOijBcT10AAAAAAD_hsw
Git의 delivery/DATA_DELIVERY.json과 FINAL_BACKUP_ACK.json에 연결 증거가 있다.
과학 executor SHA256:
99f4a0e248d853d641393d78bcc330c4b3913ad1da1b326219e3fa3f60375314

완료 상태:
- sandbox에서 392개 nominal + 2개 L24 guard IVP를 평균 z20→2까지 완료했다.
- 21개 isotope/ion population, matter/photon/neutrino stress 및 PNG/SVG 그림 6개가 있다.
- 최적화 O.C1–10 → 물리 P.R1–10 → 최종 코딩 F.C1–10의 증거는 DAG.json을 읽는다.
- 원 실행 394개 이후 scratch-loss 복구 실행 394개가 별도로 수행되었다.
- 고유한 pilot identity는 394개이며 이미 완료되었다. benchmark는 0회다.

우선할 일:
1. 독립 worktree/checkout에서 pinned final commit과 위 unit의 파일 hash를 확인한다.
2. README.md, RESULTS_KO.md, results/SUMMARY.json, results/ANGULAR_GUARDS.json,
   evidence/physics/COMPLETED_PHYSICS_READBACK.json,
   delivery/P3_GIT_READBACK.json 및 delivery/FINAL_BACKUP_ACK.json을 읽는다.
3. Python 3.12.14 / NumPy 2.3.5 / SciPy 1.17.0 / Matplotlib 3.10.8 호환성을 확인한다.
   기존 자료를 열람하는 데 새 science IVP는 필요하지 않다.
4. 먼저 전체 archive SHA를 확인하고 README 절차로 results만 새 디렉터리에 복원한다.
   Git만 받은 상태에서는 NPZ가 없으므로 바로 plot하지 않는다.
5. 필요하면 복원된 saved-data plot/readback만 수행한다. 관측량 전달은 source identity와
   NPZ/receipt SHA를 유지하는 adapter 또는 데이터 복사로 처리한다.

물리 계약:
Sigma=sqrt6*abs(s)/H, P_X=kappa_T*sqrt6*p_X/H^2,
kappa_T=8*pi*G/c^2 for J/m^3 stress and H in s^-1.
Pi_r=abs(P_gamma+P_nu), Pi_total=abs(P_m+P_gamma+P_nu).

pi_m은 nonbaryonic fm=.1 sector의 응력이다.
Baryonic atomic gas에는 추가 closure pi_b=0을 적용한다.
8개 핵종 n,H1,D,T,He3,He4,Li6,Li7의 21개 중성/양이온 상태를 추적한다.
n=T=0이며, 동일 원소의 동위원소에 공통 전자율을 적용한다.
UV는 5.392–60 eV, E^-2.5이고 Tgas는 20000 K이다.
Gamma_HI=1e-12 expit((6-z)/.3). photo + case A RR만 포함한다.
Li III/IV는 선택한 support, IC 및 CI 부재에 따라 0으로 유지된다.
모든 불안정 동위원소·분자·음이온을 포함하는 망은 아니다.
z는 평균 1/a-1이다. 관측 재이온화 적합이나 fully reactive 19개 핵반응망으로
결과의 적용 범위를 확대하여 표시하지 않는다.

실행 명령 — 저장자료가 이미 있으면 중복 적분하지 않는다:
bash research/he32_sandbox_primordial_20261021/run.sh plan
bash research/he32_sandbox_primordial_20261021/run.sh plot --out "$HE32_RESULTS"
HE32_RESULTS는 README의 archive 복원 절차에서 지정한 디렉터리다.

새로 승인된 pending 작업이 있는 경우의 NCP 자원 설정:
bash research/he32_sandbox_primordial_20261021/run.sh run --max-workers 64 --reserve-cpus 2 --reserve-gib 16 --seconds 3600

실제 affinity, quota, busy 상태, RAM 및 shared lease 안에서만 작업을 할당하고
다른 job을 중단하지 않는다. worker당 native thread 1개를 사용한다.
과학 조건·tolerance 변경이나 대규모 재설계는 ChatGPT 연구 단위로 되돌린다.
실패한 identity와 partial output은 보존한다.
새 recovery_id/out을 지정해 실패한 작업을 재시도하지 않는다.
이번 missing-artifact recovery manifest는 완료된 원 receipt가 있고 실제 파일이
유실된 경우에만 사용했다. 다른 사건이나 새 campaign에 재사용하지 않는다.

전달 검증:
본문의 그림만 보고 완료로 판정하지 말고 전체 archive의 394개 NPZ와 receipt를 확인한다.
Git에 case JSON만 남기지 않았고, 일부 업로드된 binary Git object는 branch의 원자료 게시가 아니다.
Google Drive의 P1/P2 upload는 UNKNOWN_AFTER_INTERRUPTED_UPLOAD 상태다.
검증된 Git/Dropbox ACK와 구별하고 같은 Drive upload를 반복하지 않는다.
이전 조사 범위의 한계: 다른 대화 원문 회수는 0건이다. 1060개 heads의 목록은
확보했지만, 모든 branch 본문을 전수 독해한 것은 아니다.
```
