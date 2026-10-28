# Li IV 포함 17상태 time-evolution: 빠른 경로

현재 목표는 그림의 핵종에 대해 BBN abundance figure와 같이 시간에 따른 population을 표시하는 것이다. 사용자가 Li IV를 추가했으므로 표시 상태는 **17개**다. 이 경로의 첫 산출물은 이미 계산된 ANGTHERM01의 201개 출력 시점을 그대로 사용하는 기준 그림이다. 이후 n/T 생성·붕괴 및 광핵반응이 있는 물리 이력을 별도로 연결한다.

## 선택한 최단 경로

`기존 raw 이력 회수 → 17상태 추출 → population CSV·그림 → 독립 검토`를 먼저 수행한다. 새 IVP, EOS 역함수, native25, Einstein feedback 및 새로운 stellar emissivity는 이 기준 그림의 선행 조건이 아니다. 기존 full-pilot과 공급자 연구 lane은 그대로 유지한다.

| 구분 | 이번 선택 |
|---|---|
| 표시 상태 | n; H I/II; D I/II; T I/II; ³He I/II/III; ⁴He I/II/III; ⁷Li I/II/III/IV |
| 실제 source | ANGTHERM01 `grid044_M4_nominal.npz`, 저장된 201개 시점 |
| 구간·시간좌표 | η=ln(a/a_initial), η∈[0,ln 7], a_initial=1/21; mean-scale-factor z=21 exp(−η)−1, z=20→2 |
| population | 저장된 scaled population에 source의 isotope scale을 곱해 nᵢ/nHref를 복원; baryon number fraction은 전체 21상태로 계산한 n_b/nHref로 나눔 |
| 내부 보존량 | Li6 4개 상태를 포함한 기존 21상태 유지; 그림에는 앞의 17상태만 표시 |
| n·T | 이 저장 case의 입력·채널이 강제하는 정확한 0으로 표시. 물리적 부재 또는 생성률 상한으로 해석하지 않음 |
| 광자·배경 | 기존 초기 6-bin 광자와 처방된 비등방 배경. 지속 stellar/IGM 방출은 이 source에 없음 |
| 그림 형식 | 핵종별 패널, 명시된 number-fraction 정규화, 로그 population 축; 정확한 0은 별도 명시하고 인위적 floor를 만들지 않음 |

소스에 proper-time 배열이 없으므로 이번에는 원래 η 또는 mean-scale-factor z를 사용한다. 이를 방향별 관측 redshift 또는 우주 나이로 바꾸지 않는다. 핵종 총량이 고정된 기존 atomic-only 이력의 시간 변화는 ionization partition의 변화다. BBN과 같은 그림 형식은 핵반응으로 총량이 변하는 BBN 계산을 수행했다는 뜻이 아니다.

## 실제 조사·회수

접근 가능한 GitHub 51개 repo의 **2,403개 현재 branch ref**를 확인했다. 이전 inventory 대비 새 ref 6개·이동 ref 5개이고, 변경 ancestry의 추가 commit 33개와 갱신 PR 7개를 읽었다. 핵심 7개 repo는 열린 PR 962개도 페이지 끝까지 확인했다. 변경이 없는 immutable source는 이전 조사를 재사용했다. 이는 접근 가능한 현재 ref와 변경분의 조사이며, 삭제된 ref와 모든 과거 commit 파일의 재독을 뜻하지 않는다.

Dropbox는 직접 항목 344개와 9개 하위 폴더의 19개 항목을 확인했다. Drive는 직접 항목 347개를 반환했고 해당 도구에 별도 다음 cursor는 없었다. 이전 REI 기간 필터의 파일은 양쪽 127→129개다. 개인 대화 검색은 서비스에서 unavailable을 반환했다. 실제 공유 handoff·PR·백업 자료를 대신 읽었으며 접근하지 못한 대화까지 조사했다고 주장하지 않는다.

원본 archive `REI_ANGTHERM01_FINAL_20261023_46519489c540.zip`는 15,397,188 bytes이며 SHA256은 다음과 같다:

`46519489c5406499a6c74c826fc53f1b02a46de6846773773ddc7476c0e7a036`

회수한 bytes와 이 정확한 값을 대조했다. 기존 계산은 재실행하지 않았다. source science pin은 `d870ce943005bf93e332ca32ca8c945798b1331c`; PR221 source lineage와 archive의 개별 raw manifest를 함께 보존한다. source의 n/T=0, finite-grid admission, Li angular-continuum 제한은 그대로 이어받는다.

## 전체 목표에서의 위치

원래 DAG는 **작업 33/88, 중앙 28/88, 이번 증가 0**이다. 아래 F0–F6은 이번 빠른 경로의 별도 작업 지도이며 원래 88개 노드의 분모에 더하지 않는다.

| 노드 | 의무 | 현재 상태 |
|---|---|---|
| F0 | 최신 source·예약·예산과 17상태 범위 확정 | 완료 |
| F1 | 일치하는 원본 raw 이력·source·단위 회수 | 완료 |
| F2 | 17상태 추출 구현 및 저장값 대응 검사 | 코드 작성 완료; 실행 검사 대기 |
| F3 | 기준 time-evolution 그림·독립 검토·게시 | 렌더 대기 |
| F4 | n/T 생성·붕괴·광핵·역약반응의 실제 source/rate와 적용 구간 확정 | 미완료 |
| F5 | 승인된 유한 예산의 처방 배경 핵종/이온 계산 및 수치 검증 | 미실행 |
| F6 | 확장된 17상태 최종 그림과 독립 물리 검토 | 미완료 |

현재 빠른 경로 **2/7**. F2→F3으로 먼저 진행하며 F4의 입력 조사는 병렬화할 수 있다. F5는 F4의 채널·입력·유효범위와 별도 실행 계약을 요구한다. 첫 기준 그림을 최종 확장 물리 그림으로 승격하지 않는다.

## 세 물리 축

**대칭성·게이지:** source normal tetrad의 scalar population과 mean-scale-factor clock을 유지한다. η와 proper time은 일치하는 H의 Jacobian을 통해서만 변환한다. 방향별 photon redshift와 homogeneous background clock을 구별한다.

**불변량:** atomic-only block의 isotope-total 보존과 전체 내부 상태의 baryon/charge 수지를 유지한다. ⁷Li IV를 포함하므로 lithium charge partition은 네 단계를 모두 보여 준다. Li6도 내부 n_b와 전자 수지에 남긴다.

**실제 관측가능량:** 출력은 정규화가 명시된 population history다. abundance와 charge fraction을 구별하고, spectrum/optical depth의 별도 전방 모형 없이 이 곡선을 직접 관측 스펙트럼으로 부르지 않는다.

확장 단계의 β붕괴는 `n→H II+e⁻+ν̅ₑ`; spectator-electron 근사에서는 `T I→³He II+e⁻+ν̅ₑ`, `T II→³He III+e⁻+ν̅ₑ`로 연결한다. 이미지의 n→H I는 직접 붕괴 생성물로 사용하지 않는다. cosmic-ray와 lepton source가 없는 상태에서 역약반응률을 임의로 켜지 않는다.

## 실행 경계와 다음 행동

코드 작성·source 회수·정적 검토·게시 준비를 진행한다. 이전 임시 상한 planning18/presentation52는 이미 종료되어 원래10/30으로 복귀했으며 누적 charged 값은16.586967885/50.928518494다. main595.225063/600, NO_MORE_IVPs는 불변이다. 새 추출 검사와 렌더를 완료했다고 기록하지 않는다.

준비된 코드의 단 한 번 검사/추출/그림을 위해 제안하는 임시 누적 상한은 planning18, presentation55 CPU s다. 검사 예약은1.2 CPU s(자식1+wrapper/tail예비0.2), wall10 s이고, 추출·그림 예약은3.5 CPU s(자식3+wrapper/tail예비0.5), wall30 s다. 단일 worker·자동 재시도 없음으로 제한한다. 이는 원래10/30 대비50% 이상이므로 새 승인 대상이다. 승인 후 해당 단위만 실행하고 원래 상한으로 복귀하며 누적 debit·미계측 비용은 보존한다. 이 승인은 F5의 새 IVP를 포함하지 않는다.

자세한 source 목록은 `intake/CORE_SURVEY_SYNTHESIS.md`, `intake/other_repos_and_backups_summary.md`, `intake/local_sources.md`; 식·코딩 계약은 `theory/FROZEN_SELECTED_CONTRACT.md`를 따른다. SciSpace·Exa·Wolfram 사용 기록과 실제 채택/기각 범위는 `theory/SELECTED_TOOL_EVIDENCE.json`, `theory/LITERATURE_ROUTE_ANALYSIS.md`에 있다.
