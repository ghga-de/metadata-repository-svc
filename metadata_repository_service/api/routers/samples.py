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
"Routes for retrieving Samples"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.sample import get_sample
from metadata_repository_service.models import Sample

sample_router = APIRouter()


@sample_router.get(
    "/samples/{sample_id}",
    response_model=Sample,
    summary="Get a Sample",
    tags=["Query"],
)
async def get_samples(
    sample_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Sample ID, get the Sample record from the metadata store.
    """
    sample = await get_sample(sample_id=sample_id, embedded=embedded, config=config)
    if not sample:
        raise HTTPException(
            status_code=404,
            detail=f"{Sample.__name__} with id '{sample_id}' not found",
        )
    return sample
