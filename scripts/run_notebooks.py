#!/usr/bin/env python
"""
Execute all notebooks and save outputs.

This script runs all notebooks in order, populating the database
and saving outputs (diagrams, tables, visualizations) inline.

Usage:
    python scripts/run_notebooks.py

Requirements:
    pip install lcms-demo[notebooks]
    # or: uv sync --group dev --all-extras
"""

import subprocess
import sys
from pathlib import Path


def run_notebook(notebook_path: Path, timeout: int = 600) -> bool:
    """
    Execute a notebook in place, saving outputs.

    Parameters
    ----------
    notebook_path : Path
        Path to the notebook file.
    timeout : int
        Execution timeout in seconds.

    Returns
    -------
    bool
        True if execution succeeded, False otherwise.
    """
    print(f"\n{'=' * 60}")
    print(f"Executing: {notebook_path.name}")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            f"--ExecutePreprocessor.timeout={timeout}",
            str(notebook_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"FAILED: {notebook_path.name}")
        print(result.stderr)
        return False

    print(f"SUCCESS: {notebook_path.name}")
    return True


def main():
    """Execute all notebooks in order."""
    # Find project root (parent of scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    notebooks_dir = project_root / "notebooks"

    if not notebooks_dir.exists():
        print(f"Error: notebooks directory not found at {notebooks_dir}")
        sys.exit(1)

    # Get notebooks in order
    notebooks = sorted(notebooks_dir.glob("*.ipynb"))

    if not notebooks:
        print("No notebooks found.")
        sys.exit(1)

    print(f"Found {len(notebooks)} notebooks to execute:")
    for nb in notebooks:
        print(f"  - {nb.name}")

    # Execute each notebook
    failed = []
    for notebook in notebooks:
        if not run_notebook(notebook):
            failed.append(notebook)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total:   {len(notebooks)}")
    print(f"Success: {len(notebooks) - len(failed)}")
    print(f"Failed:  {len(failed)}")

    if failed:
        print("\nFailed notebooks:")
        for nb in failed:
            print(f"  - {nb.name}")
        sys.exit(1)

    print("\nAll notebooks executed successfully!")
    print("Outputs have been saved inline in each notebook.")


if __name__ == "__main__":
    main()
