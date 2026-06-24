#!/usr/bin/env python3
import sys
import os
import subprocess
import json
import argparse
import traceback
from tqdm import tqdm
from faster_whisper import WhisperModel


SEP = "#" + "=" * 76


def is_audio_file(filepath):
    """Return True if the file is a valid audio or container format."""
    if not os.path.isfile(filepath):
        return False
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=format_name",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return False


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


def transcribe_one(model, filepath, args):
    """Transcribe a single audio file and print text to stdout."""
    duration = get_audio_duration(filepath)

    try:
        segments, info = model.transcribe(
            filepath,
            language=args.language,
            beam_size=5,
            vad_filter=not args.no_vad,
            log_progress=args.verbose,
        )
    except Exception as e:
        log(f"ERROR during transcribe({filepath}): {e}")
        log(traceback.format_exc())
        return 0, 0.0, 0

    log(f"Language: {info.language} (prob: {info.language_probability:.2f})")

    pbar = tqdm(total=duration if duration > 0 else None, unit="s",
                desc=f"{os.path.basename(filepath)}",
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
        return segment_count, info.duration, total_chars

    if not args.verbose and pbar:
        pbar.n = int(duration)
        pbar.refresh()
        pbar.close()

    log(f"Done: {segment_count} segments, {total_chars} chars.")
    return segment_count, info.duration, total_chars


def detect_device(device_arg):
    if device_arg != "auto":
        return device_arg
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        log(f"CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        device = "cpu"
        log("torch not available, using CPU")
    return device


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe one or more Persian audio files using Whisper"
    )
    parser.add_argument("audio_files", nargs="+", metavar="audio_file",
                        help="Path(s) to audio file(s) (m4a, mp3, wav, etc.)")
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

    valid = [f for f in args.audio_files if is_audio_file(f)]
    skipped = len(args.audio_files) - len(valid)
    if skipped:
        log(f"Skipped {skipped} non-audio file(s).")
    if not valid:
        log("No valid audio files to transcribe.")
        sys.exit(1)
    args.audio_files = valid

    total_files = len(args.audio_files)
    batch = total_files > 1

    # Device detection
    log("Detecting device...")
    device = detect_device(args.device)
    compute_type = "float16" if device == "cuda" else "int8"
    log(f"Device: {device}, compute_type: {compute_type}")

    # Load model (once, reused for all files)
    log(f"Loading model {args.model} on {device}...")
    log("(This includes downloading if not cached, ~3GB for large-v3)")
    model = WhisperModel(args.model, device=device, compute_type=compute_type)
    log("Model loaded successfully.")
    log(f"Settings: language={args.language}, beam_size=5, vad={not args.no_vad}")

    if batch:
        log(f"Batch mode: {total_files} files")

    total_segments = 0
    total_chars = 0
    total_duration = 0.0

    for i, filepath in enumerate(args.audio_files):
        if batch:
            log(f"[{i+1}/{total_files}] {filepath}")
            if i > 0:
                print(f"\n{SEP}")
                print(f"# file: {filepath}")
                print(f"{SEP}\n")

        seg_count, duration, char_count = transcribe_one(model, filepath, args)
        total_segments += seg_count
        total_chars += char_count
        total_duration += duration

    if batch:
        total_min = total_duration / 60
        log(f"All done. {total_files} files, {total_segments} segments, "
            f"{total_chars} chars, {total_duration:.1f}s ({total_min:.1f} min) total.")
    else:
        log(f"Done. {total_segments} segments, {total_chars} total chars.")


def log(msg):
    print(msg, file=sys.stderr)


if __name__ == "__main__":
    main()
