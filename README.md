# <div align="left">&nbsp;cuCIM/hipCIM&nbsp;</div>

## hipCIM 
hipCIM is a [HIP](https://github.com/ROCm/hip) port of the [cuCIM](https://github.com/rapidsai/cucim) library under the [RAPIDS](https://github.com/rapidsai) ecosystem.
This library is an extensible toolkit designed to provide GPU accelerated I/O, computer vision & image processing primitives for N-Dimensional images with a focus on biomedical imaging.

### Resources
- [hipCIM API reference](https://rocm.docs.amd.com/projects/hipCIM/en/latest/reference/hipcim/index.html#hipcim-reference)

### Install hipCIM on ROCm 7.2/7.0 via AMD PyPI

- [Optional step] Follow these if you want to install hipCIM inside a docker
	```
	#For ROCm 7.2
	docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
     rocm/dev-ubuntu-24.04:7.2-complete
	#For ROCm 7.0
	docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
     rocm/dev-ubuntu-24.04:7.0.2-complete
	```
- Install required system dependencies
  	```
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
       rm amdgpu-install.deb; \
    else \
       echo "amdgpu-install already present, skipping install"; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends amdgpu-lib && \
    apt-get install -y --no-install-recommends  rocjpeg rocjpeg-dev rocthrust-dev \
                   hipcub hipblas hipblas-dev hipfft hipsparse \
                   hiprand rocsolver rocrand-dev rocm-hip-sdk && \
    rm -rf /var/lib/apt/lists/*
	```

- Create a python3 virtual environment
	```
	python3 -m venv hipcim_dev
	source hipcim_dev/bin/activate
  ```

- Setup environment variables
  ```
  export ROCM_HOME=/opt/rocm
  #For MI300
  export AMDGPU_TARGETS=gfx942
  #For MI350
  export AMDGPU_TARGETS=gfx950
	```
- Install hipcim
  ```
  #For ROCm 7.2
  pip install amd-hipcim --extra-index-url=https://pypi.amd.com/rocm-7.2.0/simple/
  #For ROCm 7.0
  pip install amd-hipcim --extra-index-url=https://pypi.amd.com/rocm-7.0.2/simple/
  ```

- Verify installation
  ```
  pip show -v amd-hipcim
  ```
- Expected output
  ```
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
  ```


 - Run a sample program
   ```python3
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
   ```

 - Output
   ```
    {'level_count': 1, 'level_dimensions': ((601, 81),), 'level_downsamples': (1.0,), 'level_tile_sizes': ((0, 0),)}
    1
    ((601, 81),)
    [Warning] Loading image('oxford.tif') with a slow-path. The pixel format of the loaded image would be RGBA (4 channels) instead of RGB!
    cuda
   ```


### Build hipCIM on ROCm 7.2/7.0 from source
Please use the below steps to build the hipCIM library on a ROCM based MI300 system from source.

- Use the complete rocm docker image from dockerhub
	```
    #For ROCm 7.2
    docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
     rocm/dev-ubuntu-24.04:7.2-complete
    #For ROCm 7.0
    docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
     rocm/dev-ubuntu-24.04:7.0.2-complete
    ```

- Install required system dependencies
  	```
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
       rm amdgpu-install.deb; \
    else \
       echo "amdgpu-install already present, skipping install"; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends amdgpu-lib && \
    apt-get install -y --no-install-recommends  rocjpeg rocjpeg-dev rocthrust-dev \
                   hipcub hipblas hipblas-dev hipfft hipsparse \
                   hiprand rocsolver rocrand-dev rocm-hip-sdk && \
    rm -rf /var/lib/apt/lists/*
	```

- Create a python3 virtual environment
	```
	python3 -m venv hipcim_dev
	source hipcim_dev/bin/activate
  ```

- Setup environment variables
  ```
  export ROCM_HOME=/opt/rocm
  #For MI300
  export AMDGPU_TARGETS=gfx942
  #For MI350
  export AMDGPU_TARGETS=gfx950
	```
- Install dependencies
  ```
  pip install --upgrade pip setuptools wheel
  ```

- Download the latest version of hipCIM from the git repository:
  ```
  git clone git@github.com:ROCm-LS/hipCIM.git
  cd hipCIM
  ```
- Install dependencies
  ```
  pip install -r ./requirements.txt
  ```

- Build the cpp base libraries

  ```bash
  ./run_amd build_local cpp release
  ```

- Build the python3 bindings

  ```bash
  ./run_amd build_local hipcim release
  ```

- Install the hipCIM python3 package
  ```bash
  #For ROCm 7.2
  python3 -m pip install python/cucim --extra-index-url https://pypi.amd.com/rocm-7.2.0/simple/
  #For ROCm 7.0
  python3 -m pip install python/cucim --extra-index-url https://pypi.amd.com/rocm-7.0.2/simple/
  ```

- Run all cpp unit tests
  ```bash
  ./run_amd test cpp release
  ```

- Run all python3 unit tests
  ```bash
  #For ROCm 7.2
  export CPATH="/usr/lib/gcc/x86_64-linux-gnu/13/include"
  ./run_amd test_python
  #For ROCm 7.0
  ./run_amd test_python
  ```


### Install hipCIM on ROCm 6.4 via AMD PyPI

- [Optional step] Follow these if you want to install hipCIM inside a docker
	```
	docker pull rocm/dev-ubuntu-22.04
	docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
     rocm/dev-ubuntu-22.04:6.4.1-complete
	```
- Install required system dependencies
  	```
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
	pip install --upgrade pip
	```
	
- Create a python3 virtual environment
	```
	python3 -m venv hipcim_build
	source hipcim_build/bin/activate

  # Setup environment variables
  
  export ROCM_HOME=/opt/rocm
  export AMDGPU_TARGETS=gfx942 
	
    
    	# Install hipCIM
	pip install amd-hipcim --index-url=https://pypi.amd.com/simple
	```

 - Run a sample program
   ```python3
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
   ```

 - Output
   ```
    {'level_count': 1, 'level_dimensions': ((601, 81),), 'level_downsamples': (1.0,), 'level_tile_sizes': ((0, 0),)}
    1
    ((601, 81),)
    [Warning] Loading image('oxford.tif') with a slow-path. The pixel format of the loaded image would be RGBA (4 channels) instead of RGB!
    cuda
   ```


### Build hipCIM on ROCm 6.4 from source
Please use the below steps to build the hipCIM library on a ROCM based MI300 system from source. 

- Use the complete rocm docker image from dockerhub
	```
    docker pull rocm/dev-ubuntu-22.04
    docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
         --shm-size=128GB --network=host --device=/dev/kfd     \
         --device=/dev/dri --group-add video -it               \
         -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
     rocm/dev-ubuntu-22.04:6.4.1-complete
    ```

- Once you have the docker up and running, install the following packages
  required for the build system:
    ```
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
    ```

- Checkout the latest version of hipCIM from git
    ```
    git clone git@github.com:ROCm-LS/hipCIM.git
    cd hipCIM
    ```

- Create a python3 virtual environment and install python dependencies:
    ```bash
    python3 -m venv hipcim_dev
	source hipcim_dev/bin/activate
    
    # Setup environment variables
  export ROCM_HOME=/opt/rocm
  export AMDGPU_TARGETS=gfx942 

	pip install --upgrade pip
	pip install -r requirements.txt
    ```

- Build the cpp base libraries

   ```bash
   ./run_amd build_local cpp release
   ```

- Build the python3 bindings

  ```bash
  ./run_amd build_local hipcim release
  ```

- Install the hipCIM python3 package
  ```bash
  python -m pip install python/cucim --index-url https://pypi.amd.com/simple
  ```

- Run all cpp unit tests
  ```bash
  ./run_amd test cpp release
  ```

- Run all python3 unit tests
  ```bash
  ./run_amd test_python
  ```

### Code Coverage

hipCIM supports comprehensive code coverage for both C++ and Python components. For detailed information about generating and understanding code coverage reports, please refer to [scripts/README.md](scripts/README.md#code-coverage).

Quick commands:
- **C++ Coverage**: `./run_amd cpp_coverage`
- **Python Coverage**: Automatically generated with `./run_amd test_python`

## Contributing Guide

Contributions to hipCIM are more than welcome!
Please review the [CONTRIBUTING.md](https://github.com/ROCm-LS/hipCIM/CONTRIBUTING.md) file for information on how to contribute code and issues to the project.

## Acknowledgments

Without awesome third-party open source software, this project wouldn't exist.

Please find [LICENSE-3rdparty.md](LICENSE-3rdparty.md) to see which third-party open source software
is used in this project.

## License

Apache-2.0 License (see [LICENSE](LICENSE) file).

Copyright (c) 2025, AMD CORPORATION.
