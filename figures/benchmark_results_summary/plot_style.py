"""Physical artwork dimensions and shared visual encodings at publication size."""
import os
from io import BytesIO
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1793145600")

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

MM = 25.4
WIDTH = 180
G = "#12676A"
C = "#A44922"
INK = "#202428"
MUTED = "#444B50"
GRID = "#D5DADC"
PALE = "#EDF2F2"
MODELS = ["GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "DeepSeek V4 Pro"]
BENCH = ["BixBench", "CompBioBench", "IWC"]

faces = {entry.name for entry in font_manager.fontManager.ttflist}
font = next((name for name in ("Arial", "Helvetica", "Liberation Sans") if name in faces), "DejaVu Sans")
plt.rcParams.update({
    "font.family": font, "font.size": 7, "text.color": INK, "axes.labelcolor": INK,
    "axes.labelsize": 7, "axes.labelweight": "bold", "axes.edgecolor": MUTED, "axes.linewidth": .65,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "xtick.color": INK, "ytick.color": INK, "xtick.major.size": 2, "ytick.major.size": 0,
    "xtick.labelsize": 6.5, "ytick.labelsize": 7, "ytick.major.pad": 2.5, "xtick.major.pad": 2,
    "legend.frameon": False, "legend.fontsize": 6.5, "hatch.linewidth": .5,
    "pdf.fonttype": 42, "svg.fonttype": "none", "svg.hashsalt": "galaxy-october-2026",
    "savefig.facecolor": "white", "lines.solid_capstyle": "round",
})


def data(script, filename="source_data.csv"):
    return pd.read_csv(Path(script).resolve().parents[1] / "dataset" / filename)


class Plate:
    """Lay out panels in millimetres measured from the top left of the final page."""
    def __init__(self, height):
        self.height = height
        self.fig = plt.figure(figsize=(WIDTH / MM, height / MM))

    def axes(self, left, top, width, height):
        return self.fig.add_axes([left / WIDTH, 1 - (top + height) / self.height,
                                  width / WIDTH, height / self.height])

    def text(self, x, y, label, **kwargs):
        options = {"va": "center", "fontsize": 7, **kwargs}
        return self.fig.text(x / WIDTH, 1 - y / self.height, label, **options)

    def heading(self, x, y, letter, label):
        self.text(x, y, letter, fontsize=7, weight="bold")
        self.text(x + 4.2, y, label, fontsize=7, weight="bold")

    def line(self, x1, y1, x2, y2, color=GRID, lw=.5):
        self.fig.add_artist(Line2D([x1 / WIDTH, x2 / WIDTH],
                            [1 - y1 / self.height, 1 - y2 / self.height],
                            transform=self.fig.transFigure, color=color, linewidth=lw))

    def mark(self, x, y, marker, edge, face, size=3.6):
        self.fig.add_artist(Line2D([x / WIDTH], [1 - y / self.height], marker=marker,
                                   markersize=size, markeredgecolor=edge, markerfacecolor=face,
                                   markeredgewidth=.85, linestyle="none", transform=self.fig.transFigure))

    def box(self, x, y, w, h, color=PALE):
        self.fig.add_artist(Rectangle((x / WIDTH, 1 - (y + h) / self.height), w / WIDTH,
                            h / self.height, transform=self.fig.transFigure,
                            facecolor=color, edgecolor="none", zorder=0))

    def arrow(self, x1, y1, x2, y2):
        self.fig.add_artist(FancyArrowPatch((x1 / WIDTH, 1 - y1 / self.height),
                            (x2 / WIDTH, 1 - y2 / self.height), transform=self.fig.transFigure,
                            arrowstyle="-|>", mutation_scale=6, linewidth=.65, color=MUTED))

    def save(self, script):
        folder = Path(script).resolve().parents[1]
        out = folder / "output"
        out.mkdir(exist_ok=True)
        for extension in ("pdf", "svg"):
            path = out / f"{folder.name}.{extension}"
            self.fig.savefig(path, format=extension)
        # Convert the raster in memory so the deliverable is opened for writing only once.
        with BytesIO() as buffer:
            self.fig.savefig(buffer, dpi=450, format="png")
            buffer.seek(0)
            with Image.open(buffer) as img:
                img.convert("RGB").save(out / f"{folder.name}.png", dpi=(450, 450))
        plt.close(self.fig)


def xgrid(ax):
    ax.grid(axis="x", color=GRID, lw=.45)
    ax.set_axisbelow(True)
