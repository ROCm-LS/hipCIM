# <div align="left">&nbsp;hipCIM&nbsp;</div>

## hipCIM
hipCIM is a [HIP](https://github.com/ROCm/hip) port of the [cuCIM](https://github.com/rapidsai/cucim) library under the [RAPIDS](https://github.com/rapidsai)™ ecosystem.
This library is an extensible toolkit designed to provide GPU accelerated I/O, computer vision & image processing primitives for N-Dimensional images with a focus on biomedical imaging.

### Install hipCIM via AMD PyPI

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
	sudo apt update
	sudo apt install -y lsb-release software-properties-common libopenslide0 python3.10-venv rocjpeg
    sudo apt install -y rocthrust-dev hipcub hipblas \
               hipblas-dev hipfft hipsparse \
               hiprand rocsolver rocrand-dev
	pip install --upgrade pip
	```

- Create a python virtual environment
	```
	python3 -m venv hipcim_build
	source hipcim_build/bin/activate

    #install hipCIM
	pip install amd-hipcim --extra-index-url=https://pypi.amd.com/simple
	```

 - Checkout jupyter notebooks
   ```
   pip install notebook
   git clone --depth 1 git@github.com:ROCm-LS/hipCIM.git hipcim-notebooks \
      && cd hipcim-notebooks \
      && git filter-branch --prune-empty --subdirectory-filter notebooks HEAD
   ```
 - Run a sample program
   ```python
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
   ```
 - Output
   ```
    {'level_count': 1, 'level_dimensions': ((601, 81),), 'level_downsamples': (1.0,), 'level_tile_sizes': ((0, 0),)}
    1
    ((601, 81),)
    [Warning] Loading image('oxford.tif') with a slow-path. The pixel format of the loaded image would be RGBA (4 channels) instead of RGB!
    cuda
   ```
- Try out other notebooks.
### Build hipCIM from source
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
    sudo apt update
	sudo apt install -y software-properties-common lsb-release gnupg
	sudo apt-key adv --fetch-keys https://apt.kitware.com/keys/kitware-archive-latest.asc
	sudo add-apt-repository -y "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
	sudo apt update
	sudo apt install -y git wget gcc g++ ninja-build git \
			   yasm libopenslide-dev python3.10-venv cmake rocjpeg rocjpeg-dev
    sudo apt install -y rocthrust-dev hipcub hipblas \
               hipblas-dev hipfft hipsparse \
               hiprand rocsolver rocrand-dev

    ```

- Checkout the latest version of hipCIM from git
    ```
    git clone git@github.com:ROCm-LS/hipCIM.git
    cd hipCIM
    ```

- Create a python virtual environment and install python dependencies:
    ```bash
    python3 -m venv hipcim_dev
	source hipcim_dev/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt
    ```

- Build the cpp base libraries

   ```bash
   ./run_amd build_local cpp release
   ```

- Build the python bindings

  ```bash
  ./run_amd build_local hipcim release
  ```

- Install the hipCIM python package
  ```bash
  python -m pip install python/cucim --extra-index-url https://pypi.amd.com/simple
  ```

- Run all cpp unit tests
  ```bash
  ./run_amd test cpp release
  ```


- Run all python unit tests
  ```bash
  ./run_amd test_python
  ```

### Notebooks

Please check out our [Welcome](notebooks/Welcome.ipynb) notebook.

#### Downloading sample images

To download images used in the notebooks, please execute the following commands from the repository root folder to copy sample input images into `notebooks/input` folder:



```bash
./run_amd download_testdata
```
or

```bash
mkdir -p notebooks/input
tmp_id=$(docker create gigony/svs-testdata:little-big)
docker cp $tmp_id:/input notebooks
docker rm -v ${tmp_id}
```

## Contributing Guide

Contributions to hipCIM are more than welcome!
Please review the [CONTRIBUTING.md](CONTRIBUTING.md) file for information on how to contribute code and issues to the project.

## Acknowledgments

Without awesome third-party open source software, this project wouldn't exist.

Please find [LICENSE-3rdparty.md](LICENSE-3rdparty.md) to see which third-party open source software
is used in this project.

## License

Apache-2.0 License (see [LICENSE](LICENSE) file).

Copyright (c) 2025, AMD CORPORATION.
