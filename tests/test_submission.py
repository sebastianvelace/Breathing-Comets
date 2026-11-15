from pipelines.submission import render


def test_submission_uses_shipped_counts_and_keeps_only_the_user_disclosure_marker():
    text = render()
    assert text.count('[') == text.count(']') == 1
    assert '[This section is written by Sebastián before submission.]' in text
    assert 'All 50 validation pairs' in text
    assert '184/184' not in text
    assert 'Sum mode' not in text
    assert 'independent discovery' in text
    assert 'video is produced separately' in text
