# hipCIM Demo

**Note**
_hipCIM is in an early access state. Running production workloads is not recommended._

The hipCIM library is a robust open-source solution developed to significantly accelerate 
computer vision and image processing capabilities, particularly for multidimensional images. 
This library provides powerful support for GPU-accelerated input/output operations, coupled 
with an array of computer vision and image processing primitives tailored for N-dimensional 
image data.

One of the key strengths of hipCIM is its comprehensive suite of tools designed to facilitate 
the development of sophisticated image processing applications. In essence, hipCIM provides 
developers with a versatile platform that bridges the gap between different hardware ecosystems, 
thereby promoting flexibility and efficiency in the deployment of advanced image processing 
workloads.

The demo consists of a static Jupyter notebook and an interactive Streamlit-based dashboard, 
demonstrating some of the key functionalities enabled by hipCIM, accelerated on AMD Instinct 
GPUs.

## Instructions for the demo
Please follow the instructions available [here]([url](https://amd.atlassian.net/wiki/spaces/DCGPUAIST/pages/956684133/Installing+hipCIM)) to install hipCIM and its dependencies.

### Jupyter Notebook
The following packages need to be installed for the demo:

```
pip install matplotlib pillow numpy jupyter
```

The rest of the notebook is self-explanatory.

### Streamlit based Dashboard

This demonstrates how to build and run the hipCIM dashboard in a robust, 
GPU-accelerated Docker environment using Streamlit and supervisord. The setup is 
designed for persistent, reliable demo access on AMD ROCm systems.

---

##### `Dockerfile`
- **Purpose:** Automates the creation of a reproducible, containerized environment for the hipCIM demo.
- **Features:**
  - Uses an appropriate Ubuntu/ROCm development image.
  - Installs all system and Python dependencies.
  - Secures source code checkout using an SSH private key ARG.
  - Sets up a Python virtual environment for isolation.
  - Uses `supervisord` to launch the Streamlit dashboard and ensure automatic restarts for reliability.

##### `supervisord.conf`
- **Purpose:** Process manager configuration to keep Streamlit running inside the container.
- **Features:**
  - Launches Streamlit in the correct working directory for the app.
  - Auto-restarts the app on any failure.
  - Directs all logs to STDOUT/STDERR for easy access with `docker logs`.

---

#### Usage

##### 1. **Build the Docker Image**

```bash
docker build \
  --build-arg SSH_KEY="$(cat /home/$LOGNAME/.ssh/id_ed25519)" \
  -t hipcim-demo:latest .
```

##### 2. Run the Docker Container
```bash
docker run --shm-size=128G --device=/dev/kfd --device=/dev/dri --group-add video \
    --cap-add=SYS_PTRACE --privileged --network=host \
    --name hipcim_demo --restart unless-stopped -d hipcim-demo:latest
```

Adjust device flags as needed for your system.
This command enables persistent and robust serving of the demo over the local network.

##### 3. Rebuild and Restart After Changes

For any incremental changes, rebuild and restart the container

```bash
docker stop hipcim_demo && docker rm hipcim_demo

docker build \
  --build-arg SSH_KEY="$(cat /home/$LOGNAME/.ssh/id_ed25519)" \
  -t hipcim-demo:latest .

docker run --shm-size=128G --device=/dev/kfd --device=/dev/dri --group-add video \
    --cap-add=SYS_PTRACE --privileged --network=host \
    --name hipcim_demo --restart unless-stopped -d hipcim-demo:latest
```

##### 4. View Application Logs

```bash
docker logs -f hipcim_demo
```

This will stream the supervisord/Streamlit logs for monitoring and debugging.

##### 5. Stopping and Removing the Demo

```bash
docker stop hipcim_demo
docker rm hipcim_demo
```

#### Access
By default, the Streamlit app will be available via http://localhost:8501 on your server (or [hostname]:8501 across your network).

#### Notes
Security: Do not leave your SSH private key in the build context or image. The recommended Dockerfile clears it after use.
Persistence: For persistent demo use, the container is configured to auto-restart on failure or system reboot.
GPU Support: Both /dev/kfd and /dev/dri are passed for full AMD GPU access and graphics.

#### Troubleshooting
Check logs (`docker logs -f hipcim_demo`) for any errors or crash reports.
Ensure your system has ROCm-compatible AMD GPUs, proper drivers, and Docker configured to support device and group flags.
If the app does not start, double-check the device permissions and network/port availability.

## Potential Next Steps
- Integrate streamlit-based dashboard with an NGINX reverse proxy for enhanced security or SSL.
- Set up container monitoring (Prometheus, Grafana, etc.) for demo reliability.
- Enable interactive file browsing for the demo
