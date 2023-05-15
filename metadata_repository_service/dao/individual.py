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
Convenience methods for retrieving Individual records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import Individual

COLLECTION_NAME = "Individual"


async def retrieve_individuals(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Individual object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Individual object IDs.
        config: Rumtime configuration

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    individuals = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in individuals]


async def get_individual(
    individual_id: str, embedded: bool = False, config: Config = CONFIG
) -> Individual:
    """
    Given a Individual ID, get the Individual object from metadata store.

    Args:
        individual_id: The Individual ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Individual object

    """
    individual = await get_entity(
        identifier=individual_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Individual,
        embedded=embedded,
        config=config,
    )
    return individual


async def get_sex_count(config: Config = CONFIG):
    """
    Returns file format
    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    sex_count = await collection.find({}, {"sex": 1, "_id": False}).to_list(None)
    client.close()
    return sex_count
