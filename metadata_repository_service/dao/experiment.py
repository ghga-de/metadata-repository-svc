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
Convenience methods for retrieving Experiment records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import embed_references, get_entity
from metadata_repository_service.models import Experiment

COLLECTION_NAME = "Experiment"


async def retrieve_experiments(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Experiment object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Experiment object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    experiments = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in experiments]


async def get_experiment(
    experiment_id: str, embedded: bool = False, config: Config = CONFIG
) -> Experiment:
    """
    Given an Experiment ID, get the Experiment object from metadata store.

    Args:
        experiment_id: The Experiment ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Experiment object

    """
    experiment = await get_entity(
        identifier=experiment_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Experiment,
        embedded=embedded,
        config=config,
    )
    return experiment


async def get_experiments_by_linked_files(
    file_id_list, embedded: bool = False, config: Config = CONFIG
) -> List[Experiment]:
    """
    Given a list of File IDs, get the corresponding Experiment objects that
    reference the File IDs.

    Args:
        file_id_list: The File IDs
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        A list of Experiment objects

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    entities = await collection.find({"has_file": {"$in": file_id_list}}).to_list(None)
    if entities and embedded:
        for experiment in entities:
            experiment = await embed_references(experiment, config=config)
    client.close()
    experiment_entities = [Experiment(**x) for x in entities]
    return experiment_entities
