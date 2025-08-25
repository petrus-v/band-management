import pytest
from uuid_extensions import uuid7
from band_management.storage import storage_factory
from band_management.exceptions import ValidationError, PermissionDenied


@pytest.fixture()
async def score_with_attachment(
    bm, uploaded_score_attachment, esperanza_music, joe_pamh_current_active_band
):
    StorageClass = storage_factory()
    score_document = StorageClass()
    await score_document.save(uploaded_score_attachment)
    return bm.Score.insert(
        uuid=score_document.reference,
        name="Accordion voice",
        imported_by=joe_pamh_current_active_band,
        storage_file_metadata=score_document.file_metadata,
    )


def test_score_name_from_filename(bm):
    assert (
        bm.Score.name_from_filename("valse-des-petits-CHEVAUX_de-Bois.pdf")
        == "Valse des petits chevaux de bois"
    )


def test_query_for_musician(bm, joe_pamh_current_active_band):
    scores = bm.Score.query_for_musician(joe_pamh_current_active_band).all()
    # 1 score imported (polka pomme)
    # 1 score with music no bands (jet du lama)
    # 3 PAMH as 2 music with 3 scores: 1 envole + 2 zelda
    assert len(scores) == 5
    assert [(s.music.title if s.music else "", s.name) for s in scores] == [
        ("", "Polka pomme"),
        ("Le Jet du Lama", "Voice 1 - G/C accordéon"),
        ("L'envole", "Voice 1"),
        (
            "Zelda",
            "Voice 1 - Zelda",
        ),
        ("Zelda", "Voice 2 - Zelda"),
    ]


def test_query_for_musician_without_draft_scores(bm, joe_pamh_current_active_band):
    scores = bm.Score.query_for_musician(
        joe_pamh_current_active_band, with_draft_score=False
    ).all()
    # 3 PAMH as 2 music with 3 scores: 1 envole + 2 zelda
    assert len(scores) == 3
    assert [(s.music.title if s.music else "", s.name) for s in scores] == [
        ("L'envole", "Voice 1"),
        (
            "Zelda",
            "Voice 1 - Zelda",
        ),
        ("Zelda", "Voice 2 - Zelda"),
    ]


def test_query_for_musician_trib_active(bm, joe_musician, trib_band):
    joe_musician.set_active_band(trib_band.uuid)
    scores_query = bm.Score.query_for_musician(joe_musician, query=bm.Score.query())
    scores = scores_query.all()
    assert len(scores) == 5
    # 1 score imported (polka pomme)
    # 1 score with music no bands (jet du lama)
    # 3 tradamuse as 2 music with 3 scores: 1 esperanza + 2 zelda
    assert [(s.music.title if s.music else "", s.name) for s in scores] == [
        ("", "Polka pomme"),
        ("Esperanza", "Voice 1"),
        ("Le Jet du Lama", "Voice 1 - G/C accordéon"),
        (
            "Zelda",
            "Voice 1 - Zelda",
        ),
        ("Zelda", "Voice 2 - Zelda"),
    ]


def test_score_update_by(bm, joe_pamh_current_active_band, pamh_band, esperanza_music):
    assert pamh_band not in esperanza_music.bands
    esperanza_voice_3 = bm.Score.insert(
        name="voice 3", imported_by=joe_pamh_current_active_band
    )
    esperanza_voice_3.update_by(
        joe_pamh_current_active_band,
        name="Esperanza - Voice 3",
        source_writer_credits="Test",
        music_uuid=esperanza_music.uuid,
    )
    assert esperanza_voice_3.music == esperanza_music
    assert pamh_band in esperanza_music.bands
    assert esperanza_voice_3.name == "Esperanza - Voice 3"
    assert esperanza_voice_3.source_writer_credits == "Test"
    other_music = bm.Music.insert(
        title="Other",
    )
    esperanza_voice_3.update_by(
        joe_pamh_current_active_band,
        name="",
        source_writer_credits="",
        music_uuid=other_music.uuid,
    )
    assert esperanza_voice_3.music == other_music
    assert pamh_band in esperanza_music.bands
    assert pamh_band in other_music.bands
    assert esperanza_voice_3.name == "Esperanza - Voice 3"
    assert esperanza_voice_3.source_writer_credits is None

    esperanza_voice_3.update_by(
        joe_pamh_current_active_band, name="", source_writer_credits="", music_uuid=""
    )
    assert esperanza_voice_3.music is None


@pytest.mark.asyncio
async def test_remove_score(bm, score_with_attachment):
    score_with_attachment = await score_with_attachment
    StorageClass = storage_factory()
    score_document = StorageClass(
        reference=score_with_attachment.uuid,
        storage_metadata=score_with_attachment.storage_file_metadata,
    )
    assert score_document.path.exists()
    await score_with_attachment.delete()
    assert not score_document.path.exists()


@pytest.mark.asyncio
async def test_remove_score_not_allowed(
    bm, score_with_attachment, esperanza_music, joe_pamh_current_active_band
):
    score_with_attachment = await score_with_attachment
    score_with_attachment.music = esperanza_music
    StorageClass = storage_factory()
    StorageClass(
        reference=score_with_attachment.uuid,
        storage_metadata=score_with_attachment.storage_file_metadata,
    )
    with pytest.raises(
        ValidationError, match="Only scores unlink to its music can be removed"
    ):
        await bm.Score.delete_by(
            score_with_attachment.uuid, joe_pamh_current_active_band
        )


@pytest.mark.asyncio
async def test_delete_by(bm, score_with_attachment, joe_pamh_current_active_band):
    score_with_attachment = await score_with_attachment
    StorageClass = storage_factory()
    score_document = StorageClass(
        reference=score_with_attachment.uuid,
        storage_metadata=score_with_attachment.storage_file_metadata,
    )
    assert score_document.path.exists()
    await bm.Score.delete_by(score_with_attachment.uuid, joe_pamh_current_active_band)
    assert not score_document.path.exists()


@pytest.mark.asyncio
async def test_delete_by_not_allowed(bm, score_with_attachment, doe_musician):
    score_with_attachment = await score_with_attachment
    StorageClass = storage_factory()
    score_document = StorageClass(
        reference=score_with_attachment.uuid,
        storage_metadata=score_with_attachment.storage_file_metadata,
    )
    assert score_document.path.exists()
    with pytest.raises(
        PermissionDenied,
        match=(
            "You are not allowed to delete this score. "
            "Only the one who imported it can remove it."
        ),
    ):
        await bm.Score.delete_by(score_with_attachment.uuid, doe_musician)


def test_get_by(bm, joe_pamh_current_active_band, pamh_band, zelda_music):
    assert pamh_band in zelda_music.bands
    zelda_voice_3 = bm.Score.insert(
        name="voice 3", imported_by=joe_pamh_current_active_band
    )
    assert (
        bm.Score.get_by(zelda_voice_3.uuid, joe_pamh_current_active_band)
        == zelda_voice_3
    )


def test_get_by_unknown_ref(bm, joe_pamh_current_active_band):
    assert bm.Score.get_by(uuid7(), joe_pamh_current_active_band) is None


def test_get_imported_non_active_band(
    bm, joe_pamh_current_active_band, pamh_band, tradamuse_band, esperanza_music
):
    assert pamh_band not in esperanza_music.bands
    esperanza_voice_3 = bm.Score.insert(
        name="voice 3",
        imported_by=joe_pamh_current_active_band,
        music_uuid=esperanza_music.uuid,
    )
    assert pamh_band not in esperanza_music.bands
    assert (
        bm.Score.get_by(esperanza_voice_3.uuid, joe_pamh_current_active_band)
        == esperanza_voice_3
    )


def test_get_by_permission_denied(
    bm,
    doe_musician,
    joe_pamh_current_active_band,
    pamh_band,
    tradamuse_band,
    esperanza_music,
):
    assert pamh_band not in esperanza_music.bands
    esperanza_voice_3 = bm.Score.insert(
        name="voice 3",
        imported_by=doe_musician,
        music_uuid=esperanza_music.uuid,
    )
    assert pamh_band not in esperanza_music.bands
    with pytest.raises(
        PermissionDenied,
        match=(
            "You are not allowed to access to this score "
            f"not link to your current band {pamh_band.name}"
        ),
    ):
        bm.Score.get_by(esperanza_voice_3.uuid, joe_pamh_current_active_band)
