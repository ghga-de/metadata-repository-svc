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
"Routes for retrieving Biospecimens"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.biospecimen import get_biospecimen
from metadata_repository_service.models import Biospecimen

biospecimen_router = APIRouter()


@biospecimen_router.get(
    "/biospecimens/{biospecimen_id}",
    response_model=Biospecimen,
    summary="Get a Biospecimen",
    tags=["Query"],
)
async def get_biospecimens(
    biospecimen_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Biospecimen ID, get the Biospecimen record from the metadata store.
    """
    biospecimen = await get_biospecimen(
        biospecimen_id=biospecimen_id, embedded=embedded, config=config
    )
    if not biospecimen:
        raise HTTPException(
            status_code=404,
            detail=f"{Biospecimen.__name__} with id '{biospecimen_id}' not found",
        )
    return biospecimen
