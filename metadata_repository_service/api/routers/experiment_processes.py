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
"Routes for retrieving ExperimentProcesses"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.experiment_process import get_experiment_process
from metadata_repository_service.models import ExperimentProcess

experiment_process_router = APIRouter()


@experiment_process_router.get(
    "/experiment_processes/{experiment_process_id}",
    response_model=ExperimentProcess,
    summary="Get a ExperimentProcess",
    tags=["Query"],
)
async def get_experiment_processes(
    experiment_process_id: str,
    embedded: bool = False,
    config: Config = Depends(get_config),
):
    """
    Given a ExperimentProcess ID, get the ExperimentProcess record from the metadata store.
    """
    experiment_process = await get_experiment_process(
        experiment_process_id=experiment_process_id, embedded=embedded, config=config
    )
    if not experiment_process:
        raise HTTPException(
            status_code=404,
            detail=f"{ExperimentProcess.__name__} with id '{experiment_process_id}' not found",
        )
    return experiment_process
