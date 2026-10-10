# c64home: the Commodore projects

This file is c64home's own `CLAUDE.md`, and `~/src/cbm/CLAUDE.md` is a symlink to it. Start sessions
in `~/src/cbm/` to work across all the Commodore projects, or in one project's folder to focus on it.
Either way this file loads. Paths here are relative to `~/src/cbm/`.

`~/src/cbm/` itself is not a git repo; it holds only the `CLAUDE.md` symlink and the project
folders. Each project below is its own repo with its own GitHub remote, except cbm-joy, which is
deliberately local-only. Trial projects (see below) have no git at all. Projects refer to each other by **relative path** (`../c64home`,
`../c64doc`), never by absolute path, so the whole tree can move as one unit. Unrelated projects stay
directly under `~/src/`.

## Projects

| Folder | What it is |
|---|---|
| `c64home/` | Toolchain and pipeline: build C/6502 asm/BASIC and beam it to a real Ultimate64 over WiFi. Also the shared knowledge base (`KNOWLEDGE.md`, `C64-REFERENCE.md`, `6502-OPCODES.md`, `CC65-TOOLCHAIN.md`) and reusable code in `lib/`. |
| `c64doc/` | Offline library of ~250 Commodore books, manuals and service docs, with a git-tracked catalog and full-text search. See `c64doc/CLAUDE.md`. |
| `cbm-joy/` | Test project: joystick-driven character on the C64 screen in pure 6502 asm, built and deployed through c64home. |
| `cbm-pics/` | Image prep for a Sony digital photo frame, mostly C64 game art, with VIC-II/TED palette work. See `cbm-pics/CLAUDE.md`. |
| `xum1541/` | Diskmasher: macOS GUI for writing/reading real CBM floppies via an xum1541 USB adapter. |

Start with `c64home/README.md` (what c64home is, ground rules for sibling projects) and
`c64home/KNOWLEDGE.md`. Projects without their own `CLAUDE.md` start from their `README.md`.

## Shared ground rules

- **Look things up in c64doc** before relying on memory for hardware facts (registers, memory map,
  KERNAL, DOS, drive internals). Cite as `<doc-id> p.<PDF page>`. The workflow is in
  `c64doc/CLAUDE.md`. The library itself lives only on Antti's daily Mac (and two backup drives); on
  other machines only the catalog is available.
- **Web lookups are allowed** (Antti, 2026-10-10) when c64doc and c64home don't cover a specific
  problem, but local sources come first, and using them needs no record. Whenever you do go to the
  web, **tell Antti right away**: what you looked for, and where the local docs fell short (not
  covered, unclear, contradictory, unreadable OCR). Also list each such gap in your next findings
  file, so it can be closed locally. Anything taken from the web is handled like this:
  - Save what you used into c64doc as a new library item (see "Adding something from the web" in
    `c64doc/CLAUDE.md`). It stays on this machine, and its card records the URL and fetch date.
  - Cite it by its c64doc id from then on, and label facts that rest only on it as web-sourced.
    They're lower trust than the books until something confirms them. Web fetches have gone wrong
    before (see "Research process notes" in `c64home/KNOWLEDGE.md`).
- **Mind what goes upstream.** c64home is public on GitHub; c64doc is private, and its library
  files aren't in git at all. Anything pushed to c64home is published, so paraphrase, quote only
  short passages, and never paste pages of a book, a web page or a library file there. Check a
  repo's visibility (`gh repo view --json visibility`) before pushing sourced material to it.
- **c64home is the source of truth for shared tooling and knowledge, and is read-only from sibling
  projects.** Use its tools by relative path (e.g. `../c64home/tools/select-u64.sh`), copy `lib/`
  code into your own project, and send reusable findings back as a new
  `c64home/findings-<unix-timestamp>.md` (see c64home's README, "Ground rules for sibling/sub-projects").
- Before writing a findings file, grep c64home's docs for each item and leave out what's already
  there. Details are under "What not to send" in `c64home/KNOWLEDGE.md`.
- New Commodore projects go in a new folder here, referencing siblings by relative path. A project
  whose README or first prompt calls it a **trial** is an experiment: its findings are welcome, but
  while it's a trial it gets no git repo or remote (don't offer `git init`), no row in the table
  above, and its code isn't a `lib/` candidate. That's a stage, not a verdict: Antti may promote a
  trial to a regular project, and only then does it get all three.
