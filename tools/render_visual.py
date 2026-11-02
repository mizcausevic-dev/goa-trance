"""Procedural raster artwork and ffmpeg media steps.

The painter draws a 7-step cycle. Lime bars are the sounding steps. The
saffron bar is the step that resets the group. It is an illustration, not a
photograph of a session or of performers.

DejaVu Sans Bold is used only to rasterize the disclosure into the film and the
poster. The font file is not shipped.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from tools.statements import ON_PICTURE

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _clamp(value: int) -> int:
    return 0 if value < 0 else 255 if value > 255 else value


def paint(width: int, height: int, framing: str) -> bytes:
    groups = 5 if framing == "wide" else 4
    levels = (0.42, 0.58, 0.74, 0.86, 0.66, 0.5, 0.28)
    margin_x = int(width * (0.06 if framing == "wide" else 0.09))
    floor = int(height * (0.8 if framing == "square" else 0.76))
    top = int(height * (0.18 if framing == "square" else 0.24))
    span = max(1, width - margin_x * 2)
    count = groups * len(levels)
    gap = span / count
    pixels = bytearray(width * height * 3)
    for y in range(height):
        shade = y / max(1, height - 1)
        row = y * width * 3
        red = 7 + int(12 * shade)
        green = 20 + int(22 * shade)
        blue = 16 + int(10 * shade)
        for x in range(width):
            pixels[row + x * 3] = red
            pixels[row + x * 3 + 1] = green
            pixels[row + x * 3 + 2] = blue
    for index in range(count):
        level = levels[index % len(levels)]
        reset = index % len(levels) == len(levels) - 1
        x0 = int(margin_x + index * gap + gap * 0.22)
        x1 = int(margin_x + index * gap + gap * 0.78)
        y0 = int(floor - level * (floor - top))
        for y in range(y0, floor):
            mix = (y - y0) / max(1, floor - y0)
            if reset:
                red, green, blue = 255, 106 + int(20 * mix), 26
            else:
                red = int(170 + 40 * (1 - mix))
                green = int(255 - 30 * mix)
                blue = int(40 + 20 * mix)
            row = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                pixels[row + x * 3] = red
                pixels[row + x * 3 + 1] = green
                pixels[row + x * 3 + 2] = blue
    return bytes(pixels)

def write_ppm(path: Path, width: int, height: int, rgb: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            + " ".join(command)
            + "\n"
            + completed.stderr[-2000:]
        )


def ppm_to_jpeg(ppm: Path, jpeg: Path, quality: int = 3) -> None:
    jpeg.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(ppm), "-frames:v", "1", "-q:v", str(quality), str(jpeg)])


def draw_disclosure(source: Path, dest: Path, textfile: Path) -> list[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf",
        (
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-frames:v", "1",
        "-q:v", "3",
        str(dest),
    ]
    run(command)
    return command


def encode_mp3(wav: Path, mp3: Path) -> list[str]:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3),
    ]
    run(command)
    return command


def encode_film(plate: Path, mp3: Path, mp4: Path, textfile: Path, duration: str) -> list[str]:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(plate),
        "-i", str(mp3),
        "-t", duration,
        "-vf",
        (
            "scale=1280:720,"
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4),
    ]
    run(command)
    return command


def derive_social(hero: Path, square: Path, portrait: Path, card: Path) -> dict[str, list[str]]:
    portrait.parent.mkdir(parents=True, exist_ok=True)
    card.parent.mkdir(parents=True, exist_ok=True)
    portrait_cmd = [
        "ffmpeg", "-y", "-i", str(square),
        "-vf", "crop=864:1080:108:0,scale=1080:1350",
        "-q:v", "3",
        str(portrait),
    ]
    card_cmd = [
        "ffmpeg", "-y", "-i", str(hero),
        "-vf", "scale=1600:900",
        "-q:v", "3",
        str(card),
    ]
    run(portrait_cmd)
    run(card_cmd)
    return {"portrait": portrait_cmd, "card": card_cmd}
