#!/usr/bin/env bash
set -euo pipefail
OUT="$HOME/research_backups/rei_bianchi/20261015/c16b_v3"
ZIP="REI_C16_CASEA_ESCAPE_20261015_4f55234d_v3.zip"
SRC="$OUT/$ZIP"
DBX="dbx:bianchi/rei_bianchi/research/REI_C16_CASEA_SOURCE_BACKUPS/$ZIP"
DRV="gdrv:rei_bianchi_research_backups/$ZIP"
test -s "$SRC"
echo "UPLOAD_DROPBOX_START"; rclone copyto "$SRC" "$DBX"
echo "UPLOAD_DRIVE_START"; rclone copyto "$SRC" "$DRV"
for lane in dropbox drive; do
  upper=$(printf '%s' "$lane" | tr '[:lower:]' '[:upper:]')
  dest="$OUT/restore_$lane"
  mkdir -p "$dest"
  if [ "$lane" = dropbox ]; then address="$DBX"; else address="$DRV"; fi
  echo "RESTORE_$upper START"
  rclone copyto "$address" "$dest/$ZIP"
  cmp "$SRC" "$dest/$ZIP"
  python3 - "$SRC" "$dest/$ZIP" <<'PY'
import hashlib,sys
sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
a,b=map(sha,sys.argv[1:])
assert a==b,(a,b)
print('REMOTE_REDOWNLOAD_SHA256_MATCH',a,flush=True)
PY
  unzip -qt "$dest/$ZIP"
  unzip -q "$dest/$ZIP" -d "$dest"
  (
    cd "$dest/REI_C16_CASEA_ESCAPE_20261015"
    OPENBLAS_NUM_THREADS=1 python3 replay_v3.py
  ) 2>&1 | tee "$OUT/$lane""_62.stdout"
  cp "$dest/REI_C16_CASEA_ESCAPE_20261015/V3_TEST_RECEIPT.json" "$OUT/V3_$upper""_TEST_RECEIPT.json"
  echo "$upper 62_PASS_CONFIRMED"
done
python3 - "$OUT" "$SRC" <<'PY'
from pathlib import Path
import hashlib,json,sys,datetime
o=Path(sys.argv[1]);src=Path(sys.argv[2])
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
expected=sha(src)
lanes={}
for lane in ["dropbox","drive"]:
    copy=o/("restore_"+lane)/src.name
    report=json.loads((o/("V3_"+lane.upper()+"_TEST_RECEIPT.json")).read_text())
    assert copy.stat().st_size==src.stat().st_size
    assert sha(copy)==expected
    assert report["status"]=="PASS" and report["total_pass"]==62
    lanes[lane]={"remote_redownload_sha256":sha(copy),"filesize":copy.stat().st_size,
                 "fresh_replay_pass":report["total_pass"],"physical_HH_rate":"HOLD"}
data={"schema":"rei.c16B.v3.dual_cloud_verified.v1",
      "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "source_commit":"4f55234dee39e538de929b119c865dfcdbb5c673",
      "archive":src.name,"archive_sha256":expected,"bytes":src.stat().st_size,
      "dropbox":"dbx:bianchi/rei_bianchi/research/REI_C16_CASEA_SOURCE_BACKUPS/"+src.name,
      "google_drive":"gdrv:rei_bianchi_research_backups/"+src.name,
      "restore_replay":lanes,
      "scientific_admission":"NOT_ISSUED"}
(o/"DUAL_CLOUD_V3_RECEIPT.json").write_text(json.dumps(data,indent=2)+"\n")
print("DUAL_CLOUD_V3_PASS",expected,flush=True)
PY
