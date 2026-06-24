MODEL ?= large-v3
DEVICE ?= auto
LANG_CODE ?= fa
DIR   ?= voices

SUFFIX = $(shell python3 -c "import random,string; print(''.join(random.choices(string.ascii_lowercase, k=3)))")

.PHONY: help transcribe batch transcribe-all clean

help:
	@echo 'Usage: make <target> [OPTIONS]'
	@echo ''
	@echo 'Targets:'
	@echo '  help              Show this help'
	@echo '  transcribe        Transcribe a single file:  make transcribe FILE=voices/x.m4a'
	@echo '  batch             Transcribe multiple files: make batch FILES="voices/a.m4a voices/b.m4a"'
	@echo '  transcribe-all    Transcribe all audio files in a directory: make transcribe-all [DIR=voices]'
	@echo '  clean             Remove all generated files from results/'
	@echo ''
	@echo 'Options (defaults):'
	@echo '  MODEL=large-v3    Whisper model size'
	@echo '  DEVICE=auto       Compute device (auto, cpu, cuda)'
	@echo '  LANG_CODE=fa      Language code'
	@echo '  DIR=voices        Audio directory (for transcribe-all)'

transcribe:
	python3 transcribe.py --model $(MODEL) --device $(DEVICE) --language $(LANG_CODE) "$(FILE)" > results/$(shell basename "$(FILE)" .m4a).txt

batch:
	python3 transcribe.py --model $(MODEL) --device $(DEVICE) --language $(LANG_CODE) $(FILES) > results/combined-$(SUFFIX).txt

transcribe-all:
	python3 transcribe.py --model $(MODEL) --device $(DEVICE) --language $(LANG_CODE) $(DIR)/* > results/combined-$(SUFFIX).txt

clean:
	rm -f results/*.txt results/*.html
