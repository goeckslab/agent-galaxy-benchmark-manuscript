# Figures

Every figure is generated from code, never pasted in as an image.
Each figure has its own folder:

```text
figures/figN_short_name/
├── make_figure.py      # reads data/ and analysis/ outputs, writes the files below
├── figN_short_name.pdf
├── figN_short_name.png
└── source_data.csv     # the exact values plotted
```

Start from `_template/make_figure.py`.
Register every figure in `figures.csv` and mark it `main` or `supplementary` from the start, because journals cap main-text display items.
Use consistent model names and a colorblind-safe palette across all figures.
