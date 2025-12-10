.. meta::
   :description: The hipCIM library is a robust open-source solution developed to significantly accelerate computer vision and image processing capabilities
   :keywords: ROCm-LS, life sciences, hipCIM installation

.. _installing-hipcim:

===================
Installing hipCIM
===================

This topic discusses how to install hipCIM using the following options:

- :ref:`Build from source (for developers) <source-build>`

- :ref:`Recommended: AMD PyPI (for users) <install-package>`

System requirements
********************

+--------------+----------------+----------------+------------------+
| ROCm version | Ubuntu version | Python version | AMD Instinct GPU |
+==============+================+================+==================+
| 7.0.2        | 24.04          | 3.12           | MI300A           |
+--------------+----------------+----------------+------------------+
| 6.4.3        | 22.04          | 3.10           | MI325X           |
+--------------+----------------+----------------+------------------+

Setting up the environment
***************************

To set up the environment for installing hipCIM, follow these steps:

1. Optional: Use ROCm Docker to get started.

   - For ROCm 7.0.2, run:

     .. code-block:: shell

      docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
      --shm-size=128GB --network=host --device=/dev/kfd     \
      --device=/dev/dri --group-add video -it               \
      -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
                                       rocm/dev-ubuntu-24.04:7.0.2-complete

   - For ROCm 6.4.3, run:

     .. code-block:: shell

      docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
      --shm-size=128GB --network=host --device=/dev/kfd     \
      --device=/dev/dri --group-add video -it               \
      -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
                                       rocm/dev-ubuntu-22.04:6.4.3-complete

   For bare metal, skip this step.

2. Install system dependencies. For both ROCm 6.4.3 and 7.0.2, run:

   .. code-block:: shell

      apt-get update && \
      apt-get install -y software-properties-common lsb-release gnupg && \
      apt-key adv --fetch-keys https://apt.kitware.com/keys/kitware-archive-latest.asc && \
      add-apt-repository -y "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" && \
      mkdir -p /etc/apt/keyrings && \
      curl -fsSL https://repo.radeon.com/rocm/rocm.gpg.key | gpg --dearmor -o /etc/apt/keyrings/rocm.gpg && \
      echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/amdgpu/6.2.1/ubuntu jammy main proprietary" | tee /etc/apt/sources.list.d/amdgpu.list && \
      apt-get update && \
      apt-get install -y git wget gcc g++ ninja-build git-lfs \
                     yasm libopenslide-dev python3 python3-venv \
                     python3-dev libpython3-dev \
                     cmake rocjpeg rocjpeg-dev rocthrust-dev \
                     hipcub hipblas hipblas-dev hipfft hipsparse \
                     hiprand rocsolver rocrand-dev rocm-hip-sdk

3. Create the Python virtual environment.

   .. code-block:: shell

      python3 -m venv hipcim_dev
      source hipcim_dev/bin/activate

4. Set the environment variables:

   .. code-block:: shell

      export ROCM_HOME=/opt/rocm
      export AMDGPU_TARGETS=gfx942

.. _source-build:

Building hipCIM from source
****************************

To build hipCIM from source, follow the steps given in this section. hipCIM developers should use this installation method. hipCIM users should use the :ref:`Installing hipCIM using AMD PyPI <install-package>`

1. Install dependencies.

   .. code-block:: shell

      pip install --upgrade pip

2. Download the latest version of hipCIM from the git repository.

   .. code-block:: shell

      git clone git@github.com:ROCm-LS/hipCIM.git
      cd hipCIM

3. Install the rest of the dependencies.

   .. code-block:: shell

      pip install -r ./requirements.txt

4. Build and install hipCIM.

   To build the hipCIM library on a ROCm-based AMD system using the development environment, follow these steps:

   1. Build the base C++ libraries.

      .. code-block:: shell

         ./run_amd build_local cpp release

   2. Build the Python bindings.

      .. code-block:: shell

         ./run_amd build_local hipcim release

   3. Install the Python bindings.

      .. code-block:: shell

         # For ROCm 7.0.2
         python3 -m pip install python/cucim --extra-index-url https://pypi.amd.com/rocm-7.0.2/simple/

         # For ROCm 6.4.3
         python3 -m pip install python/cucim --extra-index-url https://pypi.amd.com/simple

6. Verify the installation.

   To verify the installation, follow these steps:

   1. Execute the tests in the base C++ libraries.

      .. code-block:: shell

         ./run_amd test cpp release

   2. Execute the Python tests.

      .. code-block:: shell

         ./run_amd test_python

.. _install-package:

Installing hipCIM using AMD PyPI (recommended)
***********************************************

Packaged versions of hipCIM and its dependencies are distributed via `AMD PyPI <https://pypi.amd.com/simple/>`_. This section discusses how to install hipCIM using this package index. hipCIM users should use this installation method. hipCIM developers should use the :ref:`source-build`.

1. Install hipCIM.

   - For ROCm 7.0.2, run:

     .. code-block:: shell

      pip install amd-hipcim --extra-index-url=https://pypi.amd.com/rocm-7.0.2/simple/

   - For ROCm 6.4.3, run:

     .. code-block:: shell

      pip install amd-cupy --extra-index-url=https://pypi.amd.com/simple
      pip install amd-hipcim --extra-index-url=https://pypi.amd.com/rocm-6.4.3/simple

2. Verify the installation.

   .. code-block:: shell

      pip show -v amd-hipcim

   Expected output:

   .. code-block:: shell

      Name: amd-hipcim
      Version: 25.10.0
      Summary: hipCIM - an extensible toolkit designed to provide GPU accelerated I/O, computer vision & image processing primitives for N-Dimensional images with a focus on biomedical imaging.
      Home-page: https://rocm.docs.amd.com/projects/hipCIM/en/latest/
      Author: AMD Corporation
      Author-email:
      License: Apache 2.0
      Location: /scratch/integration/hipCIM/hipcim_dev/lib/python3.10/site-packages
      Requires: amd-cupy, click, lazy-loader, numpy, scikit-image, scipy
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
         Homepage, https://rocm.docs.amd.com/projects/hipCIM/en/latest/
         Documentation, https://rocm.docs.amd.com/projects/hipCIM/en/latest/
         Source, https://github.com/ROCm-LS/hipCIM
         Tracker, https://github.com/ROCm-LS/hipCIM/issues

Getting started
****************

Here is a sample Python code and its expected output to help you get started.

- Sample code:

  .. code-block:: shell

   from cucim import CuImage

   img = CuImage("sample_image/oxford.tif")
   resolutions = img.resolutions
   level_dimensions = resolutions["level_dimensions"]
   level_count = resolutions["level_count"]

   print(resolutions)
   print(level_count)
   print(level_dimensions)

   region = img.read_region([0,0], level_dimensions[level_count - 1], level_count - 1, device="cuda")
   print(region.device)

- Expected output:

  .. code-block:: shell

   {'level_count': 1, 'level_dimensions': ((601, 81),), 'level_downsamples': (1.0,), 'level_tile_sizes': ((0, 0),)}
   1
   ((601, 81),)
   [Warning] Loading image('sample_image/oxford.tif') with a slow-path. The pixel format of the loaded image would be RGBA (4 channels) instead of RGB!
   cuda
