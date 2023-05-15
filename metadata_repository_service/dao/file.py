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
Convenience methods for retrieving File records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import File

COLLECTION_NAME = "File"


async def retrieve_files(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of File object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of File object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    files = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in files]


async def get_file(
    file_id: str, embedded: bool = False, config: Config = CONFIG
) -> File:
    """
    Given a File ID, get the File object from metadata store.

    Args:
        file_id: The File ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The File object

    """
    file_entity = await get_entity(
        identifier=file_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=File,
        embedded=embedded,
        config=config,
    )
    return file_entity


async def get_file_by_accession(
    file_accession: str,
    embedded: bool = False,
    config: Config = CONFIG,
) -> File:
    """
    Given a File accession, get the File object from metadata store.

    Args:
        file_accession: The File accession
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The File object

    """
    file_entity = await get_entity(
        identifier=file_accession,
        field="accession",
        collection_name=COLLECTION_NAME,
        model_class=File,
        embedded=embedded,
        config=config,
    )
    return file_entity


async def get_file_format(config: Config = CONFIG):
    """
    Returns file format
    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    file_format = await collection.find({}, {"format": 1, "_id": False}).to_list(None)
    client.close()
    return file_format
