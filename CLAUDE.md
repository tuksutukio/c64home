# c64home

Start with [README.md](README.md) (what this repo is, ground rules for sibling projects) and
[KNOWLEDGE.md](KNOWLEDGE.md). Hardware facts beyond `C64-REFERENCE.md` come from the document library
in `../c64doc` (see its `CLAUDE.md`).

## Pending

- **Move the Commodore projects under `~/src/cbm/`** (agreed 2026-10-09, not yet run). The one-off script
  `~/src/move-to-cbm.sh` (outside any repo) moves c64home, c64doc, cbm-joy, cbm-pics and xum1541 into
  `~/src/cbm/`. It also renames their `~/.claude/projects/-Users-tuksu-src-*` folders so session
  history follows, symlinks `~/src/cbm/CLAUDE.md` -> `c64home/umbrella-CLAUDE.md`, and runs checks
  (relative links, `make -n` in cbm-joy, `c64doc/tools/index.py --verify`, git status).
  - Antti wants a few words about it first, then runs it himself **with no Claude Code session open in
    any of those folders**. This includes the session that would discuss it, if that session runs
    inside c64home, so discuss, exit, then run.
  - Afterwards: start sessions from `~/src/cbm/<project>`, delete the script, and remove this item. If
    other machines (e.g. wet-mac) have clones, the same script works there.
  - Open question: cbm-joy has no GitHub remote yet (its history exists only on this Mac).
