#!/usr/bin/env python3
"""Draw the Rails sqlite3 /proc/self/fd/N animations.

The two figures are reconstructions, not captures. They reuse the mono/red
chrome from make-anims.py but live in a separate script so the existing six
GIFs are left byte-for-byte alone.

Outputs:
    07-rails-fd-bypass.gif / .mp4 / -poster.jpg
    08-rails-sqlite3-chain.gif / .mp4 / -poster.jpg

Run: python3 assets/img/anim/make-rails-anims.py
"""

import importlib.util
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("make_anims", HERE / "make-anims.py")
ma = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ma)
ma.OUT = str(HERE)

FPS = 12


def text(d, xy, value, size=16, colour=None, bold=False, max_w=None, anchor=None):
    colour = colour or ma.MID
    font = ma.fit(d, value, None, size, max_w, bold) if max_w else ma.mono(size, bold)
    d.text(xy, value, font=font, fill=colour, anchor=anchor)


def arrow(d, start, end, colour=None, width=3):
    colour = colour or ma.RED
    x1, y1 = start
    x2, y2 = end
    d.line([x1, y1, x2, y2], fill=colour, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    wing = 13
    a = (x2 - wing * math.cos(angle - 0.55), y2 - wing * math.sin(angle - 0.55))
    b = (x2 - wing * math.cos(angle + 0.55), y2 - wing * math.sin(angle + 0.55))
    d.polygon([(x2, y2), a, b], fill=colour)


def label(d, xy, value, colour=None):
    text(d, xy, value, 13, colour or ma.DIM, True)


def rails_fd():
    s = ma.Scene("rails fd bypass", 7)

    def paint(d, stage):
        text(d, (ma.M, 96), "MULTIPART UPLOAD → DESCRIPTOR PATH", 22, ma.INK, True)

        # three stages across the top of the plate
        boxes = {
            "upload": (ma.M, 142, 330, 292),
            "rack": (425, 142, 730, 292),
            "fd": (825, 142, ma.W - ma.M, 292),
        }
        for name, box in boxes.items():
            active = (name == "upload" and stage >= 0) or \
                     (name == "rack" and stage >= 1) or \
                     (name == "fd" and stage >= 2)
            ma.block(d, box, outline=ma.RED if active and name == "fd" else ma.LINE,
                     width=2 if active else 1)
            label(d, (box[0] + 16, box[1] + 12),
                  { "upload": "1  REQUEST", "rack": "2  RACK TMP", "fd": "3  FD TABLE" }[name],
                  ma.RED if active and name == "fd" else ma.DIM)

        if stage >= 0:
            text(d, (ma.M + 16, 186), "payload part", 16, ma.MID)
            text(d, (ma.M + 16, 218), "application/x-sharedlib", 14, ma.DIM,
                 max_w=240)
            text(d, (ma.M + 16, 250), "payload.so", 20, ma.INK, True)

        if stage >= 1:
            text(d, (441, 186), "randomised name", 16, ma.MID)
            text(d, (441, 220), "RackMultipart20250225-1-", 14, ma.DIM,
                 max_w=270)
            text(d, (441, 252), "oji5wc.so", 20, ma.RED, True)
            arrow(d, (332, 228), (423, 228))

        if stage >= 2:
            text(d, (841, 186), "12 → ...sc9f98.txt", 15, ma.DIM)
            text(d, (841, 224), "13 → ...oji5wc.so", 17,
                 ma.RED if stage >= 3 else ma.MID, stage >= 3)
            if stage >= 3:
                d.rectangle([833, 216, 1120, 254], outline=ma.RED, width=2)
            arrow(d, (732, 228), (823, 228))

        # the stable alias: this is the bypass, not a filename guess
        if stage >= 4:
            box = (ma.M, 350, ma.W - ma.M, 462)
            ma.block(d, box, outline=ma.RED if stage >= 5 else ma.LINE,
                     width=2 if stage >= 5 else 1)
            label(d, (ma.M + 18, 364), "STABLE ALIAS", ma.RED if stage >= 5 else ma.DIM)
            text(d, (ma.M + 18, 398), "/proc/self/fd/13", 30, ma.INK, True)
            text(d, (ma.W - ma.M - 18, 402), "same open file · no suffix", 16, ma.DIM,
                 anchor="ra", max_w=520)
            arrow(d, (975, 256), (975, 348))

        if stage >= 6:
            d.line([ma.M, 500, ma.W - ma.M, 500], fill=ma.LINE)
            text(d, (ma.M, 522), "Rack randomises the filename; the descriptor path does not use the filename.",
                 21, ma.INK, True, max_w=1070)
            text(d, (ma.M, 562), "fd 13 was observed in the reflection run. The number is enumerated, never assumed.",
                 15, ma.DIM, max_w=1070)

    seq = [0, 1, 2, 3, 4, 5, 6, 6]
    for i, stage in enumerate(seq):
        ms = 900 if i == len(seq) - 1 else 340
        s.frame(lambda d, stage=stage: paint(d, stage), ms)
        s.durations.append(ms)

    return s


def rails_chain():
    s = ma.Scene("rails sqlite3 chain", 8)

    def paint(d, stage):
        text(d, (ma.M, 96), "TWO ENTRY POINTS · ONE NATIVE EXTENSION GADGET",
             22, ma.INK, True)

        left = (ma.M, 142, 405, 344)
        mid = (455, 196, 745, 344)
        right = (795, 142, ma.W - ma.M, 344)
        for box, active in ((left, stage >= 1), (mid, stage >= 4), (right, stage >= 2)):
            ma.block(d, box, outline=ma.RED if active and box is mid else ma.LINE,
                     width=2 if active else 1)

        label(d, (ma.M + 16, 156), "A  UNSAFE REFLECTION", ma.RED if stage >= 1 else ma.DIM)
        if stage >= 1:
            text(d, (ma.M + 16, 192), 'type: "SQLite3::Database"', 15, ma.MID, max_w=310)
            text(d, (ma.M + 16, 224), "constantize / const_get", 15, ma.DIM)
            text(d, (ma.M + 16, 264), "extensions:", 17, ma.INK, True)
            text(d, (ma.M + 16, 296), '["/proc/self/fd/13"]', 17, ma.RED, True)

        label(d, (811, 156), "B  MARSHAL.LOAD", ma.RED if stage >= 2 else ma.DIM)
        if stage >= 2:
            text(d, (811, 190), "DeprecatedInstanceVariableProxy", 13, ma.MID, max_w=310)
            text(d, (811, 222), "→ SQLite3Adapter#connect!", 14, ma.MID, max_w=310)
            text(d, (811, 258), "→ new_client", 14, ma.DIM)
            text(d, (811, 296), "fd 12 in the Marshal run", 15, ma.RED, True,
                 max_w=310)

        if stage >= 3:
            arrow(d, (405, 260), (453, 260))
            arrow(d, (795, 260), (747, 260))

        if stage >= 4:
            label(d, (471, 210), "CONVERGENCE", ma.RED)
            text(d, (471, 244), "SQLite3::Database.new", 18, ma.INK, True, max_w=250)
            text(d, (471, 282), "extensions: [fd]", 15, ma.RED, max_w=250)

        if stage >= 5:
            arrow(d, (600, 346), (600, 386))
            box = (315, 390, 885, 500)
            ma.block(d, box, outline=ma.RED, width=2)
            label(d, (333, 404), "SQLITE3 EXTENSION INIT", ma.RED)
            text(d, (333, 438), "touch /tmp/rce-conf.txt", 23, ma.INK, True,
                 max_w=520)
            text(d, (333, 474), "native code runs with the Rails process's privileges",
                 14, ma.DIM, max_w=520)

        if stage >= 6:
            d.line([ma.M, 540, ma.W - ma.M, 540], fill=ma.LINE)
            text(d, (ma.M, 560), "PRECONDITION: attacker-controlled class selection or Marshal.load.",
                 20, ma.INK, True, max_w=1070)
            text(d, (ma.M, 598), "This is a gadget for that pattern — not a Rails, Rack, or sqlite3 vulnerability.",
                 15, ma.RED, max_w=1070)

    seq = [0, 1, 2, 3, 4, 5, 6, 6]
    for i, stage in enumerate(seq):
        ms = 1100 if i == len(seq) - 1 else 360
        s.frame(lambda d, stage=stage: paint(d, stage), ms)
        s.durations.append(ms)

    return s


def write_video(scene, name, poster):
    frames = []
    for im, ms in zip(scene.frames, scene.durations):
        frames.extend([im] * max(1, round(ms * FPS / 1000)))

    out = HERE / name
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ma.W}x{ma.H}",
        "-r", str(FPS), "-i", "-", "-an",
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0",
        "-c:v", "libx264",
        "-preset", "medium", "-crf", "27", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for im in frames:
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace")
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {name}: {err}")

    scene.frames[-1].save(HERE / poster, quality=90, optimize=True)
    print(f"{name}: {len(frames)} frames, {out.stat().st_size / 1024:.0f} KB")
    print(f"{poster}: {(HERE / poster).stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    fd = rails_fd()
    fd.save("07-rails-fd-bypass.gif")
    write_video(fd, "07-rails-fd-bypass.mp4", "07-rails-fd-bypass-poster.jpg")

    chain = rails_chain()
    chain.save("08-rails-sqlite3-chain.gif")
    write_video(chain, "08-rails-sqlite3-chain.mp4", "08-rails-sqlite3-chain-poster.jpg")
