.. meta::
   :description: The hipCIM library is a robust open-source solution developed to significantly accelerate computer vision and image processing capabilities
   :keywords: ROCm-LS, life sciences, hipCIM installation

.. _installing-hipcim:

===================
Installing hipCIM
===================

To install hipCIM, you have the following options:

- :ref:`Use AMD PyPI <install-package>` (recommended)

- :ref:`Build from source <source-build>`

System requirements
********************

.. raw:: html

   <div class="pst-scrollable-table-container">
      <table id="hipcim-sys-requirements" class="table">
         <thead>
            <tr>
                <th>ROCm version</th>
                <th>Ubuntu version</th>
                <th>Python version</th>
                <th>AMD Instinct™ GPU</th>
            </tr>
         </thead>
         <colgroup>
            <col span="1">
            <col span="1">
         </colgroup>
         <tbody class="hipcim-system">
            <tr>
               <td>7.2.0, 7.0.2</td>
               <td>24.04</td>
               <td>3.12</td>
               <td>MI300X, MI325X, or MI355X</td>
            </tr>
         </tbody>
      </table>
   </div>

Setting up the environment
***************************

To set up the environment for installing hipCIM, follow these steps:

1. Optional: Use a ROCm Docker image to get started.

   - For ROCm 7.2.0, run:

     .. code-block:: shell

      docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
      --shm-size=128GB --network=host --device=/dev/kfd     \
      --device=/dev/dri --group-add video -it               \
      -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
                                       rocm/dev-ubuntu-24.04:7.2-complete

   - For ROCm 7.0.2, run:

     .. code-block:: shell

      docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
      --shm-size=128GB --network=host --device=/dev/kfd     \
      --device=/dev/dri --group-add video -it               \
      -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
                                       rocm/dev-ubuntu-24.04:7.0.2-complete

   For bare metal, skip this step.

2. Install system dependencies.

   .. code-block:: shell

      apt-get update && \
         apt-get install -y software-properties-common lsb-release gnupg && \
         apt-key adv --fetch-keys https://apt.kitware.com/keys/kitware-archive-latest.asc && \
         add-apt-repository -y "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" && \
         apt-get update && \
         apt-get install -y git wget gcc g++ ninja-build git-lfs \
                        yasm libopenslide-dev python3 python3-venv \
                        python3-dev libpython3-dev \
                        cmake

      if ! dpkg -s amdgpu-install >/dev/null 2>&1; then \
         rm -f /etc/apt/sources.list.d/amdgpu.list /etc/apt/sources.list.d/rocm.list && \
         ROCM_VERSION=$(cat /opt/rocm/.info/version) && \
         UBUNTU_CODENAME=$(lsb_release -cs) && \
         echo "Detected ROCm version: ${ROCM_VERSION}, Ubuntu codename: ${UBUNTU_CODENAME}" && \
         MAJOR=$(echo ${ROCM_VERSION} | cut -d. -f1) && \
         MINOR=$(echo ${ROCM_VERSION} | cut -d. -f2) && \
         PATCH=$(echo ${ROCM_VERSION} | cut -d. -f3) && \
         PATCH=${PATCH:-0} && \
         VERNUM=$((MAJOR * 10000 + MINOR * 100 + PATCH)) && \
         if [ "${PATCH}" = "0" ]; then SHORT_VERSION="${MAJOR}.${MINOR}"; else SHORT_VERSION="${MAJOR}.${MINOR}.${PATCH}"; fi && \
         AMDGPU_URL="https://repo.radeon.com/amdgpu-install/${SHORT_VERSION}/ubuntu/${UBUNTU_CODENAME}/amdgpu-install_${SHORT_VERSION}.${VERNUM}-1_all.deb" && \
         echo "Downloading: ${AMDGPU_URL}" && \
         wget "${AMDGPU_URL}" -O amdgpu-install.deb && \
         apt-get update && \
         DEBIAN_FRONTEND=noninteractive apt-get install -y ./amdgpu-install.deb && \
         rm -f amdgpu-install.deb; \
      else \
         echo "amdgpu-install already present, skipping install"; \
      fi && \
      apt-get update && \
      apt-get install -y --no-install-recommends amdgpu-lib && \
      apt-get install -y --no-install-recommends rocjpeg rocjpeg-dev rocthrust-dev \
                     hipcub hipblas hipblas-dev hipfft hipsparse \
                     hiprand rocsolver rocrand-dev rocm-hip-sdk && \
      rm -rf /var/lib/apt/lists/*

3. Create the Python virtual environment.

   .. code-block:: shell

      python3 -m venv hipcim_dev
      source hipcim_dev/bin/activate

4. Set the environment variables.

   .. code-block:: shell

      export ROCM_HOME=/opt/rocm
      export AMDGPU_TARGETS=gfx942

.. _install-package:

Installing hipCIM using AMD PyPI (recommended)
***********************************************

Packaged versions of hipCIM and its dependencies are distributed via `AMD PyPI <https://pypi.amd.com/simple/>`_. This section discusses how to install hipCIM using this package index.

1. Install hipCIM.

   - For ROCm 7.2.0, run:

     .. code-block:: shell

      pip install amd-hipcim --extra-index-url=https://pypi.amd.com/rocm-7.2.0/simple/

   - For ROCm 7.0.2, run:

     .. code-block:: shell

      pip install amd-hipcim --extra-index-url=https://pypi.amd.com/rocm-7.0.2/simple/

2. Verify the installation.

   .. code-block:: shell

      pip show -v amd-hipcim

   Expected output:

   .. code-block:: shell

      Name: amd-hipcim
      Version: 25.10.00
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
         Development Status :: 5 - Production/Stable
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

.. _source-build:

Building hipCIM from source
****************************

To build hipCIM from source, follow the steps given in this section.

1. Install dependencies.

   .. code-block:: shell

      pip install --upgrade pip

2. Download the latest version of hipCIM from the GitHub repository.

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

         # For ROCm 7.2.0
         python3 -m pip install python/cucim --extra-index-url https://pypi.amd.com/rocm-7.2.0/simple/

         # For ROCm 7.0.2
         python3 -m pip install python/cucim --extra-index-url https://pypi.amd.com/rocm-7.0.2/simple/

Verify installation
********************

To verify the installation, follow these steps:

1. Execute the tests in the base C++ libraries.

   .. code-block:: shell

      ./run_amd test cpp release

2. Run the Python tests.

   For ROCm 7.2.0, run the following additional step before running the Python tests:

   .. code-block:: shell

      export CPATH="/usr/lib/gcc/x86_64-linux-gnu/13/include"

   For ROCm 7.0.2 and 7.2.0, run the Python tests:

   .. code-block:: shell

      ./run_amd test_python

Getting started
****************

Here is some sample Python code and its expected output to help you get started.

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
