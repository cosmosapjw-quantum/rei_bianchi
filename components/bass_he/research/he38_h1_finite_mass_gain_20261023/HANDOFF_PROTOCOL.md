# Final handoff authority and two audiences

HANDOFF_KO.md is the next ChatGPT research-thread handoff. HANDOFF_EXECUTOR.md is the narrow executor/restoration handoff. They retain workflow1.0.0/approval0.2, model identity, no-old-replay policy and the explicit original-goal gap.

Science files are frozen by SCIENCE_MANIFEST.json. The original C10 science commit records stage acceptance; a separately archived post-acceptance handoff correction may refine a future dependency without rerunning completed science. delivery/FINAL_ACK.json names the final science commit and records the original C10 acceptance commit separately. Delivery metadata and handoffs are intentionally outside that science manifest: after C10 backup/publication succeeds, the final archive ACK supplies the concrete science commit/archive SHA/DropboxID. A subsequent metadata commit publishes all20stageACKs and those handoffs. Its own SHA is recorded by the external final readback, not recursively embedded in itself.

The final saved verifier checks actual ACKs and snapshots; optional archive verification checks the new local stage/final tar payload bytes. Final remote Git tree verification binds every current unit blob to its local Git-object SHA1. All these checks execute no scientific model,IVP,benchmark or render.

If delivery is interrupted, continue from the recorded /tmp/he38_publish_state.json and actual ACK files. Never prepare an already accepted stage again. Upload failure before mutation permits retrying the same sealed archive; mismatched remote ref requires inspecting the new head before any update. Preserve failures and receipts.
