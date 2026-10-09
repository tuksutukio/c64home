# c64home: the Commodore projects

This file is c64home's own `CLAUDE.md`, and `~/src/cbm/CLAUDE.md` is a symlink to it. Start sessions
in `~/src/cbm/` to work across all the Commodore projects, or in one project's folder to focus on it.
Either way this file loads. Paths here are relative to `~/src/cbm/`.

`~/src/cbm/` itself is not a git repo. Each project below is its own repo (or plain folder) with its
own GitHub remote, or none. Projects refer to each other by **relative path** (`../c64home`,
`../c64doc`), never by absolute path, so the whole tree can move as one unit. Unrelated projects stay
directly under `~/src/`.

## Projects

| Folder | What it is |
|---|---|
| `c64home/` | Toolchain and pipeline: build C/6502 asm/BASIC and beam it to a real Ultimate64 over WiFi. Also the shared knowledge base (`KNOWLEDGE.md`, `C64-REFERENCE.md`, `6502-OPCODES.md`, `CC65-TOOLCHAIN.md`) and reusable code in `lib/`. |
| `c64doc/` | Offline library of ~250 Commodore books, manuals and service docs, with a git-tracked catalog and full-text search. See `c64doc/CLAUDE.md`. |
| `cbm-joy/` | Test project: joystick-driven character on the C64 screen in pure 6502 asm, built and deployed through c64home. Local-only, no GitHub remote. |
| `cbm-pics/` | Image prep for a Sony digital photo frame, mostly C64 game art, with VIC-II/TED palette work. See `cbm-pics/CLAUDE.md`. |
| `xum1541/` | Diskmasher: macOS GUI for writing/reading real CBM floppies via an xum1541 USB adapter. |

Start with `c64home/README.md` (what c64home is, ground rules for sibling projects) and
`c64home/KNOWLEDGE.md`. Projects without their own `CLAUDE.md` start from their `README.md`.

## Shared ground rules

- **Look things up in c64doc** before relying on memory for hardware facts (registers, memory map,
  KERNAL, DOS, drive internals). Cite as `<doc-id> p.<PDF page>`. The workflow is in
  `c64doc/CLAUDE.md`. The library itself lives only on Antti's daily Mac (and two backup drives); on
  other machines only the catalog is available.
- **c64home is the source of truth for shared tooling and knowledge, and is read-only from sibling
  projects.** Use its tools by relative path (e.g. `../c64home/tools/select-u64.sh`), copy `lib/`
  code into your own project, and send reusable findings back as a new
  `c64home/findings-<unix-timestamp>.md` (see c64home's README, "Ground rules for sibling/sub-projects").
- New Commodore projects go in a new folder here, referencing siblings by relative path.

## Pending

- **Finish the move under `~/src/cbm/`.** The move itself is done (2026-10-09). Left over:
  - Delete the one-off `~/src/move-to-cbm.sh` (outside any repo). Antti's call.
  - Open question: cbm-joy has no GitHub remote yet (its history exists only on this Mac).
  - If other machines (e.g. wet-mac) have clones, the same script works there. Its symlink step
    still points at the old `c64home/umbrella-CLAUDE.md`; the link should be
    `~/src/cbm/CLAUDE.md -> c64home/CLAUDE.md`.
