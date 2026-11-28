#!/bin/sh
set -eu
R=/root/WU088_NCP_EXEC_20261003_v2/prep_r2
/usr/bin/python3 -B "$R/observe.py" HOST_CGROUP_ANCESTORS
exec /usr/bin/unshare --mount --cgroup --propagation private /bin/sh -eu -c '
test "$(readlink /proc/self/ns/mnt)" != "$(readlink /proc/1/ns/mnt)"
test -z "$(findmnt -n -o PROPAGATION / | sed -n "/shared/p")"
umount /sys/fs/cgroup
mount -t cgroup2 -o ro,nosuid,nodev,noexec cgroup2 /sys/fs/cgroup
exec /usr/bin/setpriv --bounding-set=-all --no-new-privs /usr/bin/python3 -B /root/WU088_NCP_EXEC_20261003_v2/prep_r2/pipeline_r2.py
'
