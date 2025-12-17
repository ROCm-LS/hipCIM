#
# Copyright(c) [2025] Advanced Micro Devices, Inc. All rights reserved.
#
tooltips = {
    # Sidebar > Tile Control
    'tile_size': "Adjust the size of the tile to extract from the image (in pixels). "
                 "Typical values are 128, 256, or 512. Larger tiles show more context, but may reduce detail.",

    'x_position': "Specify the X-coordinate (in pixels) for the top-left corner of the tile. "
                  "This determines the horizontal offset from the image origin.",

    'y_position': "Specify the Y-coordinate (in pixels) for the top-left corner of the tile. "
                  "This determines the vertical offset from the image origin.",

    # Sidebar > Stain Separation
    'stain_option': """
Select a stain to separate its contribution from the image. This is useful in histological analysis:
- **None**: No stain separation.
- **Eosin**: Highlights cytoplasm and extracellular matrix in pink.
- **Hematoxylin**: Stains nuclei blue/purple.
- **DAB**: Highlights specific antigens using a brown chromogen in immunohistochemistry.
""",

    # Sidebar > Feature Extraction
    'gabor': "Apply Gabor filter to highlight texture-rich patterns. "
             "Useful for detecting oriented structures like collagen fibers or muscle layers.",
    
    'sobel': "Apply Sobel filter to detect edges by computing the intensity gradient. "
             "Helps isolate boundaries and structural features.",

    # Sidebar > Morphology
    'dilation': "Perform binary dilation to expand bright (foreground) regions. "
                "Useful for connecting fragmented structures or filling small gaps.",
    
    'smallobjs': "Remove small, disconnected components from a binary mask. "
                 "Effective for eliminating noise or irrelevant regions based on size thresholding.",

    # Sidebar > Geometric Transformations
    'rotate': "Rotate the image counter-clockwise by 45 degrees. "
              "This is a fixed-angle rotation centered on the tile.",
    
    'warp': "Apply affine transformations (scale, rotate, shear, translate) "
            "to spatially distort the tile. Useful for data augmentation or geometric corrections."
}
