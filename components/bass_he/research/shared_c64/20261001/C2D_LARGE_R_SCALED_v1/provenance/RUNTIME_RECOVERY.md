# C2d 실행환경 복구

상태는 `RECOVERED_MANUFACTURED_CHECKS_PASS`다. 자동 workspace 정리로 사라진 MPI launcher·라이브러리와 Fortran compiler를 사용자 소유 prefix `/workspace/scratch/0b54847633d9/ncp_build_deps`에 복구했다. system install·패키지 설치 script·권한 변경·커널 설정 변경은 하지 않았다. 새 물리 계산, 고유상태 계산, 기존 과학 검증 suite 실행은 0회다.

Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, mpi4py 4.1.2는 기존 환경에 남아 있었다. OpenMPI 4.1.6 (`4.1.6-7ubuntu2`)와 GNU Fortran 13.3 (`13.3.0-6ubuntu2~24.04.1`)를 Ubuntu 2026-08-28 snapshot의 apt-indexed HTTPS package에서 복구했다. 18개 패키지의 URL, 크기, SHA512 및 SHA256은 `runtime_recovery_tools/PACKAGE_MANIFEST.json`에 있다. 다운로드는 indexed SHA512와 대조한 뒤 `dpkg-deb --extract`만 실행했다.

`apt-get download`의 내부 `_apt` 사용자 전환은 이 환경의 `setgroups/setegid/seteuid` 제약 때문에 실패했다. 해당 권한이나 sandbox 설정을 바꾸지 않고, 동일 공식 패키지 URL을 일반 HTTPS file download로 받아 해결했다. 이후 누락된 `libmunge2`를 같은 방식으로 추가했다. 성공한 초기 MPI 점검에서 보인 PMIx plugin 경로 및 UCX 네트워크 열거 경고는 실제 plugin directory와 `OMPI_MCA_osc=pt2pt`를 명시해 해결했다. 최종 점검의 stderr는 모두 비어 있다.

독립적인 제조 점검은 다음 두 가지다. strict `-O3 -fopenmp -fno-fast-math -ffp-contract=off -fno-associative-math` Fortran에서 1부터 8까지 제곱합이 정확히 204임을 확인했다. OpenMPI 2 ranks에서 정수 allreduce의 합이 3임을 확인했다. 이는 toolchain·통신 준비 검사이며 과학적 정확도나 성능 scaling 증거가 아니다.

부모 C2c의 native shared library 3개는 재빌드 없이 같은 bytes로 로드했다. prolate 및 inner ABI는 1, element ABI는 3이다. 복구한 Fortran frontend SHA256은 부모와 같은 `9c86153267d3b556b4c74c204f775737b39e2bdd611c62a39c71714cde6acb1d`다. 새 compiler wrapper SHA256은 `005876624a40c83047d773d7b33a8312a00d79df3b74e64bb61de331f1d64f6b`이며, 과거 build manifest의 wrapper identity를 바꾸지 않았다. wrapper는 host GCC 13 support objects와 기존 system libgfortran5를 사용한다. 후자는 prefix 안의 local symlink를 통해 참조한다.

현재 guest가 보고하는 CPU affinity는 9개, CPU quota는 8 core, cgroup memory.max는 8 GiB다. NCP 64-core/128-GiB 장비에 접속하거나 실측한 것이 아니다. 최신 read-only preflight에서 raw headroom은 6,299,758,592 bytes였다. worker당 1.5 GiB와 controller 0.5 GiB 및 20% reserve를 적용하면 raw 정책은 2 workers까지만 통과한다. 부모에서 이미 사용한 명시적 `clean-file-half-v1` 정책은 estimated available 7,194,179,584 bytes, reserve 후 5,755,343,667 bytes로 3 workers를 통과시켰다.

따라서 권장 구성은 **4 MPI ranks = controller 1 + workers 3, 각 OMP/BLAS thread 1**이다. 이는 snapshot상의 자원 승인이지 memory reservation이 아니다. 모든 과학 batch는 실행 직전 새 launcher gate를 반드시 통과해야 하며, 실패하면 실행하지 않고 3 ranks 구성을 새로 검사한다. `--bind-to none`은 이 sandbox의 명시적 예외이고 NCP의 core binding 기본값을 변경하지 않는다.

환경 설정은 C2d root의 `runenv.sh`에 있다. `source runenv.sh` 뒤 `/workspace/scratch/0b54847633d9/ncp_build_deps/root/usr/bin/mpirun.openmpi`를 사용한다. MPI는 `ob1`, `self,vader`, `osc=pt2pt`의 단일 호스트 구성만 검증했다. 다른 fabric, RDMA, UCX 또는 원격 node 통신의 완전한 dependency closure를 주장하지 않는다.

재복구에 필요한 작은 script와 제조 입력은 `runtime_recovery_tools`에 보존했다. 동일 scratch 경로에서 사용할 때 그 파일들을 `ncp_build_deps`로 복사하고 `recover_toolchain.py`를 실행하면 indexed packages를 다시 취득·검증·추출한다. compiler wrapper 실행 권한과 `runenv.sh`를 함께 복원한다. 원 패키지 캐시나 추출된 toolchain bulk bytes를 연구 archive에 중복 수록하지 않았다.

상세 명령, stdout/stderr, native identity, host inventory, 두 memory policy의 각 rank별 결과, 실패 분류는 `RUNTIME_RECOVERY.json`이 기준이다. inspector의 마지막 console summary에 발생한 ABI-key 출력 오류도 보존했으며, 이미 저장된 JSON 및 통과한 점검값에는 영향이 없었다.
