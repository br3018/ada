FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install a pinned UV release from Astral SH's prebuilt image
# Python itself is installed by uv from .python-version
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/
