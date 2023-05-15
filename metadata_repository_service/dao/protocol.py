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
Convenience methods for retrieving Protocol records
"""

from importlib import import_module
from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity, get_schema_type
from metadata_repository_service.models import AnnotatedProtocol

COLLECTION_NAME = "Protocol"
MODELS_MODULE_NAME = "metadata_repository_service.models"


async def retrieve_protocols(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Protocol object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Protocol object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    protocols = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in protocols]


async def get_protocol(
    protocol_id: str, embedded: bool = False, config: Config = CONFIG
) -> AnnotatedProtocol:
    """
    Given an Protocol ID, get the Protocol object from metadata store.

    Args:
        protocol_id: The Protocol ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Protocol object

    """
    protocol_type = await get_schema_type(
        identifier=protocol_id,
        field="id",
        collection_name=COLLECTION_NAME,
        property_name="schema_type",
        config=CONFIG,
    )
    module = import_module(MODELS_MODULE_NAME)
    protocol_class = getattr(module, protocol_type)
    protocol = await get_entity(
        identifier=protocol_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=protocol_class,
        embedded=embedded,
        config=config,
    )

    return protocol


async def get_instrument_model_count(config: Config = CONFIG):
    """
    Returns file format
    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    instrument_model = await collection.find(
        {}, {"instrument_model": 1, "_id": False}
    ).to_list(None)
    client.close()
    return instrument_model
