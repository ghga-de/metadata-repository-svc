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
Convenience methods for retrieving Sample records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.models import Sample

COLLECTION_NAME = "Sample"


async def retrieve_samples(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Sample object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Sample object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    samples = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in samples]


async def get_sample(
    sample_id: str, embedded: bool = False, config: Config = CONFIG
) -> Sample:
    """
    Given a Sample ID, get the Sample object from metadata store.

    Args:
        sample_id: The Sample ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Sample object

    """
    sample = await get_entity(
        identifier=sample_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Sample,
        embedded=embedded,
        config=config,
    )
    return sample
