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
Convenience methods for retrieving DataAccessCommittee records
"""

from typing import List, Union

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.core.utils import generate_uuid, get_timestamp
from metadata_repository_service.creation_models import (
    CreateDataAccessCommittee,
    CreateMember,
)
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.member import create_member, get_member_by_email
from metadata_repository_service.dao.utils import generate_accession, get_entity
from metadata_repository_service.models import DataAccessCommittee

COLLECTION_NAME = "DataAccessCommittee"


async def retrieve_data_access_committees(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of DataAccessCommittee object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of DataAccessCommittee object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    data_access_committees = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in data_access_committees]


async def get_data_access_committee(
    data_access_committee_id: str, embedded: bool = False, config: Config = CONFIG
) -> DataAccessCommittee:
    """
    Given a DatasetAccessCommittee ID, get the DataAccessCommittee object
    from metadata store.

    Args:
        data_access_committee_id: The DataAccessCommittee ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The DataAccessCommittee object

    """
    data_access_committee = await get_entity(
        identifier=data_access_committee_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=DataAccessCommittee,
        embedded=embedded,
        config=config,
    )
    return data_access_committee


async def get_data_access_committee_by_accession(
    data_access_committee_accession: Union[CreateDataAccessCommittee, str],
    embedded: bool = True,
    config: Config = CONFIG,
) -> DataAccessCommittee:
    """
    Given a DataAccessCommittee accession, get the corresponding
    DataAccessCommittee object from metadata store.

    Args:
        data_access_committee_accession: The DataAccessCommittee accession
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The DataAccessCommittee object

    """
    if isinstance(data_access_committee_accession, CreateDataAccessCommittee):
        data_access_committee_accession = data_access_committee_accession.alias
    dac = await get_entity(
        identifier=data_access_committee_accession,
        field="accession",
        collection_name=COLLECTION_NAME,
        model_class=DataAccessCommittee,
        embedded=embedded,
        config=config,
    )
    return dac


class DataAccessCommitteeError(RuntimeError):
    """Custom exception for DAC"""


async def create_data_access_committee(
    data_access_committee: CreateDataAccessCommittee, config: Config = CONFIG
) -> DataAccessCommittee:
    """
    Create a DataAccessCommittee object and write to the metadata store.

    Args:
        data_access_committee: The DataAccessCommittee object
        config: Runtime configuration

    Returns:
        The newly created DataAccessCommittee object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    member_entity_id_list = []
    members = {}
    if not data_access_committee.main_contact:
        raise DataAccessCommitteeError("Data Access Committee must have main_contact")
    if not isinstance(data_access_committee.main_contact, CreateMember):
        raise DataAccessCommitteeError(
            "data_access_committee.main_contact must be an instance of CreateMember"
        )
    # CreateDataAccessCommittee.main_contact is an embedded object
    member_email = data_access_committee.main_contact.email
    members = {member_email: data_access_committee.main_contact}

    if data_access_committee.has_member:
        for member in data_access_committee.has_member:
            if isinstance(member, CreateMember):
                members[member.email] = member
    main_contact_member = None
    for member in members.values():
        member_entity = await get_member_by_email(member.email, config=config)
        if not member_entity:
            member_entity = await create_member(member, config=config)
        if member_entity.email == data_access_committee.main_contact.email:
            main_contact_member = member_entity
        member_entity_id_list.append(member_entity.id)

    dac_entity = data_access_committee.dict()
    dac_entity["id"] = await generate_uuid()
    dac_entity["create_date"] = await get_timestamp()
    dac_entity["update_date"] = dac_entity["create_date"]
    dac_entity["has_member"] = member_entity_id_list
    if main_contact_member:
        dac_entity["main_contact"] = main_contact_member.id
    dac_entity["accession"] = await generate_accession(COLLECTION_NAME, config=config)
    dac_entity["schema_type"] = "DataAccessCommittee"
    await collection.insert_one(dac_entity)
    client.close()
    dac = await get_data_access_committee(dac_entity["id"], config=config)
    return dac
