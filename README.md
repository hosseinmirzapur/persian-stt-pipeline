# Persian Audio Transcription & Article Polishing Pipeline

A two-stage pipeline that transforms Persian (Farsi) lecture audio into
print-ready HTML articles — powered by faster-whisper for speech recognition
and the `transcript-polisher` skill for editorial cleanup and layout.

## Features

- **Accurate Persian STT** — OpenAI Whisper `large-v3` via faster-whisper,
  with optional CUDA acceleration
- **Voice Activity Detection** — automatic filtering of silence and non-speech
  segments for cleaner transcripts
- **Intelligent normalization** — systematic correction of garbled ASR output
  (homophone errors, filler words, audio artifacts)
- **Print-ready HTML output** — RTL layout with Vazirmatn typography,
  warm-paper palette, gold accents, and A4-optimized print styles
- **End-to-end workflow** — from raw audio to publishable article in two
  commands with full provenance tracking

## Requirements

| Dependency       | Purpose                        | Install                              |
|------------------|--------------------------------|--------------------------------------|
| Python ≥ 3.10    | Runtime                        | system package                       |
| faster-whisper   | Whisper inference engine       | `pip install faster-whisper`         |
| tqdm             | Progress bars                  | `pip install tqdm`                   |
| ffmpeg           | Audio duration probing         | `apt install ffmpeg` / `brew install ffmpeg` |
| CUDA-compatible  | GPU acceleration _(optional)_  | NVIDIA GPU + CUDA toolkit            |
| GPU              |                                 |                                      |

## Installation

```bash
pip install faster-whisper tqdm
```

Verify the transcription engine works:

```bash
python transcribe.py --help
```

## Project Structure

```
.
├── AGENTS.md                      # Agent workflow reference
├── Makefile                       # Build automation
├── README.md                      # This file
├── transcribe.py                  # Speech-to-text engine
├── .gitignore                     # Excludes audio + results from VCS
├── .agents/
│   └── transcript-polisher/
│       └── SKILL.md               # Bundled skill (Step 2)
├── voices/
│   └── .gitkeep                   # Place .m4a / .wav / .mp3 files here
└── results/                       # Auto-generated (gitignored)
    ├── session-name.txt           # Raw transcription
    └── session-name.html          # Polished article
```

## Usage

### Step 1 — Transcribe

Run the transcription engine on one or more audio files, piping stdout to a
text file. The model is loaded **once** and reused across all files.

```bash
# Single file
python transcribe.py voices/session-name.m4a > results/session-name.txt

# Multiple files (aggregated output with file separators)
python transcribe.py voices/part-1.m4a voices/part-2.m4a > results/combined-xyz.txt

# Via shell glob
python transcribe.py voices/*.m4a > results/combined-xyz.txt
```

#### Options

| Flag            | Default     | Description                            |
|-----------------|-------------|----------------------------------------|
| `--model`       | `large-v3`  | Whisper model size                     |
| `--device`      | `auto`      | Compute device: `auto`, `cpu`, `cuda`  |
| `--language`    | `fa`        | Language code                          |
| `-v` / `--verbose` | off     | Per-segment details to stderr          |
| `--no-vad`      | off         | Disable voice activity detection       |

Output is written to stdout; progress and diagnostics go to stderr.

#### Examples

```bash
# Single file
python transcribe.py voices/jalase-11.m4a > results/jalase-11.txt

# Batch — all files in voices/
python transcribe.py voices/*.m4a > results/combined-xyz.txt
```

In batch mode, each file's output is separated by a comment-style marker:

```
# ============================================================
# file: voices/part-2.m4a
# ============================================================
```

### Step 2 — Polish

Load the **`transcript-polisher`** skill (bundled at
`.agents/transcript-polisher/SKILL.md`) and apply it to the raw text file.
The skill follows a 5-step workflow:

1. **Read & catalog** — identify garbled words and audio artifacts against
   the skill's Persian ASR error reference table
2. **Normalize** — correct all garbled words, strip artifacts and filler,
   convert spoken numbers to Persian digits. All substantive content is
   preserved.
3. **Structure** — organize the lecture into logical sections with headings
   (introduction, background, details, closing remarks)
4. **Build HTML** — generate a self-contained file at
   `results/session-name.html` with:
   - RTL direction, Vazirmatn font (Google Fonts)
   - Warm-paper palette (`#fafaf7` / `#fffdfa`), gold accents (`#c9a96e`)
   - `line-height: 2`, 750px max-width, centered
   - `.legal-quote` and `.highlight-box` styled components
   - Print-optimized: A4 margins, page-break rules, media query overrides
5. **Verify** — confirm all facts are preserved, no artifacts remain, HTML
   is valid and print-ready

## Output

The final HTML article is a single self-contained file you can:

- Open in any browser
- Print to PDF via Ctrl+P (A4, clean margins)
- Share as a standalone document
- Archive alongside the source audio

## Naming Convention

```
voices/session-name.m4a  →  results/session-name.txt  →  results/session-name.html
```

The session name must be identical across all three stages — no dropped or
added hyphens or underscores. This ensures full traceability from source
audio to polished article.

For batch transcriptions, the output follows the pattern
`results/combined-xyz.txt`, where the three random letters prevent name
collisions.

## Automation

A `Makefile` is provided for common operations:

| Command                          | Action                                         |
|----------------------------------|------------------------------------------------|
| `make transcribe FILE=voices/x.m4a` | Transcribe a single file                      |
| `make batch FILES="voices/a.m4a voices/b.m4a"` | Transcribe multiple files into one combined output |
| `make transcribe-all`            | Transcribe all `.m4a` files in `voices/`       |
| `make clean`                     | Remove all generated text and HTML files       |

Variables can be overridden:

```bash
make transcribe FILE=voices/jalase-11.m4a DEVICE=cpu
make transcribe-all MODEL=base LANG=fa
```

## Workflow Example

### Single file

```bash
# Via Python
python transcribe.py voices/jalase-11.m4a > results/jalase-11.txt

# Via Make (same result)
make transcribe FILE=voices/jalase-11.m4a

# Then polish — invoke transcript-polisher skill on results/jalase-11.txt
```

Result:

```
voices/
├── .gitkeep
└── jalase-11.m4a
results/
├── jalase-11.txt
└── jalase-11.html
```

### Batch

```bash
# Via Python (shell glob)
python transcribe.py voices/*.m4a > results/combined-abc.txt

# Via Make (same result)
make transcribe-all

# Then polish — invoke transcript-polisher on results/combined-abc.txt
```

## Tips

- **Large models** — `large-v3` downloads ~3 GB on first run. Ensure a
  stable internet connection.
- **GPU memory** — `large-v3` with `float16` on CUDA requires ~3 GB VRAM.
  Fallback to CPU with `--device cpu` on memory-constrained systems.
- **VAD filter** — Keep enabled (default) for edited recordings with pauses.
  Disable with `--no-vad` for continuous speech or music.
- **Long recordings** — The script streams segments incrementally. For
  hour-long lectures, allow 10-30 minutes depending on hardware.

## Included Skills

### transcript-polisher

Bundled at `.agents/transcript-polisher/SKILL.md`. This skill transforms raw
speech-to-text output into print-ready RTL HTML articles. It contains the
complete 5-step normalization workflow, a Persian ASR error reference table,
the HTML design specification, and the quality checklist used during Step 2
of the pipeline. The skill is versioned alongside the project so the
polishing workflow is always in sync with the code.

## License

MIT
