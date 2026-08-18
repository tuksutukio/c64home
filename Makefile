TARGET   ?= c64
BUILD    := build
CL65     := cl65
RU64     := ru64

ULTIMATE_HOST ?= 192.168.1.165

SRCS := $(wildcard src/*.c) $(wildcard src/*.s)
PRG  := $(BUILD)/hello.prg

.PHONY: all run clean info

all: $(PRG)

$(BUILD):
	mkdir -p $(BUILD)

$(PRG): src/hello.c | $(BUILD)
	$(CL65) -t $(TARGET) -o $@ src/hello.c

run: $(PRG)
	$(RU64) $(ULTIMATE_HOST) run $(PRG)

info:
	$(RU64) $(ULTIMATE_HOST) info

screen:
	python3 tools/screendump.py $(ULTIMATE_HOST)

clean:
	rm -rf $(BUILD)
