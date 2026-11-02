"""Render only the framework additions; existing gallery images are never touched."""
from pathlib import Path
import argparse
import json
from types import SimpleNamespace
from render import HERE, render

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=HERE/"figures")
    parser.add_argument("--data-dir",type=Path,default=HERE/"specs")
    parser.add_argument("--formats",nargs="+",choices=["png","svg"],default=["png","svg"])
    args=parser.parse_args()
    for item in json.loads((HERE/"manifest.json").read_text()):
        render(item["id"],args)
        print("Rendered "+item["id"])

if __name__=="__main__":main()
