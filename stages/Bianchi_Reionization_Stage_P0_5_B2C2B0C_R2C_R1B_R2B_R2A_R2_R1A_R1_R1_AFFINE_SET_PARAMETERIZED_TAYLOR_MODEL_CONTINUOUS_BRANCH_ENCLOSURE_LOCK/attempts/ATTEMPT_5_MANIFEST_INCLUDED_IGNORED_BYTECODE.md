# Attempt 5 — manifest included ignored Python bytecode

The first bundle verification ran stage tests before `sha256sum -c`. Ten ignored `__pycache__/*.pyc` files had accidentally entered the stage manifest and compact ZIP even though Git did not track them. Fresh interpreters regenerated different bytecode, producing hash failures with a clean Git worktree. The stage sealer now excludes `__pycache__`, `.pyc`, `.pyo`, and pytest cache files from both manifest and compact artifact. Source/evidence hashes were unaffected.
