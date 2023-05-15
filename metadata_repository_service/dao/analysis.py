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
Convenience methods for retrieving Analysis records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import embed_references, get_entity
from metadata_repository_service.models import Analysis

COLLECTION_NAME = "Analysis"


async def retrieve_analyses(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Analysis objects from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Analysis object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    analyses = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in analyses]


async def get_analysis(
    analysis_id: str, embedded: bool = False, config: Config = CONFIG
) -> Analysis:
    """
    Given an Analysis ID, get the Analysis object from metadata store.

    Args:
        analysis_id: The Analysis ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Analysis object

    """
    analysis = await get_entity(
        identifier=analysis_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Analysis,
        embedded=embedded,
        config=config,
    )
    return analysis


async def get_analysis_by_accession(
    analysis_accession: str, embedded: bool = False, config: Config = CONFIG
) -> Analysis:
    """
    Given an Analysis accession, get the Analysis object from metadata store.

    Args:
        analysis_accession: The Analysis accession
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Analysis object

    """
    analysis_entity = await get_entity(
        identifier=analysis_accession,
        field="accession",
        collection_name=COLLECTION_NAME,
        model_class=Analysis,
        embedded=embedded,
        config=config,
    )
    return analysis_entity


async def get_analysis_by_linked_files(
    file_id_list: List[str], embedded: bool = False, config: Config = CONFIG
) -> List[Analysis]:
    """
    Given a list of File IDs, get the corresponding Analysis objects that
    reference the File IDs.

    Args:
        file_id_list: The File IDs
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        A list of Analysis objects

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    entities = await collection.find({"has_file": {"$in": file_id_list}}).to_list(None)
    if entities and embedded:
        for analysis in entities:
            analysis = await embed_references(analysis, config=config)
    client.close()
    analysis_entities = [Analysis(**x) for x in entities]
    return analysis_entities
