# Ada

Ada is a development environment for system design and verification with SysML v2.

You write the models in SysML v2 textual notation (`.sysml` files). The [OpenSysML](https://opensysml.org) `sysml` command-line tool loads and validates the models.

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

## Setup

The dev container contains all the tools for Ada.

To open the repository in the dev container:

1. Open the repository in VS Code.
2. Run the command **Dev Containers: Reopen in Container**.
3. Wait until VS Code builds and starts the container.

The dev container contains these tools:

- the OpenSysML `sysml` command-line tool, which the image installs from `https://opensysml.org/install.sh`
- the [Syside](https://syside.sensmetry.com/) editor extension for SysML v2 models
- the [uv](https://docs.astral.sh/uv/) package manager
- Claude Code, the GitHub CLI and Node.js

When VS Code creates the container, it runs `uv sync`. This command installs Python and the Python dependencies in [pyproject.toml](pyproject.toml). The Python version is in [.python-version](.python-version).

Ada is not a Python package. uv only manages the Python version and the virtual environment.

The virtual environment is at `/home/vscode/.venvs/ada`, outside the workspace. VS Code uses this environment. Use `uv run` to run a command in it.

## Commands

Run all commands in the dev container. The [Makefile](Makefile) contains shortcuts for the usual commands. `make help` Shows the list of targets.

## Repository layout

| Path | Contents |
| --- | --- |
| [model/](model/) | The SysML v2 model. [Model.sysml](model/Model.sysml) imports the parts in [PartLibrary.sysml](model/PartLibrary.sysml). |
| [.devcontainer/](.devcontainer/) | The dev container image and configuration. |
| [Makefile](Makefile) | Shortcuts for the usual commands. |
| [pyproject.toml](pyproject.toml), [uv.lock](uv.lock), [.python-version](.python-version) | The Python version and the Python dependencies. |

## OpenSysML version

The [Dockerfile](.devcontainer/Dockerfile) pins the OpenSysML release in the `OPENSYSML_VERSION` build argument. The current release is `v0.12.1`.

To change the OpenSysML release:

1. Find the release tag on the [OpenSysML releases](https://github.com/Open-MBEE/OpenSysML/releases) page.
2. Set `OPENSYSML_VERSION` in [.devcontainer/Dockerfile](.devcontainer/Dockerfile) to that tag.
3. Run the command **Dev Containers: Rebuild Container**.
4. Run `sysml -version` and make sure that it shows the new release.
5. Run `make sysml-validate`.

## SysMLv2 Validation

`make sysml-validate` checks the model complies to the SysMLv2 specification. It runs `sysml -strict -validate $(MODEL)`. The default value of `MODEL` is `model`.

- The `sysml` tool loads all the files that you give it as one model. A declaration in one file can refer to a declaration in a different file, in any order.
- `-validate` reports the diagnostics of the model. The tool exits with a nonzero code when the model has an error.
- `-strict` applies the SysML v2 standard strictly. Notation that the standard does not allow is an error, not a warning.

The nonzero exit code lets a build or a CI job stop when the model has an error.

To validate the model:

1. Open a terminal in the dev container.
2. Run `make sysml-validate`.
3. Read the output. The tool gives one line for each package and one line for the full model.
4. If the tool reports an error, correct the `.sysml` file at the location in the error.
5. Do steps 2 to 4 again until the tool reports no errors.

## Problems and solutions

- **The shell reports `sysml: command not found`.** The dev container image does not contain the tool. Run the command **Dev Containers: Rebuild Container**.
- **`make sysml-validate` reports an error.** The model has an error at the given location. Run `sysml -explain <code>` to get the cause and the solution.
- **`-validate=<object>` reports `no instance of "<object>"`.** The object does not exist yet. Add `-instantiate <object>` to the command.
- **`make` reports `Clock skew detected`.** The workspace can be on a Windows mount, with file times that differ from the container clock. All the targets are phony, so this warning has no effect on the result. A phony target is a command name, not a file that `make` builds.

## Resources

- [OpenSysML MDK](https://runtime.opensysml.org/): the `sysml` command-line tool
- [SysML-v2-Release](https://github.com/Systems-Modeling/SysML-v2-Release): the SysML v2 specifications and training material
