# Local Dropbox backup inventory scope

Inventory roots are exactly those listed in `ROOTS.tsv`: the owner-named BASS dossier, Dropbox BASS and WU088 backup roots, discovered REI backup folders, REI research archive/handoff packages and survey copies, and REC archive/handoff packages. The inventory does not claim to cover all Dropbox content.

Within selected roots, the walk records every non-directory filesystem entry, including large files, archives, raw evidence, and symlinks, without following symlinks. Exact path, byte size, file type/mode, and nanosecond mtime rendered in UTC are recorded. Archive indexing records only container member names and declared sizes; it does not extract members or read private payload contents. No entire archive is hashed or CRC-checked. Existing verified receipt hashes are reused as documentary metadata.

Excluded roots and classes: unrelated Dropbox projects (including HTT, squish_squash, TOV and personal folders); active source/project trees except the selected backup, archive and handoff package roots above; Git internals and worktrees; hidden tool/cache directories outside selected roots; all remote Dropbox contents; and package member contents other than bounded metadata documents specifically selected for intake. Missing roots, access errors, and archive-index errors are reported rather than silently treated as empty.
