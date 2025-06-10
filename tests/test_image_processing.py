from PIL import Image, ImageChops

from app.utils.image_processing import correct_inversion


def test_correct_inversion_round_trip() -> None:
    base = Image.new("RGB", (10, 10), color="white")
    corrected, inverted = correct_inversion(base)
    assert not inverted
    assert ImageChops.difference(base, corrected).getbbox() is None


def test_detects_and_corrects_inversion() -> None:
    base = Image.new("RGB", (10, 10), color="white")
    mirrored = base.transpose(Image.FLIP_LEFT_RIGHT)
    exif = mirrored.getexif()
    exif[274] = 2
    mirrored.info["exif"] = exif.tobytes()

    corrected, inverted = correct_inversion(mirrored)
    assert inverted
    assert ImageChops.difference(base, corrected).getbbox() is None
