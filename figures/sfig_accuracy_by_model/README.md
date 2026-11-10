# Supplementary figure: accuracy by model

Accuracy of each model in Galaxy and custom code on the four benchmarks, plus all models together, from the results website's data in `data/site/`.
`make_figure.py` reads `data/accuracy_by_model.csv`, written by `analysis/accuracy.py`, which documents how accuracy is defined for each benchmark.
Each panel has its own accuracy axis because the benchmarks' accuracy ranges differ.
The IWC multi-step tasks were run with three models, not four.
