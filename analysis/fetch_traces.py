#!/usr/bin/env python3
"""Download run traces from the Hugging Face dataset into traces/ (git-ignored).

Usage:
    export HF_TOKEN=...      # read token; never commit it
    python analysis/fetch_traces.py --pattern "compbiobench/**/cryptic-exon-q1/**"

Prints the dataset revision (commit hash). Record it in data/results_manifest.csv
so each reported number can be traced to an exact version of the traces.
"""
import argparse
import os
import sys

from huggingface_hub import HfApi, snapshot_download

DEFAULT_REPO = "goeckslab/galaxy-agent-benchmark-run-traces"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=DEFAULT_REPO, help="Hugging Face dataset id")
    p.add_argument(
        "--pattern",
        action="append",
        help="Glob of files to download; repeat for several. Omit to download everything (large).",
    )
    p.add_argument("--out", default="traces", help="Output directory (git-ignored)")
    p.add_argument("--revision", default=None, help="Dataset revision (commit hash) to pin")
    args = p.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Warning: HF_TOKEN is not set; this only works if the dataset is public.", file=sys.stderr)

    info = HfApi(token=token).dataset_info(args.repo, revision=args.revision)
    print(f"Dataset revision: {info.sha}")

    path = snapshot_download(
        repo_id=args.repo,
        repo_type="dataset",
        revision=info.sha,
        allow_patterns=args.pattern,
        local_dir=args.out,
        token=token,
    )
    print(f"Downloaded to {path}")


if __name__ == "__main__":
    main()
