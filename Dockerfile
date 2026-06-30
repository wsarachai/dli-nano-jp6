# DLI Nano AI — rebuilt for JetPack 6.x (L4T R36/R39, Ubuntu 24.04)
#
# Why ubuntu:24.04?  The host runs Ubuntu 24.04 with GLib 2.80 and
# GStreamer 1.24.  The NVIDIA Container Runtime injects NVIDIA GStreamer
# plugins (nvarguscamerasrc, nvvidconv, …) compiled against those exact
# versions.  Using the same OS version in the container means the plugins
# load without GLib/GStreamer version mismatches.
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# ── System packages ──────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev python3-venv \
    build-essential git curl wget ca-certificates \
    # OpenCV built with GStreamer support
    python3-opencv \
    libopencv-dev \
    # GStreamer 1.24 (must match host so NVIDIA plugins load)
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    # Misc utilities
    v4l-utils \
    kmod \
    && rm -rf /var/lib/apt/lists/*

# ── Python virtual environment ───────────────────────────────────────────────
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV --system-site-packages
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ── Core Python packages ─────────────────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ── PyTorch for Jetson JetPack 6 (CUDA 12.6) ────────────────────────────────
# Wheels from the Jetson AI Lab project — pre-built for aarch64 + CUDA.
# Swap the index URL if CUDA version differs (cu124, cu128, etc.)
RUN pip install --no-cache-dir \
    --extra-index-url https://pypi.jetson-ai-lab.dev/jp6/cu126 \
    torch torchvision torchaudio

# ── jetcam — camera abstraction library ─────────────────────────────────────
COPY jetcam/ /opt/jetcam/
RUN pip install --no-cache-dir -e /opt/jetcam/

# ── jupyter_clickable_image_widget ───────────────────────────────────────────
# Rewritten with anywidget — no npm/webpack needed, works with JupyterLab 4
COPY jupyter_clickable_image_widget/ /opt/jupyter_clickable_image_widget/
RUN pip install --no-cache-dir -e /opt/jupyter_clickable_image_widget/

# ── Course notebooks ─────────────────────────────────────────────────────────
WORKDIR /workspace
COPY notebooks/ /workspace/

EXPOSE 8888

# Tell the NVIDIA Container Runtime to inject all L4T host libraries
# (GPU drivers, GStreamer plugins, Argus camera stack, etc.)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
