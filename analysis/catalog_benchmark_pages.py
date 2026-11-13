"""Index public item, specification and supporting pages without downloading execution traces.

Item pages are enumerated from the frozen site exports in data/site. Supporting pages are discovered by
following same-site links breadth-first from the three benchmark entry pages, so a linked page cannot be
missed by an incomplete hand-written list. A page whose bytes are unchanged since the previous catalogue
keeps its original row and retrieval date; new or changed pages get a new row dated today.
"""
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/benchmark_results_summary/sources"
SITE = "https://goeckslab.github.io/galaxy-agent-benchmark/"
ENTRY = ["index.html", "iwc/index.html", "compbiobench/index.html"]
ITEM = re.compile(r"^(bixbench|compbiobench|iwc)/([^/]+)/index\.html$")
MAX_DEPTH = 4


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href")
        if tag == "a" and href:
            self.urls.add(href)


def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "Galaxy-paper-source-index/2"}), timeout=45) as res:
                return res.read(), res.headers.get("Last-Modified", "")
        except OSError:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def links_of(url, body):
    if not url.endswith((".html", "/")):
        return []
    parser = Links()
    parser.feed(body.decode("utf-8"))
    return sorted({urljoin(url, h).split("#")[0] for h in parser.urls})


def classify(relative, item_ids):
    match = ITEM.match(relative)
    if match and match[2] in item_ids.get(match[1], ()):
        return {"bixbench": "BixBench", "compbiobench": "CompBioBench", "iwc": "IWC"}[match[1]], match[2]
    long_chain = re.match(r"^iwc/long-chain/(task-\d+)/index\.html$", relative)
    if long_chain:
        return "IWC multi-step", long_chain[1]
    july6 = re.match(r"^bixbench/july6/(bix-[^/]+)/index\.html$", relative)
    if july6:
        return "BixBench July 6 archive", july6[1]
    if not relative.endswith(".html"):
        return "data", ""
    return "navigation", ""


def discover(item_ids):
    """Breadth-first crawl of same-site links from the entry pages; item pages are leaves."""
    seen, frontier, bodies = set(), [urljoin(SITE, p) for p in ENTRY], {}
    for _ in range(MAX_DEPTH):
        frontier = [u for u in frontier if u not in seen]
        seen.update(frontier)
        with ThreadPoolExecutor(max_workers=5) as pool:
            fetched = dict(zip(frontier, pool.map(fetch, frontier)))
        bodies.update(fetched)
        nxt = []
        for url, (body, _) in fetched.items():
            if classify(url.removeprefix(SITE), item_ids)[0] in ("BixBench", "CompBioBench", "IWC"):
                continue
            nxt.extend(u for u in links_of(url, body) if u.startswith(SITE) and u not in seen)
        frontier = sorted(set(nxt))
        if not frontier:
            break
    return bodies


def row(url, body, modified, item_ids):
    benchmark, item = classify(url.removeprefix(SITE), item_ids)
    targets = links_of(url, body)
    counts = {host: sum(urlsplit(h).hostname == host for h in targets)
              for host in ("usegalaxy.org", "huggingface.co", "iwc.galaxyproject.org")}
    return dict(benchmark=benchmark, item=item, url=url, retrieved_utc=str(datetime.now(timezone.utc).date()),
                last_modified=modified, bytes=str(len(body)), sha256=sha256(body).hexdigest(),
                unique_links=str(len(targets)), galaxy_links=str(counts["usegalaxy.org"]),
                hf_links=str(counts["huggingface.co"]), iwc_workflow_links=str(counts["iwc.galaxyproject.org"]))


def main():
    item_ids = {}
    for name, path in [("bixbench", "bixbench/data/results.json"), ("compbiobench", "compbiobench/data/paper_results.json"),
                       ("iwc", "iwc/data/results.json")]:
        items = json.loads((ROOT / "data/site" / path).read_bytes())["items"]
        item_ids[name] = set(items.keys() if isinstance(items, dict) else [i.get("item_id", i.get("id")) for i in items])
    target = OUT / "web_pages.csv"
    previous = {}
    if target.exists():
        with target.open(encoding="utf-8", newline="") as f:
            previous = {r["url"]: r for r in csv.DictReader(f)}
    bodies = discover(item_ids)
    linked = set(bodies)
    # Item pages come from the exports; pages catalogued earlier but no longer linked are re-fetched, not dropped.
    missing = [urljoin(SITE, f"{b}/{i}/index.html") for b, ids in item_ids.items() for i in ids]
    missing = [u for u in [*missing, *previous] if u not in bodies]
    with ThreadPoolExecutor(max_workers=5) as pool:
        bodies.update(zip(missing, pool.map(fetch, missing)))
    unlinked = sorted(u for u in bodies if u not in linked and not ITEM.match(u.removeprefix(SITE)))
    if unlinked:
        print("Catalogued but not linked from any crawled page:", *unlinked, sep="\n  ")
    rows = []
    for url, (body, modified) in bodies.items():
        new = row(url, body, modified, item_ids)
        old = previous.get(url)
        rows.append(old if old and old["sha256"] == new["sha256"] else new)
    order = {"BixBench": 0, "CompBioBench": 1, "IWC": 2, "IWC multi-step": 3, "BixBench July 6 archive": 4,
             "navigation": 5, "data": 6}
    first = {u: i for i, u in enumerate(previous)}
    rows.sort(key=lambda r: (r["url"] not in first, first.get(r["url"], 0), order[r["benchmark"]], r["url"]))
    with target.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)
    unchanged = sum(1 for r in rows if previous.get(r["url"]) is r)
    changed = sum(1 for r in rows if r["url"] in previous and previous[r["url"]] is not r)
    print(f"Catalogued {len(rows)} pages: {unchanged} unchanged since the previous catalogue, "
          f"{changed} changed, {len(rows) - unchanged - changed} newly discovered.")


if __name__ == "__main__":
    main()
