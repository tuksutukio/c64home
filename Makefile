TARGET     ?= c64
BUILD      := build
CL65       := cl65
RU64       := ru64
PETCAT     := petcat
STATE_FILE := .ultimate_host

# Make this Makefile work regardless of shell type (interactive/login or
# not) without requiring ~/.zshrc to have been sourced -- see
# KNOWLEDGE.md's PATH section for why ru64/petcat specifically need this.
# NOTE: on macOS's stock GNU Make 3.81, this `export PATH :=` is silently
# ignored for any recipe line with no shell metacharacters -- Make execve()s
# those directly instead of routing through a shell, bypassing this
# reassignment entirely. Every recipe line below that depends on it ends
# with `;` to force shell routing (also see KNOWLEDGE.md).
export PATH := $(HOME)/.cargo/bin:/Applications/VICE-GTK3-3.9/bin:/opt/homebrew/bin:/opt/homebrew/sbin:$(PATH)

PRG ?= $(BUILD)/hello.prg

# No IP is hardcoded here -- run tools/select-u64.sh <name> to pick a
# device (see tools/u64-hosts.txt); it's remembered in $(STATE_FILE)
# (gitignored) until you switch again. Override per-invocation with
# ULTIMATE_HOST=<ip> without touching the saved selection.
ifeq ($(origin ULTIMATE_HOST), undefined)
ifneq (,$(wildcard $(STATE_FILE)))
ULTIMATE_HOST := $(shell cat $(STATE_FILE))
endif
endif

.PHONY: all run clean info screen host check-host

all: $(PRG)

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.prg: src/%.c | $(BUILD)
	$(CL65) -t $(TARGET) -o $@ $<;

$(BUILD)/%.prg: src/%.s | $(BUILD)
	$(CL65) -t $(TARGET) -C c64-asm.cfg -u __EXEHDR__ -o $@ $<;

$(BUILD)/%.prg: src/%.bas | $(BUILD)
	$(PETCAT) -w2 -o $@ -- $<;

check-host:
	@if [ -z "$(ULTIMATE_HOST)" ]; then \
		echo "No Ultimate64 selected. Run: tools/select-u64.sh <name>" >&2; \
		echo "Known devices:" >&2; sed 's/^/  /' tools/u64-hosts.txt >&2; \
		echo "(or pass ULTIMATE_HOST=<ip> for a one-off override)" >&2; \
		exit 1; \
	fi

host:
	@if [ -n "$(ULTIMATE_HOST)" ]; then echo "$(ULTIMATE_HOST)"; \
	else echo "(none selected -- run tools/select-u64.sh <name>)"; fi

run: $(PRG) check-host
	$(RU64) $(ULTIMATE_HOST) run $(PRG);

info: check-host
	$(RU64) $(ULTIMATE_HOST) info;

screen: check-host
	python3 tools/screendump.py $(ULTIMATE_HOST);

clean:
	rm -rf $(BUILD)
