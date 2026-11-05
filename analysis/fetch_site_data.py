#!/usr/bin/env python3
"""Copy the benchmark results website's machine-readable data into data/site/.

Usage:
    python analysis/fetch_site_data.py                          # fetch and verify
    python analysis/fetch_site_data.py --source-commit <sha>    # also record the commit
    python analysis/fetch_site_data.py --check                  # re-verify local copies, no network

The results website (https://goeckslab.github.io/galaxy-agent-benchmark/) publishes
data/index.json, which lists each results file with its byte count and SHA-256.
This script downloads the index, its README, every file it lists, and the token and
user-defined-tool usage tables the README links to. Each file is saved under
data/site/ at the same path it has on the website, so the index's relative URLs
still resolve. Files listed in the index are checked against its size and SHA-256;
the script stops without writing anything if any check fails.

data/site/MANIFEST.csv records, for every file, its URL, size, SHA-256, whether that
checksum was checked against the index, the fetch date, the server's Last-Modified
time, and (if given with --source-commit) the commit of goeckslab/galaxy-agent-benchmark
the website was deployed from. The website does not publish that commit itself, so
pass it only after confirming it, for example by comparing a file's SHA-256 with the
same file at that commit.

The website regenerates these files on every deployment, so analyses must read the
copies in data/site/, never the live URLs. Refresh them in a pull request of their
own, so the diff shows what changed.
"""
import argparse
import csv
import datetime
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:  # use the system trust store where a proxy re-signs TLS traffic
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

SITE = "https://goeckslab.github.io/galaxy-agent-benchmark/"
INDEX = "data/index.json"
# Linked from the website's data README but not listed in the index (no published checksum).
EXTRA = [
    "data/README.md",
    "compbiobench/data/public_token_usage.tsv",
    "compbiobench/data/public_udt_usage.tsv",
    "iwc/data/token_usage.tsv",
]
OUT = Path("data/site")
FIELDS = ["path", "url", "bytes", "sha256", "checksum_source", "fetched", "last_modified", "source_commit"]


def fetch(url: str) -> tuple[bytes, str]:
    with urllib.request.urlopen(url) as r:
        return r.read(), r.headers.get("Last-Modified", "")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def site_path(url: str) -> str:
    """Path of a website URL relative to the site root, e.g. 'iwc/data/results.json'."""
    if not url.startswith(SITE):
        sys.exit(f"{url} is outside {SITE}")
    return urllib.parse.urlparse(url).path[len(urllib.parse.urlparse(SITE).path):]


def check(out: Path) -> None:
    manifest = out / "MANIFEST.csv"
    bad = 0
    with open(manifest, newline="") as f:
        for row in csv.DictReader(f):
            data = (out / row["path"]).read_bytes()
            if len(data) != int(row["bytes"]) or sha256(data) != row["sha256"]:
                print(f"MISMATCH {row['path']}", file=sys.stderr)
                bad += 1
    if bad:
        sys.exit(f"{bad} file(s) in {out} do not match {manifest}")
    print(f"All files in {out} match {manifest}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--source-commit", default="",
                   help="Confirmed commit of goeckslab/galaxy-agent-benchmark the website was deployed from")
    p.add_argument("--check", action="store_true", help="Re-verify local copies against MANIFEST.csv and exit")
    args = p.parse_args()

    if args.check:
        check(args.out)
        return

    today = datetime.date.today().isoformat()
    index_url = urllib.parse.urljoin(SITE, INDEX)
    index_bytes, index_modified = fetch(index_url)
    index = json.loads(index_bytes)
    if index.get("schema_version") != 1:
        sys.exit(f"Unsupported index schema_version {index.get('schema_version')!r}; update this script")

    files = {INDEX: (index_url, index_bytes, index_modified, "none (the index itself)")}
    for d in index["datasets"]:
        url = urllib.parse.urljoin(index_url, d["url"])
        data, modified = fetch(url)
        if len(data) != d["bytes"] or sha256(data) != d["sha256"]:
            sys.exit(f"{url} does not match the index (bytes {len(data)} vs {d['bytes']}, "
                     f"sha256 {sha256(data)} vs {d['sha256']}); nothing written")
        files[site_path(url)] = (url, data, modified, "index.json")
    for path in EXTRA:
        url = urllib.parse.urljoin(SITE, path)
        data, modified = fetch(url)
        files[path] = (url, data, modified, "none (not in index)")

    rows = []
    for path, (url, data, modified, checksum_source) in sorted(files.items()):
        dest = args.out / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        rows.append({"path": path, "url": url, "bytes": len(data), "sha256": sha256(data),
                     "checksum_source": checksum_source, "fetched": today,
                     "last_modified": modified, "source_commit": args.source_commit})
    with open(args.out / "MANIFEST.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} files and MANIFEST.csv to {args.out} from {SITE} ({today})")


if __name__ == "__main__":
    main()
