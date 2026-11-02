"""Render F03_webthinker_nested; edit ../specs/F03_webthinker_nested.json to change the diagram."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render import options, render

if __name__ == "__main__":
    render("F03_webthinker_nested", options("F03_webthinker_nested"))
