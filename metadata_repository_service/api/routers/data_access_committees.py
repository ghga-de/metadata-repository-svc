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
"Routes for retrieving DataAccessCommittees"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.creation_models import CreateDataAccessCommittee
from metadata_repository_service.dao.data_access_committee import (
    create_data_access_committee,
    get_data_access_committee,
)
from metadata_repository_service.models import DataAccessCommittee

data_access_committee_router = APIRouter()


@data_access_committee_router.get(
    "/data_access_committees/{data_access_committee_id}",
    response_model=DataAccessCommittee,
    summary="Get a DataAccessCommittee",
    tags=["Query"],
)
async def get_data_access_committees(
    data_access_committee_id: str,
    embedded: bool = False,
    config: Config = Depends(get_config),
):
    """
    Given a DataAccessCommittee ID, get the DataAccessCommittee record
    from the metadata store.
    """
    data_access_committee = await get_data_access_committee(
        data_access_committee_id=data_access_committee_id,
        embedded=embedded,
        config=config,
    )
    if not data_access_committee:
        raise HTTPException(
            status_code=404,
            detail=f"{DataAccessCommittee.__name__} with id '{data_access_committee_id}' not found",
        )
    return data_access_committee


@data_access_committee_router.post(
    "/data_access_committees",
    response_model=DataAccessCommittee,
    summary="Create a DataAccessCommittee",
    tags=["DataAccessCommittee"],
)
async def create_data_access_committees(
    data_access_committee: CreateDataAccessCommittee,
    config: Config = Depends(get_config),
):
    """
    Create a DataAccessCommittee and write to the metadata store.
    """

    dac_entity = await create_data_access_committee(
        data_access_committee, config=config
    )
    return dac_entity
