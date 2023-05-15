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
Convenience methods for retrieving Member records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.core.utils import generate_uuid, get_timestamp
from metadata_repository_service.creation_models import CreateMember
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import Member

COLLECTION_NAME = "Member"


async def retrieve_members(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Member object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Member object IDs.
        config: Rumtime configuration

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    members = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in members]


async def get_member(
    member_id: str, embedded: bool = False, config: Config = CONFIG
) -> Member:
    """
    Given a Member ID, get the Member object from metadata store.

    Args:
        member_id: The Member ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Member object

    """
    member = await get_entity(
        identifier=member_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Member,
        embedded=embedded,
        config=config,
    )
    return member


async def get_member_by_email(
    email: str, embedded: bool = False, config: Config = CONFIG
) -> Member:
    """
    Given an email of a Member, get the Member object from metadata store.

    Args:
        email: The Member email
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Member object

    """
    member = await get_entity(
        identifier=email,
        field="email",
        collection_name=COLLECTION_NAME,
        model_class=Member,
        embedded=embedded,
        config=config,
    )
    return member


async def create_member(member_obj: CreateMember, config: Config = CONFIG) -> Member:
    """
    Create a Member object and write to the metadata store.

    Args:
        member_obj: The Member object
        config: Rumtime configuration

    Returns:
        The newly created Member object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    member_entity = member_obj.dict()
    member_entity["id"] = await generate_uuid()
    member_entity["creation_date"] = await get_timestamp()
    member_entity["update_date"] = member_entity["creation_date"]
    member_entity["schema_type"] = "Member"
    await collection.insert_one(member_entity)
    client.close()
    member = await get_member(member_entity["id"], config=config)
    return member
