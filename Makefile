MODEL ?= large-v3
DEVICE ?= auto
LANG  ?= fa

SUFFIX = $(shell python3 -c "import random,string; print(''.join(random.choices(string.ascii_lowercase, k=3)))")

.PHONY: help transcribe batch transcribe-all clean

help:
	@echo 'Usage: make <target> [OPTIONS]'
	@echo ''
	@echo 'Targets:'
	@echo '  help              Show this help'
	@echo '  transcribe        Transcribe a single file:  make transcribe FILE=voices/x.m4a'
	@echo '  batch             Transcribe multiple files: make batch FILES="voices/a.m4a voices/b.m4a"'
	@echo '  transcribe-all    Transcribe all .m4a in voices/ into one aggregated output'
	@echo '  clean             Remove all generated files from results/'
	@echo ''
	@echo 'Options (defaults):'
	@echo '  MODEL=large-v3    Whisper model size'
	@echo '  DEVICE=auto       Compute device (auto, cpu, cuda)'
	@echo '  LANG=fa           Language code'

transcribe:
	python3 transcribe.py --model $(MODEL) --device $(DEVICE) --language $(LANG) "$(FILE)" > results/$(shell basename "$(FILE)" .m4a).txt

batch:
	python3 transcribe.py --model $(MODEL) --device $(DEVICE) --language $(LANG) $(FILES) > results/combined-$(SUFFIX).txt

transcribe-all:
	python3 transcribe.py --model $(MODEL) --device $(DEVICE) --language $(LANG) voices/*.m4a > results/combined-$(SUFFIX).txt

clean:
	rm -f results/*.txt results/*.html
