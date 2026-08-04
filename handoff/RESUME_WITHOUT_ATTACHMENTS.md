# Resume without conversation attachments

The private repository is the durable source of truth. A new thread needs only the repository URL and the instruction to read `handoff/CURRENT_HANDOFF_PROMPT.md`.

## Preferred path: authenticated private GitHub access

```bash
git clone git@github.com:cosmosapjw-quantum/rei_bianchi.git
cd rei_bianchi
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
cat handoff/CURRENT_HANDOFF_PROMPT.md
```

The agent or connector must actually be authorized for the private repository. A web-only agent cannot read it merely because the URL is known.

## Offline immediate recovery: main branch

The cloneable main bundle contains the resumable source, compact authoritative artifacts, provenance ledgers, sandbox scripts, and current handoff.

```bash
git clone rei_bianchi_main.bundle rei_bianchi
cd rei_bianchi
git switch main
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
cat handoff/CURRENT_HANDOFF_PROMPT.md
```

## Offline complete-history recovery

The full mirror archive contains the bare Git repository, including `main`, `archive/full-history`, tags, and all split archive objects.

```bash
tar -xf rei_bianchi_full_mirror.git.tar
# This creates rei_bianchi_full_mirror.git/
git clone rei_bianchi_full_mirror.git rei_bianchi
cd rei_bianchi
git switch main
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
```

To inspect or restore the archive branch:

```bash
git switch archive/full-history
python scripts/reassemble_artifact.py \
  artifacts/archive/<artifact>.parts.json /target/directory
```

## Lightweight handoff package

`rei_bianchi_handoff_package.zip` contains the current prompt, project state, sandbox instructions, verification/push scripts, artifact registry, and the latest compact science bundle. It is not itself a Git clone, but it is sufficient to understand the current state and reconstruct a sandbox while the repository package is being restored.

## Private GitHub upload from an authenticated machine

After restoring either Git package:

```bash
export REI_BIANCHI_REMOTE=https://github.com/cosmosapjw-quantum/rei_bianchi.git
export REC_BIANCHI_REMOTE=https://github.com/cosmosapjw-quantum/rec_bianchi.git
# Configure a credential helper, `gh auth login`, or an SSH agent first.
./scripts/push_to_github.sh
./scripts/update_rec_bianchi_lock.sh || true
```

Never report a successful upload unless `git ls-remote`, every `git push`, and the final remote-SHA comparison all succeed.
