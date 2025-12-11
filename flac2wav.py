#!/usr/bin/env python3
import os
import sys
import subprocess
import concurrent.futures
from pathlib import Path

def check_ffmpeg():
    """Проверяем наличие ffmpeg и ffprobe"""
    for cmd in ("ffmpeg", "ffprobe"):
        if subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            sys.exit(f"❌ {cmd} не найден. Установи его (macOS: brew install ffmpeg; Ubuntu: sudo apt install ffmpeg)")

def get_bit_depth(filepath: Path) -> str:
    """Определяем битность аудиопотока"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=bits_per_raw_sample",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True
        )
        bit = result.stdout.strip()
        return bit if bit else "24"
    except Exception:
        return "24"

def extract_metadata(filepath: Path) -> list:
    """Извлекаем метаданные и превращаем в список аргументов -metadata"""
    args = []
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format_tags",
             "-of", "default=noprint_wrappers=1", str(filepath)],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.strip().split("=", 1)
                if key and value:
                    args += ["-metadata", f"{key}={value}"]
    except Exception:
        pass
    return args

def extract_cover(filepath: Path, outdir: Path):
    """Извлекаем встроенную обложку, если есть"""
    out_cover = outdir / (filepath.stem + ".jpg")
    try:
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(filepath),
             "-an", "-vcodec", "copy", str(out_cover)],
            capture_output=True
        )
        if out_cover.exists() and out_cover.stat().st_size > 0:
            print(f"🖼️  Обложка: {out_cover.name}")
        else:
            out_cover.unlink(missing_ok=True)
    except Exception:
        pass

def convert_file(fpath: Path, outdir: Path):
    """Основная функция конвертации"""
    bit_depth = get_bit_depth(fpath)
    codec = {
        "16": "pcm_s16le",
        "24": "pcm_s24le",
        "32": "pcm_s32le"
    }.get(bit_depth, "pcm_s24le")

    meta_args = extract_metadata(fpath)
    outpath = outdir / (fpath.stem + ".wav")

    # Конвертация в WAV
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(fpath), "-c:a", codec, *meta_args, str(outpath)]
    try:
        subprocess.run(cmd, check=True)
        extract_cover(fpath, outdir)
        print(f"✅ {outpath.name} ({codec})")
    except subprocess.CalledProcessError:
        print(f"❌ Ошибка конвертации: {fpath}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        sys.exit("Использование: python3 flac_to_wav.py <папка-с-FLAC>")

    input_dir = Path(sys.argv[1]).resolve()
    if not input_dir.is_dir():
        sys.exit(f"❌ Нет такой папки: {input_dir}")

    check_ffmpeg()

    files = list(input_dir.rglob("*.flac"))
    if not files:
        sys.exit("❌ В папке нет .flac файлов.")

    output_dir = Path(str(input_dir) + ".wav")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"▶️ Найдено FLAC: {len(files)}. Конвертирую в {output_dir}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
        for f in files:
            ex.submit(convert_file, f, output_dir)

    print("🎉 Готово. Все файлы и обложки обработаны без потерь.")

if __name__ == "__main__":
    main()
