#!/usr/bin/env python3
# Copyright AMD CORPORATION.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Filter an llvm-cov JSON export to only the files listed in a diff list.

llvm-cov export records absolute build-time paths (e.g.
/src/hipcim/cpp/src/cucim/loader/cuimage_loader.cpp) while the diff list
produced by `git diff --name-only` contains repository-relative paths (e.g.
cpp/src/cucim/loader/cuimage_loader.cpp).  This script matches entries using
str.endswith() so that the path prefix introduced by the build environment is
irrelevant.

Usage:
    python3 hipcim_filter_cpp_coverage.py <difflist> <input_json> <output_json>

Arguments:
    difflist     Path to difflist.txt (one relative source path per line).
    input_json   Path to the full llvm-cov JSON export.
    output_json  Path to write the filtered JSON (may be the same as input_json).
"""

import json
import sys


def main():
    if len(sys.argv) != 4:
        print(
            f"Usage: {sys.argv[0]} <difflist> <input_json> <output_json>",
            file=sys.stderr,
        )
        sys.exit(1)

    difflist_path, input_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(difflist_path) as f:
        diff_paths = [line.strip() for line in f if line.strip()]

    if not diff_paths:
        print("Diff list is empty; writing unfiltered coverage JSON.")
        if input_path != output_path:
            import shutil
            shutil.copy2(input_path, output_path)
        return

    with open(input_path) as f:
        data = json.load(f)

    total_before = sum(len(entry["files"]) for entry in data["data"])

    for entry in data["data"]:
        entry["files"] = [
            file_entry for file_entry in entry["files"]
            if any(file_entry["filename"].endswith(p) for p in diff_paths)
        ]
        # Filter functions to match retained files
        retained = {file_entry["filename"] for file_entry in entry["files"]}
        entry["functions"] = [
            fn for fn in entry.get("functions", [])
            if fn.get("filenames") and any(f in retained for f in fn["filenames"])
        ]

    total_after = sum(len(entry["files"]) for entry in data["data"])
    print(
        f"Filtered coverage: {total_before} -> {total_after} files "
        f"({len(diff_paths)} paths in diff list)"
    )

    with open(output_path, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
