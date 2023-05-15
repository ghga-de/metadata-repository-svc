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
"Routes for retrieving DataAccessPolicys"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.creation_models import (
    CreateDataAccessCommittee,
    CreateDataAccessPolicy,
)
from metadata_repository_service.dao.data_access_committee import (
    get_data_access_committee_by_accession,
)
from metadata_repository_service.dao.data_access_policy import (
    create_data_access_policy,
    get_data_access_policy,
)
from metadata_repository_service.models import DataAccessPolicy

data_access_policy_router = APIRouter()


@data_access_policy_router.get(
    "/data_access_policies/{data_access_policy_id}",
    response_model=DataAccessPolicy,
    summary="Get a DataAccessPolicy",
    tags=["Query"],
)
async def get_data_access_policies(
    data_access_policy_id: str,
    embedded: bool = False,
    config: Config = Depends(get_config),
):
    """
    Given a DataAccessPolicy ID, get the DataAccessPolicy record from the metadata store.
    """
    data_access_policy = await get_data_access_policy(
        data_access_policy_id=data_access_policy_id, embedded=embedded, config=config
    )
    if not data_access_policy:
        raise HTTPException(
            status_code=404,
            detail=f"{DataAccessPolicy.__name__} with id '{data_access_policy_id}' not found",
        )
    return data_access_policy


@data_access_policy_router.post(
    "/data_access_policies",
    response_model=DataAccessPolicy,
    summary="Create a DataAccessPolicy",
    tags=["DataAccessPolicy"],
)
async def create_data_access_policies(
    data_access_policy: CreateDataAccessPolicy,
    config: Config = Depends(get_config),
):
    """
    Create a DataAccessPolicy and write to the metadata store.
    """

    if isinstance(
        data_access_policy.has_data_access_committee, CreateDataAccessCommittee
    ):
        dac_accession = data_access_policy.has_data_access_committee.alias
    else:
        dac_accession = data_access_policy.has_data_access_committee

    dac_entity = await get_data_access_committee_by_accession(
        dac_accession, config=config
    )
    if not dac_entity:
        raise HTTPException(
            status_code=404,
            detail=f"DataAccessCommittee Accession {dac_accession} provided in "
            + "'data_access_policy.has_data_access_committee' could not be found. "
            + "Cannot create a DataAccessPolicy that references a "
            + "non-existing DataAccessCommittee.",
        )
    dap = await create_data_access_policy(data_access_policy, config=config)
    return dap
