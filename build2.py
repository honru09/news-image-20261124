#!/usr/bin/env python3
"""Round-2 entry image for make.fun news-image-20261124.

Draws a fresh 1024x1024 front-page infographic (Pillow) summarising
Tuesday 24 November 2026 world news. Lead: Ukraine sinks the Russian
corvette Merkury in Benghazi, Libya. Layout differs from round 1:
navy masthead, one big lead panel with a drawn sea motif, a 2x3 grid
of story cards, and a dark "also in brief" strip.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 244, 236)
INK = (17, 17, 17)
NAVY = (14, 42, 71)
NAVY_LT = (30, 68, 104)
RED = (178, 34, 34)
GOLD = (232, 184, 75)
GREY = (90, 90, 88)
CARD = (255, 255, 255)
LINE = (205, 200, 188)
SEA = (24, 72, 110)

F = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(F, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(F, "DejaVuSerif.ttf")
SANS_B = os.path.join(F, "DejaVuSans-Bold.ttf")
SANS = os.path.join(F, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, bg, fg=(255, 255, 255)):
    fnt = font(SANS_B, 15)
    w = int(draw.textlength(text, font=fnt)) + 18
    draw.rounded_rectangle([x, y, x + w, y + 26], radius=4, fill=bg)
    draw.text((x + 9, y + 4), text, font=fnt, fill=fg)
    return w


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -----------------------------------------------------
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 152], fill=GOLD)
    title = "THE WORLD IN ONE DAY"
    tf = font(SERIF_B, 58)
    d.text(((W - d.textlength(title, font=tf)) / 2, 22), title,
           font=tf, fill=(255, 255, 255))
    sub = "T U E S D A Y   ·   2 4   N O V E M B E R   2 0 2 6"
    sf = font(SANS_B, 24)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 96), sub,
           font=sf, fill=GOLD)

    # ---- Lead panel ---------------------------------------------------
    lx, ly, lw, lh = 36, 168, 952, 290
    d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=10,
                        fill=CARD, outline=LINE, width=2)
    chip(d, lx + 24, ly + 20, "LEAD  ·  WAR AT SEA", RED)
    d.text((lx + 250, ly + 22), "BENGHAZI, LIBYA — 2,400 KM FROM THE FRONT LINE",
           font=font(SANS_B, 15), fill=GREY)

    head = "Ukraine sinks Russian warship in Libya"
    hf = font(SERIF_B, 40)
    lines = wrap(d, head, hf, 560)
    y = ly + 62
    y = draw_lines(d, lines, lx + 24, y, hf, INK, 48)

    facts = [
        "Seven sea drones, launched from a “mother ship”, sank the corvette Merkury.",
        "A Ka-27 combat helicopter was destroyed; the cargo ship Angara was also hit.",
        "Kyiv calls both vessels legitimate targets.",
    ]
    ff = font(SANS, 18)
    y += 6
    for fact in facts:
        fl = wrap(d, fact, ff, 560)
        for i, ln in enumerate(fl):
            prefix = "•  " if i == 0 else "    "
            d.text((lx + 24, y), prefix + ln, font=ff, fill=(40, 40, 40))
            y += 24

    # Drawn sea motif (right side of lead panel)
    mx0, my0, mx1, my1 = 668, ly + 62, lx + lw - 24, ly + lh - 24
    d.rounded_rectangle([mx0, my0, mx1, my1], radius=8, fill=SEA)
    # waves
    for k, wy in enumerate((my1 - 58, my1 - 34, my1 - 12)):
        for x0 in range(mx0 + 6, mx1 - 10, 34):
            d.arc([x0, wy - 8, x0 + 30, wy + 10], start=200, end=340,
                  fill=(150, 190, 220), width=3)
    # ship hull + superstructure
    d.polygon([(mx0 + 34, my1 - 78), (mx0 + 250, my1 - 78),
               (mx0 + 228, my1 - 52), (mx0 + 58, my1 - 52)],
              fill=(226, 226, 220))
    d.rectangle([mx0 + 96, my1 - 108, mx0 + 176, my1 - 78], fill=(200, 200, 194))
    d.rectangle([mx0 + 128, my1 - 128, mx0 + 140, my1 - 108], fill=(200, 200, 194))
    # explosion starburst above the ship
    cx, cy = mx0 + 215, my1 - 145
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 12, 30
        a = math.radians(ang)
        d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                (cx + r2 * math.cos(a), cy + r2 * math.sin(a))],
               fill=GOLD, width=5)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 120, 40))
    d.text((mx0 + 10, my0 + 8), "THE MERKURY, SUNK",
           font=font(SANS_B, 14), fill=(255, 255, 255))

    # ---- Story grid: 2 cols x 3 rows ---------------------------------
    cards = [
        ("CHINA", RED,
         "Beijing probes a Politburo member",
         "Shanghai party chief Chen Jining under investigation — the fourth top leader probed since 2025."),
        ("UKRAINE", NAVY_LT,
         "Russian strike kills 2, wounds 22 in Zaporizhzhia",
         "Two children among the wounded in the overnight attack, regional officials say."),
        ("MIDDLE EAST", (120, 60, 20),
         "Israel kills senior Hamas security chief in Gaza",
         "Naeem Abu Nahel struck in western Gaza City, Hamas sources say."),
        ("IRAQ", (40, 110, 70),
         "Baghdad seizes Kurdistan border crossings",
         "PM orders a takeover of all crossings after an oil-smuggling probe."),
        ("ASIA", (90, 60, 130),
         "Hanoi blast kills 6, injures 10",
         "Explosion at a food shop in Dong Da shatters windows across the street."),
        ("GULF", (150, 90, 10),
         "Bus–truck crash kills 11 in the UAE",
         "Eleven dead when a passenger bus and a truck collided in Ras Al Khaimah."),
    ]
    gx, gy = 36, 478
    cw, chh, gap = 466, 128, 20
    for i, (tag, colour, head, fact) in enumerate(cards):
        cx0 = gx + (i % 2) * (cw + gap)
        cy0 = gy + (i // 2) * (chh + 12)
        d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + chh], radius=8,
                            fill=CARD, outline=LINE, width=1)
        chip(d, cx0 + 14, cy0 + 12, tag, colour)
        hf2 = font(SANS_B, 19)
        hl = wrap(d, head, hf2, cw - 28)
        y = cy0 + 46
        y = draw_lines(d, hl[:2], cx0 + 14, y, hf2, INK, 22)
        ff2 = font(SANS, 14)
        fl = wrap(d, fact, ff2, cw - 28)
        draw_lines(d, fl[:2], cx0 + 14, y + 2, ff2, (70, 70, 70), 17)

    # ---- Also in brief strip ------------------------------------------
    bx, by, bw, bh = 36, 892, 952, 76
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=NAVY)
    d.text((bx + 18, by + 12), "ALSO IN BRIEF",
           font=font(SANS_B, 15), fill=GOLD)
    briefs = [
        "UK sanctions the Houthis and four senior figures over abuses.",
        "Norway and Ukraine expand cooperation on anti-drone defence.",
        "Moscow accuses Estonia of acts “on the verge of open war”.",
    ]
    bf = font(SANS, 14)
    col_w = (bw - 36) / 3
    for i, b in enumerate(briefs):
        bl = wrap(d, b, bf, col_w - 18)
        draw_lines(d, bl[:3], bx + 18 + i * col_w, by + 34, bf,
                   (235, 235, 235), 17)

    # ---- Footer -------------------------------------------------------
    d.text((36, 984),
           "Sources: Reuters · CNN · AP · Al Jazeera · Dawn — all events reported Tuesday 24 November 2026.",
           font=font(SANS, 13), fill=GREY)
    d.text((36, 1004),
           "One image, one day — the world in a single page.",
           font=font(SANS, 12), fill=GREY)

    img.save(OUT, format="PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} {size} bytes")
    assert size <= 1024 * 1024, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
