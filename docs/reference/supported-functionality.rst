.. meta::
   :description: The hipCIM library is a robust open-source solution developed to significantly accelerate computer vision and image processing capabilities
   :keywords: ROCm-LS, life sciences, hipCIM installation

.. _supported-features:

*******************************
Supported hipCIM functionality
*******************************

hipCIM 1.0.00 is based on `cuCIM 25.04.00 <https://github.com/rapidsai/cucim/tree/branch-25.04>`_ and includes the following features:

.. list-table::

    * - **Functionality**

    * - | Core image interface (cucim.core):
        | - All primary image manipulation functions (read, write, and resample) are GPU-accelerated with CPU fallbacks.
        | - Metadata operations (accessing dtype, dims, and shape) run on CPU only.

    * - | Image processing (cucim.skimage):
        | - Nearly all transform operations (resize, rotate, and warp) are GPU-accelerated with CPU fallbacks.
        | - Complete filter suite (Gaussian, median, and edge detectors) benefits from GPU acceleration.
        | - Most morphological operations (erosion, dilation, and opening) are GPU-accelerated.

    * - | Segmentation:
        | - Several advanced segmentation algorithms (felzenszwalb, quickshift, and active_contour) lack GPU acceleration.
        | - Core segmentation operations such as watershed and SLIC are GPU-accelerated.

    * - | Color operations:
        | - All color space conversions (rgb2gray, rgb2hsv, and rgb2lab) are GPU-accelerated.
        | - Specialized operations for medical imaging, such as stain separation or combination, also benefit from GPU acceleration.

    * - | Whole slide imaging:
        | - Patch extraction operations are GPU-accelerated.
        | - Metadata operations run exclusively on the CPU.

    * - | Measurement functions:
        | - Core measurement functions like region labeling are GPU-accelerated.
        | - Some advanced functions like ``marching_cubes`` lack GPU acceleration.

Limitations
------------

- Support for multilevel TIFF images is under development.

- No Support for JPEG2K compression.

- No GDS support

- No Dask support

- The following image processing operations are not supported:

  - affine, similarity, euclidean , threshold_niblack , threshold_sauvola, convex_hull_image ,corner_fast ,denoise_bilateral, denoise_wavelet, wiener, richardson_lucy, unsupervised_wiener, estimate_sigma, random_walker, felzenszwalb,slic, quickshift, watershed, active_contour and all exposure operations.

- Registration:

  - All registration functions (optical flow and demons) are GPU-accelerated but typically lack CPU fallbacks.

- Clara DL pipeline:

  - Data loading has partial GPU acceleration.

  - Most Clara transformations are GPU-accelerated with CPU fallbacks.
