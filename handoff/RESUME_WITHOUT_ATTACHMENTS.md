# Resume without conversation attachments

## Preferred path: private GitHub connector available

In a new thread, provide only the repository URL and instruct the agent to read `handoff/CURRENT_HANDOFF_PROMPT.md`. The connector must have access to the private repository.

## Local sandbox path

```bash
git clone git@github.com:cosmosapjw-quantum/rei_bianchi.git
cd rei_bianchi
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
cat handoff/CURRENT_HANDOFF_PROMPT.md
```

## No connector

A private repository cannot be read by a web-only agent without authorization. In that case paste the contents of `handoff/CURRENT_HANDOFF_PROMPT.md`; no scientific artifact needs to be attached because the prompt contains exact repository paths and hashes.

## Offline recovery

```bash
git clone rei_bianchi_main.bundle rei_bianchi
cd rei_bianchi
git switch main
./scripts/bootstrap_sandbox.sh
```

For the archive branch:

```bash
git fetch ../rei_bianchi_full.bundle 'refs/heads/*:refs/remotes/archive/*'
```
