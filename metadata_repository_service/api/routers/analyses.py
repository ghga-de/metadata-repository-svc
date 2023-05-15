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
"Routes for retrieving Analyses"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.analysis import get_analysis
from metadata_repository_service.models import Analysis

analysis_router = APIRouter()


@analysis_router.get(
    "/analyses/{analysis_id}",
    response_model=Analysis,
    summary="Get an Analysis",
    tags=["Query"],
)
async def get_analyses(
    analysis_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given an Analysis ID, get the Analysis record from the metadata store.
    """
    analysis = await get_analysis(
        analysis_id=analysis_id, embedded=embedded, config=config
    )
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"{Analysis.__name__} with id '{analysis_id}' not found",
        )
    return analysis
