import argparse
import xml.etree.ElementTree as ET
import datetime

# Parse the coverage report in XML
def parse_coverage(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    def safe_int(attr): return int(root.attrib.get(attr, 0))
    def safe_float(attr): return float(root.attrib.get(attr, 0.0))

    # Collect the metadata for reporting
    metadata = {
        "file": xml_path,
        "version": root.attrib.get("version", "?"),
        "timestamp": int(root.attrib.get("timestamp", 0)),
        "datetime": datetime.datetime.fromtimestamp(int(root.attrib.get("timestamp", 0)) / 1000),
        "lines_valid": safe_int("lines-valid"),
        "lines_covered": safe_int("lines-covered"),
        "line_rate": safe_float("line-rate"),
        "branches_valid": safe_int("branches-valid"),
        "branches_covered": safe_int("branches-covered"),
        "branch_rate": safe_float("branch-rate"),
        "complexity": safe_float("complexity"),
        "source": root.find("sources/source").text.strip() if root.find("sources/source") is not None else "N/A"
    }

    # Gather coverage details
    coverage_by_file = {}
    for pkg in root.findall(".//package"):
        for cls in pkg.findall(".//class"):
            file = cls.attrib["filename"]
            rate = float(cls.attrib["line-rate"])
            coverage_by_file[file] = rate

    return metadata, coverage_by_file

# Compare the coverage details between the baseline and the test report
def compare_coverage(baseline, report):
    baseline_meta, baseline_cov = parse_coverage(baseline)
    report_meta, report_cov = parse_coverage(report)

    result = {
        "baseline": baseline_meta,
        "report": report_meta,
        "delta": {
            "rate_change": report_meta["line_rate"] - baseline_meta["line_rate"],
            "regressions": [],
            "progressions": [],
            "new_files": [],
            "removed_files": [],
        }
    }

    # Build up the comparison report
    all_files = set(baseline_cov.keys()).union(report_cov.keys())
    for file in sorted(all_files):
        base = baseline_cov.get(file)
        rep = report_cov.get(file)

        if base is not None and rep is not None:
            delta = rep - base
            if delta > 0:
                result["delta"]["progressions"].append((file, base, rep))
            elif delta < 0:
                result["delta"]["regressions"].append((file, base, rep))
        elif base is None:
            result["delta"]["new_files"].append((file, rep))
        elif rep is None:
            result["delta"]["removed_files"].append((file, base))

    return result

def fmt_pct(val): return f"{val:.2%}"
def fmt_int(val): return f"{val:,}"

# Create a human-friendly metadata report
def format_metadata(label, meta):
    return [
        f"{label} File: {meta['file']}",
        f"  Source Path:     {meta['source']}",
        f"  Coverage Ver:    {meta['version']}",
        f"  Timestamp:       {meta['datetime'].strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Lines Valid:     {fmt_int(meta['lines_valid'])}",
        f"  Lines Covered:   {fmt_int(meta['lines_covered'])}",
        f"  Line Rate:       {fmt_pct(meta['line_rate'])}",
        f"  Branches Valid:  {fmt_int(meta['branches_valid'])}",
        f"  Branches Covered:{fmt_int(meta['branches_covered'])}",
        f"  Branch Rate:     {fmt_pct(meta['branch_rate'])}",
        f"  Complexity:      {meta['complexity']}",
    ]

# Create human-friendly comparison report
def format_output(data):
    lines = []
    lines.append("==== Coverage Report Comparison ====")
    lines.append("")

    lines.extend(format_metadata("Baseline", data["baseline"]))
    lines.append("")
    lines.extend(format_metadata("Report", data["report"]))
    lines.append("")

    lines.append(f"Line Rate Delta: {fmt_pct(data['delta']['rate_change'])}")
    lines.append("")

    if data["delta"]["new_files"]:
        lines.append("\nNew Files:")
        for file, rate in data["delta"]["new_files"]:
            lines.append(f"  - {file}: {fmt_pct(rate)}")

    if data["delta"]["removed_files"]:
        lines.append("\nRemoved Files:")
        for file, rate in data["delta"]["removed_files"]:
            lines.append(f"  - {file}: {fmt_pct(rate)}")

    if data["delta"]["regressions"]:
        lines.append("\nRegressions:")
        for file, base, rep in data["delta"]["regressions"]:
            lines.append(f"  - {file}: {fmt_pct(base)} vs. {fmt_pct(rep)}")

    if data["delta"]["progressions"]:
        lines.append("\nProgressions:")
        for file, base, rep in data["delta"]["progressions"]:
            lines.append(f"  - {file}: {fmt_pct(base)} vs. {fmt_pct(rep)}")

    return "\n".join(lines)

# MAIN
def main():
    parser = argparse.ArgumentParser(description="Compare two coverage XML reports.")
    parser.add_argument("--baseline", required=True, help="Baseline coverage XML")
    parser.add_argument("--report", required=True, help="New coverage XML")
    args = parser.parse_args()

    try:
        data = compare_coverage(args.baseline, args.report)
        print(format_output(data))
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()

