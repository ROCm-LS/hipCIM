.. meta::
   :description: The hipCIM library is a robust open-source solution developed to significantly accelerate computer vision and image processing capabilities
   :keywords: ROCm-LS, life sciences, hipCIM installation

.. _installing-hipcim:

===================
Installing hipCIM
===================

This topic discusses how to install hipCIM using the following options:

- AMD PyPI (for users)

- Build from source (for developers)

Prerequisites
**************

- Ubuntu 22.04 or later

- ROCm 6.4.0 or later

- Python 3.10 or later

- AMD Instinct MI300 series accelerators (gfx942)

Also, install the following ROCm components before installing hipCIM:

- `rocJPEG <https://rocm.docs.amd.com/projects/rocJPEG/en/latest/>`_

- `amd-cupy <https://pypi.amd.com/simple/amd-cupy/>`_ 13.0 or later

.. _install-package:

Installing hipCIM using AMD PyPI
*********************************

Packaged versions of hipCIM and its dependencies are distributed via `AMD PyPI <https://pypi.amd.com/simple/>`_. This section discusses how to install hipCIM using this package index. This installation method should be used by hipCIM users. hipCIM developers should use the :ref:`source-build`

1. Optional: Use ROCm Docker to get started:

   To run it inside a Docker, use:

   .. code-block:: shell

      docker pull rocm/dev-ubuntu-22.04-complete

      docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
            --shm-size=128GB --network=host --device=/dev/kfd     \
            --device=/dev/dri --group-add video -it               \
            -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
                                             rocm/dev-ubuntu-22.04:6.4.1-complete

   For bare metal, skip this step.

2. Install system dependencies:

   .. code-block:: shell

      sudo apt update
      sudo apt install -y lsb-release software-properties-common libopenslide0 python3.10-venv rocjpeg
      sudo apt install -y rocthrust-dev hipcub hipblas \
                  hipblas-dev hipfft hipsparse \
                  hiprand rocsolver rocrand-dev

3. Create the Python virtual environment:

   .. code-block:: shell

      pip install --upgrade pip
      python3 -m venv hipcim
      source hipcim/bin/activate

4. Install hipCIM using pip

   .. code-block:: shell

      pip install amd-hipcim --extra-index-url=https://pypi.amd.com/simple

5. Verify installation

   .. code-block:: shell

      $pip show -v amd-hipcim
      Name: amd-hipcim
      Version: 1.0.0b0
      Summary: hipCIM - an extensible toolkit designed to provide GPU accelerated I/O, computer vision & image processing primitives for N-Dimensional images with a focus on biomedical imaging.
      Home-page: https://rocm.docs.amd.com/projects/hipcim/en/latest/
      Author: AMD Corporation
      Author-email:
      License: Apache 2.0
      Location: /home/kthatipa/work/hipCIM/hipcim_build/lib/python3.12/site-packages
      Requires: click, lazy-loader, numpy, scikit-image, scipy
      Required-by:
      Metadata-Version: 2.4
      Installer: pip
      Classifiers:
         Development Status :: 4 - Beta
         Intended Audience :: Developers
         Intended Audience :: Education
         Intended Audience :: Science/Research
         Intended Audience :: Healthcare Industry
         Topic :: Scientific/Engineering
         Operating System :: POSIX :: Linux
         Environment :: Console
         Environment :: GPU :: AMD Instinct :: MI300
         License :: OSI Approved :: Apache Software License
         Programming Language :: C++
         Programming Language :: Python
         Programming Language :: Python :: 3
      Entry-points:
         [console_scripts]
         cucim = cucim.clara.cli:main
      Project-URLs:
         Homepage, https://rocm.docs.amd.com/projects/hipcim/en/latest/
         Documentation, https://rocm.docs.amd.com/projects/hipcim/en/latest/reference/hipcim/index.html#hipcim-reference
         Source, https://github.com/ROCm-LS/hipCIM
         Tracker, https://github.com/ROCm-LS/hipCIM/issues

6. Checkout the sample jupyter notebooks

   .. code-block:: shell

      pip install notebook
      git clone --depth 1 git@github.com:ROCm-LS/hipCIM.git hipcim-notebooks && cd hipcim-notebooks && git filter-branch --prune-empty --subdirectory-filter notebooks HEAD

7. Download sample images

   To download images used in the notebooks, execute the following commands from the repository's root folder. This copies sample input images into notebooks or input folder.

   .. code-block:: shell

      ./run_amd download_testdata

   Or use:

   .. code-block:: shell

      mkdir -p notebooks/input
      tmp_id=$(docker create gigony/svs-testdata:little-big)
      docker cp $tmp_id:/input notebooks
      docker rm -v ${tmp_id}

7. Run a sample program

   .. code-block:: shell

      from cucim import CuImage

      img = CuImage("oxford.tif")
      resolutions = img.resolutions
      level_dimensions = resolutions["level_dimensions"]
      level_count = resolutions["level_count"]

      print(resolutions)
      print(level_count)
      print(level_dimensions)

      region = img.read_region([0,0], level_dimensions[level_count - 1], level_count - 1, device="cuda")
      print(region.device)

   Here is the output:

   .. code-block:: shell

      {'level_count': 1, 'level_dimensions': ((601, 81),), 'level_downsamples': (1.0,), 'level_tile_sizes': ((0, 0),)}
      1
      ((601, 81),)
      [Warning] Loading image('oxford.tif') with a slow-path. The pixel format of the loaded image would be RGBA (4 channels) instead of RGB!
      cuda

.. _source-build:

Building hipCIM from source
****************************

To build hipCIM from source, follow the steps given in this section. This installation method should be used by hipCIM developers. hipCIM users should use the :ref:`install-package`

1. Set up the Docker image

   Use the ROCm Docker image from Dockerhub:

   .. code-block:: shell

      docker pull rocm/dev-ubuntu-22.04
      docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
                                           rocm/dev-ubuntu-22.04

2. Install required system dependencies for hipCIM

   .. code-block:: shell

      sudo apt update
      sudo apt install -y software-properties-common lsb-release gnupg
      sudo apt-key adv --fetch-keys https://apt.kitware.com/keys/kitware-archive-latest.asc
      sudo add-apt-repository -y "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
      sudo apt update
      sudo apt install -y git wget gcc g++ ninja-build git \
                    yasm libopenslide-dev python3.10-venv cmake rocjpeg rocjpeg-dev

3. Download the hipCIM repository

   Checkout the latest version of hipCIM from the git repository:

   .. code-block:: shell

      git clone git@github.com:ROCm-LS/hipCIM.git
      cd hipCIM

4. Create and activate the development environment for building hipCIM

   .. code-block:: shell

      python3 -m venv hipcim_dev
      source hipcim_dev/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt

5. Build and install hipCIM

   To build the hipCIM library on a ROCm-based AMD system using the development environment, follow these steps:

   1. Build the base C++ libraries

   .. code-block:: shell

      ./run_amd build_local cpp release

   2. Build the Python bindings

   .. code-block:: shell

      ./run_amd build_local hipcim release

   3. Install the Python bindings

   .. code-block:: shell

      python -m pip install python/cucim --extra-index-url https://pypi.amd.com/simple

6. Verify the installation

   1. Execute the tests in the base C++ libraries

   .. code-block:: shell

      ./run_amd test cpp release

   2. Execute the Python tests

   .. code-block:: shell

      ./run_amd test_python

Support and limitations
************************

The hipCIM support is limited to C++ and Python interfaces.

There is no support for:

- GPU direct storage (KvikIO, cuFile)

- rocTX tracing

hipCIM only supports features from amd-cupy 13.0 and later.
