.. meta::
  :description: The hipCIM library is a robust open-source solution developed to significantly accelerate computer vision and image processing capabilities
  :keywords: ROCm-LS, life sciences, hipCIM documentation

.. _index:

**********************
hipCIM documentation
**********************

.. note::

    hipCIM is in an early access state. Running production workloads is not recommended.

The hipCIM library is a robust open-source solution developed to significantly accelerate computer vision and image processing capabilities, particularly for multidimensional images. The hipCIM library provides powerful support for GPU-accelerated I/O operations, coupled with an array of computer vision and image processing primitives designed for N-dimensional image data in fields such as biomedical imaging. It facilitates efficient loading and processing of images from modalities such as digital pathology, CT, MR, and PET.

One of the key strengths of hipCIM is its comprehensive suite of tools designed to facilitate the development of sophisticated image processing applications. Derived from the NVIDIA RAPIDS® open-source project cuCIM, hipCIM maintains full API compatibility with the `NVIDIA cuCIM library <https://github.com/rapidsai/cucim/tree/branch-25.04>`_, which is pivotal for developers looking to transition workloads to AMD devices seamlessly. This feature eliminates the need for :doc:`hipification <hipify:index>`, allowing for a smoother migration process without altering the existing codebase.

hipCIM key features include:

- **Efficient image I/O**–Expedites loading and saving of images, especially large ones like those in digital pathology.

- **N-dimensional image processing**–Enables processing of multidimensional images, which is common in biomedical imaging and other fields.

- **GPU acceleration**–Leverages the power of GPUs to expedite computationally intensive tasks like image processing.

- **Extensible toolkit**–Offers both C++ and Python APIs, as well as a flexible mechanism for extensions using plugins.

- **Interoperability**–Can be used with other libraries in the ROCm-LS ecosystem and easily interoperate with libraries like `CuPy <https://cupy.dev/>`_.

- **Accelerated workflows**–Helps accelerate workflows in digital pathology and other fields that utilize large, high-resolution images.

In essence, hipCIM provides a versatile platform that bridges the gap between different hardware ecosystems, thereby promoting flexibility and efficiency in the deployment of advanced image processing workloads.

The code is open and hosted at `<https://github.com/ROCm-LS/hipCIM>`_.

The documentation is structured as follows:

.. grid:: 2
  :gutter: 3

  .. grid-item-card:: Install

    * :ref:`installing-hipcim`

  .. grid-item-card:: Reference

    * :ref:`supported-features`

To contribute to the documentation, refer to
`Contributing to ROCm-LS <https://rocm.docs.amd.com/projects/rocm-ls/en/latest/contribution.html#rocm-ls-contribution>`_.

You can find licensing information on the
:doc:`Licensing <license>` page.
