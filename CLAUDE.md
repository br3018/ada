# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Ada is a dev environment for SysML v2 system design and verification. The pipeline is:

```text
models/*.sysml ──make publish──▶ SysML v2 Pilot API server (localhost:9000) ──PySAM──▶ Python verification
```

README.md is the user-facing reference and is kept detailed; update it when behaviour or commands change.

## Commands

Everything runs inside the dev container. `make help` lists targets.

```sh
make setup                                   # uv sync (venv is at /home/vscode/.venvs/ada, outside the workspace)
make lint                                    # ruff check --fix + ruff format
make api-up / make api-down / make api-logs  # API server + Postgres via docker compose (sysml-api/compose.yaml)
make publish MODEL=models/example.sysml [PROJECT=Foo]
uv run python -m ada.publish --help          # --element, --server, --verbose
```

Run Python with `uv run`. There are no tests yet; planned verification checks are pytest tests run via `uv run pytest` behind a future `make verify` target (see README "Verification (planned)").

The first `make api-up` compiles the server from source (several minutes), and the server takes a while longer before answering. A publish takes about a minute because the kernel loads the SysML standard library on startup.

## Architecture

- **Publishing (`src/ada/publish.py`)**: the API server accepts only JSON model elements, not `.sysml` text. `ada.publish` builds an in-memory notebook (`%repo <server>`, the file's text, then one `%publish` per element) and executes it with `nbclient` on the `sysml` Jupyter kernel (the Java pilot kernel installed in the dev image, kernelspec in `.devcontainer/sysml-kernel.json`). Kernel failures are detected by output lines starting with `ERROR`. Top-level packages are found by a regex on unindented `package` declarations.
- **One project per top-level package**: each `%publish` replaces the whole content of its project with a new commit, so `--project` is rejected when a file has more than one top-level package. Server reachability is checked before starting the kernel, since the kernel reports it only as a Java stack trace.
- **Reading (`src/ada/pilot_connector.py`)**: `PilotSysML2APIConnector` subclasses PySAM's `TemplateSysML2APIConnector` to talk to the unauthenticated pilot server at its root (PySAM only ships an Ansys SAM connector). Listing projects works; `get_sysml_project` does **not** yet, because PySAM requests `/projects/{id}/commits/head/...` and the pilot server needs a real commit ID (and likely result paging). Fixing this is the prerequisite for verification.
- **API server (`sysml-api/`)**: built from the SysML-v2-API-Services tag, with `persistence.xml` patched via `sed` to point at the compose `db` service and use `hbm2ddl.auto=update` (data persists in the `pgdata` volume). Both the Docker build and the dev container use the repo root as build context, hence the root `.dockerignore`.

## Version pinning

`sysml-versions.env` is the single source for the pilot release; the API server (`SYSML_RELEASE`) and the Jupyter kernel (`SYSML_KERNEL_VERSION`, `SYSML_KERNEL_SHA256`) must come from the same release. README "Updating the pilot release" explains how to find the matching kernel version and checksum. After changing it, rebuild the dev container and run `make api-up`.
