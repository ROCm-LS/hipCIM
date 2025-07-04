# Test and Coverage Comparison Tools

The following two Python scripts are used for comparing test results and code
coverage across different runs. These are especially useful in comparison of
AMD based runs against H100 runs, as well as in continuous integration
pipelines.

- `cucim_compare_junit.py`
    Compare two XML test reports 

- `cucim_compare_coverage.py`
    Compare two coverage.py XML reports

Note that these scripts are integrated into the `../run_amd` script as part of
the Python tests and the comparison reports are automatically written to the
files `junit-cucim_report.txt` and `cucim-coverage_report.txt`, respectively,
after each run.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
  - [Test Comparison](#test-comparison)
  - [Coverage Comparison](#coverage-comparison)
  - [Baselines](#baselines)
- [Examples](#examples)
- [Diagnostics](#diagnostics)
- [Next Steps](#next-steps)

---

## Features

### cucim_compare_junit.py

- Detects test regressions, fix-ups, additions, and removals.
- Prints a summary of total tests, test suite name, run time, host, and path.
- Ensures test suite consistency between runs.

### cucim_compare_coverage.py

- Compares overall line and branch coverage rates.
- Detects coverage regressions, improvements, and file-level changes.
- Displays detailed metadata: version, run timestamp, line and branch statistics.
- Handles divergent source paths gracefully.

---

## Requirements

- Python 3.7+
- Standard libraries only (no third-party dependencies)

---

## Usage

### Test Comparison

Script: `cucim_compare_junit.py`

#### Arguments

```bash
python cucim_compare_junit.py --baseline BASELINE_XML --report TEST_XML [--skip SKIPLIST]
```

| Argument     | Description                                                              | Required  |
|--------------|--------------------------------------------------------------------------|-----------|
| `--baseline` | Path to baseline XML file                                                | Yes       |
| `--report`   | Path to current test XML file                                            | Yes       |
| `--skip`     | Path to plain text file containing list of files to skip from comparison | No        |

#### Output

- Metadata for both baseline and test runs
- Total tests
- Diagnostics on:
  - Test suite mismatch
  - Total tests mismatch
- Summary of:
  - New passing tests
  - New failing tests
  - Fixed tests
  - Removed tests

---

### Coverage Comparison

Script: `cucim_compare_coverage.py`

#### Arguments

```bash
python cucim_compare_coverage.py --baseline BASELINE_XML --report COVERAGE_XML
```

| Argument     | Description                      | Required |
|--------------|----------------------------------|----------|
| `--baseline` | Path to baseline coverage XML    | Yes      |
| `--report`   | Path to current coverage XML     | Yes      |

#### Output

- Metadata for both baseline and test runs:
  - Source path
  - Coverage version
  - Timestamp of run
  - Line & branch statistics
  - Complexity
- Overall line rate delta
- Regressions and progressions at the file level
- New or removed files in test run

---

## Baselines

A collection of known test results from prior executions, including those from
competitive systems, is maintained under the directory `test_data/baseline/`. 
These baselines serve as reference points for comparison against current test
or coverage results.

### Naming Conventions

To simplify identification and tracking, test result files adhere to a
structured naming format that embeds the timestamp, host system, and versioning
information. This standardization aids reproducibility and clarity.

- Unit Test Results

    Format: `junit-cucim_YYYYMMDD_HHMMSS_hostname.xml`

    Example: `junit-cucim_20250320_071825_rocm-framework-h100-sxm-1.xml`

- Coverage Results

    Format: `cucim-coverage_VERSION_TIMESTAMP.xml`

    Example: `cucim-coverage_v1.3_1742457165573.xml`

- Expected Failures (Skip List)

    Format: `junit-cucim_skiplist_YYYYMMDD_HHMMSS_hostname.txt`

    Example: `junit-cucim_skiplist_20250320_071825_rocm-framework-h100-sxm-1.txt`

### Symbolic Links for Default Baselines

To streamline comparisons, symbolic links are maintained to always point to the
most recent test artifacts. These are used as the default baselines by the test
automation scripts unless explicitly overridden via command-line options.

- Latest unit test result
    ```
    junit-cucim_latest.xml
    ```

- Latest coverage result
    ```
    cucim-coverage_latest.xml
    ```

- Latest skip list
    ```
    junit-cucim_skiplist_latest.txt
    ```

---

## Examples

### Compare Test Reports

```bash
python cucim_compare_junit.py                \
   --baseline junit-cucim.xml                \
   --report AMD_lifescience/junit-cucim.xml
```

Sample output:

```
===== Test Report Comparison Summary =====

Baseline Report:
  File        : junit-cucim.xml
  Suite Name  : pytest
  Tests       : 10626
  Timestamp   : 2025-03-20T07:18:25.157139+00:00
  Hostname    : rocm-framework-h100-sxm-1

Current Report:
  File        : AMD_lifescience/junit-cucim.xml
  Suite Name  : pytest
  Tests       : 10617
  Timestamp   : 2025-04-29T12:34:40.305180+00:00
  Hostname    : hpe-hq-08

WARNING: Total test count differs: 10626 vs. 10617

===== Test Classification =====
  Total Tests           : 10627
  Skipped Test(s)       : 0
  Regression(s)         : 4840 (45.54%)
  Progression(s)        : 47 (0.44%)
  Known Failure(s)      : 0
  Changed Failure(s)    : 3
  Missing Test(s)       : 10
  Extra Test(s)         : 1

Missing Test Case(s):
  src.cucim.skimage.restoration.tests.test_j_invariant::test_calibrate_denoiser
  src.cucim.skimage.restoration.tests.test_j_invariant::test_calibrate_denoiser_extra_output
  src.cucim.skimage.restoration.tests.test_j_invariant::test_calibrate_denoiser_tv
  ...

Extra Test Case(s):
  tests.unit.clara.converter.test_converter::test_image_converter_stripe_4096x4096_256_jpeg

Regression(s):
  src.cucim.skimage._vendored.tests.test_morphology::test_binary_axes[binary_closing-0-origin0-0]
  src.cucim.skimage._vendored.tests.test_morphology::test_binary_axes[binary_closing-0-origin0-1]
  src.cucim.skimage._vendored.tests.test_morphology::test_binary_axes[binary_closing-0-origin1-0]
  ...

Progression(s):
  tests.performance.clara.test_read_region_memory_usage::test_read_random_region_cpu_memleak[testimg_tiff_stripe_4096x4096_256_deflate]
  tests.performance.clara.test_read_region_memory_usage::test_read_random_region_cpu_memleak[testimg_tiff_stripe_4096x4096_256_jpeg]
  tests.performance.clara.test_read_region_memory_usage::test_read_random_region_cpu_memleak[testimg_tiff_stripe_4096x4096_256_raw]
  ...

Changed Failure(s):
  tests.performance.clara.test_read_region_memory_usage::test_read_region_cuda_memleak
  tests.unit.clara.test_image_cache::test_get_shared_memory_cache
  ...
```

---

### Compare Coverage Reports

```bash
python cucim_compare_coverage.py                \
   --baseline cucim-coverage.xml                \
   --report AMD_lifescience/cucim-coverage.xml
```

Sample output:

```
==== Coverage Report Comparison ====

Baseline File: cucim-coverage.xml
  Source Path:     /home/goplanid/cucim/python/cucim
  Coverage Ver:    7.7.0
  Timestamp:       2025-03-20 13:22:45
  Lines Valid:     10,077
  Lines Covered:   9,384
  Line Rate:       93.12%
  Branches Valid:  0
  Branches Covered:0
  Branch Rate:     0.00%
  Complexity:      0.0

Report File: AMD_lifescience/cucim-coverage.xml
  Source Path:     /home/dgoplani/dgoplani_cucim/hipCIM/python/cucim
  Coverage Ver:    7.8.0
  Timestamp:       2025-04-29 18:48:16
  Lines Valid:     11,000
  Lines Covered:   8,524
  Line Rate:       77.49%
  Branches Valid:  0
  Branches Covered:0
  Branch Rate:     0.00%
  Complexity:      0.0

Line Rate Delta: -15.63%


New Files:
  - src/cucim/clara/converter/tiff.py: 90.29%
  - src/cucim/skimage/measure/tests/test_regionprops.py: 12.80%

Regressions:
  - src/cucim/skimage/_shared/_gradient.py: 96.55% vs. 93.10%
  - src/cucim/skimage/_shared/coord.py: 100.00% vs. 93.02%
  ...

Progressions:
  - src/cucim/clara/__init__.py: 42.86% vs. 100.00%
  - src/cucim/clara/cache/__init__.py: 0.00% vs. 100.00%
```

---

## Diagnostics

Test Comparison will emit diagnostics if:

- Test suite names differ → "ERROR: Test suite name mismatch"
- Total test count differs → "WARNING: Total test count mismatch"

Coverage Comparison:

- Does not raise errors for source path mismatches
- Prints line rate delta and categorizes changes

---

## Next Steps

Potential enhancement(s):

- Export diffs as JSON/XML for downstream tools
- Write comparison report to a file based on CLI option
- Integrate with CI/CD (e.g., GitHub Actions, GitLab, Jenkins)
- Colorized terminal output

