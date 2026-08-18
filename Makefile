TARGET   ?= c64
BUILD    := build
CL65     := cl65
RU64     := ru64

ULTIMATE_HOST ?= 192.168.1.165

PRG ?= $(BUILD)/hello.prg

.PHONY: all run clean info screen

all: $(PRG)

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.prg: src/%.c | $(BUILD)
	$(CL65) -t $(TARGET) -o $@ $<

$(BUILD)/%.prg: src/%.s | $(BUILD)
	$(CL65) -t $(TARGET) -C c64-asm.cfg -u __EXEHDR__ -o $@ $<

run: $(PRG)
	$(RU64) $(ULTIMATE_HOST) run $(PRG)

info:
	$(RU64) $(ULTIMATE_HOST) info

screen:
	python3 tools/screendump.py $(ULTIMATE_HOST)

clean:
	rm -rf $(BUILD)
