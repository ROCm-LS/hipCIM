# <div align="left">&nbsp;cuCIM/hipCIM&nbsp;</div>

## hipCIM 
hipCIM is a [HIP](https://github.com/ROCm/hip) port of the [cuCIM](https://github.com/rapidsai/cucim) library under the [RAPIDS](https://github.com/rapidsai) ecosystem.
This library is an extensible toolkit designed to provide GPU accelerated I/O, computer vision & image processing primitives for N-Dimensional images with a focus on biomedical imaging.

### Resources
- [hipCIM API reference](https://rocm.docs.amd.com/projects/hipCIM/en/latest/reference/hipcim/index.html#hipcim-reference)

### Install hipCIM via AMD PyPI

- [Optional step] Follow these if you want to install hipCIM inside a docker
	```bash
  docker pull rocm/dev-ubuntu-22.04
  docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
          --shm-size=128GB --network=host --device=/dev/kfd     \
          --device=/dev/dri --group-add video -it               \
          -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
          rocm/dev-ubuntu-22.04:6.4.1-complete
	```
- Install required system dependencies
  ```bash
  sudo apt update
  sudo apt install -y lsb-release software-properties-common libopenslide0 python3.10-venv rocjpeg
  sudo apt install -y rocthrust-dev hipcub hipblas \
                hipblas-dev hipfft hipsparse \
                hiprand rocsolver rocrand-dev git git-lfs
  pip install --upgrade pip
	```
	
- Create a python3 virtual environment
	```
  python3 -m venv hipcim_build
  source hipcim_build/bin/activate
  ```

- Setup environment variables
  ```bash
  export ROCM_HOME=/opt/rocm
  export AMDGPU_TARGETS=gfx942 
  ```

- Install hipCIM
  ```bash
  # Install amd-cupy
  pip install amd-cupy --index-url=https://pypi.amd.com/simple
  # Install amd-hipcim
  pip install amd-hipcim --index-url=https://pypi.amd.com/rocm-6.4.3/simple
  ```

- Run a sample program
  ```python
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
  ```bash
  {'level_count': 1, 'level_dimensions': ((601, 81),), 'level_downsamples': (1.0,), 'level_tile_sizes': ((0, 0),)}
  1
  ((601, 81),)
  [Warning] Loading image('sample_image/oxford.tif') with a slow-path. The pixel format of the loaded image would be RGBA (4 channels) instead of RGB!
  cuda
  ```


### Build hipCIM from source
Please use the below steps to build the hipCIM library on a ROCM based MI300 system from source. 

- Use the complete rocm docker image from dockerhub
	```bash
  docker pull rocm/dev-ubuntu-22.04
  docker run --cap-add=SYS_PTRACE --ipc=host --privileged=true   \
        --shm-size=128GB --network=host --device=/dev/kfd     \
        --device=/dev/dri --group-add video -it               \
        -v $HOME:$HOME  --name ${LOGNAME}_rocm                \
        rocm/dev-ubuntu-22.04:6.4.1-complete
  ```

- Once you have the docker up and running, install the following packages
  required for the build system:
  ```bash
  sudo apt update
  sudo apt install -y software-properties-common lsb-release gnupg
  sudo apt-key adv --fetch-keys https://apt.kitware.com/keys/kitware-archive-latest.asc
  sudo add-apt-repository -y "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
  sudo apt update
  sudo apt install -y git wget gcc g++ ninja-build git git-lfs \
                yasm libopenslide-dev python3.10-venv cmake \
                rocjpeg rocjpeg-dev rocthrust-dev hipcub hipblas \
                hipblas-dev hipfft hipsparse hiprand rocsolver \
                rocrand-dev
  ```

- Checkout the latest version of hipCIM from git
  ```bash
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

  # Install dependencies
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
  python3 -m pip install python/cucim --index-url https://pypi.amd.com/simple
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