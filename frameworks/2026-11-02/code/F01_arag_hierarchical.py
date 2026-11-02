"""Render F01_arag_hierarchical; edit ../specs/F01_arag_hierarchical.json to change the diagram."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render import options, render

if __name__ == "__main__":
    render("F01_arag_hierarchical", options("F01_arag_hierarchical"))
