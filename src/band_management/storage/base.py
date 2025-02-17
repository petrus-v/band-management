from typing import Type
from uuid_extensions import uuid7
from abc import ABC, abstractmethod
from mimetypes import guess_file_type
from fastapi import UploadFile
from band_management import config
from pydantic import BaseModel
from aiofile import async_open


class StorageMetadata(BaseModel):
    original_filename: str | None = None
    mime_type: str | None = None
    size: int | None = None


class FileSystemStorageMetadata(StorageMetadata):
    relative_path: str | None = None


class IStorage(ABC):
    """Iterface to manage files in an async way
    that should make easier to move from filesystem to an
    other backend such as s3 likes / postgreql large object / nextcloud...
    """

    MetadataClass = StorageMetadata
    reference: uuid7
    storage_metadata: Type[StorageMetadata]

    def __init__(self, reference: uuid7 = None, storage_metadata: dict = None):
        if reference is None:
            reference = uuid7()

        self.reference = reference
        if storage_metadata is None:
            storage_metadata = {}

        self.storage_metadata = self.MetadataClass(**storage_metadata)

    async def save(self, upload_file: UploadFile):
        self.storage_metadata.original_filename = upload_file.filename
        self.storage_metadata.mime_type = upload_file.headers.get("content-type")
        if not self.storage_metadata.mime_type:
            self.storage_metadata.mime_type = guess_file_type(upload_file.filename)[0]
        self.storage_metadata.size = upload_file.size
        await self._save(upload_file)

    @abstractmethod
    async def _save(self, file_pointer: UploadFile):
        """Save file somewhere in an async way"""

    @property
    def file_metadata(self):
        return self.storage_metadata.model_dump()


class FileSystemStorage(IStorage):
    MetadataClass = FileSystemStorageMetadata

    @property
    def path(self):
        if self.storage_metadata.relative_path:
            return config.ORIGINAL_SCORE_PATH / self.storage_metadata.relative_path
        reference = str(self.reference)
        return config.ORIGINAL_SCORE_PATH / reference[:2] / reference[2:]

    @property
    def relative_path(self) -> str:
        return str(self.path.relative_to(config.ORIGINAL_SCORE_PATH))

    def ensure_directory(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def _save(self, upload_file: UploadFile):
        self.ensure_directory()
        async with (
            async_open(upload_file.file) as src,
            async_open(self.path, "wb") as dest,
        ):
            async for chunk in src.iter_chunked():
                await dest.write(chunk)
        self.storage_metadata.relative_path = self.relative_path
