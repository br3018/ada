FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install a pinned uv release from the Astral image.
# This image does not contain Python. uv downloads the version in .python-version
# when `uv sync` runs after the container starts.
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/

# Install curl. The OpenSysML install script needs it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install OpenSysML. It supplies the sysml command-line tool.
# Pin the release here. To update it, change OPENSYSML_VERSION and rebuild the dev container.
ARG OPENSYSML_VERSION=v0.12.1
RUN curl -fsSL https://opensysml.org/install.sh | sh -s -- --version "${OPENSYSML_VERSION}"

# Make the Claude configuration directory now, so that the vscode user owns its volume.
RUN mkdir -p /home/vscode/.claude && chown -R vscode:vscode /home/vscode/.claude
