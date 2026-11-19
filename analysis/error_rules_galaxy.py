"""Rule-based classifier for failed Galaxy MCP tool calls in the Galaxy runs.

Pure standard library, no I/O. Rules are ordered and deterministic.

Entry point:
    classify_mcp(tool, call_status, result, call_error, text="") -> str | None

    tool        MCP tool name (item["tool"]).
    call_status item["status"] ("completed" or "failed").
    result      the parsed JSON object of the tool's text result, or None if it did not parse.
    call_error  item["error"] as a string ("" or "None" when absent); a dict is accepted and its "message" used.
    text        optional: the raw text content of the result (needed only when result is None,
                because interface exceptions such as "Error executing tool ..." arrive as plain text,
                with call_error empty).

Returns one label from MCP_LABELS, or None when the call is not an error.
Each label belongs to one stage (MCP_STAGE) and one severity (MCP_SEVERITY):
    "error"        the call failed: no job ran, the job failed, or the interface could not finish;
    "warning"      the call returned, but the interface flagged a discrepancy or a not-ready dataset;
    "out_of_scope" a call to a connector that is not the benchmark's Galaxy interface.
"""
import json
import re

# ---------------------------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------------------------
MCP_LABELS = [
    # Request rejected before a job ran
    ("Tool lookup failed for lack of history context",
     "inspect_galaxy_tool refused because no history was given or the given history was unusable"),
    ("Tool ID not found",
     "Galaxy could not find or route the requested tool ID (guessed, short, wrong version, or unroutable ID)"),
    ("Parameter rejected: nested-key structure",
     "Galaxy rejected the parameter tree shape (invalid key structure, conflicting flat and nested keys, invalid conditional case)"),
    ("Parameter rejected: value or datatype",
     "Galaxy rejected a parameter value, a missing required value, or an input of the wrong datatype or collection type"),
    ("Parameters did not resolve as requested (not submitted)",
     "the interface's pre-submission check found requested parameters dropped or changed by Galaxy, and did not submit"),
    ("Dataset, history or job ID problem",
     "a wrong, truncated, undecodable, foreign or inaccessible dataset, collection, history or job ID"),
    ("UDT definition rejected",
     "the user-defined tool representation failed the interface's or Galaxy's schema checks"),
    ("Upload or staging failed",
     "uploading or staging a workspace file into Galaxy failed (unknown datatype, upload dataset error, wrong upload route)"),
    ("Interface rejected the call arguments",
     "the MCP interface rejected malformed or missing arguments before contacting Galaxy"),
    ("Archive inspection rejected",
     "inspect_archive_inventory was called on a non-archive or a missing file"),
    ("Server, transport or rate-limit problem",
     "Galaxy returned HTTP 429 or 5xx, an uncaught server exception, or the connection dropped"),
    ("MCP call failed or timed out",
     "the MCP call itself failed (transport closed, call timeout, server not ready) or the job wait timed out"),
    # Job ran and failed
    ("Tool runtime error with diagnostic",
     "an installed Galaxy tool's command ran and failed, with stderr or a job message"),
    ("UDT script runtime error with diagnostic",
     "the agent's own UDT command ran and failed, with stderr or a job message"),
    ("Job failed before execution or without diagnostic",
     "an installed tool's job errored before its command ran, or with no stderr beyond an exit code"),
    ("UDT job failed before its command ran",
     "a UDT job errored before its command line was rendered, with no stderr"),
    ("Missing software dependency in job",
     "the job's container or environment lacked a program, module or library (mostly UDT containers)"),
    ("Input format, compression or index problem",
     "the job failed because an input was not in the expected format, compression, sort order or index"),
    ("Job hit memory, disk or time limit",
     "the job was killed for memory (OOM), ran out of disk, or hit the scheduler time limit"),
    ("Job paused",
     "the job was paused by Galaxy (typically because an upstream input failed)"),
    ("Job deleted or cancelled",
     "the job was deleted or cancelled before completing"),
    ("Output dataset failed metadata",
     "the job finished but an output dataset entered the failed_metadata state"),
    ("Output collection lookup failed after the job",
     "the job finished but the interface could not look up the output collection (interface-side fault)"),
    ("Other",
     "a failure that matched none of the rules above"),
    # Warnings (the call returned; not counted as errors)
    ("Job ran with parameters that differ from the request",
     "warning: submitted job ran, but resolved parameters differ from or omit requested ones"),
    ("Job ran on inputs that differ from the request",
     "warning: submitted job ran, but resolved input datasets differ from the intended ones"),
    ("Peek at a dataset that is not ready or failed",
     "warning: peek_galaxy_dataset on a dataset in error, failed_metadata or a transient state"),
    ("Dataset is outside the stated history",
     "warning: peek_galaxy_dataset returned content but the dataset belongs to another history"),
    # Out of scope
    ("Other connector call failed (out of scope)",
     "a failed call to a connector other than the benchmark's Galaxy interface (GitHub, Hugging Face, Galaxy apps)"),
]

MCP_STAGE = {
    "Tool lookup failed for lack of history context": "Request rejected before a job ran",
    "Tool ID not found": "Request rejected before a job ran",
    "Parameter rejected: nested-key structure": "Request rejected before a job ran",
    "Parameter rejected: value or datatype": "Request rejected before a job ran",
    "Parameters did not resolve as requested (not submitted)": "Request rejected before a job ran",
    "Dataset, history or job ID problem": "Request rejected before a job ran",
    "UDT definition rejected": "Request rejected before a job ran",
    "Upload or staging failed": "Request rejected before a job ran",
    "Interface rejected the call arguments": "Request rejected before a job ran",
    "Archive inspection rejected": "Request rejected before a job ran",
    "Server, transport or rate-limit problem": "Server or transport",
    "MCP call failed or timed out": "Server or transport",
    "Tool runtime error with diagnostic": "Job failed",
    "UDT script runtime error with diagnostic": "Job failed",
    "Job failed before execution or without diagnostic": "Job failed",
    "UDT job failed before its command ran": "Job failed",
    "Missing software dependency in job": "Job failed",
    "Input format, compression or index problem": "Job failed",
    "Job hit memory, disk or time limit": "Job failed",
    "Job paused": "Job failed",
    "Job deleted or cancelled": "Job failed",
    "Output dataset failed metadata": "Job finished, output failed",
    "Output collection lookup failed after the job": "Job finished, output failed",
    "Other": "Other",
    "Job ran with parameters that differ from the request": "Warning",
    "Job ran on inputs that differ from the request": "Warning",
    "Peek at a dataset that is not ready or failed": "Warning",
    "Dataset is outside the stated history": "Warning",
    "Other connector call failed (out of scope)": "Out of scope",
}

MCP_SEVERITY = {lab: ("warning" if MCP_STAGE[lab] == "Warning" else
                      "out_of_scope" if MCP_STAGE[lab] == "Out of scope" else "error")
                for lab, _ in MCP_LABELS}

# ---------------------------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------------------------
_RX_SERVER = re.compile(
    r"status code: (429|5\d\d)\b|error (429|5\d\d)\b|with status (429|5\d\d)\b|too many requests|internal server error"
    r"|uncaught exception|connection aborted|remotedisconnected|bad gateway|gateway time-?out|service unavailable"
    r"|tus server failed", re.I)
_RX_TRANSPORT = re.compile(r"transport closed|timed out awaiting|was not ready|tool call failed|connection reset", re.I)
_RX_STRUCT = re.compile(r"invalid key structure|received conflicting value|selected case is unavailable"
                        r"|invalid dataset id \{", re.I)
_RX_ID = re.compile(
    r"wrong id \(|unable to decode|invalid id length|not owned by user|is not accessible by user|history not found"
    r"|invalid dataset id|invalid input id|is not a datasetinstance|invalid history id|invalid dataset id"
    r"|invalid galaxy job id|rejected job id|history dataset association not found|does not belong to the selected history"
    r"|previously selected dataset has been deleted|previously selected dataset has entered an unusable state",
    re.I)
_RX_TOOL_NOT_FOUND = re.compile(r"tool not found|could not find tool with id|kwd not provided", re.I)
_RX_UPLOAD = re.compile(r"__data_fetch__|no data was entered in the upload form|requested extension .{0,60} unknown, cannot upload"
                        r"|cannot upload dataset", re.I)
_RX_UDT_REPR = re.compile(r"udt representation|representation\b.{0,80}(field required|valid dictionary|valid string)"
                          r"|'representation'", re.I)
_RX_ARCHIVE = re.compile(r"supported archive formats|archive file does not exist|archive dataset|while decompressing", re.I)
_RX_ARGS = re.compile(
    r"validation errors? for \w+arguments|job_ids may contain at most|job_ids must contain at least"
    r"|already present in tool_inputs|has unsupported keys|path must resolve inside|name must be a basename"
    r"|workspace file does not exist|provide exactly one of|workspace input '[^']*' (must|is not|has|is already)", re.I)

_RX_RESOURCE = re.compile(
    r"oom-kill|out of memory|memoryerror|cannot allocate memory|std::bad_alloc|no space left on device"
    r"|due to time limit|exceeded (the )?memory|memory limit", re.I)
_RX_DEPENDENCY = re.compile(
    r"command not found|no module named|modulenotfounderror|importerror|there is no package called"
    r"|cannot open shared object file|error while loading shared libraries|can't locate \S+\.pm in @inc", re.I)
_RX_INPUT_FORMAT = re.compile(
    r"gzip: (stdin: )?(invalid magic|not in gzip format|crc error)|not in gzip format|not a gzipped file|badgzipfile"
    r"|badzipfile|file is not a zip file|not compressed with bgzip|not bgzf compressed|bgzf_read_block"
    r"|no bgzf eof marker|cannot index files compressed with gzip|does not look like a tar archive"
    r"|unknown file type|cannot be usefully indexed|file signature not found|invalid bcf|unicodedecodeerror"
    r"|missing header|too few columns|expected file format|is not sorted|\bunsorted\b|must be sorted"
    r"|could not load fai index|malformed fasta index|failed to read from \S+\.(vcf|bcf|bam|sam|cram)"
    r"|unrecogni[sz]ed (file )?format|not a valid (bam|sam|vcf|bcf|fasta|fastq|bed|gff|gtf|hdf5|h5ad|zip)"
    r"|file is truncated|truncated file|compressed file ended before", re.I)
_RX_EXITCODE_ONLY = re.compile(r"^\s*(tool_stderr:\s*)?(\|\s*)?(stderr:\s*)?(\|\s*)?exit_code:\s*-?\d+\s*$", re.I)

# Lower-case Galaxy built-in tool IDs that would otherwise look like UDT IDs.
_BUILTIN_IDS = {"upload1", "cat1", "sort1", "join1", "comp1", "gene2exon1", "random_lines1", "ucsc_table_direct1",
                "ucsc_table_direct_archaea1", "ucsc_table_direct_test1", "gff2bed1", "ebi_sra_main", "sra_source"}
_RX_UDT_ID = re.compile(r"[a-z][a-z0-9_-]*")

_WARN_STATUS = {
    "parameter_mismatch": "Job ran with parameters that differ from the request",
    "provenance_mismatch": "Job ran on inputs that differ from the request",
}


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def _s(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    try:
        return json.dumps(x, default=str)
    except Exception:
        return str(x)


def _err_text(call_error) -> str:
    if isinstance(call_error, dict):
        return _s(call_error.get("message") or call_error)
    e = _s(call_error)
    return "" if e in ("None", "null") else e


def _unwrap(result):
    """Some results are double-wrapped as {"content": [{"text": "<json>"}], ...}; return the inner object."""
    if isinstance(result, dict) and "status" not in result and isinstance(result.get("content"), list):
        c = result["content"]
        if c and isinstance(c[0], dict) and isinstance(c[0].get("text"), str):
            try:
                inner = json.loads(c[0]["text"])
                if isinstance(inner, dict):
                    return inner
            except Exception:
                pass
    return result


def _is_udt_job(tool: str, job: dict) -> bool:
    if tool == "run_galaxy_udt_and_wait":
        return True
    tid = str(job.get("tool_id") or "")
    if not tid or tid.startswith("toolshed.") or tid.startswith("__") or tid.startswith("CONVERTER_"):
        return False
    if tid in _BUILTIN_IDS or tid.startswith("interactive_tool_"):
        return False
    return bool(_RX_UDT_ID.fullmatch(tid))


def _job_text(job: dict) -> str:
    fd = job.get("failure_diagnostic") if isinstance(job.get("failure_diagnostic"), dict) else {}
    parts = [_s(job.get("failure")), _s(fd.get("message")), _s(fd.get("job_messages"))]
    return " | ".join(p for p in parts if p and p not in ("None", "null", "[]"))


def _classify_job(tool: str, job: dict) -> str:
    state = str(job.get("state"))
    fd = job.get("failure_diagnostic") if isinstance(job.get("failure_diagnostic"), dict) else {}
    phase = str(fd.get("phase"))
    txt = _job_text(job)
    udt = _is_udt_job(tool, job)
    if state == "paused":
        return "Job paused"
    if state in ("deleted", "deleting", "deleted_new") or phase == "cancelled_or_deleted":
        return "Job deleted or cancelled"
    if phase == "resource_runtime" or _RX_RESOURCE.search(txt) or str(fd.get("exit_code")) == "137":
        return "Job hit memory, disk or time limit"
    if phase == "dependency_runtime" or _RX_DEPENDENCY.search(txt):
        return "Missing software dependency in job"
    if str(job.get("tool_id") or "").startswith("CONVERTER_") or _RX_INPUT_FORMAT.search(txt):
        return "Input format, compression or index problem"
    no_diag = (not txt) or bool(_RX_EXITCODE_ONLY.match(_s(job.get("failure")))) and not _s(fd.get("job_messages")).strip("[]\" ")
    if phase == "pre_execution_or_command_rendering" or no_diag:
        if udt and phase == "pre_execution_or_command_rendering":
            return "UDT job failed before its command ran"
        return "Job failed before execution or without diagnostic"
    return "UDT script runtime error with diagnostic" if udt else "Tool runtime error with diagnostic"


def _first_bad_job(result: dict):
    jobs = result.get("jobs")
    if not isinstance(jobs, list):
        return None
    for j in jobs:
        if isinstance(j, dict) and str(j.get("state")) not in ("ok", "None", ""):
            return j
    return None


def _classify_request_error(e: str, default: str) -> str:
    """Classify an HTTP/API rejection message (submission, inspection, upload)."""
    if _RX_SERVER.search(e):
        return "Server, transport or rate-limit problem"
    if _RX_TOOL_NOT_FOUND.search(e):
        return "Tool ID not found"
    if _RX_UPLOAD.search(e):
        return "Upload or staging failed"
    if _RX_STRUCT.search(e):
        return "Parameter rejected: nested-key structure"
    if _RX_ID.search(e):
        # mixed messages that also carry a value/datatype complaint count as value problems
        if re.search(r"invalid option|requires a value|no value provided|required format|collection supplied", e, re.I):
            return "Parameter rejected: value or datatype"
        return "Dataset, history or job ID problem"
    if re.search(r"parameter|parametervalueerror|invalid option|extension .{0,40} unknown|collection|validator|"
                 r"requires a value|genome build|non-commercial|invalid literal", e, re.I):
        return "Parameter rejected: value or datatype"
    return default


def _classify_exception_text(tool: str, t: str) -> str:
    """Plain-text results such as 'Error executing tool X: ...' (call_status failed, call_error empty)."""
    body = t.split(":", 1)[1] if t.startswith("Error executing tool") and ":" in t else t
    if _RX_SERVER.search(body):
        return "Server, transport or rate-limit problem"
    if tool == "run_galaxy_udt_and_wait" and _RX_UDT_REPR.search(body):
        return "UDT definition rejected"
    if tool == "inspect_archive_inventory" and re.search(r"does not belong to the selected history", body, re.I):
        return "Dataset, history or job ID problem"
    if _RX_ARCHIVE.search(body) or (tool == "inspect_archive_inventory" and re.search(r"does not exist", body, re.I)):
        return "Archive inspection rejected"
    if _RX_ID.search(body):
        return "Dataset, history or job ID problem"
    if _RX_ARGS.search(body):
        if tool == "stage_workspace_file" and re.search(r"workspace file does not exist", body, re.I):
            return "Upload or staging failed"
        return "Interface rejected the call arguments"
    if _RX_TOOL_NOT_FOUND.search(body):
        return "Tool ID not found"
    return "Other"


# ---------------------------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------------------------
def classify_mcp(tool: str, call_status: str, result, call_error, text: str = ""):
    tool = str(tool or "")
    err = _err_text(call_error)
    result = _unwrap(result)

    # 0. Out of scope: other connectors (namespaced tool names such as github.fetch, galaxy_mcp.get_user).
    if "." in tool:
        failed = call_status == "failed" or bool(err)
        if isinstance(result, dict) and (result.get("success") is False or str(result.get("status")) == "error"):
            failed = True
        return "Other connector call failed (out of scope)" if failed else None

    # 1. Transport-level failure of the MCP call itself.
    if err and _RX_TRANSPORT.search(err):
        return "MCP call failed or timed out"

    # 2. No parsable JSON result.
    if not isinstance(result, dict):
        t = text or ""
        if call_status == "failed" or err:
            if t.strip():
                return _classify_exception_text(tool, t)
            if tool in ("list_mcp_resources", "list_mcp_resource_templates"):
                return "MCP call failed or timed out"
            return "MCP call failed or timed out" if err else "Other"
        # completed but unparsable: look for a job failure summary in the raw text
        m = re.search(r'"failure_summary":\s*"[0-9a-f]{16,}=(error|paused|deleted)', t)
        if m:
            if m.group(1) == "paused":
                return "Job paused"
            if m.group(1) == "deleted":
                return "Job deleted or cancelled"
            fake = {"state": "error", "failure": t[:20000], "tool_id": "",
                    "failure_diagnostic": {"phase": "command_runtime"}}
            return _classify_job(tool, fake)
        return None

    status = str(result.get("status"))
    state = str(result.get("state"))

    # 3. Resource listings and archive inventory: success has no status field.
    if tool in ("list_mcp_resources", "list_mcp_resource_templates", "inspect_archive_inventory", "inspect_galaxy_history"):
        return None if call_status != "failed" else "Other"

    # 4. Peek.
    if tool == "peek_galaxy_dataset":
        if status == "ok":
            return None
        if status == "dataset_not_ready":
            return "Peek at a dataset that is not ready or failed"
        if status == "history_mismatch":
            return "Dataset is outside the stated history"
        return "Other"

    # 5. Search and inspect.
    if tool == "search_galaxy_tools":
        if status in ("ok", "None"):
            return None
        return _classify_request_error(_s(result.get("error")), "Other")
    if tool == "inspect_galaxy_tool":
        if status == "ok":
            return None
        e = _s(result.get("error"))
        if re.search(r"history unavailable", e, re.I):
            return "Tool lookup failed for lack of history context"
        if re.search(r"could not find tool with id", e, re.I):
            return "Tool ID not found"
        return _classify_request_error(e + " " + _s(result.get("history_error")), "Other")

    # 6. Staging.
    if tool == "stage_workspace_file":
        if status == "ok":
            return None
        e = _s(result.get("error"))
        if status == "upload_failed":
            if _RX_ID.search(e):
                return "Dataset, history or job ID problem"
            if _RX_SERVER.search(e) or re.search(r"create file url with status 5\d\d", e, re.I):
                return "Server, transport or rate-limit problem"
            return "Upload or staging failed"
        if status in ("dataset_error", "failed"):
            return "Upload or staging failed"
        return "Other"

    # 7. Run / wait tools.
    if status == "ok":
        return None
    if status in _WARN_STATUS:
        bad = _first_bad_job(result)
        return _classify_job(tool, bad) if bad is not None else _WARN_STATUS[status]
    if status == "validation_parameter_mismatch":
        return "Parameters did not resolve as requested (not submitted)"
    if status == "validation_failed":
        errs = result.get("errors")
        msgs = list(errs.values()) if isinstance(errs, dict) else [errs]
        joined = " || ".join(_s(m) for m in msgs)
        if _RX_STRUCT.search(joined):
            return "Parameter rejected: nested-key structure"
        if msgs and all(_RX_ID.search(_s(m)) for m in msgs):
            return "Dataset, history or job ID problem"
        return "Parameter rejected: value or datatype"
    if status == "submission_failed":
        e = _s(result.get("error"))
        # The interface keeps only the tail of very long Galaxy errors; those tails are parameter-error
        # payloads (long "valid options" lists or a rejected query string in err_data).
        default = ("Parameter rejected: value or datatype"
                   if len(e) >= 1900 and not e.startswith("Unexpected HTTP status code") else "Other")
        return _classify_request_error(e, default)
    if status == "udt_creation_failed":
        e = _s(result.get("error"))
        if _RX_SERVER.search(e):
            return "Server, transport or rate-limit problem"
        return "UDT definition rejected"
    if status == "workspace_staging_failed":
        return "Upload or staging failed"
    if status == "collection_lookup_failed":
        return "Output collection lookup failed after the job"
    if status == "dataset_error":
        return "Output dataset failed metadata"
    if status == "timeout":
        return "MCP call failed or timed out"
    if status == "failed":
        bad = _first_bad_job(result)
        if bad is not None:
            return _classify_job(tool, bad)
        return "Other"
    return "Other"
