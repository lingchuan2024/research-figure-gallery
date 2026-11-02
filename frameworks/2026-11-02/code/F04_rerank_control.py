"""Render F04_rerank_control; edit ../specs/F04_rerank_control.json to change the diagram."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render import options, render

if __name__ == "__main__":
    render("F04_rerank_control", options("F04_rerank_control"))
