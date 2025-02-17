from .base import FileSystemStorage


def storage_factory(*args, **kwargs):
    return FileSystemStorage
