from band_management import config


def paging_query(query, page: int = 0, page_size: int = config.ITEM_PER_PAGE):
    limit = page_size
    offset = page * limit
    query = query.limit(limit + 1)
    query = query.offset(offset)
    next_page = None
    if query.count() > limit:
        next_page = page + 1
    elements = query.all()[:limit]
    return elements, next_page, elements[-1] if elements else None
