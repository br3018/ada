# Ada

A development environment for carrying out system design and verification using SysML v2.

Models are written in SysML v2 textual notation (`.sysml` files) in VS Code, published to a local SysML v2 API server, and read from Python with [Ansys PySAM SysML2](https://sysml2.docs.pyansys.com/) for verification:

```text
models/*.sysml ──make publish──▶ SysML v2 API server ──PySAM──▶ verification scripts
                                 (localhost:9000)
```

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

## Setup

Open the repository in VS Code and run **Dev Containers: Reopen in Container**. The dev container provides:

- the [Syside](https://syside.sensmetry.com/) editor extension for writing SysML v2 models
- the SysML v2 Pilot Jupyter kernel (with Java and Graphviz) for parsing and publishing models
- Docker, for running the SysML v2 API server
- the [uv](https://docs.astral.sh/uv/) package manager

When the container is created, `uv sync` installs Python (the version in [.python-version](.python-version)) and the project's dependencies. The virtual environment lives at `/home/vscode/.venvs/ada`, outside the workspace, and VS Code is configured to use it. Run commands in it with `uv run`. After changing dependencies in [pyproject.toml](pyproject.toml), run `make setup` to update it.

Common tasks are wrapped in the [Makefile](Makefile). Run `make help` to list them.

## Repository layout

| Path | Contents |
| --- | --- |
| [models/](models/) | The SysML v2 models (`.sysml` files). [example.sysml](models/example.sysml) is a small sample. |
| [src/ada/](src/ada/) | The `ada` Python package: [publish.py](src/ada/publish.py) publishes models and [pilot_connector.py](src/ada/pilot_connector.py) connects PySAM to the API server. |
| [sysml-api/](sysml-api/) | Docker build and compose file for the API server and its PostgreSQL database. |
| [.devcontainer/](.devcontainer/) | Dev container image and configuration, including the SysML kernel's kernelspec. |
| [sysml-versions.env](sysml-versions.env) | The SysML v2 pilot release used by both the API server and the kernel. |
| [Makefile](Makefile) | Shortcuts for common tasks. |

## Running the API server

The [SysML v2 Pilot API server](https://github.com/Systems-Modeling/SysML-v2-API-Services) runs in Docker inside the dev container, backed by a PostgreSQL database:

```sh
make api-up      # build and start
make api-logs    # follow the server logs
make api-down    # stop
```

The first `make api-up` compiles the server from source, which takes several minutes. After it starts, the server takes some time before it answers requests. Once it does:

- API: `http://localhost:9000` (e.g. `curl localhost:9000/projects`)
- Swagger UI: `http://localhost:9000/docs/`

Port 9000 is forwarded to your machine.

> [!WARNING]
> The server has no authentication and uses fixed development credentials (see [sysml-api/compose.yaml](sysml-api/compose.yaml)). It is meant for local use only; don't expose port 9000 beyond your machine.

## Publishing a model

The API server only accepts model elements as JSON, not `.sysml` text. Models are parsed and published with the [SysML v2 Pilot Jupyter kernel](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation):

```sh
make publish MODEL=models/example.sysml              # one project per top-level package
make publish MODEL=models/example.sysml PROJECT=Foo  # choose the project name
```

This runs `python -m ada.publish` (see `uv run python -m ada.publish --help` for `--element`, `--server` and `--verbose`). Starting the kernel loads the standard library, so a publish takes about a minute.

- If the file has parse errors, they are printed and nothing is published. Error locations give the line in the file; the `2.sysml` prefix only names the notebook cell the file was loaded into.
- Each publish replaces the whole content of its project with a new commit, so a project holds one top-level package. Publishing the same package again adds a new commit to the same project.

## Reading models from Python

PySAM only ships a connector for Ansys SAM, so use `ada.pilot_connector.PilotSysML2APIConnector` with the pilot server:

```python
from ansys.sam.sysml2 import SysML2ProjectManager
from ada.pilot_connector import PilotSysML2APIConnector

project_manager = SysML2ProjectManager(PilotSysML2APIConnector("http://localhost:9000"))
for p in project_manager.get_projects():
    print(p["name"], p["@id"])
```

> [!NOTE]
> Listing projects works, but loading a project's content (`get_sysml_project`) does not work yet. PySAM requests `/projects/{id}/commits/head/...`. `head` is a shortcut that Ansys SAM supports, but the pilot server needs a real commit ID. The connector needs to resolve the branch's head commit, and probably to follow the server's result paging for larger models.

## Verification (planned)

Verification is not implemented yet. The intended approach:

1. **Requirements live in the model.** Each model in `models/` carries its requirements and the attribute values they constrain (for example a mass limit and the masses of the parts).
2. **Checks are Python tests.** Each check loads the published project through PySAM (`SysML2ProjectManager.get_sysml_project`), finds the elements it needs (for example with `Project.find_elements_by_name`), reads their attribute values and asserts the requirement holds. Writing checks as pytest tests gives a pass or fail per requirement.
3. **One command runs them.** A `make verify` target publishes the models and then runs the checks with `uv run pytest`.

Step 2 depends on fixing the connector so that it can load project content (see the note under [Reading models from Python](#reading-models-from-python)).

## Interactive notebooks

The SysML kernel can also be used interactively. Create a `.ipynb` notebook in VS Code, select the **SysML** kernel, and enter SysML in the cells. Magic commands such as `%show`, `%viz` and `%publish` work there too (run `%help` for the full list). Notebooks publish to `http://localhost:9000`.

## Updating the pilot release

The API server and the kernel must come from the same pilot release. Both read it from [sysml-versions.env](sysml-versions.env):

- `SYSML_RELEASE`: a tag of [SysML-v2-API-Services](https://github.com/Systems-Modeling/SysML-v2-API-Services/tags), such as `2026-04`.
- `SYSML_KERNEL_VERSION`: the kernel version for the same release. It is the `SYSML_VERSION` in `install/jupyter/install.sh` of [SysML-v2-Release](https://github.com/Systems-Modeling/SysML-v2-Release) at the same tag (`2026-04` is `0.59.0`).
- `SYSML_KERNEL_SHA256`: the checksum of the kernel's conda-forge package, which you can compute with:

  ```sh
  curl -fsSL https://conda.anaconda.org/conda-forge/noarch/jupyter-sysml-kernel-<version>-pyhd8ed1ab_0.conda | sha256sum
  ```

Then rebuild the dev container and run `make api-up`.

## Troubleshooting

- **`make publish` says the API server isn't responding.** Start it with `make api-up`. After it starts, it takes some time before it answers requests; `make api-logs` shows its progress.
- **`make publish` prints `ERROR:` lines.** These come from the SysML parser or from the publish itself. Nothing is published until the model parses cleanly.

## Resources

- [PySAM SysML2 docs](https://sysml2.docs.pyansys.com/)
- [SysML-v2-Pilot-Implementation](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation): the reference implementation, including the Jupyter kernel
- [SysML-v2-API-Services](https://github.com/Systems-Modeling/SysML-v2-API-Services): the pilot API server
- [SysML-v2-Release](https://github.com/Systems-Modeling/SysML-v2-Release): pilot releases, specifications and training material
- [Syside](https://syside.sensmetry.com/): the SysML v2 editor extension used in the dev container
