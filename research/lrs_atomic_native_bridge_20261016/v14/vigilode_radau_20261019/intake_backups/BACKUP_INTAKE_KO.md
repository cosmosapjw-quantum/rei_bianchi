# V16 백업 선행 intake

2026-10-19 12:26–12:40 UTC에 독립 read-only subagent `/root/drive_v15_intake`가 관련 provider의 목록과 작은 원문을 읽었다. **PR198 독립 LRS SSPRK2의 새 실행은 조회한 범위에서 관측되지 않았다.** 과학 코드를 바꾸거나 실행하지 않았고, 외부 업로드·수정도 하지 않았다.

## 현재 LRS 기준

부모 agent가 제공한 기준은 source `339dab4336d1fcfd38106640ee9bf7056dabcfd8`, final HEAD `fa9615a565a10a770eb1768d8f10cd503b0e1336`다. 최신 GitHub의 source와 raw 증거 판독은 부모 agent 담당이다.

기존 C10 archive `REI_LRS_V14_SSPRK2_C10_20261019_20261019T102447Z.tar.gz`의 전체 로컬 bytes를 실제 다시 읽어 8,323,125 B, SHA256 `1c55c41bb6426afed99a8df75e08f0df1b17502926defd413fbb5a2b1d3c015d`를 확인했다. Dropbox의 현재 ID `id:BSpOijBcT10AAAAAAD_QwQ`, 수정시각 10:27:39Z가 기존 전체 readback receipt와 연결된다. 새 과학 이력으로 다시 세지 않는다.

기존 post-clock source receipt, 실제 stdout와 exit 파일, CSV 본문을 읽었다. 표적시험 stdout에는 7+7 PASS가 있으며 build/test/fixed-geometry/birth 실행의 exit는 모두 0이다. 고정기하 CSV 504행, birth CSV 1,984행, transport 진단 CSV 52행의 전체파일 SHA가 기존 receipt와 연결된다. 고유 coupled history는 16개이며 sandbox CPU 실행이다. 이번 intake에서 NCP 실행이나 재실행을 하지 않았다. 구체적인 bytes, source hashes, stdout, CSV 첫·마지막 관측행은 `BASELINE_EVIDENCE_REUSE.json`에 보존했다.

## 조회 범위와 한계

| 경로 | 실제 관측 | 판정 |
|---|---:|---|
| Drive `REI_RESEARCH_BACKUPS/rei_bianchi` | 루트·13개 첫 하위·25개 말단, 합계 39개 폴더 | 관측 하위 트리 전체 순회, 폴더별 cap1000 미도달 |
| Dropbox `/bianchi/research_backups/rei_bianchi` | 38개, 1페이지 | `has_more=false` |
| Dropbox `/ode_solver` | 3개, 1페이지 | `has_more=false` |
| Dropbox `/VIGILODE_V35_BOOTSTRAP_IMPORT_20260819` | 5개, 1페이지 | `has_more=false` |
| Dropbox `REI_BASS_HIERARCHY_BACKUPS` | 27개, 1페이지 | `has_more=false` |
| Dropbox `REI_POSITIVE_AGE_REFERENCE_BACKUPS` | 18개, 1페이지 | `has_more=false` |
| Drive PR199/206 공통 parent `1phclg92jkhC5KgvnXhks8GbOFlya4qGe` | 112개, 하위 폴더 없음 | 관측 직접 자식 전체, cap 미도달 |
| Dropbox `/BASS_DERIVATION_DOSSIERS_20260912` | 4,600개 고유 경로, 8페이지 | 마지막 `has_more=false` |
| Drive RUN15/16 parent `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI` | 1,000개 | **넓은 dossier 전체는 부분 관측** |

마지막 Drive dossier 목록은 최대 1,000개 한도에 닿았다. `list_folder`에는 continuation을 전달할 수 없으며, `top_k=10000`은 provider가 최대 1000으로 거절했다. RUN15/16 이름의 별도 검색은 이미 목록에 보이는 ZIP/JSON을 누락하고 TXT만 반환했다. 따라서 검색의 빈 next-page 상태를 archive 완전성으로 사용하지 않았다. 관측 1,000개 안에서 RUN15/16의 관련 6개는 Dropbox의 전체 재귀 목록과 이름·크기·각 provider ID가 대응한다. 다른 오래된 Drive dossier 전체를 읽었다고 주장하지 않는다.

Drive V14에 이전 Stage A와 C10 final upload는 현재 목록에서도 보이지 않는다. 과거 upload는 ACK가 없었으므로 **UNKNOWN을 그대로 유지**한다. 목록 부재를 업로드 실패나 미생성 증명으로 바꾸지 않았고 중복 업로드를 하지 않았다.

## 관련 레인에서 새로 읽은 증거

VigilODE의 10월16일 README는 matrix-free Jacobian-free RODAS5P Rust library example과 cargo offline wrapper를 명시한다. source `ab8fbcdb709aa1e87603b1ef6f83c5e610c8cb04`는 README가 기록한 당시 source이며 최신 GitHub HEAD를 뜻하지 않는다. 54 calibration 결과는 모두 output-policy-dominated라고 명시되어 있어 성능·ranking·scaling·equal-error 증거로 이식하지 않는다. 오래된 bootstrap selftest의 SHA는 local test remote 전용이다. 이 두 폴더에서 10월19일 새 VigilODE 실행은 관측되지 않았다. Drive의 vigilode 문자열 content match는 MES 문서였고 그 문서는 VIGILODE를 의존성에서 제외했다고 명시했다.

PR199 age v5 confirmation의 실제 본문을 양쪽 provider에서 읽었다. source `9f85ea1a08063d27f1148b386b5e4fb0d4c16c28`, final `0ae749e9fdb179729c018706dbd59c4f61732b6a`를 기록한다. N4 exit1, 22.150563978초의 고정 support quantization 실패와 tiny off/on exit0·각1302 RHS를 구분한다. 이전 age64 block-max 결과를 새 LRS history로 세지 않는다. 이 confirmation은 현재 NCP 실행을 NOT_RUN으로 기록한다. Drive raw JSON은 17,287 B이고 Dropbox 추출문은 17,288 B다. 바이트는 다르지만 parse한 JSON은 동일하다. 비교는 `AGE_CONFIRMATION_READ.json`에 기록했으며 대형 archive 전체 readback을 이번에 했다는 뜻이 아니다.

PR206 BASS BR05의 76,033,888 B archive는 Drive와 Dropbox 양쪽 목록에서 관측했다. Dropbox ID는 `id:BSpOijBcT10AAAAAAD_QzQ`, 수정시각은 11:55:31Z다. 이 agent의 지위는 metadata 관측이다. 실제 source/stdout/result 검사는 부모 agent가 담당한다.

PR204 RUN15의 작은 resume와 surface-loss 기록을 읽었다. 소실 전 네 optical native 이력의 raw states가 현재 없다는 사실, transcript reconstruction-only 지위, 새 quadrature binary byte mismatch 미해결을 그대로 보존했다. PR205 RUN16 resume도 실제 읽었다. source `b808f9afddf3943eb0533bf86596d8bebb911ddd`, final `45ee7192b9d405214ec2650185aeaaa635e0fa13`를 기록하며 E16/T32 fixed-path response, 점 RHS85회, 첫 birth 이전 gas5변수 prefix RHS246회를 구분한다. full transport IVP는 0이라고 명시한다. 이는 PR198 SSPRK2의 새 실행이나 transport checkpoint가 아니다.

## 보존 및 다음 단계

`BACKUP_INTAKE.json`이 통합 결과이며 `RELATED_RUN15_RUN16_INTAKE.json`에 마지막 추가 범위, `DOSSIER_DROPBOX_INVENTORY.json`에 8페이지 전체 metadata를 보존했다. 읽은 작은 원문과 원본 Drive confirmation, 기존 source/stdout/exit/CSV 판독 snapshot도 같은 디렉터리에 있다. bearer URL과 계정 소유자 정보는 보존하지 않았다.

DAG 선행 intake는 위에 적은 provider 한계를 포함해 완료했다. 이 agent는 새 과학 admission을 발행하지 않는다. 부모 agent가 GitHub raw source/실행 결과와 결합해 다음 유한한 연구 단위를 결정한다. 기존 LRS source-on 전체2차, uniform stiff, fullEoR, CaseB, signed Bianchi의 지위는 이 intake로 승격하지 않는다.
