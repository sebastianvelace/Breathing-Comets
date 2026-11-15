import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def test_all_fifty_neowise_pairs_keep_the_exported_cv_ratio():
    folder = ROOT/'apps/web/static/data/neo'
    refs = json.loads((folder/'validation_diameters.json').read_text())
    cv = json.loads((folder/'validation.json').read_text())['cv']
    assert len(refs['points']) == len(cv) == 50
    assert {p['key'] for p in refs['points']} == {p['key'] for p in cv}
    ratios = {p['key']: p['D_ratio'] for p in cv}
    for p in refs['points']:
        assert p['reference_rows'] >= 1
        assert p['neowise_km'] > 0
        assert p['ratio'] == ratios[p['key']]
        assert p['spherex_km']/p['neowise_km'] == pytest.approx(p['ratio'])
    assert hashlib.sha256((ROOT/refs['retained_source']).read_bytes()).hexdigest() == refs['sha256']
