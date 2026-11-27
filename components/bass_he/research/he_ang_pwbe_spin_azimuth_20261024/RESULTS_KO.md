# PWBE — scoped science admitted, presentation open

Root R6 PASS와 R7 actual single evaluator10booleanTrue를 확인한 뒤 새 scope만 실행했다. 현재 상태는 **PASS_SCOPED_SCIENCE_PRESENTATION_OPEN**이다. 실제 독립 C9와 root admission은 `reviews/C9_REPORT.json` 및 `reviews/ROOT_ADMISSION.json`에 있다. C8은 PARTIAL이며 figure/render/visual review는 OPEN이다.

## Test evidence

초기 14 methods는 12 PASS/2 FAIL이다. Root가 두 건을 assertion-contract FALSE_FAIL로 분류하고 기존 close의 frozen rel2e-13/abs2e-15를 쓰는 한정 수정을 승인했다.Test01 exact dict equality를 세 값의 close로 대체하고 test06의 absolute=0 override만 제거했다. Tolerance 값과 core/source/theory/contract/analysis는 변경하지 않았다. 원본 test/runner와 diff는 reviews/C6-ASSERT-01_BEFORE에 있다.

Reserve 1 child에서 해당 두 methods만 PASS했다. 초기 12 PASS와 targeted 2 PASS를 합성한 근거이며 전체 14를 재실행하지 않았다. 초기 TEST_REPORT와 stderr는 보존했다.

## Six frozen geometry observations

Independent NumPy Cartesian source D/X amplitudes with direct nuclear subtraction and source spin weights/prefactor were averaged by periodic trapezoid; production closed azimuth routine was not the integrand. Global-angle/energy integral and source-table fitting were not performed.

| Geometry | final Kbar relative error | conditional cos absolute error | normalization error |
|---|---:|---:|---:|
| G1 | 7.15623529622744e-15 | 1.154231499391531e-16 | 6.772360450213455e-15 |
| G2 | 5.4440310711161585e-15 | 3.3306690738754696e-16 | 5.329070518200751e-15 |
| G3 | 5.594641514666567e-16 | 5.551115123125783e-17 | 4.440892098500626e-16 |
| G4 | 4.391425663952355e-16 | 2.220446049250313e-16 | 4.440892098500626e-16 |
| G5 | 1.0995603396105956e-15 | 3.3306690738754696e-16 | 8.881784197001252e-16 |
| G6 | 6.382081054537734e-16 | 0.0 | 6.661338147750939e-16 |

N=64/256/1024/2048 actual rows and conditioning flags are in results/AZIMUTH_ANALYSIS.json. All six final checks pass the unchanged1e-10criteria. The conditional normalization check uses the independent raw source density divided by the analytic closed normalization; the nonconstant API denominator is separately checked in test14. These are finite-case model-numerical observations.

## Actual attempts and costs

| Attempt | Result | CPU s | wall s | cap CPU/wall |
|---|---|---:|---:|---|
| 01_01_tests | FAIL | 0.09388400000000001 | 0.11865653000040766 | 2/5 |
| 02_01_tests | PASS | 0.08966199999999999 | 0.12036444200020924 | 2/10 |
| 03_02_azimuth_analysis | PASS | 0.172483 | 0.2182225649994507 | 2/5 |
| 04_03_plot | FAIL | 1.610416 | 1.6219177279999712 | 2/10 |

Measured cumulative CPU 1.966445, wall 2.079161265000039. Frozen new increment8/30, reserve1used/remaining0. No timeout/cap overshoot. Initial FAIL and plot FAIL remain charged; host/model/I/O and remote total CPU UNKNOWN_NOT_ZERO, end_to_end_cpu_cap_established=false. Historical ledgers/failures/unknowns were not reset/transferred.

## Plot failure and next action

First PNG draw failed at Mathtext title `\overline K` because `\overline{body}` requires braces. No PNG/SVG success or visual PASS is claimed. Raw traceback is evidence/execution/04_03_plot/stderr.txt. Plot only reads saved analysis; no numeric kernel changes. Root authorized only the three static label corrections documented below; no additional repair/render after reserve use.

The child supplies DERIVED_PWBE_MODEL_INPUT_AVAILABLE: analytic exact-swapped amplitudes and continuous pointwise joint density. Finite conditional-law implementation evidence is admitted by actual C9/root within the frozen scope. ParentHEANG SOURCE_INPUT_PENDING/physical_provider_admitted=false remain; remaining obligations are physical accuracy/calibration, finite-mass recoil, consumer admission and requiredsupport/uncertainty. No claim that no joint amplitude exists.

## Saved analysis comparison table

아래 값은 `results/AZIMUTH_ANALYSIS.json`의 `fixtures[].closed`와 마지막 level을 그대로 읽어 전사했다. 새 kernel 평가나 수치 재계산은 하지 않았다.

| Geometry | Kbar [a0²/Eh per sr²] | E[cos(phi)] | E[nA dot nB] | final Kbar relative error |
|---|---:|---:|---:|---:|
| G1 | 3.4992701523574837e-12 | 0.0 | 0.2 | 7.15623529622744e-15 |
| G2 | 2.4271929760419153e-05 | -0.9970629282251592 | 0.0014097944519235739 | 5.4440310711161585e-15 |
| G3 | 5.77548044734344e-12 | 0.2622029354496094 | -0.1410479178676509 | 5.594641514666567e-16 |
| G4 | 6.172267592876118e-05 | -0.9978972840121045 | 0.006150288565540729 | 4.391425663952355e-16 |
| G5 | 5.642122920098023e-10 | -0.9694320682299375 | -0.47707405117245305 | 1.0995603396105956e-15 |
| G6 | 4.050308029839717e-10 | 0.0 | -1.0 | 6.382081054537734e-16 |

## Static presentation correction and actual delivery state

Root classified the plot failure as presentation syntax only. The original plot and exact diff are in `reviews/C8-PLOT-01_BEFORE/`. Only `\overline K` → `\overline{K}`, `\frac14` → `\frac{1}{4}`, and `\frac34` → `\frac{3}{4}` changed. **NOT_RERENDERED=true**: no renderer/import/compile or fifth child occurred. C8 is PARTIAL; actual figure/render/visual review remains OPEN.

B1 actual dual upload and separate metadata readback are confirmed by `delivery/B1_BACKUP_ACK.json`: 210830bytes/37members/localSHA256 `4a3f1c5c2e9e7941d113c6217befcf51167eb0f0cb48c58bc0ab87d3652e8b49`; Drive `1mkc6jKqa2trgI_5gjm1UV3DABSGTmrmu`, Dropbox `id:BSpOijBcT10AAAAAAD_9Zg`. Independent remote SHA256 was not checked. The Science S snapshot recorded publication/B2/B3 as pending at its historical creation; actual S/C/B2 and current D state are updated in the delivery section below.

R7 used one actual evaluator:10booleansTrue, toolwall8.83s/bodyCPU.399022s/bodywall.400572s. Context1toolwall21.435s was unused/NOT_ADOPTED; totalremoteCPUUNKNOWN_NOT_ZERO. The private context bytes/hash are referenced in ASSESSMENT.json; future B2 must preserve private_context/CONTEXT_RAW.json without public documentation excerpts. No Wolfram replay occurred.

## Adopted outcome and stage completion

Actual C9 and root adopt **PASS_SCOPED_SCIENCE_PRESENTATION_OPEN**, with accepted states DERIVED / IMPLEMENTATION_VERIFIED_SCOPED / NUMERICALLY_CHECKED_SCOPED. Science S assesses all20stages:17complete,C8partial,R10+C10pending actual publication/backup/delivery. Final delivery may close R10/C10 to19complete while retaining C8partial;20/20 is not admitted. There are no open blocking scientific findings. C6-ASSERT-01 is closed with the initialfailure retained. C8-PLOT-01 remains OPEN for a future separately authorized saved-output-only render and actual visual inspection; no invocation is authorized now.

## 실제 S/C·B2와 현재 delivery D

Actual Science S는 `db91cbd3ac0f4db7908cd69c1f40e961f81051f9` (tree `d04f1bfb97d9c3a61835b3d0709825453f9b3a3f`), Central C는 `cdba5c98819ea615c32c4d7cea2c613a737e9eb1` (tree `231b55364af1ba41456da3cfc078e49c2e315bae`)다. PR97은 draft/open/unmerged이며 activation하지 않았다. 각각의 실제 byte readback은 delivery/S_PUBLISHED.json과 C_PUBLISHED.json에 있다.

B2는 2026-10-24 09:12:06UTC에 실제 양쪽 upload와 별도 metadata-size readback을 완료했다. 235069bytes/83members/localSHA256 `257d9c570d4ea66bb76b4645ced443215424f679f9976f8a9d1a0fb82e221e11`, Drive `1r5dabbTUT-rTVt4pSwQDs-36ET49PEg3`, Dropbox `id:BSpOijBcT10AAAAAAD_9bg`이며 양쪽 size는235069다. Independent remote SHA256은 검증하지 않았다. B2는 exact S74/C3와 실제 영수증·보존근거·미채택 privatecontext를 담으며, 이후 D/E는 포함하지 않는다.

현재 D의 commit identity는 **CURRENT_FILE_COMMIT**이다. D는 metadata-only이며 Science S의17complete/C8partial/R10+C10pending을 실제 전달 상태 **19complete/C8partial**로 연결한다. R10/C10의 정의된 scoped 인계·실제 S/C/B2 근거를 현재 containing commit에 결속했다. C8 figure/render/visual review는 OPEN이고20/20완료가 아니다. 후속 Central E와 D/E B3 supplement는 PENDING_ACTUAL이며 실제 B3 SHA/Drive/Dropbox ACK의 최종 위치는 [PR97 description](https://github.com/cosmosapjw-quantum/BASS_HE/pull/97)이다. 이 archive의 미래 ACK를 꾸미거나 science를 재실행하지 않는다.

## S 이후 병렬 owner 관측

Central 최신 parent는 `79c042a15e7e29b894dadc32188e286dade73aad`, tree `887f413e928d21f5f80fbd2e04b309610c6a8fc5`다. REI pressure는 실제1child와 exact8/9..1의 scoped admission을 받았으며 이전 S survey의 pressure NOT_RUN 관측만 갱신한다. 해당 비용은 HE 예산이 아니다. 새 Bianchi stock은 theory/static PASS, numerical NOT_RUN/proposal NOT_RELEASED, physicalstock/L4false다. Root가 읽은4문서와 freshness 및 짧은 addendum은 `evidence/survey/post_S_parallel_owner/`에 있다. Assembly/AGENTS는 불변이고48개 owner leaf를 보존한 새 base 위에서 E를 조립한다. S/B2는 불변이며 science 재실행은 없다. ANGTHERM02 READ_ONLY와 fullL1/physicalstock 미채택을 유지한다.

## 현재 additive C8 closeout — 새 prospective continuation 이후

Root의 새 명시적 user-loop authorization으로 old NO_FIFTH snapshot 이후 invocation-count 정책만 한정 갱신했다. 새 예산/reserve 없이 같은8CPU/30wall에서05 saved-output-only render(CPU3/wall10cap)를1회 실행했다. Kernel/source/tests/analysis/Wolfram 재실행은 없다. 실제05PASS CPU1.3375929999999998/wall1.3716336839988799, cumulative5attemptsCPU3.304038/wall3.4507949489989187이며 originalreserve1used0remaining을 유지한다.

독립 C9 delta와 root는 실제 PNG/SVG 및3panel시각확인을 PASS로 채택해 C8-PLOT-01을 닫았다. 왼쪽 peak/legend 공간 공유는 해석가능한 cosmetic observation으로 남겼고 추가 render를 요청하지 않았다. 현재 정의된 PWBE unit은 **20/20 scoped complete**이며 fullphysicalprovider=false/HEANGSOURCE_INPUT_PENDING/전체물리goalpercentnull을 유지한다. PR97 S/D/E 및 B1/B2/B3의 과거19complete/C8partial는 역사 기록으로 그대로다. 현재 closeout은 다음새branch의additive oldC8delta로 게시 대기하며 PR97을 작업자가 수정하지 않는다. 실제 근거: reviews/C9_C8_CONTINUATION_REPORT.json 및 ROOT_ADMISSION_C8_ADDENDUM.json.
