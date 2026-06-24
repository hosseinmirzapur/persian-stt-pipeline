# Persian Audio Transcription & Article Polishing Pipeline

Transcribes Persian (Farsi) lecture audio using faster-whisper, then polishes
raw STT output into print-ready RTL HTML articles via the `transcript-polisher` skill.

## Directory Layout

```
voices/         Input audio files (.m4a, .wav, etc.)
results/        Raw transcripts (.txt) + polished articles (.html)
transcribe.py   Transcription script (faster-whisper)
AGENTS.md       This file
```

## Pipeline

### Step 1 — Transcribe

Run `transcribe.py` on an audio file, piping stdout to `results/<name>.txt`.

```bash
python transcribe.py [options] voices/<name>.m4a > results/<name>.txt
```

| Option       | Default    | Description                        |
|--------------|------------|------------------------------------|
| `--model`    | `large-v3` | Whisper model size                 |
| `--device`   | `auto`     | `auto`, `cpu`, or `cuda`           |
| `--language` | `fa`       | Language code                      |
| `-v`         | off        | Per-segment verbose output to stderr |
| `--no-vad`   | off        | Disable VAD filter                 |

### Step 2 — Polish (use `transcript-polisher` skill)

Invoke the **transcript-polisher** skill on the raw `.txt` and follow its
5-step workflow:

1. **Read & catalog** — build a table of garbled words and audio artifacts
   (see the skill's reference table for common Persian ASR errors like
   `ارز کنم` → `عرض کنم خدمت شما`, `حیعت مدیره` → `هیئت مدیره`, etc.)

2. **Normalize** — fix all garbled words, remove audio artifacts (cut-outs,
   connection complaints, filler), convert spoken numbers to Persian digits.
   **Preserve all substantive content.**

3. **Structure** — organize into logical sections with headings (introduction,
   historical background, changes, details, final remarks).

4. **Build HTML** — generate a self-contained file at `results/<name>.html`
   with:
   - RTL (`dir="rtl"`, `lang="fa"`), Vazirmatn font (Google Fonts)
   - Warm-paper palette: body `#fafaf7`, article bg `#fffdfa`, gold accents
     (`#c9a96e`, `#8b6914`)
   - `line-height: 2`, max-width 750px, centered
   - `.legal-quote` and `.highlight-box` styled blocks
   - Print-ready: `@page A4` margins, `@media print`, `page-break-inside`

5. **Verify** — checklist below.

### Step 3 — Verify

- All original facts preserved
- No garbled words remain
- No audio artifacts or filler remain
- Sections flow logically
- HTML is valid and print-optimized
- Vazirmatn font loads correctly
- Output saved to `results/<name>.html`

## Naming Convention

```
voices/<session-name>.m4a  →  results/<session-name>.txt  →  results/<session-name>.html
```

The session name must be identical across all three stages. No dropping or
adding hyphens/underscores.

## Quick Start

```bash
# Transcribe
python transcribe.py voices/jalase-11.m4a > results/jalase-11.txt

# Polish — invoke transcript-polisher skill on results/jalase-11.txt
# Output: results/jalase-11.html
```
