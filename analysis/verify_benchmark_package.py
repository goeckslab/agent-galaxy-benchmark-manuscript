"""Check scientific reconciliations, typography, vector objects and delivery formats offline."""
import argparse
import csv
from collections import Counter
from hashlib import sha256
import json
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from lxml import html
import numpy as np
import pandas as pd
import pdfplumber
from pdfminer.pdftypes import resolve1
from PIL import Image

from benchmark_records import BASE, FIGS, KEY, ROOT
from summary_provenance import fingerprint, rows, verify

NS = "{http://www.w3.org/2000/svg}"
PANELS = ["abcd","abc","abcde","abcd","abc","ab","ab","abcde","abcd"]
SUPPLEMENT_PAGES = len(FIGS) - 2
PT_TO_MM = 25.4 / 72


def read(folder, filename="source_data.csv"):
    return pd.read_csv(BASE/folder/"dataset"/filename)


def inspect_plate(folder, letters):
    prefix = BASE/folder/"output"/folder
    with Image.open(prefix.with_suffix(".png")) as im:
        pixel_width, pixel_height = im.size
        assert im.mode == "RGB" and all(abs(d - 450) < .1 for d in im.info["dpi"]), folder
    with pdfplumber.open(prefix.with_suffix(".pdf")) as doc:
        assert len(doc.pages) == 1
        page = doc.pages[0]
        width, height = page.width * PT_TO_MM, page.height * PT_TO_MM
        assert abs(width - 180) < .01 and height <= 185, folder
        assert abs(pixel_width - width * 450 / 25.4) < 1.1
        assert abs(pixel_height - height * 450 / 25.4) < 1.1
        assert page.chars and not page.images and (page.curves or page.rects), folder
        for ch in page.chars:
            assert min(ch["x0"],ch["top"],page.width-ch["x1"],page.height-ch["bottom"]) >= -.05, (folder,ch)
        pdf_sizes = [ch["size"] for ch in page.chars if ch["text"].strip() and ch["upright"]]
        assert min(pdf_sizes) >= 6.49 and max(pdf_sizes) <= 7.01, (folder, min(pdf_sizes), max(pdf_sizes))
        fonts = set()
        for ref in resolve1(page.page_obj.resources["Font"]).values():
            font = resolve1(ref)
            fonts.add(font["BaseFont"].name.split("+")[-1])
            descendant, = resolve1(font["DescendantFonts"])
            assert "FontFile2" in resolve1(resolve1(descendant)["FontDescriptor"]), folder
    svg = ET.parse(prefix.with_suffix(".svg")).getroot()
    assert not svg.findall(f".//{NS}image")
    assert abs(float(svg.get("width").removesuffix("pt")) * PT_TO_MM - width) < .01
    labels = svg.findall(f".//{NS}text")
    sizes = []
    found = set()
    for label in labels:
        style = label.attrib["style"]
        sizes.append(float(re.search(r"font-size:\s*([\d.]+)px",style)[1]))
        if "font-weight: 700" in style and re.fullmatch("[a-z]", label.text or ""):
            found.add(label.text)
    assert labels and set(letters) == found and min(sizes) >= 6.5 and max(sizes) <= 7, folder
    assert prefix.with_suffix(".pdf").stat().st_size < 50_000_000
    legend = (BASE/folder/"README.md").read_text(encoding="utf8").split("\n\n")[1]
    return dict(figure=folder, panels=letters, width_mm=round(width,2), height_mm=round(height,2),
                min_type_pt=min(sizes), max_type_pt=max(sizes), embedded_truetype=" | ".join(sorted(fonts)),
                pdf_raster_objects=0, svg_text_objects=len(labels), png_rgb_width=pixel_width,
                png_rgb_height=pixel_height, png_dpi=450, legend_words=len(legend.split()))


def verify_answer_votes(manifest, repeat):
    """Select strings from the run manifest before looking at their grades."""
    by_outcome = Counter()
    strings = manifest[manifest.notes.str.startswith(("benchmark=BixBench", "benchmark=CompBioBench"))]
    for (task, cond, _), runs in strings.groupby(["task_id", "track", "model"]):
        assert len(runs) == 3, (task, cond)
        bench = "BixBench" if runs.notes.iloc[0].startswith("benchmark=BixBench") else "CompBioBench"
        answers = runs.final_answer.str.strip().str.casefold()
        winners = [answer for answer, count in Counter(answers).items() if answer and count >= 2]
        outcome = "vote_abstained"
        if winners:
            winner, = winners
            grades = runs.loc[answers == winner, "correct"].unique()
            if len(grades) == 1:
                outcome = {"true": "vote_correct", "false": "vote_incorrect"}[grades[0]]
            else:
                outcome = "vote_ungraded"
        by_outcome[bench, cond, outcome] += 1
    for row in repeat[repeat.benchmark != "IWC"].itertuples():
        for field in ["vote_correct", "vote_incorrect", "vote_abstained", "vote_ungraded"]:
            assert getattr(row, field) == by_outcome[row.benchmark, row.condition, field], (row.benchmark, field)
    assert repeat[repeat.benchmark == "IWC"].vote_correct.isna().all()


def science():
    perf, interface, execution, reruns, repeats, workflow, requests, usage, drivers = FIGS
    item = read(perf,"item_scores.csv")
    primary = read(perf).query("model=='Pooled'").set_index("benchmark")
    assert not item.duplicated(KEY).any() and len(item)==3840 and primary.tasks.sum()==160
    design = read(execution).query("panel == 'design'").set_index("benchmark")
    for bench, sub in item.groupby("benchmark"):
        r = design.loc[bench]
        assert (r.tasks, r.models, r.policies, r.replicates) == tuple(
            sub[field].nunique() for field in ("task", "model", "condition", "replicate"))
        assert r.runs == r.tasks * r.models * r.policies * r.replicates == len(sub)
        assert primary.loc[bench, "runs_per_condition"] * r.policies == len(sub)
    for bench in ("BixBench","IWC"):
        sub = item[item.benchmark==bench]
        for cond,col in [("Galaxy","galaxy"),("custom code","custom_code")]:
            block = sub[sub.condition==cond]
            assert len(block)==primary.loc[bench,"runs_per_condition"]
            assert np.isclose(100*block.item_score.mean(),primary.loc[bench,col])
    official = read(perf,"official_submissions.csv").groupby("condition").official_pct
    assert tuple(official.mean().loc[["Galaxy","custom code"]])==(87,86.75) and official.size().eq(12).all()
    assert read(perf).query("benchmark=='CompBioBench'")[["lower_95","upper_95"]].isna().all().all()
    effects = read(reruns,"report_effects.csv")
    selection = read(reruns).query("panel=='selection'").groupby("benchmark").selected.sum()
    assert effects.groupby("benchmark").reruns.sum().to_dict()==selection.to_dict()=={"BixBench":19,"CompBioBench":55,"IWC":3}
    comp = effects[effects.benchmark=="CompBioBench"]
    assert comp.changed_strings.sum()==22 and comp.groupby("condition").reported_delta_pp.sum().eq(0).all()
    comp_plot = read(reruns).query("benchmark == 'CompBioBench' and panel == 'release_scores'")
    assert np.allclose(comp_plot.changed_answer_pct, 100 * comp_plot.changed_strings / comp_plot.reruns)
    fig2 = read(interface)
    display_panels = {"failure_categories": "a", "answer_selection": "b", "development_ratios": "c"}
    assert fig2.figure_panel.fillna("").equals(fig2.panel.map(display_panels).fillna(""))
    causes = fig2[fig2.panel=="current_failures"]
    assert causes.runs.sum()==133 and causes.loc[causes.classification=="UNREVIEWED","runs"].item()==7
    assert (causes.galaxy_runs.sum(),causes.custom_code_runs.sum())==(63,70)
    ledger = read(interface,"bixbench_current_failures.csv")
    assert not ledger.duplicated(KEY).any() and len(ledger) == 133
    split = ledger.groupby(["classification","condition"]).size().unstack(fill_value=0)
    assert split["Galaxy"].reindex(causes.classification).tolist()==causes.galaxy_runs.tolist()
    assert split["custom code"].reindex(causes.classification).tolist()==causes.custom_code_runs.tolist()
    resolved = ledger.audit_status.eq("Classified")
    assert ledger.failure_category.notna().equals(resolved)
    assert ledger.audit_status.eq("Unresolved audit").equals(ledger.confidence.eq("unresolved"))
    assert ledger.audit_status.eq("Awaiting review").equals(ledger.classification.eq("UNREVIEWED"))
    for category, labels in {"Task or scoring ambiguity": ["SPEC", "EVALUATOR"], "Missing validation": ["RIGOR"],
                             "Platform or harness": ["PLATFORM", "HARNESS"], "Model knowledge": ["KNOWLEDGE"]}.items():
        assert ledger.failure_category.eq(category).equals(resolved & ledger.primary_cause.isin(labels)), category
    by_category = ledger[resolved].groupby(["failure_category", "condition"]).size().unstack(fill_value=0)
    assert by_category.loc["Task or scoring ambiguity"].to_dict() == {"Galaxy": 36, "custom code": 48}
    assert by_category.loc["Missing validation"].to_dict() == {"Galaxy": 14, "custom code": 13}
    assert by_category.loc["Platform or harness"].to_dict() == {"Galaxy": 6, "custom code": 0}
    assert by_category.loc["Model knowledge"].to_dict() == {"Galaxy": 1, "custom code": 4}
    plotted = fig2.query("panel == 'failure_categories'").copy()
    group_keys = ["condition", "audit_status", "failure_category"]
    expected_counts = ledger.groupby(group_keys, dropna=False).size().sort_index()
    plotted_counts = plotted.set_index(group_keys).runs.sort_index()
    pd.testing.assert_series_equal(plotted_counts, expected_counts, check_names=False, check_dtype=False)
    totals_by_policy = plotted.condition.map(ledger.condition.value_counts())
    assert plotted.failed_runs_in_policy.eq(totals_by_policy).all()
    assert np.allclose(plotted.pct_of_incorrect, 100 * plotted.runs / totals_by_policy)
    bix = item[(item.benchmark=="BixBench")]
    assert bix.groupby("condition").item_score.apply(lambda s:(s==0).sum()).to_dict()=={"Galaxy":63,"custom code":70}
    sens = read(repeats,"sensitivity.csv").set_index("selection")
    accepted = lambda row:(round(row.galaxy*row.runs_per_condition),round(row.custom_code*row.runs_per_condition))
    assert accepted(sens.loc["Historical primary specification/scorer flag"])==(496,496)
    assert accepted(sens.loc["Pre-review grades (raw_status) for all questions"])==(523,521)
    assert accepted(sens.loc["bix-45-q1 graded by its pre-October status (raw_status)"])==(525,526)
    batches = read(reruns,"run_batches.csv")
    assert batches.runs.sum()==3840
    by_class = batches.groupby(["benchmark","batch_class"]).runs.sum()
    assert by_class[("BixBench","recovery or repeat run")]==78
    assert by_class[("CompBioBench","earlier adopted rerun (not in report)")]==52
    assert batches[batches.batch_class=="October integrity rerun (report)"].runs.sum()==77
    baseline = read(execution,"no_udt_baseline.csv").iloc[0]
    assert (baseline.accepted,baseline.tasks)==(42,50)
    tok = read(drivers)
    loops = tok[tok.panel=="loops"].set_index(["metric","condition"])
    assert loops.loc[("Agent loop steps per run","Galaxy"),"page_ratio"]==2.66
    assert loops.loc[("Cached input per loop step","Galaxy"),"page_ratio"]==2.2
    skills = tok[tok.panel=="skills"]
    assert sorted(skills.accepted.astype(int))==[122,126,135,139]
    assert np.allclose(skills.accepted_pct, 100 * skills.accepted / skills.runs)
    manifest = pd.read_csv(ROOT/"data/results_manifest.csv",keep_default_na=False,dtype=str)
    assert len(manifest)==3840 and not manifest.duplicated(["task_id","track","model","replicate"]).any()
    bix_manifest = manifest[manifest.notes.str.startswith("benchmark=BixBench")]
    assert bix_manifest.groupby("track").correct.apply(lambda s:(s=="true").sum()).to_dict()=={"Galaxy":537,"custom code":530}
    manifest_groups = ["task_id", "track", "model"]
    manifest_bix = bix_manifest.assign(passed=bix_manifest.correct.eq("true"),
                                       replicate=bix_manifest.replicate.astype(int))
    manifest_bix["other_passes"] = manifest_bix.groupby(manifest_groups).passed.transform("sum") - manifest_bix.passed.astype(int)
    independent = manifest_bix.loc[~manifest_bix.passed].rename(columns={"task_id": "task", "track": "condition"})
    observed = ledger.merge(independent[["task", "condition", "model", "replicate", "other_passes"]],
                            on=["task", "condition", "model", "replicate"], how="outer", validate="one_to_one")
    assert observed.other_replicates_correct.eq(observed.other_passes).all()
    by_group = observed.assign(another_pass=observed.other_passes.gt(0)).groupby(group_keys, dropna=False).another_pass.sum()
    pd.testing.assert_series_equal(plotted.set_index(group_keys).runs_with_another_pass.sort_index(),
                                   by_group.sort_index(), check_names=False, check_dtype=False)
    pooled = read(perf).query("model=='Pooled'").set_index("benchmark")
    assert round(pooled.loc["BixBench","lower_95"],1)==-1.5 and round(pooled.loc["BixBench","upper_95"],1)==4.2
    assert round(pooled.loc["IWC","lower_95"],1)==.8 and round(pooled.loc["IWC","upper_95"],1)==7.3
    classes = read(requests).groupby("failure_class").requests.sum()
    request_rows = read(requests)
    assert np.allclose(request_rows.class_pct, 100 * request_rows.requests / request_rows.benchmark_failures)
    fig2_counts = fig2[fig2.panel=="request_classes"].set_index("failure_class").requests
    assert classes.sum()==7098 and fig2_counts.reindex(classes.index).eq(classes).all()
    stages = fig2[fig2.panel=="optimization"].set_index("stage")
    obs = fig2[fig2.panel=="replicates"].groupby("stage")
    assert obs.size().reindex(stages.index).eq(stages.replicates).all()
    for field in ("total_tokens","model_requests","wait_calls"):
        name = "mean_tokens" if field=="total_tokens" else "mean_"+field
        assert np.allclose(obs[field].mean().reindex(stages.index), stages[name],equal_nan=True)
    # The all-model stage on page 18 used the October 12 snapshot, before the DeepSeek reruns.
    timeline = fig2.query("panel == 'development_ratios'").set_index(["model", "slug"]).sort_index()
    archived = pd.read_csv(ROOT / "data/site_token_totals.csv").query("benchmark == 'BixBench-Verified-50'")
    totals = archived.pivot(index="model", columns="track", values="total_tokens")
    history = read(usage, "historical_rounds.csv")
    history = history[~history.slug.isin(["round2", "round2-sol"])].set_index(["model", "slug"])
    published = totals["Galaxy"].div(totals["custom code"]).rename("ratio").reset_index()
    published["slug"] = "mcp_execution"
    expected = pd.concat([history.ratio, published.set_index(["model", "slug"]).ratio]).sort_index()
    pd.testing.assert_series_equal(timeline.ratio, expected)
    assert len(timeline) == 9 and timeline.groupby(level="model").size().sort_values().tolist() == [1, 1, 3, 4]
    assert set(timeline.index[timeline.evidence.eq("author estimate")]) == {("GPT-5.5", "baseline"), ("GPT-5.5", "round1")}
    measured = timeline[timeline.evidence.eq("reported token totals")]
    assert np.allclose(measured.ratio, measured.galaxy_tokens_m / measured.custom_code_tokens_m)
    assert timeline.index.is_unique and round(timeline.loc[("DeepSeek V4 Pro", "mcp_execution"), "ratio"], 2) == 3.67
    for slug, stage in [("mcp_execution", "website_galaxy"), ("round3a", "mcp_v2"), ("round3b", "long_wait")]:
        assert round(timeline.loc[("GPT-5.6 Sol", slug), "ratio"], 2) == round(stages.loc[stage, "galaxy_over_open_ended"], 2)
    sensitivity = read(interface,"optimization_key_sensitivity.csv")
    assert sensitivity.passed.sum()==137 and sensitivity.pass_with_updated_phykit_key.sum()==140
    check = read(FIGS[2],"workflow_check.csv").iloc[0]
    assert (check.run_genes,check.reference_genes,check.shared_genes,check.shared_significant)==(2526,7127,2526,12)
    routes = read(execution).query("panel == 'routes'")
    assert np.allclose(routes.runs_pct, 100 * routes.runs / routes.model_runs)
    repeat_source = read(repeats)
    repeat = repeat_source[repeat_source.panel == "repeatability"]
    assert repeat[["zero","one","two","three"]].sum(axis=1).eq(repeat.groups).all()
    assert np.allclose((repeat.one+2*repeat.two+3*repeat.three)/repeat.runs_per_condition,repeat.single)
    for row in repeat.itertuples():
        block = item[(item.benchmark == row.benchmark) & (item.condition == row.condition)]
        passing = block.item_score.ge(.99).groupby([block.task, block.model]).sum()
        assert len(passing) == row.groups and np.isclose(passing.ge(2).mean(), row.majority)
        assert np.isclose(passing.ge(1).mean(), row.any_correct)
        assert np.isclose(block.item_score.ge(.99).mean(), row.single)
        for field in ("single", "majority", "any_correct"):
            assert np.isclose(getattr(row, field + "_pct"), 100 * getattr(row, field))
        if row.benchmark != "IWC":
            for field in ("vote_correct", "vote_incorrect", "vote_abstained"):
                assert np.isclose(getattr(row, field + "_pct"), 100 * getattr(row, field) / row.groups)
    verify_answer_votes(manifest, repeat)
    keys = ["benchmark", "condition"]
    fields = ["groups", "runs_per_condition", "single_pct", "majority_pct", "any_correct_pct"]
    selection = fig2.query("panel == 'answer_selection'").set_index(keys)[fields].sort_index()
    pd.testing.assert_frame_equal(selection, repeat.set_index(keys)[fields].sort_index())
    case = repeat_source.query("panel == 'promoter'").iloc[0]
    seq = json.loads((BASE/"sources/hg38_promoter_sequence.json").read_bytes())
    dna = seq["dna"].upper()
    assert (case.interval_start, case.interval_end, case.bases) == (seq["start"] + 1, seq["end"], len(dna))
    assert case.gc_bases == dna.count("G") + dna.count("C")
    assert np.isclose(case.gc_fraction, case.gc_bases / len(dna)) and case.reported_fraction == round(case.gc_fraction, 2)
    key = (f"{case.chromosome.removeprefix('chr')};{case.interval_start:.0f};{case.interval_end:.0f};"
           f"{case.strand};{case.bases:.0f};{case.gc_bases:.0f};{case.reported_fraction:.2f}")
    answers = manifest.loc[manifest.task_id == case.task, "final_answer"]
    assert (case.answers_checked, case.answers_matching) == (len(answers), answers.eq(key).sum())
    totals = read(usage).query("panel=='main_runs' and model=='Pooled'")
    assert totals.missing_usage_Galaxy.sum()==1
    assert np.allclose(totals.ratio,totals.total_tokens_Galaxy/totals.total_tokens_custom_code)
    assert np.allclose(totals.galaxy_token_change_pct, 100 * (totals.ratio - 1))
    iwc = read(workflow)
    runs = iwc[iwc.panel=="individual_run"]
    assert len(runs)==240 and not runs.duplicated(KEY).any()
    reference_scores = item[item.benchmark=="IWC"].set_index(KEY).item_score
    by_workflow = reference_scores.groupby(["task","condition"]).mean()
    shown = iwc.query("panel == 'workflow_summary'").set_index(["task", "condition"]).mean_agreement_pct
    assert np.allclose(shown.reindex(by_workflow.index), 100 * by_workflow)
    assert np.allclose(runs.set_index(KEY).item_score.reindex(reference_scores.index),reference_scores,rtol=1e-11,atol=0)
    strata = np.select([runs.item_score==1,runs.item_score>=.99,runs.item_score>=.9,runs.item_score>0],
                       ["exact","near","high","partial"],default="zero")
    assert (runs.score_band==strata).all()
    assert len(read(workflow,"score_explanations.csv"))==runs.item_score.lt(1).sum()==98


def delivery():
    with pdfplumber.open(BASE/"supplementary_figures.pdf") as doc:
        assert len(doc.pages)==SUPPLEMENT_PAGES
        for i,page in enumerate(doc.pages,1):
            txt = " ".join(page.extract_text().split())
            assert f"SupplementaryFigure{i}" in txt.replace(" ","") and not page.images, i
            assert len(page.chars)>700 and page.curves+page.rects, i
            margins = [min(ch["top"] for ch in page.chars),
                       page.height - max(ch["bottom"] for ch in page.chars)]
            assert all(6 < m * PT_TO_MM < 10 for m in margins), (i, margins)
    article = (ROOT/"manuscript/brief-communication.qmd").read_text(encoding="utf8")
    for folder in FIGS[:2]:
        heading,legend,*_=(BASE/folder/"README.md").read_text(encoding="utf8").split("\n\n")
        title=heading.split(". ",1)[1]
        assert (title+". "+legend) in " ".join(article.split()), folder


def rendered_manuscript():
    out = ROOT/"manuscript/_output"
    tree = html.parse(str(out/"index.html"))
    pictures = tree.xpath('//img[starts-with(@src,"data:image/svg+xml")]')
    assert len(pictures)==2 and all(pic.get("alt") for pic in pictures)
    with ZipFile(out/"index.docx") as archive:
        hashes = {sha256(archive.read(p)).digest() for p in archive.namelist() if p.startswith("word/media/")}
        for folder in FIGS[:2]:
            assert sha256((BASE/folder/"output"/f"{folder}.png").read_bytes()).digest() in hashes
    with pdfplumber.open(out/"index.pdf") as doc:
        texts = [" ".join(page.extract_text().split()) for page in doc.pages]
        for phrase in ("Paired experimental design","Consensus and validation across benchmarks"):
            pages = [page for page,txt in zip(doc.pages,texts) if phrase in txt]
            assert len(pages)==1 and not pages[0].images, phrase


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--without-inventory",action="store_true",help="QA before recording a new output inventory")
    parser.add_argument("--write-artwork-checks",action="store_true",help="write the measured plate characteristics")
    parser.add_argument("--with-manuscript",action="store_true",help="also inspect the three Quarto outputs")
    args=parser.parse_args()
    verify()
    report = [inspect_plate(f,p) for f,p in zip(FIGS,PANELS,strict=True)]
    if args.write_artwork_checks:
        with (BASE/"artwork_checks.csv").open("w",newline="",encoding="utf8") as out:
            writer=csv.DictWriter(out,fieldnames=report[0],lineterminator="\n")
            writer.writeheader()
            writer.writerows(report)
    else:
        stored = pd.read_csv(BASE/"artwork_checks.csv")
        pd.testing.assert_frame_equal(stored,pd.DataFrame(report),check_dtype=False)
    for file in BASE.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)",file.read_text(encoding="utf8")):
            if ":" not in link and not link.startswith("#"):
                assert (file.parent/link.split("#")[0]).exists(), (file,link)
    registry=pd.read_csv(ROOT/"figures/figures.csv").set_index("figure_id")
    for folder in FIGS:
        assert (ROOT/registry.loc[folder,"source_data"]).exists() and (ROOT/registry.loc[folder,"script"]).exists()
    science()
    delivery()
    if args.with_manuscript:
        rendered_manuscript()
    if not args.without_inventory:
        for row in rows(BASE/"artifact_manifest.csv"):
            assert fingerprint(ROOT/row["path"],row["hash_policy"]=="LF text")==row["sha256"],row["path"]
    print(f"Verified {len(FIGS)} 180-mm vector plates, embedded fonts, editable SVGs, RGB PNGs, "
          f"{SUPPLEMENT_PAGES} supplementary pages, the results manifest, source data and numerical checks.")


if __name__=="__main__":
    main()
