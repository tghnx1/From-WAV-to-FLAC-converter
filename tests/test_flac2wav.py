from pathlib import Path

from flac2wav import choose_codec, discover_flac_files, output_path_for


def test_choose_codec_uses_supported_bit_depths():
    assert choose_codec("16") == "pcm_s16le"
    assert choose_codec("24") == "pcm_s24le"
    assert choose_codec("32") == "pcm_s32le"


def test_choose_codec_defaults_to_24_bit():
    assert choose_codec("") == "pcm_s24le"
    assert choose_codec("20") == "pcm_s24le"


def test_discover_flac_files_is_recursive_and_case_insensitive(tmp_path):
    nested = tmp_path / "album"
    nested.mkdir()
    first = tmp_path / "one.flac"
    second = nested / "two.FLAC"
    ignored = nested / "notes.txt"
    first.touch()
    second.touch()
    ignored.touch()

    assert discover_flac_files(tmp_path) == sorted([first, second])


def test_output_path_preserves_relative_structure():
    input_dir = Path("/music/flac")
    output_dir = Path("/music/wav")
    source = input_dir / "album" / "track.flac"

    assert output_path_for(source, input_dir, output_dir) == (
        output_dir / "album" / "track.wav"
    )
