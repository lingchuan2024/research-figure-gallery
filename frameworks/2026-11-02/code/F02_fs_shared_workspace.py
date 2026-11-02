"""Render F02_fs_shared_workspace; edit ../specs/F02_fs_shared_workspace.json to change the diagram."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render import options, render

if __name__ == "__main__":
    render("F02_fs_shared_workspace", options("F02_fs_shared_workspace"))
