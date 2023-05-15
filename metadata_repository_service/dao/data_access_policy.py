#!/usr/bin/env python3

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
"""
Convenience methods for retrieving DataAccessPolicy records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.core.utils import generate_uuid, get_timestamp
from metadata_repository_service.creation_models import CreateDataAccessPolicy
from metadata_repository_service.dao.data_access_committee import (
    get_data_access_committee_by_accession,
)
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import generate_accession, get_entity
from metadata_repository_service.models import DataAccessPolicy

COLLECTION_NAME = "DataAccessPolicy"


async def retrieve_data_access_policies(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of DataAccessPolicy object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of DataAccessPolicy object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    data_access_policies = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in data_access_policies]


async def get_data_access_policy(
    data_access_policy_id: str, embedded: bool = False, config: Config = CONFIG
) -> DataAccessPolicy:
    """
    Given a DataAccessPolicy ID, get the DataAccessPolicy object from metadata store.

    Args:
        data_access_policy_id: The DataAccessPolicy ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The DataAccessPolicy object

    """
    data_access_policy = await get_entity(
        identifier=data_access_policy_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=DataAccessPolicy,
        embedded=embedded,
        config=config,
    )
    return data_access_policy


async def get_data_access_policy_by_accession(
    data_access_policy_accession: str, embedded: bool = False, config: Config = CONFIG
) -> DataAccessPolicy:
    """
    Given a DataAccessPolicy accession, get the DataAccessPolicy object
    from metadata store.

    Args:
        data_access_policy_accession: The DataAccessPolicy accession
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The DataAccessPolicy object

    """
    data_access_policy = await get_entity(
        identifier=data_access_policy_accession,
        field="accession",
        collection_name=COLLECTION_NAME,
        model_class=DataAccessPolicy,
        embedded=embedded,
        config=config,
    )
    return data_access_policy


class DataAccessPolicyError(RuntimeError):
    """Custom exception for DAP"""


async def create_data_access_policy(
    data_access_policy: CreateDataAccessPolicy, config: Config = CONFIG
) -> DataAccessPolicy:
    """
    Create a DataAccessPolicy object and write to the metadata store.

    Args:
        data_access_policy: The DataAccessPolicy object
        config: Rumtime configuration

    Returns:
        The newly created DataAccessPolicy object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    if not data_access_policy.has_data_access_committee:
        raise DataAccessPolicyError(
            "Data Access Policy does not have a corresponding DataAccessCommittee: "
            f"{data_access_policy.dict()}"
        )
    dac_entity = await get_data_access_committee_by_accession(
        data_access_policy.has_data_access_committee, config=config
    )
    if not dac_entity:
        raise DataAccessPolicyError(
            "Cannot find a DataAccessCommittee with accession: "
            f"{data_access_policy.has_data_access_committee}"
        )
    dap_entity = data_access_policy.dict()
    dap_entity["id"] = await generate_uuid()
    dap_entity["has_data_access_committee"] = dac_entity.id
    dap_entity["creation_date"] = await get_timestamp()
    dap_entity["update_date"] = dap_entity["creation_date"]
    dap_entity["accession"] = await generate_accession(COLLECTION_NAME, config=config)
    dap_entity["schema_type"] = "DataAccessPolicy"
    await collection.insert_one(dap_entity)
    client.close()
    dap = await get_data_access_policy(dap_entity["id"], config=config)
    return dap
