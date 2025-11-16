import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
import os
import json


# Parse JUnit test report file
def parse_junit_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Expecting one testsuite node
    suite = root.find("testsuite")
    if suite is None:
        raise ValueError(f"No <testsuite> found in {file_path}")

    # Gather metadata for reporting
    metadata = {
        "name": suite.attrib.get("name", "unknown"),
        "tests": int(suite.attrib.get("tests", 0)),
        "failures": int(suite.attrib.get("failures", 0)),
        "errors": int(suite.attrib.get("errors", 0)),
        "skipped": int(suite.attrib.get("skipped", 0)),
        "time": suite.attrib.get("time", "0"),
        "timestamp": suite.attrib.get("timestamp", "unknown"),
        "hostname": suite.attrib.get("hostname", "unknown"),
    }

    # Classify results
    results = {}
    for case in suite.findall("testcase"):
        name = case.attrib.get("classname", "") + "::" + case.attrib.get("name", "")
        if case.find("failure") is not None:
            results[name] = "failure"
        elif case.find("error") is not None:
            results[name] = "error"
        elif case.find("skipped") is not None:
            results[name] = "skipped"
        else:
            results[name] = "passed"

    return metadata, results

# Read in the optional skip list
def read_skiplist(path):
    with open(path, "r") as f:
        return set(line.strip() for line in f if line.strip() and not line.startswith("#"))

# Classify the test report against the baseline report
def classify_tests(baseline, current, skiplist):
    regressions = []
    progressions = []
    known_failures = []
    changed_failures = []
    missing_tests = []
    extra_tests = []

    # Unify the test list from both the baseline and the test report
    all_tests = set(baseline) | set(current)

    # Iterate over the test report, clasifying each result
    for test in all_tests:
        base_status = baseline.get(test, "missing")
        curr_status = current.get(test, "missing")

        # Ignore failures from the skip list, if specified
        if test in skiplist:
            if curr_status != "passed":
                known_failures.append(test)
            continue

        if base_status in ("failure", "error", "skipped") and curr_status == "passed":
            progressions.append(test)
        elif base_status == "passed" and curr_status in ("failure", "error", "skipped"):
            regressions.append(test)
        elif base_status != curr_status and base_status != "missing" and curr_status != "missing":
            changed_failures.append(test)
        elif base_status == 'missing' and curr_status != "missing":
            extra_tests.append(test)
        elif base_status != 'missing' and curr_status == "missing":
            missing_tests.append(test)

    return regressions, progressions, known_failures, changed_failures, missing_tests, extra_tests

# Display details of the run
def print_metadata(label, meta, path):
    print(f"{label} Report:")
    print(f"  File        : {os.path.abspath(path)}")
    print(f"  Suite Name  : {meta['name']}")
    print(f"  Tests       : {meta['tests']}")
    print(f"  Timestamp   : {meta['timestamp']}")
    print(f"  Hostname    : {meta['hostname']}")
    print()

# MAIN
def main():
    # Define command line arguments
    parser = argparse.ArgumentParser(description="Compare JUnit XML test results.")
    parser.add_argument("--baseline", required=True, help="Path to baseline XML file")
    parser.add_argument("--report", required=True, help="Path to new result XML file")
    parser.add_argument("--skip", help="Optional skiplist file")
    args = parser.parse_args()

    # Parse respective report files
    base_meta, baseline = parse_junit_xml(args.baseline)
    curr_meta, current = parse_junit_xml(args.report)
    skiplist = read_skiplist(args.skip) if args.skip else set()

    print("\n===== Test Report Comparison Summary =====\n")

    print_metadata("Baseline", base_meta, args.baseline)
    print_metadata("Current", curr_meta, args.report)

    # Print a diagnostic if the testsuite names differ between the baseline and
    # the current test report
    # (potentially invalid comparison)
    if base_meta["name"] != curr_meta["name"]:
        print(f"WARNING: Test suite names differ: '{base_meta['name']}' vs. '{curr_meta['name']}'\n")

    # Print a diagnostic if the number of tests differ between the baseline run
    # and the current test run
    # (potential mis-configuration)
    if base_meta["tests"] != curr_meta["tests"]:
        print(f"WARNING: Total test count differs: {base_meta['tests']} vs. {curr_meta['tests']}\n")

    # Classify the current test report against the baseline
    regressions, progressions, known_failures, changed_failures, missing_tests, extra_tests = classify_tests(baseline, current, skiplist)
    total_tests = len(set(baseline) | set(current))
    regression_pct = len(regressions) * 100 / total_tests
    progression_pct = len(progressions) * 100 / total_tests

    # Display a formatted comparion report
    print("===== Test Classification =====")
    print(f"  Total Tests           : {len(set(baseline) | set(current))}")
    print(f"  Skipped Test(s)       : {len(skiplist)}")
    print(f"  Regression(s)         : {len(regressions)} ({regression_pct:.2f}%)")
    print(f"  Progression(s)        : {len(progressions)} ({progression_pct:.2f}%)")
    print(f"  Known Failure(s)      : {len(known_failures)}")
    print(f"  Changed Failure(s)    : {len(changed_failures)}")
    print(f"  Missing Test(s)       : {len(missing_tests)}")
    print(f"  Extra Test(s)         : {len(extra_tests)}")

    # List out each test case categorically
    if missing_tests:
        print("\nMissing Test Case(s):")
        for test in sorted(missing_tests):
            print(f"  {test}")

    if extra_tests:
        print("\nExtra Test Case(s):")
        for test in sorted(extra_tests):
            print(f"  {test}")

    if regressions:
        print("\nRegression(s):")
        for test in sorted(regressions):
            print(f"  {test}")

    if progressions:
        print("\nProgression(s):")
        for test in sorted(progressions):
            print(f"  {test}")

    if known_failures:
        print("\nKnown Failure(s):")
        for test in sorted(known_failures):
            print(f"  {test}")

    if changed_failures:
        print("\nChanged Failure(s):")
        for test in sorted(changed_failures):
            print(f"  {test}")


if __name__ == "__main__":
    main()
