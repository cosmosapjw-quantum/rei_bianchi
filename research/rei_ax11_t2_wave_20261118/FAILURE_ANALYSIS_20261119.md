# REI AX11 T2 ZERO/PLUS 실패 및 checkpoint 범위 물리 분석

**확인일:** 2026-11-19 KST. **결론:** INCOMPLETE / FILESYSTEM_IO_BLOCKED.  전체 zbar20→4 native endpoint와 D12 accuracy admission 없음.

**원본 고정:** `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`; source identity SHA256 `57a2c412c70295cbce9db88b92fe2d716fa904997ba07dbed23ae555bfa03eed`. T1 target 2.5e-6/start 1e-4; T2 target 6.25e-7/start 1e-10. 따라서 D12는 초기 step 선택까지 달라진 두 실측 실행 수준의 차이다.

## 원격 실행 상태

- 2026-11-19 17:09 KST: 컨트롤러 PID3172775와 두 native job은 없음. `RUN_LEDGER.json`의 `FULL_T2_RUNNING`은 오류 때문에 갱신되지 않은 값.
- `LAUNCH_CONTROLLER.log`는 `RUN_LEDGER.json.tmp`와 `launch_FAILURE.json.tmp` 저장 중 ENOSPC를 기록. 두 native stderr/stdout는 `AX11_T2_STOP AX11_T2_IO`, exit2.
- 11월19일 재현: `/mnt/extdrive`, `/mnt/extdrive/workdir`, 실행 root에서 10-byte 쓰기 모두 ENOSPC; `/home/cosmosapjw` ext4에서는 성공. NTFS/FUSE `/mnt/extdrive`의 보고된 여유공간 약1.8TiB, free inode 충분. 정확한 NTFS/호스트 장치 원인은 미확정.

|항목|ZERO|PLUS|
|---|---:|---:|
|accepted|182,640|182,340|
|trial|547,920|547,020|
|RHS|3,835,314|3,829,014|
|checkpoint scale factor a|0.05121695643|0.05121069474|
|checkpoint-supported T2 history rows|178,545|178,245|
|checkpoint 이후 미수용 history rows|0|60|
|checkpoint 이후 미수용 ledger rows|0|1,620|

GNU time receipts (native segment_000): ZERO CPU 390.66+2042.35=2433.01s, wall8254.88s; PLUS CPU 413.26+2032.24=2445.50s, wall8256.94s. Native 합 CPU4878.51s, job-wall16511.82s. Prepare 6.47CPU/8.506wall 별도. 자원 상한 도달 아님.

## checkpoint 범위 수치 판정

각 T2 CSV를 원 accepted4096 prefix + 원 checkpoint accepted count에 정확히 결속하고, PLUS의 checkpoint 뒤 60행은 제외했다. 두 history는 a와 time이 증가하며 H/He fraction 정규화 최대 잔차 1.11e-16. 각 case의 native ledger 27행/accepted state를 검사했고 PASS tolerance 위반 0.

ZERO ledger: 4,820,715행, PASS 535,635개. PLUS ledger: 4,812,615행, PASS 534,735개.

**분석 겹침 범위:** a=0.047628561041…0.051210694744, zbar=18.527171…19.995805. 동일 경과 proper-time 대응도 분석했다. 각 좌표99개 엄밀 내부 표본, 원 native 행 사이 선형 보간, 외삽 없음.

|관측량|fixed-a max abs(T2−T1)|equal-t max abs(T2−T1)|fixed-a max abs(paired D12)|equal-t max abs(paired D12)|
|---|---:|---:|---:|---:|
|x_HII|3.1840469e-05|3.1845448e-05|1.3066136e-09|2.5488906e-10|
|x_HeII|2.1594878e-07|2.1602047e-07|2.2918848e-11|6.2420208e-13|
|x_HeIII|1.0838476e-11|1.0843604e-11|1.5743706e-15|9.283184e-17|
|temperature_K|0.0047561234 K|0.0047579326 K|5.4520468e-07 K|3.9937788e-08 K|
|photon_n_per_H|1.4404698e-12/H|1.4408164e-12/H|6.3104292e-17/H|3.8530139e-17/H|
|photon_u_eV_per_H|3.2682334e-11 eV/H|3.2690294e-11 eV/H|1.4559745e-15 eV/H|8.7966976e-16 eV/H|

Fixed-a x_HII max case ~0.05117487341, T2-T1 x_HII is negative in both cases (~-3.18e-5), Tgas is positive (~+0.004756K). Pair D12 fixed-a xHII max 1.30661e-09 and equal-t max 2.54889e-10.

**해석 한계:** early z~20→18.53 partial segment에 대한 sampled D12만 있다. T1/T2의 startup h도 다르다. 전체 z=4 endpoint, 재이온화 milestone, original T0-T1-T2 수렴차수, 개별 gas/abundance error bound, dE·dμ 분리 검증은 미완료. Pair 차분의 상쇄를 개별 이력 정확도로 오인하지 말 것.

## 재개 조건

현재 마운트는 새 파일 생성이 불가능하므로 즉시 재시작 금지. 원본 read-only 보존, Linux ext4로 checkpoint/출력 백업, NTFS offline 진단 또는 충분한 ext4 출력 볼륨 확보 후, checkpoint, 누적 accepted/trials/RHS/wall, source+binary/config+IC, 출력 ledger boundary 및 남은 원 budget을 대조해야 한다. PLUS의 checkpoint 이후 60행을 재개 state로 쓰지 말 것. 기존 launch controller나 실패한 native process에 blind retry는 허용되지 않는다. 원래 `automatic_retries=0`을 유지하고 별도 확인된 재개 결정이 필요하다.

원 DAG 10/17, 확장 28/88 불변. Named consumer = REI owner / AX11. AX12 유예.

## 재현

`analyze_partial.py`는 두 원본 history의 공통-a 및 공통-time 99-point D12를 계산한다. `audit_ledgers.py`는 checkpoint 이후 행을 제거하고 원래 PASS gate를 검사한다. 모두 Python stdlib만 사용한다. 같은 작성자의 별도 audit이며 독립 blind referee는 아니다.

**원 실행 root:** `/mnt/extdrive/workdir/rei_ax11_t2_wave_20261118_v1`. **검사 결과:** `PARTIAL_T2_ANALYSIS.json`, `PARTIAL_T2_COMPARISON_99PTS.csv`, `PARTIAL_LEDGER_CHECK.json`.
