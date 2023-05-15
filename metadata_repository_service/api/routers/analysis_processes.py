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
"Routes for retrieving Analysis Processes"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.analysis_process import get_analysis_process
from metadata_repository_service.models import AnalysisProcess

analysis_process_router = APIRouter()


@analysis_process_router.get(
    "/analysis_process/{analysis_process_id}",
    response_model=AnalysisProcess,
    summary="Get an AnalysisProcess",
    tags=["Query"],
)
async def get_analysis_processes(
    analysis_process_id: str,
    embedded: bool = False,
    config: Config = Depends(get_config),
):
    """
    Given an AnalysisProcess ID, get the AnalysisProcess record from the metadata store.
    """
    analysis_process = await get_analysis_process(
        analysis_process_id=analysis_process_id, embedded=embedded, config=config
    )
    if not analysis_process:
        raise HTTPException(
            status_code=404,
            detail=f"{AnalysisProcess.__name__} with id '{analysis_process_id}' not found",
        )
    return analysis_process
