# 🎵 FLAC → WAV Converter
High-performance batch audio converter from **FLAC** to **WAV** with metadata and cover preservation.  
Built in **Python**, powered by **FFmpeg**, supports **multithreaded** processing.

## ✨ Features

- 🔍 Automatic bit-depth detection via `ffprobe`
- 🎧 Correct PCM codec selection (`pcm_s16le`, `pcm_s24le`, `pcm_s32le`)
- 📝 Metadata preservation — all FLAC tags copied into the WAV file
- 🖼 Embedded cover extraction (saved as .jpg)
- 🚀 Multithreaded batch processing using `ThreadPoolExecutor`
- 📁 Recursive scanning for .flac files
- 💾 Auto-generated output folder (`<your_folder>.wav/`)
- 🛡 Error handling for corrupted files, missing ffmpeg, metadata issues
- 🖥 Cross‑platform: macOS, Linux, Windows

## 📦 Requirements

- Python 3.8+
- FFmpeg & FFprobe installed  
  macOS: `brew install ffmpeg`  
  Ubuntu: `sudo apt install ffmpeg`  
  Windows: https://ffmpeg.org/download.html

## 🛠 Installation

```
git clone https://github.com/yourname/flac2wav
cd flac2wav
```

Optional:

```
chmod +x flac2wav.py
```

## ▶️ Usage

```
python3 flac2wav.py <folder_with_flac_files>
```

Example:

```
python3 flac2wav.py ~/Music/FLAC_Collection
```

Output folder will be:

```
~/Music/FLAC_Collection.wav/
```

Containing both `.wav` files and extracted `.jpg` covers.

## 📁 Output Example

```
MyAlbum/
├── track1.flac
├── track2.flac
└── cover.jpg

MyAlbum.wav/
├── track1.wav
├── track1.jpg
├── track2.wav
└── track2.jpg
```

## ⚙️ Code Overview

- `check_ffmpeg()` — validates ffmpeg presence
- `get_bit_depth()` — determines audio bit depth
- `extract_metadata()` — collects metadata tags
- `extract_cover()` — extracts and writes album art
- `convert_file()` — executes full FLAC → WAV pipeline
- `ThreadPoolExecutor` — parallel batch conversion

## 🧪 Example Output

```
▶️ Found FLAC: 42. Converting into /Users/me/Music/Collection.wav
🖼️  Cover: track1.jpg
✅ track1.wav (pcm_s24le)
🖼️  Cover: track2.jpg
✅ track2.wav (pcm_s24le)
🎉 Done. All files and covers processed successfully.
```

## 📄 License
MIT

## 🙌 Author
GitHub: @tghnx1
