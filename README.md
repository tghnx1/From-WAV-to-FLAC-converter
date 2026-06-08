# FLAC to WAV Converter

A small Python command-line utility for recursively converting FLAC audio files to WAV with FFmpeg.

The code converts **FLAC to WAV**. The current GitHub repository name is inconsistent with that direction and should be renamed in the GitHub UI.

## Features

- Recursive FLAC file discovery
- Parallel conversion with a configurable worker count
- WAV codec selection based on detected source bit depth
- Metadata forwarding through FFmpeg arguments
- Best-effort extraction of embedded artwork
- Preserved input subdirectory structure
- Dry-run mode for validating planned output
- Non-zero exit status when conversion fails

## Requirements

- Python 3.9+
- FFmpeg
- FFprobe

Install FFmpeg on macOS:

```bash
brew install ffmpeg
```

Install FFmpeg on Debian/Ubuntu:

```bash
sudo apt install ffmpeg
```

Verify the tools:

```bash
ffmpeg -version
ffprobe -version
```

## Installation

```bash
git clone https://github.com/tghnx1/From-WAV-to-FLAC-converter.git
cd From-WAV-to-FLAC-converter
```

No Python package dependencies are required for normal use.

## Usage

Convert a directory:

```bash
python3 flac2wav.py ~/Music/FLAC
```

Choose an output directory:

```bash
python3 flac2wav.py ~/Music/FLAC --output-dir ~/Music/WAV
```

Limit parallel work:

```bash
python3 flac2wav.py ~/Music/FLAC --workers 4
```

Preview conversions without running FFmpeg:

```bash
python3 flac2wav.py ~/Music/FLAC --dry-run
```

By default, output is written to `<input-directory>.wav`.

## Input and output

```text
FLAC/
  Album A/
    track01.flac
    track02.flac

FLAC.wav/
  Album A/
    track01.wav
    track01.jpg
    track02.wav
```

Artwork files are created only when FFmpeg can extract an embedded image.

## Error handling

- Missing input directories and invalid worker counts return exit code `2`.
- Missing FFmpeg or FFprobe returns exit code `2`.
- A directory containing no FLAC files returns exit code `1`.
- Failed individual conversions are reported and produce a final non-zero exit status.

## Tests

Pure helper functions are covered with pytest:

```bash
python3 -m pip install pytest
pytest -q
```

For an end-to-end validation, run the tool against a small test directory and inspect the result with `ffprobe`:

```bash
python3 flac2wav.py ./sample-flac --output-dir ./sample-wav
ffprobe ./sample-wav/example.wav
```

## Limitations

- Metadata support in WAV players varies.
- Embedded artwork extraction is best effort.
- Existing output files are overwritten.
- Audio conversion behavior depends on the installed FFmpeg version.

## Status

Small utility project. The CLI and helper tests provide a clean base for further validation without turning it into a larger application.
