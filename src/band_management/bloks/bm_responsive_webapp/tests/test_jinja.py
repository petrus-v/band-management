from ..jinja import highlight_match


def test_highlight_match():
    assert (
        highlight_match("Hello Pierre VerKest", "e verk")
        == 'Hello Pierr<strong class="has-text-danger">e VerK</strong>est'
    )
    assert highlight_match("Hello Pierre VerKest", "er") == (
        'Hello Pi<strong class="has-text-danger">er</strong>re V'
        '<strong class="has-text-danger">er</strong>Kest'
    )
    assert highlight_match("Hello Pierre VerKest", "") == "Hello Pierre VerKest"
