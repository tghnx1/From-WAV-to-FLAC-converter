#!/usr/bin/env python3
import argparse
import concurrent.futures
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively convert FLAC files to WAV with FFmpeg."
    )
    parser.add_argument("input_dir", type=Path, help="Directory containing FLAC files")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: <input_dir>.wav)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 2,
        help="Maximum parallel conversions",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List planned conversions without running FFmpeg",
    )
    return parser.parse_args()


def check_dependencies() -> None:
    missing = [command for command in ("ffmpeg", "ffprobe") if not shutil.which(command)]
    if missing:
        raise RuntimeError(f"Missing required command(s): {', '.join(missing)}")


def choose_codec(bit_depth: str) -> str:
    return {
        "16": "pcm_s16le",
        "24": "pcm_s24le",
        "32": "pcm_s32le",
    }.get(bit_depth, "pcm_s24le")


def discover_flac_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.rglob("*") if path.suffix.lower() == ".flac")


def get_bit_depth(filepath: Path) -> str:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=bits_per_raw_sample",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(filepath),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "24"


def extract_metadata(filepath: Path) -> list[str]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format_tags",
            "-of",
            "default=noprint_wrappers=1",
            str(filepath),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    arguments: list[str] = []
    for line in result.stdout.splitlines():
        if "=" in line:
            key, value = line.strip().split("=", 1)
            if key and value:
                arguments.extend(["-metadata", f"{key}={value}"])
    return arguments


def extract_cover(filepath: Path, output_path: Path) -> None:
    cover_path = output_path.with_suffix(".jpg")
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(filepath),
            "-an",
            "-vcodec",
            "copy",
            str(cover_path),
        ],
        capture_output=True,
        check=False,
    )
    if not cover_path.exists() or cover_path.stat().st_size == 0:
        cover_path.unlink(missing_ok=True)


def output_path_for(filepath: Path, input_dir: Path, output_dir: Path) -> Path:
    relative_path = filepath.relative_to(input_dir).with_suffix(".wav")
    return output_dir / relative_path


def convert_file(filepath: Path, input_dir: Path, output_dir: Path, dry_run: bool) -> bool:
    output_path = output_path_for(filepath, input_dir, output_dir)
    if dry_run:
        print(f"{filepath} -> {output_path}")
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    codec = choose_codec(get_bit_depth(filepath))
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-i",
        str(filepath),
        "-c:a",
        codec,
        *extract_metadata(filepath),
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True)
        extract_cover(filepath, output_path)
        print(f"Converted: {output_path} ({codec})")
        return True
    except subprocess.CalledProcessError:
        print(f"Conversion failed: {filepath}", file=sys.stderr)
        return False


def main() -> int:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = (args.output_dir or Path(f"{input_dir}.wav")).resolve()

    if not input_dir.is_dir():
        print(f"Input directory does not exist: {input_dir}", file=sys.stderr)
        return 2
    if args.workers < 1:
        print("--workers must be at least 1", file=sys.stderr)
        return 2

    files = discover_flac_files(input_dir)
    if not files:
        print(f"No FLAC files found in: {input_dir}", file=sys.stderr)
        return 1

    if not args.dry_run:
        try:
            check_dependencies()
        except RuntimeError as error:
            print(error, file=sys.stderr)
            return 2
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(files)} FLAC file(s). Output: {output_dir}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = executor.map(
            lambda filepath: convert_file(filepath, input_dir, output_dir, args.dry_run),
            files,
        )
    failures = sum(not result for result in results)
    print(f"Finished with {failures} failed conversion(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
