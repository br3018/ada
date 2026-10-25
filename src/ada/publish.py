"""Publish a SysML v2 textual model to the API server using the pilot Jupyter kernel.

The API server only accepts model elements as JSON, so the file is parsed by the SysML kernel
(installed in the dev image) and pushed with its %publish magic.

Each %publish replaces the whole content of its project with the published element, so every
top-level element goes to its own project, named after the element unless --project is given.

Usage: python -m ada.publish FILE [--element NAME] [--project NAME] [--server URL] [--verbose]
"""

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import nbformat
from nbclient import NotebookClient

from ada.pilot_connector import DEFAULT_SERVER_URL

KERNEL_NAME = "sysml"
# Starting the kernel loads the whole standard library, which takes most of a minute
TIMEOUT_SECONDS = 600
TOP_LEVEL_PACKAGE = re.compile(
    r"^(?:standard\s+)?(?:library\s+)?package\s+('[^']+'|[\w$]+)", re.MULTILINE
)


def find_top_level_packages(source: str) -> list[str]:
    """Return the names of packages declared at the start of a line (i.e. not indented)."""
    return TOP_LEVEL_PACKAGE.findall(source)


def cell_text(cell) -> str:
    """Join the text of a cell's outputs (stdout, stderr and results)."""
    parts = []
    for output in cell.outputs:
        if output.output_type == "stream":
            parts.append(output.text)
        elif output.output_type in ("execute_result", "display_data"):
            parts.append(output.data.get("text/plain", ""))
        elif output.output_type == "error":
            parts.append(f"ERROR:{output.ename}: {output.evalue}\n")
    return "".join(parts)


def has_errors(text: str) -> bool:
    """The kernel reports parse and publish failures as lines starting with ERROR:."""
    return any(line.startswith("ERROR") for line in text.splitlines())


def server_problem(server_url: str) -> str | None:
    """Return why the API server can't be used, or None if it answers."""
    try:
        with urllib.request.urlopen(f"{server_url}/projects", timeout=10):
            return None
    except urllib.error.HTTPError as error:
        return f"answered {server_url}/projects with HTTP {error.code}"
    except (urllib.error.URLError, OSError) as error:
        reason = getattr(error, "reason", error)
        return f"isn't responding ({reason})"


def publish(
    path: Path, elements: list[str], project: str | None, server_url: str, verbose: bool
) -> bool:
    """Parse the model at path and publish each element. Returns True on success."""
    project_arg = f'--project="{project}" ' if project else ""
    sources = [f"%repo {server_url}", path.read_text()]
    sources += [f"%publish {project_arg}{element}" for element in elements]
    nb = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_code_cell(source) for source in sources]
    )

    client = NotebookClient(nb, kernel_name=KERNEL_NAME, timeout=TIMEOUT_SECONDS)
    kernel_output = None if verbose else subprocess.DEVNULL
    print(f"Starting the SysML kernel and parsing {path}...", flush=True)
    with client.setup_kernel(stdout=kernel_output, stderr=kernel_output):
        for index, cell in enumerate(nb.cells):
            client.execute_cell(cell, index)
            text = cell_text(cell)
            print(text, end="", flush=True)
            if has_errors(text):
                return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", type=Path, help="the .sysml file to publish")
    parser.add_argument(
        "--element",
        help="fully qualified element to publish (default: each top-level package in the file)",
    )
    parser.add_argument(
        "--project", help="project to create or update (default: the element's name)"
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER_URL,
        help=f"API server URL (default: {DEFAULT_SERVER_URL})",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="show the kernel's own log output"
    )
    args = parser.parse_args()

    elements = (
        [args.element]
        if args.element
        else find_top_level_packages(args.file.read_text())
    )
    if not elements:
        parser.error(
            f"no top-level package found in {args.file}; name one with --element"
        )
    if args.project and len(elements) > 1:
        parser.error(
            f"{args.file} has {len(elements)} top-level packages ({', '.join(elements)}) and each publish "
            "replaces the project's content; drop --project to publish each to its own project, "
            "or pick one with --element"
        )

    # Checked up front: the kernel takes most of a minute to start and reports this as a Java stack trace
    problem = server_problem(args.server)
    if problem:
        print(
            f"error: the API server at {args.server} {problem}.\n"
            "Start it with 'make api-up'. After it starts, it takes some time before it answers requests; "
            "'make api-logs' shows its progress.",
            file=sys.stderr,
        )
        return 1

    return (
        0
        if publish(args.file, elements, args.project, args.server, args.verbose)
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
