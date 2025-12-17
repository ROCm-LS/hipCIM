#
# Copyright(c) [2025] Advanced Micro Devices, Inc. All rights reserved.
#
import numpy as np
from scipy.ndimage import sobel
from scipy import ndimage as ndi
from skimage import color
from skimage.util import img_as_float32
from skimage.filters import gabor_kernel
from skimage.filters import threshold_otsu
from skimage.morphology import binary_dilation, disk
from skimage.morphology import remove_small_objects
from skimage.measure import label
from skimage.transform import rotate, warp, AffineTransform

# Convert an image to grayscale only if it is not already grayscale
def ensure_grayscale(img_array):
    # If image is already 2D (grayscale), return as is
    if img_array.ndim == 2:
        return img_array
    
    # If image is 3D with 3 or more channels (RGB or RGBA)
    elif img_array.ndim == 3 and img_array.shape[2] >= 3:
        # Use only the first three channels (R, G, B)
        return img_array[..., :3].mean(axis=-1)

    else:
        raise ValueError("Input image must be either grayscale or RGB.")

# Stain separation on CPU
def stain_separation(tile, stain_option):
    if stain_option:
        # Convert 4-channel (RGBA) regions to RGB
        ihc_rgb = color.rgba2rgb(np.asarray(tile))

        # Transform to colorspace where the stains are separated
        ihc_hed = color.rgb2hed(ihc_rgb)

        # Create an RGB image for visualizing each of the stains
        null = np.zeros_like(ihc_hed[:, :, 0])

        # Separate out selected stain
        if stain_option == "Hematoxylin":
            ihc_h = color.hed2rgb(np.stack((ihc_hed[:, :, 0], null, null), axis=-1))
            tile = ihc_h

        if stain_option == "Eosin":
            ihc_e = color.hed2rgb(np.stack((null, ihc_hed[:, :, 1], null), axis=-1))
            tile = ihc_e

        if stain_option == "DAB":
            ihc_d = color.hed2rgb(np.stack((null, null, ihc_hed[:, :, 2]), axis=-1))
            tile = ihc_d

    return tile

# Generate a Gabor filter using the parameters and return the filtered tile
# sigma: Controls the width of the Gaussian envelope. A larger
#        sigma will result in more smoothing; smaller details
#        may be suppressed, emphasizing larger structures.
# theta: Defines the orientation of the Gabor filter; helps in
#        detecting features oriented in different directions.
# lambda: Determines the frequency of the sinusoidal wave. A
#         smaller lambda emphasizes finer textures, while a
#         larger lambda highlights coarser patterns.
# psi: Changing psi can shift the sinusoidal component along
#      the spatial domain, which might reveal different
#      features depending on the phase shift.
# gamma: Controls the ellipticity of the Gaussian. A gamma less
#        than 1 creates elongated filters, which might be useful
#        for emphasizing features that appear more linear at
#        certain orientations.
def gabor_filter(tile, frequency=0.05, theta=0.0, sigma=1):
    # Convert input to float32 and grayscale
    tile = img_as_float32(np.asarray(tile))
    #tile = tile[..., :3].mean(axis=-1)
    tile = ensure_grayscale(tile)

    # Create a single Gabor kernel with input parameters
    kernel = gabor_kernel(frequency, theta=theta, sigma_x=sigma, sigma_y=sigma)

    # Apply the Gabor filter (real part only, as in your original code)
    filtered = ndi.convolve(tile, np.asarray(kernel.real), mode='wrap')

    # Compute mean and variance as features
    mean = filtered.mean()
    var = filtered.var()

    # Optionally, compute the "power" image (magnitude response)
    tile_norm = (tile - tile.mean()) / tile.std()
    power_img = np.sqrt(
        ndi.convolve(tile_norm, np.asarray(kernel.real), mode='wrap')**2 +
        ndi.convolve(tile_norm, np.asarray(kernel.imag), mode='wrap')**2
    )

    ## Name	        Type	    Description	                                    Typical Use
    ## ----         ----        -----------                                     -----------
    ## filtered	    2D array	Filtered image (real part)	                    Feature map, analysis
    ## mean	        Scalar	    Mean of filtered image	                        Compact feature
    ## var	        Scalar	    Variance of filtered image	                    Compact feature
    ## power_img	2D array	Magnitude of filter response (real + imag)	    Visualization, analysis

    #return filtered, mean, var, power_img
    return power_img

# Apply Sobel filter to detect edges
def sobel_edge(tile):
    # Convert the image to a numpy array
    img_array = np.array(tile)

    # Convert to grayscale for simplicity
    gray_img = ensure_grayscale(img_array)

    # Normalize to [0, 1]
    gray_img = (gray_img - gray_img.min()) / (gray_img.max() - gray_img.min() + 1e-8)

    # Apply sobel filter to detect edges
    sobel_x = sobel(gray_img, axis=0)
    sobel_y = sobel(gray_img, axis=1)
    sobel_edges = np.sqrt(sobel_x**2 + sobel_y**2)

    # Return detected edges
    return sobel_edges

# Apply binary dilation
def dilation(tile):
    # Convert the image to a numpy array
    img_array = np.array(tile)

    # Convert to grayscale for simplicity
    gray_img = ensure_grayscale(img_array)
    
    # Apply binary threshold
    thresh = threshold_otsu(gray_img)
    binary = gray_img > thresh

    # Apply dilation
    selem = disk(3)  # structuring element
    dilated = binary_dilation(binary, selem)

    # Convert the boolean dilated mask to a displayable format
    tile = dilated.astype(np.uint8) * 255

    return tile

# Remove small objects
def erase_small_objects(tile, min_size=100):
    # Convert RGBA to RGB
    if tile.shape[-1] == 4:
        tile = np.array(tile)[:, :, :3]

    # Handle grayscale or color tiles
    if tile.ndim == 3 and tile.shape[2] >= 3:
        # Convert RGB to grayscale
        gray_img = (
            0.2989 * tile[:, :, 0]
            + 0.5870 * tile[:, :, 1]
            + 0.1140 * tile[:, :, 2]
        )
    else:
        # Already grayscale (H, W)
        gray_img = tile

    # Apply binary threshold
    thresh = threshold_otsu(gray_img)
    binary = gray_img > thresh

    # Label connected components
    labeled = label(binary)

    # Remove small objects (e.g., smaller than 100 pixels)
    cleaned = remove_small_objects(labeled, min_size=min_size)

    # Convert to binary mask for display
    result = cleaned > 0
    tile = result.astype(np.uint8) * 255

    return tile

# Rotate patch by 45 degrees
def rotate_patch(tile, angle=45):
    # Ensure tile is a (H, W, C) NumPy array
    if tile.shape[-1] == 4:
        tile = np.asarray(tile)[:, :, :3]  # Remove alpha channel if present

    # Rotate image by 45 degrees
    rotated = rotate(
        tile,
        angle=angle,              # degrees counter-clockwise
        resize=False,             # keep original shape; set True to expand output
        center=None,              # rotate around image center
        preserve_range=True,      # maintain pixel value range
        order=1,                  # bilinear interpolation
        mode='constant',          # fill border with constant value (default=0)
        cval=0                    # value used for padding outside input bounds
    )

    return rotated

# Apply affine transformations to warp the tile
def affine_warp(tile, scale=(0.8, 0.8), rotation=0.2, shear=0.1, translation=(10, -5)):
    # Remove alpha if present
    if tile.shape[-1] == 4:
        tile = np.asarray(tile)[:, :, :3]

    # Define an affine transformation: scale, rotate, shear, translate
    tform = AffineTransform(
        scale=scale,                # shrink image
        rotation=rotation,          # ~11 degrees
        shear=shear,                # slight shear
        translation=translation     # x and y shift
    )

    # Apply warp using inverse mapping
    warped = warp(
        tile,
        inverse_map=tform.inverse,   # required
        preserve_range=True,
        output_shape=tile.shape[:2],  # same shape
        order=1,                      # bilinear interpolation
        mode='constant',
        cval=0
    )

    return warped

