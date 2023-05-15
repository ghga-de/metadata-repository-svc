# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"Routes for retrieving Members"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.member import get_member
from metadata_repository_service.models import Member

member_router = APIRouter()


@member_router.get(
    "/members/{member_id}",
    response_model=Member,
    summary="Get a Member",
    tags=["Query"],
)
async def get_members(
    member_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Member ID, get the Member record from the metadata store.
    """
    member = await get_member(member_id=member_id, embedded=embedded, config=config)
    if not member:
        raise HTTPException(
            status_code=404,
            detail=f"{Member.__name__} with id '{member_id}' not found",
        )
    return member
