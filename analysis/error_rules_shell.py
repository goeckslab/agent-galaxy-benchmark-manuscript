"""Rule-based labels for failed shell commands run by an agent.

Pure standard library, no I/O.  ``classify_shell(command, output, exit_code)`` returns exactly one
label from ``SHELL_LABELS``.  The rules are ordered; the first rule that matches wins.

Inputs as stored in the event extract: ``command`` is the first 600 characters of the command;
``output`` is the combined stdout+stderr, cut to the first 300 + " ... " + last 700 characters when
longer than 1,000 characters.

Precedence (several causes can co-occur in one command, so the order is part of the definition):

1. How the process ended beats what it printed: a closed pipe (exit 141, BrokenPipeError, curl
   "failure writing output" into head/grep/...) is "Not an error"; exit 130/143/124/129 or a
   KeyboardInterrupt is "Time limit reached or command interrupted"; exit 137 or a "Killed" /
   cannot-allocate line is "Out of memory or killed"; exit 134/139/132 or a segmentation fault,
   abort or unsupported-CPU-instruction message is "Program crashed".
2. galaxy-cli prints a JSON error with a category: "usage_error" is a command-line error, every
   other category is "Galaxy API request failed".
3. A failed installation or build command (pip, conda/mamba/micromamba, apt, R installers, make,
   cmake, maven) is labelled by the cause its output shows: a missing program first, then
   permission, then interruption, then network; only when none of these is visible is it
   "Package installation failed".  A Python error raised by the agent's code *after* a successful
   install is labelled by that error instead.  ``is_install_command`` exposes the command type so
   that every failed installation attempt can still be counted, whatever its cause.
4. A missing program ("command not found", exit 127, exec-format error) beats later text, unless a
   Python, R or curl error is printed after it.
5. Otherwise the last Python exception decides, unless further error text follows it (for example a
   later `wc: x: No such file`), in which case the generic rules are first applied to that later text.
   HTTP and connection failures go to "Galaxy API request failed" when the target is Galaxy (bioblend,
   GALAXY_URL, usegalaxy.*, /api/histories ...) and to "Network or remote resource failure" otherwise.
   A Galaxy job or dataset found in an error state by bioblend counts as "Galaxy API request failed".
6. Then an R error block ("Error in ...", "Execution halted").
7. Then generic text rules in this order: web failure, syntax, permission, command-line usage,
   file not found, undefined function/variable (wrong use of API), Perl module missing, unreadable
   data, build/installation, bioinformatics tool error, explicit failed check.
8. A non-zero exit with no error text anywhere in the output is "Not an error" when the shell part of
   the command (heredoc bodies removed) is a search, test, comparison or probe (grep, rg, test, diff,
   which, command -v, ls/find/stat with errors silenced, ps, git status), and "No error message
   captured" otherwise.
"""
import re

SHELL_LABELS = [
    ("Program not installed",
     "The shell could not start a program: command not found (exit 127), missing executable path, or a binary that cannot run on this machine."),
    ("Package or module missing",
     "An import or load of a Python, R or Perl package failed because the package is not installed or cannot be loaded."),
    ("Package installation failed",
     "pip, conda, mamba, apt, an R installer or a source build (make, cmake, maven) ran and could not install or build the software."),
    ("Network or remote resource failure",
     "A download or web request to a non-Galaxy host failed: DNS, proxy, time-out, rate limit, HTTP error status, missing remote file."),
    ("Galaxy API request failed",
     "A bioblend, galaxy-cli or direct HTTP request to the Galaxy server returned an error, or a Galaxy job or dataset it polled was in an error state."),
    ("File or path not found",
     "A local file or directory named by the command did not exist (or was a directory where a file was needed)."),
    ("Permission or sandbox restriction",
     "The operating system or sandbox refused the action: permission denied, operation not permitted, read-only file system, user install refused."),
    ("Time limit reached or command interrupted",
     "The command was stopped before it finished: exit 130, 143 or 124, KeyboardInterrupt, SIGINT/SIGTERM, or an explicit time-out."),
    ("Out of memory or killed",
     "The process was killed (exit 137, 'Killed') or reported that it could not allocate memory."),
    ("Program crashed",
     "The program aborted abnormally: segmentation fault, abort, illegal or unsupported CPU instruction (exit 139, 134, 132)."),
    ("Syntax error in the agent's own code",
     "Python, R, shell, awk, sed, perl or jq code written by the agent did not parse."),
    ("Data did not match what the code expected",
     "The code ran but the data were not as assumed: missing key or column, index out of range, parse, decompression or encoding error, wrong shape or type."),
    ("Wrong use of a library or API",
     "The code called something that does not exist or passed it the wrong thing: missing attribute or function, wrong argument, undefined name."),
    ("Wrong command-line arguments to a program",
     "A program rejected its options or arguments: usage message, unknown or invalid option, missing operand."),
    ("Bioinformatics tool reported a failure",
     "A bioinformatics program started, ran and exited with its own error message that fits no more general cause."),
    ("The agent's own check failed",
     "An assertion or explicit validation written by the agent stopped the command (AssertionError, stopifnot, deliberate exit after a check)."),
    ("No error message captured",
     "Non-zero exit with empty output, or output without any error text, from a command that is not a search, test or probe."),
    ("Other runtime error",
     "An error message is present but fits none of the other labels."),
    ("Not an error",
     "Non-zero exit without a failure: search with no match, test, comparison, deliberate probe, closed pipe, warning-only exit."),
]

L_PROG = "Program not installed"
L_PKG = "Package or module missing"
L_INSTALL = "Package installation failed"
L_NET = "Network or remote resource failure"
L_GALAXY = "Galaxy API request failed"
L_FILE = "File or path not found"
L_PERM = "Permission or sandbox restriction"
L_TIME = "Time limit reached or command interrupted"
L_OOM = "Out of memory or killed"
L_CRASH = "Program crashed"
L_SYNTAX = "Syntax error in the agent's own code"
L_DATA = "Data did not match what the code expected"
L_API = "Wrong use of a library or API"
L_CLI = "Wrong command-line arguments to a program"
L_BIO = "Bioinformatics tool reported a failure"
L_CHECK = "The agent's own check failed"
L_NOMSG = "No error message captured"
L_OTHER = "Other runtime error"
L_NOT = "Not an error"

# --------------------------------------------------------------------------- command helpers

_WRAP = re.compile(r"^\s*(?:/usr)?/bin/(?:ba|z|da)?sh\s+-l?c\s+")
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?(?:\n\s*\2\b|\Z)", re.S)


def _unwrap(command):
    """Drop the `/bin/bash -lc '...'` wrapper."""
    c = command or ""
    m = _WRAP.match(c)
    if m:
        c = c[m.end():]
        if c[:1] in "'\"":
            c = c[1:]
    return c


def _shell_only(cmd):
    """The shell part of a command: heredoc bodies (inline Python/R code) removed."""
    return _HEREDOC.sub("<<HEREDOC ", cmd)


_INSTALL_CMD = re.compile(
    r"(?:^|[\s;&|(\"'/])(?:"
    r"pip3?(?:\.\d+)?\s+(?:--?[\w-]+(?:[= ]\S+)?\s+)*(?:install|download|wheel)"
    r"|-m\s+pip\s+(?:--?[\w-]+(?:[= ]\S+)?\s+)*(?:install|download|wheel)"
    r"|uv\s+(?:pip\s+install|add|sync|venv)"
    r"|(?:conda|mamba|micromamba)\s+(?:--?[\w-]+(?:[= ]\S+)?\s+)*(?:install|create|update|env\s+(?:create|update))"
    r"|apt(?:-get)?\s+(?:--?[\w:=-]+(?:\s+[\w/:=.-]+)?\s+)*(?:install|update|download)"
    r"|apt-cache\s|dpkg\s+-i|apk\s+add|yum\s+install|dnf\s+install|brew\s+install"
    r"|install\.packages\s*\(|BiocManager::install|biocLite\s*\(|(?:remotes|devtools|pak)::(?:install_\w+|pkg_install|pak)"
    r"|R\s+CMD\s+INSTALL|cpanm?\s|gem\s+install|npm\s+(?:install|i)\s|cargo\s+(?:install|build)|go\s+install"
    r"|setup\.py\s+(?:install|build|develop)"
    r"|make(?:\s+-\S+)*(?:\s+[\w./=-]+)*\s*(?:$|[;&|>\n])|cmake\s|\./configure\b|mvn\s|gradle\s|\./gradlew\s"
    r")"
)


def is_install_command(command):
    """True when the shell part of the command asks a package manager or build tool to install or build software."""
    return bool(_INSTALL_CMD.search(_shell_only(_unwrap(command))))


_GALAXY_MARK = re.compile(
    r"usegalaxy\.|GALAXY_URL|GALAXY_API|galaxy_url|galaxy_api_key|x-api-key|bioblend|GalaxyInstance"
    r"|galaxy-cli|/api/(?:histories|tools|datasets|jobs|workflows|invocations|dataset_collections|users|"
    r"version|tool_data|genomes|libraries|tool_shed_repositories|configuration|whoami|upload|tus|remote_files)\b",
    re.I)
_GALAXY_URL = re.compile(r"https?://[\w.-]*(?:usegalaxy\.[\w.]+|galaxy[\w-]*\.(?:org|eu|au|fr|be|edu|io|no|cz)\b)", re.I)
_ANY_URL = re.compile(r"(?:https?|ftp)://[\w.-]+", re.I)


def _galaxy_target(cmd, errtext):
    """Decide whether a failed web request was addressed to Galaxy."""
    urls = _ANY_URL.findall(errtext or "")
    if urls:
        return any(_GALAXY_URL.match(u) for u in urls)
    if not _GALAXY_MARK.search(cmd):
        return False
    if re.search(r"bioblend|GalaxyInstance|galaxy-cli|GALAXY_URL|GALAXY_API|galaxy_api_key|usegalaxy", cmd, re.I):
        return True
    # only an /api/... path matched: Galaxy only if a Galaxy host is named (Hugging Face also has /api/datasets)
    return any(_GALAXY_URL.match(u) for u in _ANY_URL.findall(cmd))


# --------------------------------------------------------------------------- text patterns

_PY_EXC = re.compile(
    r"^[ \t]*((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*(?:Error|Exception|Interrupt|Exit|Iteration|BadZipFile|BadGzipFile|"
    r"Timeout|TimeoutExpired|IncompleteRead|RemoteDisconnected|InvalidURL|gaierror|herror|Warning)|"
    r"(?:[A-Za-z_]\w*\.)+(?:error|timeout|Error)|"
    r"AssertionError|KeyboardInterrupt|SystemExit|EOFError|MemoryError|Exception)"
    r"(?::[ \t]*(.*))?[ \t]*$", re.M)

_BUILTIN_TYPES = (r"(?:NoneType|list|dict|str|int|float|tuple|bytes|set|bool|bytearray|generator|dict_keys|"
                  r"dict_values|dict_items|map|filter|zip|range|function|builtin_function_or_method|method)")

_NET_TEXT = re.compile(
    r"Could not resolve host|Temporary failure in name resolution|Name or service not known|nodename nor servname"
    r"|getaddrinfo|Connection refused|Connection reset|Connection timed out|Connection aborted|Network is unreachable"
    r"|No route to host|Failed to connect|Could not connect|CONNECT tunnel failed|Proxy(?:Error| CONNECT aborted)"
    r"|SSL(?:Error|_read|_connect| routines| certificate)|certificate verify failed|TLS connect error"
    r"|Max retries exceeded|Read timed out|Operation timed out|timed out after|Timeout was reached"
    r"|RemoteDisconnected|IncompleteRead|Empty reply from server|Recv failure|transfer closed"
    r"|HTTP Error [45]\d\d|[45]\d\d (?:Client|Server) Error|HTTP/[\d.]+ [45]\d\d"
    r"|The requested URL returned error|returned error: [45]\d\d|ERROR [45]\d\d:|error [45]\d\d while"
    r"|HTTP error [45]\d\d|status(?: code)?[ :=]+[45]\d\d\b|Too Many Requests|Service Unavailable|Bad Gateway"
    r"|Gateway Time-?out|CondaHTTPError|Connection(?:Error| broken)|NewConnectionError|URLError|urlopen error"
    r"|Download(?:ing)? (?:failed|error)|Failed to download|Unable to (?:fetch|download|connect)"
    r"|Failed to fetch|Could not fetch|could not be (?:fetched|downloaded)|cannot open URL|unable to access 'https?:"
    r"|Server denied you|Multi-download failed|Transferred a partial|Transfer failed"
    r"|unable to resolve host|wget: unable|ERROR: cannot verify|network (?:error|unreachable|failure)"
    r"|could not read Username|remote did not send all|Repository not found|RPC failed|early EOF"
    r"|server seems to be down|\[E::hts_open_format\] Failed to open file \"https?:",
    re.I)

_PERM_TEXT = re.compile(
    r"Permission denied|Operation not permitted|Read-only file system|are you root\?|must be (?:run as )?root"
    r"|not permitted|PermissionError|EACCES|EPERM|requires? (?:root|superuser|sudo)|sudo: |not in the sudoers"
    r"|Can not perform a '--user' install|externally-managed-environment|could not open lock file",
    re.I)

_CMD_NOT_FOUND = re.compile(
    r"(?:^|\n)[^\n]*?(?:(?:ba|z|da)?sh|/bin/sh|line \d+|env|xargs|timeout|nohup|sudo|time|nice|exec|parallel)[^\n]*?:\s*"
    r"(?:[^\n:]*:\s*)?(?:command not found|not found\s*(?=\n|$)|No such file or directory\s*(?=\n|$))"
    r"|command not found|is not recognized as an internal or external command"
    r"|Exec format error|cannot execute binary file|qemu-\w+: Could not open|bad interpreter"
    r"|Error: Could not find or load main class|Unable to locate a Java Runtime|executable file not found"
    r"|no (?:\w+ )?executable found|is not installed\b|not installed or not in PATH|not found in PATH",
    re.I)
_CMD_NOT_FOUND_STRICT = re.compile(
    r"command not found|: not found\s*(?=\n|$)|Exec format error|cannot execute binary file|qemu-\w+: Could not open"
    r"|bad interpreter|Unable to locate a Java Runtime",
    re.I)

_FILE_TEXT = re.compile(
    r"No such file or directory|FileNotFoundError|cannot open file|does not exist|doesn't exist|not exist\b"
    r"|No such file|cannot access|Is a directory|Not a directory|cannot find (?:the )?(?:file|path)|file not found"
    r"|Could not open (?:file|input)|could not open|can't open|cannot open|unable to open"
    r"|Failed to open|can't read|cannot stat|can't cd|cannot read|couldn't open"
    r"|NotADirectoryError|IsADirectoryError|No files? (?:found|matching|matched)|no matches found|cannot find"
    r"|non-existent directory|nonexistent",
    re.I)

_SYNTAX_TEXT = re.compile(
    r"SyntaxError|IndentationError|TabError|syntax error|unexpected EOF|unexpected end of file|unexpected token"
    r"|unterminated|unexpected (?:symbol|string constant|numeric constant|input|end of input|assignment|SPECIAL|"
    r"'[^'\n]{1,12}'|\"[^\"\n]{1,12}\")(?: in|$| at)|unknown command: |unknown option to `s'|aborted due to compilation errors"
    r"|compile error|illegal statement|illegal field|awk: cmd\. line|unmatched [`'\"(\[{]|newline in string|bailing out"
    r"|parse error near|-e expression #\d+, char \d+|extra characters at the end|invalid command code|bad substitution"
    r"|unexpected character|invalid escape|EOL while scanning|was never closed|here-document[^\n]*delimited by end-of-file"
    r"|Missing right curly|Can't find string terminator|unbalanced",
    re.I)

_CLI_TEXT = re.compile(
    r"(?:^|\n)\s*usage:|\bUsage:|unrecognized (?:option|argument|command|arguments)|invalid option|unknown option"
    r"|illegal option|unknown (?:primary|argument|flag|command|subcommand|parameter|switch)|unknown \w+ parameter"
    r"|no such option|No such command"
    r"|Try [`'\"]?[\w ./-]+(?:--help|-h)|try [`'\"]?\w+ --help|for more information|requires an argument|option requires"
    r"|missing (?:operand|argument|file operand|required)|unexpected argument|too few arguments|too many arguments"
    r"|extra operand|keyword not found|unknown primary or operator|not a valid (?:option|argument|command)"
    r"|invalid (?:argument|choice|value for|number of arguments|flag|parameter|command)|expected one argument"
    r"|is unknown|ambiguous option|the following arguments are required|error: argument|Unknown (?:option|argument)"
    r"|option .{1,40} (?:is not recognized|not recognized|doesn't allow|needs an argument)|invalid context length"
    r"|URL (?:rejected|using bad/illegal format)|No URL specified|mutually exclusive"
    r"|bad (?:option|flag|argument)|Unsupported option|not an? \w+ command|invalid mode"
    r"|Got unexpected extra argument|Error: Missing (?:option|argument)|Error: Invalid value",
    re.I)

_DATA_TEXT = re.compile(
    r"not in gzip format|unexpected end of file|invalid compressed data|not a gzip file|Not a gzipped file|data stream error"
    r"|uncompress failed|crc error|does not look like a tar archive|End-of-central-directory signature not found|not a zip ?file"
    r"|cannot find zipfile|Cannot index \w+ with|Cannot iterate over|jq: error|parse error: |Invalid numeric literal|invalid literal"
    r"|is not valid JSON|Expecting value|Unexpected token|malformed|truncated|corrupt|invalid (?:header|format|magic|record|line)"
    r"|not a valid (?:\w+ )?file|unrecognized (?:file )?format|unknown (?:file )?format|wrong (?:file )?format"
    r"|illegal byte sequence|invalid multibyte|input is not|No (?:columns|records|data|sequences) |empty (?:file|input)"
    r"|different number of (?:columns|fields)|wrong number of (?:columns|fields)|division by zero"
    r"|unexpected EOF in archive|Unexpected EOF|not (?:a|in) (?:BAM|SAM|VCF|BCF|FASTA|FASTQ|BED|GFF|HDF5|bgzip)"
    r"|file signature not found|is not a \w+ file|could not parse|couldn't parse|cannot parse"
    r"|failed to parse|unable to parse|Error parsing|parsing error|Parse error|sort: [^\n]*disorder|non-numeric",
    re.I)

_OOM_TEXT = re.compile(
    r"(?:^|\n)[^\n]*\bKilled\b(?!\s+process)|MemoryError|Cannot allocate memory|cannot allocate (?:memory|vector)"
    r"|std::bad_alloc|[Oo]ut of memory|OutOfMemory|Unable to allocate \d|not enough memory|memory exhausted"
    r"|insufficient memory|oom-kill|EXITING because of fatal ERROR: not enough memory|Java heap space")
_CRASH_TEXT = re.compile(
    r"Segmentation fault|Abort trap|Illegal instruction|core dumped|Bus error|terminate called|libc\+\+abi: terminating"
    r"|Fatal Python error|\*\*\* caught segfault|double free or corruption|stack smashing|Floating point exception"
    r"|compiled to use \w+ instructions|SIGSEGV|SIGABRT|SIGILL|Trace/BPT trap|free\(\): invalid|malloc\(\): ")
_TIME_TEXT = re.compile(
    r"KeyboardInterrupt|TimeoutExpired|(?:^|\n)\s*\^C|SIGINT received|Operation cancelled by user|(?:^|\n)[^\n]*\bTerminated\b"
    r"|command timed out|Interrupted system call|(?:^|\n)timeout: |Thread interrupted|interrupted by signal|received SIGTERM")

_INSTALL_FAIL = re.compile(
    r"(?:^|\n)\s*(?:ERROR|error|E|Error|CRITICAL|critical libmamba|error\s+libmamba|CondaError|\S*Error)[: ]"
    r"|No matching distribution|Could not find a version|PackagesNotFoundError|ResolvePackageNotFound|Unsatisfiable"
    r"|Could not solve|Solving environment: failed|is not installable|conflicts? with|nothing provides"
    r"|Failed to build|failed-wheel-build|Failed building wheel|subprocess-exited-with-error|metadata-generation-failed"
    r"|Unable to locate package|has no installation candidate|Couldn't find any package|held broken packages|Could not get lock"
    r"|had non-zero exit status|is not available for (?:this version of R|package)|package .{1,40} is not available"
    r"|installation of (?:package|\d+ packages?) .{0,60}(?:failed|had)|dependenc(?:y|ies) .{1,80}(?:not available|is not available)"
    r"|EnvironmentLocationNotFound|The given prefix does not|No module named pip|CondaValueError|InvalidArchiveError"
    r"|requires a different Python|not supported on this platform|is not a supported wheel|Could not build wheels"
    r"|compilation failed|ERROR: configuration failed|non-zero exit status|command '[^'\n]+' failed|exit status \d+"
    r"|make(?:\[\d+\])?: \*\*\*|BUILD FAILURE|fatal error: |: error: |CMake Error|configure: error",
    re.I)

_BIO_TOOLS = (
    r"samtools|bcftools|bedtools|htsfile|tabix|bgzip|bwa(?:-mem2)?|bowtie2?(?:-build|-align\S*)?|minimap2|hisat2(?:-build)?|STAR"
    r"|salmon|kallisto|blast[npx]|tblast[nx]|makeblastdb|blastdbcmd|update_blastdb(?:\.pl)?|psiblast|rpsblast|diamond"
    r"|mmseqs|hmm(?:search|scan|build|press|align)|jackhmmer|phmmer|nhmmer|mafft|muscle|clustalo|clustalw2?|t_coffee|prank|trimal"
    r"|iqtree2?|raxml(?:-ng|HPC\S*)?|fasttree|FastTree|phyml|mrbayes|treetime|phykit|clipkit|busco|orthofinder|augustus"
    r"|prokka|bakta|prodigal|spades(?:\.py)?|megahit|flye|canu|hifiasm|unicycler|quast(?:\.py)?|meryl|merqury|jellyfish|genomescope2?"
    r"|kmc|kmc_tools|mash|sourmash|fastANI|skani|seqkit|seqtk|fastqc|fastp|multiqc|cutadapt|trimmomatic|trim_galore|bbduk(?:\.sh)?"
    r"|bbmap(?:\.sh)?|picard|gatk|freebayes|varscan|lofreq|snpEff|snpSift|vep|annovar|vcftools|vcfutils\.pl|plink2?|king|admixture"
    r"|shapeit\d?|beagle|featureCounts|htseq-count|stringtie|cufflinks|gffread|gffcompare|rsem-\w+|macs[23]|homer|findMotifsGenome\.pl"
    r"|annotatePeaks\.pl|makeTagDirectory|meme|fimo|tomtom|streme|centrimo|bamCoverage|bamCompare|computeMatrix|plotHeatmap"
    r"|plotProfile|multiBamSummary|plotFingerprint|alignmentSieve|bigWig\w+|bedGraphToBigWig|wigToBigWig|bigBed\w+|bedToBigBed"
    r"|twoBitToFa|faToTwoBit|liftOver|faSize|faSomeRecords|bedSort|genePredTo\w+|gtfToGenePred|gfClient|gfServer|kraken2?|bracken"
    r"|metaphlan|humann|centrifuge|ktImportTaxonomy|qiime|mothur|vsearch|usearch|cd-hit(?:-est)?|needle|transeq|seqret|getorf"
    r"|primer3_core|RNAfold|cellranger|velocyto|alevin-fry|umi_tools|deepvariant|manta|delly|cnvkit(?:\.py)?|bismark"
    r"|MethylDackel|NanoPlot|NanoFilt|filtlong|medaka\w*|racon|pilon|porechop|sniffles|whatshap"
    r"|pepquery|PepQuery|msconvert|FileConverter|FeatureFinder\w+|percolator|caper|croo|cromwell|womtool|nextflow|snakemake"
    r"|miniwdl|cwltool|planemo|prefetch|fasterq-dump|fastq-dump|vdb-\w+|esearch|efetch|esummary|datasets|dataformat"
    r"|SAMstats|idr|preseq|ataqv|Genrich|chromap|pyGenomeTracks|cooler|pairtools|pairix|mosdepth|qualimap"
    r"|infer_experiment\.py|read_distribution\.py|Trinity|TransDecoder\S*|interproscan(?:\.sh)?|emapper(?:\.py)?|abricate"
    r"|amrfinder|rgi|mlst|snippy|roary|panaroo|gubbins|snp-sites|snp-dists|nextclade|pangolin|ivar|kma|shovill|skesa|dnadiff"
    r"|nucmer|show-coords|lastz|lastal|lastdb|blat|pblat|gmap|gsnap|exonerate|miniprot|liftoff|ragtag(?:\.py)?|purge_dups"
    r"|gfatools|mitohifi(?:\.py)?|tRNAscan-SE|barrnap|cmsearch|cmscan|RepeatMasker|dustmasker|windowmasker|bedops|bedmap"
    r"|sort-bed|wiggletools|faidx|vg|odgi|encode_task_\w+\.py|hap\.py|truvari|pbmm2|dorado|modkit|nanopolish|bustools|simpleaf"
    r"|ThermoRawFileParser\S*|sirius"
)
_BIO_CMD = re.compile(r"(?:^|[\s;&|(`\"'/=])(?:" + _BIO_TOOLS + r")(?=[\s;'\"`)]|$)")
_BIO_TEXT = re.compile(
    r"\[E::\w+\]|\[main_\w+\]|\[bam_\w+\]|\[bwa_\w+\]|\[mem_\w+\]|\[mpileup\]|\[fai_\w+\]|\[tabix\]|\[faidx\]|\[bcftools|\[samtools"
    r"|samtools \w+: |bcftools \w+: |BLAST (?:Database|engine|query|options) error|\[blast\w*\] |Error: \(\d+\.\d+\)|CFastaReader"
    r"|NCBI C\+\+ Exception|\[ERROR\]\s|EXITING because of|\[bowtie2?\]|bowtie2-align exited|\(ERR\): |htslib|Pipeline aborted"
    r"|at (?:picard|htsjdk|org\.broadinstitute)\.|Failed to (?:read|parse|open) (?:BAM|SAM|VCF|BCF|FASTA|FASTQ|header)"
    r"|\[E\]|\[error\]|\[fatal\]|FATAL|Fatal error",
    re.I)

_ERR_HINT = re.compile(
    r"Traceback \(most recent call last\)|[Ee]rror\b|ERROR|[Ee]xception|[Ff]atal|FATAL|[Ff]ailed|FAILED|[Ff]ailure|cannot|can't|Cannot"
    r"|[Dd]enied|not found|No such|not permitted|[Ii]nvalid|[Ii]llegal|[Uu]nknown|[Uu]nrecognized|[Uu]sage:|Execution halted"
    r"|[Aa]bort|Killed|timed out|[Uu]nable to|not exist|[Mm]issing|[Uu]nexpected|[Rr]efused|not installed|not available"
    r"|could not|Could not|couldn't|Couldn't|Segmentation|panic|undefined|[Uu]nsupported|not supported|is not a|bad \w+")

_SEARCH_CMD = re.compile(
    r"(?:^|[;&|(\n`$]|\bthen\b|\bdo\b|\bif\b|\bwhile\b|\buntil\b|!|\|\|)\s*(?:\w+=\S*\s+)*(?:command\s+-v|which|type|hash|grep|egrep|fgrep"
    r"|zgrep|bzgrep|rg|ag|ack|pgrep|pidof|test|\[\[?|diff|cmp|ps|kill\s+-0|git\s+(?:diff|grep|status|rev-parse)|compgen|dpkg\s+-[sl]"
    r"|pip3?\s+show|jq\s+-e|xargs\s+(?:-\S+\s+)*(?:grep|rg|test)|lsof|getent|expr)(?=\s|$)")
_SILENCED_LS = re.compile(r"(?:^|[;&|(\n])\s*(?:ls|stat|find|cat|head|file|du|wc|readlink|realpath|id|pip3?\s+show|conda\s+list)\b[^;|&\n]*2>\s*/dev/null")

_R_ERR = re.compile(r"(?:^|\n)(Error(?: in [^\n]*?)?\s*:[^\n]*(?:\n(?!Calls:|Execution halted|In addition:|Backtrace)[^\n]*){0,6})")

_GALAXY_STATE = re.compile(r"terminal state|DatasetStateException|state is not 'ok'|non-terminal state|failed_metadata"
                           r"|\bstate[=:\s]+['\"]?(?:error|failed|paused)\b")


def _last(regex, text):
    m = None
    for m in regex.finditer(text):
        pass
    return m


def _tail_lines(out, n=10):
    lines = [l for l in out.splitlines() if l.strip()]
    return "\n".join(lines[-n:])


# --------------------------------------------------------------------------- sub-classifiers

def _classify_web(cmd, errtext):
    return L_GALAXY if _galaxy_target(cmd, errtext) else L_NET


def _classify_python(name, msg, cmd, out):
    """Label from the last Python exception line; None when it gives no decision."""
    short = name.rsplit(".", 1)[-1]
    msg = msg or ""
    full = name + ": " + msg
    if short == "KeyboardInterrupt" or short == "TimeoutExpired":
        return L_TIME
    if short == "MemoryError" or _OOM_TEXT.search(msg):
        return L_OOM
    if short == "BrokenPipeError":
        return L_NOT
    if short == "ModuleNotFoundError":
        return L_PKG
    if short == "ImportError":
        if re.search(r"cannot import name|has no attribute", msg) and not re.search(r"partially initialized|circular", msg):
            return L_API
        return L_PKG
    if _GALAXY_STATE.search(full) and re.search(r"galaxy|bioblend", cmd + out, re.I):
        return L_GALAXY
    if "bioblend" in name.lower() or (short == "ConnectionError" and "Unexpected HTTP status code" in msg):
        return L_GALAXY
    if re.search(r"err_msg|err_code", msg) and _galaxy_target(cmd, ""):
        return L_GALAXY
    if (name.startswith(("urllib", "requests", "http.client", "urllib3", "socket", "ssl", "httpx", "aiohttp", "ftplib", "httpcore"))
            or short in ("HTTPError", "URLError", "ConnectionError", "ConnectionResetError", "ConnectionRefusedError",
                         "ConnectionAbortedError", "TimeoutError", "ReadTimeout", "ConnectTimeout", "Timeout", "SSLError",
                         "ProxyError", "IncompleteRead", "RemoteDisconnected", "MaxRetryError", "NewConnectionError",
                         "ChunkedEncodingError", "gaierror", "timeout", "ProtocolError", "ContentTooShortError",
                         "TooManyRedirects", "ReadTimeoutError", "error_perm", "error_temp", "HfHubHTTPError",
                         "RepositoryNotFoundError", "GatedRepoError", "LocalEntryNotFoundError")):
        if short in ("JSONDecodeError", "InvalidJSONError"):
            return L_DATA
        if short in ("MissingSchema", "InvalidSchema", "InvalidURL", "LocationParseError", "InvalidHeader"):
            return L_API
        return _classify_web(cmd, msg)
    if short in ("FileNotFoundError", "NotADirectoryError", "IsADirectoryError", "FileExistsError"):
        # subprocess could not find the executable: "No such file or directory: 'samtools'"
        if short == "FileNotFoundError" and re.search(r"No such file or directory: '[\w+-]+'\s*$", msg) \
                and re.search(r"subprocess|Popen|check_output|check_call|\brun\(", cmd + out):
            return L_PROG
        return L_FILE
    if short == "PermissionError":
        return L_PERM
    if short in ("SyntaxError", "IndentationError", "TabError"):
        return L_SYNTAX
    if short in ("AssertionError", "SystemExit"):
        return L_CHECK
    if short == "CalledProcessError":
        return None
    if short in ("KeyError", "IndexError", "JSONDecodeError", "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeError",
                 "ParserError", "EmptyDataError", "BadZipFile", "BadGzipFile", "EOFError", "StopIteration",
                 "ZeroDivisionError", "OverflowError", "LibrdataError", "ParseError", "UnpicklingError",
                 "LookupError", "InvalidIndexError", "MergeError", "InvalidFileException", "XMLSyntaxError", "ExpatError",
                 "ScannerError", "YAMLError", "TOMLDecodeError", "FloatingPointError", "LinAlgError",
                 "PerfectSeparationError", "DecodeError", "InvalidJSONError", "ReadError", "AxisError", "UndefinedVariableError",
                 "PyreadrError", "NewickError", "NexusError", "TreeError", "StreamModeError", "CompressionError",
                 "IncompleteReadError", "DuplicateLabelError", "IntCastingNaNError", "OutOfBoundsDatetime", "DateParseError",
                 "SpecificationError", "DataError", "ShapeError", "ComputeError", "ColumnNotFoundError",
                 "SchemaError", "NoDataError", "HeaderError") or name in ("struct.error", "zlib.error", "binascii.Error",
                                                                          "csv.Error", "lzma.LZMAError", "tarfile.ReadError"):
        return L_DATA
    if name == "re.error":
        return L_SYNTAX
    if short == "ValueError":
        if re.search(r"parameter has been removed|use the \w+\(\) method|Valid options are|Invalid organism|no signature found"
                     r"|is not a valid \w+ (?:name|option|method|mode|style)|must be one of|[Uu]nknown (?:method|format code|option|"
                     r"mode|metric|kernel|solver|projection|label type|url type)|not a valid (?:option|method|argument)|[Ii]nvalid (?:"
                     r"mode|option|method|argument|keyword|format specifier|file mode|metric)|Unrecognized (?:\w+ )?(?:option|keyword|"
                     r"argument|method)|[Mm]issing scheme|unknown url type|mutually exclusive|cannot specify|not supported"
                     r"|only supported|unsupported format|Unsupported|got an unexpected|keyword|Did you mean|n_components|"
                     r"must be (?:a |an )?(?:positive|non-negative|str|int|bool|callable|either)|is not in the list of available|"
                     r"provide (?:a|an|either)|needs to be|should be (?:one of|a |an )|expected one of|is not a valid", msg):
            return L_API
        return L_DATA
    if short == "TypeError":
        if re.search(r"unexpected keyword argument|positional argument|takes (?:no|\d+|from \d+|exactly|at (?:most|least))"
                     r"|missing \d+ required|got multiple values|is not callable|__init__\(\)|\(\) (?:got|takes|missing)"
                     r"|required (?:keyword-only )?argument|invalid keyword|is an invalid keyword|abstract class|no len\(\)"
                     r"|does not support|descriptor|Wrong number or type of arguments|incompatible function arguments"
                     r"|argument \d+ must be|must be called with|expected at most|expected at least|\(\) received an invalid", msg):
            return L_API
        return L_DATA
    if short == "AttributeError":
        if re.search(r"'" + _BUILTIN_TYPES + r"' object has no attribute", msg):
            return L_DATA
        return L_API
    if short in ("NameError", "UnboundLocalError", "NotImplementedError", "MissingSchema", "InvalidSchema", "InvalidURL",
                 "UsageError", "BadParameter", "NoSuchOption", "ArgumentError", "ArgumentTypeError", "RecursionError",
                 "InvalidParameterError", "NotFittedError", "ValidationError", "OptionError", "UnsupportedOperation",
                 "InvalidArgumentError", "ClickException"):
        return L_API
    # OSError, RuntimeError, Exception and library-specific errors: decide from the message text
    if _NET_TEXT.search(full):
        return _classify_web(cmd, msg)
    if _PERM_TEXT.search(full):
        return L_PERM
    if re.search(r"No space left on device", full):
        return L_OTHER
    if _CMD_NOT_FOUND_STRICT.search(full) or re.search(r"not found in PATH|is not installed|not installed", full):
        return L_PROG if not re.search(r"package|module|library|optional dependency|requirements", full, re.I) else L_PKG
    if re.search(r"requirements are not installed|optional dependency|pip install|conda install|is required (?:to|for)|"
                 r"requires (?:the )?[\w.-]+ (?:package|library|module|to be installed)|[Ii]nstall (?:it )?(?:with|via|using)", full):
        return L_PKG
    if _FILE_TEXT.search(full):
        return L_FILE
    if _DATA_TEXT.search(full) or re.search(
            r"shape|dimension|length|mismatch|does not match|not aligned|duplicate|not unique|empty|NaN|None|no \w+ found"
            r"|not in (?:index|list|columns)|out of (?:range|bounds)|column|index|key\b|dtype|convert|decode|encode|parse"
            r"|unrecognized object|file opening|HDF5|h5py|signature|format|[Uu]nable to (?:read|load|synchronously)|"
            r"[Cc]ould not (?:read|load|convert|interpret|determine)|[Ff]ailed to (?:read|load|interpret)|not a \w+ file"
            r"|[Nn]o such (?:column|key|field|sample|contig|sequence|group|sheet|table)|not present|not found in", full):
        return L_DATA
    return None


def _python_label(exc, cmd, out):
    """Label for the Python exception `exc`, including CalledProcessError; always returns a label."""
    name = exc.group(1)
    msg = exc.group(2) or ""
    lab = _classify_python(name, msg, cmd, out)
    if lab:
        return lab
    if name.rsplit(".", 1)[-1] == "CalledProcessError":
        sub = re.search(r"Command '?\[?['\"]?([^\s'\",\]]+)", msg)
        prog = sub.group(1).rsplit("/", 1)[-1] if sub else ""
        pre = out[:exc.start()]
        if re.search(r"^(?:pip3?|conda|mamba|micromamba|apt(?:-get)?)$", prog) or "'-m', 'pip'" in msg:
            return _classify_install(cmd, out, _tail_lines(out)) or L_INSTALL
        if _NET_TEXT.search(pre[-600:]) and re.search(r"^(?:curl|wget|aria2c|git|rsync|scp|ftp|lftp)$", prog):
            return _classify_web(cmd, "")
        if _PERM_TEXT.search(_tail_lines(pre, 6)):
            return L_PERM
        if re.fullmatch(_BIO_TOOLS, prog) or _BIO_TEXT.search(pre[-600:]):
            return L_BIO
        if _FILE_TEXT.search(_tail_lines(pre, 6)):
            return L_FILE
        if _CLI_TEXT.search(_tail_lines(pre, 8)):
            return L_CLI
    return L_OTHER


def _classify_r(block, cmd):
    """Label from an R error block ("Error in ...: message" up to "Execution halted"); None when undecided."""
    b = block
    if re.search(r"there is no package called|could not find package|package .{1,60} (?:is )?required|namespace .{1,60} is not available"
                 r"|package or namespace load failed|loadNamespace|required package|is not installed|not installed|unable to load shared object"
                 r"|unable to find required package|requires installing the \w+ package|requires .{1,30} package which cannot be found"
                 r"|package .{1,60} could not be loaded|Could not find tools necessary to compile", b) \
            and not re.search(r"could not find function", b):
        return L_PKG
    if re.search(r"is an unrecognized escape in character string", b):
        return L_SYNTAX
    if re.search(r"Please run UpdateSeuratObject|layers are not joined|doesn't work for multiple layers|Can't add `", b):
        return L_API
    if re.search(r"is not subsettable|cannot be coerced|cannot be handled by|must be coercible|wrong length|not recognized"
                 r"|insufficient unique values|do not match|values must be type|seek not enabled|Invalid value for", b):
        return L_DATA
    if re.search(r"cannot open URL|cannot open the connection to 'https?|HTTP (?:status|error)|Could not resolve|Timeout was reached"
                 r"|download.{0,20}failed|cannot download|SSL|curl::|InternetOpenUrl|status was|Failed to connect", b):
        return _classify_web(cmd, b)
    if re.search(r"unexpected (?:symbol|string constant|numeric constant|input|end of input|assignment|SPECIAL|'[^']{1,12}'|INCOMPLETE_STRING|"
                 r"else|'else'|'\}'|'\)'|','|'='|'in')|<text>:\d+:\d+|invalid multibyte string|unexpected end|malformed raw string", b):
        return L_SYNTAX
    if re.search(r"cannot open file|No such file or directory|does not exist|cannot open (?:compressed )?file|cannot open the connection"
                 r"|file not found|no such file|path does not|doesn't exist|cannot find|not find file|File .{1,80} not found"
                 r"|cannot change working directory|Not all provided files exist", b) \
            and not re.search(r"Column .{1,40} doesn't exist|Can't (?:subset|rename|select)", b):
        return L_FILE
    if re.search(r"[Pp]ermission denied|not writable|cannot create dir", b):
        return L_PERM
    if re.search(r"cannot allocate|memory exhausted|vector memory", b):
        return L_OOM
    if re.search(r"is not TRUE|are not all TRUE|stopifnot|not all TRUE", b):
        return L_CHECK
    if re.search(r"could not find function|unused arguments?|object '[^']*' not found|object .{1,40} not found|argument \"[^\"]*\" is missing"
                 r"|is not an exported object|formal argument|invalid '\w+' argument|unable to find an inherited method"
                 r"|no applicable method|no slot of name|is not a valid field|should be one of|must be one of|invalid argument"
                 r"|not a function|attempt to apply non-function|no method for|is defunct|is deprecated|must be NULL"
                 r"|No such slot|invalid first argument|unimplemented|not implemented|unknown (?:option|argument)"
                 r"|Can't find|non-function", b):
        if re.search(r"Can't (?:subset|rename|select) columns|Column .{1,40} (?:doesn't exist|not found)|subscript", b):
            return L_DATA
        return L_API
    if re.search(r"subscript out of bounds|undefined columns|differing number of rows|non-conformable|incorrect number of (?:dimensions|subscripts)"
                 r"|more columns than column names|did not have \d+ elements|replacement has|names do not match|same length|same number"
                 r"|non-numeric argument|invalid (?:type|subscript|class|factor level)|missing values?|NA/NaN|duplicate|must have|not equal"
                 r"|length \d|dims |dimnames|contrasts can be applied|no lines available|empty|zero|no reads|removed all|None of the keys"
                 r"|not compatible|incompatible|is not a|not found in|unknown (?:format|column)|bad restore|magic number|unknown input format"
                 r"|ReadItem|invalid .{1,30} value|\$ operator is invalid|cannot coerce|not meaningful|scan\(|line \d+|parse error|embedded nul"
                 r"|invalid UTF|column|rows?\b|levels|ncol|nrow|argument is of length zero|missing value where TRUE/FALSE needed|subscript"
                 r"|non-character|not numeric|must be numeric|singular|not positive definite|infinite|degrees of freedom|all samples have"
                 r"|every gene contains|design matrix|model matrix|not full rank|need at least|too few|not enough|no non-missing"
                 r"|invalid format|doesn't exist|argument of length 0|argument is not", b):
        return L_DATA
    if re.search(r"must be (?:a|an) |`\w+` (?:must|is)|Can't (?:subset|rename|select|combine|convert)", b):
        return L_API
    return None


def _classify_install(cmd, out, tail):
    """Label a failed installation/build command by the cause its output shows; None when no installer failure is visible."""
    if _CMD_NOT_FOUND_STRICT.search(tail):
        return L_PROG
    if not _INSTALL_FAIL.search(out):
        return None
    if re.search(r"Permission denied|Operation not permitted|Read-only file system|are you root\?|Can not perform a '--user' install"
                 r"|externally-managed-environment|not writable|not permitted|PermissionError|EACCES", out):
        return L_PERM
    if re.search(r"KeyboardInterrupt|Operation cancelled by user|SIGINT received|Thread interrupted", out):
        return L_TIME
    if _NET_TEXT.search(out) and not re.search(
            r"No matching distribution|Could not find a version|PackagesNotFoundError|Unable to locate package|is not installable"
            r"|Failed to build|Failed building wheel|failed-wheel-build|nothing provides|Could not solve|Unsatisfiable", out):
        return L_NET
    return L_INSTALL


def _classify_curl(cmd, out):
    m = _last(re.compile(r"curl: \((\d+)\)([^\n]*)"), out)
    if not m:
        return None
    code = int(m.group(1))
    msg = m.group(2)
    if code == 23:
        if re.search(r"\|\s*(?:head|sed|awk|grep|rg|python3?|jq|cut|tr|tail|less|more|wc|file|xxd|od|strings|gzip|gunzip|zcat|tar"
                     r"|bsdtar|unzip|funzip|sort|uniq|tee|cat|column|fold|perl|bgzip|samtools|bcftools|zstd|xz|bzip2|openssl"
                     r"|sha\d+sum|md5sum|md5)\b", cmd):
            return L_NOT
        return L_FILE
    if (code in (2, 3, 43, 48) and not re.search(r"getaddrinfo|resolve", msg)) \
            or re.search(r"URL rejected|bad/illegal format|No URL specified|is unknown", msg):
        return L_CLI
    if code in (26, 37):
        return L_FILE
    return _classify_web(cmd, "")


def _generic(cmd, sh, text, code, install, n_tail=10):
    """Text rules that apply to any command output (last `n_tail` non-empty lines); None when nothing matches."""
    tail = _tail_lines(text, n_tail)
    if re.search(r"galaxy", cmd, re.I) and _GALAXY_STATE.search(tail):
        return L_GALAXY
    lab = _classify_curl(cmd, text)
    if lab:
        return lab
    if _NET_TEXT.search(tail) and (re.search(r"\b(?:curl|wget|aria2c|git|rsync|ftp|lftp|scp|ssh|esearch|efetch|prefetch|fasterq-dump"
                                             r"|datasets|gh|huggingface-cli|hf|aws|gsutil|blast[npx]|tblast[nx]|gfClient|-remote)\b|https?://|ftp://", cmd)
                                   or re.search(r"https?://|ftp://|resolve host|HTTP|[Cc]onnect", tail)):
        return _classify_web(cmd, "")
    if re.search(r"not a git repository", tail) and re.search(r"\bgit\s+(?:status|rev-parse|log|diff|branch|remote)", sh):
        return L_NOT
    if _SYNTAX_TEXT.search(tail) and not re.search(r"jq: error \(at|parse error: (?:Invalid numeric literal|Unfinished|Invalid|Expected|Objects)", tail):
        return L_SYNTAX
    if _PERM_TEXT.search(tail):
        return L_PERM
    if re.search(r"No space left on device|Disk quota exceeded", tail):
        return L_OTHER
    if re.search(r"unknown primary or operator|keyword not found|illegal option|invalid option|unrecognized option"
                 r"|unknown option|requires an argument|missing operand", tail):
        return L_CLI
    if _FILE_TEXT.search(tail):
        return L_FILE
    if _CLI_TEXT.search(tail):
        return L_CLI
    if re.search(r"awk: (?:calling undefined function|function \w+ never defined)|undefined function|undefined variable|unbound variable"
                 r"|not a valid identifier|jq: error: \w+/\d+ is not defined|Undefined subroutine|Can't locate object method", tail):
        return L_API
    if re.search(r"Can't locate \S+\.pm in @INC|you may need to install the \S+ module", tail):
        return L_PKG
    if _DATA_TEXT.search(tail):
        if _BIO_CMD.search(sh) and _BIO_TEXT.search(tail) and not re.search(r"gzip:|jq:|tar:|unzip:|parse error", tail):
            return L_BIO
        return L_DATA
    if code in (5, 6, 7, 18, 22, 28, 35, 52, 56) and re.match(r"\s*(?:\w+=\S+\s+)*curl\b", sh) \
            and not re.search(r"\|\s*(?:jq|python3?|grep|rg|head|sed|awk|tar|gzip|zcat)\b", sh):
        return _classify_web(cmd, "")
    if install:
        lab = _classify_install(cmd, text, tail)
        if lab:
            return lab
    hint = bool(_ERR_HINT.search(text))
    if hint and _BIO_TEXT.search(text) and (_BIO_CMD.search(sh) or re.search(
            r"\[E::|samtools|bcftools|BLAST|\[main_|picard|htsjdk|gatk|bowtie|STAR", text)):
        return L_BIO
    if hint and _BIO_CMD.search(sh) and not _SEARCH_CMD.search(sh):
        return L_BIO
    if re.search(r"(?:^|\n)\s*(?:FAIL(?:ED)?|ASSERT\w*|CHECK FAILED|VALIDATION (?:FAILED|ERROR)|MISSING|MISMATCH|NOT OK|not ok)\b", _tail_lines(text, 3)) \
            and re.search(r"exit\s+[1-9]|sys\.exit|SystemExit|quit\(|stop\(|\bassert\b|\|\|\s*\{?\s*echo|test\s|\[\s", cmd):
        return L_CHECK
    return None


# --------------------------------------------------------------------------- main entry point

def classify_shell(command, output, exit_code):
    """Return exactly one label from SHELL_LABELS for a failed shell command."""
    cmd = _unwrap(command or "")
    sh = _shell_only(cmd)
    out = output or ""
    try:
        code = int(exit_code) if exit_code is not None else None
    except (TypeError, ValueError):
        code = None
    tail = _tail_lines(out, 10)
    last3 = _tail_lines(out, 3)
    stripped = out.strip()
    exc = _last(_PY_EXC, out)
    exc_short = exc.group(1).rsplit(".", 1)[-1] if exc else ""
    has_tb = "Traceback (most recent call last)" in out or bool(exc and re.search(r"\n\s+File \"", out))

    # 1. how the process ended
    if code == 141 or exc_short == "BrokenPipeError" or (
            re.search(r"Broken pipe|write error|Failed writing body", last3) and not has_tb
            and re.search(r"\|\s*(?:head|sed -n|awk|grep|rg|less|more|tail|cut|python3?|jq)\b", sh)
            and not re.search(r"curl: \((?!23)\d+\)", out)):
        return L_NOT
    if code in (130, 143, 124, 129, 142) or exc_short in ("KeyboardInterrupt", "TimeoutExpired"):
        return L_TIME
    if code == 137 or (code == 9 and not stripped):
        return L_OOM
    if _OOM_TEXT.search(tail) and not re.search(r"pip|conda|mamba", cmd[:40]):
        return L_OOM
    if code in (139, 134, 132, 136, 138, 135, 133, 131) or _CRASH_TEXT.search(tail):
        return L_CRASH
    if _TIME_TEXT.search(last3) and not re.search(r"curl: \(\d+\)|Read timed out|Connection timed out|urlopen|requests\.", tail):
        return L_TIME

    # 2. galaxy-cli structured error
    m = re.search(r'"category":\s*"(\w+)"', out)
    if m and re.search(r"galaxy[-_]cli", cmd):
        return L_CLI if m.group(1) == "usage_error" else L_GALAXY

    # 3. installation or build commands: label by the visible cause
    install = bool(_INSTALL_CMD.search(sh))
    if install:
        tb_text = out[out.rfind("Traceback"):] if "Traceback" in out else ""
        after_install_exc = has_tb and not re.search(r"site-packages/(?:pip|conda|mamba|setuptools)/|pip/_internal|pip/_vendor|"
                                                     r"conda/cli|No module named pip|ensurepip", tb_text)
        if not after_install_exc or re.search(r"ERROR: |error: subprocess-exited|Failed to build|libmamba", last3):
            lab = _classify_install(cmd, out, tail)
            if lab:
                return lab

    # 4. program missing
    mnf = _last(_CMD_NOT_FOUND, out)
    later_error = False
    if mnf:
        rest = out[mnf.end():]
        later_error = bool(_PY_EXC.search(rest)) or bool(_R_ERR.search(rest)) or bool(re.search(r"curl: \(\d+\)", rest))
        only_nsf = mnf.group(0).rstrip().endswith("No such file or directory") and "command not found" not in mnf.group(0)
        if only_nsf and code not in (127, 126):
            mnf = None
    if code == 127 and not later_error:
        return L_PROG
    if mnf and not later_error:
        if code == 126 and re.search(r"Permission denied", tail) and not re.search(r"Exec format|cannot execute binary", tail):
            return L_PERM
        if re.search(r"is not installed|not installed or not in PATH|not found in PATH|no \w* ?executable found", mnf.group(0), re.I) \
                and re.search(r"package|module|library|optional dependency|requirements are",
                              out[max(0, mnf.start() - 120):mnf.end() + 80], re.I):
            return L_PKG
        return L_PROG
    if code == 126:
        return L_PERM if re.search(r"Permission denied", out) else L_PROG

    # 5. Python exception (unless further error text follows it)
    if exc and (has_tb or exc_short in ("AssertionError", "SystemExit") or re.search(r"Error$|Exception$", exc_short)):
        py_lab = _python_label(exc, cmd, out)
        after = out[exc.end():]
        if after.strip() and _ERR_HINT.search(after):
            lab = _generic(cmd, sh, after, code, install)
            if lab and lab != L_NOT:
                return lab
        return py_lab

    # 6. R error
    rm = _last(_R_ERR, out)
    if rm and ("Execution halted" in out or re.search(r"Rscript|\bR\b\s+(?:-e|--|CMD|<)|\.R\b", cmd)):
        lab = _classify_r(out[rm.start():], cmd)
        if lab:
            return lab
        if install:
            return L_INSTALL
        if _BIO_TEXT.search(tail):
            return L_BIO
        return L_OTHER
    if "Execution halted" in last3:
        return _classify_r(tail, cmd) or L_OTHER

    # 7. generic text rules
    lab = _generic(cmd, sh, out, code, install)
    if lab:
        return lab

    # 8. no error text: probe, or nothing captured
    if not _ERR_HINT.search(out):
        if re.search(r"decompression OK, trailing garbage ignored", out):
            return L_NOT
        if _SEARCH_CMD.search(sh) or _SILENCED_LS.search(sh):
            return L_NOT
        if code == 1 and re.match(r"\s*(?:ls|find|stat|file|du|cat|head|wc)\b", sh) and re.search(r"2>\s*/dev/null|2>&1", sh):
            return L_NOT
        if stripped and re.search(r"exit\s+[1-9]\b|sys\.exit\(\s*[1-9]|raise SystemExit\(|quit\(\s*status\s*=\s*[1-9]|\bassert\s", cmd):
            return L_CHECK
        return L_NOMSG
    if _SEARCH_CMD.search(sh) and code == 1 and not re.search(
            r"(?:^|\n)\s*(?:\S+: )?(?:[Ee]rror|ERROR|fatal|FATAL)[: ]|Traceback|cannot|No such|not found|[Dd]enied", last3):
        return L_NOT
    # 9. the error line may have scrolled out of the last 10 lines: apply the text rules to the whole output
    lab = _generic(cmd, sh, out, code, install, n_tail=100000)
    if lab and lab != L_NOT:
        return lab
    return L_OTHER
