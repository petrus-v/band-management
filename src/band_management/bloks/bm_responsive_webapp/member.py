from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse

from anyblok.registry import Registry
from fastapi import Security

from band_management import _t
from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management.exceptions import PermissionDenied
from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    get_authenticated_musician,
    _get_musician_from_token,
    RenewTokenRoute,
)


router = APIRouter(
    prefix="/member",
    tags=["musician"],
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)


@router.put(
    "/{member_uuid}/accept",
)
def accept_member_invitation(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    member_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        member = anyblok.BandManagement.Member.query().get(member_uuid)
        if not member or member.musician != musician:
            raise PermissionDenied(
                _t(
                    "Your are not allowed to accept invitation for someone else.",
                    lang=musician.lang,
                ),
            )

        member.accept_invitation()
        return RedirectResponse(
            request.headers.get("HX-Current-URL", "/"),
            status_code=201,
            headers={
                # "HX-Redirect": "/bands/",
                "HX-Refresh": "true",
            },
        )


@router.put(
    "/{member_uuid}/reject",
)
def reject_member_invitation(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    member_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        member = anyblok.BandManagement.Member.query().get(member_uuid)
        if not member or member.musician != musician:
            raise PermissionDenied(
                _t(
                    "Your are not allowed to update other user active bands",
                    lang=musician.lang,
                ),
            )

        member.reject_invitation()
        return RedirectResponse(
            request.headers.get("HX-Current-URL", "/"),
            status_code=201,
            headers={
                # "HX-Redirect": "/bands/",
                "HX-Refresh": "true",
            },
        )
