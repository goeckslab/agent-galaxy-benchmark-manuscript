"""Assemble the supplementary vector plates at 180 mm and typeset their canonical README legends."""
import argparse
import os
import re
import shutil
import subprocess
from uuid import uuid4

from benchmark_records import BASE, FIGS, ROOT


def latex(text):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "_": r"\_",
                    "#": r"\#", "<": r"\textless{}", ">": r"\textgreater{}",
                    "≥": r"\ensuremath{\geq}", "≤": r"\ensuremath{\leq}",
                    "×": r"\ensuremath{\times}", "–": "--", "−": r"\ensuremath{-}",
                    "’": "'", "°": r"\textdegree{}"}
    escaped = "".join(replacements.get(c, c) for c in text)
    return re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", escaped)


def assemble(engine):
    preamble = r"""\documentclass[10pt,multi=figureplate,border={10mm 8mm 10mm 8mm}]{standalone}
\usepackage[T1]{fontenc}
\usepackage{textcomp,graphicx}
\newenvironment{figureplate}{}{}
\IfFileExists{tgheros.sty}{\usepackage{tgheros}}{}
\renewcommand{\familydefault}{\sfdefault}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\pdfinfoomitdate=1
\pdftrailerid{}
\pdfsuppressptexinfo=15
\pdfinfo{/Title (Supplementary figures - Improving Galaxy's interface for agents)}
\pagestyle{empty}
\begin{document}"""
    # Keep the build inside the project's ignored render tree, including in restricted environments.
    build_root = ROOT/"manuscript/_output"
    work = build_root/("supplement-" + uuid4().hex)
    work.mkdir(parents=True)
    try:
        pages = []
        for folder in FIGS[2:]:
            first, legend, *_ = (BASE/folder/"README.md").read_text(encoding="utf8").split("\n\n")
            label, title = first.removeprefix("# ").split(". ", 1)
            shutil.copyfile(BASE/folder/"output"/f"{folder}.pdf", work/f"{folder}.pdf")
            pages.append("\n".join([
                r"\begin{figureplate}\begin{minipage}{180mm}",
                r"{\small\bfseries " + latex(label) + r"}\par\vspace{2mm}",
                r"{\Large\bfseries " + latex(title) + r"}\par\vspace{3mm}",
                r"\includegraphics[width=180mm]{" + folder + r".pdf}\par\vspace{2mm}",
                r"\raggedright\fontsize{10}{13}\selectfont " + latex(legend) + r"\par",
                r"\end{minipage}\end{figureplate}"]))
        tex = preamble + "\n" + "\n".join(pages) + "\n\\end{document}\n"
        (work/"supplement.tex").write_text(tex, encoding="utf8")
        env = {**os.environ, "SOURCE_DATE_EPOCH":"1793145600", "FORCE_SOURCE_DATE":"1"}
        result = subprocess.run([engine,"-interaction=nonstopmode","-halt-on-error","supplement.tex"],
                                cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(result.stdout.decode(errors="replace")[-3500:])
        (work/"supplement.pdf").replace(BASE/"supplementary_figures.pdf")
    finally:
        if work.resolve().parent != build_root.resolve():
            raise RuntimeError("Unexpected supplementary build directory")
        for file in work.iterdir():
            if file.is_file():
                file.unlink()
        work.rmdir()
    print(f"Assembled {len(FIGS) - 2} supplementary figures with their source legends.")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine",default="pdflatex",help="path to a pdfLaTeX executable")
    assemble(parser.parse_args().engine)
