def import_declarations(reload=None):
    from . import musician

    if reload is not None:
        reload(musician)
