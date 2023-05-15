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
"Routes for retrieving Publications"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.publication import get_publication
from metadata_repository_service.models import Publication

publication_router = APIRouter()


@publication_router.get(
    "/publications/{publication_id}",
    response_model=Publication,
    summary="Get a Publication",
    tags=["Query"],
)
async def get_publications(
    publication_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Publication ID, get the Publication record from the metadata store.
    """
    publication = await get_publication(
        publication_id=publication_id, embedded=embedded, config=config
    )
    if not publication:
        raise HTTPException(
            status_code=404,
            detail=f"{Publication.__name__} with id '{publication_id}' not found",
        )
    return publication
