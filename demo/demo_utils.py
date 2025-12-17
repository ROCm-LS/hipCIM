#
# Copyright(c) [2025] Advanced Micro Devices, Inc. All rights reserved.
#
import subprocess
import re
import glob
import os
import importlib.metadata
import pyvips
from collections import Counter

# Given a WSI, generate a downscaled thumbnail, retaining the aspect ration
def generate_wsi_thumbnail(input_path, output_path, width):
    if not os.path.exists(output_path):
        image = pyvips.Image.thumbnail(input_path, width)
        image.write_to_file(output_path)

# Extract CPU information
def get_cpu_info():
    with open('/proc/cpuinfo', 'r') as f:
        cpuinfo = f.read()
    
    # Get model name
    model = re.search(r'model name\s+: (.*)', cpuinfo).group(1)
    
    # Get core counts
    physical_cores = len(re.findall(r'processor\s+: \d+', cpuinfo))
    threads = len(re.findall(r'processor\s+: ', cpuinfo))
    
    # Get frequency (in MHz, convert to GHz)
    freq = float(re.search(r'cpu MHz\s+: ([\d.]+)', cpuinfo).group(1)) / 1000
    
    return f"{model} ({physical_cores}C/{threads}T @ {freq:.1f} GHz)"

# Extract GPU information
def get_gpu_info():
    try:
        # Run rocminfo and capture output
        output = subprocess.check_output(['rocminfo'], text=True)
        lines = output.splitlines()

        gpus = []
        current_gpu = None
        for line in lines:
            marketing = re.search(r'Marketing Name:\s*(.+)', line)
            name = re.search(r'Name:\s*(gfx\d+)', line)
            if marketing:
                current_gpu = {'marketing_name': marketing.group(1), 'arch': None}
            if current_gpu is not None and name:
                current_gpu['arch'] = name.group(1)
                # Filter only AMD Instinct GPUs
                if current_gpu['marketing_name'].strip().startswith("AMD Instinct"):
                    gpus.append(current_gpu)
                current_gpu = None  # Reset for next block

        if not gpus:
            return "Information not available"

        # Count and summarize
        tuples = [(g['marketing_name'].strip(), g['arch']) for g in gpus if g['arch']]
        counter = Counter(tuples)
        info_strings = [
            f"{count} x {gpu} ({arch})"
            for (gpu, arch), count in counter.items()
        ]
        return ", ".join(info_strings)

    except Exception:
        return "Information not available"

# Extract pip package version
def get_package_version(pkg_name):
    try:
        version = importlib.metadata.version(pkg_name)
    except importlib.metadata.PackageNotFoundError:
        version = "Information not available"
    return version

# Convert a DLDataType to a familiar dtype string
def dl_datatype_to_str(dl_dtype):
    code_map = {0: 'int', 1: 'uint', 2: 'float'}
    base = code_map.get(dl_dtype.code, 'unknown')
    bits = dl_dtype.bits
    lanes = dl_dtype.lanes
    if lanes > 1:
        return f"{base}{bits}x{lanes}"
    else:
        return f"{base}{bits}"

# Mapping from full unit names to abbreviations/symbols
unit_map = {
    'micrometer': 'µm',
    'millimeter': 'mm',
    'centimeter': 'cm',
    'meter': 'm',
    'nanometer': 'nm',
    'pixel': 'px',
    'color': '',  # Not a spatial unit
}

# Calculate human-friendly file size
def filesize_h(filename):
    # Get the file size in bytes
    size = os.path.getsize(filename)

    # Convert bytes to KB, or MB or GB
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

