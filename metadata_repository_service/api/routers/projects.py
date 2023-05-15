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
"Routes for retrieving Projects"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.project import get_project
from metadata_repository_service.models import Project

project_router = APIRouter()


@project_router.get(
    "/projects/{project_id}",
    response_model=Project,
    summary="Get a Project",
    tags=["Query"],
)
async def get_projects(
    project_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Project ID, get the Project record from the metadata store.
    """
    project = await get_project(project_id=project_id, embedded=embedded, config=config)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"{Project.__name__} with id '{project_id}' not found",
        )
    return project
