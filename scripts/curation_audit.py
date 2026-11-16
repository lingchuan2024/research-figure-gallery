"""Apply explicit curation receipts without rewriting historical image baselines."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/'curation/2026-11-15-dedup/deletions.json'
FAMILY_RECEIPT=ROOT/'curation/2026-11-16-families/changes.json'
FAMILY_OVERVIEW='docs/gallery_overview.png'


def _authorized_changes():
    """Validate the chronological receipts before following their hash chains."""
    receipts=[json.loads(RECEIPT.read_text())]
    if FAMILY_RECEIPT.is_file():
        family=json.loads(FAMILY_RECEIPT.read_text())
        changes=family.get('rebuilt_contact_sheets',[])
        assert not family.get('deleted_files',[]),'Family curation does not authorize deletions'
        assert len(changes)==1 and changes[0]['path']==FAMILY_OVERVIEW, \
            'Family curation may rebuild only '+FAMILY_OVERVIEW
        receipts.append(family)
    deleted={}
    rebuilt={}
    for receipt in receipts:
        for item in receipt.get('deleted_files',[]):
            name=item['path']
            assert name not in deleted and name not in rebuilt,name+' has conflicting receipts'
            deleted[name]=item
        for item in receipt.get('rebuilt_contact_sheets',[]):
            name=item['path']
            assert name not in deleted,name+' cannot be deleted and rebuilt'
            chain=rebuilt.setdefault(name,[])
            if chain:
                assert chain[-1]['sha256_after']==item['sha256_before'],name+' has a broken receipt chain'
            chain.append(item)
    return deleted,rebuilt


def assert_preserved_images(baseline):
    deleted,rebuilt=_authorized_changes()
    for name,digest in baseline.items():
        path=ROOT/name
        if name in deleted:
            assert deleted[name]['sha256_before']==digest,name
            assert not path.exists(),name+' was authorized for deletion but still exists'
        elif name in rebuilt:
            chain=rebuilt[name]
            checkpoints={chain[0]['sha256_before'],*(item['sha256_after'] for item in chain)}
            assert digest in checkpoints,name+' baseline is not an authorized checkpoint'
            assert hashlib.sha256(path.read_bytes()).hexdigest()==chain[-1]['sha256_after'],name
        else:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    # Some older baselines predate the unified docs overview. Its latest
    # authorized result must still be checked rather than silently ignored.
    for name,chain in rebuilt.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==chain[-1]['sha256_after'],name


def deleted_paths():
    return set(_authorized_changes()[0])
