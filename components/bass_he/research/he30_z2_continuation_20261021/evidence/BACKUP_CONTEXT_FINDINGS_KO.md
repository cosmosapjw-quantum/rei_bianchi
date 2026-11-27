# 백업·대화·첨부 조사와 D3 원자료 복구

작성일: 2026-10-21. 담당: `/root/backup_context`. 이 문서는 연결된 저장소의 읽기 전용 조사와 원자료 복구 결과다. 새로운 IVP, 벤치마크, 과학 모형 코드는 실행하지 않았다. Git 브랜치/PR의 최신 원격 상태는 별도 upstream 조사와 함께 읽어야 한다.

## 가장 중요한 결과

최신 `REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`에 **z=20→2를 끝낸 237개 전체 상태 궤적**이 있었다. 기존의 HE PR82 raw 일부 유실을 재계산할 필요 없이 이 자료를 독립적인 source lane으로 재사용할 수 있다. 다만 HE PR82, C21M27, PR198, PR213과 초기값·출력구간·정규화가 모두 같다는 뜻은 아니다.

현재 복구된 권위 있는 자료는 다음과 같다.

- 원본 archive: `recovered/REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`
- 크기: 31,904,176 bytes.
- SHA-256: `7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498`.
- 현재 Dropbox 전체 GET과 provider block hash 일치 확인. Dropbox ID: `id:BSpOijBcT10AAAAAAD_gNA`.
- Dropbox 경로: `/bianchi/research_backups/rei_bianchi/REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`.
- 같은 이름의 Drive 객체 ID: `1_noyMOexSIBbHdWIqkoGsvt3nBxwGZGi`. 이번 조사에서 Drive 쪽은 metadata를 확인했고, 같은 archive의 Drive 전체 GET을 다시 하지 않았다.
- 안전하게 추출한 원본 pilot subtree: `recovered/REI_UNIFIED_D3/`. 일반 파일 2,325개, 40,991,814 bytes. 경로 traversal/절대 경로를 허용하지 않았고 archive 안의 실행 파일을 실행하지 않았다.
- 계약·과거 검토·D0 게시 영수증: `recovered/REI_UNIFIED_D3/_archive_evidence/`.
- 현재 데이터 읽기 검증: `recovered/D3_RAW_REUSE_READBACK.json`.
- 원본 source/실행 source/게시 상태를 구분한 기록: `D3_SOURCE_AUTHORITY.json`.

### 실제 완료 범위

| 자료 | 수량 | 실제 관찰 상태 |
|---|---:|---|
| B1 joint grid | 175 nominal + 3 guard | 35개 exact reuse, 143개 신규 계산 완료; CHECK numerical PASS_SCOPED_PRELIMINARY |
| B2 z4→2 tails | 231 nominal + 6 guard = 237 | 237/237 COMPLETED, STATUS exit=0, CASE_SET_EXHAUSTED |
| B2 joined histories | 237 × 153 epochs | 이전 121점 전체 보존 + 새로운 32점, z20→2 |
| Nominal full states | 231 × (40,153) | 모든 raw에서 직접 확인 |
| Guard full states | 6 × (56,153) | 모든 raw에서 직접 확인 |
| Current data integrity | 237개 전부 | raw/tail/prefix raw/input/result SHA 일치, 정확한 prefix/join/tail, 유한 배열, z20/z2 endpoint; 실패 0 |
| Original numeric checks | 237개 전부 | false check 0; six refinement controls PASS |
| Current independent scientific admission | 별도 검토 담당 | archive CHECK는 PENDING_INDEPENDENT_RESULT_REVIEW; 이번 복구 감사 자체는 과학적 admission을 발행하지 않음 |
| z2 그림 | 0개 | archive 안에 z2 PNG/PDF가 없으며 해당 PLOT.stdout/stderr가 비어 있음; 완료 raw에서 새로 그릴 수 있음 |

`UNIFIED_STATUS.md`와 `UNIFIED_DAG.json`의 D0/D1 문구는 실행 전 상태에 머물러 있다. 실제 D3 실행 결과는 `components/results/{CHECK,STATUS}.json`와 `z2_extension/results/{CHECK,STATUS}.json` 및 개별 raw/RESULT를 우선해야 한다.

### 과학 범위와 source identity

D3는 non-tilted LRS Bianchi I의 collisionless photon/neutrino hierarchy와 massive Vlasov matter, cold dust, Lambda를 사용한다. massive fraction 0.1, mass/Tref 30.0이다. matter와 radiation quadrupole은 독립 초기 축이다. gamma와 nu는 공통 초기 brightness를 사용한다. 새 native H/He thermochemistry나 CMB production admission을 포함하지 않는다.

Joint 초기 grid는 Sigma_F ∈ {0,0.0003,0.001,0.003,0.01,0.03,0.1}, signed P_m ∈ {-0.0003,-0.0001,0,0.0001,0.0003}, signed P_r ∈ {-0.001,-0.0003,0,0.0003,0.001}이다. 원래 radiation grid 91점과 joint 175점은 35점을 공유하므로 nominal union은 231점이다. 물리축의 zero-matter 원래 case는 config에서 P_m_i key가 생략될 수 있으므로 출력 `P_m`와 원래 config 의미를 함께 사용해야 한다. 단순한 missing-key 필터로 0축을 제외하면 안 된다.

Frobenius convention과 signed component 정보를 그대로 보존해야 한다. PR198 half-contraction convention과 비교할 때에는 명시적 sqrt(2) 변환이 필요하다. norm의 합과 tensor 합의 norm을 같은 것으로 처리하지 않는다. 세부식과 해석은 독립 물리 검토 담당이 확인한다.

Kernel authority는 REI PR147의 `3b85dedce84d37b3e165da00685a8a984950aafe` 및 `SOURCE_MANIFEST.json`의 vendor SHA다. 실행 wrapper는 unpublished source를 SHA로 식별한다. B1 및 최초 100 B2 tails의 runner SHA는 `49d4464ecb4682846ace0d07411d3a9f9e49bc494fa8d641b567306725374d97`; 보존 경로는 `z2_extension/verification/executed_source_49d/unified_pilot.py`다. 나머지 137 tails를 완료한 현재 runner SHA는 `a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64`다.

최초 100 tails는 전체 raw를 기록한 뒤 `numpy.bool_` JSON serialization에서 실패했다. 해당 raw와 최초 실패 영수증을 보존하고 데이터만으로 영수증을 복구했으며 복구 도중 ODE calls=0이다. 이 100개의 `nfev`, `solver_message`, `worker_wall_s`, `peak_rss_bytes`는 실제로 null이다. 나머지 137개에는 값이 있다. 누락된 실행 metadata를 새로 추정하거나 생성하지 않는다. 전체 endpoint/raw의 직접 확인과 과거 100개 독립 raw audit가 수치 자료의 회수 근거다.

D0 계약 게시 영수증은 branch `research/rei-age-exposure-envelope-20261018`, PR199, commit `8b71c13e23202edfce1ee67fb2da552fefb9a583`, parent `964b2e3c098f6e475999a4eddc7a6aa0f8f053cc`를 가리킨다. 이 영수증의 scope는 additive inventory/convention/prereview checkpoint다. **이것을 D3 전체 source/results가 Git에 게시됐다는 근거로 사용하면 안 된다.** 이번 조사에서 D3 전체 게시 영수증은 확인하지 못했다. HE에서 archive identity를 고정한 파생 후처리·그림을 게시하는 것은 이 불확실성과 양립한다.

## 실제 조사 범위와 한계

| 표면 | 실제 수행 | 완료/제한 |
|---|---|---|
| Personal context | 연결 도구 실제 호출 1회 | `Personal context is unavailable for this conversation.` 오류. 다른 모든 대화를 읽었다고 주장할 수 없음 |
| Dropbox HE dossier | `/BASS_DERIVATION_DOSSIERS_20260912`, recursive=false | 600+600+600+600+600+274=3,274 direct children, 6페이지, 마지막 has_more=false |
| Dropbox BASS backups | `/BASS_BACKUPS`, recursive=true | 213 entries, 1페이지, has_more=false |
| Dropbox REI backups | `/bianchi/research_backups/rei_bianchi`, recursive=true | 68 entries, 1페이지, has_more=false |
| Drive HE dossier | folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI` | top_k=1000으로 정확히 1000개 반환; 페이지 도구 없음. 전체 폴더를 다 보았다고 주장하지 않음 |
| Drive REI backups | folder `1phclg92jkhC5KgvnXhks8GbOFlya4qGe` | 150 entries, 요청 cap=1000 미도달; 이 반환 목록 범위 확인 |
| Search | BASS_HE, HE29, HE30, HE31, SIGMA_PI 등 | 검색의 false negative/무관한 fuzzy result 관찰. title search의 0건을 부재의 증명으로 쓰지 않음 |
| 로컬 첨부 | 명시적으로 제공된 20개 파일 | 크기·SHA·archive member 목록 기록; 관련 정책 텍스트 읽기 |
| 원격 Git branches/PRs | parent/upstream agent 담당 | 이 문서가 별도 조사 결과를 대신하지 않음 |
| NCP 실시간 상태 | 이 child에서 미관찰 | archive에 남은 과거 관측을 현재 서버 상태로 표현하지 않음 |

Drive `list_folder`를 처음 잘못된 argument로 호출하여 INVALID_ARGUMENT가 한 차례 발생했고, 실제 schema의 URL 입력으로 수정해 성공했다. 다운로드는 sandbox network 제한으로 최초 한 차례 실패한 뒤 명시적으로 허용된 read-only download의 승격 실행으로 성공했다. 일회용 다운로드 링크는 최종 증거에 저장하지 않는다.

원시 folder inventory는 사적인 무관한 파일명을 포함할 수 있으므로 공개 결과에는 이 요약과 관련 파일 provenance만 넣는 것이 적절하다. 원시 service 응답 전체를 무분별하게 Git에 복사할 필요가 없다.

## 구분해야 하는 이전 결과 lane

| Lane | 실제 범위/상태 | 이번 작업에서의 쓰임 |
|---|---|---|
| HE PR82 HE29 pilot | 역사적 28 original + 12 split = 40 completed IVPs; z20→4. Git recovery에는 original raw 27개, split raw 0개가 보존됨 | 유실의 존재와 운영 교훈 기록. missing13의 재실행 없이 D3 독립 lane 활용 |
| PR198 sigma-pi | 최초 625, 뒤 matter/radiation extension 606; 총 1,231 unique z20→4, half-contraction | 별도 source/규약으로 보존; D3와 동일 IVP로 자동 치환 금지 |
| PR213 / BASS PR176 split729 | 729 cases, 243 groups, 47,385 rows; native warm slice a=.1999→.2 | HE native kernel·reuse 참고. D3 z20→2 collisionless data와 물리 결과 합치지 않음 |
| D3 Lane B | 231 nominal + 6 guard, z20→2, Frobenius | 현재 목적에 직접 쓰이는 완료된 전체 raw |
| C21M27 | parent가 따로 회수한 signed S0±.012, Pm/Pr±.0002의 27-point 자료 | D3와 다른 초기축; 같은 case로 표시하거나 raw를 뒤섞지 않음 |

### HE PR82 missing raw 조사 결론

현재 HE README `RUNTIME_INTERRUPTION_RECOVERY`는 2026-10-21 10:29 UTC interruption/pruning 이후 보존 상태를 명시한다. `DELIVERY.json`의 code/results archive는 NOT_YET_UPLOADED이며, 관찰된 `HE29_REI_PILOT_INTAKE`는 intake/source만 담는다. inspect한 최신 HE 백업 범위에서 missing original 1개 + split 12개를 회수하지 못했다. 다른 모든 저장소/대화에도 없다고 단정하지 않는다. parent 지시 후 이 유실분의 추가 복구/재계산을 중지하고 D3 재사용을 우선했다.

## 내려받아 직접 byte identity를 확인한 archive

| 파일 | bytes | SHA-256 | 설명 |
|---|---:|---|---|
| HE29_REI_PILOT_INTAKE_20261021_96d2d9a4.tar.gz | 1,490,785 | 96d2d9a43c2556034bd0b7f4616229d92a5cbdd4a19c59f76a33fe8963dacacf | source/intake 137 members; missing pilot raw 아님 |
| HE29_HPC64_CANARY_ANALYSIS_CLOSEOUT_20261021_dc188d52.tar.gz | 83,377 | dc188d523167c1fe7cd092e021be2ba23be5c38a06306d8088156344e98a3427 | report/producer identity 41 files |
| BASS_HE_HE29_HPC64_CANARY_RETURN_20261021_a00990e5.tar.gz | 32,120,999 | a00990e5f8a5978a8881c1b56fb96072df5abd91600495494b9397cc9360aec7 | 21 outer files, nested canonical return 40 files; PR82 raw가 아님 |
| REI_BIANCHI_SIGMA_PI_PILOT_FINAL_20261021.tar.gz | 8,495,429 | db182cc8a4c09bc9e6c20d0864e2eb07c7cccb8ea2d509194852ca01c29acb7d | PR198 최초 625-case lane, 2,608 members |
| REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz | 31,904,176 | 7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498 | 현재 재사용의 중심, 2,361 archive members |

모두 Dropbox 현재 전체 GET을 수행했고, size 및 Dropbox block hash가 provider 값과 일치했다. HE canary는 m8/GL4/q0/r4/table512의 scoped single case이며 source `802a32361288bf5aa0e0d1f63c912768f1a1d407`, 182,280 native calls의 기존 receipt를 보존한다. 이것을 HE native whole EoR solver의 완료나 현 세션의 새 성능 측정으로 해석하지 않는다.

## 현재 읽은 index/ACK와 역사적 백업 영수증

PR198 matter/radiation final ACK는 archive 37,945,383 bytes, SHA `2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d`, reviewed source `b140170ce0c58159368b6b81be49ac35ca764851`, final delivery `8bd35af5f11c7ea5945b656be1c013d1c1933498`를 기록한다. 이 37.9 MB archive는 이번 child가 새로 full GET하지 않았으며 ACK와 D3의 과거 recovery report를 읽었다.

PR213 Stage5 index는 18 split parts, 원래 1,715 files / 423,198,268 bytes, original history SHA `139f3f75f535116483ff05dd96933611ac15896ce125c78d9394eb983bb58332` 및 과거 FULL_REMOTE_GET_AND_EXACT_REASSEMBLY_VERIFIED receipt를 기록한다. 현재 폴더 목록에서 18 parts를 확인했다. 이번 child가 18 parts를 전부 다시 내려받거나 재조립하지는 않았다.

Stage6 index는 109 payload files / 9,334,387 bytes와 2 zip parts / 4,683,866 bytes를 기록한다. branch `research/rei-sigma-pi-pilot-20261021`; BASS PR176 commit `25126962530d748c242fdf879833026bbdc90c48`; REI PR213 commit `c8e9f67aa031ffb33a9b0347bdea61dbb01fb746`. Stage6 snapshot은 raw history를 제외하므로 원본 raw 복원에는 Stage5가 별도로 필요하다.

`dropbox_fetch`로 받은 index/ACK는 추출된 text다. provider byte 길이와 local text 길이가 일부 2 bytes 차이 나는 것을 관찰했다. 따라서 local fetched-text SHA를 원격 raw index의 SHA로 표현하지 않는다. 보존 파일은 의미적 index/receipt 기록이며, 위 archive의 실제 bytes 검증과 구분된다.

## 첨부 정책·자료에서 적용한 규칙

- 01 문서는 원래 htt/bass용 comprehensive audit template다. 현재 사용자가 지정한 BASS_HE→REI 목적을 우선하고, same physics/tolerance/output의 최적화, actual code와 문서 구분, registry와 구현 구분, tilt와 단순 boost 구분을 재사용한다. 이번 요청에 없는 모든 family의 신규 audit를 추가하지 않는다.
- 04/05는 equation→code→observable 계약을 복구하고 minimal targeted patch, 물리 감사 후 코드 감사, 실제 plot 생성 후 시각 확인을 요구한다. 간단한 실행 성공을 과학적 타당성으로 대체하지 않는다. 현재 사용자가 제외한 상세 benchmarking 캠페인은 수행하지 않는다.
- 07/08 그림 규칙은 P0 의미·sign·norm, P1 잘림·겹침·가독성, P2 패널 구조, P3 미관 순으로 점검한다. finite grid를 허위 연속 영역으로 보간하지 않고, 축·단위·색 범위와 90/180 mm 가독성을 확인한 후 필요한 작은 수정만 한다.
- 03 환경 스크립트, 09 bootstrap, 16 checksum을 읽었다. bootstrap의 설치/전체 테스트를 실행하지 않았다.
- 17 BASS Rust core ZIP은 첨부 checksum과 실제 SHA `f30a4da90c68819d16df44632da91fa76e443df3b8dcf1d55c843bede1e1fb29`가 일치한다. Rust tar의 PGP signature 검증까지 했다고 주장하지 않는다.
- 18/19 문헌 ZIP은 member inventory만 확인했다. 문헌 내용 전체를 읽었다고 주장하지 않는다. 외부 최신 문헌 검토는 물리·문헌 담당의 primary-source 조사와 결합한다.

## 기존 HE 단계 백업 목적지

실제 HE29 intake/canary 객체를 확인한 기존 Dropbox 폴더는 `/BASS_DERIVATION_DOSSIERS_20260912`이고 namespace 표기는 `ns:183516487//BASS_DERIVATION_DOSSIERS_20260912`다. Drive 폴더는 `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, URL은 `https://drive.google.com/drive/folders/1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`다. 새 HE stage publication에서 이 목적지를 재사용할 수 있다.

## 다음 담당자에게 전달할 최소 계약

1. `D3_SOURCE_AUTHORITY.json`, D3 CHECK/STATUS, 현재 `D3_RAW_REUSE_READBACK.json`을 읽는다.
2. `REI_UNIFIED_D3/z2_extension/results/cases/*/raw.npz`의 237개 immutable raw를 후처리한다. 새 IVP는 필요하지 않다.
3. 231 nominal과 6 refined guard를 분리하고, signed P_m/P_r 및 norm을 보존한다. zero-matter 원래 config의 생략된 key를 0축 누락으로 처리하지 않는다.
4. 과거 100 serialization recovery의 null solver metadata를 그대로 유지한다. bytes가 검증된 raw와 history를 충분한 근거로 쓰되 없는 실행 로그를 채워 넣지 않는다.
5. 새 그림/파생 테이블 및 독립 결과 검토를 HE의 새 source commit에 연결한다. D3 archive SHA와 PR147 kernel pin을 둘 다 남긴다.
6. 원본 D3 Git publication은 별도 current readback이 확보되기 전까지 미확인이다. HE 파생 결과 게시와 원본 D3 게시를 구분한다.
7. 현재 다른 대화의 전수 검토는 Personal Context unavailable로 불가능했고, Drive HE 폴더는 1000개 cap이므로 조사 범위를 그대로 명시한다.
