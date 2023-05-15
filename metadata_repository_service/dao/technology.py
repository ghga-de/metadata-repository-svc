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
Convenience methods for retrieving Technology records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import Technology

COLLECTION_NAME = "Technology"


async def retrieve_technologies(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Technology object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Technology object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    technologies = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in technologies]


async def get_technology(
    technology_id: str, embedded: bool = False, config: Config = CONFIG
) -> Technology:
    """
    Given an Technology ID, get the Technology object from metadata store.

    Args:
        technology_id: The Technology ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Technology object

    """
    technology = await get_entity(
        identifier=technology_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Technology,
        embedded=embedded,
        config=config,
    )
    return technology
