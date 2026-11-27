# 재시작 경계의 수신

REPORT_KO.md,CONTRACT.json,evidence/RESULTS.json과evidence/final/process_tests/SUMMARY.json은 DELIVERY_RECEIPT의 전체 ZIP에서 읽는다. 원 addon86payload를 수정하지 않았고 소비기는read-only다. 동일 finite검사를 전달 때문에 반복하지 않는다.

재현: source /path/to/rust_1_94_1_env.sh 후 bash run_checks.sh /absolute/new/verification. 실제 E2E를 통과한 wrapper이며 dependency는 ZIP안 localpath이다. mpmath나SciPy는 이번 재시작 경계 실행에 필요하지 않다.

일반 사용은 src/restart.py의--make-config로 명시적 검증용 설정을 생성하고--new로 새run을 시작한다. --stop-after3 같은 정지는 기존prefix를 남긴다. 재개는 같은 config/binary/controller와 기존directory를 지정하며--new를 빼야 한다. source/Ebar/tolerance를 바꾸어 기존run을 이어가지 않는다. --crash-stage/--crash-seq는 실제SIGKILL 시험옵션이므로 정상 연구에는 사용하지 않는다.

state/count/nextdt의 단일commit과 미확정 재평가를 구분한다. checksum은 인증이 아니며 corruptrecord에서 자동fallback/hash재작성은 금지한다. powerloss/NFS/cross-host/production성능 보장은 없다. owner의 기존add-on·수치예산 채택과F08예약을 유지하고 이 재시작 검증을 새로운 과학선행조건으로 만들지 않는다.
