# C2c timeout cleanup 구현 기록

과학 계산을 시작하기 전에 발견한 독립 session worker의 orphan 위험을 수정했다. 최초 제조시험은 7개 중 PASS 1개, error 5개, failure 1개였다. 원인은 `Popen`의 안쪽 PID namespace와 `/proc` mount의 바깥쪽 namespace 불일치였다. 숫자 PID를 그대로 `/proc`에 대입하면 다른 process를 읽었으며, session identity 검증이 이를 거절했다. **관련 없는 프로세스에 보낸 signal은 0개, 과학 작업 0개, MPI 작업 0개**다. 테스트가 직접 생성한 sleep 프로세스만 종료했다.

이제 pid namespace inode를 먼저 일치시키고 `NSpid`, `NSpgid`, `NSsid`를 해당 namespace로 변환한다. 외부 procfs PID와 start time도 보존하고, batch/task 소유 token 및 session identity를 검사한 후 pidfd를 열고 identity를 재확인하여 signal을 보낸다. 재사용된 숫자 PID나 다른 batch의 registry에는 signal을 보내지 않는다.

과학 자식은 parent-death SIGKILL을 설정하고 expected supervisor PID를 두 번 확인한다. 부모가 ownership registry를 atomic+fsync로 저장한 뒤 pipe gate를 열어야 payload를 실행한다. MPI rank의 SIGTERM/finally와 외부 batch wrapper의 등록된 task cleanup을 함께 적용했다. 전체 wall cap은 작업중단 요청 시점이고 cleanup에는 작은 bounded grace가 추가될 수 있다.

수정 후 같은 7개 제조시험이 모두 PASS했다. 자기 child/grandchild 종료와 무관한 control 보존, start-time 불일치 거절, 소유권 불일치/미등록 task 보호, registry gate, 부모 사망, 개별 task timeout, rank SIGTERM을 확인했다. 기존 source/DATA/STATE 검증과 3개 native-library pin은 보존했다. 전체 출력의 핵심 수치와 source SHA는 동반 JSON에 있다.

참조: [proc_pid_status](https://www.man7.org/linux/man-pages/man5/proc_pid_status.5.html), [pidfd_open](https://www.man7.org/linux/man-pages/man2/pidfd_open.2.html), [pidfd_send_signal](https://www.man7.org/linux/man-pages/man2/pidfd_send_signal.2.html). 임의로 새 PID namespace를 만들거나 소유 token을 바꾸는 악성 자식 격리 기능은 주장하지 않는다.
