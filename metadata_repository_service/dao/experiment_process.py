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
Convenience methods for retrieving ExperimentProcess records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import ExperimentProcess

COLLECTION_NAME = "ExperimentProcess"


async def retrieve_experiment_processes(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of ExperimentProcess object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of ExperimentProcess object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    experiment_processes = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in experiment_processes]


async def get_experiment_process(
    experiment_process_id: str, embedded: bool = False, config: Config = CONFIG
) -> ExperimentProcess:
    """
    Given a ExperimentProcess ID, get the ExperimentProcess object from metadata store.

    Args:
        experiment_process_id: The ExperimentProcess ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The ExperimentProcess object

    """
    experiment_process = await get_entity(
        identifier=experiment_process_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=ExperimentProcess,
        embedded=embedded,
        config=config,
    )
    return experiment_process
