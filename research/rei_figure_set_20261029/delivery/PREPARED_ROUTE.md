# Final publication / backup route (prepared, not executed)

Preparation only. Root must freeze final artifacts and issue READY before publication. No final commit, PR, or backup was created in this preparation task. No solver or render ran.

- Repository: `cosmosapjw-quantum/rei_bianchi`.
- Existing branch: `research/rei-figure-set-20261029`.
- Checkpoint parent: `81721528c4a40b90aa38fd65a29f032dcf9c5f41`; base tree `750bce9547def68636514e51426bbf60f104ea60` (receipt already present).
- Stack new draft on `research/rei-physical-fast-20261028` (PR251). PR251 metadata was read again and still reports head `c5ab42c8673db614e7fb16695ad071c65becb81b`.
- No merge; update ref with `force=false` and expected checkpoint SHA. Check current branch if lease fails.

Git tools: `mcp__codex_apps__github_create_blob` accepts `content` with `encoding: base64`, so PDFs/PNGs can be real binary Git blobs; `github_create_tree` accepts `base_tree_sha` and `tree_elements`; `github_create_commit`; `github_update_ref`; `github_create_pull_request` accepts `draft:true`, `base`, `head`, and multiline `body`. Readbacks: `github_fetch_file`, `github_fetch_blob` / known Git blob identity. Discover exact current tool descriptions through ALL_TOOLS before use.

Existing backup destinations were separately verified:

- Drive folder ID: `1phclg92jkhC5KgvnXhks8GbOFlya4qGe`, name `rei_bianchi_research_backups`, URL `https://drive.google.com/drive/folders/1phclg92jkhC5KgvnXhks8GbOFlya4qGe`.
- Dropbox folder: `/bianchi/research_backups/rei_bianchi`, ID `id:BSpOijBcT10AAAAAAD8NWg`. Path with trailing slash returned INVALID_PATH; exact path without slash succeeded. Do not infer a mutation from this read error.

`mcp__codex_apps__google_drive_upload_file` accepts an absolute local path through `file_uri` adapter, plus `parent_folder_id` and `file_name`. `mcp__codex_apps__dropbox_upload_file` accepts absolute local path through `source_file` adapter, plus complete destination path including filename. Previous authorized deliveries used a content-addressed JSON capsule with UTF-8 text and base64 binary payloads, local SHA256, completed upload ACKs, and separate provider metadata sizes. Do not claim remote byte-download verification unless actually done. Add final delivery receipt to Git after freezing the capsule to avoid circular inclusion.

Exclude `intake/PRIVATE_*`, caches, transport payload copies, and stale PNGs from promoted deliverables. Preserve attempt1 under historical outputs as root decides. Root is cleaning final PNG names; do not infer that existing named PNGs are corrected. Final vector PDF/SVG files are corrected; only preview01–03 had new raster output at preparation time.

Current reports must reference actual reviewer filenames (root alerted: initial REPORT linked `review/DECISION.json`, assignment used `review/REVIEW.json`). Final root state/report/handoff/budget and review were still pending at preparation time.

Selected contract is exact user skill1.0.0: `skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop`; its RESEARCH_POLICY and EVIDENCE_AND_HANDOFF were read. c38 plugin now resolves1.3.0 and was observed only; it did not silently replace the frozen task policy. AGENTS requires lower-tier mechanical execution, so root requested a Sol delivery executor. Actual runtime model identity of this preparation agent is UNKNOWN.

Useful previous receipt examples: `research/rei_source_history_20261028/DELIVERY_RECEIPT.json` and `research/rei_ic_shear_20261028/DELIVERY_RECEIPT.json`. Avoid broad rg over payload JSON: those contain large base64 data. Packaging/transport cost is not scientific compute; any unobserved host/tool costs remain UNKNOWN_NOT_ZERO.
