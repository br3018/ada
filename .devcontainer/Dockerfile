FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Built with the repository root as context (see devcontainer.json and /.dockerignore)

# Install a pinned uv release from Astral's prebuilt image.
# Python itself is not installed here: uv downloads the version in .python-version when
# `uv sync` runs after the container is created.
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/

# Java runs the SysML Jupyter kernel, Graphviz renders %viz, zstd/unzip unpack the kernel package
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-21-jre-headless graphviz zstd unzip \
    && rm -rf /var/lib/apt/lists/*

# SysML v2 Pilot Jupyter kernel, used to parse models and %publish them to the API server.
# The version comes from sysml-versions.env so it matches the API server.
# The kernel is taken from its conda-forge package (a jar plus the standard library) and registered
# system-wide so Jupyter in any venv finds it. sysml-kernel.json replaces the packaged kernelspec,
# which points %publish at a public server.
COPY sysml-versions.env .devcontainer/sysml-kernel.json /tmp/
RUN set -eux; \
    . /tmp/sysml-versions.env; \
    cd /tmp; \
    curl -fsSL -o kernel.conda "https://conda.anaconda.org/conda-forge/noarch/jupyter-sysml-kernel-${SYSML_KERNEL_VERSION}-pyhd8ed1ab_0.conda"; \
    echo "${SYSML_KERNEL_SHA256}  kernel.conda" | sha256sum -c -; \
    unzip -q kernel.conda "pkg-*.tar.zst"; \
    mkdir pkg; \
    zstd -dc pkg-*.tar.zst | tar -x -C pkg; \
    mkdir -p /usr/local/share/jupyter/kernels; \
    mv pkg/share/jupyter/kernels/sysml /usr/local/share/jupyter/kernels/sysml; \
    mv /tmp/sysml-kernel.json /usr/local/share/jupyter/kernels/sysml/kernel.json; \
    rm -rf /tmp/kernel.conda /tmp/pkg-*.tar.zst /tmp/pkg /tmp/sysml-versions.env

# Pre-create the Claude config dir so the named volume mounted there is owned by vscode, not root
RUN mkdir -p /home/vscode/.claude && chown -R vscode:vscode /home/vscode/.claude
