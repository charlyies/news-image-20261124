#!/usr/bin/env python3
"""Render the front page of THE WORLD TODAY for Tuesday 24 November 2026.

Produces entry.png, 1024 by 1024 pixels, using PIL alone: a newspaper
front page that sums up the day's world news. Every picture element is
drawn in code - gradients, silhouettes, glow layers - and every word is
set with a real font, so nothing comes out garbled.

The five stories, each checked against reputable reporting on 23-24 Nov:
  LEAD - Iran vows to use "every means" against the US naval blockade
         of its ports at the Strait of Hormuz; Trump threatens to sink
         ships that defy it (Reuters, 23 Nov)
  2    - Nvidia's board reinstates Jensen Huang as CEO after Trump
         lobbied the board by phone; the shares soar 33% (Reuters, 23 Nov)
  3    - Zelensky confirms Ukraine sank the Russian corvette Merkury
         off Libya with seven sea drones; MV Angara hit, Ka-27 destroyed
         (AP / Reuters, 23 Nov)
  4    - COP31 collapses with no deal: the longest COP ever, and the
         first no-deal COP since 2009 (Reuters / BBC, 22 Nov)
  5    - 12,000 evacuated from a Don Toliver concert at Manchester's
         Co-op Live after an unknown substance is released; 80+ checked,
         one person in hospital (Reuters / BBC, 23 Nov)
"""
import math as _math
import random as _random

from PIL import Image as _Image
from PIL import ImageDraw as _Draw
from PIL import ImageFilter as _Filter
from PIL import ImageFont as _Font

PAGE_W, PAGE_H = 1024, 1024
EDGE = 36
INNER_W = PAGE_W - 2 * EDGE  # 952

PAGE = (246, 241, 231)
BLACK = (17, 17, 17)
CRIMSON = (168, 30, 30)
MIDNIGHT = (20, 33, 61)
ASH = (90, 86, 78)

_FONTS = "/usr/share/fonts/truetype/noto/"
F_SERIF_BLACK = _FONTS + "NotoSerifDisplay-Black.ttf"
F_SERIF_BOLD = _FONTS + "NotoSerif-Bold.ttf"
F_SERIF = _FONTS + "NotoSerif-Regular.ttf"
F_SERIF_IT = _FONTS + "NotoSerif-Italic.ttf"
F_SANS_BLACK = _FONTS + "NotoSansDisplay-Black.ttf"
F_SANS_BOLD = _FONTS + "NotoSans-Bold.ttf"
F_SANS = _FONTS + "NotoSans-Regular.ttf"

_random.seed(20261124)


def load_font(path, size):
    return _Font.truetype(path, size)


def blend(a, b, t):
    """Mix two RGB triples by t (0 -> a, 1 -> b)."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_shade(dr, box, top, bottom):
    """Paint a top-to-bottom gradient across box."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        dr.line([(x0, y), (x1, y)], fill=blend(top, bottom, (y - y0) / span))


def fit_text(dr, text, path, size, max_w, floor=10):
    """Biggest size at or under `size` that fits `text` inside max_w."""
    while size > floor:
        f = load_font(path, size)
        if dr.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return load_font(path, floor)


def wrap_text(dr, text, f, max_w):
    """Greedy word wrap: lines of `text` that each fit max_w."""
    words = text.split()
    out, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if dr.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def halo(layer, centre, radius, colour):
    """Soft radial glow built from concentric circles, alpha falling off."""
    dr = _Draw.Draw(layer)
    steps = 14
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(colour[3] * (1 - i / steps) ** 2)
        dr.ellipse([centre[0] - r, centre[1] - r, centre[0] + r, centre[1] + r],
                   fill=(colour[0], colour[1], colour[2], a))


def speckle(img, amount=1200, alpha=9):
    """Sprinkle faint grain so the picture never looks like flat vector art."""
    iw, ih = img.size
    g = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    gd = _Draw.Draw(g)
    for _ in range(amount):
        x = _random.randint(0, iw - 1)
        y = _random.randint(0, ih - 1)
        v = _random.randint(0, 255)
        gd.point((x, y), fill=(v, v, v, alpha))
    return _Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")


# ---------------------------------------------------------------- lead scene
def hormuz_scene():
    """The Strait of Hormuz at dusk: a tanker hemmed in by grey warships,
    a dashed red blockade line across the channel, searchlights, and a low
    sun sinking behind the headland."""
    iw, ih = INNER_W, 340
    img = _Image.new("RGB", (iw, ih), (20, 26, 52))
    dr = _Draw.Draw(img)
    horizon = int(ih * 0.58)

    # Dusk sky: deep indigo down to a smouldering orange band at the sea.
    vertical_shade(dr, (0, 0, iw, horizon), (14, 18, 44), (206, 88, 46))
    # The sea: dark steel blue fading to near-black at the bottom edge.
    vertical_shade(dr, (0, horizon, iw, ih), (46, 66, 106), (7, 11, 26))

    # A low sun, half sunk on the horizon with a wide warm halo. It sits
    # left of centre, clear of the warship superstructures on the right.
    glow = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    halo(glow, (250, horizon - 26), 120, (255, 190, 110, 90))
    halo(glow, (250, horizon - 26), 55, (255, 220, 160, 140))
    img = _Image.alpha_composite(img.convert("RGBA"), glow)
    dr = _Draw.Draw(img)
    dr.ellipse([250 - 30, horizon - 56, 250 + 30, horizon + 4],
               fill=(255, 236, 190, 255))

    # Cloud bands: long soft ellipses, dark on top, lit orange underneath.
    clouds = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    cd = _Draw.Draw(clouds)
    for cx, cy, rx, ry, al in [
        (120, 44, 160, 15, 70), (420, 30, 190, 12, 60), (760, 60, 180, 14, 75),
        (300, 90, 150, 11, 55), (640, 112, 160, 11, 50), (890, 26, 130, 11, 60),
        (520, 150, 150, 10, 45), (80, 140, 120, 10, 45),
    ]:
        cd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                   fill=(36, 28, 56, al))
        cd.ellipse([cx - rx, cy + ry - 6, cx + rx, cy + ry + 6],
                   fill=(238, 140, 80, 40))
    clouds = clouds.filter(_Filter.GaussianBlur(5))
    img = _Image.alpha_composite(img, clouds)
    dr = _Draw.Draw(img)

    # Rocky headlands on both banks, framing the narrow channel.
    dr.polygon([(0, horizon), (0, horizon - 96), (70, horizon - 132),
                (150, horizon - 88), (210, horizon - 60), (210, horizon)],
               fill=(12, 15, 32))
    dr.polygon([(iw, horizon), (iw, horizon - 110), (880, horizon - 140),
                (800, horizon - 92), (760, horizon - 58), (760, horizon)],
               fill=(12, 15, 32))

    # Sunset reflections on the water: horizontal streaks only, never vertical.
    streaks = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    sd = _Draw.Draw(streaks)
    for _ in range(90):
        y = _random.randint(horizon + 6, ih - 8)
        x = _random.randint(0, iw - 120)
        ln = _random.randint(30, 150)
        warm = _random.random() < 0.65
        col = (238, 140, 80) if warm else (150, 180, 220)
        sd.line([(x, y), (x + ln, y)], fill=col + (_random.randint(18, 70),),
                width=_random.choice([1, 2, 3]))
    streaks = streaks.filter(_Filter.GaussianBlur(1.2))
    img = _Image.alpha_composite(img, streaks)
    dr = _Draw.Draw(img)

    # The tanker: a long dark hull mid-channel, deck houses and a funnel,
    # warm portholes in a row along the waterline.
    hull = (6, 9, 20)
    dr.polygon([(330, ih - 66), (330, ih - 38), (640, ih - 38),
                (668, ih - 50), (640, ih - 66)], fill=hull)
    dr.rectangle([420, ih - 92, 470, ih - 66], fill=hull)
    dr.rectangle([560, ih - 96, 606, ih - 66], fill=hull)
    dr.rectangle([446, ih - 108, 454, ih - 92], fill=hull)
    for x in range(350, 630, 26):
        dr.rectangle([x, ih - 56, x + 5, ih - 51], fill=(255, 196, 110, 255))

    # A grey warship on the right, bow toward the tanker, mast and radar
    # dome, its searchlight beam sweeping across the water.
    war = (52, 58, 70)
    dr.polygon([(700, ih - 60), (700, ih - 40), (900, ih - 40),
                (924, ih - 50), (900, ih - 60)], fill=war)
    dr.rectangle([780, ih - 88, 830, ih - 60], fill=war)
    dr.rectangle([806, ih - 112, 812, ih - 88], fill=war)
    dr.ellipse([798, ih - 122, 820, ih - 100], fill=war)
    beam = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    bd = _Draw.Draw(beam)
    bd.polygon([(810, ih - 100), (640, ih - 52), (640, ih - 30),
                (810, ih - 96)], fill=(255, 240, 200, 46))
    img = _Image.alpha_composite(img, beam.filter(_Filter.GaussianBlur(2)))
    dr = _Draw.Draw(img)
    lamp = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    halo(lamp, (810, ih - 100), 16, (255, 240, 200, 180))
    img = _Image.alpha_composite(img, lamp)
    dr = _Draw.Draw(img)
    # A second, smaller patrol boat on the left edge of the frame.
    dr.polygon([(60, ih - 52), (60, ih - 36), (180, ih - 36),
                (196, ih - 44), (180, ih - 52)], fill=(40, 45, 58))
    dr.rectangle([110, ih - 70, 140, ih - 52], fill=(40, 45, 58))

    # The blockade line: a dashed red cordon across the channel with small
    # warning buoys, drawn high enough to clear the ships below it.
    by = horizon + 26
    for x in range(230, 760, 34):
        dr.line([(x, by), (x + 20, by)], fill=(220, 60, 50), width=4)
    for x in (300, 470, 640):
        dr.polygon([(x, by - 10), (x + 7, by + 2), (x - 7, by + 2)],
                   fill=(230, 80, 60))
        dr.ellipse([x - 4, by + 2, x + 4, by + 10], fill=(230, 80, 60))

    return speckle(img)


# ------------------------------------------------------------- mini thumbnails
def chip_thumb():
    """A green circuit board with a chip and a steep rising arrow: +33%."""
    iw, ih = 150, 100
    img = _Image.new("RGB", (iw, ih), (10, 40, 22))
    dr = _Draw.Draw(img)
    vertical_shade(dr, (0, 0, iw, ih), (14, 66, 36), (7, 26, 15))
    # Circuit traces with solder dots at the ends.
    for x0, y0, x1, y1 in [(10, 20, 44, 20), (10, 80, 30, 80),
                           (120, 14, 140, 14), (118, 86, 140, 86),
                           (44, 20, 44, 34), (30, 80, 30, 62)]:
        dr.line([(x0, y0), (x1, y1)], fill=(46, 160, 90), width=2)
    for cx, cy in [(10, 20), (10, 80), (140, 14), (140, 86)]:
        dr.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(90, 220, 140))
    # The chip itself, centre-left, with pins top and bottom.
    dr.rectangle([52, 30, 92, 70], fill=(18, 90, 48),
                 outline=(120, 240, 160), width=2)
    dr.rectangle([62, 40, 82, 60], fill=(10, 50, 26))
    for x in (58, 67, 76, 85):
        dr.line([(x, 30), (x, 22)], fill=(120, 240, 160), width=2)
        dr.line([(x, 70), (x, 78)], fill=(120, 240, 160), width=2)
    # The rising arrow, bottom-left to top-right, over the chip's right side.
    dr.line([(96, 82), (118, 52), (132, 60), (146, 30)],
            fill=(255, 210, 80), width=4)
    dr.polygon([(146, 30), (134, 30), (146, 42)], fill=(255, 210, 80))
    return img


def corvette_thumb():
    """A listing, half-sunk corvette off Libya: fire, smoke, a sea drone."""
    iw, ih = 150, 100
    img = _Image.new("RGB", (iw, ih), (16, 22, 40))
    dr = _Draw.Draw(img)
    vertical_shade(dr, (0, 0, iw, ih), (30, 34, 58), (10, 14, 28))
    dr.ellipse([96, 6, 126, 36], fill=(220, 200, 160))
    smoke = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    sd = _Draw.Draw(smoke)
    for cx, cy, r in [(58, 34, 14), (70, 24, 17), (84, 16, 13)]:
        sd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 110, 105, 120))
    img = _Image.alpha_composite(img.convert("RGBA"),
                                 smoke.filter(_Filter.GaussianBlur(4)))
    dr = _Draw.Draw(img)
    # The hull, listing with its bow down.
    dr.polygon([(18, 74), (30, 52), (118, 66), (128, 84), (60, 84)],
               fill=(8, 10, 18))
    dr.rectangle([66, 44, 74, 56], fill=(8, 10, 18))
    fire = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    halo(fire, (52, 60), 22, (255, 150, 60, 190))
    img = _Image.alpha_composite(img, fire)
    dr = _Draw.Draw(img)
    dr.polygon([(44, 64), (52, 50), (60, 64)], fill=(255, 220, 140))
    # One small sea drone skimming the water, bottom right.
    dr.ellipse([112, 88, 138, 94], fill=(30, 34, 44))
    dr.line([(112, 91), (104, 88)], fill=(200, 200, 210), width=2)
    for y in range(86, 100, 3):
        dr.line([(30, y), (110, y)], fill=(90, 120, 170, 255), width=1)
    return img.convert("RGB")


def globe_thumb():
    """A globe crossed out in red: climate talks that ended with no deal."""
    iw, ih = 150, 100
    img = _Image.new("RGB", (iw, ih), (18, 60, 52))
    dr = _Draw.Draw(img)
    vertical_shade(dr, (0, 0, iw, ih), (24, 88, 74), (10, 34, 30))
    dr.ellipse([25, 8, 125, 108], fill=(38, 110, 180))
    dr.ellipse([38, 24, 66, 50], fill=(70, 150, 80))
    dr.ellipse([76, 58, 106, 86], fill=(70, 150, 80))
    dr.ellipse([54, 72, 76, 92], fill=(70, 150, 80))
    dr.arc([25, 8, 125, 108], 20, 200, fill=(246, 241, 231), width=3)
    dr.line([(22, 96), (128, 16)], fill=(200, 40, 40), width=7)
    dr.line([(22, 96), (128, 16)], fill=(255, 90, 80), width=3)
    return img


def arena_thumb():
    """A concert arena at night: a lit stage, light beams, a crowd filing out."""
    iw, ih = 150, 100
    img = _Image.new("RGB", (iw, ih), (14, 12, 26))
    dr = _Draw.Draw(img)
    vertical_shade(dr, (0, 0, iw, ih), (26, 20, 48), (10, 8, 20))
    # The arena roof arc.
    dr.pieslice([10, -70, 140, 40], 0, 180, fill=(40, 36, 66))
    dr.arc([10, -70, 140, 40], 0, 180, fill=(120, 110, 160), width=2)
    # The stage at the back, lit.
    dr.rectangle([58, 46, 92, 66], fill=(220, 200, 120))
    dr.rectangle([62, 50, 88, 62], fill=(30, 24, 50))
    # Light beams fanning out from the stage.
    beams = _Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    bd = _Draw.Draw(beams)
    for x2, a in [(20, 60), (48, 80), (102, 80), (130, 60)]:
        bd.polygon([(75, 50), (x2, 96), (x2 + 8, 96)], fill=(255, 230, 150, a))
    img = _Image.alpha_composite(img.convert("RGBA"),
                                 beams.filter(_Filter.GaussianBlur(1)))
    dr = _Draw.Draw(img)
    # The crowd: rows of small heads, with a gap for the exit stream.
    for row, y in enumerate((72, 80, 88, 95)):
        for x in range(8, 144, 11):
            if row >= 2 and 60 < x < 96:
                continue
            dr.ellipse([x, y, x + 6, y + 6], fill=(200, 190, 170))
    # The exit stream: a column of dots heading down the middle gap.
    for y in range(72, 100, 6):
        dr.ellipse([72, y, 78, y + 5], fill=(255, 210, 90))
    return img.convert("RGB")


# ------------------------------------------------------------------- the page
def build_page():
    page = _Image.new("RGB", (PAGE_W, PAGE_H), PAGE)
    dr = _Draw.Draw(page)

    # Masthead.
    dr.line([(EDGE, 30), (PAGE_W - EDGE, 30)], fill=BLACK, width=2)
    f_title = fit_text(dr, "THE WORLD TODAY", F_SERIF_BLACK, 96, INNER_W)
    dr.text(((PAGE_W - dr.textlength("THE WORLD TODAY", font=f_title)) / 2, 34),
            "THE WORLD TODAY", font=f_title, fill=BLACK)

    # Dateline bar.
    dr.line([(EDGE, 146), (PAGE_W - EDGE, 146)], fill=BLACK, width=3)
    f_date = fit_text(dr, "TUESDAY, 24 NOVEMBER 2026", F_SANS_BOLD, 28,
                      INNER_W - 240)
    date_w = dr.textlength("TUESDAY, 24 NOVEMBER 2026", font=f_date)
    dr.text(((PAGE_W - date_w) / 2, 152), "TUESDAY, 24 NOVEMBER 2026",
            font=f_date, fill=BLACK)
    f_side = load_font(F_SANS, 19)
    dr.text((EDGE, 156), "WORLD NEWS", font=f_side, fill=ASH)
    side_r = "No. 328"
    dr.text((PAGE_W - EDGE - dr.textlength(side_r, font=f_side), 156),
            side_r, font=f_side, fill=ASH)
    dr.line([(EDGE, 190), (PAGE_W - EDGE, 190)], fill=BLACK, width=2)

    # The lead scene.
    scene = hormuz_scene()
    page.paste(scene, (EDGE, 196))
    dr = _Draw.Draw(page)
    dr.rectangle([EDGE, 196, PAGE_W - EDGE, 196 + 340], outline=BLACK, width=2)
    # Caption on a dark strip inside the scene's bottom edge.
    cap = _Image.new("RGBA", (INNER_W, 30), (10, 10, 12, 190))
    page.paste(_Image.alpha_composite(
        page.crop((EDGE, 196 + 340 - 30, PAGE_W - EDGE, 196 + 340)).convert("RGBA"),
        cap), (EDGE, 196 + 340 - 30))
    dr = _Draw.Draw(page)
    f_cap = load_font(F_SANS, 17)
    dr.text((EDGE + 10, 196 + 340 - 25),
            "THE STRAIT OF HORMUZ: TANKERS AND WARSHIPS AS THE BLOCKADE TIGHTENS",
            font=f_cap, fill=(246, 241, 231))

    # Lead headline and deck.
    y = 548
    f_head = fit_text(dr, "IRAN VOWS \u2018EVERY MEANS\u2019", F_SANS_BLACK, 62, INNER_W)
    dr.text((EDGE, y), "IRAN VOWS \u2018EVERY MEANS\u2019", font=f_head, fill=BLACK)
    y += 66
    dr.text((EDGE, y), "AGAINST U.S. BLOCKADE", font=f_head, fill=CRIMSON)
    y += 70
    f_deck = load_font(F_SERIF_IT, 27)
    deck = ("Tehran swears to break the Hormuz shipping blockade as Trump "
            "threatens to sink vessels that defy it.")
    for line in wrap_text(dr, deck, f_deck, INNER_W):
        dr.text((EDGE, y), line, font=f_deck, fill=BLACK)
        y += 32

    # Secondary stories in a 2 by 2 grid.
    dr.line([(EDGE, 766), (PAGE_W - EDGE, 766)], fill=BLACK, width=2)
    stories = [
        (chip_thumb(), "HUANG IS BACK \u2014 NVIDIA +33%",
         "Board reinstates its CEO after Trump lobbied it by phone."),
        (corvette_thumb(), "UKRAINE SINKS RUSSIAN WARSHIP",
         "Zelensky: seven sea drones hit the corvette Merkury off Libya."),
        (globe_thumb(), "COP31 COLLAPSES \u2014 NO DEAL",
         "Longest climate talks ever end with no fossil-fuel pact."),
        (arena_thumb(), "12,000 FLEE MANCHESTER CONCERT",
         "Unknown substance released at a Don Toliver show; 80+ checked."),
    ]
    cell_w, cell_h = (INNER_W - 24) // 2, 100
    gx, gy = EDGE, 778
    for i, (thumb, head, deck_text) in enumerate(stories):
        x = gx + (i % 2) * (cell_w + 24)
        yy = gy + (i // 2) * (cell_h + 10)
        page.paste(thumb, (x, yy))
        dr = _Draw.Draw(page)
        dr.rectangle([x, yy, x + 150, yy + 100], outline=BLACK, width=1)
        tx = x + 162
        tw = cell_w - 162
        f_h = fit_text(dr, head, F_SANS_BLACK, 27, tw)
        lines = wrap_text(dr, head, f_h, tw)
        ly = yy + 2
        for line in lines[:2]:
            dr.text((tx, ly), line, font=f_h, fill=BLACK)
            ly += 28
        f_dd = load_font(F_SERIF, 18)
        for line in wrap_text(dr, deck_text, f_dd, tw)[:2]:
            dr.text((tx, ly), line, font=f_dd, fill=(60, 56, 50))
            ly += 21

    # Footer ticker, shrunk until it fits the page width.
    dr.rectangle([EDGE, 992, PAGE_W - EDGE, 1014], fill=BLACK)
    f_tick = load_font(F_SANS_BOLD, 15)
    tick = ("ALSO: US SANCTIONS 24 IRAN-LINKED TARGETS  \u2022  POLAND: FALLEN "
            "OBJECTS WERE RUSSIAN KH-101s  \u2022  DEMOCRATS HOLD 258 SEATS")
    while dr.textlength(tick, font=f_tick) > INNER_W - 16 and f_tick.size > 11:
        f_tick = load_font(F_SANS_BOLD, f_tick.size - 1)
    dr.text((EDGE + 8, 994), tick, font=f_tick, fill=(246, 241, 231))

    page.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build_page()
