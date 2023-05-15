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
Convenience methods for retrieving Publication records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import Publication

COLLECTION_NAME = "Publication"


async def retrieve_publications(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Publication object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Publication object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    publications = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in publications]


async def get_publication(
    publication_id: str, embedded: bool = False, config: Config = CONFIG
) -> Publication:
    """
    Given a Publication ID, get the Publication object from metadata store.

    Args:
        publication_id: The Publication ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Publication object

    """
    publication = await get_entity(
        identifier=publication_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Publication,
        embedded=embedded,
        config=config,
    )
    return publication
