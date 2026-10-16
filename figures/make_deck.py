#!/usr/bin/env python
"""make_deck.py — builds deck_all_figures.pdf: one letter-size page per figure, the PNG (downsampled to 750 px
wide, about 100 ppi on the page) on top and its caption from captions.md below.

Usage (in figures/):  python make_deck.py [--captions captions.md] [--out deck_all_figures.pdf]
Needs matplotlib (and Pillow, a matplotlib dependency).  The captions in paper/sections/*.tex are authoritative;
captions.md is the plain-text companion of the figure files.
"""
import argparse
import re
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

ORDER = [("1", "fig01.png"), ("2", "fig02.png"), ("3", "fig03.png"), ("4", "fig04.png"), ("5", "fig05.png"),
         ("6", "fig06.png"), ("6b", "fig06b.png"), ("6c", "fig06c.png"), ("7", "fig07.png"), ("8", "fig08.png"),
         ("9", "fig09.png")]


def plain(md):
    """Markdown emphasis and code marks to plain text; the marks (*) and (**) of Figure 7 are kept; 𝔍 is written I."""
    md = md.replace("`", "").replace("𝔍", "I")    # DejaVu Sans has no Fraktur J; the figures also write I, I_S
    md = re.sub(r"\*\*(?!\))(.+?)(?<!\()\*\*", r"\1", md)            # **bold**
    md = re.sub(r"(?<![(*])\*(?=[^\s*)])(.+?)(?<=[^\s(*])\*(?![*)])", r"\1", md)   # *italic*
    return md


def captions(path):
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"(?m)^\*\*Figure (\d+[bc]?)\b", text)
    out = {}
    for i in range(1, len(parts), 2):
        key, body = parts[i], parts[i + 1]
        out[key] = plain("**Figure " + key + body.split("\n\n**Figure")[0]).strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captions", default="captions.md")
    ap.add_argument("--out", default="deck_all_figures.pdf")
    a = ap.parse_args()
    caps = captions(a.captions)
    missing = [k for k, _ in ORDER if k not in caps]
    if missing:
        raise SystemExit(f"captions.md has no entry for figures {missing}")
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"]})
    with PdfPages(a.out, metadata={"Title": "Figures and captions", "CreationDate": None, "ModDate": None}) as pdf:
        for key, png in ORDER:
            im = Image.open(png).convert("RGB")
            w, h = im.size
            im = im.resize((750, max(1, round(h * 750 / w))), Image.LANCZOS)
            fig = plt.figure(figsize=(8.5, 11))
            iw = 7.5
            ih = min(iw * im.size[1] / im.size[0], 7.6)
            iw = ih * im.size[0] / im.size[1]
            ax = fig.add_axes([(8.5 - iw) / 2 / 8.5, (11 - 0.5 - ih) / 11, iw / 8.5, ih / 11])
            ax.imshow(im, interpolation="none")
            ax.axis("off")
            wrapped = "\n".join(textwrap.fill(par, 118) for par in caps[key].split("\n") if par.strip())
            fig.text(0.5 / 8.5, (11 - 0.5 - ih - 0.25) / 11, wrapped, ha="left", va="top", fontsize=6.5)
            pdf.savefig(fig)
            plt.close(fig)
    print(f"{a.out}: {len(ORDER)} pages")


if __name__ == "__main__":
    main()
