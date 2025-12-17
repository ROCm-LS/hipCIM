FROM rocm/dev-ubuntu-22.04

# Basic setup
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update &&                        \
    apt-get install -y                       \
    software-properties-common lsb-release gnupg
RUN apt-key adv --fetch-keys                 \
    https://apt.kitware.com/keys/kitware-archive-latest.asc
RUN add-apt-repository -y                    \
    "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
RUN apt-get update &&                        \
    apt-get install -y                       \
    build-essential cmake g++ gcc            \
    ninja-build                              \
    hipblas hipblas-dev hipcub hipfft        \
    hiprand hipsparse                        \
    rocjpeg rocjpeg-dev rocrand-dev          \
    rocsolver rocthrust-dev                  \
    libopenslide0 libopenslide-dev           \
    python3.10 python3.10-venv python3-pip   \
    libvips openssh-client                   \
    git git-lfs supervisor wget yasm &&      \
    apt-get clean &&                         \
    rm -rf /var/lib/apt/lists/*

# Setup app directory
WORKDIR /app

# Copy your SSH private key for git clone (DO NOT leave in production images!)
# In practice, it's best to use multi-stage build and remove after cloning!
# Here, assume you build with: docker build --build-arg SSH_KEY="$(cat ~/.ssh/id_ed25519)" ...
ARG SSH_KEY
RUN mkdir -p /root/.ssh && \
    echo "$SSH_KEY" > /root/.ssh/id_ed25519 && \
    chmod 600 /root/.ssh/id_ed25519 && \
    ssh-keyscan github.com > /root/.ssh/known_hosts

# Clone the repository using the private key
RUN GIT_SSH_COMMAND='ssh -i /root/.ssh/id_ed25519 -o IdentitiesOnly=yes' \
    git clone git@github.com:AMD-AIOSS/hipCIM.git /app/hipCIM

# Remove SSH key for security (should be in a multi-stage build for true safety)
RUN rm -f /root/.ssh/id_ed25519

# Set up Python venv
WORKDIR /app/hipCIM
RUN python3.10 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python requirements
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install albumentations streamlit plotly importlib voila pillow pyvips

# Prepare demo
RUN GIT_SSH_COMMAND='ssh -i /root/.ssh/id_ed25519 -o IdentitiesOnly=yes' \
    git lfs pull
RUN GIT_SSH_COMMAND='ssh -i /root/.ssh/id_ed25519 -o IdentitiesOnly=yes' \
    git checkout feature/demo2

# Build & install hipCIM
RUN ./run_amd build_local cpp release
RUN ./run_amd build_local hipcim release
RUN pip install python/cucim --extra-index-url https://pypi.amd.com/simple

# Copy demo artifacts
# (Ensure sample_images/77917-ome_base.tif is made available from local storage)
COPY sample_images/77917-ome_base.tif /app/hipCIM/demo/sample_images/77917-ome_base.tif

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose Streamlit port
EXPOSE 8501

# Entrypoint: supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
