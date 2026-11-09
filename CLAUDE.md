# CLAUDE.md

This file gives guidance to Claude Code (claude.ai/code) for the code in this repository.

## What this is

Ada is a dev environment for SysML v2 system design and verification. The pipeline is:

```text
model/*.sysml ──make sysml-validate──▶ sysml -strict -validate (OpenSysML CLI) ──▶ pass or fail
```

README.md is the reference for users and has the full details. Update it when the behaviour or the commands change.

## Commands

All commands run in the dev container. `make help` shows the list of targets.

```sh
make sysml-validate [MODEL=model/Foo.sysml]  # sysml -strict -validate; MODEL is model/ by default
uv sync                                      # update the venv at /home/vscode/.venvs/ada after a pyproject.toml change
sysml -help                                  # all the options of the sysml CLI
sysml -explain <code>                        # cause and solution for a diagnostic code
```

## Architecture

- **Model (`model/`)**: `Model.sysml` imports the parts in `PartLibrary.sysml`. The `sysml` tool loads all the files that it gets as one model, so the file order is not important.
- **Python**: Ada is not a Python package (`tool.uv.package = false`). uv only manages the Python version and the virtual environment.
- **Dev container (`.devcontainer/`)**: the image installs uv and the `sysml` CLI from `https://opensysml.org/install.sh`. The `OPENSYSML_VERSION` build argument in the Dockerfile pins the release (now `v0.12.1`). To update it, change the argument and rebuild the dev container. README "OpenSysML version" gives the procedure. devcontainer.json also installs the Syside VS Code extension for SysML v2.

## Conversational style

Write and converse in ASD-STE100 Simplified Technical English:

- Use short sentences: at most 20 words in procedural text and 25 in descriptive text.
- Write each instruction as one action in the imperative ("Run make setup.").
- Use the active voice and simple present, past or future tenses only.
- Use one word for one meaning, and use the same term every time.
- Do not use phrasal verbs, -ing verb forms or long noun clusters.
- Put a list of numbered steps in each procedure, and give one instruction per step.
Code, commands and file names stay as they are.

When something is unclear, ask the user to clarify.

When making a change, provide options along with a reccomendation and why.