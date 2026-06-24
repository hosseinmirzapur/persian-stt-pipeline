#!/usr/bin/env python3
import sys
import subprocess
import json
import argparse
import traceback
from tqdm import tqdm
from faster_whisper import WhisperModel


def get_audio_duration(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", filepath],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        if "format" in data and "duration" in data["format"]:
            return float(data["format"]["duration"])
    except (json.JSONDecodeError, KeyError, ValueError, subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            return float(result.stdout.strip())
    except (ValueError, subprocess.CalledProcessError, FileNotFoundError):
        pass

    log("Warning: Could not determine audio duration. Progress bar disabled.")
    return 0.0


def main():
    parser = argparse.ArgumentParser(description="Transcribe Persian audio using Whisper")
    parser.add_argument("audio_file", help="Path to audio file (m4a, mp3, wav, etc.)")
    parser.add_argument("--model", default="large-v3",
                        help="Whisper model size (default: large-v3)")
    parser.add_argument("--device", default="auto",
                        help="Device: auto, cpu, or cuda (default: auto)")
    parser.add_argument("--language", default="fa",
                        help="Language code (default: fa for Persian)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-segment progress and debug info")
    parser.add_argument("--no-vad", action="store_true",
                        help="Disable voice activity detection filter")
    args = parser.parse_args()

    # Phase 1: Audio duration
    log("Phase 1/5: Probing audio duration...")
    duration = get_audio_duration(args.audio_file)
    log(f"Duration: {duration:.1f}s ({duration/60:.1f} min)")

    # Phase 2: Device detection
    log("Phase 2/5: Detecting device...")
    device = args.device
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            log(f"CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            device = "cpu"
            log("torch not available, using CPU")

    compute_type = "float16" if device == "cuda" else "int8"
    log(f"Device: {device}, compute_type: {compute_type}")

    # Phase 3: Load model
    log(f"Phase 3/5: Loading model {args.model} on {device}...")
    log("(This includes downloading if not cached, ~3GB for large-v3)")
    model = WhisperModel(args.model, device=device, compute_type=compute_type)
    log("Model loaded successfully.")

    # Phase 4: Transcribe
    log("Phase 4/5: Running transcription...")
    log(f"Settings: language={args.language}, beam_size=5, vad={not args.no_vad}")

    try:
        segments, info = model.transcribe(
            args.audio_file,
            language=args.language,
            beam_size=5,
            vad_filter=not args.no_vad,
            log_progress=args.verbose,
        )
    except Exception as e:
        log(f"ERROR during transcribe(): {e}")
        log(traceback.format_exc())
        sys.exit(1)

    log(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    log(f"Duration processed: {info.duration:.1f}s")
    log("Phase 5/5: Decoding segments...")

    pbar = tqdm(total=duration if duration > 0 else None, unit="s", desc="Progress",
                file=sys.stderr, disable=args.verbose)

    segment_count = 0
    total_chars = 0
    try:
        for segment in segments:
            text = segment.text.strip()
            segment_count += 1
            total_chars += len(text)

            if args.verbose:
                ts = f"[{segment.start:7.1f}s -> {segment.end:7.1f}s]"
                log(f"{ts}  {len(text):4d} chars  {text[:80]}")

            print(text, flush=True)

            if not args.verbose and pbar:
                pbar.n = int(segment.end)
                pbar.refresh()
    except Exception as e:
        log(f"ERROR during segment decoding: {e}")
        log(traceback.format_exc())
        sys.exit(1)

    if not args.verbose and pbar:
        pbar.n = int(duration)
        pbar.refresh()
        pbar.close()

    log(f"Done. {segment_count} segments, {total_chars} total chars.")


def log(msg):
    print(msg, file=sys.stderr)


if __name__ == "__main__":
    main()
