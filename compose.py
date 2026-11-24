#!/usr/bin/env python3
"""Compose the front page for THE WORLD TODAY - Tuesday 24 November 2026.

Builds entry.png (1024x1024) with PIL: a newspaper front page summing up
the day's world news. All artwork is drawn in code (gradients, silhouettes,
glow layers) and all text is set with real fonts, so nothing is garbled.

Stories (all verified against reputable reporting on 23-24 Nov 2026):
  LEAD  Iran vows to use "every means" against the US naval blockade of
        its ports at the Strait of Hormuz; Trump threatens to sink ships
        that defy it (Reuters, 23 Nov)
  2     Nvidia board reinstates Jensen Huang as CEO after Trump lobbied
        the board by phone; shares soar 33% (Reuters, 23 Nov)
  3     Zelensky confirms Ukraine sank the Russian corvette Merkury off
        Libya with seven sea drones; MV Angara hit, Ka-27 destroyed
        (AP/Reuters, 23 Nov)
  4     COP31 collapses with no deal - longest COP ever, first no-deal
        COP since 2009 (Reuters/BBC, 22 Nov)
  5     12,000 evacuated from Don Toliver concert at Manchester's Co-op
        Live after an unknown substance is released; 80+ checked, one
        in hospital (Reuters/BBC, 23 Nov)
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (246, 241, 231)
INK = (17, 17, 17)
RED = (168, 30, 30)
NAVY = (20, 33, 61)
GREY = (90, 86, 78)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = FONT_DIR + "NotoSerifDisplay-Black.ttf"
SERIF_BOLD = FONT_DIR + "NotoSerif-Bold.ttf"
SERIF = FONT_DIR + "NotoSerif-Regular.ttf"
SERIF_IT = FONT_DIR + "NotoSerif-Italic.ttf"
SANS_BLACK = FONT_DIR + "NotoSansDisplay-Black.ttf"
SANS_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
SANS = FONT_DIR + "NotoSans-Regular.ttf"

random.seed(20261124)


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    """Vertical gradient inside box."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / span))


def fit(draw, text, path, size, max_w, min_size=10):
    """Largest font size <= size whose rendered width fits max_w."""
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap(draw, text, f, max_w):
    """Greedy word wrap into lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def glow_dot(layer, xy, radius, colour):
    """Soft radial glow: concentric circles with falling alpha."""
    d = ImageDraw.Draw(layer)
    steps = 14
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(colour[3] * (1 - i / steps) ** 2)
        d.ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r],
                  fill=(colour[0], colour[1], colour[2], a))


def grain(img, amount=1200, alpha=9):
    """Fine grain so the picture never reads as flat vector art."""
    iw, ih = img.size
    g = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for _ in range(amount):
        x = random.randint(0, iw - 1)
        y = random.randint(0, ih - 1)
        v = random.randint(0, 255)
        gd.point((x, y), fill=(v, v, v, alpha))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")


# ---------------------------------------------------------------- lead scene
def lead_scene():
    """The Strait of Hormuz at dusk: a tanker hemmed in by grey warships,
    a red blockade line, searchlights and a low burning sun."""
    iw, ih = CW, 340
    img = Image.new("RGB", (iw, ih), (20, 26, 52))
    d = ImageDraw.Draw(img)
    horizon = int(ih * 0.58)

    # Sky: deep indigo dusk down to a smouldering orange horizon band.
    vgrad(d, (0, 0, iw, horizon), (14, 18, 44), (206, 88, 46))
    # Sea: dark steel blue fading to near-black at the bottom.
    vgrad(d, (0, horizon, iw, ih), (46, 66, 106), (7, 11, 26))

    # Low sun, half-sunk on the horizon, wide warm halo, kept left of centre
    # so it never collides with the warship superstructures.
    glow = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    glow_dot(glow, (250, horizon - 26), 120, (255, 190, 110, 90))
    glow_dot(glow, (250, horizon - 26), 55, (255, 220, 160, 140))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)
    d.ellipse([250 - 30, horizon - 56, 250 + 30, horizon + 4],
              fill=(255, 236, 190, 255))

    # Cloud bands: long soft ellipses, dark above, lit orange below.
    clouds = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for cx, cy, rx, ry, alpha in [
        (120, 44, 160, 15, 70), (420, 30, 190, 12, 60), (760, 60, 180, 14, 75),
        (300, 90, 150, 11, 55), (640, 112, 160, 11, 50), (890, 26, 130, 11, 60),
        (520, 150, 150, 10, 45), (80, 140, 120, 10, 45),
    ]:
        cd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                   fill=(36, 28, 56, alpha))
        cd.ellipse([cx - rx, cy + ry - 6, cx + rx, cy + ry + 6],
                   fill=(238, 140, 80, 40))
    clouds = clouds.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, clouds)
    d = ImageDraw.Draw(img)

    # Rocky headlands on both banks of the strait, framing the channel.
    d.polygon([(0, horizon), (0, horizon - 96), (70, horizon - 132),
               (150, horizon - 88), (210, horizon - 60), (210, horizon)],
              fill=(12, 15, 32))
    d.polygon([(iw, horizon), (iw, horizon - 110), (880, horizon - 140),
               (800, horizon - 92), (760, horizon - 58), (760, horizon)],
              fill=(12, 15, 32))

    # Sea: soft horizontal reflections of the sunset (never vertical).
    streaks = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streaks)
    for _ in range(90):
        y = random.randint(horizon + 6, ih - 8)
        x = random.randint(0, iw - 120)
        ln = random.randint(30, 150)
        warm = random.random() < 0.65
        col = (238, 140, 80) if warm else (150, 180, 220)
        sd.line([(x, y), (x + ln, y)], fill=col + (random.randint(18, 70),),
                width=random.choice([1, 2, 3]))
    streaks = streaks.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img, streaks)
    d = ImageDraw.Draw(img)

    # The tanker: long dark hull mid-channel, deck houses and funnel,
    # a row of warm portholes along the waterline.
    hull = (6, 9, 20)
    d.polygon([(330, ih - 66), (330, ih - 38), (640, ih - 38),
               (668, ih - 50), (640, ih - 66)], fill=hull)
    d.rectangle([420, ih - 92, 470, ih - 66], fill=hull)
    d.rectangle([560, ih - 96, 606, ih - 66], fill=hull)
    d.rectangle([446, ih - 108, 454, ih - 92], fill=hull)
    for x in range(350, 630, 26):
        d.rectangle([x, ih - 56, x + 5, ih - 51], fill=(255, 196, 110, 255))

    # Grey warship on the right, bow toward the tanker, mast and radar
    # dome, a searchlight beam sweeping across the water.
    war = (52, 58, 70)
    d.polygon([(700, ih - 60), (700, ih - 40), (900, ih - 40),
               (924, ih - 50), (900, ih - 60)], fill=war)
    d.rectangle([780, ih - 88, 830, ih - 60], fill=war)
    d.rectangle([806, ih - 112, 812, ih - 88], fill=war)
    d.ellipse([798, ih - 122, 820, ih - 100], fill=war)
    beam = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(810, ih - 100), (640, ih - 52), (640, ih - 30),
                (810, ih - 96)], fill=(255, 240, 200, 46))
    img = Image.alpha_composite(img, beam.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(img)
    glow2 = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    glow_dot(glow2, (810, ih - 100), 16, (255, 240, 200, 180))
    img = Image.alpha_composite(img, glow2)
    d = ImageDraw.Draw(img)
    # Second, smaller patrol boat on the left edge.
    d.polygon([(60, ih - 52), (60, ih - 36), (180, ih - 36),
               (196, ih - 44), (180, ih - 52)], fill=(40, 45, 58))
    d.rectangle([110, ih - 70, 140, ih - 52], fill=(40, 45, 58))

    # The blockade line: a dashed red cordon across the channel, with
    # small warning buoys, drawn high enough to clear the ships.
    by = horizon + 26
    for x in range(230, 760, 34):
        d.line([(x, by), (x + 20, by)], fill=(220, 60, 50), width=4)
    for x in (300, 470, 640):
        d.polygon([(x, by - 10), (x + 7, by + 2), (x - 7, by + 2)],
                  fill=(230, 80, 60))
        d.ellipse([x - 4, by + 2, x + 4, by + 10], fill=(230, 80, 60))

    return grain(img)


# ------------------------------------------------------------- mini thumbnails
def thumb_nvidia():
    """Green circuit board with a chip and a steep rising arrow: +33%."""
    iw, ih = 150, 100
    img = Image.new("RGB", (iw, ih), (10, 40, 22))
    d = ImageDraw.Draw(img)
    vgrad(d, (0, 0, iw, ih), (14, 66, 36), (7, 26, 15))
    # Circuit traces.
    for x0, y0, x1, y1 in [(10, 20, 44, 20), (10, 80, 30, 80), (120, 14, 140, 14),
                           (118, 86, 140, 86), (44, 20, 44, 34), (30, 80, 30, 62)]:
        d.line([(x0, y0), (x1, y1)], fill=(46, 160, 90), width=2)
    for cx, cy in [(10, 20), (10, 80), (140, 14), (140, 86)]:
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(90, 220, 140))
    # The chip, centre-left.
    d.rectangle([52, 30, 92, 70], fill=(18, 90, 48), outline=(120, 240, 160), width=2)
    d.rectangle([62, 40, 82, 60], fill=(10, 50, 26))
    for x in (58, 67, 76, 85):
        d.line([(x, 30), (x, 22)], fill=(120, 240, 160), width=2)
        d.line([(x, 70), (x, 78)], fill=(120, 240, 160), width=2)
    # Rising arrow, bottom-left to top-right, over the chip's right side.
    d.line([(96, 82), (118, 52), (132, 60), (146, 30)], fill=(255, 210, 80), width=4)
    d.polygon([(146, 30), (134, 30), (146, 42)], fill=(255, 210, 80))
    return img


def thumb_merkury():
    """A listing, half-sunk corvette off Libya: fire, smoke, sea drones."""
    iw, ih = 150, 100
    img = Image.new("RGB", (iw, ih), (16, 22, 40))
    d = ImageDraw.Draw(img)
    vgrad(d, (0, 0, iw, ih), (30, 34, 58), (10, 14, 28))
    d.ellipse([96, 6, 126, 36], fill=(220, 200, 160))
    smoke = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for cx, cy, r in [(58, 34, 14), (70, 24, 17), (84, 16, 13)]:
        sd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 110, 105, 120))
    img = Image.alpha_composite(img.convert("RGBA"),
                                smoke.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(img)
    # Listing hull, bow down.
    d.polygon([(18, 74), (30, 52), (118, 66), (128, 84), (60, 84)],
              fill=(8, 10, 18))
    d.rectangle([66, 44, 74, 56], fill=(8, 10, 18))
    glow = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    glow_dot(glow, (52, 60), 22, (255, 150, 60, 190))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    d.polygon([(44, 64), (52, 50), (60, 64)], fill=(255, 220, 140))
    # A small sea drone skimming the water, bottom right.
    d.ellipse([112, 88, 138, 94], fill=(30, 34, 44))
    d.line([(112, 91), (104, 88)], fill=(200, 200, 210), width=2)
    for y in range(86, 100, 3):
        d.line([(30, y), (110, y)], fill=(90, 120, 170, 255), width=1)
    return img.convert("RGB")


def thumb_cop31():
    """A globe crossed out in red: the talks that ended with no deal."""
    iw, ih = 150, 100
    img = Image.new("RGB", (iw, ih), (18, 60, 52))
    d = ImageDraw.Draw(img)
    vgrad(d, (0, 0, iw, ih), (24, 88, 74), (10, 34, 30))
    d.ellipse([25, 8, 125, 108], fill=(38, 110, 180))
    d.ellipse([38, 24, 66, 50], fill=(70, 150, 80))
    d.ellipse([76, 58, 106, 86], fill=(70, 150, 80))
    d.ellipse([54, 72, 76, 92], fill=(70, 150, 80))
    d.arc([25, 8, 125, 108], 20, 200, fill=(246, 241, 231), width=3)
    d.line([(22, 96), (128, 16)], fill=(200, 40, 40), width=7)
    d.line([(22, 96), (128, 16)], fill=(255, 90, 80), width=3)
    return img


def thumb_manchester():
    """A concert arena at night: stage, light beams, and a crowd filing out."""
    iw, ih = 150, 100
    img = Image.new("RGB", (iw, ih), (14, 12, 26))
    d = ImageDraw.Draw(img)
    vgrad(d, (0, 0, iw, ih), (26, 20, 48), (10, 8, 20))
    # Arena roof arc.
    d.pieslice([10, -70, 140, 40], 0, 180, fill=(40, 36, 66))
    d.arc([10, -70, 140, 40], 0, 180, fill=(120, 110, 160), width=2)
    # Stage at the back, lit.
    d.rectangle([58, 46, 92, 66], fill=(220, 200, 120))
    d.rectangle([62, 50, 88, 62], fill=(30, 24, 50))
    # Light beams fanning out from the stage.
    beams = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    for x2, a in [(20, 60), (48, 80), (102, 80), (130, 60)]:
        bd.polygon([(75, 50), (x2, 96), (x2 + 8, 96)], fill=(255, 230, 150, a))
    img = Image.alpha_composite(img.convert("RGBA"),
                                beams.filter(ImageFilter.GaussianBlur(1)))
    d = ImageDraw.Draw(img)
    # The crowd: rows of small heads, with a gap where the exit stream is.
    for row, y in enumerate((72, 80, 88, 95)):
        for x in range(8, 144, 11):
            if row >= 2 and 60 < x < 96:
                continue
            d.ellipse([x, y, x + 6, y + 6], fill=(200, 190, 170))
    # Exit stream: a column of dots heading down the middle gap.
    for y in range(72, 100, 6):
        d.ellipse([72, y, 78, y + 5], fill=(255, 210, 90))
    return img.convert("RGB")


# ------------------------------------------------------------------- the page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    d.line([(MARGIN, 30), (W - MARGIN, 30)], fill=INK, width=2)
    f_title = fit(d, "THE WORLD TODAY", SERIF_BLACK, 96, CW)
    d.text(((W - d.textlength("THE WORLD TODAY", font=f_title)) / 2, 34),
           "THE WORLD TODAY", font=f_title, fill=INK)

    # Dateline bar.
    d.line([(MARGIN, 146), (W - MARGIN, 146)], fill=INK, width=3)
    f_date = fit(d, "TUESDAY, 24 NOVEMBER 2026", SANS_BOLD, 28, CW - 240)
    date_w = d.textlength("TUESDAY, 24 NOVEMBER 2026", font=f_date)
    d.text(((W - date_w) / 2, 152), "TUESDAY, 24 NOVEMBER 2026",
           font=f_date, fill=INK)
    f_side = font(SANS, 19)
    d.text((MARGIN, 156), "WORLD NEWS", font=f_side, fill=GREY)
    side_r = "No. 328"
    d.text((W - MARGIN - d.textlength(side_r, font=f_side), 156),
           side_r, font=f_side, fill=GREY)
    d.line([(MARGIN, 190), (W - MARGIN, 190)], fill=INK, width=2)

    # Lead scene.
    scene = lead_scene()
    img.paste(scene, (MARGIN, 196))
    d = ImageDraw.Draw(img)
    d.rectangle([MARGIN, 196, W - MARGIN, 196 + 340], outline=INK, width=2)
    # Caption inside the scene's bottom edge.
    cap = Image.new("RGBA", (CW, 30), (10, 10, 12, 190))
    img.paste(Image.alpha_composite(img.crop((MARGIN, 196 + 340 - 30,
                                              W - MARGIN, 196 + 340)).convert("RGBA"),
                                    cap), (MARGIN, 196 + 340 - 30))
    d = ImageDraw.Draw(img)
    f_cap = font(SANS, 17)
    d.text((MARGIN + 10, 196 + 340 - 25),
           "THE STRAIT OF HORMUZ: TANKERS AND WARSHIPS AS THE BLOCKADE TIGHTENS",
           font=f_cap, fill=(246, 241, 231))

    # Lead headline + deck.
    y = 548
    f_head = fit(d, "IRAN VOWS \u2018EVERY MEANS\u2019", SANS_BLACK, 62, CW)
    d.text((MARGIN, y), "IRAN VOWS \u2018EVERY MEANS\u2019", font=f_head, fill=INK)
    y += 66
    d.text((MARGIN, y), "AGAINST U.S. BLOCKADE", font=f_head, fill=RED)
    y += 70
    f_deck = font(SERIF_IT, 27)
    deck = ("Tehran swears to break the Hormuz shipping blockade as Trump "
            "threatens to sink vessels that defy it.")
    for line in wrap(d, deck, f_deck, CW):
        d.text((MARGIN, y), line, font=f_deck, fill=INK)
        y += 32

    # Secondary stories, 2 x 2 grid.
    d.line([(MARGIN, 766), (W - MARGIN, 766)], fill=INK, width=2)
    stories = [
        (thumb_nvidia(), "HUANG IS BACK \u2014 NVIDIA +33%",
         "Board reinstates its CEO after Trump lobbied it by phone."),
        (thumb_merkury(), "UKRAINE SINKS RUSSIAN WARSHIP",
         "Zelensky: seven sea drones hit the corvette Merkury off Libya."),
        (thumb_cop31(), "COP31 COLLAPSES \u2014 NO DEAL",
         "Longest climate talks ever end with no fossil-fuel pact."),
        (thumb_manchester(), "12,000 FLEE MANCHESTER CONCERT",
         "Unknown substance released at a Don Toliver show; 80+ checked."),
    ]
    cell_w, cell_h = (CW - 24) // 2, 100
    gx, gy = MARGIN, 778
    for i, (thumb, head, deck_text) in enumerate(stories):
        x = gx + (i % 2) * (cell_w + 24)
        yy = gy + (i // 2) * (cell_h + 10)
        img.paste(thumb, (x, yy))
        d = ImageDraw.Draw(img)
        d.rectangle([x, yy, x + 150, yy + 100], outline=INK, width=1)
        tx = x + 162
        tw = cell_w - 162
        f_h = fit(d, head, SANS_BLACK, 27, tw)
        lines = wrap(d, head, f_h, tw)
        ly = yy + 2
        for line in lines[:2]:
            d.text((tx, ly), line, font=f_h, fill=INK)
            ly += 28
        f_dd = font(SERIF, 18)
        for line in wrap(d, deck_text, f_dd, tw)[:2]:
            d.text((tx, ly), line, font=f_dd, fill=(60, 56, 50))
            ly += 21

    # Footer ticker.
    d.rectangle([MARGIN, 992, W - MARGIN, 1014], fill=INK)
    f_tick = font(SANS_BOLD, 15)
    tick = ("ALSO: US SANCTIONS 24 IRAN-LINKED TARGETS  \u2022  POLAND: FALLEN "
            "OBJECTS WERE RUSSIAN KH-101s  \u2022  DEMOCRATS HOLD 258 SEATS")
    while d.textlength(tick, font=f_tick) > CW - 16 and f_tick.size > 11:
        f_tick = font(SANS_BOLD, f_tick.size - 1)
    d.text((MARGIN + 8, 994), tick, font=f_tick, fill=(246, 241, 231))

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
