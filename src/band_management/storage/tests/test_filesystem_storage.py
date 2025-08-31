from uuid_extensions import uuid7
import pytest
from band_management.storage import FileSystemStorage


@pytest.fixture()
async def attachment(uploaded_score_attachment):
    file = FileSystemStorage()
    await file.save(uploaded_score_attachment)
    return file


@pytest.mark.asyncio
async def test_save(uploaded_score_attachment):
    ref = uuid7()
    attachment = FileSystemStorage(reference=ref)
    await attachment.save(uploaded_score_attachment)
    assert attachment.path.exists()
    assert attachment.storage_metadata.original_filename == "myscore.pdf"
    assert attachment.reference == ref


@pytest.mark.asyncio
async def test_remove(attachment):
    attachment = await attachment
    await attachment.remove()
    assert not attachment.path.exists()


@pytest.mark.asyncio
async def test_new_attachement_from_metadata(attachment):
    attachment = await attachment
    new_file = FileSystemStorage(
        reference=attachment.reference, storage_metadata=attachment.file_metadata
    )
    assert new_file.reference == attachment.reference
    assert new_file.file_metadata == attachment.file_metadata
    assert new_file.path == attachment.path
