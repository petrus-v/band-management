from band_management.bloks.bm_responsive_webapp.paging import paging_query


def test_paging_query(bm):
    elements, next_page, last_element = paging_query(
        bm.Score.query(), page=0, page_size=2
    )
    assert len(elements) == 2
    assert next_page == 1
    assert last_element == elements[-1]


def test_paging_query_page_over(bm):
    elements, next_page, last_element = paging_query(
        bm.Score.query(), page=9999, page_size=10000
    )
    assert len(elements) == 0
    assert next_page is None
    assert last_element is None
