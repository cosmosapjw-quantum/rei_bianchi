set -euo pipefail
HE29_FETCH_STAGE="$(mktemp -d /root/HE29_HPC64_SOURCE_XXXXXXXX)"
HE29_SOURCE="$HE29_FETCH_STAGE/source"
git clone --single-branch --branch research/he29-survival-budget-20261018 \
  https://github.com/cosmosapjw-quantum/BASS_HE.git "$HE29_SOURCE"
HE29_LANE=research/he29_survival_budget_20261018/hpc64_20261021
HE29_PY=/root/HE29_REFERENCE_20261020T120000Z/venv/bin/python
HE29_CODE="$("$HE29_PY" -B - "$HE29_SOURCE/$HE29_LANE/DELIVERY.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1]))
pin=v.get('code_commit')
if (v.get('code_readback_status')!='PASS' or not isinstance(pin,str)
    or len(pin)!=40 or any(c not in '0123456789abcdef' for c in pin)):
    raise SystemExit('HE29_HPC_CODE_PUBLICATION_NOT_VERIFIED')
print(pin)
PY
)"
cp "$HE29_SOURCE/$HE29_LANE/DELIVERY.json" "$HE29_FETCH_STAGE/PUBLICATION_DELIVERY.json"
git -C "$HE29_SOURCE" checkout --detach "$HE29_CODE"
bash "$HE29_SOURCE/$HE29_LANE/ncp/RUN_READY.sh" "$HE29_CODE"
