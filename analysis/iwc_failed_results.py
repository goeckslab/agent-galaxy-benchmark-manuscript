"""IWC multi-step tasks: why each failed result failed, by condition, from the scorer's recorded reasons.

Every failed result gets one primary reason by the priority order P1-P7 below (a missing file makes a
result 0 whatever else is wrong, a mis-shaped file stops its content being judged, and so on), and an
alternative order A1-A4 for comparison. The scorer records symptoms, not causes: most failed results
carry only "content below the pass mark".

Input : data/site/iwc/long-chain/data/results.json (read-only)
Output: data/error_taxonomy/iwc_multistep_reasons.csv        one row per failed result (573 rows)
        data/error_taxonomy/iwc_multistep_reason_counts.csv  long-format count tables
Run from the repository root:  python analysis/iwc_failed_results.py [output directory]
"""
import json, os, re, sys, collections
import pandas as pd

S = sys.argv[1] if len(sys.argv) > 1 else "data/error_taxonomy"
os.makedirs(S, exist_ok=True)
SRC = "data/site/iwc/long-chain/data/results.json"
d = json.load(open(SRC, encoding="utf-8"))

MODEL = {"luna": "GPT-5.6 Luna", "sol": "GPT-5.6 Sol", "ds": "DeepSeek V4 Pro"}
COND = {"galaxy": "Galaxy", "open": "custom code"}
KINDS = ["content", "member", "check", "list", "instruction", "format", "method"]
UNREADABLE = "Required content missing or unreadable"

# Primary-reason priority (first match wins).
P1 = "1 Required file missing"
P2 = "2 Output format or naming"
P3 = "3 Other output instruction not followed"
P4 = "4 Required content missing or unreadable"
P5 = "5 Stated method or setting not followed"
P6 = "6 Content below the pass mark"
P7 = "7 Only a member, check or gene-list minimum missed"
PRIMARY = [P1, P2, P3, P4, P5, P6, P7]
# Alternative order suggested in the brief (missing or unreadable first).
A1 = "A1 Required file or content missing or unreadable"
A2 = "A2 Output format or naming"
A3 = "A3 Instruction or method not followed"
A4 = "A4 Content below the pass mark (incl. member, check, list)"
ALT = [A1, A2, A3, A4]

# Symptom-level mapping to the paper's categories (what the scorer saw, not the cause).
SYMPTOM = {
    P1: ("Execution environment", "Required output missing or unreadable"),
    P2: ("Execution environment", "Output delivered in the wrong format or under the wrong name"),
    P3: ("Execution environment", "Output delivered in the wrong format or under the wrong name"),
    P4: ("Execution environment", "Required output missing or unreadable"),
    P6: ("Unclear", "Content differs from the reference; cause not in the scorer record"),
    P7: ("Unclear", "Content differs from the reference; cause not in the scorer record"),
}
# Method reasons: a named setting -> wrong parameter; a stated rule or formula -> instruction misread.
METHOD_PARAM_PREFIX = (
    "Recorded STAR settings contradict the task",
    "fastp trimmed with adapter sequences",
    "Supplementary alignments are not soft-clipped",
    "Peptides carry RIA cluster groups",
)


def method_subcategory(summaries):
    if all(s.startswith(METHOD_PARAM_PREFIX) for s in summaries):
        return "Wrong parameter or threshold"
    if not any(s.startswith(METHOD_PARAM_PREFIX) for s in summaries):
        return "Task instruction misread"
    return "Wrong parameter or threshold"  # mixed: none occur in this data set (asserted below)


rows = []
n_results = collections.Counter()
n_runs = collections.Counter()
for it in d["items"]:
    for r in it["runs"]:
        cond = COND[r["condition"]]
        n_runs[cond] += 1
        for idx, res in enumerate(r["score"]["results"], start=1):
            n_results[cond] += 1
            if res["passed"]:
                assert not res["reasons"]
                continue
            reasons = res["reasons"]
            assert reasons, "failed result without reasons"
            kinds = [x["kind"] for x in reasons]
            assert set(kinds) <= set(KINDS), kinds
            cnt = collections.Counter(kinds)
            instr = [x["summary"] for x in reasons if x["kind"] == "instruction"]
            file_missing = [s for s in instr if s.startswith("Required file is missing")]
            other_instr = [s for s in instr if not s.startswith("Required file is missing")]
            checks = [c for x in reasons for c in x.get("checks", [])]
            unreadable = [c for c in checks if c["kind"] == UNREADABLE and c["value"] == 0]
            unreadable_nonzero = [c for c in checks if c["kind"] == UNREADABLE and c["value"] != 0]
            meth = [x["summary"] for x in reasons if x["kind"] == "method"]
            members = [m["value"] for x in reasons if x["kind"] == "member" for m in x["members"]]
            if file_missing:
                prim = P1
            elif cnt["format"]:
                prim = P2
            elif other_instr:
                prim = P3
            elif unreadable:
                prim = P4
            elif cnt["method"]:
                prim = P5
            elif cnt["content"]:
                prim = P6
            else:
                prim = P7
            if file_missing or unreadable:
                alt = A1
            elif cnt["format"]:
                alt = A2
            elif cnt["instruction"] or cnt["method"]:
                alt = A3
            else:
                alt = A4
            if prim == P5:
                cat, sub = "Knowledge", method_subcategory(meth)
                assert all(s.startswith(METHOD_PARAM_PREFIX) for s in meth) or not any(s.startswith(METHOD_PARAM_PREFIX) for s in meth)
            else:
                cat, sub = SYMPTOM[prim]
            summaries = []
            for x in reasons:
                s = x["summary"]
                if s.startswith("Required file is missing"):
                    s = "Required file is missing"
                if s not in summaries:
                    summaries.append(s)
            rows.append(dict(
                task=it["id"], task_title=it["title"], model=MODEL[r["model"]], condition=cond, replicate=r["replicate"],
                result_position=idx,
                result_id="+".join(str(int(x)) for x in re.findall(r"(?:^|\+)(\d{2})_", res["name"])),
                result_name=res["name"], result_score=round(res["score"], 6),
                score_at_or_above_pass_mark=bool(res["score"] >= d["pass_mark"]),
                n_reasons=len(reasons), reason_kinds=";".join(k for k in KINDS if cnt[k]),
                **{"n_" + k: cnt[k] for k in KINDS},
                n_files_reported_missing=len(file_missing),
                has_unreadable_content_check=bool(unreadable),
                unreadable_check_nonzero=bool(unreadable_nonzero),
                n_members_listed=len(members), n_members_scoring_zero=sum(1 for v in members if v == 0),
                primary_reason=prim, primary_reason_alt_order=alt,
                symptom_category=cat, symptom_subcategory=sub,
                reason_summaries=" | ".join(summaries),
            ))

f = pd.DataFrame(rows)
assert len(f) == 573, len(f)
assert dict(n_results) == {"Galaxy": 783, "custom code": 783}, n_results
assert f.groupby("condition").size().to_dict() == {"Galaxy": 253, "custom code": 320}
f.to_csv(os.path.join(S, "iwc_multistep_reasons.csv"), index=False, encoding="utf-8", lineterminator="\n")

out = []
long_rows = []


def to_md(df, index=True):
    def fmt(v):
        if isinstance(v, tuple):
            return " / ".join(map(str, v))
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    cols = [fmt(c) for c in df.columns]
    if index:
        names = [n for n in df.index.names if n]
        head = [" / ".join(map(str, names))] + cols
    else:
        head = cols
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for idx, row in df.iterrows():
        cells = ([fmt(idx)] if index else []) + [fmt(v) for v in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def md(df, title, index=True):
    out.append("\n### " + title + "\n")
    out.append(to_md(df, index=index))


def add_long(table, df):
    for idx, row in df.iterrows():
        for col, val in row.items():
            long_rows.append(dict(table=table, row=idx if not isinstance(idx, tuple) else " / ".join(map(str, idx)), column=col, n=int(val)))


CONDS = ["Galaxy", "custom code"]
# T0 totals
t0 = pd.DataFrame({"runs": pd.Series(n_runs), "scored results": pd.Series(n_results), "failed results": f.groupby("condition").size()}).loc[CONDS]
t0["failed, score below 0.80"] = f[~f.score_at_or_above_pass_mark].groupby("condition").size()
t0["failed, score 0.80 or above"] = f[f.score_at_or_above_pass_mark].groupby("condition").size()
t0["failed, score exactly 0"] = f[f.result_score == 0].groupby("condition").size()
md(t0.T, "T0. Totals")
add_long("T0 totals", t0.T)

# T1 by kind: failed results carrying at least one reason of that kind, and number of reason entries
t1 = pd.DataFrame({(c, "failed results with this reason"): [(f[(f.condition == c)]["n_" + k] > 0).sum() for k in KINDS] for c in CONDS}, index=KINDS)
for c in CONDS:
    t1[(c, "reason entries")] = [f[(f.condition == c)]["n_" + k].sum() for k in KINDS]
t1 = t1[[(c, m) for m in ("failed results with this reason", "reason entries") for c in CONDS]]
t1.columns = ["%s: %s" % (c, m) for c, m in t1.columns]
md(t1, "T1. Reason kinds (a failed result can carry several; columns do not add to 253 / 320)")
add_long("T1 kinds", t1)

# T1b kind combinations
t1b = f.groupby(["reason_kinds", "condition"]).size().unstack(fill_value=0).reindex(columns=CONDS, fill_value=0)
t1b["both"] = t1b.sum(axis=1)
t1b = t1b.sort_values("both", ascending=False)
md(t1b, "T1b. Combinations of reason kinds per failed result")
add_long("T1b kind combinations", t1b)

# T2 primary reason by condition
t2 = f.groupby(["primary_reason", "condition"]).size().unstack(fill_value=0).reindex(index=PRIMARY, columns=CONDS, fill_value=0)
t2.loc["Total"] = t2.sum()
t2["Galaxy % of failed"] = (100 * t2["Galaxy"] / 253).round(1)
t2["custom code % of failed"] = (100 * t2["custom code"] / 320).round(1)
md(t2, "T2. Primary reason by condition (each failed result counted once)")
add_long("T2 primary by condition", t2[CONDS])

t2a = f.groupby(["primary_reason_alt_order", "condition"]).size().unstack(fill_value=0).reindex(index=ALT, columns=CONDS, fill_value=0)
t2a.loc["Total"] = t2a.sum()
md(t2a, "T2a. Same, under the alternative order (missing or unreadable first)")
add_long("T2a alt-order primary by condition", t2a)

moved = f[(f.primary_reason.isin([P2, P3])) & (f.primary_reason_alt_order == A1)]
out.append("\nResults that move between T2 and T2a (format or instruction reason plus an unreadable-content check, no file reported missing): "
           + str(moved.groupby("condition").size().reindex(CONDS, fill_value=0).to_dict()))

# T3 primary reason by task and condition
t3 = f.groupby(["task", "condition", "primary_reason"]).size().unstack(fill_value=0).reindex(columns=PRIMARY, fill_value=0)
t3["failed"] = t3.sum(axis=1)
tot = pd.Series({(it["id"], COND[c]): sum(len(r["score"]["results"]) for r in it["runs"] if r["condition"] == c) for it in d["items"] for c in COND})
t3["scored"] = [tot[i] for i in t3.index]
t3.columns = [c.split(" ", 1)[0] if c in PRIMARY else c for c in t3.columns]
md(t3, "T3. Primary reason by task and condition (columns 1-7 = primary reasons in T2 order)")
add_long("T3 primary by task and condition", t3)

# T4 primary reason by model and condition
t4 = f.groupby(["model", "condition", "primary_reason"]).size().unstack(fill_value=0).reindex(columns=PRIMARY, fill_value=0)
t4 = t4.reindex([(m, c) for m in MODEL.values() for c in CONDS])
t4["failed"] = t4.sum(axis=1)
totm = collections.Counter()
for it in d["items"]:
    for r in it["runs"]:
        totm[(MODEL[r["model"]], COND[r["condition"]])] += len(r["score"]["results"])
t4["scored"] = [totm[i] for i in t4.index]
t4.columns = [c.split(" ", 1)[0] if c in PRIMARY else c for c in t4.columns]
md(t4, "T4. Primary reason by model and condition")
add_long("T4 primary by model and condition", t4)

# T5 symptom-level categories
t5 = f.groupby(["symptom_category", "symptom_subcategory", "condition"]).size().unstack(fill_value=0).reindex(columns=CONDS, fill_value=0)
t5.loc[("Total", ""), :] = t5.sum()
t5 = t5.astype(int)
md(t5, "T5. Symptom-level category of the primary reason (what the scorer recorded, not the cause)")
add_long("T5 symptom category", t5)

# T6 method summaries
meth = []
for it in d["items"]:
    for r in it["runs"]:
        for idx, res in enumerate(r["score"]["results"], start=1):
            for x in res["reasons"]:
                if x["kind"] == "method":
                    s = x["summary"]
                    key = s.split(" (")[0] if s.startswith(("Supplementary", "Recorded STAR")) else s.split(":")[0]
                    if s.startswith("Recorded STAR"):
                        key = s.split(" in S01")[0]
                    meth.append(dict(task=it["id"], condition=COND[r["condition"]], model=MODEL[r["model"]], replicate=r["replicate"], result=idx, summary=key))
m = pd.DataFrame(meth)
t6 = m.groupby(["task", "summary", "condition"]).size().unstack(fill_value=0).reindex(columns=CONDS, fill_value=0)
md(t6, "T6. Method reasons (38 failed results) by stated deviation")
add_long("T6 method reasons", t6)

# T7 non-file instruction and format summaries
oth = []
for it in d["items"]:
    for r in it["runs"]:
        for idx, res in enumerate(r["score"]["results"], start=1):
            seen = set()
            for x in res["reasons"]:
                if x["kind"] in ("instruction", "format"):
                    s = x["summary"]
                    if s.startswith("Required file is missing"):
                        s = "Required file is missing"
                    if s.startswith("Membership identifiers do not literally match"):
                        s = "Membership identifiers do not literally match the submitted peak identifiers"
                    if s.startswith("Named stored field is missing"):
                        s = "Named stored field is missing (raw/X, raw/var)"
                    if (x["kind"], s) in seen:
                        continue
                    seen.add((x["kind"], s))
                    oth.append(dict(kind=x["kind"], summary=s, condition=COND[r["condition"]], task=it["id"]))
o = pd.DataFrame(oth)
t7 = o.groupby(["kind", "summary", "condition"]).size().unstack(fill_value=0).reindex(columns=CONDS, fill_value=0)
t7["tasks"] = o.groupby(["kind", "summary"])["task"].agg(lambda s: ", ".join(sorted(set(x.replace("task-", "") for x in s))))
md(t7, "T7. Instruction and format reasons: failed results carrying each statement")
add_long("T7 instruction and format statements", t7[CONDS])

# T8 content check kinds on failed results (number of failed results where the check kind is listed)
ck = []
for it in d["items"]:
    for r in it["runs"]:
        for res in r["score"]["results"]:
            if res["passed"]:
                continue
            kinds = set()
            for x in res["reasons"]:
                for c in x.get("checks", []):
                    kinds.add((x["kind"], c["kind"]))
            for k in kinds:
                ck.append(dict(reason_kind=k[0], check=k[1], condition=COND[r["condition"]]))
c = pd.DataFrame(ck)
t8 = c.groupby(["reason_kind", "check", "condition"]).size().unstack(fill_value=0).reindex(columns=CONDS, fill_value=0)
md(t8, "T8. Checks listed under content and check reasons: failed results listing each check")
add_long("T8 checks listed", t8)

# extra facts
out.append("\n### Extra facts\n")
out.append("- Failed results with a zero-valued '%s' check: %s" % (UNREADABLE, f[f.has_unreadable_content_check].groupby("condition").size().reindex(CONDS, fill_value=0).to_dict()))
out.append("- Failed results where that check is listed with a non-zero value: %s (all: %s)" % (
    f[f.unreadable_check_nonzero].groupby("condition").size().reindex(CONDS, fill_value=0).to_dict(),
    sorted(set(f[f.unreadable_check_nonzero].task + " " + f[f.unreadable_check_nonzero].result_name))))
out.append("- Failed results reporting at least one missing file: %s ; files reported missing: %s" % (
    f[f.n_files_reported_missing > 0].groupby("condition").size().reindex(CONDS, fill_value=0).to_dict(),
    f.groupby("condition")["n_files_reported_missing"].sum().reindex(CONDS, fill_value=0).to_dict()))
out.append("- Failed results with a member reason in which every listed member scores 0: %s ; some but not all: %s" % (
    f[(f.n_members_listed > 0) & (f.n_members_listed == f.n_members_scoring_zero)].groupby("condition").size().reindex(CONDS, fill_value=0).to_dict(),
    f[(f.n_members_scoring_zero > 0) & (f.n_members_listed > f.n_members_scoring_zero)].groupby("condition").size().reindex(CONDS, fill_value=0).to_dict()))
out.append("- Minimums attached to 'check' reasons: %s" % dict(collections.Counter(x["minimum"] for it in d["items"] for r in it["runs"] for res in r["score"]["results"] for x in res["reasons"] if x["kind"] == "check")))
out.append("- Runs with at least one failed result: %s of 90 per condition" % f.groupby("condition").apply(lambda g: g.groupby(["task", "model", "replicate"]).ngroups).reindex(CONDS).to_dict())

pd.DataFrame(long_rows).to_csv(os.path.join(S, "iwc_multistep_reason_counts.csv"), index=False, encoding="utf-8",
                                lineterminator="\n")
print("\n".join(out))
