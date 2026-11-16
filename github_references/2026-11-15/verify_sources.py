"""Verify pinned source images, code snapshots and licenses for the unified gallery."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_digest(path):
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def collect():
    # One canonical source manifest; downloaded candidates were consolidated.
    items = json.loads((ROOT / 'manifest.json').read_text())['figures']
    for item in items:
        for field in ['original_local', 'preview_local', 'source_local', 'license_local']:
            assert (ROOT / item[field]).is_file(), item[field]
        assert digest(ROOT / item['original_local']) == item['original_sha256'], item['id']
        assert blob_digest(ROOT / item['original_local']) == item['image_blob_sha'], item['id']
        if 'source_blob_sha' in item:
            assert blob_digest(ROOT / item['source_local']) == item['source_blob_sha'], item['id']
        with Image.open(ROOT / item['preview_local']) as image:
            item['preview_dimensions'] = list(image.size)
        item['preview_sha256'] = digest(ROOT / item['preview_local'])
        item['source_sha256'] = digest(ROOT / item['source_local'])
        item['license_sha256'] = digest(ROOT / item['license_local'])
        item['original_upstream_image'] = True
        item['our_redraw'] = False
        item['code_execution'] = 'Source inspected; not executed.'
    assert len({item['original_sha256'] for item in items}) == len(items)
    return items



def main():
    items = collect()
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    manifest.update(scope='Source records used by the unified chart-type gallery', figures=items, count=len(items))
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Verified {len(items)} pinned source images, snapshots and licenses.')


if __name__ == '__main__':
    main()
