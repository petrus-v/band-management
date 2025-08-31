import base64
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import HorizontalBarsDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from pathlib import Path
from io import BytesIO
from datetime import datetime
from anyblok import Declarations
from anyblok.relationship import Many2One
from anyblok.column import String, Text, DateTime
from random import choices, randint

from band_management import _t

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model
URI_CHARS = "abcdefghijkmnpqrstuvxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789"


@register(Model.BandManagement)
class Event(Mixin.PrimaryColumn):
    uri_code: str = String(
        label="Uri shorten code",
        nullable=False,
        default=lambda: "".join(choices(URI_CHARS, k=randint(3, 7))),
        unique=True,
    )
    name: str = String(
        label="Event name",
        size=256,
        index=True,
        nullable=False,
    )
    date: datetime = DateTime(
        nullable=False,
        index=True,
    )
    band: "Model.BandManagement.Band" = Many2One(
        model="Model.BandManagement.Band",
        nullable=False,
    )
    place: str = String(
        label="Event place",
        size=256,
    )
    comment: str = Text(label="More info not displayed on final report")
    header: str = Text(
        label="Header comment",
    )
    footer: str = Text(
        label="Footer comment",
    )

    def copy(self):
        BM = self.anyblok.BandManagement
        event = BM.Event.insert(
            name=self.name + _t(" (copy)"),
            date=self.date,
            band=self.band,
            place=self.place,
            comment=self.comment,
            header=self.header,
            footer=self.footer,
        )
        for music in self.musics:
            BM.EventMusic.insert(
                event=event,
                music_uuid=music.music_uuid,
                sequence=music.sequence,
                comment=music.comment,
            )
        return event

    @property
    def ordered_musics(self):
        return sorted(self.musics, key=lambda music: music.sequence)

    def print_for(self, musician):
        return self.print(musician.lang)

    def print(self, lang):
        pdf = self.anyblok.Report.print("event", self.prepare_event_report_data(lang))
        return pdf

    def prepare_event_report_data(self, lang):
        return {
            "lang": lang,
            "event": self,
            "amnezik_event_qrcode": self._generate_event_qrcode(),
        }

    def _generate_event_qrcode(self):
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
        )
        qr.add_data(f"https://www.amnezik.com/event/{self.uri_code}")
        image = qr.make_image(
            image_factory=StyledPilImage,
            embedded_image_path=(
                Path(__file__).parent / "documents" / "favicon.png"
            ).absolute(),
            module_drawer=HorizontalBarsDrawer(),
            color_mask=RadialGradiantColorMask(
                back_color=(255, 255, 255),
                center_color=(41, 41, 41),
                edge_color=(59, 124, 112),
            ),
        )
        buffered = BytesIO()
        image.save(buffered)
        return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode(
            "utf-8"
        )

    def update_event_musics(
        self,
        event_music_uuids: list[str],
        event_music_music_uuids: list[str],
        event_music_comments: list[str],
    ):
        position = 0
        BM = self.anyblok.BandManagement
        for to_remove in (
            BM.EventMusic.query()
            .filter(
                BM.EventMusic.event == self,
                BM.EventMusic.uuid.not_in(event_music_uuids),
            )
            .all()
        ):
            to_remove.delete()
        for event_music_uuid, event_music_music_uuid, event_music_comment in zip(
            event_music_uuids,
            event_music_music_uuids,
            event_music_comments,
        ):
            position += 1
            event_music = BM.EventMusic.query().get(event_music_uuid)
            if not event_music:
                method = BM.EventMusic.insert
            else:
                method = event_music.update
            music = BM.Music.query().get(event_music_music_uuid)
            if not music:
                raise ValueError(
                    _t("Music reference %(music_uuid)s not found")
                    % dict(music_uuid=event_music_music_uuid)
                )

            if not music.is_played_by(self.band):
                raise ValueError(
                    _t(
                        "This music %(music)s is not played by the current band %(band)s"
                    )
                    % dict(music=music.title, band=self.band.name)
                )

            method(
                uuid=event_music_uuid,
                event=self,
                music_uuid=event_music_music_uuid,
                sequence=position,
                comment=event_music_comment,
            )

    @classmethod
    def query_for_musician(cls, musician, query=None):
        if not query:
            query = cls.query()

        query = query.filter(cls.band == musician.active_band)

        query = query.order_by(cls.date.desc())

        return query
