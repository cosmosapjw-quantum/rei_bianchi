#!/bin/sh
set -eu
R=/root/WU088_NCP_EXEC_20261003_v2/fd2_prep_20261004_v2
/usr/bin/python3 -B "$R/observe.py" FD2_PREP_OUTSIDE
exec /usr/bin/unshare --mount --cgroup --propagation private /bin/sh -eu -c '
test "$(readlink /proc/self/ns/mnt)" != "$(readlink /proc/1/ns/mnt)"
test -z "$(findmnt -n -o PROPAGATION / | sed -n "/shared/p")"
mount --bind /sys/fs/cgroup /root/WU088_NCP_EXEC_20261003_v2/fd2_prep_20261004_v2/host_cgroup_view
mount -o remount,bind,ro,nosuid,nodev,noexec /root/WU088_NCP_EXEC_20261003_v2/fd2_prep_20261004_v2/host_cgroup_view
umount /sys/fs/cgroup
mount -t cgroup2 -o ro,nosuid,nodev,noexec cgroup2 /sys/fs/cgroup
exec /usr/bin/setpriv --bounding-set=-all --no-new-privs /usr/bin/python3 -B /root/WU088_NCP_EXEC_20261003_v2/fd2_prep_20261004_v2/prepare_candidate.py
'
