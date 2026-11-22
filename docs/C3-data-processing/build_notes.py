"""Build the C-II data-processing report from source and run artifacts.

Requires reportlab==4.4.9 (available in the Codex bundled Python runtime).
This C-II report is a component of the full group report.
"""
import csv
import hashlib
from html import escape
import json
from pathlib import Path
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                               TableStyle, PageBreak, Preformatted, KeepTogether)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = A4[0] - 38 * mm
INK = colors.HexColor("#172A3A")
ACCENT = colors.HexColor("#176B73")
PALE = colors.HexColor("#ECF4F5")
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle("PacketTitle", fontName="Helvetica-Bold", fontSize=23,
                          leading=27, textColor=INK, spaceAfter=8))
STYLES.add(ParagraphStyle("PacketHeading", fontName="Helvetica-Bold", fontSize=13,
                          leading=17, textColor=ACCENT, spaceBefore=11, spaceAfter=6))
STYLES.add(ParagraphStyle("PacketBody", fontName="Helvetica", fontSize=10,
                          leading=14, textColor=INK, spaceAfter=7))
STYLES.add(ParagraphStyle("PacketSmall", parent=STYLES["PacketBody"], fontSize=8,
                          leading=11, spaceAfter=5))
STYLES.add(ParagraphStyle("PacketCell", fontName="Helvetica", fontSize=8,
                          leading=10, textColor=INK))
STYLES.add(ParagraphStyle("PacketCode", fontName="Courier", fontSize=7.2,
                          leading=9.6, textColor=INK, spaceAfter=5))
STYLES.add(ParagraphStyle("PacketSource", fontName="Courier", fontSize=7.3,
                          leading=9.2, textColor=INK, spaceAfter=0))


def p(text, style="PacketBody"):
    return Paragraph(text, STYLES[style])


def inline(text):
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)


def table(headers, rows, widths, compact=False):
    data = [[p(escape(str(v)), "PacketCell") for v in headers]]
    data += [[p(escape(str(v)), "PacketCell") for v in row] for row in rows]
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 if compact else 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 if compact else 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FA")]),
    ]))
    return result


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(ACCENT)
    canvas.line(19 * mm, 16 * mm, A4[0] - 19 * mm, 16 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(INK)
    canvas.drawString(19 * mm, 11 * mm, "SWE309 | Member3 | C-II Data Processing")
    canvas.drawRightString(A4[0] - 19 * mm, 11 * mm, str(document.page))
    canvas.restoreState()


def build():
    verification = json.loads((ROOT / "evidence/C3/verification.json").read_text(encoding="utf-8"))
    if verification.get("status") != "passed":
        raise RuntimeError("Build requires successful current C3 verification")
    for path, digest in verification["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise RuntimeError("Source changed after verification; rerun C3 checks")
    runtime = verification["datasets"]["extended"]["runtime"]
    with (ROOT / "data/aggregated/c3/extended/audit.csv").open(encoding="utf-8", newline="") as stream:
        audit = list(csv.DictReader(stream))
    story = [p("C-II / Rating-count pipeline", "PacketTitle"),
             p("DATA PROCESSING REPORT  |  22 NOVEMBER 2026", "PacketSmall"),
             p("Member3 has confirmed manual review of the report content.", "PacketSmall")]
    # Preserve the actual technical prose, with references and limitations.
    text = (HERE / "report.md").read_text(encoding="utf-8")
    selected = text.split("## Results and interpretation\n\n", 1)[1].split("## Reflection and integration boundary", 1)[0]
    reflection = text.split("## Reflection and integration boundary\n\n", 1)[1].split("## Evidence and scope", 1)[0]
    for block in selected.strip().split("\n\n"):
        if block.startswith("## "):
            story.append(p(inline(block[3:]), "PacketHeading"))
        else:
            story.append(p(inline(" ".join(block.splitlines()))))
    story.append(PageBreak())
    story += [p("01 / Table 2 reference trace", "PacketTitle"),
              p("Table 2 hand trace. CSV record numbers exclude the header. Synthetic timestamps were added; the assignment provides only IDs and ratings.")]
    story.append(table(["Split", "Original records", "Excluded"], [
        ["1", "r01 Good; r02 Poor; r03 Good; r04 OK", "None"],
        ["2", "r05 OK; r06 Good; r07 Poor; r08 Good", "None"],
        ["3", "r09 OK; r07 Poor; r10 Good; r11 Gd", "Record 10: duplicate r07. Record 12: illegal Gd."],
    ], [32, 259, WIDTH-291]))
    story += [p("Map output after global ID deduplication", "PacketHeading"),
              table(["Split", "Pairs"], [
                  ["1", "(Good,1), (Poor,1), (Good,1), (OK,1)"],
                  ["2", "(OK,1), (Good,1), (Poor,1), (Good,1)"],
                  ["3", "(OK,1), (Good,1)"],
              ], [32, WIDTH-32]),
              p("Shuffle and reduce", "PacketHeading"),
              table(["Key", "Grouped values", "Reduce output"], [
                  ["Good", "[1,1,1,1,1]", "(Good,5)"],
                  ["OK", "[1,1,1]", "(OK,3)"],
                  ["Poor", "[1,1]", "(Poor,2)"],
              ], [70, 215, WIDTH-285]),
              p("<b>12 = 1 duplicate + 1 invalid + 10 accepted; 5 + 3 + 2 = 10.</b> Deduplicating within each printed split alone would miss r07 across splits 2 and 3. ID deduplication needs its own global grouping before rating counting."),
              p("Extended reference arithmetic", "PacketHeading"),
              table(["Rating", "Accepted IDs", "Count"], [
                  ["Good", "r01 r03 r06 r08 r10 r12 r15 r18 r21 r24 r27 r30", "12"],
                  ["OK", "r04 r05 r09 r13 r16 r19 r22 r25 r28 r31", "10"],
                  ["Poor", "r02 r07 r14 r17 r20 r23 r26 r29", "8"],
              ], [55, WIDTH-100, 45]),
              p("Twenty new accepted IDs contribute 7/7/6. Add Table 2's 5/3/2 to obtain 12/10/8. <b>40 = 5 duplicates + 5 invalid ratings + 30 accepted.</b> Full row-level reference and actual results follow."),
              PageBreak(), p("02 / Full 40-record audit", "PacketTitle"),
              p("Actual Spark audit of the complete synthetic input. The first 12 rows preserve Table 2. All timestamps are fictional ISO 8601 values on 22 November 2026 (UTC+08:00). Quotes below make rating whitespace/empty strings visible; quotes are display notation.", "PacketSmall")]
    story.append(table(["Row", "ID", "Rating", "submitted_at", "Disposition"], [
        [r["source_row"], r["response_id"], repr(r["rating"]), r["submitted_at"], r["status"]] for r in audit
    ], [27, 35, 65, 160, WIDTH-287], compact=True))
    story += [Spacer(1, 8), p("Source: data/aggregated/c3/extended/audit.csv. Every ID/rating/status matches the separate expected-ledger.csv fixture. Source ordinal is assigned before repartitioning; record 40 does not replace record 14.", "PacketSmall"), PageBreak(),
              p("03 / Actual execution evidence", "PacketTitle"),
              p("The following table is generated from successful verification.json, not from expected values. All three subprocess exit codes were zero.")]
    story.append(table(["Dataset", "Input", "Accepted", "Duplicate", "Invalid", "Good/OK/Poor"], [
        [label, d["input_rows"], d["accepted"], d["duplicate"], d["invalid_rating"],
         "/".join(str(d["counts"][r]) for r in ("Good", "OK", "Poor"))]
        for label, d in verification["datasets"].items()
    ], [70, 44, 60, 60, 48, WIDTH-282]))
    story += [p("Observed runtime", "PacketHeading"),
              p(f"Windows; Python {runtime['python']}; Spark {runtime['spark']}; Java {runtime['java']}. Master: {runtime['master']}. Input and shuffle partitions: 4; AQE disabled. No cloud region. Verified at {verification['verified_at_utc']}.", "PacketSmall"),
              p("Eight real-Spark tests passed: reference totals/ledger and prefix; partition and delivery-order invariance; invalid-first duplicate; exact ratings and missing IDs; empty input; quoted/Unicode SQL parameter binding; CSV contract errors; output consistency and unchanged source.", "PacketSmall"),
              p("Physical plan excerpt", "PacketHeading"),
              Preformatted("LocalTableScan\n  Exchange RoundRobinPartitioning(4)\n    Exchange hashpartitioning(response_id, 4)\n      Sort -> Window row_number -> disposition\n        Cache -> Filter accepted\n          partial_count -> Exchange by rating\n            final HashAggregate count", STYLES["PacketCode"]),
              p("This is a readable outline of execution-plan.txt, not a terminal screenshot. The raw formatted plans, actual sanitized transcript and machine-readable verification are stored alongside the code. Native-Hadoop/winutils and PySpark socket ResourceWarnings in the transcript are nonfatal for the successful route; no native Hadoop writer or external winutils binary was used.", "PacketSmall"),
              p("Reproduction", "PacketHeading"),
              Preformatted("py -3.12 -m venv .venv/c3-runtime\n$py = '.venv/c3-runtime/Scripts/python.exe'\n& $py -m pip install -r processing/spark/requirements.txt\n# Set JAVA_HOME to Java 17 if not already configured.\n& $py processing/spark/verify_c3.py", STYLES["PacketCode"]),
              p("The runner can discover this computer's checksum-verified portable JRE in ignored .venv/java/. It changes no global settings.", "PacketSmall"),
              p("Reflection and integration boundary", "PacketHeading"),
              p(inline(" ".join(reflection.splitlines())), "PacketSmall"),
              PageBreak(), p("04 / Sources and evidence map", "PacketTitle")]
    refs = [
        ("[1] Apache Spark 3.5.7. Window functions.", "https://spark.apache.org/docs/3.5.7/sql-ref-syntax-qry-select-window.html"),
        ("[2] Apache Spark 3.5.7. RDD programming guide.", "https://spark.apache.org/docs/3.5.7/rdd-programming-guide.html"),
        ("[3] Apache Spark 3.5.7. Performance tuning.", "https://spark.apache.org/docs/3.5.7/sql-performance-tuning.html"),
        ("[4] Zaharia et al. (2012). Resilient Distributed Datasets. NSDI '12, pp. 15-28.", "https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf"),
        ("[5] Apache Spark 3.5.7. Cluster mode overview.", "https://spark.apache.org/docs/3.5.7/cluster-overview.html"),
        ("[6] Apache Spark 3.5.7. PySpark installation.", "https://spark.apache.org/docs/3.5.7/api/python/getting_started/install.html"),
        ("[7] Dean and Ghemawat (2004). MapReduce. OSDI '04, pp. 137-150.", "https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/"),
    ]
    for title, url in refs:
        story.append(p(escape(title) + f'<br/><link href="{url}" color="#176B73">Official source</link>', "PacketSmall"))
    story += [p("Sources checked 22 November 2026. Full dated release/region register and runtime-source metadata: docs/C3-data-processing/sources.md. Original case workload: assignment Table 1; original trace records: Table 2, p. 9.", "PacketSmall"),
              p("Files for independent reproduction", "PacketHeading")]
    for item in ["processing/spark/rating_count.py - actual pipeline (complete source follows)",
                 "processing/spark/verify_c3.py - runs jobs/tests and compares every row",
                 "tests/processing/test_rating_count.py - eight edge and integration tests",
                 "tests/processing/expected-ledger.csv - independent reference disposition",
                 "data/synthetic/c3-table2.csv and c3-responses.csv - immutable input",
                 "data/aggregated/c3/table2/ and extended/ - real complete outputs",
                 "evidence/C3/run.txt and verification.json - actual command evidence",
                 "evidence/C3/sync-check.json - latest upstream/protected-file check"]:
        story.append(p(escape(item), "PacketSmall"))
    story += [p("Input integrity", "PacketHeading")]
    for name, dataset in verification["datasets"].items():
        story.append(p(escape(name) + " SHA-256:", "PacketSmall"))
        story.append(Preformatted(dataset["input_sha256"], STYLES["PacketCode"]))
    story += [PageBreak(), p("Appendix / Executed program", "PacketTitle"),
              p("Complete rating_count.py at packet build time. Tests and the reproduction runner remain separate repository files. Wrapped long lines are marked with indentation for readability, not intended for copying from PDF.", "PacketSmall")]
    lines = []
    for number, line in enumerate((ROOT / "processing/spark/rating_count.py").read_text(encoding="utf-8").splitlines(), 1):
        wrapped = textwrap.wrap(line, width=100, replace_whitespace=False, drop_whitespace=False) or [""]
        lines.append(f"{number:3d} " + wrapped[0])
        lines.extend("    " + part for part in wrapped[1:])
    # Separate flowables per source line keep page splitting reliable.
    for line in lines:
        story.append(Preformatted(line, STYLES["PacketSource"], dedent=0))
    output = HERE / "c3-working-notes.pdf"
    document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=19*mm,
                                 leftMargin=19*mm, topMargin=18*mm, bottomMargin=22*mm,
                                 title="C-II Rating-count pipeline - data-processing report",
                                 author="Member 3")
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output.name)


if __name__ == "__main__":
    build()
