#!/usr/bin/env python3
"""Round 3 — fresh 1024x1024 front-page infographic for 24 Nov 2026 world news.

Layout (new for round 3): dark-red serif masthead with gold date ribbon,
full-width horizontal lead banner with a drawn tanker-and-strait motif,
numbered 2x3 story grid, dark 'ALSO TODAY' strip, sources footer.
All stories verified as reported on Tue 24 Nov 2026 (see PROGRESS.md).
Deterministic: no clock, no randomness, fixed fonts.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/home/hatch/workspace/makefun-news-image-20261124/entry.png"

PAPER = (247, 243, 234)
INK = (28, 24, 20)
RED = (122, 26, 20)
GOLD = (212, 175, 105)
NAVY = (24, 42, 66)
SEA = (46, 98, 140)
CREAM = (255, 253, 246)
GREY = (90, 84, 76)
ORANGE = (232, 116, 30)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = ImageFont.truetype(FD + "DejaVuSerif-Bold.ttf", 54)
SERIF_L = ImageFont.truetype(FD + "DejaVuSerif-Bold.ttf", 48)
SANS_B = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 21)
SANS = ImageFont.truetype(FD + "DejaVuSans.ttf", 18)
SANS_S = ImageFont.truetype(FD + "DejaVuSans.ttf", 16)
KICK = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 17)
DATE_F = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 25)
FOOT = ImageFont.truetype(FD + "DejaVuSans.ttf", 15)


def wrap(draw, text, font, width):
    """Greedy word wrap by measured pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- Masthead: dark-red band, serif title, gold date ribbon ----
d.rectangle([0, 0, W, 118], fill=RED)
title = "THE WORLD IN ONE DAY"
tw = d.textlength(title, font=SERIF_B)
d.text(((W - tw) / 2, 16), title, font=SERIF_B, fill=(255, 250, 240))
d.rectangle([36, 84, W - 36, 86], fill=GOLD)
date = "TUESDAY  24  NOVEMBER  2026"
dw = d.textlength(date, font=DATE_F)
d.text(((W - dw) / 2, 92), date, font=DATE_F, fill=GOLD)

# ---- Lead banner ----
LX, LY, LW, LH = 36, 134, 952, 282
d.rectangle([LX, LY, LX + LW, LY + LH], fill=CREAM, outline=INK, width=3)
d.rectangle([LX, LY, LX + LW, LY + 34], fill=INK)
d.text((LX + 16, LY + 6), "LEAD  —  THE STRAIT OF HORMUZ", font=KICK, fill=(255, 250, 240))

# Lead headline, left column
hx, hy = LX + 18, LY + 46
d.text((hx, hy), "MINES IN THE STRAIT", font=SERIF_L, fill=RED)
d.text((hx, hy + 54), "TANKERS ABLAZE", font=SERIF_L, fill=RED)

# Lead facts, under headline (narrow column)
facts = [
    "IRGC: 3 tankers exploded and burned after hitting naval mines; a 4th struck early Tue.",
    "Six tankers hit in total, Iran's army and IRGC say; strait 'closed' until demands met.",
    "US probing Iran over cyberattacks on up to 50 tankers, WSJ reports.",
]
fy = LY + 46 + 132
for f in facts:
    for line in wrap(d, f, SANS_S, 640):
        d.text((hx, fy), line, font=SANS_S, fill=INK)
        fy += 20

# Drawn motif, right side: sea, tanker, explosion starburst, smoke
mx0, my0, mx1, my1 = 700, LY + 44, LX + LW - 16, LY + LH - 34
d.rectangle([mx0, my0, mx1, my1], fill=(214, 232, 240), outline=NAVY, width=2)
# sea band
d.rectangle([mx0, my1 - 52, mx1, my1], fill=SEA)
d.line([mx0, my1 - 52, mx1, my1 - 52], fill=NAVY, width=2)
# tanker hull + bridge + funnel
d.polygon([(mx0 + 18, my1 - 52), (mx0 + 240, my1 - 52), (mx0 + 222, my1 - 22),
           (mx0 + 36, my1 - 22)], fill=(52, 52, 56))
d.rectangle([mx0 + 168, my1 - 84, mx0 + 208, my1 - 52], fill=(52, 52, 56))
d.rectangle([mx0 + 96, my1 - 76, mx0 + 112, my1 - 52], fill=ORANGE)
d.rectangle([mx0 + 18, my1 - 58, mx0 + 240, my1 - 52], fill=RED)
# explosion starburst above bow
cx, cy = mx0 + 205, my0 + 42
for ang in range(0, 360, 30):
    import math
    r1, r2 = 12, 34
    x1 = cx + r1 * math.cos(math.radians(ang))
    y1 = cy + r1 * math.sin(math.radians(ang))
    x2 = cx + r2 * math.cos(math.radians(ang + 15))
    y2 = cy + r2 * math.sin(math.radians(ang + 15))
    d.polygon([(cx, cy), (x1, y1), (x2, y2)], fill=ORANGE)
d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 214, 64))
# smoke puffs
for sx, sy, sr in [(mx0 + 150, my0 + 26, 14), (mx0 + 128, my0 + 14, 11),
                   (mx0 + 172, my0 + 12, 10)]:
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 120, 120))
d.text((mx0 + 8, my1 - 18), "STRAIT OF HORMUZ", font=KICK, fill=(255, 255, 255))

# ---- Story grid: 2 cols x 3 rows, numbered ----
stories = [
    ("RIYADH", "Houthis hit Riyadh's tallest tower again",
     "PIF Tower struck a 2nd time in a week; 11 injured, incl. 2 Indians."),
    ("UKRAINE TALKS", "Lukashenko offers to fly with Zelensky to Moscow",
     "Belarus leader proposes a joint trip for Kremlin peace talks."),
    ("UNITED STATES", "Abrego Garcia to leave US voluntarily",
     "Wrongly deported migrant to fly to Europe on Tuesday."),
    ("ISRAEL", "Eisenkot seals first coalition deal",
     "Ex-army chief pacts with Lieberman to form a government."),
    ("MIGRATION", "175 migrants missing off Senegal",
     "Contact lost with a Europe-bound boat that left Dakar ~Nov 9."),
    ("TRADE", "New US tariffs loom after capacity probe",
     "Section 301 findings on 16 trading partners due Tue / Wed."),
]
GX, GY = 36, 436
CW, CH, GAP = 466, 138, 20
for i, (kick, head, fact) in enumerate(stories):
    x = GX + (i % 2) * (CW + GAP)
    y = GY + (i // 2) * (CH + 14)
    d.rectangle([x, y, x + CW, y + CH], fill=CREAM, outline=INK, width=2)
    # number badge
    d.ellipse([x + 12, y + 12, x + 40, y + 40], fill=RED)
    num = str(i + 1)
    nw = d.textlength(num, font=SANS_B)
    d.text((x + 26 - nw / 2, y + 14), num, font=SANS_B, fill=(255, 250, 240))
    d.text((x + 52, y + 10), kick, font=KICK, fill=RED)
    hyy = y + 36
    for line in wrap(d, head, SANS_B, CW - 24)[:2]:
        d.text((x + 12, hyy), line, font=SANS_B, fill=INK)
        hyy += 25
    for line in wrap(d, fact, SANS, CW - 24)[:2]:
        d.text((x + 12, hyy + 2), line, font=SANS, fill=GREY)
        hyy += 21

# ---- ALSO TODAY strip ----
AY = 890
d.rectangle([36, AY, W - 36, AY + 74], fill=NAVY)
d.text((52, AY + 8), "ALSO TODAY", font=KICK, fill=GOLD)
also = ("EU sanctions Russia's banks, soldiers, athletes  •  UK sanctions Myanmar generals "
        "after ICJ ruling  •  Malaysia to return 6,500+ Rohingya  •  Landmine toll "
        "hits 5-year high of 7,000")
ayy = AY + 30
for line in wrap(d, also, SANS_S, W - 104)[:2]:
    d.text((52, ayy), line, font=SANS_S, fill=(235, 238, 242))
    ayy += 19

# ---- Footer ----
foot = "Sources: Reuters · Al Jazeera · IRNA · AFP · WSJ — All events reported Tuesday 24 November 2026"
fw = d.textlength(foot, font=FOOT)
d.text(((W - fw) / 2, 978), foot, font=FOOT, fill=GREY)

img.save(OUT, optimize=True)
print("saved", OUT)
