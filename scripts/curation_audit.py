"""Apply explicit curation receipts without rewriting historical image baselines."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/'curation/2026-11-15-dedup/deletions.json'


def assert_preserved_images(baseline):
    receipt=json.loads(RECEIPT.read_text())
    deleted={item['path']:item for item in receipt['deleted_files']}
    rebuilt={item['path']:item for item in receipt['rebuilt_contact_sheets']}
    assert not set(deleted)&set(rebuilt)
    for name,digest in baseline.items():
        path=ROOT/name
        if name in deleted:
            assert deleted[name]['sha256_before']==digest,name
            assert not path.exists(),name+' was authorized for deletion but still exists'
        elif name in rebuilt:
            assert rebuilt[name]['sha256_before']==digest,name
            assert hashlib.sha256(path.read_bytes()).hexdigest()==rebuilt[name]['sha256_after'],name
        else:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name


def deleted_paths():
    return {item['path'] for item in json.loads(RECEIPT.read_text())['deleted_files']}
