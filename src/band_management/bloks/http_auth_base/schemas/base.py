from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from uuid_extensions import uuid7


class RefSchema(BaseModel):
    """Main Band Management Base Model
    which can be use later to manage
    common behavior like managing schema
    version.
    """

    model_config = ConfigDict(from_attributes=True)

    uuid: UUID = Field(
        default_factory=uuid7,
        title="Primary key",
        description="Primary key using UUID7 format",
    )


class BMBaseModel(RefSchema):
    """Main Band Management Base Model
    which can be use later to manage
    common behavior like managing schema
    version.
    """


# TypeItems = TypeVar("TypeItems")


# # class PaginateInfo(BaseModel):
# #     model_config = ConfigDict(extra="ignore")

# #     per_page: int = Field(help="Number of elements per page", default=80)
# #     page: int = Field(help="Page number, first page is 0")


# # class PaginatedResult(BaseModel, Generic[TypeItems]):
# #     model_config = ConfigDict(extra="ignore")

# #     items: list[TypeItems]
# #     page_info: PaginateInfo
# #     have_more: bool  = Field(
# #         help="What ever there is at least one element in the next page"
# #     )


# class ListOf(BaseModel, Generic[TypeItems]):
#     """Non paginate result, usefull to wrapp list[object]
#     to easily serialize/deserialyze data
#     """

#     model_config = ConfigDict(extra="ignore")
#     items: list[TypeItems]
