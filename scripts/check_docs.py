"""Check repository Markdown links, conflict markers and the API snapshot offline."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parents[1]
errors = []
files = sorted(root.rglob('*.md'))
for path in files:
    content = path.read_text()
    if re.search(r'^(?:<{7}|={7}|>{7})(?: |$)', content, re.M):
        errors.append(f'{path.relative_to(root)}: unresolved merge marker')
    # Current docs use inline Markdown links; remote URLs are not fetched.
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
        target = target.strip('<>')
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        destination = path.parent / unquote(parts.path)
        if not destination.exists():
            errors.append(f'{path.relative_to(root)}: missing target {target}')
with (root / 'openapi.json').open() as stream:
    schema = json.load(stream)
if not schema.get('openapi') or not isinstance(schema.get('paths'), dict):
    errors.append('openapi.json: expected an OpenAPI document with paths')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Checked {len(files)} Markdown files: local link targets, merge markers and OpenAPI JSON pass.')
