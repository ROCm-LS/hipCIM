# =============================================================================
# MIT License
#
# Copyright (C) 2024-2026 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

import time
import argparse
from cucim import CuImage

def process_image(image_path, use_gpu = False):
    # Load and process the image on GPU  
    start_time = time.time()  
    image = CuImage(image_path)

    # Gather image data
    resolutions = image.resolutions
    level_dimensions = resolutions["level_dimensions"]
    level_count = resolutions["level_count"]
    print(f"Image details for {image_path}:")
    print(f" - Dimensions: {level_dimensions}")
    print(f" - Levels: {level_count}")
    print(f" - Device: {image.device}")  
    print(f" - Shape: {image.shape}")  
    print(f" - Dtype: {image.dtype}")  
    print(f" - Loaded: {image.is_loaded}")  
    print()  

    # Select device based on user input
    device = "cpu"
    if use_gpu:
        device = "cuda"

    # Extract subresolution image
    data = image.read_region( device=device )

    # Process extracted data
    duration = time.time() - start_time
    print(f"{device} processing time for {image_path}: {duration:.4f} seconds")
  
    # Print key details
    print(f"Subresolution image details for {image_path}:")
    print(f" - Device: {data.device}")  
    print(f" - Shape: {data.shape}")  
    print(f" - Dtype: {data.dtype}")  
    print(f" - Loaded: {data.is_loaded}")  
    print()  
  
if __name__ == "__main__":  
    # Set up argument parser  
    parser = argparse.ArgumentParser(description='Process images with cucim on GPU.')
    parser.add_argument('images', metavar='I', type=str, nargs='+',
                        help='One or more image files to process')
    parser.add_argument('--use-gpu', action='store_true',
                        help='Use GPU for processing') 

    args = parser.parse_args()
  
    # Process each image from the command line arguments
    for image_path in args.images: 
        try:
            process_image(image_path, use_gpu=args.use_gpu)
            print(f"Success processing {image_path}")
        except Exception as e:
            print(f"Failed to process {image_path}: {str(e)}")

