#!/usr/bin/env python3
"""Check manuscript prose against the house style in ../references/house-style.md.

    python check_style.py main.tex sections/*.tex
    python check_style.py draft.md
    pbpaste | python check_style.py -          # text on stdin

Two rules, both from the PI's review of a manuscript draft:

  1. No semicolons in prose (hard rule: any hit makes the exit status 1).
  2. Experimental results in the past tense (heuristic: hits are warnings to
     read, not errors, because some present-tense sentences are correct).

LaTeX handling: the preamble, comments, math, verbatim-like environments,
the bibliography, and the arguments of \\cite, \\ref, \\label, \\url, \\href,
\\includegraphics and similar commands are blanked before checking, so a
semicolon in $f(x;\\theta)$, a URL or a reference list is not reported.
Markdown handling: fenced code, inline code and $...$ math are blanked.
Line numbers always refer to the original file.

Exit status: 0 clean or warnings only, 1 semicolons found, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- blanking --

def _blank(m: re.Match) -> str:
    """Replace a match with spaces, keeping newlines so line numbers survive."""
    return re.sub(r"[^\n]", " ", m.group(0))


LATEX_BLOCK_ENVS = (
    "equation", "equation*", "align", "align*", "alignat", "alignat*", "gather", "gather*",
    "multline", "multline*", "eqnarray", "eqnarray*", "displaymath", "math", "split",
    "verbatim", "Verbatim", "lstlisting", "minted", "comment", "thebibliography",
    "tabular", "tabular*", "tabularx", "array", "tikzpicture", "filecontents", "filecontents*",
)
# Commands whose (last) braced argument is not prose.
LATEX_NONPROSE_CMDS = (
    "cite", "citep", "citet", "citealp", "autocite", "parencite", "textcite", "nocite",
    "ref", "eqref", "cref", "Cref", "autoref", "pageref", "label", "url", "href",
    "includegraphics", "input", "include", "bibliography", "bibliographystyle",
    "bibliographyfullrefs", "usepackage", "documentclass", "graphicspath", "setlength",
    "newcommand", "renewcommand", "providecommand", "DeclareSIUnit", "sisetup",
    "journal", "setboolean",
    "affil", "address", "email", "orcid",
)


def strip_latex(text: str) -> str:
    # Everything outside \begin{document} ... \end{document} when the file has one.
    m_begin = re.search(r"\\begin\{document\}", text)
    if m_begin:
        text = re.sub(r"[^\n]", " ", text[: m_begin.end()]) + text[m_begin.end():]
    m_end = re.search(r"\\end\{document\}", text)
    if m_end:
        text = text[: m_end.start()] + re.sub(r"[^\n]", " ", text[m_end.start():])
    # Comments: an unescaped % to end of line.
    text = re.sub(r"(?<!\\)%[^\n]*", _blank, text)
    # Block environments, matched by name so nesting of different envs is fine.
    for env in LATEX_BLOCK_ENVS:
        e = re.escape(env)
        text = re.sub(rf"\\begin\{{{e}\}}.*?\\end\{{{e}\}}", _blank, text, flags=re.S)
    # Display and inline math.
    text = re.sub(r"\$\$.*?\$\$", _blank, text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", _blank, text, flags=re.S)
    text = re.sub(r"\\\(.*?\\\)", _blank, text, flags=re.S)
    # Inline math keeps its $ delimiters so "is $1.2\times10^6$" still reads as "is <number>".
    text = re.sub(r"(?<!\\)\$(?:\\.|[^$\\])*?(?<!\\)\$", lambda m: "$" + _blank(m)[1:-1] + "$", text, flags=re.S)
    # Non-prose command arguments: \cmd*[opt]{arg}{arg}.
    cmds = "|".join(sorted(map(re.escape, LATEX_NONPROSE_CMDS), key=len, reverse=True))
    text = re.sub(rf"\\(?:{cmds})\*?(?:\[[^\]]*\])*(?:\{{[^{{}}]*\}})+", _blank, text)
    # \bibitem lines and thin-space macro \; outside math.
    text = re.sub(r"\\bibitem(?:\[[^\]]*\])?\{[^}]*\}[^\n]*", _blank, text)
    text = text.replace("\\;", "  ")
    return text


def strip_markdown(text: str) -> str:
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", _blank, text, flags=re.S | re.M)
    text = re.sub(r"`[^`\n]*`", _blank, text)
    text = re.sub(r"\$\$.*?\$\$", _blank, text, flags=re.S)
    text = re.sub(r"(?<!\\)\$[^$\n]+\$", _blank, text)
    text = re.sub(r"<[^>\n]+>", _blank, text)          # HTML tags and autolinks
    text = re.sub(r"&[a-zA-Z]+;|&#\d+;", _blank, text)  # HTML entities such as &nbsp;
    text = re.sub(r"\]\([^)\n]*\)", _blank, text)      # link targets
    return text


# ------------------------------------------------------------------ rules --

# Verbs that describe something done in the lab or in a simulation run.
_EXP_PARTICIPLES = (
    "measured|observed|obtained|recorded|extracted|fitted|fit|estimated|characteri[sz]ed|"
    "fabricated|demonstrated|achieved|acquired|imaged|detected|found|determined|calculated|"
    "simulated|tested|evaluated|confirmed|verified|reali[sz]ed|attained|reached|collected|"
    "averaged|normali[sz]ed|resampled|processed|applied|used|performed|conducted|swept|"
    "scanned|captured|compared|plotted|reduced|improved|increased|decreased|suppressed"
)
_WE_PRESENT = (
    "demonstrate|show|achieve|observe|measure|obtain|find|fabricate|characteri[sz]e|record|"
    "extract|fit|image|acquire|detect|reali[sz]e|attain|reach|perform|conduct|test|evaluate|"
    "compare|use|employ|apply|estimate|calculate|simulate|confirm|verify|see|note|collect|"
    "average|normali[sz]e|resample|process|sweep|scan|capture|reduce|improve|increase|"
    "decrease|suppress|integrate|couple|pattern|etch|deposit|anneal|bond|drive|bias|tune"
)
_DEVICE_NOUNS = (
    "device|modulator|resonator|ring|microring|microresonator|waveguide|laser|source|system|"
    "chip|PIC|circuit|interferometer|MZI|filter|coupler|detector|photodetector|image|B-scan|"
    "A-scan|PSF|spectrum|spectra|measurement|sample|prototype|setup|set-up|engine|"
    "transmitter|receiver|comb|sweep|link|probe|phantom|experiment|result|data"
)
_RESULT_VERBS = (
    "exhibits?|achieves?|shows?|demonstrates?|reaches?|yields?|provides?|delivers?|maintains?|"
    "attains?|displays?|reveals?|produces?|outperforms?|exceeds?|confirms?|operates?|"
    "remains?|stays?|drops?|falls?|rises?|increases?|decreases?|agrees?|matches?|sweeps?|covers?|"
    "spans?|emits?|resolves?|suppresses?"
)
# Figures of merit whose value, stated with "is" and a number, is a measured result.
_QUANTITIES = (
    "loss|losses|bandwidth|resolution|depth|range|sensitivity|Q|Q factor|Q-factor|linewidth|"
    "extinction ratio|V_?\\?pi|Vpi|Vπ|efficiency|rate|speed|SNR|signal-to-noise ratio|roll-off|"
    "FSR|noise|RIN|power|contrast|crosstalk|isolation|responsivity|accuracy|precision|error|"
    "linearity|duty cycle|repeatability|drift|uniformity|yield"
)
_NUMBER_START = r"(?:about\s+|approximately\s+|only\s+|below\s+|above\s+|over\s+|up\s+to\s+|less\s+than\s+|" \
                r"more\s+than\s+|as\s+(?:low|high|large|small)\s+as\s+|~|\\sim\s*|\\approx\s*)?" \
                r"(?:[-−]?\d|\$|\\(?:qty|SI|num|numrange|qtyrange)\b)"

TENSE_RULES = [
    (
        "present-passive",
        re.compile(rf"\b(is|are)\s+(?:\w+ly\s+)?({_EXP_PARTICIPLES})\b", re.I),
        "experimental step or outcome in present passive: use 'was/were {1}'",
    ),
    (
        "we-present",
        re.compile(rf"\b[Ww]e\s+(?:\w+ly\s+|also\s+|then\s+|further\s+)?({_WE_PRESENT})\b"),
        "experimental work in present tense: use the past ('we {0}' -> past form)",
    ),
    (
        "device-present",
        re.compile(rf"\b(?:the|this|our|each|both|all|these)\s+(?:[\w-]+\s+){{0,3}}?(?:{_DEVICE_NOUNS})s?\s+"
                   rf"(?:\w+ly\s+|also\s+)?({_RESULT_VERBS})\b", re.I),
        "measured behaviour stated in present tense: use the past ('{0}' -> past form)",
    ),
    (
        "value-is",
        re.compile(rf"\b(?:{_QUANTITIES})\s+(?:of\s+(?:the\s+)?[\w-]+\s+)?(is|are)\s+{_NUMBER_START}", re.I),
        "a figure of merit stated as '{0}' + value: use 'was/were'",
    ),
    (
        "results-show",
        re.compile(r"(?:^|(?<=[.!?]\s))(?:Images?|B-scans?|A-scans?|Measurements?|Spectra|Results?|Data|Experiments?)"
                   r"\s+(?:of\s+(?:[\w-]+\s+){1,4}?)?(shows?|reveals?|demonstrates?|confirms?|exhibits?)\b", re.M),
        "an observation stated in present tense: use the past ('{0}' -> past form)",
    ),
    (
        "has-measured",
        re.compile(r"\b(has|have)\s+(?:a|an)\s+(?:measured|loaded|intrinsic|fitted|extracted|experimental|record)\b", re.I),
        "a measured value introduced with '{0}': use 'had', or 'the measured ... was'",
    ),
    (
        "measured-is",
        re.compile(r"\b(?:measured|fitted|extracted|obtained|observed|recorded|achieved|experimental)\s+"
                   r"(?:[\w-]+\s+){0,4}?(is|are)\b", re.I),
        "a measured quantity followed by 'is/are': use 'was/were'",
    ),
]

# Present tense that is correct and must not be reported.
TENSE_ALLOW = re.compile(
    r"\b(?:Fig(?:ure)?s?\.?|Table|Section|Sec\.|Eq\.|Equation|Supplement(?:ary)?|Appendix|Movie|Visualization)"
    r"[\s~]*\S*\s+(?:shows?|presents?|plots?|compares?|summari[sz]es?|lists?|illustrates?|depicts?|gives?|describes?)\b",
    re.I,
)

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\\(\[])|\n\s*\n")


def display_text(original: str, clean: str) -> str:
    """The original text with non-prose lines blanked, for quoting context.

    A line that is entirely non-prose after cleaning (preamble, comment, code
    fence, equation) is blanked, and a trailing LaTeX comment is cut, so the
    quoted sentence stays inside the paragraph it belongs to. Same length and
    line breaks as the original, so positions carry over.
    """
    out = []
    for o, c in zip(original.split("\n"), clean.split("\n")):
        if not c.strip():
            out.append(" " * len(o))
        else:
            m = re.search(r"(?<!\\)%", o)
            out.append(o if not m else o[: m.start()] + " " * (len(o) - m.start()))
    return "\n".join(out)


def sentence_at(text: str, pos: int) -> str:
    """The sentence of the given text that contains position pos, on one line."""
    starts = [0] + [m.end() for m in SENTENCE_END.finditer(text) if m.end() <= pos]
    start = starts[-1]
    m = SENTENCE_END.search(text, pos)
    end = m.start() if m else len(text)
    s = " ".join(text[start:end].split())
    return s if len(s) <= 240 else s[:237] + "..."


def line_col(text: str, pos: int) -> tuple[int, int]:
    line = text.count("\n", 0, pos) + 1
    col = pos - (text.rfind("\n", 0, pos) + 1) + 1
    return line, col


def check(original: str, kind: str) -> list[dict]:
    clean = strip_latex(original) if kind == "tex" else strip_markdown(original) if kind == "md" else original
    shown = display_text(original, clean)
    findings = []
    for m in re.finditer(";", clean):
        line, col = line_col(original, m.start())
        findings.append({"rule": "semicolon", "level": "error", "line": line, "col": col,
                         "message": "semicolon in prose: split the sentence or rewrite with a conjunction",
                         "sentence": sentence_at(shown, m.start())})
    allowed_spans = [(m.start(), m.end()) for m in TENSE_ALLOW.finditer(clean)]
    taken = []  # spans already reported, so one clause gets one finding
    for name, rx, msg in TENSE_RULES:
        for m in rx.finditer(clean):
            if any(a <= m.start() < b for a, b in allowed_spans):
                continue
            if any(m.start() < b and a < m.end() for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            line, col = line_col(original, m.start())
            words = [g for g in m.groups() if g]
            findings.append({"rule": name, "level": "warning", "line": line, "col": col,
                             "message": msg.format(*(words + ["", ""])),
                             "match": " ".join(m.group(0).split()),
                             "sentence": sentence_at(shown, m.start())})
    findings.sort(key=lambda f: (f["line"], f["col"]))
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="files to check; '-' reads stdin")
    ap.add_argument("--kind", choices=["auto", "tex", "md", "text"], default="auto",
                    help="how to strip non-prose (default: from the file extension; stdin is plain text)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--no-tense", action="store_true", help="report semicolons only")
    a = ap.parse_args(argv)

    report, errors, warnings = {}, 0, 0
    for name in a.files:
        if name == "-":
            text, kind = sys.stdin.read(), ("text" if a.kind == "auto" else a.kind)
        else:
            p = Path(name)
            if not p.is_file():
                print(f"check_style: no such file: {name}", file=sys.stderr)
                return 2
            text = p.read_text(encoding="utf-8", errors="replace")
            kind = a.kind if a.kind != "auto" else {".tex": "tex", ".md": "md", ".markdown": "md"}.get(p.suffix.lower(), "text")
        found = check(text, kind)
        if a.no_tense:
            found = [f for f in found if f["rule"] == "semicolon"]
        report[name] = found
        errors += sum(f["level"] == "error" for f in found)
        warnings += sum(f["level"] == "warning" for f in found)

    if a.json:
        print(json.dumps({"files": report, "errors": errors, "warnings": warnings}, indent=2, ensure_ascii=False))
    else:
        for name, found in report.items():
            for f in found:
                tag = "ERROR" if f["level"] == "error" else "check"
                hit = f" [{f['match']}]" if "match" in f else ""
                print(f"{name}:{f['line']}:{f['col']}: {tag} {f['rule']}{hit}: {f['message']}")
                print(f"    {f['sentence']}")
        print(f"\n{errors} semicolon(s), {warnings} tense warning(s) in {len(report)} file(s).")
        if warnings:
            print("Tense warnings are candidates: rewrite experimental results in the past tense, keep the present for "
                  "what a figure shows, design facts and general physics. See references/house-style.md.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
